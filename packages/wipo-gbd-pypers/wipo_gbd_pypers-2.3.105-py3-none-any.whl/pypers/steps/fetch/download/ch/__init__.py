from os.path import realpath, dirname
from pypers import import_all
import requests


def get_auth_token(config):
    # Encode the client ID and client secret
    #authorization = base64.b64encode(bytes(self.config["username"] + ":" + self.config["password"], "ISO-8859-1")).decode("ascii")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "username": config["credentials"]["user"],
        "password": config["credentials"]["password"],
        "client_id": "datadelivery-api-client",
        "grant_type": "password"
    }

    auth_end_url = "https://"+config["apiIpiHost"]+"/auth/realms/egov/protocol/openid-connect/token"

    response = requests.post(auth_end_url, data=body, headers=headers, verify=False)
    if response.status_code == 200:
        payload = response.json()
    elif response.status_code == 401 or response.status_code == 403:
        raise Exception("invalid crendentials")
    else:
        raise Exception("error from authentication service")

    return payload.get('access_token', None)


# Import all Steps in this directory.
import_all(namespace=globals(), dir=dirname(realpath(__file__)))