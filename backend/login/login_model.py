import json
import keyring
import requests
import asyncio
import aiohttp
from dataclasses import dataclass, asdict
from backend.environments import api_url
from backend.local_storage import LocalStorage
from backend.http import Http, HttpMethod, GenericErrorBody, ResultType

@dataclass
class AuthMethodResp:
    email: bool
    password: bool
    sms: bool


async def login(username: str) -> AuthMethodResp:
    print("Getting auth methods")
    result = await Http(
            HttpMethod.GET,
            f"user/authOptions?unameMailPhone={username}",
            None,
            AuthMethodResp
        )

    if result.type == ResultType.SUCCESS:
        return result.success
    else:
        raise ValueError("API Returned An Error")
