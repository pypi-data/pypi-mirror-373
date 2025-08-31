import random
import asyncio

from typing import List, Literal, Iterator, Self, Dict, Any, Optional

import aiohttp

from pydantic import BaseModel
from typeguard import typechecked

from exceptions import NotCorrectArgumentError


class HTTPResponse(BaseModel):
    """Unific format for storage of HTTP response"""

    status: int
    url: str

    content_type: str
    headers: Dict[str, str]

    text: Optional[str] = None
    json: Optional[Dict[str, Any]] = None


@typechecked
class HTTPClient:
    """Client for HTTP"""

    def __init__(
        self,
        proxy_pool: Optional[List[str]] = None,
        proxy_type: str = "rotating",
        attempts: int = 3,
        base_delay: int | float = 1,
        timeout: int = 600,
        retry_policy: str = "exponential",
        logging_policy: str = "full",
        logger: Optional[Any] = None,
        raise_for_status: bool = True,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        """
        Client-adapter with performance library for working with HTTP.
        Current library: aiohttp.

        Args:
            proxy_pool (List[str], optional): Poll proxy via work (default None)
            proxy_type (str): Type of work with proxy, may be is 'sticky' or 'rotating' (default 'rotating')
            attempts (int): Number of attempts of requests (default 3)
            base_delay (int | float): First delay via requests (default 1)
            timeout (int): Timeout for requests
            retry_policy (str): Retry policy via requests, may be is 'linear' or 'exponential' (default 'exponential')
            logging_policy (str): Logging policy, may be is 'full', 'min', 'none' (default 'full')
            logger (LoggerLike): Logger
            raise_for_status (bool): calling exceptions for 4xx/5xx (default True)
            session (aiohttp.ClientSession, optional): Existing aiohttp session (default None)
        """
        self._proxy_pool = [self._setup_proxy(proxy) for proxy in proxy_pool] if proxy_pool else []
        self._proxy_type = proxy_type
        self._proxy_gen = self._get_proxy()

        self._attempts = attempts
        self._base_delay = base_delay
        self._retry_policy = retry_policy

        self._logging_policy = logging_policy
        self._logger = logger

        self._session: aiohttp.ClientSession = session or aiohttp.ClientSession(
            cookie_jar=aiohttp.DummyCookieJar(), timeout=aiohttp.ClientTimeout(total=timeout), raise_for_status=raise_for_status
        )

        self._valid_arguments()

    def _valid_arguments(self) -> None:
        """Verifing args"""
        not_correct: List[str] = []

        if self._proxy_type not in ("sticky", "rotating"):
            not_correct.append("proxy_type")
        if self._retry_policy not in ("exponential", "linear"):
            not_correct.append("retry_policy")
        if self._logging_policy not in ("full", "min", "none"):
            not_correct.append("logging_policy")

        if not_correct:
            raise NotCorrectArgumentError(
                "Troubles:\n -$" + "\n -".join(error + "can not be " + getattr(self, "_" + error) for error in not_correct)
            )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.down()

    async def down(self) -> None:
        """Closing"""
        await self._session.close()

    @staticmethod
    def _setup_proxy(proxy: str) -> str:
        """Setuping proxy to this format - 'http://{user}:{pass}@{ip}:{port}'"""
        if "http" not in proxy:
            return f"http://{proxy}"
        return proxy

    def _get_proxy(self) -> Iterator[Optional[str]]:
        """Give next proxy"""
        if self._proxy_type == "sticky":
            proxy = random.choice(self._proxy_pool) if self._proxy_pool else None
            while True:
                yield proxy
        else:
            while True:
                yield random.choice(self._proxy_pool) if self._proxy_pool else None

    async def _request(
        self,
        method: Literal["GET", "POST"],
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[HTTPResponse]:
        """Making request"""

        for attempt in range(1, self._attempts + 1):
            proxy = next(self._proxy_gen)
            if self._logger and self._logging_policy == "full":
                self._logger.debug(f"Попытка {attempt} запроса {method} к {url}")

            try:
                async with self._session.request(
                    method=method, url=url, headers=headers, json=json, params=params, cookies=cookies, proxy=proxy
                ) as request:
                    response = HTTPResponse(
                        status=request.status, url=str(request.url), content_type=request.content_type, headers=request.headers
                    )
                    if request.content_type == "application/json":
                        response.json = await request.json()
                    else:
                        response.text = await request.text()
                if self._logger and self._logging_policy in ("full", "min"):
                    self._logger.info(f"Запрос успешен, ответ: {response}")
                return response

            except Exception as error_type:
                if self._logger and self._logging_policy in ("full", "min"):
                    self._logger.error(f"Ошибка при {attempt} попытке {method} запроса к {url}: {error_type}")

            if self._retry_policy == "linear":
                timeout = self._base_delay * attempt
            else:
                timeout = self._base_delay**attempt
            if self._logger and self._logging_policy == "full":
                self._logger.debug(f"Задержка {timeout} секунд перед следующим запросом..")
            await asyncio.sleep(timeout)

        else:
            if self._logger and self._logging_policy in ("full", "min"):
                self._logger.error(f"После {self._attempts} не получилось получить ответа от {method} {url}. Возврат None..")

        return None

    async def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[HTTPResponse]:
        """
        GET-request.

        Args:
            url (str): Link
            headers (Dict[str, str], optional): headers (default None)
            params (Dict[str, str], optional): Parameters for URL (default None)
            cookies (Dict[str, str], optional): Cookies (default None)

        Return:
            HTTPResponse or None(if HTTP/aiohttp-errors)
        """
        return await self._request(method="GET", url=url, headers=headers, params=params, cookies=cookies)

    async def post(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
    ) -> Optional[HTTPResponse]:
        """
        POST-запрос.

        Args:
            url (str): Link
            headers (Dict[str, str], optional): Headers (default None)
            json (Dict[str, Any], optional): JSON for request (default None)
            params (Dict[str, str], optional): Parameters for URL (default None)
            cookies (Dict[str, str], optional): Cookies (default None)

        Return:
            HTTPResponse or None(if HTTP/aiohttp-errors)
        """
        return await self._request(method="POST", url=url, headers=headers, json=json, params=params, cookies=cookies)
