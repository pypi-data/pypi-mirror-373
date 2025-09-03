import requests
import json
import urllib
import time
import prefect


def get_landing_pages(api_key, app_private_token, limit=50, after=None):
    url = f"https://api.hubapi.com/cms/v3/pages/landing-pages?"
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

    if after is not None:
        parameter_dict["after"] = after

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    try:
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        return response_dict
    except Exception as e:
        print(e)


def get_all_landing_pages(api_key, app_private_token, limit=50):
    has_more = True
    after = None
    attempts = 0
    while has_more:
        resp = get_landing_pages(api_key, app_private_token, limit, after)

        try:
            if "results" in resp:
                attempts = 0
                yield resp["results"]
                if "paging" not in resp:
                    has_more = False
                else:
                    after = resp["paging"]["next"]["after"]
            else:
                attempts += 1
                if attempts > 2:
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


def get_landing_pages_stats(api_key, app_private_token, limit=50, offset=None):
    url = f"https://api.hubapi.com/analytics/v2/reports/landing-pages/total?"
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

    parameters = urllib.parse.urlencode(parameter_dict)

    url = url + parameters

    try:
        r = requests.get(url=url, headers=headers)
        response_dict = json.loads(r.text)
        return response_dict
    except Exception as e:
        print(e)


def get_all_landing_pages_stats(api_key, app_private_token, limit=50):
    has_more = True
    offset = 0
    attempts = 0
    while has_more:
        resp = get_landing_pages_stats(api_key, app_private_token, limit, offset)

        try:
            if "breakdowns" in resp:
                attempts = 0
                yield resp["breakdowns"]
                if resp["offset"] == 0 or resp['total'] == offset:
                    has_more = False
                else:
                    offset = len(resp["breakdowns"]) + offset
            else:
                attempts += 1
                if attempts > 2:
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
