import asyncio
import json
from typing import AsyncGenerator

from fastapi import (
    APIRouter,
    HTTPException,
)
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from llama_deploy.appserver.deployment import Deployment
from llama_deploy.appserver.types import (
    EventDefinition,
    SessionDefinition,
    TaskDefinition,
    TaskResult,
    generate_id,
)
from llama_deploy.appserver.workflow_loader import DEFAULT_SERVICE_ID
from workflows import Context
from workflows.context import JsonSerializer
from workflows.handler import WorkflowHandler


def create_base_router(name: str) -> APIRouter:
    base_router = APIRouter(
        prefix="",
    )

    @base_router.get("/", response_model=None)
    async def root() -> RedirectResponse:
        return RedirectResponse(f"/deployments/{name}/ui")

    return base_router


def create_deployments_router(name: str, deployment: Deployment) -> APIRouter:
    deployments_router = APIRouter(
        prefix="/deployments",
    )

    @deployments_router.post(f"/{name}/tasks/run")
    async def create_deployment_task(
        task_definition: TaskDefinition,
        session_id: str | None = None,
    ) -> JSONResponse:
        """Create a task for the deployment, wait for result and delete associated session."""

        service_id = task_definition.service_id or DEFAULT_SERVICE_ID

        if service_id not in deployment.service_names:
            raise HTTPException(
                status_code=404,
                detail=(
                    "There is no default service for this deployment. service_id is required"
                    if not task_definition.service_id
                    else f"Service '{service_id}' not found in deployment 'deployment_name'"
                ),
            )

        run_kwargs = json.loads(task_definition.input) if task_definition.input else {}
        result = await deployment.run_workflow(
            service_id=service_id, session_id=session_id, **run_kwargs
        )
        return JSONResponse(result)

    @deployments_router.post(f"/{name}/tasks/create")
    async def create_deployment_task_nowait(
        task_definition: TaskDefinition,
        session_id: str | None = None,
    ) -> TaskDefinition:
        """Create a task for the deployment but don't wait for result."""
        service_id = task_definition.service_id or DEFAULT_SERVICE_ID
        if service_id not in deployment.service_names:
            raise HTTPException(
                status_code=404,
                detail=(
                    "There is no default service for this deployment. service_id is required"
                    if not task_definition.service_id
                    else f"Service '{service_id}' not found in deployment 'deployment_name'"
                ),
            )

        run_kwargs = json.loads(task_definition.input) if task_definition.input else {}
        handler_id, session_id = deployment.run_workflow_no_wait(
            service_id=service_id, session_id=session_id, **run_kwargs
        )

        task_definition.session_id = session_id
        task_definition.task_id = handler_id

        return task_definition

    @deployments_router.post(f"/{name}/tasks/{{task_id}}/events")
    async def send_event(
        task_id: str,
        session_id: str,
        event_def: EventDefinition,
    ) -> EventDefinition:
        """Send a human response event to a service for a specific task and session."""
        ctx = deployment._contexts[session_id]
        serializer = JsonSerializer()
        event = serializer.deserialize(event_def.event_obj_str)
        ctx.send_event(event)

        return event_def

    @deployments_router.get(f"/{name}/tasks/{{task_id}}/events")
    async def get_events(
        session_id: str,
        task_id: str,
        raw_event: bool = False,
    ) -> StreamingResponse:
        """
        Get the stream of events from a given task and session.

        Args:
            raw_event (bool, default=False): Whether to return the raw event object
                or just the event data.
        """

        async def event_stream(handler: WorkflowHandler) -> AsyncGenerator[str, None]:
            serializer = JsonSerializer()
            # this will hang indefinitely if done and queue is empty. Bail
            if (
                handler.is_done()
                and handler.ctx is not None
                and handler.ctx.streaming_queue.empty()
            ):
                return
            async for event in handler.stream_events():
                data = json.loads(serializer.serialize(event))
                if raw_event:
                    yield json.dumps(data) + "\n"
                else:
                    yield json.dumps(data.get("value")) + "\n"
                await asyncio.sleep(0.01)
            await handler

        return StreamingResponse(
            event_stream(deployment._handlers[task_id]),
            media_type="application/x-ndjson",
        )

    @deployments_router.get(f"/{name}/tasks/{{task_id}}/results")
    async def get_task_result(
        session_id: str,
        task_id: str,
    ) -> TaskResult | None:
        """Get the task result associated with a task and session."""

        handler = deployment._handlers[task_id]
        return TaskResult(task_id=task_id, history=[], result=await handler)

    @deployments_router.get(f"/{name}/tasks")
    async def get_tasks() -> list[TaskDefinition]:
        """Get all the tasks from all the sessions in a given deployment."""

        tasks: list[TaskDefinition] = []
        for task_id, handler in deployment._handlers.items():
            if handler.is_done():
                continue
            tasks.append(
                TaskDefinition(
                    task_id=task_id,
                    input=deployment._handler_inputs[task_id],
                )
            )

        return tasks

    @deployments_router.get(f"/{name}/sessions")
    async def get_sessions() -> list[SessionDefinition]:
        """Get the active sessions in a deployment and service."""

        return [SessionDefinition(session_id=k) for k in deployment._contexts.keys()]

    @deployments_router.get(f"/{name}/sessions/{{session_id}}")
    async def get_session(
        session_id: str,
    ) -> SessionDefinition:
        """Get the definition of a session by ID."""

        return SessionDefinition(session_id=session_id)

    @deployments_router.post(f"/{name}/sessions/create")
    async def create_session() -> SessionDefinition:
        """Create a new session for a deployment."""

        workflow = deployment.default_service
        if workflow is None:
            raise HTTPException(
                status_code=400,
                detail="There is no default service for this deployment",
            )
        session_id = generate_id()
        deployment._contexts[session_id] = Context(workflow)

        return SessionDefinition(session_id=session_id)

    @deployments_router.post(f"/{name}/sessions/delete")
    async def delete_session(
        session_id: str,
    ) -> None:
        """Get the active sessions in a deployment and service."""

        deployment._contexts.pop(session_id)

    return deployments_router
