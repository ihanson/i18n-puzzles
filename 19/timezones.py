import datetime
import os
import re
from collections import namedtuple
from typing import Iterator, Literal, Self, TypeVar

data_root = "C:\\Users\\Ira\\Code\\zones"
data_files = [
	"africa", "antarctica", "asia", "australasia",
	"backward", "backzone", "etcetera", "europe",
	"factory", "northamerica", "southamerica"
]

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

days_of_week = {
	"Monday": 0,
	"Tuesday": 1,
	"Wednesday": 2,
	"Thursday": 3,
	"Friday": 4,
	"Saturday": 5,
	"Sunday": 6
}

class DayOfMonth(object):
	def calculate(self, year: int, month: int) -> datetime.date:
		raise NotImplementedError()
	
	@staticmethod
	def parse(day_spec: str) -> "DayOfMonth":
		if (match := re.fullmatch(r"\d+", day_spec)):
			return AbsoluteDayOfMonth(int(match.group(0)))
		elif (match := re.fullmatch(r"last(\w+)", day_spec)):
			return LastDayOfWeekOfMonth(
				match_keyword_dict(days_of_week, match.group(1))
			)
		elif (match := re.fullmatch(r"(\w+)([<>]=)(\d+)", day_spec)):
			return NextDayOfWeekOfMonth(
				match_keyword_dict(days_of_week, match.group(1)),
				int(match.group(3)),
				1 if match.group(2) == ">=" else -1
			)
		else:
			raise ValueError(f"Unknown day of month specifier {day_spec}")

class AbsoluteDayOfMonth(DayOfMonth):
	def __init__(self, day: int):
		self.day = day

	def calculate(self, year: int, month: int) -> datetime.date:
			return datetime.date(year, month, self.day)

class LastDayOfWeekOfMonth(DayOfMonth):
	def __init__(self, day_of_week: int):
		self.day_of_week = day_of_week

	def calculate(self, year, month):
		first_of_next = (
			datetime.date(year, month + 1, 1) if month < 12
			else datetime.date(year + 1, 1, 1)
		)
		shift = (self.day_of_week - first_of_next.weekday() + 7) % 7
		return first_of_next + datetime.timedelta(days=shift - 7)

class NextDayOfWeekOfMonth(DayOfMonth):
	def __init__(self, day_of_week: int, start_day: int, direction: Literal[-1, 1]):
		self.day_of_week = day_of_week
		self.start_day = start_day
		self.direction: Literal[-1, 1] = direction
	
	def calculate(self, year, month) -> datetime.date:
		start = datetime.date(year, month, self.start_day)
		shift = ((self.day_of_week - start.weekday()) * self.direction + 7) % 7
		return start + datetime.timedelta(days=shift * self.direction)

class ZoneLine(object):
	def __init__(
		self,
		name: str,
		std_offset: datetime.timedelta | None,
		rules: str | datetime.timedelta | None,
		format: str,
		until: tuple[datetime.date, datetime.timedelta, str] | None
	):
		self.name = name
		self.std_offset = std_offset
		self.rules = rules
		self.format = format
		self.until = until
	
	@staticmethod
	def parse(name: str, stdoff: str, rules: str, format: str, *until: str) -> "ZoneLine":
		if name == "":
			raise ValueError("Zone cannot have a blank name")
		return ZoneLine(
			name=name,
			std_offset=parse_time_delta(stdoff),
			rules=(
				None if rules == "-"
				else rules if rules[0].isalpha()
				else parse_time_delta(rules)
			),
			format=format,
			until=parse_date_with_delta(" ".join(until)) if len(until) > 0 else None
		)

