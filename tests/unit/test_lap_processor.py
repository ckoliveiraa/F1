from f1.domain.models import Driver, Lap
from f1.processing.lap_processor import (
    build_driver_index,
    compute_top_n_laps,
    filter_valid_laps,
)


def test_filter_valid_laps_removes_none_duration(sample_laps: list[Lap]) -> None:
    result = filter_valid_laps(sample_laps)
    assert all(lap.lap_duration is not None for lap in result)


def test_filter_valid_laps_removes_pit_out(sample_laps: list[Lap]) -> None:
    result = filter_valid_laps(sample_laps)
    assert all(not lap.is_pit_out_lap for lap in result)


def test_filter_valid_laps_count(sample_laps: list[Lap]) -> None:
    # sample_laps has 1 None duration and 1 pit out → 4 valid
    result = filter_valid_laps(sample_laps)
    assert len(result) == 4


def test_filter_valid_laps_empty() -> None:
    assert filter_valid_laps([]) == []


def test_build_driver_index(sample_drivers: list[Driver]) -> None:
    index = build_driver_index(sample_drivers)
    assert 1 in index
    assert index[1].name_acronym == "VER"
    assert len(index) == 4


def test_build_driver_index_empty() -> None:
    assert build_driver_index([]) == {}


def test_compute_top_n_laps_returns_sorted(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    entries = compute_top_n_laps(sample_laps, sample_drivers, top_n=3)
    durations = [e.lap_duration for e in entries]
    assert durations == sorted(durations)


def test_compute_top_n_laps_respects_top_n(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    entries = compute_top_n_laps(sample_laps, sample_drivers, top_n=2)
    assert len(entries) <= 2


def test_compute_top_n_laps_rank_starts_at_one(
    sample_laps: list[Lap], sample_drivers: list[Driver]
) -> None:
    entries = compute_top_n_laps(sample_laps, sample_drivers, top_n=5)
    assert entries[0].rank == 1


def test_compute_top_n_laps_empty_laps(sample_drivers: list[Driver]) -> None:
    entries = compute_top_n_laps([], sample_drivers, top_n=5)
    assert entries == []


def test_compute_top_n_laps_empty_drivers(sample_laps: list[Lap]) -> None:
    entries = compute_top_n_laps(sample_laps, [], top_n=5)
    assert entries == []


def test_compute_top_n_laps_unknown_driver_skipped(
    sample_drivers: list[Driver],
) -> None:
    laps = [Lap(lap_number=1, lap_duration=85.0, driver_number=999)]
    entries = compute_top_n_laps(laps, sample_drivers, top_n=5)
    assert entries == []
