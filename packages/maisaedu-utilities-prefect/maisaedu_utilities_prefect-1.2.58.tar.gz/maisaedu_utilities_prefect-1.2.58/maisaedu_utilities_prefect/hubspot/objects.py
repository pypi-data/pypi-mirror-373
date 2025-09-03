from datetime import datetime
import prefect
import pytz
import requests
import json
import urllib
from time import sleep


def get_objects_search(
    hapikey, app_private_token, object_name, properties, since, after, tries=5
):
    if hapikey is not None:
        url = f"https://api.hubapi.com/crm/v3/objects/{object_name}/search?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = f"https://api.hubapi.com/crm/v3/objects/{object_name}/search"
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
                { "propertyName": "hs_lastmodifieddate", "operator": "GTE", "value": "%s" }
            ] 
        }],
        "sorts": [{ "propertyName": "hs_lastmodifieddate", "direction": "ASCENDING" }],
        "query":"",
        "properties":["%s"],
        "limit":%d %s
    }""" % (
        since,
        '","'.join(properties),
        100,
        strAfter,
    )

    r = requests.post(url=post_url, headers=headers, data=publicObjectSearchRequest)
    response_dict = json.loads(r.text)
    return response_dict


def get_all_objects_incremental(
    hapikey, app_private_token, object_name, properties, since_parameter
):
    after = 0
    hasmore = True
    since = since_parameter
    size = 0
    attempts = 0
    while hasmore:
        resp = get_objects_search(
            hapikey, app_private_token, object_name, properties, since, after
        )

        try:
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
            size = resp["total"]

        except KeyError as e:
            if size > 10000:
                since = lasttimestamp
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
