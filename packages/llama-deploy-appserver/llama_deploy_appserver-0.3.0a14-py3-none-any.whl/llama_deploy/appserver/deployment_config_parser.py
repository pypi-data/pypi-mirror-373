import functools

from llama_deploy.appserver.settings import BootstrapSettings, settings
from llama_deploy.core.deployment_config import DeploymentConfig, read_deployment_config


@functools.cache
def get_deployment_config() -> DeploymentConfig:
    base_settings = BootstrapSettings()
    base = settings.app_root.resolve()
    name = base_settings.deployment_name
    parsed = read_deployment_config(base, settings.deployment_file_path)
    if name is not None:
        parsed.name = name
    return parsed
