from datetime import datetime

import pytest
from pydantic import ValidationError

from f1.domain.models import Driver, FastestLapEntry, Lap, Meeting, Session


def test_meeting_valid() -> None:
    m = Meeting(
        meeting_key=1219,
        meeting_name="Bahrain Grand Prix",
        country_name="Bahrain",
        circuit_short_name="Bahrain",
        date_start=datetime(2024, 3, 2),
        year=2024,
    )
    assert m.meeting_key == 1219
    assert m.year == 2024


def test_session_valid() -> None:
    s = Session(session_key=9158, session_name="Race", session_type="Race")
    assert s.session_key == 9158


def test_lap_default_is_pit_out() -> None:
    lap = Lap(lap_number=1, lap_duration=90.0, driver_number=1)
    assert lap.is_pit_out_lap is False


def test_lap_none_duration() -> None:
    lap = Lap(lap_number=1, lap_duration=None, driver_number=1)
    assert lap.lap_duration is None


def test_driver_valid() -> None:
    d = Driver(
        driver_number=1,
        full_name="Max Verstappen",
        name_acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
    )
    assert d.name_acronym == "VER"


def test_fastest_lap_entry_valid() -> None:
    entry = FastestLapEntry(
        rank=1,
        driver_name="Max Verstappen",
        driver_acronym="VER",
        team_name="Red Bull Racing",
        team_colour="3671C6",
        lap_number=42,
        lap_duration=87.5,
    )
    assert entry.rank == 1
    assert entry.lap_duration == 87.5


def test_lap_invalid_driver_number() -> None:
    with pytest.raises(ValidationError):
        Lap(lap_number=1, lap_duration=90.0, driver_number="not_an_int")  # type: ignore[arg-type]
