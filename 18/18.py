from typing import Callable, Iterable, Iterator, TypeVar
from collections import namedtuple
import re

use_test = False
EmbeddedValue = namedtuple("EmbeddedValue", ["value", "level"])
operators = {
	"+": lambda a, b: a + b,
	"-": lambda a, b: a - b,
	"*": lambda a, b: a * b,
	"/": lambda a, b: a / b
}

def run(lines: Iterator[str]):
	print(sum(
		abs(eval_expr_rex(line) - eval_expr_lynx(line))
		for line in lines
	))

def eval_expr_rex(expr: str) -> int:
	return eval_expr(re.sub(r"[^\d.+\-*/()]", "", expr))

def eval_expr_lynx(expr: str) -> int:
	rtl_fixed = parse_embedded(embed_rtl(expr), reverse_chars)
	return eval_expr("".join(rtl_fixed))

def eval_expr(expr: str) -> int:
	return round(parse_embedded(embed_expr(expr), evaluate_subexpr)[0])

T = TypeVar("T")
def parse_embedded(embedded: list[EmbeddedValue], transform: Callable[[list[str | T]], Iterable[T]]) -> list[T]:
	embedded = list(embedded)
	while (max_level := max(emb_value.level for emb_value in embedded)) > 0:
		prev_level = 0
		max_level_start = None
		i = 0
		while i < len(embedded):
			level = embedded[i].level
			if prev_level == max_level and level < prev_level:
				i += replace_chunk(embedded, transform, max_level_start, i, max_level - 1)
				max_level_start = None
			if level == max_level and max_level_start is None:
				max_level_start = i
			prev_level = level
			i += 1
		if max_level_start is not None:
			i += replace_chunk(embedded, transform, max_level_start, len(embedded), max_level - 1)
	return [emb_value.value for emb_value in embedded]

def replace_chunk(
		embedded: list[EmbeddedValue],
		transform: Callable[[list[str]], Iterable[str]],
		start: int,
		end: int,
		new_level: int
	) -> int:
	transformed = list(transform([
		emb_value.value
		for emb_value in embedded[start:end]
	]))
	embedded[start:end] = (
		EmbeddedValue(value=val, level=new_level)
		for val in transformed
	)
	return len(transformed) - (end - start)

def is_rtl(level: int) -> bool:
	return level % 2 == 1

def embed_expr(text: str) -> list[EmbeddedValue]:
	return embed_levels(
		f"({text})",
		lambda current_level, char: (
			(None, current_level + 1) if char == "("
			else (None, current_level - 1) if char == ")"
			else (None, current_level) if char.isspace()
			else (current_level, current_level)
		)
	)

def embed_rtl(text: str) -> list[EmbeddedValue]:
	return embed_levels(text, embed_rtl_char)

def embed_rtl_char(current_level: int, char: str) -> tuple[int | None, int]:
	if char == "\N{RIGHT-TO-LEFT ISOLATE}":
		return (
			None,
			current_level + 1 if not is_rtl(current_level) else current_level
		)
	elif char == "\N{LEFT-TO-RIGHT ISOLATE}":
		return (
			None,
			current_level + 1 if is_rtl(current_level) else current_level
		)
	elif char == "\N{POP DIRECTIONAL ISOLATE}":
		return (
			None,
			current_level - 1 if current_level > 0 else current_level
		)
	else:
		return (
			current_level + 1 if is_rtl(current_level) and char.isdigit() else current_level,
			current_level
		)

def embed_levels(text: str, embed_func: Callable[[int, str], tuple[int | None, int]]) -> list[EmbeddedValue]:
	leveled: list[EmbeddedValue] = []
	level = 0
	for char in text:
		(embed_at, level) = embed_func(level, char)
		if embed_at is not None:
			leveled.append(EmbeddedValue(value=char, level=embed_at))
	return leveled

def reverse_chars(chars: list[str]) -> Iterable[str]:
	return (flip_bracket(char) for char in reversed(chars))

def evaluate_subexpr(subexpr: list[str | float]) -> Iterable[float]:
	op_i = op_index(subexpr)
	if op_i is None:
		return "".join(subexpr)
	return [operators[subexpr[op_i]](parse_number(subexpr[:op_i]), parse_number(subexpr[op_i + 1:]))]

def parse_number(number: list[str | float]) -> float:
	return float("".join(number)) if isinstance(number[0], str) else number[0]

def op_index(subexpr: list[str | float]) -> int | None:
	for (i, value) in enumerate(subexpr):
		if value in operators and not (value == "-" and i == 0):
			return i
	return None

def flip_bracket(char: str) -> str:
	return (
		")" if char == "("
		else "(" if char == ")"
		else char
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
