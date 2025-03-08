import datetime

def grouped_times(times: list[datetime.datetime]):
	groups: dict[datetime.datetime, int] = {}
	for time in times:
		rounded = time.replace(second=0, microsecond=0).astimezone(datetime.timezone.utc)
		groups[rounded] = groups.get(rounded, 0) + 1
	return groups

if __name__ == "__main__":
	with open("02\\input.txt", encoding="utf-8") as in_file:
		grouped = grouped_times(datetime.datetime.fromisoformat(line.strip()) for line in in_file.readlines())
	for time in grouped.keys():
		if grouped[time] >= 4:
			print(time.isoformat(timespec="seconds"))