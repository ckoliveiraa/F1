from unittest.mock import MagicMock

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)


def _mock_client(return_value: list[dict]) -> MagicMock:
    client = MagicMock()
    client.get.return_value = return_value
    return client


def test_meeting_repo_parses_valid_data() -> None:
    data = [
        {
            "meeting_key": 1219,
            "meeting_name": "Bahrain Grand Prix",
            "country_name": "Bahrain",
            "circuit_short_name": "Bahrain",
            "date_start": "2024-03-02T00:00:00",
            "year": 2024,
        }
    ]
    repo = OpenF1MeetingRepository(_mock_client(data))
    meetings = repo.get_meetings(2024)

    assert len(meetings) == 1
    assert isinstance(meetings[0], Meeting)
    assert meetings[0].meeting_key == 1219


def test_meeting_repo_skips_invalid_data() -> None:
    data = [{"bad": "data"}]
    repo = OpenF1MeetingRepository(_mock_client(data))
    meetings = repo.get_meetings(2024)
    assert meetings == []


def test_meeting_repo_empty_response() -> None:
    repo = OpenF1MeetingRepository(_mock_client([]))
    assert repo.get_meetings(2024) == []


def test_session_repo_parses_valid_data() -> None:
    data = [
        {
            "session_key": 9158,
            "session_name": "Race",
            "session_type": "Race",
        }
    ]
    repo = OpenF1SessionRepository(_mock_client(data))
    sessions = repo.get_sessions(1219, "Race")

    assert len(sessions) == 1
    assert isinstance(sessions[0], Session)
    assert sessions[0].session_key == 9158


def test_session_repo_skips_invalid_data() -> None:
    repo = OpenF1SessionRepository(_mock_client([{"bad": "data"}]))
    assert repo.get_sessions(1219, "Race") == []


def test_lap_repo_parses_valid_data() -> None:
    data = [
        {
            "lap_number": 1,
            "lap_duration": 90.123,
            "driver_number": 1,
            "is_pit_out_lap": False,
        }
    ]
    repo = OpenF1LapRepository(_mock_client(data))
    laps = repo.get_laps(9158)

    assert len(laps) == 1
    assert isinstance(laps[0], Lap)
    assert laps[0].lap_duration == 90.123


def test_lap_repo_skips_invalid_data() -> None:
    repo = OpenF1LapRepository(_mock_client([{"bad": "data"}]))
    assert repo.get_laps(9158) == []


def test_driver_repo_parses_valid_data() -> None:
    data = [
        {
            "driver_number": 1,
            "full_name": "Max Verstappen",
            "name_acronym": "VER",
            "team_name": "Red Bull Racing",
            "team_colour": "3671C6",
        }
    ]
    repo = OpenF1DriverRepository(_mock_client(data))
    drivers = repo.get_drivers(9158)

    assert len(drivers) == 1
    assert isinstance(drivers[0], Driver)
    assert drivers[0].name_acronym == "VER"


def test_driver_repo_skips_invalid_data() -> None:
    repo = OpenF1DriverRepository(_mock_client([{"bad": "data"}]))
    assert repo.get_drivers(9158) == []
