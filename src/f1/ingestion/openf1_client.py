import requests

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingRepository,
    SessionRepository,
)
from f1.ingestion.http_client import HttpClient
from f1.utils.logger import get_logger

logger = get_logger(__name__)


class OpenF1MeetingRepository(MeetingRepository):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_meetings(self, year: int) -> list[Meeting]:
        try:
            data = self._client.get("/meetings", params={"year": year})
        except requests.exceptions.RequestException as exc:
            logger.warning("HTTP error fetching meetings year=%s: %s", year, exc)
            return []
        meetings: list[Meeting] = []
        for item in data:
            try:
                meetings.append(Meeting.model_validate(item))
            except Exception:
                logger.warning("Failed to parse meeting: %s", item)
        return meetings


class OpenF1SessionRepository(SessionRepository):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_sessions(self, meeting_key: int, session_name: str) -> list[Session]:
        try:
            data = self._client.get(
                "/sessions",
                params={"meeting_key": meeting_key, "session_name": session_name},
            )
        except requests.exceptions.RequestException as exc:
            logger.warning(
                "HTTP error fetching sessions meeting=%s session=%s: %s",
                meeting_key,
                session_name,
                exc,
            )
            return []
        sessions: list[Session] = []
        for item in data:
            try:
                sessions.append(Session.model_validate(item))
            except Exception:
                logger.warning("Failed to parse session: %s", item)
        return sessions


class OpenF1LapRepository(LapRepository):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_laps(self, session_key: int) -> list[Lap]:
        try:
            data = self._client.get("/laps", params={"session_key": session_key})
        except requests.exceptions.RequestException as exc:
            logger.warning("HTTP error fetching laps session=%s: %s", session_key, exc)
            return []
        laps: list[Lap] = []
        for item in data:
            try:
                laps.append(Lap.model_validate(item))
            except Exception:
                logger.warning("Failed to parse lap: %s", item)
        return laps


class OpenF1DriverRepository(DriverRepository):
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_drivers(self, session_key: int) -> list[Driver]:
        try:
            data = self._client.get("/drivers", params={"session_key": session_key})
        except requests.exceptions.RequestException as exc:
            logger.warning(
                "HTTP error fetching drivers session=%s: %s", session_key, exc
            )
            return []
        drivers: list[Driver] = []
        for item in data:
            try:
                drivers.append(Driver.model_validate(item))
            except Exception:
                logger.warning("Failed to parse driver: %s", item)
        return drivers
