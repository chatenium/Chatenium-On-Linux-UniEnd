from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from enum import Enum
from .environments import api_url
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
        
async def Http(method: HttpMethod, path: str, data: Optional[T],
               successType: type(S) = GenericSuccessBody,
               errorType: type(E) = GenericErrorBody) -> Result[S, E]:

    async with aiohttp.ClientSession() as session:
        if method == HttpMethod.GET:
            async with session.get(f"{api_url}/{path}") as resp:
                body = await resp.json()
        elif method == HttpMethod.POST:
            async with session.post(f"{api_url}/{path}", data=json.dumps(data)) as resp:
                body = await resp.json()
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if 200 <= resp.status < 300:
            return Result.ok(successType(**body))
        else:
            return Result.fail(errorType(**body))
