import re
import datetime
import zoneinfo
from typing import Iterator

use_test = False

def run(lines: Iterator[str]):
	total_duration = datetime.timedelta()
	for (departure, arrival) in read_lines(lines):
		total_duration += arrival - departure
	print(total_duration // datetime.timedelta(minutes=1))

def read_lines(lines: Iterator[str]):
	try:
		while True:
			departure = parse_line(next(lines))
			arrival = parse_line(next(lines))
			yield (departure, arrival)
			_ = next(lines)
	except StopIteration:
		pass

parse_regex = re.compile(r"\w++:\s*+(?P<tz>\S++)\s++(?P<dt>.*+)")
def parse_line(line: str):
	match = parse_regex.fullmatch(line)
	return (
		datetime.datetime.strptime(match.group("dt"), "%b %d, %Y, %H:%M")
			.replace(tzinfo=zoneinfo.ZoneInfo(match.group("tz")))
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.strip() for line in in_file)
#endregion
