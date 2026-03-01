from unittest.mock import MagicMock

from f1.domain.models import Driver, FastestLapEntry, Lap, Meeting, Session
from f1.domain.services import F1DashboardService


def _make_service(
    meetings: list[Meeting] | None = None,
    sessions: list[Session] | None = None,
    laps: list[Lap] | None = None,
    drivers: list[Driver] | None = None,
) -> F1DashboardService:
    meeting_repo = MagicMock()
    meeting_repo.get_meetings.return_value = meetings or []

    session_repo = MagicMock()
    session_repo.get_sessions.return_value = sessions or []

    lap_repo = MagicMock()
    lap_repo.get_laps.return_value = laps or []

    driver_repo = MagicMock()
    driver_repo.get_drivers.return_value = drivers or []

    return F1DashboardService(
        meeting_repo=meeting_repo,
        session_repo=session_repo,
        lap_repo=lap_repo,
        driver_repo=driver_repo,
    )


def test_get_meetings_for_year_delegates_to_repo() -> None:
    from datetime import datetime

    expected = [
        Meeting(
            meeting_key=1,
            meeting_name="GP Test",
            country_name="Test",
            circuit_short_name="T",
            date_start=datetime(2024, 1, 1),
            year=2024,
        )
    ]
    service = _make_service(meetings=expected)
    result = service.get_meetings_for_year(2024)
    assert result == expected
    service._meeting_repo.get_meetings.assert_called_once_with(2024)  # type: ignore[attr-defined]


def test_get_top_laps_no_sessions_returns_empty() -> None:
    service = _make_service(sessions=[])
    result = service.get_top_laps_for_meeting(meeting_key=1, session_name="Race")
    assert result == []


def test_get_top_laps_delegates_repos() -> None:
    session = Session(session_key=99, session_name="Race", session_type="Race")
    lap = Lap(lap_number=1, lap_duration=90.0, driver_number=1)
    driver = Driver(
        driver_number=1,
        full_name="Max Verstappen",
        name_acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    service = _make_service(sessions=[session], laps=[lap], drivers=[driver])
    result = service.get_top_laps_for_meeting(meeting_key=1, session_name="Race")

    assert len(result) == 1
    assert isinstance(result[0], FastestLapEntry)
    assert result[0].driver_acronym == "VER"

    service._lap_repo.get_laps.assert_called_once_with(99)  # type: ignore[attr-defined]
    service._driver_repo.get_drivers.assert_called_once_with(99)  # type: ignore[attr-defined]
