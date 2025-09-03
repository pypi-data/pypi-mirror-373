from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import List

from dockwershell import DockerImage, path_to_wsl
from loguru import logger as log

from .factory import AzureCLI
from .util import json_to_dataclass


@dataclass(slots=True)
class ServicePrincipalCreds:
    appId: str
    displayName: str
    password: str
    tenant: str


@dataclass
class SPUser:
    name: str  # this is the clientId of the service principal
    type: str  # always "servicePrincipal"


@dataclass
class ServicePrincipalContext:
    cloudName: str
    homeTenantId: str
    id: str  # subscriptionId
    isDefault: bool
    managedByTenants: List  # usually empty unless you're delegating mgmt
    name: str  # sub name e.g. "Azure subscription 1"
    # state: str                   # "Enabled" or "Disabled"
    tenantId: str
    # actual tenant used
    user: SPUser


class AzureCLIServicePrincipal:
    instances = {}
    dockerfile: str = """
    FROM mcr.microsoft.com/azure-cli
    WORKDIR /app
    """

    def __init__(self, azure_cli: AzureCLI):
        self.azure_cli: AzureCLI = azure_cli
        self.cwd: Path = azure_cli.cwd
        self.user: DockerImage = azure_cli.user.image
        _ = self.paths
        log.success(f"{self}: Successfully initialized!")

    def __repr__(self):
        return f"[{self.azure_cli.cwd.name.title()}.AzureCLI.ServicePrincipal]"

    @cached_property
    def paths(self) -> SimpleNamespace:
        cwd: Path = self.cwd / "azure" / "sp"  # type-ignore
        cwd.mkdir(exist_ok=True, parents=True)

        dockerfile_path: Path = cwd / "Dockerfile.sp"
        dockerfile_path.touch(exist_ok=True)
        with open(dockerfile_path, "w", encoding="utf-8") as f: f.write(self.dockerfile)

        azure_config: Path = cwd / ".azure"
        azure_config.mkdir(exist_ok=True)
        azure_cmds: Path = azure_config / "commands"
        azure_cmds.mkdir(exist_ok=True)

        return SimpleNamespace(
            dir=cwd,
            dockerfile=dockerfile_path,
            azure_config=azure_config
        )

    @cached_property
    def creds(self) -> ServicePrincipalCreds | str:
        log.debug(f"{self}: Attempting to get service principal credentials...")
        meta = self.azure_cli.metadata
        data = self.user.run(
            f"az ad sp create-for-rbac -n mileslib --role Contributor --scope /subscriptions/{meta.subscription_id} --output json",
            headless=True)
        log.success(f"$$$$$$$$${data.json}")
        if not data.json: log.warning(f"{self}: Could not extract json for service principal credentials!")
        creds = json_to_dataclass(ServicePrincipalCreds, data.json[0])
        if creds.appId: log.success(f"{self}: Successfully initialized service principal in AzureCLI!")
        return creds

    @cached_property
    def run_args(self):
        creds: ServicePrincipalCreds = self.creds
        dir_wsl = path_to_wsl(self.paths.dir)
        cfg_wsl = path_to_wsl(self.paths.azure_config)
        cmd = f"-v {dir_wsl}:/app -v {cfg_wsl}:/root/.azure -e AZURE_CONFIG_DIR=/root/.azure -w /app"
        env = [
            f"-e AZURE_CLIENT_ID={creds.appId}",
            f"-e AZURE_CLIENT_SECRET={creds.password}",
            f"-e AZURE_TENANT_ID={creds.tenant}"
        ]
        cmd = f"{cmd} {" ".join(env)}"
        return cmd

    @cached_property
    def image(self):
        inst: DockerImage = DockerImage(self.paths.dockerfile, run_args=self.run_args, rebuild=True)
        return inst

    @cached_property
    def login(self):
        image: DockerImage = self.image
        creds: ServicePrincipalCreds = self.creds
        cmd = (
            f"az login --service-principal "
            f"--username {creds.appId} "
            f"--password {creds.password} "
            f"--tenant {creds.tenant}"
        )
        out = image.run(cmd, headless=True)
        subscription_data = out.json[0] if isinstance(out.json, list) else out.json
        ses = json_to_dataclass(ServicePrincipalContext, subscription_data)
        return ses
