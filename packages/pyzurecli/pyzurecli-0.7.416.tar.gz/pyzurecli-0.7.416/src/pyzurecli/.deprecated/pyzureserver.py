import time
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Type

from loguru import logger as log
from starlette.responses import Response, RedirectResponse, JSONResponse
from toomanyports import PortManager
from toomanysessions import SessionedServer, Session, User, Sessions, Users, MicrosoftOAuth, GraphAPI

from src.pyzurecli.factory import AzureCLI

DEBUG = True

class PyzureServer(SessionedServer):
    def __init__(
            self,
            host: str = "localhost",
            port: int = PortManager.random_port(),
            cwd: Path = Path.cwd(),
            session_name: str = "session",
            session_age: int = (3600 * 8),
            session_model: Type[Session] = Session,
            user_model: Type[User] = User,
            user_whitelist: list = None,
            tenant_whitelist: list = None,
            verbose: bool = DEBUG,
    ):
        self.host = host
        self.port = port
        self.cwd = cwd
        self.session_name = session_name
        self.session_age = session_age
        self.session_model = session_model
        self.sessions = Sessions(
            session_model=self.session_model,
            session_name=self.session_name,
            verbose=verbose,
        )
        self.user_model = user_model
        self.users = Users(
            self.user_model,
            self.user_model.create,
        )
        self.user_whitelist = user_whitelist
        self.tenant_whitelist = [self.azure_cli.tenant_id]
        if tenant_whitelist: self.tenant_whitelist = self.tenant_whitelist + tenant_whitelist
        self.scopes = [
            # User, Tenant, and profile
            "User.ReadWrite.All",
            "Organization.ReadWrite.All",
            "Directory.ReadWrite.All",

            # Files and SharePoint
            "Files.ReadWrite.All",
            "Sites.ReadWrite.All",

            # Mail and Calendar
            "Mail.ReadWrite",
            "Calendars.ReadWrite",

            # Teams
            "Team.ReadBasic.All",
            "Channel.ReadBasic.All",

            # Applications
            "Application.ReadWrite.All",

            # Groups
            "Group.ReadWrite.All",

            # Device management
            "Device.ReadWrite.All",

            # Security
            "SecurityEvents.ReadWrite.All",
        ]
        self.scopes_str = " ".join(self.scopes)
        self.verbose = verbose

        _ = self.authentication_model

        super().__init__(
            host=self.host,
            port=self.port,
            session_name=self.session_name,
            session_age=self.session_age,
            session_model=self.session_model,
            authentication_model=self.authentication_model, #type: ignore
            user_model=self.user_model,
            user_whitelist=self.user_whitelist,
            tenant_whitelist=self.tenant_whitelist,
            verbose=self.verbose,
        )

    @cached_property
    def authentication_model(self):
        inst = MicrosoftOAuth(
            self,
            tenant_id="common",
            client_id=self.azure_cli.app_registration.client_id,
            scopes=self.scopes_str
        )
        return inst

    @cached_property
    def redirect_uri(self):
        return f"{self.url}/microsoft_oauth/callback"

    @cached_property
    def azure_cli(self) -> AzureCLI:
        inst = AzureCLI(
            cwd=self.cwd,
            redirect_uri=self.redirect_uri
        )
        return inst

    @cached_property
    def app_registration(self):
        azure_cli = self.azure_cli
        return azure_cli.app_registration
