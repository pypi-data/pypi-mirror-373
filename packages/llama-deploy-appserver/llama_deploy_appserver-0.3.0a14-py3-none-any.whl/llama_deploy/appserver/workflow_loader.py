import configparser
import functools
import importlib
import logging
import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from importlib.metadata import version as pkg_version
from pathlib import Path
from textwrap import dedent

from dotenv import dotenv_values
from llama_deploy.appserver.deployment_config_parser import (
    DeploymentConfig,
)
from llama_deploy.appserver.process_utils import run_process, spawn_process
from llama_deploy.appserver.settings import ApiserverSettings, settings
from llama_deploy.core.ui_build import ui_build_output_path
from packaging.version import InvalidVersion, Version
from workflows import Workflow
from workflows.server import WorkflowServer

logger = logging.getLogger(__name__)

DEFAULT_SERVICE_ID = "default"


def load_workflows(config: DeploymentConfig) -> dict[str, Workflow]:
    """
    Creates WorkflowService instances according to the configuration object.

    """
    workflow_services: dict[str, Workflow] = {}

    if config.app:
        module_name, app_name = config.app.split(":", 1)
        module = importlib.import_module(module_name)
        workflow = getattr(module, app_name)
        if not isinstance(workflow, WorkflowServer):
            raise ValueError(
                f"Workflow {app_name} in {module_name} is not a WorkflowServer object"
            )
        # kludge to get the workflows
        workflow_services = workflow._workflows
    else:
        for service_id, workflow_name in config.workflows.items():
            module_name, workflow_name = workflow_name.split(":", 1)
            module = importlib.import_module(module_name)
            workflow = getattr(module, workflow_name)
            if not isinstance(workflow, Workflow):
                logger.warning(
                    f"Workflow {workflow_name} in {module_name} is not a Workflow object",
                )
            workflow_services[service_id] = workflow

    return workflow_services


def load_environment_variables(config: DeploymentConfig, source_root: Path) -> None:
    """
    Load environment variables from the deployment config.
    """
    env_vars = {**config.env} if config.env else {}
    for env_file in config.env_files or []:
        env_file_path = source_root / env_file
        values = dotenv_values(env_file_path)
        env_vars.update(**values)
    for key, value in env_vars.items():
        if value:
            os.environ[key] = value


@functools.cache
def are_we_editable_mode() -> bool:
    """
    Check if we're in editable mode.
    """
    # Heuristic: if the package path does not include 'site-packages', treat as editable
    top_level_pkg = "llama_deploy.appserver"
    try:
        pkg = importlib.import_module(top_level_pkg)
        pkg_path = Path(getattr(pkg, "__file__", "")).resolve()
        if not pkg_path.exists():
            return False

        return "site-packages" not in pkg_path.parts
    except Exception:
        return False


def inject_appserver_into_target(
    config: DeploymentConfig, source_root: Path, sdists: list[Path] | None = None
) -> None:
    """
    Ensures uv, and uses it to add the appserver as a dependency to the target app.
    - If sdists are provided, they will be installed directly for offline-ish installs (still fetches dependencies)
    - If the appserver is currently editable, it will be installed directly from the source repo
    - otherwise fetches the current version from pypi

    Args:
        config: The deployment config
        source_root: The root directory of the deployment
        sdists: A list of tar.gz sdists files to install instead of installing the appserver
    """
    path = settings.resolved_config_parent
    logger.info(f"Installing ensuring venv at {path} and adding appserver to it")
    _ensure_uv_available()
    _install_and_add_appserver_if_missing(path, source_root, sdists=sdists)


def _get_installed_version_within_target(path: Path) -> Version | None:
    try:
        result = subprocess.check_output(
            [
                "uv",
                "run",
                "python",
                "-c",
                dedent("""
                        from importlib.metadata import version
                        try:
                            print(version("llama-deploy-appserver"))
                        except Exception:
                            pass
                       """),
            ],
            cwd=path,
            stderr=subprocess.DEVNULL,
        )
        try:
            return Version(result.decode("utf-8").strip())
        except InvalidVersion:
            return None
    except subprocess.CalledProcessError:
        return None


