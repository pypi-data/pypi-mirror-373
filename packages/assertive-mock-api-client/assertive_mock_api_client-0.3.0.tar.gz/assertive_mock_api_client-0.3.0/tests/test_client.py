import pytest
from unittest.mock import patch, create_autospec
import json
from assertive import (
    as_json_matches,
    is_gte,
    is_eq,
    was_called_once_with,
    has_key_values,
)
from assertive.serialize import serialize
from assertive_mock_api_client import MockApiClient
import httpx


def test_basic_request_call():
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    with patch("httpx.post") as mock_httpx_post:
        mock_httpx_post.return_value = create_autospec(httpx.Response)

        mock_client.when_requested_with(path="/test", method="GET").respond_with_json(
            status_code=200, body={"hello": "world"}
        )

        assert mock_httpx_post == was_called_once_with(
            "http://localhost:8910/__mock__/stubs",
            json={
                "request": {
                    "path": "/test",
                    "method": "GET",
                },
                "action": {
                    "response": {
                        "status_code": 200,
                        "body": json.dumps({"hello": "world"}),
                        "headers": {"Content-Type": "application/json"},
                    }
                },
            },
        )


def test_json_request_call():
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    with patch("httpx.post") as mock_httpx_post:
        mock_httpx_post.return_value = create_autospec(httpx.Response)

        mock_client.when_requested_with(
            path="/test", method="GET", json={"hello": "world"}
        ).respond_with_json(status_code=200, body={"goodbye": "world"})

        assert mock_httpx_post == was_called_once_with(
            "http://localhost:8910/__mock__/stubs",
            json={
                "request": {
                    "path": "/test",
                    "method": "GET",
                    "body": serialize(as_json_matches({"hello": "world"})),
                },
                "action": {
                    "response": {
                        "status_code": 200,
                        "body": json.dumps({"goodbye": "world"}),
                        "headers": {"Content-Type": "application/json"},
                    }
                },
            },
        )


def test_request_call__raises_error_when_json_and_body_defined():
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    with patch("httpx.post") as mock_httpx_post:
        mock_httpx_post.return_value = create_autospec(httpx.Response)

        with pytest.raises(ValueError, match="Cannot specify both body and json"):
            mock_client.when_requested_with(
                path="/test", method="GET", json={"hello": "world"}, body="hello"
            ).respond_with_json(status_code=200, body={"goodbye": "world"})


def test_confirm_request():
    """Test the basic functionality of confirm_request with minimal parameters"""

    mock_client = MockApiClient(base_url="http://localhost:8910")

    with patch("httpx.post") as mock_httpx_post:
        mock_httpx_post.return_value = create_autospec(httpx.Response)

        mock_client.confirm_request(
            path="/test",
            method=is_eq("GET") | is_eq("POST"),
            headers={"Accept": "application/json"},
            query=has_key_values({"id": is_gte(1)}),
        )

        assert mock_httpx_post == was_called_once_with(
            "http://localhost:8910/__mock__/assert",
            json={
                "path": "/test",
                "method": serialize(is_eq("GET") | is_eq("POST")),
                "headers": {"Accept": "application/json"},
                "query": serialize(has_key_values({"id": is_gte(1)})),
                "times": serialize(is_gte(1)),
            },
        )