class RuleLine(object):
	def __init__(
		self,
		name: str,
		from_year: int,
		to_year: int | None,
		month: int,
		day_of_month: DayOfMonth,
		at_time: tuple[datetime.timedelta, str],
		save_offset: datetime.timedelta,
		is_dst: bool,
		letters: str
	):
		self.name = name
		self.from_year = from_year
		self.to_year = to_year
		self.month = month
		self.day_of_month = day_of_month
		self.at_time = at_time
		self.offset_from_std = save_offset
		self.is_dst = is_dst
		self.letters = letters
	
	@staticmethod
	def parse(name: str, from_: str, to: str, _, in_: str, on: str, at: str, save: str, letters: str):
		if name == "":
			raise ValueError("Rule cannot have a blank name")
		(at_time, at_suffix) = split_suffix(at)
		(save_offset, save_suffix) = split_suffix(save)
		save_offset = parse_time_delta(save_offset)
		return RuleLine(
			name=name,
			from_year=int(from_),
			to_year=(
				None if match_keyword("maximum", to)
				else int(from_) if match_keyword("only", to)
				else int(to)
			),
			month=match_keyword_dict(months, in_),
			day_of_month=DayOfMonth.parse(on),
			at_time=(
				parse_time_delta(at_time),
				norm_time_suffix(at_suffix)
			),
			save_offset=save_offset,
			is_dst=save_suffix == "d" or (
				save_suffix is None and save_offset.total_seconds() > 0.0
			),
			letters=letters
		)

LinkLine = namedtuple(
	"LinkLine",
	["target", "link_name"]
)