def _get_current_version() -> Version:
    return Version(pkg_version("llama-deploy-appserver"))


def _is_missing_or_outdated(path: Path) -> Version | None:
    """
    returns the current version if the installed version is missing or outdated, otherwise None
    """
    installed = _get_installed_version_within_target(path)
    current = _get_current_version()
    if installed is None or installed < current:
        return current
    return None


def _install_and_add_appserver_if_missing(
    path: Path,
    source_root: Path,
    save_version: bool = False,
    sdists: list[Path] | None = None,
) -> None:
    """
    Ensure venv, install project deps, and add the appserver to the venv if it's missing or outdated
    """

    if not (source_root / path / "pyproject.toml").exists():
        logger.warning(
            f"No pyproject.toml found at {source_root / path}, skipping appserver injection. The server will likely not be able to install your workflows."
        )
        return

    def run_uv(cmd: str, args: list[str] = [], extra_env: dict[str, str] | None = None):
        env = os.environ.copy()
        if extra_env:
            env.update(extra_env)
        run_process(
            ["uv", cmd] + args,
            cwd=source_root / path,
            prefix=f"[uv {cmd}]",
            color_code="36",
            use_tty=False,
            line_transform=_exclude_venv_warning,
            env=env,
        )

    def ensure_venv(path: Path, force: bool = False) -> Path:
        venv_path = source_root / path / ".venv"
        if force or not venv_path.exists():
            run_uv("venv", [str(venv_path)])
        return venv_path

    editable = are_we_editable_mode()
    venv_path = ensure_venv(path, force=editable)
    run_uv(
        "sync",
        ["--no-dev", "--inexact"],
        extra_env={"UV_PROJECT_ENVIRONMENT": str(venv_path)},
    )

    if sdists:
        run_uv(
            "pip",
            ["install"]
            + [str(s.absolute()) for s in sdists]
            + ["--prefix", str(venv_path)],
        )
    elif are_we_editable_mode():
        same_python_version = _same_python_version(venv_path)
        if not same_python_version.is_same:
            logger.error(
                f"Python version mismatch. Current: {same_python_version.current_version} != Project: {same_python_version.target_version}. During development, the target environment must be running the same Python version, otherwise the appserver cannot be installed."
            )
            raise RuntimeError(
                f"Python version mismatch. Current: {same_python_version.current_version} != Project: {same_python_version.target_version}"
            )
        pyproject = _find_development_pyproject()
        if pyproject is None:
            raise RuntimeError("No pyproject.toml found in llama-deploy-appserver")
        base = (source_root.resolve() / path).resolve()
        rel = Path(os.path.relpath(pyproject, start=base))
        target = f"file://{str(rel)}"

        run_uv(
            "pip",
            [
                "install",
                "--reinstall-package",
                "llama-deploy-appserver",
                target,
                "--prefix",
                str(venv_path),
            ],
        )

    else:
        version = _is_missing_or_outdated(path)
        if version is not None:
            if save_version:
                run_uv("add", [f"llama-deploy-appserver>={version}"])
            else:
                run_uv(
                    "pip",
                    [
                        "install",
                        f"llama-deploy-appserver=={version}",
                        "--prefix",
                        str(venv_path),
                    ],
                )


def _find_development_pyproject() -> Path | None:
    dir = Path(__file__).parent.resolve()
    while not (dir / "pyproject.toml").exists():
        dir = dir.parent
        if dir == dir.root:
            return None
    return dir


def _exclude_venv_warning(line: str) -> str | None:
    if "use `--active` to target the active environment instead" in line:
        return None
    return line


