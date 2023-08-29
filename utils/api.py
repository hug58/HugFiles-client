import requests
import json
from urllib.parse import urljoin


class Api:
    def __init__(self, url):
        self.url = url
    
    def get_token(self, email:str) -> str:
        url = urljoin(self.url, "/token")
        response = requests.post(url, json={"email": email}, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            code = response.json()["code"]
            return code
        return ""