import requests
import json
import urllib
from retry import retry

@retry(tries=5, delay=1, jitter=1)
def get_all_owners(hapikey, app_private_token, next_url=None):
    if hapikey is not None:
        url = "https://api.hubapi.com/crm/v3/owners/?"
        parameter_dict = {"hapikey": hapikey}
        headers = {}
    else:
        if next_url is not None:
            url = next_url
        else:
            url = "https://api.hubapi.com/crm/v3/owners/"

        headers = {"content-type": "application/json", "cache-control": "no-cache",
                   'Authorization': f"Bearer {app_private_token}"}
        parameter_dict = ""

    parameters = urllib.parse.urlencode(parameter_dict)
    get_url = url + parameters
    r = requests.get(url=get_url, headers=headers)
    response_dict = json.loads(r.text)

    return response_dict
