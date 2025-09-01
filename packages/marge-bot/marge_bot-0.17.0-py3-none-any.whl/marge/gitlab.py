import abc
import dataclasses
import logging as log
from typing import TYPE_CHECKING, Any, Callable, Optional, Union, cast

import gitlab
import requests


class Api:
    def __init__(self, gitlab_url: str, auth_token: str) -> None:
        self._auth_token = auth_token
        self._api_base_url = gitlab_url.rstrip("/") + "/api/v4"
        self._gitlab = gitlab.Gitlab(gitlab_url, auth_token)

    def call(
        self, command: "Command", sudo: Optional[int] = None
    ) -> Union[bool, dict[str, Any], list[dict[str, Any]]]:
        method = command.method
        url = self._api_base_url + command.endpoint
        kwargs: dict[str, Any] = {}
        if sudo:
            kwargs["sudo"] = sudo
        log.debug("REQUEST: %s %s %s %r", method, url, sudo, command.call_args)
        # Timeout to prevent indefinitely hanging requests. 60s is very conservative,
        # but should be short enough to not cause any practical annoyances. We just
        # crash rather than retry since marge-bot should be run in a restart loop anyway.
        try:
            response = self._gitlab.http_request(
                method,
                command.endpoint,
                timeout=60,
                retry_transient_errors=True,
                **command.call_args,
                **kwargs,
            )
        except requests.exceptions.Timeout as err:
            log.error("Request timeout: %s", err)
            raise
        except gitlab.GitlabHttpError as err:
            code = err.response_code
            errors = {
                400: BadRequest,
                401: Unauthorized,
                403: Forbidden,
                404: NotFound,
                405: MethodNotAllowed,
                409: Conflict,
                422: Unprocessable,
                500: InternalServerError,
            }

            if code in errors:
                raise errors[code](*err.args) from err

            if code is not None and 500 < code < 600:
                raise InternalServerError(*err.args) from err

            raise UnexpectedError(*err.args) from err

        log.debug("RESPONSE CODE: %s", response.status_code)
        log.debug("RESPONSE BODY: %r", response.content)

        if response.status_code == 202:
            return True  # Accepted

        if response.status_code == 204:
            return True  # NoContent

        return command.extract(response.json()) if command.extract else response.json()

    def collect_all_pages(self, get_command: "GET") -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        fetch_again, page_no = True, 1
        while fetch_again:
            page = self.call(get_command.for_page(page_no))
            if page:
                if TYPE_CHECKING:
                    assert isinstance(page, list)
                result.extend(page)
                page_no += 1
            else:
                fetch_again = False

        return result


def from_singleton_list(
    fun: Optional[Callable[[dict[str, Any]], Any]] = None,
) -> Callable[[list[dict[str, Any]]], Any]:
    def extractor(response_list: list[dict[str, Any]]) -> Any:
        assert isinstance(response_list, list), type(response_list)
        assert len(response_list) <= 1, len(response_list)
        if not response_list:
            return None
        if fun is None:
            return response_list[0]
        return fun(response_list[0])

    return extractor


@dataclasses.dataclass(frozen=True)
class Command(abc.ABC):
    endpoint: str
    args: dict[str, Any] = dataclasses.field(default_factory=dict)
    extract: Optional[Callable[[list[dict[str, Any]]], dict[str, Any]]] = None

    @property
    def method(self) -> str:
        return self.__class__.__name__

    @property
    def call_args(self) -> dict[str, Any]:
        return {"post_data": self.args}


class GET(Command):
    @property
    def call_args(self) -> dict[str, Any]:
        return {"query_data": self.args}

    def for_page(self, page_no: int) -> "GET":
        args = self.args
        return dataclasses.replace(self, args=dict(args, page=page_no, per_page=100))


class PUT(Command):
    pass


class POST(Command):
    pass


class DELETE(Command):
    pass


class ApiError(gitlab.GitlabHttpError):
    @property
    def error_message(self) -> str:
        return self._error_message

    @error_message.setter
    def error_message(self, error: Union[str, dict[str, Any]]) -> None:
        # Might be as deep as {"message": {"base": ["real message"]}}
        if isinstance(error, dict) and "base" in error:
            error = cast(dict[str, Any], error.get("base"))

        if isinstance(error, list) and len(error) == 1:
            error = error[0]

        if TYPE_CHECKING:
            assert isinstance(error, str)
        self._error_message = error


class BadRequest(ApiError):
    pass


class Unauthorized(ApiError):
    pass


class Forbidden(ApiError):
    pass


class NotFound(ApiError):
    pass


class MethodNotAllowed(ApiError):
    pass


class Conflict(ApiError):
    pass


class Unprocessable(ApiError):
    pass


class InternalServerError(ApiError):
    pass


class UnexpectedError(ApiError):
    pass


class Resource(abc.ABC):
    def __init__(self, api: Api, info: dict[str, Any]):
        self._info = info
        self._api = api

    @property
    def info(self) -> dict[str, Any]:
        return self._info

    @property
    @abc.abstractmethod
    def id(self) -> Union[int, str]:  # pylint: disable=invalid-name
        ...

    @property
    def api(self) -> Api:
        return self._api

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._api}, {self.info})"
