import json


class datasource:
    id = "id"
    gateway_id = "gatewayId"
    datasource_name = "datasourceName"

    def __init__(
        self, id, gateway_id, datasource_name
    ):
        self.id = id
        self.gateway_id = gateway_id
        self.datasource_name = datasource_name

    @classmethod
    def from_dict(cls, dictionary):
        id = dictionary.get(cls.id)
        gateway_id = dictionary.get(cls.gateway_id)
        datasource_name = dictionary.get(cls.datasource_name)

        return cls(
            id, gateway_id, datasource_name
        )

    def __repr__(self):
        return f"{str(self.__dict__)}"
