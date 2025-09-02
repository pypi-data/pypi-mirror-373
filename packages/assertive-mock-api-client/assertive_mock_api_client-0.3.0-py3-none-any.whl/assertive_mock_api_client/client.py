import json
from typing import Any

from assertive import Criteria, as_json_matches, is_gte
from pydantic import BaseModel, Field
from assertive.serialize import serialize
import httpx


class StubRequestPayload(BaseModel):
    method: str | dict | None = None
    path: str | dict | None = None
    body: Any | None = None
    headers: dict | None = None
    host: str | dict | None = None
    query: dict | None = None


class StubResponsePayload(BaseModel):
    status_code: int
    headers: dict
    body: Any


class StubProxyPayload(BaseModel):
    url: str
    headers: dict = Field(default_factory=dict)
    timeout: int = 5


class StubActionPayload(BaseModel):
    response: StubResponsePayload | None = None
    proxy: StubProxyPayload | None = None


class StubPayload(BaseModel):
    request: StubRequestPayload
    action: StubActionPayload
    max_calls: int | None = None


class ApiAssertionPayload(BaseModel):
    path: str | dict | None = None
    method: str | dict | None = None
    headers: dict | None = None
    body: Any | None = None
    host: str | dict | None = None
    query: dict | None = None
    times: int | dict | None


class _PreActionedStub:
    def __init__(self, mock_api: "MockApiClient", request: StubRequestPayload):
        self.mock_api = mock_api
        self.request = request

    def respond_with(self, status_code: int, headers: dict, body: Any) -> None:
        """
        Responds with the given response.
        """
        response = StubResponsePayload(
            status_code=status_code,
            headers=headers,
            body=body,
        )

        action = StubActionPayload(response=response)
        stub = StubPayload(request=self.request, action=action)
        self.mock_api.create_stub(stub)

    def respond_with_json(
        self, status_code: int, body: dict, headers: dict = {}
    ) -> None:
        return self.respond_with(
            status_code=status_code,
            headers={"Content-Type": "application/json", **headers},
            body=json.dumps(body),
        )

    def proxy_to(self, url: str, headers: dict = {}, timeout: int = 5) -> None:
        """
        Proxies the request to the given URL.
        """
        proxy = StubProxyPayload(url=url, headers=headers, timeout=timeout)
        action = StubActionPayload(proxy=proxy)
        stub = StubPayload(request=self.request, action=action)
        self.mock_api.create_stub(stub)


class MockApiClient:
    def __init__(self, base_url: str = "http://localhost:8910"):
        self.base_url = base_url

    def when_requested_with(
        self,
        host: str | Criteria | None = None,
        headers: dict | Criteria | None = None,
        query: dict | Criteria | None = None,
        path: str | Criteria | None = None,
        method: str | Criteria | None = None,
        body: Any | None = None,
        json: Any | None = None,
    ) -> "_PreActionedStub":
        if json is not None and body is not None:
            raise ValueError("Cannot specify both body and json")

        if json is not None:
            body = as_json_matches(json)

        return _PreActionedStub(
            self,
            StubRequestPayload(
                headers=serialize(headers),
                path=serialize(path),
                method=serialize(method),
                body=serialize(body),
                host=serialize(host),
                query=serialize(query),
            ),
        )

    def create_stub(self, stub: StubPayload) -> None:
        """
        Stubs the request with the given stub.
        """

        # Convert the stub to a JSON object
        serialized_stub = stub.model_dump(exclude_unset=True, exclude_none=True)

        # Send the stub to the mock API server

        response = httpx.post(
            f"{self.base_url}/__mock__/stubs",
            json=serialized_stub,
        )

        response.raise_for_status()

    def confirm_request(
        self,
        host: str | Criteria | None = None,
        path: str | Criteria | None = None,
        method: str | Criteria | None = None,
        headers: dict | Criteria | None = None,
        body: Any | None = None,
        query: dict | Criteria | None = None,
        times: int | Criteria | None = is_gte(1),
    ) -> bool:
        """
        Confirms that the request was made.
        """

        assertion = ApiAssertionPayload(
            path=serialize(path),
            method=serialize(method),
            headers=serialize(headers),
            body=serialize(body),
            host=serialize(host),
            query=serialize(query),
            times=serialize(times),
        )

        response = httpx.post(
            f"{self.base_url}/__mock__/assert",
            json=assertion.model_dump(exclude_none=True, exclude_unset=True),
        )

        json_response = response.json()

        result = json_response["result"]

        return result
