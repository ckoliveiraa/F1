from abc import ABC, abstractmethod

from f1.domain.models import Driver, Lap, Meeting, Session


class MeetingRepository(ABC):
    @abstractmethod
    def get_meetings(self, year: int) -> list[Meeting]: ...


class SessionRepository(ABC):
    @abstractmethod
    def get_sessions(self, meeting_key: int, session_name: str) -> list[Session]: ...


class LapRepository(ABC):
    @abstractmethod
    def get_laps(self, session_key: int) -> list[Lap]: ...


class DriverRepository(ABC):
    @abstractmethod
    def get_drivers(self, session_key: int) -> list[Driver]: ...
