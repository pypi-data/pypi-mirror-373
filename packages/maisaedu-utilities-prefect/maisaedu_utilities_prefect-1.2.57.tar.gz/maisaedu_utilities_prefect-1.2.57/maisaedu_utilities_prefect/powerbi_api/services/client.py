import adal

from .adminGroupsService import AdminGroupsService
from .activityLogsService import ActivityLogsService
from .datasetService import DatasetService
from .userService import UserService
from .gatewayService import GatewayService
from .datasourceService import DatasourceService


class PowerBIClient:
    default_resource_url = "https://analysis.windows.net/powerbi/api"
    default_api_url = "https://api.powerbi.com"
    default_authority_url = "https://login.windows.net/common"

    api_version_snippet = "v1.0"
    api_myorg_snippet = "myorg"
    api_admin_snippet = "admin"

    @staticmethod
    def get_client_with_username_password(
        client_id,
        username,
        password,
        authority_url=None,
        resource_url=None,
        api_url=None,
    ):
        """
        Constructs a client with the option of using common defaults.

        :param client_id: The Power BI Client ID
        :param username: Username
        :param password: Password
        :param authority_url: The authority_url; defaults to 'https://login.windows.net/common'
        :param resource_url: The resource_url; defaults to 'https://analysis.windows.net/powerbi/api'
        :param api_url: The api_url: defaults to 'https://api.powerbi.com'
        :return:
        """
        if authority_url is None:
            authority_url = PowerBIClient.default_authority_url

        if resource_url is None:
            resource_url = PowerBIClient.default_resource_url

        if api_url is None:
            api_url = PowerBIClient.default_api_url

        context = adal.AuthenticationContext(
            authority=authority_url, validate_authority=True, api_version=None
        )

        # get your authentication token
        token = context.acquire_token_with_username_password(
            resource=resource_url,
            client_id=client_id,
            username=username,
            password=password,
        )

        return PowerBIClient(api_url, token)

    def __init__(self, api_url, token):
        self.__auth_header = None
        self.api_url = api_url
        self.token = token
        self.activityLogs = ActivityLogsService(self)
        self.adminGroups = AdminGroupsService(self)
        self.datasets = DatasetService(self)
        self.users = UserService(self)
        # self.reports = Reports(self)
        # self.imports = Imports(self)
        # self.groups = Groups(self)
        self.gateways = GatewayService(self)
        self.datasources = DatasourceService(self)

    @property
    def auth_header(self):
        if self.__auth_header is None:
            self.__auth_header = {
                "Authorization": f'Bearer {self.token["accessToken"]}'
            }

        return self.__auth_header
