from typing import Awaitable, Callable, ParamSpec, TypeVar

from httpx import HTTPStatusError, Response


P = ParamSpec("P")
R = TypeVar("R")


class ApiError(Exception):
    """
    Base Api error class
    """
    code: int = 500000
    detail: str = "Internal Server Error"

    def __init__(
        self,
        response: Response,
        detail: str | None = None,
        code: int | None = None
    ) -> None:
        self.response = response
        self.code = code or self.code
        self.detail = detail or self.detail

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.code} - {self.detail}"


class BadRequestError(ApiError):
    code = 400000
    detail = "Bad Request"


class ResourceNotFoundError(ApiError):
    code = 404000
    detail = "Resource Not Found"


class UnauthorizedError(ApiError):
    code = 401000
    detail = "Unauthorized"


class ForbiddenError(ApiError):
    code = 403000
    detail = "Forbidden"


class MethodNotAllowed(ApiError):
    code = 405000
    detail = "Method Not Allowed"


class RequestTimeoutError(ApiError):
    code = 408000
    detail = "Request Timeout"


class RateLimitExceededError(ApiError):
    code = 429000
    detail = "Rate Limit Exceeded"


class ConcurrencyLimitExceededError(ApiError):
    code = 429001
    detail = "Concurrency Limit Exceeded"


class ServiceUnavailableError(ApiError):
    code = 503000
    detail = "Service Unavailable"


class ValidationError(ApiError):
    code = 422000
    detail: dict = {}  # type: ignore[assignment]

    def __init__(
        self,
        response: Response,
        detail: dict | None = None,
        code: int | None = None
    ) -> None:
        self.response = response
        self.code = code or self.code
        self.detail = detail or self.detail



ErrorMap = {
    400000: BadRequestError,
    401000: UnauthorizedError,
    403000: ForbiddenError,
    404000: ResourceNotFoundError,
    405000: MethodNotAllowed,
    408000: RequestTimeoutError,
    422000: ValidationError,
    429000: RateLimitExceededError,
    429001: ConcurrencyLimitExceededError,
    500000: ApiError,
    503000: ServiceUnavailableError,
}


def err_from_response(response: Response) -> ApiError:
    try:
        body = (
            json
            if (json := response.json()) and isinstance(json, dict)
            else {}
        )
    except Exception:
        body = {}

    code = body.get("code", response.status_code * 1000)
    detail = body.get("detail", response.text or "An error occurred")

    raise ErrorMap.get(code, ApiError)(response, detail, code)


def to_api_error(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except HTTPStatusError as err:
            raise err_from_response(err.response) from err
        except Exception as err:
            raise err
    return wrapper


def to_api_error_async(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return await func(*args, **kwargs)
        except HTTPStatusError as err:
            raise err_from_response(err.response) from err
        except Exception as err:
            raise err
    return wrapper
