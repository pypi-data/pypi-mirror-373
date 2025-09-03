from datetime import datetime
import pytz
import prefect
import requests
import json
import urllib
from time import sleep


def get_deals_v1(hapikey, app_private_token, properties, offset, extraparams, tries=5):
    url = "https://api.hubapi.com/deals/v1/deal/paged?"
    if hapikey is not None:
        parameter_dict = {
            "hapikey": hapikey,
            "count": "250",
            "includeAssociations": "true",
        }
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"count": "250", "includeAssociations": "true"}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
    if offset > 0:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)

    for i in properties:
        parameters = parameters + "&properties=" + i
    if extraparams != "":
        parameters = parameters + "&" + extraparams

    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def get_deals_v1_recent_modified(
    hapikey, app_private_token, properties, offset, extraparams, since, tries=5
):
    url = "https://api.hubapi.com/deals/v1/deal/recent/modified?"
    if hapikey is not None:
        parameter_dict = {
            "hapikey": hapikey,
            "count": "250",
            "includeAssociations": "true",
        }
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"count": "250", "includeAssociations": "true"}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    if offset > 0:
        parameter_dict["offset"] = offset

    parameters = urllib.parse.urlencode(parameter_dict)

    for i in properties:
        parameters = parameters + "&properties=" + i
    if extraparams != "":
        parameters = parameters + "&" + extraparams

    parameters = parameters + "&since=" + since

    parameters = parameters + "&includePropertyVersions=true"

    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def get_all_deals_v1(hapikey, app_private_token, properties, extraparams):
    data = list()
    hasmore = True
    offset = 0
    attempts = 0
    while hasmore:
        resp = get_deals_v1(hapikey, app_private_token, properties, offset, extraparams)
        try:
            yield resp["deals"]
            hasmore = resp["hasMore"]
            offset = resp["offset"]
            attempts = 0
        except KeyError as e:
            attempts += 1
            sleep(10)
            if attempts > 2:
                prefect.get_run_logger().error(resp)
                raise Exception(e)
    return data


def get_all_deals_v1_recent_modified(
    hapikey, app_private_token, properties, extraparams, since
):
    data = list()
    hasmore = True
    offset = 0
    attempts = 0
    while hasmore:
        resp = get_deals_v1_recent_modified(
            hapikey, app_private_token, properties, offset, extraparams, since
        )
        try:
            yield resp["results"]
            if len(resp["results"]) == 0 and offset < 10000:
                hasmore = False
            else:
                lasttimestamp = list(resp["results"])[0]["properties"][
                    "hs_lastmodifieddate"
                ]["timestamp"]
                attempts = 0
                hasmore = resp["hasMore"]
                offset = resp["offset"]
                attempts = 0
        except KeyError as e:
            if offset >= 10000:
                since = str(lasttimestamp)
                offset = 0

            attempts += 1
            sleep(10)
            if attempts > 2:
                prefect.get_run_logger().error(resp)
                raise Exception(e)
    return data