class TimeZoneData(object):
	def __init__(
		self,
		zone_lines: list[ZoneLine],
		rule_lines: list[RuleLine],
		link_lines: list[LinkLine]
	):
		self.zones: dict[str, list[ZoneLine]] = {}
		for line in zone_lines:
			if line.name not in self.zones:
				self.zones[line.name] = []
			self.zones[line.name].append(line)
		
		self.rules: dict[str, list[RuleLine]] = {}
		for line in rule_lines:
			if line.name not in self.rules:
				self.rules[line.name] = []
			self.rules[line.name].append(line)
		
		self.links = {line.link_name: line.target for line in link_lines}

	def find_timezone(self, timezone_name: str) -> list[ZoneLine]:
		while timezone_name in self.links:
			timezone_name = self.links[timezone_name]
		return self.zones[timezone_name]

	def local_to_utc(self, local_datetime: datetime.datetime, timezone_name: str) -> set[datetime.datetime]:
		if local_datetime.tzinfo is not None:
			raise ValueError("Local datetime must not have a timezone attached")
		zone_line = self.__active_zone_line_wall(timezone_name, local_datetime)
		active_rules = [
			rule_line
			for (start, end, rule_line)
			in self.__rule_wall_times_in_year(zone_line, local_datetime.year)
			if start <= local_datetime < end
		]
		return {
			local_datetime - rule.offset_from_std - zone_line.std_offset
			for rule in active_rules
		}

	def utc_to_local(self, utc_datetime: datetime.datetime, timezone_name: str) -> datetime.datetime:
		if utc_datetime.tzinfo is not None:
			raise ValueError("UTC datetime must not have a timezone attached")
		zone_line = self.__active_zone_line_utc(timezone_name, utc_datetime)
		std_datetime = utc_datetime + zone_line.std_offset
		active_rules = [
			rule_line
			for (start, end, rule_line)
			in self.__rule_wall_times_in_year(zone_line, std_datetime.year)
			if start <= (std_datetime + rule_line.offset_from_std) < end
		]
		assert len(active_rules) == 1
		return std_datetime + active_rules[0].offset_from_std

	def __active_zone_line_wall(self, timezone_name: str, wall_datetime: datetime.datetime) -> ZoneLine:
		zone = self.find_timezone(timezone_name)
		for line in zone:
			end_wall_datetime = self.__zone_line_wall_end(line)
			if end_wall_datetime is None or end_wall_datetime > wall_datetime:
				return line
		raise ValueError(f"Time zone is not active at {wall_datetime}")
	
	def __active_zone_line_utc(self, timezone_name: str, utc_datetime: datetime.datetime) -> ZoneLine:
		zone = self.find_timezone(timezone_name)
		for line in zone:
			end_utc_datetime = self.__zone_line_utc_end(line)
			if end_utc_datetime is None or end_utc_datetime > utc_datetime:
				return line
		raise ValueError(f"Time zone is not active at {utc_datetime}")

	def __rule_wall_times_in_year(self, zone_line: ZoneLine, year: int) -> Iterator[tuple[datetime.datetime, datetime.datetime, RuleLine]]:
		rule_lines = (
			self.rules[zone_line.rules] if isinstance(zone_line.rules, str)
			else [RuleLine(
				name="",
				from_year=year - 1,
				to_year=year - 1,
				month=1,
				day_of_month=AbsoluteDayOfMonth(1),
				at_time=(datetime.timedelta(), "w"),
				save_offset=zone_line.rules or datetime.timedelta(),
				is_dst=False,
				letters=""
			)]
		)
		last_before_year = max(
			(line for line in rule_lines if line.from_year < year),
			key=lambda line: line.day_of_month.calculate(
				min(line.to_year, year - 1) if line.to_year is not None else (year - 1),
				line.month
			),
			default=None
		)
		changes_in_year = {
			line.day_of_month.calculate(year, line.month): line
			for line in rule_lines
			if line.from_year <= year and (line.to_year is None or line.to_year >= year)
		}
		start_datetime = datetime.datetime(year, 1, 1) - datetime.timedelta(days=7)
		current_line = last_before_year if last_before_year is not None else RuleLine(
			name="", from_year=year, to_year=year, month=1, day_of_month=AbsoluteDayOfMonth(1),
			at_time=(datetime.timedelta(), "w"), save_offset=datetime.timedelta(),
			is_dst=False, letters="S"
		)
		for change_date in sorted(changes_in_year.keys()):
			change = changes_in_year[change_date]
			(change_time, change_suffix) = change.at_time
			end_wall_time_delta = (
				change_time + zone_line.std_offset + current_line.offset_from_std if change_suffix == "u"
				else change_time + current_line.offset_from_std if change_suffix == "s"
				else change_time
			)
			yield (
				start_datetime,
				datetime.datetime(
					change_date.year,
					change_date.month,
					change_date.day
				) + end_wall_time_delta,
				current_line
			)
			start_datetime = (
				datetime.datetime(change_date.year, change_date.month, change_date.day)
				+ end_wall_time_delta
				- current_line.offset_from_std
				+ change.offset_from_std
			)
			current_line = change
		yield (
			start_datetime,
			datetime.datetime(year + 1, 1, 1) + datetime.timedelta(days=7),
			current_line
		)

	def __zone_line_utc_end(self, zone_line: ZoneLine) -> datetime.datetime | None:
		if zone_line.until is None:
			return None
		(until_date, until_offset, until_suffix) = zone_line.until
		until_datetime = datetime.datetime(
			until_date.year,
			until_date.month,
			until_date.day
		) + until_offset
		if until_suffix == "u":
			return until_datetime
		elif until_suffix == "s":
			return until_datetime - zone_line.std_offset
		else:
			wall_times = self.__rule_wall_times_in_year(zone_line, until_date.year)
			wall_times = list(wall_times)
			active_rules = [
				rule_line
				for (start, end, rule_line) in wall_times
				if start < until_datetime <= end
			]
			if len(active_rules) == 0:
				raise ValueError("Zone line end time does not exist")
			if len(active_rules) > 1:
				raise ValueError("Zone line end time is ambiguous")
			return until_datetime - active_rules[0].offset_from_std - zone_line.std_offset

	def __zone_line_wall_end(self, zone_line: ZoneLine) -> datetime.datetime | None:
		if zone_line.until is None:
			return None
		(until_date, until_offset, until_suffix) = zone_line.until
		until_datetime = datetime.datetime(
			until_date.year,
			until_date.month,
			until_date.day
		) + until_offset
		if until_suffix == "w":
			return until_datetime
		else:
			until_std_datetime = (
				until_datetime + zone_line.std_offset if until_suffix == "u"
				else until_datetime
			)
			std_times = [
				(
					start_wall - rule_line.offset_from_std,
					end_wall - rule_line.offset_from_std, rule_line
				)
				for (start_wall, end_wall, rule_line)
				in self.__rule_wall_times_in_year(zone_line, until_date.year)
			]
			active_rules = [
				rule_line
				for (start, end, rule_line) in std_times
				if start < until_std_datetime <= end
			]
			if len(active_rules) == 0:
				raise ValueError("Zone line end time does not exist")
			if len(active_rules) > 1:
				raise ValueError("Zone line end time is ambiguous")
			return until_std_datetime + active_rules[0].offset_from_std

			

