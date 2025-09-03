import prefect
import requests
import json
import urllib
from time import sleep


def get_hubspot_form_submission_events(
        hapikey, app_private_token, occurred_after, occurred_before, after, limit
):
    url = "https://api.hubapi.com/events/v3/events?"

    parameter_dict = {
        "eventType": "e_form_submission_v2",
        "occurredAfter": occurred_after,
        "limit": limit
    }

    if occurred_before:
        parameter_dict["occurredBefore"] = occurred_before

    if after:
        parameter_dict["after"] = after

    if hapikey is not None:
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    parameters = urllib.parse.urlencode(parameter_dict)

    url += parameters
    try:
        response = requests.get(url=url, headers=headers)
        response_dict = json.loads(response.text)
        return response_dict
    except Exception as e:
        print(e)


def get_form_submission_events(
        hapikey, app_private_token, occurred_after, occurred_before=None, limit=100
):
    after = None
    has_more = True
    attempts = 0
    while has_more:
        response = get_hubspot_form_submission_events(
            hapikey, app_private_token, occurred_after, occurred_before, after, limit
        )

        try:
            if "results" in response:
                attempts = 0
                yield response["results"]
                if "paging" not in response:
                    has_more = False
                else:
                    after = response["paging"]["next"]["after"]
            else:
                attempts += 1
                if attempts > 2:
                    has_more = False
        except TypeError as e:
            print("Erro de tipo encontrado:", e)
            print(response)
            sleep(10)
        except Exception as e:
            if "errorType" in e and e["errorType"] == "RATE_LIMIT":
                print(e)
                print(response)
                sleep(10)
            else:
                prefect.get_run_logger().error("Failed")
                prefect.get_run_logger().error(e)
                prefect.get_run_logger().error(response)
                raise e
