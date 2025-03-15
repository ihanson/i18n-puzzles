from typing import Iterator
from enum import StrEnum
import re
import calendar
import datetime

use_test = False

class DateComponent(StrEnum):
	Year = "Y"
	Month = "M"
	Day = "D"

class UnknownFormatException(Exception):
	pass

DateFormat = tuple[DateComponent, DateComponent, DateComponent]
UnknownDate = tuple[int, int, int]
Date = tuple[int, int, int]

def run(lines: Iterator[str]):
	target_date = datetime.date(2001, 9, 11)
	names = [
		name
		for (name, unk_dates) in read_people(lines).items()
		if target_date in translate_unknown_dates(unk_dates)
	]
	names.sort()
	print(" ".join(names))

def read_people(lines: Iterator[str]) -> dict[str, list[UnknownDate]]:
	people: dict[str, list[UnknownDate]] = {}
	for line in lines:
		(unk_date, names) = parse_line(line)
		for name in names:
			if name not in people:
				people[name] = []
			people[name].append(unk_date)
	return people

def parse_line(line: str) -> tuple[UnknownDate, list[str]]:
	match = re.fullmatch(r"(\d+)-(\d+)-(\d+):\s*(?P<names>.*)", line)
	return (
		(int(match.group(1)), int(match.group(2)), int(match.group(3))),
		re.split(r",\s*", match.group("names"))
	)

def translate_unknown_dates(unk_dates: list[UnknownDate]) -> set[datetime.date]:
	formats = possible_date_formats(unk_dates)
	if len(formats) != 1:
		raise UnknownFormatException(f"{len(formats)} possible formats for {unk_dates}: {({date_format_name(format) for format in formats})}")
	[format] = list(formats)
	return {
		parse_date(interpret_with_format(unk_date, format))
		for unk_date in unk_dates
	}

def possible_date_formats(unk_dates: list[UnknownDate]) -> set[DateFormat]:
	formats = {
		(DateComponent.Year, DateComponent.Month, DateComponent.Day),
		(DateComponent.Year, DateComponent.Day, DateComponent.Month),
		(DateComponent.Month, DateComponent.Day, DateComponent.Year),
		(DateComponent.Day, DateComponent.Month, DateComponent.Year)
	}
	for unk_date in unk_dates:
		formats.difference_update([
			format for format in formats
			if not is_possible_format(unk_date, format)
		])
	return formats

def is_possible_format(unk_date: UnknownDate, format: DateFormat):
	(year, month, day) = interpret_with_format(unk_date, format)
	return (
		0 <= year <= 99
		and 1 <= month <= 12
		and 1 <= day <= days_in_month(year, month)
	)

def interpret_with_format(unk_date: UnknownDate, format: DateFormat) -> Date:
	components = dict(zip(format, unk_date))
	return (
		components[DateComponent.Year],
		components[DateComponent.Month],
		components[DateComponent.Day]
	)

def parse_date(date: Date) -> datetime.date:
	(year00, month, day) = date
	year = (2000 if year00 < 20 else 1900) + year00
	return datetime.date(year, month, day)

def days_in_month(year: int, month: int) -> int:
	(_, days) = calendar.monthrange(year, month)
	return days

def date_format_name(format: DateFormat) -> str:
	return "".join(str(piece) for piece in format)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
