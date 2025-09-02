import requests

from requests.exceptions import HTTPError
from ..models.gatewayModel import gateway


class GatewayService:
    gateways_snippet = "gateways"

    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.api_url}/{self.client.api_version_snippet}/{self.client.api_myorg_snippet}"

    def get_gateways(self):
        url = (
            self.base_url
            + f"/{self.gateways_snippet}"
        )
        headers = self.client.auth_header
        
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPError(
                response,
                f"Get gateways returned http error: {response.json()}",
            )

        response = response.json()['value']

        gateways = []
        for entry in response:
            gateways.append(gateway.from_dict(entry))

        return gateways