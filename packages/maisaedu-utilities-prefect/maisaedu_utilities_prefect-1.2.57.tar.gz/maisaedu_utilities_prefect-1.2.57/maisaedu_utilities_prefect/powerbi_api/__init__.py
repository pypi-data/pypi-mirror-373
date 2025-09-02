import json

def get_power_bi_api_credentials(credentials_file_path: str = "data/powerbi-api-credentials.json"):
    with open(credentials_file_path) as f:
        r = f.read()
        return json.loads(r)