def _ensure_uv_available() -> None:
    # Check if uv is available on the path
    uv_available = False
    try:
        subprocess.check_call(
            ["uv", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        uv_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    if not uv_available:
        # bootstrap uv with pip
        try:
            run_process(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "uv",
                ],
                prefix="[python -m pip]",
                color_code="31",  # red
            )
        except subprocess.CalledProcessError as e:
            msg = f"Unable to install uv. Environment must include uv, or uv must be installed with pip: {e.stderr}"
            raise RuntimeError(msg)


@dataclass
class SamePythonVersionResult:
    is_same: bool
    current_version: str
    target_version: str | None


def _same_python_version(venv_path: Path) -> SamePythonVersionResult:
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    target_version = None
    cfg = venv_path / "pyvenv.cfg"
    if cfg.exists():
        parser = configparser.ConfigParser()
        parser.read_string("[venv]\n" + cfg.read_text())
        ver_str = parser["venv"].get("version_info", "").strip()
        if ver_str:
            try:
                v = Version(ver_str)
                target_version = f"{v.major}.{v.minor}"
            except InvalidVersion:
                pass
    return SamePythonVersionResult(
        is_same=current_version == target_version,
        current_version=current_version,
        target_version=target_version,
    )


def install_ui(config: DeploymentConfig, config_parent: Path) -> None:
    if config.ui is None:
        return
    package_manager = config.ui.package_manager
    try:
        run_process(
            [package_manager, "install"],
            cwd=config_parent / config.ui.directory,
            prefix=f"[{package_manager} install]",
            color_code="33",
            # auto download the package manager
            env={**os.environ.copy(), "COREPACK_ENABLE_DOWNLOAD_PROMPT": "0"},
        )
    except BaseException as e:
        if "No such file or directory" in str(e):
            raise RuntimeError(
                f"Package manager {package_manager} not found. Please download and enable corepack, or install the package manager manually."
            )
        raise e


def _ui_env(config: DeploymentConfig, settings: ApiserverSettings) -> dict[str, str]:
    env = os.environ.copy()
    env["LLAMA_DEPLOY_DEPLOYMENT_URL_ID"] = config.name
    env["LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH"] = f"/deployments/{config.name}/ui"
    if config.ui is not None:
        env["PORT"] = str(settings.proxy_ui_port)
    return env


def build_ui(
    config_parent: Path, config: DeploymentConfig, settings: ApiserverSettings
) -> bool:
    """
    Returns True if the UI was built (and supports building), otherwise False if there's no build command
    """
    if config.ui is None:
        return False
    path = Path(config.ui.directory)
    env = _ui_env(config, settings)

    has_build = ui_build_output_path(config_parent, config)
    if has_build is None:
        return False

    run_process(
        ["npm", "run", "build"],
        cwd=config_parent / path,
        env=env,
        prefix="[npm run build]",
        color_code="34",
    )
    return True


def start_dev_ui_process(
    root: Path, settings: ApiserverSettings, config: DeploymentConfig
) -> None | subprocess.Popen:
    ui_port = settings.proxy_ui_port
    ui = config.ui
    if ui is None:
        return None

    # If a UI dev server is already listening on the configured port, do not start another
    def _is_port_open(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                return sock.connect_ex(("127.0.0.1", port)) == 0
            except Exception:
                return False

    if _is_port_open(ui_port):
        logger.info(
            f"Detected process already running on port {ui_port}; not starting a new one."
        )
        return None
    # start the ui process
    env = _ui_env(config, settings)
    # Transform first 20 lines to replace the default UI port with the main server port
    line_counter = 0

    def _transform(line: str) -> str:
        nonlocal line_counter
        if line_counter < 20:
            line = line.replace(f":{ui_port}", f":{settings.port}")
        line_counter += 1
        return line

    return spawn_process(
        ["npm", "run", ui.serve_command],
        cwd=root / (ui.directory),
        env=env,
        prefix=f"[npm run {ui.serve_command}]",
        color_code="35",
        line_transform=_transform,
        use_tty=False,
    )
