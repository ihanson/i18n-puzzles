import datetime
from typing import Iterator
import timezones
import functools

use_test = False

def run(lines: Iterator[str]):
	observations = [parse_line(line) for line in lines]
	stations = {station for (station, _) in observations}
	observations = {
		station: [
			observation
			for (obs_station, observation) in observations
			if obs_station == station
		]
		for station in stations
	}
	versions = ["2018c", "2018g", "2021b", "2023d"]
	tzdata = {
		version: timezones.load_tz_data(version)
		for version in versions
	}
	utc_observations: list[set[datetime.datetime]] = []
	for station in stations:
		station_observations: set[datetime.datetime] = set()
		for version in versions:
			for observation in observations[station]:
				for possibility in tzdata[version].local_to_utc(observation, station):
					station_observations.add(possibility)
		utc_observations.append(station_observations)
	common = functools.reduce(
		lambda acc, datetimes: acc & datetimes,
		utc_observations
	)
	if len(common) > 0:
		print(" ".join(
			observation.replace(tzinfo=datetime.timezone.utc).isoformat()
			for observation in common
		))

def possible_configs(stations: list[str], versions: list[str]) -> Iterator[dict[str, str]]:
	if len(stations) == 0:
		yield {}
	else:
		[station, *others] = stations
		for version in versions:
			for config in possible_configs(others, versions):
				yield dict([
					(station, version),
					*config.items()
				])

def parse_line(line: str) -> tuple[str, datetime.datetime]:
	[datetime_str, timezone] = line.split(";")
	return (
		timezone.strip(),
		datetime.datetime.fromisoformat(datetime_str.strip())
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
