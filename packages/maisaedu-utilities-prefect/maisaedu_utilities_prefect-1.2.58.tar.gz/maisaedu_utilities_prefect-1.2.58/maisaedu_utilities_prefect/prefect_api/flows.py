import requests


def check_flow_already_running_on_another_call(
    prefect_api_key,
    prefect_api_url,
    deployment_id=None,
    deployment_name=None,
    check_parameters=None,
):
    if deployment_id is None and deployment_name is None:
        return False

    headers = {"Authorization": f"Bearer {prefect_api_key}"}
    endpoint_task_runs = f"{prefect_api_url}/flow_runs"

    deployment_obj = {}

    if deployment_id is not None:
        deployment_obj = {"id": {"any_": [deployment_id]}}
    elif deployment_name is not None:
        deployment_obj = {"name": {"any_": [deployment_name]}}

    body = {
        "deployments": deployment_obj,
        "flow_runs": {"state": {"name": {"any_": ["Running"]}}},
    }

    endpoint = f"{endpoint_task_runs}/filter"

    attempts = 0
    while True:
        response = requests.post(endpoint, headers=headers, json=body, timeout=60)
        attempts += 1
        if response.status_code != 200:
            if attempts > 5:
                raise Exception(
                    f"Failed to retrieve flows runs of deployment {deployment_id}. Status code: {response.status_code}"
                )
            
        if response.status_code == 200:
            flow_runs = response.json()
            break

    if len(flow_runs) > 1:  # 1 because the flow is running on this call
        if check_parameters is not None:
            return __check_parameters(flow_runs, check_parameters)
        else:
            return True
    else:
        return False


def __check_parameters(flow_runs, check_parameters):
    r = False
    for flow_run in flow_runs:
        for key in check_parameters:
            if flow_run["parameters"][key] == check_parameters[key]:
                r = True
    return r
