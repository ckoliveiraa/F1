from unittest.mock import MagicMock, patch

import pytest
import requests

from f1.ingestion.http_client import HttpClient


@pytest.fixture
def http_client() -> HttpClient:
    return HttpClient(base_url="https://api.example.com", timeout=5)


def test_http_client_default_base_url() -> None:
    from f1.utils.config import BASE_URL

    client = HttpClient()
    assert client._base_url == BASE_URL


def test_http_client_custom_base_url() -> None:
    client = HttpClient(base_url="https://custom.api.com", timeout=3)
    assert client._base_url == "https://custom.api.com"
    assert client._timeout == 3


def test_get_returns_list(http_client: HttpClient) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = [{"id": 1}, {"id": 2}]
    mock_response.raise_for_status = MagicMock()

    with patch.object(
        http_client._session, "get", return_value=mock_response
    ) as mock_get:
        result = http_client.get("/meetings", params={"year": 2024})

    mock_get.assert_called_once_with(
        "https://api.example.com/meetings",
        params={"year": 2024},
        timeout=5,
    )
    assert result == [{"id": 1}, {"id": 2}]


def test_get_no_params(http_client: HttpClient) -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = MagicMock()

    with patch.object(http_client._session, "get", return_value=mock_response):
        result = http_client.get("/sessions")

    assert result == []


def test_get_raises_on_http_error(http_client: HttpClient) -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404")

    with patch.object(http_client._session, "get", return_value=mock_response):
        with pytest.raises(requests.HTTPError):
            http_client.get("/bad-path")


def test_build_session_has_retry_adapter(http_client: HttpClient) -> None:
    from requests.adapters import HTTPAdapter

    adapter = http_client._session.get_adapter("https://api.example.com")
    assert isinstance(adapter, HTTPAdapter)
