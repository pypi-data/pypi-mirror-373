import requests
import json
import urllib
import time
import prefect


def get_contacts_lists(api_key, app_private_token, offset=None, limit=250):
    url = "https://api.hubapi.com/contacts/v1/lists?"
    if api_key is not None:
        parameter_dict = {"hapikey": api_key, "count": limit}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"count": limit}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset is not None:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    try:
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        return response_dict
    except Exception as e:
        print(e)


def get_all_contacts_lists(api_key, app_private_token, limit=250):
    offset = 0
    has_more = True
    while has_more:
        resp = get_contacts_lists(api_key, app_private_token, offset, limit)

        try:
            yield resp["lists"]
            offset = offset + len(resp["lists"])
            has_more = resp["has-more"]
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
