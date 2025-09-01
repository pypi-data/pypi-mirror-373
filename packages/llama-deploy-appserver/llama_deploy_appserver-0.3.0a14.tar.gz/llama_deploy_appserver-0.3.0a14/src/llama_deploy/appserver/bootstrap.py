"""
Bootstraps an application from a remote github repository given environment variables.

This just sets up the files from the repository. It's more of a build process.
"""

import os
from pathlib import Path

from llama_deploy.appserver.deployment_config_parser import get_deployment_config
from llama_deploy.appserver.settings import (
    BootstrapSettings,
    configure_settings,
    settings,
)
from llama_deploy.appserver.workflow_loader import (
    build_ui,
    inject_appserver_into_target,
    install_ui,
    load_environment_variables,
)
from llama_deploy.core.git.git_util import (
    clone_repo,
)


def bootstrap_app_from_repo(
    target_dir: str = "/opt/app",
):
    bootstrap_settings = BootstrapSettings()
    # Needs the github url+auth, and the deployment file path
    # clones the repo to a standard directory
    # (eventually) runs the UI build process and moves that to a standard directory for a file server

    repo_url = bootstrap_settings.repo_url
    if repo_url is None:
        raise ValueError("repo_url is required to bootstrap")
    clone_repo(
        repository_url=repo_url,
        git_ref=bootstrap_settings.git_sha or bootstrap_settings.git_ref,
        basic_auth=bootstrap_settings.auth_token,
        dest_dir=target_dir,
    )
    # Ensure target_dir exists locally when running tests outside a container
    os.makedirs(target_dir, exist_ok=True)
    os.chdir(target_dir)
    configure_settings(
        app_root=Path(target_dir),
        deployment_file_path=Path(bootstrap_settings.deployment_file_path),
    )
    config = get_deployment_config()
    load_environment_variables(config, settings.resolved_config_parent)

    sdists = None
    if bootstrap_settings.bootstrap_sdists:
        sdists = [
            Path(bootstrap_settings.bootstrap_sdists) / f
            for f in os.listdir(bootstrap_settings.bootstrap_sdists)
        ]
        sdists = [f for f in sdists if f.is_file() and f.name.endswith(".tar.gz")]
        if not sdists:
            sdists = None
    # Use the explicit base path rather than relying on global settings so tests
    # can safely mock configure_settings without affecting call arguments.
    inject_appserver_into_target(config, settings.resolved_config_parent, sdists)
    install_ui(config, settings.resolved_config_parent)
    build_ui(settings.resolved_config_parent, config, settings)

    pass


if __name__ == "__main__":
    bootstrap_app_from_repo()
