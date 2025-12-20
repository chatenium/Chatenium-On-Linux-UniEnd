from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from enum import Enum
from .environments import api_url
import aiohttp

T = TypeVar("RequestBody")
S = TypeVar("SuccessResponse")
E = TypeVar("ErrorResponse")

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

async def Http(method: HttpMethod, path: str, data: Optional[T], successType: type(S), errorType: type(E) = GenericErrorBody) -> Result[S, E]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{api_url}/{path}") as resp:
            body = await resp.json()

            if 200 <= resp.status < 300:
                return Result.ok(successType(**body))
            else:
                return Result.fail(errorType(**body))