def load_tz_data(version: str) -> TimeZoneData:
	zones: list[ZoneLine] = []
	rules: list[RuleLine] = []
	links: list[LinkLine] = []
	for filename in data_files:
		path = os.path.join(data_root, version, filename)
		prev_zone = None
		for line in file_lines(path):
			[line_type, *data] = split_line(line, prev_zone)
			if match_keyword("Zone", line_type):
				[zone_name, *zone_data] = data
				zones.append(ZoneLine.parse(zone_name, *zone_data))
				prev_zone = ["Zone", zone_name]
			elif match_keyword("Rule", line_type):
				rules.append(RuleLine.parse(*data))
			elif match_keyword("Link", line_type):
				links.append(LinkLine(*data))
			else:
				raise ValueError(f"Unknown line type f{line_type!r}")
	data = TimeZoneData(zones, rules, links)
	return data

def file_lines(path: str) -> Iterator[str]:
	with open(path, encoding="utf-8") as file_in:
		for line in file_in:
			if "#" in line:
				line = line[:line.index("#")]
			if not all(char.isspace() for char in line):
				yield line.rstrip()

def split_line(line: str, assumed_vals: list[str] | None = []) -> list[str]:
	if "\"" in line:
		raise ValueError("Quotes not supported in data lines")
	vals = []
	if assumed_vals is not None and (tabs := re.match(r"^\t{2,} *", line)):
		vals.extend(assumed_vals)
		line = line[len(tabs.group(0)):]
	vals.extend(re.split(r"\s+", line))
	return vals

def match_keyword(keyword: str, test: str) -> bool:
	return len(test) > 0 and keyword.upper().startswith(test.upper())

T = TypeVar("T")
def match_keyword_dict(dictionary: dict[str, T], test: str) -> T:
	for (key, value) in dictionary.items():
		if match_keyword(key, test):
			return value
	raise KeyError(test)

def expand(source: list[T], length: int, default: T) -> list[T]:
	if len(source) >= length:
		return list(source)
	return source + ([default] * (length - len(source)))

def parse_time_delta(delta: str) -> datetime.timedelta:
	if delta == "-":
		return datetime.timedelta()
	[hours, minutes, seconds] = expand([float(p) for p in delta.split(":")], 3, 0)
	sign = -1 if hours < 0 else 1
	return sign * datetime.timedelta(hours=hours * sign, minutes=minutes, seconds=seconds)

def split_suffix(string: str) -> tuple[str, str | None]:
	if len(string) >= 2 and string[-2].isnumeric() and string[-1].isalpha():
		return (string[:-1], string[-1])
	else:
		return (string, None)

def norm_time_suffix(suffix: str | None) -> str:
	match suffix:
		case "w" | None: return "w"
		case "u" | "g" | "z": return "u"
		case "s": return "s"
		case _: raise ValueError(f"Invalid suffix {suffix}")

def parse_date_with_delta(datetime_str: str) -> tuple[datetime.date, datetime.timedelta, str]:
	[year, month, day, delta] = expand(datetime_str.split(" "), 4, None)
	year = int(year)
	month = match_keyword_dict(months, month) if month is not None else 1
	day = DayOfMonth.parse(day).calculate(year, month).day if day is not None else 1
	(delta, delta_suffix) = split_suffix(delta) if delta is not None else (None, None)
	return (
		datetime.date(year, month, day),
		parse_time_delta(delta) if delta is not None else datetime.timedelta(),
		norm_time_suffix(delta_suffix)
	)
