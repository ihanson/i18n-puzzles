from typing import Iterator
import zoneinfo
import datetime
import re

use_test = False

def run(lines: Iterator[str]):
	halifax = zoneinfo.ZoneInfo("America/Halifax")
	santiago = zoneinfo.ZoneInfo("America/Santiago")

	total = 0
	for (index, line) in enumerate(lines):
		[timestamp, correct, incorrect] = re.split(r"\s+", line)
		incorrect_time = datetime.datetime.fromisoformat(timestamp)
		correct_time = (
			incorrect_time
			- datetime.timedelta(minutes=int(incorrect))
			+ datetime.timedelta(minutes=int(correct))
		).astimezone(
			halifax if incorrect_time.utcoffset() == halifax.utcoffset(incorrect_time)
			else santiago
		)
		total += correct_time.hour * (index + 1)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
