import json
from dataclasses import dataclass, asdict

import requests

from UniEnd.environments import api_url


def login(username: str, password: str) -> str:
    print("login attempt")
    body = json.dumps(asdict(LoginPayload(username, password)))
    print(body)
    response = requests.post(f"{api_url}/user/login", data=body)
    if response.status_code == 200:
        print("login successful")
    else:
        raise LoginRespError(json.loads(response.text))
    print(response.text)

    return username

@dataclass
class LoginPayload:
    unameMail: str
    password: str

class LoginRespError(Exception):
    def __init__(self, error_dict: dict):
        super().__init__(str(error_dict))

        self.unameMailError = error_dict.get('unameMailError')
        self.passwordError = error_dict.get('passwordError')