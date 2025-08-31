Example:
```python
from asyncio import run
from asyncio import gather
from random import choice

from http_extended_client import AsyncHttpClient


async def main() -> None:
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        "/get_100",
        "/get_80",
        "/get_50",
        "/get_20",
        "/get_0",
    ]
    request_count = 20

    client = AsyncHttpClient(
        base_url,
        retry_non_success_response=True,
        raise_on_max_attempts=True,
    )

    tasks = [client.get(choice(endpoints)) for _ in range(request_count)]

    await gather(*tasks)


if __name__ == "__main__":
    run(main())
```