import argparse
import logging
import os
import threading
import time
import webbrowser
from contextlib import asynccontextmanager
from importlib.metadata import version
from pathlib import Path
from typing import Any, AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from llama_deploy.appserver.configure_logging import (
    add_log_middleware,
    setup_logging,
)
from llama_deploy.appserver.deployment_config_parser import (
    get_deployment_config,
)
from llama_deploy.appserver.routers.deployments import (
    create_base_router,
    create_deployments_router,
)
from llama_deploy.appserver.routers.ui_proxy import (
    create_ui_proxy_router,
    mount_static_files,
)
from llama_deploy.appserver.settings import configure_settings, settings
from llama_deploy.appserver.workflow_loader import (
    _exclude_venv_warning,
    build_ui,
    inject_appserver_into_target,
    install_ui,
    load_environment_variables,
    load_workflows,
    start_dev_ui_process,
)
from llama_deploy.core.config import DEFAULT_DEPLOYMENT_FILE_PATH
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.routing import Route
from starlette.schemas import SchemaGenerator
from workflows.server import WorkflowServer

from .deployment import Deployment
from .interrupts import shutdown_event
from .process_utils import run_process
from .routers import health_router
from .stats import apiserver_state

logger = logging.getLogger("uvicorn.info")

# Auto-configure logging on import when requested (e.g., uvicorn reload workers)
if os.getenv("LLAMA_DEPLOY_AUTO_LOGGING", "0") == "1":
    setup_logging(os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    shutdown_event.clear()
    apiserver_state.state("starting")
    config = get_deployment_config()

    workflows = load_workflows(config)
    deployment = Deployment(workflows)
    base_router = create_base_router(config.name)
    deploy_router = create_deployments_router(config.name, deployment)
    server = deployment.create_workflow_server()

    for route in server.app.routes:
        # add routes directly rather than mounting, so that we can share a root
        if isinstance(route, Route):
            app.add_api_route(
                f"/deployments/{config.name}{route.path}",
                route.endpoint,
                name=f"{config.name}_{route.name}",
                methods=route.methods,
                include_in_schema=True,  # change to false when schemas are added to workflow server
                tags=["workflows"],
            )

    app.include_router(base_router)
    app.include_router(deploy_router)

    _setup_openapi(config.name, app, server)

    if config.ui is not None:
        if settings.proxy_ui:
            ui_router = create_ui_proxy_router(config.name, settings.proxy_ui_port)
            app.include_router(ui_router)
        else:
            # otherwise serve the pre-built if available
            mount_static_files(app, config, settings)

    apiserver_state.state("running")
    yield

    apiserver_state.state("stopped")


def _setup_openapi(name: str, app: FastAPI, server: WorkflowServer) -> None:
    """
    extends the fastapi based openapi schema with starlette generated schema
    """
    schema_title = "Llama Deploy App Server"
    app_version = version("llama-deploy-appserver")

    prefix = f"/deployments/{name}"
    workflow_routes = [x for x in server.app.routes if isinstance(x, Route)]
    server_app_routes = []
    for route in workflow_routes:
        server_app_routes.append(
            Route(
                path=prefix + route.path,
                endpoint=route.endpoint,
                methods=route.methods,
                name=route.name,
                include_in_schema=route.include_in_schema,
            )
        )

    schemas = SchemaGenerator(
        {"openapi": "3.0.0", "info": {"title": schema_title, "version": app_version}}
    )
    starlette_schema = schemas.get_schema(server_app_routes)

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=schema_title,
            version=app_version,
            routes=app.routes + server_app_routes,
        )
        openapi_schema["paths"] = {
            **openapi_schema["paths"],
            **starlette_schema["paths"],
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # ty: ignore[invalid-assignment] - doesn't like us overwriting the method


app = FastAPI(lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


# Configure CORS middleware if the environment variable is set
if not os.environ.get("DISABLE_CORS", False):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

app.include_router(health_router)
add_log_middleware(app)


def open_browser_async(host: str, port: int) -> None:
    def _open_with_delay() -> None:
        time.sleep(1)
        webbrowser.open(f"http://{host}:{port}")

    threading.Thread(target=_open_with_delay).start()


def prepare_server(
    deployment_file: Path | None = None,
    install: bool = False,
    build: bool = False,
) -> None:
    configure_settings(
        deployment_file_path=deployment_file or Path(DEFAULT_DEPLOYMENT_FILE_PATH)
    )
    load_environment_variables(get_deployment_config(), settings.resolved_config_parent)
    if install:
        config = get_deployment_config()
        inject_appserver_into_target(config, settings.resolved_config_parent)
        install_ui(config, settings.resolved_config_parent)
    if build:
        build_ui(settings.resolved_config_parent, get_deployment_config(), settings)


def start_server(
    proxy_ui: bool = False,
    reload: bool = False,
    cwd: Path | None = None,
    deployment_file: Path | None = None,
    open_browser: bool = False,
    configure_logging: bool = True,
) -> None:
    # Configure via environment so uvicorn reload workers inherit the values
    configure_settings(
        proxy_ui=proxy_ui,
        app_root=cwd,
        deployment_file_path=deployment_file or Path(DEFAULT_DEPLOYMENT_FILE_PATH),
        reload=reload,
    )
    load_environment_variables(get_deployment_config(), settings.resolved_config_parent)

    ui_process = None
    if proxy_ui:
        ui_process = start_dev_ui_process(
            settings.resolved_config_parent, settings, get_deployment_config()
        )
    try:
        if open_browser:
            open_browser_async(settings.host, settings.port)
        # Ensure reload workers configure logging on import
        os.environ["LLAMA_DEPLOY_AUTO_LOGGING"] = "1"
        # Configure logging for the launcher process as well
        if configure_logging:
            setup_logging(os.getenv("LOG_LEVEL", "INFO"))
        uvicorn.run(
            "llama_deploy.appserver.app:app",
            host=settings.host,
            port=settings.port,
            reload=reload,
            timeout_graceful_shutdown=60,
            access_log=False,
            log_config=None,
        )
    finally:
        if ui_process is not None:
            ui_process.terminate()


def start_server_in_target_venv(
    proxy_ui: bool = False,
    reload: bool = False,
    cwd: Path | None = None,
    deployment_file: Path | None = None,
    open_browser: bool = False,
    port: int | None = None,
    ui_port: int | None = None,
    log_level: str | None = None,
    log_format: str | None = None,
) -> None:
    # Ensure settings reflect the intended working directory before computing paths

    configure_settings(
        app_root=cwd,
        deployment_file_path=deployment_file,
        reload=reload,
        proxy_ui=proxy_ui,
    )
    base_dir = cwd or Path.cwd()
    path = settings.resolved_config_parent.relative_to(base_dir)
    args = ["uv", "run", "--no-progress", "python", "-m", "llama_deploy.appserver.app"]
    if proxy_ui:
        args.append("--proxy-ui")
    if reload:
        args.append("--reload")
    if deployment_file:
        args.append("--deployment-file")
        args.append(str(deployment_file))
    if open_browser:
        args.append("--open-browser")

    env = os.environ.copy()
    if port:
        env["LLAMA_DEPLOY_APISERVER_PORT"] = str(port)
    if ui_port:
        env["LLAMA_DEPLOY_APISERVER_PROXY_UI_PORT"] = str(ui_port)
    if log_level:
        env["LOG_LEVEL"] = log_level
    if log_format:
        env["LOG_FORMAT"] = log_format

    ret = run_process(
        args,
        cwd=path,
        env=env,
        line_transform=_exclude_venv_warning,
    )

    if ret != 0:
        raise SystemExit(ret)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--proxy-ui", action="store_true")
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--deployment-file", type=Path)
    parser.add_argument("--open-browser", action="store_true")

    args = parser.parse_args()
    start_server(
        proxy_ui=args.proxy_ui,
        reload=args.reload,
        deployment_file=args.deployment_file,
        open_browser=args.open_browser,
    )
