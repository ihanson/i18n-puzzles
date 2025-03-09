import datetime

use_test = False

def run(lines):
	grouped = grouped_times(datetime.datetime.fromisoformat(line) for line in lines)
	for time in grouped.keys():
		if grouped[time] >= 4:
			print(time.isoformat(timespec="seconds"))

def grouped_times(times: list[datetime.datetime]):
	groups: dict[datetime.datetime, int] = {}
	for time in times:
		rounded = time.replace(second=0, microsecond=0).astimezone(datetime.timezone.utc)
		groups[rounded] = groups.get(rounded, 0) + 1
	return groups

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.strip() for line in in_file)
#endregion
