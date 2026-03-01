import pytest

from f1.domain.models import Meeting
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import OpenF1MeetingRepository


@pytest.mark.integration
def test_get_meetings_2024_returns_list() -> None:
    client = HttpClient()
    repo = OpenF1MeetingRepository(client)
    meetings = repo.get_meetings(2024)
    assert isinstance(meetings, list)
    assert len(meetings) > 0
    assert all(isinstance(m, Meeting) for m in meetings)


@pytest.mark.integration
def test_get_meetings_2024_has_expected_fields() -> None:
    client = HttpClient()
    repo = OpenF1MeetingRepository(client)
    meetings = repo.get_meetings(2024)
    first = meetings[0]
    assert first.year == 2024
    assert first.meeting_key > 0
    assert first.meeting_name != ""
