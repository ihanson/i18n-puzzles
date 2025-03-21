from typing import Iterable, Iterator, Self
import datetime
import itertools
import functools

class TimePeriod(object):
	__slots__ = ["_TimePeriod__start", "_TimePeriod__end"]
	def __init__(self, start: datetime.datetime, end: datetime.datetime):
		if start > end:
			raise ValueError(f"Time period start {start} is after end {end}")
		self.__start = start
		self.__end = end
	
	@property
	def start(self):
		return self.__start
	
	@property
	def end(self):
		return self.__end

	def __eq__(self, other: Self):
		return self.start == other.start and self.end == other.end
	
	def __hash__(self):
		return hash(self.start, self.end)

	def __contains__(self, dt: datetime.datetime):
		return self.start <= dt < self.end

	def union(self, other: Self) -> "MultiPeriod":
		return MultiPeriod([self, other])
	
	def intersection(self, other: Self) -> "MultiPeriod":
		if other.start in self:
			if other.end in self:
				return MultiPeriod([other])
			else:
				return MultiPeriod([TimePeriod(other.start, self.end)])
		elif self.start in other:
			if self.end in other:
				return MultiPeriod([self])
			else:
				return MultiPeriod([TimePeriod(self.start, other.end)])
		else:
			return MultiPeriod()
	
	def duration(self) -> datetime.timedelta:
		return self.end - self.start
	
	def __sub__(self, other: Self) -> "MultiPeriod":
		if other.start in self:
			if other.end in self:
				return MultiPeriod([
					TimePeriod(self.start, other.start),
					TimePeriod(other.end, self.end)
				])
			else:
				return MultiPeriod([TimePeriod(self.start, other.start)])
		elif self.start in other:
			if self.end in other:
				return MultiPeriod()
			else:
				return MultiPeriod([TimePeriod(other.end, self.end)])
		else:
			return MultiPeriod([self])

	def touches(self, other: Self) -> bool:
		return not(
			self.start > other.end
			or other.start > self.end
		)
	
	def __str__(self) -> str:
		return f"({self.start} \u2014 {self.end})"

class MultiPeriod(object):
	def __init__(self, periods: Iterable[TimePeriod] = []):
		periods = list(periods)
		periods.sort(key=lambda period: period.start)
		i = 0
		while i < len(periods):
			while (i + 1) < len(periods) and periods[i].touches(periods[i + 1]):
				periods[i] = TimePeriod(periods[i].start, periods[i + 1].end)
				periods.pop(i + 1)
			i += 1
		self.__periods = periods
	
	def __iter__(self) -> Iterator[TimePeriod]:
		return iter(self.__periods)

	def union(self, *others: Self) -> Self:
		return MultiPeriod(itertools.chain(self, *others))
	
	def intersection(self, *others: Self) -> Self:
		periods = list(self)
		for other in others:
			intersections: list[TimePeriod] = []
			for self_period in periods:
				for other_period in other:
					intersections += other_period.intersection(self_period)
			periods = intersections
		return MultiPeriod(periods)
	
	def duration(self) -> datetime.timedelta:
		return functools.reduce(
			lambda acc, period: acc + period.duration(),
			self.__periods,
			datetime.timedelta()
		)
	
	def __sub__(self, other: Self) -> Self:
		periods = list(self)
		for isect_period in self.intersection(other):
			i = 0
			while i < len(periods):
				self_period = periods[i]
				sub_periods = list(self_period - isect_period)
				periods[i : i + 1] = sub_periods
				i += len(sub_periods)
		return MultiPeriod(periods)
	
	def __str__(self) -> str:
		joined = ", ".join(str(period) for period in self.__periods)
		return f"[{joined}]"