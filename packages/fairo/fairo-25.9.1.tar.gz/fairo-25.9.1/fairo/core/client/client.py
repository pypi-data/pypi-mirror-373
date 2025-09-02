# base_client.py
import requests
from requests.auth import HTTPBasicAuth

class BaseClient:
    def __init__(self, base_url: str, username: str = None, password: str = None, fairo_auth_token: str = None):
        self.base_url = base_url
        self.session = requests.Session()
        if username is not None and password is not None:
            self.session.auth = HTTPBasicAuth(username, password)
        elif fairo_auth_token is not None:
            self.session.headers.update({
                "Authorization": f"Bearer {fairo_auth_token}"
            })
        else:
            raise ValueError("Must provide either username/password or fairo_auth_token")
        self.session.headers.update({
            "Content-Type": "application/json",
        })

    def get(self, endpoint: str, params=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data=None, json=None):
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json)
        response.raise_for_status()
        return response.json()
