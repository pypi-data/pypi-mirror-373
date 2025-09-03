from .factory import AzureCLI

az = AzureCLI

from .user import AzureUser, AzureCLIUser, Subscription, UserSession
from .sp import SPUser, ServicePrincipalCreds, ServicePrincipalContext, AzureCLIServicePrincipal
from .app_registration import AzureCLIAppRegistration, AppRegistrationCreds
from .graph_api import GraphAPI, Organization, Me