import json
import keyring
from dataclasses import dataclass, asdict

import requests

from UniEnd.environments import api_url
from UniEnd.shared.local_storage import LocalStorage


def login(username: str, password: str) -> str:
    body = json.dumps(asdict(LoginPayload(username, password)))
    response = requests.post(f"{api_url}/user/login", data=body)
    if response.status_code == 200:
        print("login successful")
        decoded_resp = LoginRespOk(**json.loads(response.text))

        keyring.set_password("chatenium_universal_backend", f"token_{decoded_resp.userid}", decoded_resp.token)
        LocalStorage.write(f"userdata_{decoded_resp.userid}", asdict(UserData(
            displayName=decoded_resp.displayName,
            username=decoded_resp.username,
            pfp=decoded_resp.pfp,
            userid=decoded_resp.userid
        )))
        print("Keyring write successful + Cache write successful")
    else:
        raise LoginRespError(json.loads(response.text))
    print(response.text)

    return username

@dataclass
class UserData:
    displayName: str
    username: str
    pfp: str
    userid: str

@dataclass
class LoginRespOk:
    displayName: str
    username: str
    pfp: str
    userid: str
    token: str

@dataclass
class LoginPayload:
    unameMail: str
    password: str

class LoginRespError(Exception):
    def __init__(self, error_dict: dict):
        super().__init__(str(error_dict))

        self.unameMailError = error_dict.get('unameMailError')
        self.passwordError = error_dict.get('passwordError')