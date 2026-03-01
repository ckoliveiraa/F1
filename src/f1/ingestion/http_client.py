import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from f1.utils.config import BASE_URL, REQUEST_TIMEOUT
from f1.utils.logger import get_logger

logger = get_logger(__name__)


class HttpClient:
    def __init__(
        self, base_url: str = BASE_URL, timeout: int = REQUEST_TIMEOUT
    ) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def get(self, path: str, params: dict | None = None) -> list[dict]:
        url = f"{self._base_url}{path}"
        logger.info("GET %s params=%s", url, params)
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()
