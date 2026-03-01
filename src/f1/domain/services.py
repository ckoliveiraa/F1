from f1.domain.models import FastestLapEntry, Meeting
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingRepository,
    SessionRepository,
)
from f1.processing.lap_processor import compute_top_n_laps
from f1.utils.config import TOP_N_LAPS
from f1.utils.logger import get_logger

logger = get_logger(__name__)


class F1DashboardService:
    def __init__(
        self,
        meeting_repo: MeetingRepository,
        session_repo: SessionRepository,
        lap_repo: LapRepository,
        driver_repo: DriverRepository,
    ) -> None:
        self._meeting_repo = meeting_repo
        self._session_repo = session_repo
        self._lap_repo = lap_repo
        self._driver_repo = driver_repo

    def get_meetings_for_year(self, year: int) -> list[Meeting]:
        logger.info("Fetching meetings for year %s", year)
        return self._meeting_repo.get_meetings(year)

    def get_top_laps_for_meeting(
        self, meeting_key: int, session_name: str
    ) -> list[FastestLapEntry]:
        logger.info(
            "Fetching top laps for meeting %s / session %s", meeting_key, session_name
        )
        sessions = self._session_repo.get_sessions(meeting_key, session_name)
        if not sessions:
            logger.warning(
                "No sessions found for meeting %s / %s", meeting_key, session_name
            )
            return []

        session = sessions[0]
        laps = self._lap_repo.get_laps(session.session_key)
        drivers = self._driver_repo.get_drivers(session.session_key)
        return compute_top_n_laps(laps, drivers, TOP_N_LAPS)
