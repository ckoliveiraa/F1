import pytest

from f1.domain.models import Driver, Lap


@pytest.fixture
def sample_laps() -> list[Lap]:
    return [
        Lap(lap_number=1, lap_duration=90.123, driver_number=1, is_pit_out_lap=False),
        Lap(lap_number=2, lap_duration=89.456, driver_number=44, is_pit_out_lap=False),
        Lap(lap_number=3, lap_duration=None, driver_number=1, is_pit_out_lap=False),
        Lap(lap_number=4, lap_duration=88.999, driver_number=16, is_pit_out_lap=True),
        Lap(lap_number=5, lap_duration=87.500, driver_number=55, is_pit_out_lap=False),
        Lap(lap_number=6, lap_duration=91.000, driver_number=44, is_pit_out_lap=False),
    ]


@pytest.fixture
def sample_drivers() -> list[Driver]:
    return [
        Driver(
            driver_number=1,
            full_name="Max Verstappen",
            name_acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        Driver(
            driver_number=44,
            full_name="Lewis Hamilton",
            name_acronym="HAM",
            team_name="Mercedes",
            team_colour="27F4D2",
        ),
        Driver(
            driver_number=16,
            full_name="Charles Leclerc",
            name_acronym="LEC",
            team_name="Ferrari",
            team_colour="E8002D",
        ),
        Driver(
            driver_number=55,
            full_name="Carlos Sainz",
            name_acronym="SAI",
            team_name="Ferrari",
            team_colour="E8002D",
        ),
    ]
