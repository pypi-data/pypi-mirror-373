import json


class datasetRefreshSchedule:
    days = "days"
    times = "times"
    enabled = "enabled"
    local_time_zone_id = "localTimeZoneId"
    notify_option = "notifyOption"

    def __init__(
        self, dataset_id, days, times, enabled, local_time_zone_id, notify_option
    ):
        self.dataset_id = dataset_id
        self.days = days
        self.times = times
        self.enabled = enabled
        self.local_time_zone_id = local_time_zone_id
        self.notify_option = notify_option

    @classmethod
    def from_dict(cls, dictionary, dataset_id):
        days = dictionary.get(cls.days)
        times = dictionary.get(cls.times)
        enabled = dictionary.get(cls.enabled)
        local_time_zone_id = dictionary.get(cls.local_time_zone_id)
        notify_option = dictionary.get(cls.notify_option)

        return cls(dataset_id, days, times, enabled, local_time_zone_id, notify_option)

    def __repr__(self):
        return f"{str(self.__dict__)}"
