from asyncio import sleep
from logging import getLogger
from random import uniform
from ssl import SSLContext
from typing import Literal, Any, Self

from httpx import HTTPError, AsyncClient, URL, Response
from httpx._types import (
    CookieTypes,
    AuthTypes,
    QueryParamTypes,
    HeaderTypes,
    RequestExtensions,
    RequestContent,
    RequestData,
    RequestFiles,
)

from .models import JitterStrategyType


logger = getLogger(__name__)


class AsyncHttpClient:
    DEFAULT_MAX_ATTEMPTS = 5
    DEFAULT_BASE_DELAY = 1
    DEFAULT_MAX_DELAY = 30

    DEFAULT_REQUEST_TIMEOUT = 60

    DEFAULT_JITTER_STRATEGY = JitterStrategyType.full

    DEFAULT_RAISE_ON_MAX_ATTEMPTS = False
    DEFAULT_RETRY_NON_SUCCESS_RESPONSE = False

    DEFAULT_RETRY_EXCEPTIONS = (HTTPError, TimeoutError, ConnectionError)

    DEFAULT_ENCODING = "UTF-8"

    AVAILABLE_METHODS = Literal["GET", "POST", "PUT", "DELETE"]
    FOLLOW_REDIRECTS = False

    def __init__(
        self,
        base_url: URL | str = "",
        *,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        base_delay: int | float = DEFAULT_BASE_DELAY,
        max_delay: int | float = DEFAULT_MAX_DELAY,
        raise_on_max_attempts: bool = DEFAULT_RAISE_ON_MAX_ATTEMPTS,
        retry_non_success_response: bool = DEFAULT_RETRY_NON_SUCCESS_RESPONSE,
        auth: AuthTypes | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        verify: SSLContext | str | bool = True,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        default_encoding: str = DEFAULT_ENCODING,
    ) -> None:
        self.__client: AsyncClient | None = None

        self.max_attempts = max_attempts
        self.raise_on_max_attempts = raise_on_max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_non_success_responses = retry_non_success_response
        self.base_url = base_url
        self.timeout = timeout
        self.auth = auth
        self.params = params
        self.headers = headers
        self.cookies = cookies
        self.verify = verify
        self.default_encoding = default_encoding

    async def __aenter__(self) -> Self:
        self.__get_client()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def __get_client(self) -> AsyncClient:
        if not self.__client:
            self.__client = AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                auth=self.auth,
                params=self.params,
                headers=self.headers,
                cookies=self.cookies,
                verify=self.verify,
                default_encoding=self.default_encoding,
            )

            logger.debug("Made http async client")

        return self.__client

    @property
    def httpx_client(self) -> AsyncClient:
        return self.__get_client()

    async def close(self) -> None:
        if self.__client:
            await self.__client.aclose()
            self.__client = None

            logger.debug("Closed http async client")

    async def __send_request(
        self,
        method: AVAILABLE_METHODS,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
    ) -> Response:
        return await self.httpx_client.request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
        )

    async def __retry_with_backoff(
        self,
        method: AVAILABLE_METHODS,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        if raise_on_max_attempts is None:
            raise_on_max_attempts = self.raise_on_max_attempts

        if retry_non_success_responses is None:
            retry_non_success_responses = self.retry_non_success_responses

        response = None
        prev_delay = 0
        last_ex: type[Exception | None] = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = await self.__send_request(
                    method,
                    url,
                    content=content,
                    data=data,
                    files=files,
                    json=json,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    follow_redirects=follow_redirects,
                    timeout=timeout,
                    extensions=extensions,
                )

                if attempt == self.max_attempts:
                    self.__notify_fail(
                        url,
                        response,
                        last_ex,
                        raise_on_max_attempts,
                    )
                    break

                if retry_non_success_responses and not response.is_success:
                    prev_delay = await self.__delay(
                        jitter_strategy,
                        attempt,
                        prev_delay,
                    )
                    continue

                return response

            except retry_on as ex:
                if attempt == self.max_attempts:
                    self.__notify_fail(
                        url,
                        response,
                        last_ex,
                        raise_on_max_attempts,
                    )
                    break

                last_ex = ex

                prev_delay = await self.__delay(
                    jitter_strategy,
                    attempt,
                    prev_delay,
                )

    def __notify_fail(
        self,
        url: URL | str,
        response: Response | None,
        last_ex: type[Exception],
        raise_on_max_attempts: bool,
    ) -> None:
        if raise_on_max_attempts:
            raise last_ex or RuntimeError(
                f"Max retries exceeded. Base URL={self.base_url!r}, URL={url!r}"
            )

        logger.warning(
            "All attempts failed. Return none. Last exception=%r, status code=%r",
            last_ex,
            response.status_code if response else None,
        )

    async def __delay(
        self,
        jitter_strategy: JitterStrategyType,
        attempt: int,
        prev_delay: int | float = 0,
    ) -> float:
        delay = self.__get_delay(
            jitter_strategy,
            attempt,
            prev_delay,
        )

        await sleep(delay)

        logger.info(
            "Attempt failed, sleeping for %.2f seconds",
            delay,
        )

        return delay

    def __get_delay(
        self,
        jitter_strategy: JitterStrategyType,
        attempt: int,
        prev_delay: int | float = 0,
    ) -> float:
        exp = self.base_delay * (2**attempt)

        if jitter_strategy is jitter_strategy.none:
            return exp

        if jitter_strategy is jitter_strategy.full:
            return uniform(self.base_delay, exp)

        if jitter_strategy is jitter_strategy.equal:
            return exp / 2 + uniform(self.base_delay, exp / 2)

        if jitter_strategy is jitter_strategy.decorrelated:
            return min(self.max_delay, uniform(self.base_delay, prev_delay * 3))

        raise ValueError(f"Unknown strategy {jitter_strategy!r}")

    async def request(
        self,
        method: AVAILABLE_METHODS,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        return await self.__retry_with_backoff(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            retry_on=retry_on,
            jitter_strategy=jitter_strategy,
            raise_on_max_attempts=raise_on_max_attempts,
            retry_non_success_responses=retry_non_success_responses,
        )

    async def get(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        return await self.__retry_with_backoff(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            retry_on=retry_on,
            jitter_strategy=jitter_strategy,
            raise_on_max_attempts=raise_on_max_attempts,
            retry_non_success_responses=retry_non_success_responses,
        )

    async def post(
        self,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        return await self.__retry_with_backoff(
            "POST",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            retry_on=retry_on,
            jitter_strategy=jitter_strategy,
            raise_on_max_attempts=raise_on_max_attempts,
            retry_non_success_responses=retry_non_success_responses,
        )

    async def put(
        self,
        url: URL | str,
        *,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        return await self.__retry_with_backoff(
            "PUT",
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            retry_on=retry_on,
            jitter_strategy=jitter_strategy,
            raise_on_max_attempts=raise_on_max_attempts,
            retry_non_success_responses=retry_non_success_responses,
        )

    async def delete(
        self,
        url: URL | str,
        *,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        cookies: CookieTypes | None = None,
        follow_redirects: bool = FOLLOW_REDIRECTS,
        timeout: int | float = DEFAULT_REQUEST_TIMEOUT,
        extensions: RequestExtensions | None = None,
        retry_on: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        jitter_strategy: JitterStrategyType = DEFAULT_JITTER_STRATEGY,
        raise_on_max_attempts: bool | None = None,
        retry_non_success_responses: bool | None = None,
    ) -> Response | None:
        return await self.__retry_with_backoff(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            follow_redirects=follow_redirects,
            timeout=timeout,
            extensions=extensions,
            retry_on=retry_on,
            jitter_strategy=jitter_strategy,
            raise_on_max_attempts=raise_on_max_attempts,
            retry_non_success_responses=retry_non_success_responses,
        )
