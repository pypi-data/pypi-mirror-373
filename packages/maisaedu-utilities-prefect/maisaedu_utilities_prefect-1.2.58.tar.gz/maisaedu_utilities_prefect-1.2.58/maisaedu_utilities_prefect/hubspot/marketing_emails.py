import requests
import json
import urllib
import time
import prefect


def get_marketing_emails(api_key, app_private_token, offset=None):
    url = "https://api.hubapi.com/marketing-emails/v1/emails/with-statistics?"
    if api_key is not None:
        parameter_dict = {"hapikey": api_key, "limit": 100}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"limit": 100}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset is not None:
        parameter_dict["offset"] = offset

    parameter_dict["orderBy"] = "updated"

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    try:
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        return response_dict
    except Exception as e:
        print(e)


def get_all_marketing_emails(api_key, app_private_token):
    offset = 0
    total = 1
    attempts = 0
    while total > offset:
        resp = get_marketing_emails(api_key, app_private_token, offset)

        try:
            if "objects" in resp and "offset" in resp:
                attempts = 0
                offset = resp["offset"] + len(resp["objects"])
                total = resp["total"]

                yield resp["objects"]
            else:
                attempts += 1
                if attempts > 2:
                    offset = total
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
