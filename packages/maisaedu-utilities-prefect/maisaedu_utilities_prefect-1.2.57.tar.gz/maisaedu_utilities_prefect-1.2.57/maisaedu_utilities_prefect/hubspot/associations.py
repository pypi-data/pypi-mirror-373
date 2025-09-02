import prefect
import requests
import json
import urllib
from retry import retry

def get_associations(hapikey, app_private_token, fromType, toType, ids, tries=5):
    url = "https://api.hubapi.com/crm/v3/associations/%s/%s/batch/read?" % (
        fromType,
        toType,
    )
    if hapikey is not None:
        parameter_dict = {"hapikey": hapikey}
        headers = {"content-type": "application/json", "cache-control": "no-cache"}

    else:
        parameter_dict = {"a": "a"}
        headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
            "Authorization": f"Bearer {app_private_token}",
        }

    parameters = urllib.parse.urlencode(parameter_dict)

    body = json.dumps({"inputs": ids})

    post_url = url + parameters
    for i in range(tries):
        try:
            r = requests.post(url=post_url, headers=headers, data=body)
            response_dict = json.loads(r.text)

            return response_dict
        except Exception as e:
            prefect.get_run_logger().error(e)

@retry(tries=5, delay=1, jitter=2)
def get_all_associations(
    hapikey, app_private_token, fromType, toType, ids, batch_size=1000
):
    list_df = [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]

    for i in list_df:
        resp = get_associations(hapikey, app_private_token, fromType, toType, i)
        yield resp["results"]
