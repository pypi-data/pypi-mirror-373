import requests

from ... import auth


class ApiError(Exception):
    pass


class Client:
    _class_reasoner = None

    def __init__(
        self, reasoner=None, api_key=None, scheme=None, host=None, api_version=None
    ):
        self._reasoner = reasoner or self._class_reasoner
        if self._reasoner is None:
            raise ValueError("Please provide a reasoner")
        self._config = auth.Config(
            api_key=api_key, scheme=scheme, host=host, api_version=api_version
        )

    def eval(self, input: str, config=None):
        headers = self._config.get_headers()
        base_url = self._config.get_url()
        url = f"{base_url}/reasoners/{self._reasoner}/eval"

        json = {"input": input}
        if config:
            json["config"] = config

        response = requests.post(url, headers=headers, json=json)

        if response.status_code != 200:
            raise ApiError(response)

        return response.json()


try:
    from aiohttp import ClientSession

    class AsyncClient:
        _class_reasoner = None

        def __init__(
            self,
            session: ClientSession,
            reasoner: str | None = None,
            api_key: str | None = None,
            scheme: str | None = None,
            host: str | None = None,
            api_version: str | None = None,
        ):
            self._session = session
            self._reasoner = reasoner or self._class_reasoner
            if self._reasoner is None:
                raise ValueError("Please provide a reasoner")
            self._config = auth.Config(
                api_key=api_key, scheme=scheme, host=host, api_version=api_version
            )

        async def eval(self, input: str, config=None):
            headers = self._config.get_headers()
            base_url = self._config.get_url()
            url = f"{base_url}/reasoners/{self._reasoner}/eval"

            json = {"input": input}
            if config:
                json["config"] = config

            async with await self._session.post(
                url=url, json=json, headers=headers
            ) as resp:
                if resp.status != 200:
                    raise ApiError(resp)

                return await resp.json(content_type=None)
except ImportError:
    pass
