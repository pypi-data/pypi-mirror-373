import requests
import json
import time

from requests.exceptions import HTTPError
from ..models.datasetRefreshScheduleModel import datasetRefreshSchedule
from ..models.datasetDatasourceModel import datasetDatasource


class DatasetService:
    groups_snippet = "groups"
    datasets_snippet = "datasets"
    datasources_snippet = "datasources"
    refreshes_snippet = "refreshes"
    refresh_schedule_snippet = "refreshSchedule"

    get_datasources_value_key = "value"

    def __init__(self, client):
        self.client = client
        self.base_url = f"{self.client.api_url}/{self.client.api_version_snippet}/{self.client.api_myorg_snippet}"

    def refresh_dataset_in_group(self, dataset_id, group_id):
        url = (
            self.base_url
            + f"/{self.groups_snippet}/{group_id}/{self.datasets_snippet}/{dataset_id}/{self.refreshes_snippet}"
        )
        headers = self.client.auth_header
        response = requests.post(url, headers=headers)

        if response.status_code != 202:
            raise HTTPError(
                response,
                f"Failed when trying to refresh dataset {dataset_id}:\n{response.json()}",
            )

    def get_refresh_schedule(self, dataset_id):
        url = (
            self.base_url
            + f"/{self.datasets_snippet}/{dataset_id}/{self.refresh_schedule_snippet}"
        )
        headers = self.client.auth_header
        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return self.refresh_schedules_from_get_refresh_schedule_response(
                    response, dataset_id
                )
            elif response.status_code == 429:
                attempts += 1
                if attempts < max_attempts:
                    retry_after = int(response.headers.get("Retry-After", "30"))
                    print(f"Too many requests. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    raise HTTPError(
                        response,
                        f"Get Refresh Schedule request for dataset {dataset_id} returned http error: {response.json()}",
                    )
            else:
                raise HTTPError(
                    response,
                    f"Get Refresh Schedule request for dataset {dataset_id} returned http error: {response.json()}",
                )

    @classmethod
    def refresh_schedules_from_get_refresh_schedule_response(cls, response, dataset_id):
        """
        Creates a list of refresh schedules from a http response object
        :param response:
            The http response object
        :return: list
            The list of refresh schedules
        """
        # load the response into a dict
        response_dict = json.loads(response.text)
        refreshables = []

        # go through entries returned from API
        refreshables.append(datasetRefreshSchedule.from_dict(response_dict, dataset_id))

        return refreshables

    def get_datasources(self, dataset_id):
        url = (
            self.base_url
            + f"/{self.datasets_snippet}/{dataset_id}/{self.datasources_snippet}"
        )
        headers = self.client.auth_header
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPError(
                response,
                f"Get Datasources request for dataset {dataset_id} returned http error: {response.json()}",
            )

        return self.datasources_from_get_datasources_response(response, dataset_id)

    @classmethod
    def datasources_from_get_datasources_response(cls, response, dataset_id):
        """
        Creates a list of datasources related to a given dataset from a http response object
        :param response:
            The http response object
        :return: list
            The list of datasources related to a given dataset
        """
        # load the response into a dict
        response_dict = json.loads(response.text)
        datasources = []

        # go through entries returned from API
        for entry in response_dict[cls.get_datasources_value_key]:
            datasources.append(datasetDatasource.from_dict(entry, dataset_id))

        return datasources
