from typing import Iterable
import datetime
from zoneinfo import ZoneInfo
from period import TimePeriod, MultiPeriod

class Schedule(object):
	def next_period(self, at_or_after: datetime.datetime) -> TimePeriod | None:
		raise NotImplementedError()
	def over_period(self, period: TimePeriod) -> MultiPeriod:
		periods_in_range = []
		current = self.next_period(period.start)
		while current is not None and current.start < period.end:
			periods_in_range.append(current)
			current = self.next_period(current.end)
		return MultiPeriod(periods_in_range).intersection(MultiPeriod([period]))

class WeekdaySchedule(Schedule):
	def __init__(self, timezone: ZoneInfo, holidays: Iterable[datetime.date]):
		self.timezone = timezone
		self.holidays = frozenset(holidays)

	def possible_period_on_day(self, day: datetime.date) -> TimePeriod:
		raise NotImplementedError()
	
	def next_period(self, at_or_after):
		local = at_or_after.astimezone(self.timezone)
		test_date = local.date()
		if local >= self.possible_period_on_day(test_date).end:
			test_date += datetime.timedelta(days=1)
		while not is_weekday(test_date) or test_date in self.holidays:
			test_date += datetime.timedelta(days=1)
		return self.possible_period_on_day(test_date)

class SupportSchedule(WeekdaySchedule):
	def possible_period_on_day(self, day):
		return TimePeriod(
			datetime_from(day, datetime.time(8, 30), self.timezone),
			datetime_from(day, datetime.time(17, 0), self.timezone)
		)

class AllDaySchedule(WeekdaySchedule):
	def possible_period_on_day(self, day):
		return TimePeriod(
			datetime_from(day, datetime.time(0, 0), self.timezone),
			datetime_from(day + datetime.timedelta(days=1), datetime.time(0, 0), self.timezone)
		)

def is_weekday(date: datetime.date) -> bool:
	return date.weekday() <= 4

def datetime_from(date: datetime.date, time: datetime.time, tz: ZoneInfo) -> datetime.datetime:
	return datetime.datetime(
		date.year,
		date.month,
		date.day,
		time.hour,
		time.minute,
		time.second,
		time.microsecond,
		tz
	)