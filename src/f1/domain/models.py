from datetime import datetime

from pydantic import BaseModel


class Meeting(BaseModel):
    meeting_key: int
    meeting_name: str
    country_name: str
    circuit_short_name: str
    date_start: datetime
    year: int


class Session(BaseModel):
    session_key: int
    session_name: str
    session_type: str


class Lap(BaseModel):
    lap_number: int
    lap_duration: float | None
    driver_number: int
    is_pit_out_lap: bool = False


class Driver(BaseModel):
    driver_number: int
    full_name: str
    name_acronym: str
    team_name: str
    team_colour: str


class FastestLapEntry(BaseModel):
    rank: int
    driver_name: str
    driver_acronym: str
    team_name: str
    team_colour: str
    lap_number: int
    lap_duration: float
