from f1.domain.models import Driver, FastestLapEntry, Lap


def filter_valid_laps(laps: list[Lap]) -> list[Lap]:
    return [
        lap for lap in laps if lap.lap_duration is not None and not lap.is_pit_out_lap
    ]


def build_driver_index(drivers: list[Driver]) -> dict[int, Driver]:
    return {driver.driver_number: driver for driver in drivers}


def compute_top_n_laps(
    laps: list[Lap],
    drivers: list[Driver],
    top_n: int = 5,
) -> list[FastestLapEntry]:
    valid_laps = filter_valid_laps(laps)
    driver_index = build_driver_index(drivers)

    sorted_laps = sorted(valid_laps, key=lambda lap: lap.lap_duration)  # type: ignore[arg-type]

    entries: list[FastestLapEntry] = []
    for rank, lap in enumerate(sorted_laps[:top_n], start=1):
        driver = driver_index.get(lap.driver_number)
        if driver is None:
            continue
        entries.append(
            FastestLapEntry(
                rank=rank,
                driver_name=driver.full_name,
                driver_acronym=driver.name_acronym,
                team_name=driver.team_name,
                team_colour=driver.team_colour,
                lap_number=lap.lap_number,
                lap_duration=lap.lap_duration,  # type: ignore[arg-type]
            )
        )
    return entries
