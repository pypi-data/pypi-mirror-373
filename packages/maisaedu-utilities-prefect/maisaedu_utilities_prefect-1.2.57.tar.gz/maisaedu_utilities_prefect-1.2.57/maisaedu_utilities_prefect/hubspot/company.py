
import prefect
import requests
import json
import urllib
from time import sleep


def getCompanies(hapikey, app_private_token, properties, offset, tries=5):
    url = "https://api.hubapi.com/companies/v2/companies/paged?"
    if hapikey is not None:
        parameter_dict = {"hapikey": hapikey, "limit": 25}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
    else:
        parameter_dict = {"limit": 25}
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
    get_url = url + parameters
    for i in range(tries):
        try:
            r = requests.get(url=get_url, headers=headers)
            response_dict = json.loads(r.text)
            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)


def getAllCompanies(hapikey, app_private_token, properties):
    hasmore = True
    offset = 0
    attempts = 0

    while hasmore:
        resp = getCompanies(hapikey, app_private_token, properties, offset)
        resp_merged_with_history = []
        try:
            hasmore = resp["has-more"]
            offset = resp["offset"]
            resp_with_history = get_companies_with_properties_history(hapikey, app_private_token, properties, resp["companies"])

            for company in resp["companies"]:
                for record in resp_with_history:
                    if company["companyId"] == int(record["id"]):
                        company["propertiesWithHistory"] = record["propertiesWithHistory"]
                        resp_merged_with_history.append(company)
                
            yield resp_merged_with_history
            attempts = 0
        except KeyError as e:
            if "status" in resp and resp["status"] == "error":
                attempts += 1
                sleep(10)
                if attempts > 2:
                    raise Exception(resp["message"])
            else:
                hasmore = False


def get_companies_with_properties_history(hapikey, app_private_token, properties, data):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read?"
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}
        parameters = urllib.parse.urlencode(parameter_dict)
    else:
        url = "https://api.hubapi.com/crm/v3/objects/companies/batch/read"
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }
        parameters = ""

    post_url = url + parameters


    post_data = {
        "properties": [prop for prop in properties],
        "propertiesWithHistory": [prop for prop in properties],
        "inputs": [{"id": i["companyId"]} for i in data],
        "limit": 100,
    }

    results_part = []

    attempts = 0

    while len(results_part) == 0:
        try:
            r = requests.post(
                url=post_url, headers=headers, data=json.dumps(post_data)
            )
            attempts = 0
            response_dict = json.loads(r.text)
            if len(response_dict["results"]) == 0:
                break
            results_part = response_dict["results"]
        except Exception as e:
            attempts += 1
            if attempts > 2:
                raise e
            sleep(10)
 
    return results_part