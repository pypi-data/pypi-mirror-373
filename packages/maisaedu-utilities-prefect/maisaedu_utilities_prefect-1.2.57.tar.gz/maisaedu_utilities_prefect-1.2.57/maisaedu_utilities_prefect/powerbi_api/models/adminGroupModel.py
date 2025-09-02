import json

class adminGroup:
    id_key = 'id'
    name_key = 'name'
    description = 'description'
    type = 'type'
    dashboards = 'dashboards'
    dataflows = 'dataflows'
    datasets = 'datasets'
    reports = 'reports'
    users = 'users'
    workbooks = 'workbooks'
    is_readonly_key = 'isReadOnly'
    is_on_dedicated_capacity_key = 'isOnDedicatedCapacity'

    def __init__(self, group_id, name, description, type, dashboards, dataflows, datasets, reports, users, workbooks, is_readonly=False, is_on_dedicated_capacity=False):
        self.id = group_id
        self.name = name
        self.description = description
        self.type = type
        self.dashboards = dashboards
        self.dataflows = dataflows
        self.datasets = datasets
        self.reports = reports
        self.users = users
        self.workbooks = workbooks
        self.is_readonly = is_readonly
        self.is_on_dedicated_capacity = is_on_dedicated_capacity

    @classmethod
    def from_dict(cls, dictionary):
        group_id = dictionary.get(cls.id_key)
        if group_id is None:
            raise RuntimeError("Group dictionary has no id key")

        name = dictionary.get(cls.name_key)
        description = dictionary.get(cls.description)
        type = dictionary.get(cls.type)
        dashboards = dictionary.get(cls.dashboards)
        dataflows = dictionary.get(cls.dataflows)
        datasets = dictionary.get(cls.datasets)
        reports = dictionary.get(cls.reports)
        users = dictionary.get(cls.users)
        workbooks = dictionary.get(cls.workbooks)
        is_readonly = dictionary.get(cls.is_readonly_key, False)
        is_on_dedicated_capacity = dictionary.get(cls.is_on_dedicated_capacity_key, False)

        return cls(group_id, name, description, type, dashboards, dataflows, datasets, reports, users, workbooks, is_readonly, is_on_dedicated_capacity)

    def __repr__(self):
        return f'{str(self.__dict__)}'
