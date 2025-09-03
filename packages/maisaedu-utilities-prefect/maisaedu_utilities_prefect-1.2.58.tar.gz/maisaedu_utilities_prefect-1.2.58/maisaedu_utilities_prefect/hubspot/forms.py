import requests
import json
import urllib
import time
import prefect


def get_forms(api_key, app_private_token, offset=None, limit=1000):
    url = "https://api.hubapi.com/forms/v2/forms?"

    parameter_dict = {
        "limit": limit,
        "formTypes": "ALL"
    }

    headers = {"content-type": "application/json", "cache-control": "no-cache"}
    if api_key is not None:
        parameter_dict["hapikey"] = api_key
    else:
        headers["Authorization"] = f"Bearer {app_private_token}"

    if offset:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)
    url += parameters

    try:
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        return response_dict
    except Exception as e:
        print(e)


def get_all_forms(api_key, app_private_token, limit=1000):
    offset = 0
    has_more = True
    while has_more:
        resp = get_forms(api_key, app_private_token, offset, limit)

        try:
            yield resp
            offset = offset + len(resp)
            if len(resp) == 0:
                has_more = False
        except Exception as e:
            if "errorType" in e and e["errorType"] == "RATE_LIMIT":
                print(e)
                print(resp)
                time.sleep(10)
            else:
                prefect.get_run_logger().error("Failed")
                prefect.get_run_logger().error(e)
                prefect.get_run_logger().error(resp)
                raise e
