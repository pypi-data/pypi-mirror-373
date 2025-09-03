from dataclasses import dataclass
from functools import cached_property
from typing import Optional

from loguru import logger as log

from .factory import AzureCLI


@dataclass
class AppRegistrationCreds:
    """Azure App Registration credentials"""
    appId: str
    displayName: str
    tenantId: str
    objectId: Optional[str] = None


class AzureCLIAppRegistration:
    """Manages Azure App Registrations for multi-tenant OAuth"""

    # scopes: list = ["User.Read", "Mail.Read", "Files.Read"]

    def __init__(self, azure_cli: AzureCLI, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs.pop(kwarg))
        self.azure_cli = azure_cli
        self.cwd = azure_cli.cwd
        self.redirect_uri = self.azure_cli.redirect_uri
        self.tenant_id = self.azure_cli.metadata.tenant_id
        self.client_id = self.creds.appId
        log.success(f"{self}: Successfully initialized!")

    def __repr__(self):
        return f"[{self.cwd.name.title()}.AppRegistration]"

    @cached_property
    def creds(self) -> AppRegistrationCreds:
        """Get or create multi-tenant OAuth app registration"""
        user_image = self.azure_cli.user.image
        app_name = f"{self.cwd.name.title()}-MultiTenant"

        if getattr(self, "redirect_uri", None):
            log.debug(f"{self}: Registering app with redirect uri: {self.redirect_uri}")
            result = user_image.run(
                (f"az ad app create "
                 f"--display-name {app_name} "
                 f"--sign-in-audience AzureADMultipleOrgs "
                 f"--web-redirect-uris {self.redirect_uri} "
                 f"--public-client-redirect-uris {self.redirect_uri} "
                 f"--is-fallback-public-client true "
                 f"--enable-id-token-issuance true "
                 f"--enable-access-token-issuance false"),
                headless=True
            )
        else:
            log.debug(f"{self}: Registering app without redirect uri...")
            result = user_image.run(
                (f"az ad app create "
                 f"--display-name {app_name}"
                 ),
                headless=True
            )

        if not result.json: raise RuntimeError(f"{self}: OAuth app registration creation failed")
        app_data = result.json[0]
        if "Found an existing application" in result.output:
            log.success(f"{self}: Successfully patched multi-tenant app: {app_data['appId']}")
        else:
            log.success(f"{self}: Successfully created multi-tenant app: {app_data['appId']}")

        app = AppRegistrationCreds(
            appId=app_data["appId"],
            displayName=app_data["displayName"],
            tenantId=self.tenant_id,
            objectId=app_data.get("id")
        )

        if app:
            user_image.run(
                (f"az ad app update --id {app.appId} "
                 "--sign-in-audience AzureADMultipleOrgs "
                 "--is-fallback-public-client true"),
                headless=True
            )
        else:
            raise RuntimeError(f"Error in creating Multi-Tenant App!")

        return app

    # @property
    # def admin_consent_url(self) -> str:
    #     """Generate admin consent URL for cross-tenant permissions"""
    #     scopes = " ".join(self.scopes)
    #     log.debug(f"{self}: Generating admin consent url for following scopes: {scopes}")
    #     return (
    #         f"https://login.microsoftonline.com/common/adminconsent?"
    #         f"client_id={self.client_id}&"
    #         f"redirect_uri={self.redirect_uri}"
    #         f"scope={self.scopes}"
    #     )

    def delete(self):
        """Delete the OAuth app registration"""
        creds = self.creds
        user_image = self.azure_cli.user.image

        user_image.run(f"az ad app delete --id {creds.appId} --only-show-errors", headless=True)
        log.info(f"{self}: Deleted app registration: {creds.appId}")


App = AzureCLIAppRegistration
