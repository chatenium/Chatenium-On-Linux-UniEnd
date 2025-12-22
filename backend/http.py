from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from enum import Enum
from .environments import api_url
from backend.session_manager import SessionManager
import aiohttp
import json

T = TypeVar("T")
S = TypeVar("S")
E = TypeVar("E")

class ResultType(Enum):
    SUCCESS = "success"
    ERROR = "error"

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

@dataclass
class GenericErrorBody:
    error: str

@dataclass
class GenericSuccessBody:
    response: str

@dataclass
class Result(Generic[S, E]):
    type: ResultType
    success: S = None
    error: E = None

    @classmethod
    def ok(cls, value: S) -> "Result[S, E]":
        return cls(type=ResultType.SUCCESS, success=value)

    @classmethod
    def fail(cls, value: E) -> "Result[S, E]":
        return cls(type=ResultType.ERROR, error=value)

async def Http(method: HttpMethod, path: str, data: Optional[T], successType: type(S) = GenericSuccessBody, errorType: type(E) = GenericErrorBody) -> Result[S, E]:
    header = {}

    if SessionManager.instance().currentSession is not None:
        header = {"Authorization": SessionManager.instance().currentSession[0]}

    async with aiohttp.ClientSession(headers=header) as session:
        todo = session.get(f"{api_url}/{path}")

        if method == HttpMethod.POST:
            todo = session.post(f"{api_url}/{path}", data=json.dumps(data))

        async with todo as resp:
            body = await resp.json()

            if 200 <= resp.status < 300:
                if isinstance(body, list):
                    result = [successType(**item) for item in body]
                    return Result.ok(result)
                else:
                    return Result.ok(successType(**body))
            else:
                return Result.fail(errorType(**body))
