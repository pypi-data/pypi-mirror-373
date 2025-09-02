import prefect
import requests
import json
import urllib
from time import sleep


def getLineItems(hapikey, app_private_token, properties, after, tries=5):
    url = "https://api.hubapi.com/crm/v3/objects/line_items?"
    if hapikey is not None:
        parameter_dict = {"hapikey": hapikey, "after": after, "limit": 100}
        headers = {}
    else:
        parameter_dict = {"after": after, "limit": 100}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    parameters = urllib.parse.urlencode(parameter_dict)
    for i in properties:
        parameters = parameters + "&properties=" + i
    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def getLineItemsFull(hapikey, app_private_token, properties):
    after = 0
    hasmore = True
    attempts = 0
    while hasmore:
        resp = getLineItems(hapikey, app_private_token, properties, after)

        try:
            yield resp["results"]
            after = resp["paging"]["next"]["after"]
            attempts = 0
        except Exception as e:
            if "status" in resp and resp["status"] == "error":
                attempts += 1
                sleep(10)
                if attempts > 2:
                    raise Exception(resp["message"])
            else:
                hasmore = False
