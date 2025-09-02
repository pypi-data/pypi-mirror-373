import requests
import json
import urllib
import time
import prefect


def get_events(
    api_key,
    app_private_token,
    start_timestamp=None,
    end_timestamp=None,
    offset=None,
    limit=1000,
):
    url = "https://api.hubapi.com/email/public/v1/events?"
    if api_key is not None:
        parameter_dict = {"hapikey": api_key, "limit": limit}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"limit": limit}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset is not None:
        parameter_dict["offset"] = offset

    if start_timestamp is not None:
        parameter_dict["startTimestamp"] = start_timestamp

    if end_timestamp is not None:
        parameter_dict["endTimestamp"] = end_timestamp

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    r = requests.get(url=url, headers=headers, timeout=35)
    response_dict = json.loads(r.text)
    return response_dict


def get_all_email_events(
    api_key, app_private_token, start_timestamp=None, end_timestamp=None, limit=1000
):
    offset = None
    has_more = True
    attempts = 0
    while has_more:
        resp = get_events(
            api_key, app_private_token, start_timestamp, end_timestamp, offset, limit
        )

        try:
            if "hasMore" in resp and "offset" in resp:
                attempts = 0
                has_more = resp["hasMore"]
                offset = resp["offset"]

                yield resp["events"]
            else:
                attempts += 1
                if attempts > 3:
                    has_more = False
        except Exception as e:
            if (
                isinstance(e, TypeError)
                and "errorType" in e
                and e["errorType"] == "RATE_LIMIT"
            ):
                print(e)
                print(resp)
                time.sleep(10)
            else:
                prefect.get_run_logger().error("Failed")
                prefect.get_run_logger().error(e)
                prefect.get_run_logger().error(resp)
                raise e
