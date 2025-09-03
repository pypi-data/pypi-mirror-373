import time
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace

from loguru import logger as log

from .graph_api import GraphAPI


@dataclass
class GraphToken:
    accessToken: str
    expiresOn: str
    expires_on: str
    subscription: str
    tenant: str
    tokenType: str


class AzureCLI:
    def __init__(
            self,
            cwd: Path = Path.cwd(),
            redirect_uri=None
    ):
        self.cwd = cwd
        if redirect_uri: log.debug(f"{self}: Registered redirect_uri {redirect_uri}.")
        if not redirect_uri: log.warning(
            f"{self}: Without a specified Redirect URI, your Azure App won't be able to distribute auth tokens!."
            f" Ignore if you are just using AzureCLI programmatically without user interaction.")
        self.redirect_uri = redirect_uri
        # turned off auto loading
        # _ = self.user
        # _ = self.service_principal
        # _ = self.app_registration
        # _ = self.graph_api
        log.success(f"{self}: Successfully initialized!")

    def __repr__(self):
        return f"[{self.cwd.name.title()}.AzureCLI]"

    @cached_property
    def user(self):
        from .user import AzureCLIUser
        return AzureCLIUser(self)

    @cached_property
    def service_principal(self):
        from .sp import AzureCLIServicePrincipal
        return AzureCLIServicePrincipal(self)

    @cached_property
    def app_registration(self):
        from .app_registration import App
        return App(self)

    @cached_property
    def graph_api(self):
        result = self.user.image.run("az account get-access-token")
        result = result.json[0]
        log.debug(f"{self}: Retrieved GraphAPI metadata: {result}")
        token = result["accessToken"]
        log.debug(f"{self}: Retrieved token {token[:4]}...")
        return GraphAPI(token=token)

    @cached_property
    def metadata(self) -> SimpleNamespace:
        from .user import UserSession  # abandoned rel imports lol
        ses: UserSession = self.user.azure_profile
        if ses is None:
            try:
                ses: UserSession = self.user.azure_profile
                log.debug(ses)
            except ses is None:
                raise RuntimeError(f"{self}: UserSession returned '{ses}', "
                                   f"which is unreadable! "
                                   f"Either your login failed or there was "
                                   f"an race condition... Try restarting."
                                   )
        subscription = ses.subscriptions[0]
        subscription_id = subscription.id
        tenant_id = subscription.tenantId
        return SimpleNamespace(
            user=ses,
            subscription_id=subscription_id,
            tenant_id=tenant_id
        )

    @cached_property
    def tenant_id(self):
        return self.metadata.tenant_id

    @cached_property
    def subscription_id(self):
        return self.metadata.subscription_id


def debug():
    AzureCLI(Path.cwd())


if __name__ == "__main__":
    debug()
    time.sleep(50)
