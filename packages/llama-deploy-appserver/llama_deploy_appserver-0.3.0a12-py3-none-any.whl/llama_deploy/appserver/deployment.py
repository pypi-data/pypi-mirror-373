import asyncio
import json
import logging
from typing import Any, Tuple

from llama_deploy.appserver.types import generate_id
from llama_deploy.appserver.workflow_loader import DEFAULT_SERVICE_ID
from workflows import Context, Workflow
from workflows.handler import WorkflowHandler
from workflows.server import WorkflowServer

logger = logging.getLogger()


class DeploymentError(Exception): ...


class Deployment:
    def __init__(
        self,
        workflows: dict[str, Workflow],
    ) -> None:
        """Creates a Deployment instance.

        Args:
            config: The configuration object defining this deployment
            root_path: The path on the filesystem used to store deployment data
            local: Whether the deployment is local. If true, sources won't be synced
        """

        self._default_service: str | None = workflows.get(DEFAULT_SERVICE_ID)
        self._service_tasks: list[asyncio.Task] = []
        # Ready to load services
        self._workflow_services: dict[str, Workflow] = workflows
        self._contexts: dict[str, Context] = {}
        self._handlers: dict[str, WorkflowHandler] = {}
        self._handler_inputs: dict[str, str] = {}

    @property
    def default_service(self) -> Workflow | None:
        return self._default_service

    @property
    def name(self) -> str:
        """Returns the name of this deployment."""
        return self._name

    @property
    def service_names(self) -> list[str]:
        """Returns the list of service names in this deployment."""
        return list(self._workflow_services.keys())

    async def run_workflow(
        self, service_id: str, session_id: str | None = None, **run_kwargs: dict
    ) -> Any:
        workflow = self._workflow_services[service_id]
        if session_id:
            context = self._contexts[session_id]
            return await workflow.run(context=context, **run_kwargs)

        if run_kwargs:
            return await workflow.run(**run_kwargs)

        return await workflow.run()

    def run_workflow_no_wait(
        self, service_id: str, session_id: str | None = None, **run_kwargs: dict
    ) -> Tuple[str, str]:
        workflow = self._workflow_services[service_id]
        if session_id:
            context = self._contexts[session_id]
            handler = workflow.run(context=context, **run_kwargs)
        else:
            handler = workflow.run(**run_kwargs)
            session_id = generate_id()
            self._contexts[session_id] = handler.ctx or Context(workflow)

        handler_id = generate_id()
        self._handlers[handler_id] = handler
        self._handler_inputs[handler_id] = json.dumps(run_kwargs)
        return handler_id, session_id

    def create_workflow_server(self) -> WorkflowServer:
        server = WorkflowServer()
        for service_id, workflow in self._workflow_services.items():
            server.add_workflow(service_id, workflow)
        return server
