from datetime import datetime
import prefect
import pytz
import requests
import json
import urllib
from time import sleep


def get_tickets_search(
    hapikey, app_private_token, properties, since, after, id, tries=5
):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/tickets/search?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/tickets/search"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
        parameters = ""

    post_url = url + parameters
    if int(after) > 0:
        strAfter = ', "after":"%s"' % (after)
    else:
        strAfter = ""
    publicObjectSearchRequest = """{
        "filterGroups": [ 
            { "filters": [
                { "propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": "%s" },
                { "propertyName": "hs_object_id", "operator": "GT", "value": %d }
            ] 
        }],
        "sorts": [{ "propertyName": "hs_lastmodifieddate", "direction": "ASCENDING" }],
        "query":"",
        "properties":["%s"],
        "limit":%d %s
    }""" % (
        since,
        id,
        '","'.join(properties),
        100,
        strAfter,
    )

    r = requests.post(url=post_url, headers=headers, data=publicObjectSearchRequest)
    response_dict = json.loads(r.text)
    return response_dict


def get_tickets_with_properties_history(hapikey, app_private_token, properties, data):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/tickets/batch/read?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/tickets/batch/read"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
        parameters = ""

    post_url = url + parameters

    data_part1 = data[: len(data) // 2]
    data_part2 = data[len(data) // 2 :]

    post_data_part_1 = {
        "properties": [prop for prop in properties],
        "propertiesWithHistory": [prop for prop in properties],
        "inputs": [{"id": i["id"]} for i in data_part1],
        "limit": 100,
    }

    post_data_part_2 = {
        "properties": [prop for prop in properties],
        "propertiesWithHistory": [prop for prop in properties],
        "inputs": [{"id": i["id"]} for i in data_part2],
        "limit": 100,
    }

    results_part_1 = []
    results_part_2 = []

    attempts = 0

    while len(results_part_1) == 0:
        try:
            r = requests.post(
                url=post_url, headers=headers, data=json.dumps(post_data_part_1)
            )
            attempts = 0
            response_dict = json.loads(r.text)
            if len(response_dict["results"]) == 0:
                break
            results_part_1 = response_dict["results"]
        except Exception as e:
            attempts += 1
            prefect.get_run_logger().info(f"Error {e}")
            if attempts > 2:
                raise e
            sleep(10)

    attempts = 0

    while len(results_part_2) == 0:
        try:
            r = requests.post(
                url=post_url, headers=headers, data=json.dumps(post_data_part_2)
            )
            attempts = 0
            response_dict = json.loads(r.text)
            if len(response_dict["results"]) == 0:
                break
            results_part_2 = response_dict["results"]
        except Exception as e:
            attempts += 1
            prefect.get_run_logger().info(f"Error {e}")
            if attempts > 2:
                raise e
            sleep(10)

    return results_part_1 + results_part_2


def get_all_tickets_incremental(
    hapikey, app_private_token, properties, since_parameter
):
    after = 0
    hasmore = True
    since = since_parameter
    size = 0
    id = 0
    attempts = 0
    while hasmore:
        resp = get_tickets_search(
            hapikey, app_private_token, properties, since, after, id
        )

        try:
            resp["results"] = get_tickets_with_properties_history(
                hapikey, app_private_token, properties, resp["results"]
            )

            yield resp["results"]
            attempts = 0
            lasttimestamp = int(
                pytz.utc.localize(
                    datetime.strptime(
                        list(resp["results"])[-1]["updatedAt"][:19], "%Y-%m-%dT%X"
                    ),
                    is_dst=False,
                ).timestamp()
                * 1000
            )
            after = resp["paging"]["next"]["after"]
            lastId = int(list(resp["results"])[-1]["id"])
            size = resp["total"]
        except KeyError as e:
            if size > 10000:
                since = lasttimestamp
                id = lastId
                after = 0
            else:
                if "status" in resp and resp["status"] == "error":
                    attempts += 1
                    sleep(10)
                    if attempts > 2:
                        raise Exception(resp["message"])
                else:
                    hasmore = False
        except Exception as e:
            hasmore = False


def get_tickets_full_load(hapikey, app_private_token, properties, after, tries=5):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/tickets?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/tickets?"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
        parameters = ""

    url = url + parameters
    url = url + "&properties=" + ",".join(properties)
    url = url + "&limit=100"
    if after:
        url = url + "&after=" + str(after)

    for i in range(tries):
        try:
            r = requests.get(url=url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            print(e)


def get_all_tickets_full_load(hapikey, app_private_token, properties):
    after = 0
    hasmore = True
    while hasmore:
        resp = get_tickets_full_load(hapikey, app_private_token, properties, after)

        try:
            resp["results"] = get_tickets_with_properties_history(
                hapikey, app_private_token, properties, resp["results"]
            )

            yield resp["results"]
            after = resp["paging"]["next"]["after"]
        except KeyError as e:
            if "message" in resp:
                if resp["message"] == "You have reached your secondly limit.":
                    sleep(10)
            else:
                hasmore = False
        except Exception as e:
            hasmore = False
