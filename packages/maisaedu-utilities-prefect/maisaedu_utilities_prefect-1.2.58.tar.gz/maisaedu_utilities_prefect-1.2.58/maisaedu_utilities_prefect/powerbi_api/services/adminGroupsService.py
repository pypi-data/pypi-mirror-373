import requests
import json
import urllib.parse

from requests.exceptions import HTTPError
from ..models.adminGroupModel import adminGroup


class AdminGroupsService:
    # url snippets
    groups_snippet = "groups"
    users_snippet = "users"

    # json keys
    get_groups_value_key = "value"

    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.api_url}/{self.client.api_version_snippet}/{self.client.api_myorg_snippet}/{self.client.api_admin_snippet}"

    def get_groups_as_admin(self, filter_str=None, top=None, skip=None, expand=None):
        """
        Fetches all groups that the client has access to
        :param filter_str: OData filter string to filter results
        :param top: int > 0, OData top parameter to limit to the top n results
        :param skip: int > 0,  OData skip parameter to skip the first n results
        :return: list
            The list of groups
        """
        query_parameters = []

        if filter_str:
            query_parameters.append(f"$filter={urllib.parse.quote(filter_str)}")

        if top:
            stripped_top = json.dumps(top).strip('"')
            query_parameters.append(f"$top={urllib.parse.quote(stripped_top)}")

        if skip:
            stripped_skip = json.dumps(skip).strip('"')
            query_parameters.append(f"$skip={urllib.parse.quote(stripped_skip)}")

        if expand:
            query_parameters.append(f"$expand={urllib.parse.quote(expand)}")

        # form the url
        url = f"{self.base_url}/{self.groups_snippet}"

        # add query parameters to url if any
        if len(query_parameters) > 0:
            url += f'?{str.join("&", query_parameters)}'

        # form the headers
        headers = self.client.auth_header
        # get the response
        response = requests.get(url, headers=headers)

        # 200 is the only successful code, raise an exception on any other response code
        if response.status_code != 200:
            raise HTTPError(
                response, f"Get Groups request returned http error: {response.json()}"
            )

        return self.admin_groups_from_get_groups_as_admin_response(response)

    def add_user_as_admin(self, group_id, username, access_right="Viewer"):
        """Grants user permissions to the specified workspace."""
        url = f"{self.base_url}/{self.groups_snippet}/{group_id}/{self.users_snippet}"
        body = {"userEmailAddress": username, "groupUserAccessRight": access_right}

        response = requests.post(url, body, headers=self.client.auth_header)

        if response.status_code != 200:
            raise HTTPError(
                response,
                f"Request to add user {username} permissions to group {group_id} failed.",
            )

    @classmethod
    def admin_groups_from_get_groups_as_admin_response(cls, response):
        """
        Creates a list of groups from a http response object
        :param response:
            The http response object
        :return: list
            The list of groups
        """
        # load the response into a dict
        response_dict = json.loads(response.text)
        groups = []

        # go through entries returned from API
        for entry in response_dict[cls.get_groups_value_key]:
            groups.append(adminGroup.from_dict(entry))

        return groups
