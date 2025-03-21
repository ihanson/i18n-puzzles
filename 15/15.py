from typing import Iterable
from zoneinfo import ZoneInfo
import datetime
import schedule

use_test = False
months = {
	"January": 1,
	"February": 2,
	"March": 3,
	"April": 4,
	"May": 5,
	"June": 6,
	"July": 7,
	"August": 8,
	"September": 9,
	"October": 10,
	"November": 11,
	"December": 12
}

def run(lines: Iterable[str]):
	support: list[schedule.Schedule] = []
	while len(line := next(lines)) > 0:
		(_, tz, holidays) = parse_office(line)
		support.append(schedule.SupportSchedule(tz, holidays))

	customers: list[schedule.Schedule] = []
	for line in lines:
		(_, tz, holidays) = parse_office(line)
		customers.append(schedule.AllDaySchedule(tz, holidays))
	
	overtime = [
		(
			schedules_over_year([customer], 2022)
			- schedules_over_year(support, 2022)
		).duration()
		for customer in customers
	]
	print((max(overtime) - min(overtime)) // datetime.timedelta(minutes=1))

def schedules_over_year(schedules: Iterable[schedule.Schedule], utc_year: int) -> schedule.MultiPeriod:
	year = schedule.TimePeriod(
		datetime.datetime(utc_year, 1, 1, tzinfo=ZoneInfo("UTC")),
		datetime.datetime(utc_year + 1, 1, 1, tzinfo=ZoneInfo("UTC"))
	)
	return schedule.MultiPeriod().union(*(sched.over_period(year) for sched in schedules))

def parse_office(office_line: str) -> tuple[str, ZoneInfo, frozenset[datetime.date]]:
	[name, tz_name, holidays] = office_line.split("\t")
	return (
		name,
		ZoneInfo(tz_name),
		frozenset(parse_date(date_str) for date_str in holidays.split(";"))
	)

def parse_date(date_str: str) -> datetime.date:
	[day, month, year] = date_str.split(" ")
	return datetime.date(int(year), months[month], int(day))

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
