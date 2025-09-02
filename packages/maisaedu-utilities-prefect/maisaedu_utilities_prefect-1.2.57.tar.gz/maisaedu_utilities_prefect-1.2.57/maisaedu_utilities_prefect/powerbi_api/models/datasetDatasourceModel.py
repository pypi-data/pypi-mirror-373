import json


class datasetDatasource:
    datasource_type = "datasourceType"
    connection_details = "connectionDetails"
    datasource_id = "datasourceId"
    gateway_id = "gatewayId"

    def __init__(
        self, dataset_id, datasource_type, connection_details, datasource_id, gateway_id
    ):
        self.dataset_id = dataset_id
        self.datasource_type = datasource_type
        self.connection_details = connection_details
        self.datasource_id = datasource_id
        self.gateway_id = gateway_id

    @classmethod
    def from_dict(cls, dictionary, dataset_id):
        datasource_type = dictionary.get(cls.datasource_type)
        connection_details = dictionary.get(cls.connection_details)
        datasource_id = dictionary.get(cls.datasource_id)
        gateway_id = dictionary.get(cls.gateway_id)

        return cls(
            dataset_id, datasource_type, connection_details, datasource_id, gateway_id
        )

    def __repr__(self):
        return f"{str(self.__dict__)}"
