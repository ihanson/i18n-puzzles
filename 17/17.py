from typing import Iterable, Iterator
import codecs
import re

use_test = False
Fragment = list[bytes]
horiz_edge = re.compile(r"[╔╚]?[-═]+[╗╝]?")

def run(lines: Iterator[str]):
	fragments: list[Fragment] = [
		[line for line in fragment]
		for fragment in read_input(lines)
	]
	
	solution = solve(fragments)
	(col, row) = x_coords(solution)
	print(col * row)
	writeToJS(solution);

def solve(fragments: list[Fragment]) -> list[str]:
	left_edges = {i for (i, f) in enumerate(fragments) if is_left_edge(f)}
	right_edges = {i for (i, f) in enumerate(fragments) if is_right_edge(f)}
	top_edges = {i for (i, f) in enumerate(fragments) if is_horiz_edge(f[0])}
	solution = list(solve_helper(
		[[] for _ in range(len(top_edges))],
		fragments,
		set(range(len(fragments))),
		left_edges,
		right_edges,
		top_edges,
		None
	))[0]

	return [
		b"".join(
			solution[col_index][row_index]
			for col_index in range(len(solution))
		).decode("utf-8")
		for row_index in range(len(solution[0]))
	]

def solve_helper(
		solution_cols: list[list[bytes]],
		fragments: list[Fragment],
		all_pieces: set[int],
		left_edges: set[int],
		right_edges: set[int],
		top_edges: set[int],
		last_col_index: int | None
	) -> Iterator[list[str]]:
	col_count = len(top_edges)
	col_index = 0 if last_col_index is None else (last_col_index + 1) % col_count
	col = solution_cols[col_index]
	if len(col) > 0 and is_horiz_edge(col[-1]):
		yield from solve_helper(
			solution_cols,
			fragments,
			all_pieces,
			left_edges, right_edges, top_edges,
			col_index
		)
		return
	horiz = (all_pieces & top_edges) if len(col) == 0 else (all_pieces - top_edges)
	vert = (
		(all_pieces & left_edges) if col_index == 0
		else (all_pieces & right_edges) if col_index == col_count - 1
		else (all_pieces - left_edges - right_edges)
	)
	matches = [
		frag_index for frag_index in horiz.intersection(vert)
		if fragment_matches(solution_cols, col_index, fragments[frag_index])
	]
	if len(matches) <= 3:
		for match_index in matches:
			new_cols = [[line for line in copy_col] for copy_col in solution_cols]
			new_cols[col_index].extend(fragments[match_index])
			if len(all_pieces) == 1:
				if is_valid_solution(new_cols):
					yield new_cols
			else:
				yield from solve_helper(
					new_cols,
					fragments,
					all_pieces - {match_index},
					left_edges, right_edges, top_edges,
					col_index
				)
	else:
		yield from solve_helper(
			solution_cols,
			fragments,
			all_pieces,
			left_edges, right_edges, top_edges,
			0
		)

def is_valid_solution(solution_cols: list[list[bytes]]) -> bool:
	if any(len(col) != len(solution_cols[0]) for col in solution_cols):
		return False
	if not is_horiz_edge_str(b"".join(
		col[-1] for col in solution_cols
	).decode("utf-8")):
		return False
	return True

x_char = "\N{BOX DRAWINGS LIGHT DIAGONAL CROSS}"

def x_coords(solution: list[str]) -> tuple[int, int]:
	for (y, row) in enumerate(solution):
		for (x, char) in enumerate(row):
			if char == x_char:
				return (x, y)
	raise ValueError("X not found")

def fragment_matches(solution_cols: list[list[bytes]], col_index: int, fragment: Fragment) -> bool:
	for (row_index, line) in enumerate(fragment, len(solution_cols[col_index])):
		if (col_index - 1) >= 0 and row_index < len(solution_cols[col_index - 1]):
			left_line = solution_cols[col_index - 1][row_index]
			if missing_at_end(left_line) != extra_at_start(line):
				return False
		if (col_index + 1) < len(solution_cols) and row_index < len(solution_cols[col_index + 1]):
			right_line = solution_cols[col_index + 1][row_index]
			if missing_at_end(line) != extra_at_start(right_line):
				return False
	return True

def is_left_edge(fragment: Fragment) -> bool:
	return all(extra_at_start(line) == 0 for line in fragment)

def is_right_edge(fragment: Fragment) -> bool:
	return all(missing_at_end(line) == 0 for line in fragment)

def is_horiz_edge(line: bytes) -> bool:
	left = extra_at_start(line)
	missing_right = missing_at_end(line)
	right = len(line) - (0 if missing_right == 0 else (first_start_byte_index(reversed(line)) + 1))
	return is_horiz_edge_str(line[left:right].decode("utf-8"))

def is_horiz_edge_str(line: str) -> bool:
	return horiz_edge.fullmatch(line) is not None

def first_start_byte_index(line: Iterable[int]) -> int:
	for (i, byte) in enumerate(line):
		if not is_continuation_byte(byte):
			return i
	raise ValueError(f"No UTF-8 start byte found")

def extra_at_start(line: bytes) -> int:
	return first_start_byte_index(line)

def missing_at_end(line: bytes) -> int:
	i = first_start_byte_index(reversed(line))
	partial = line[-(i + 1):]
	return codepoint_length(partial[0]) - len(partial)


def is_continuation_byte(byte: int) -> bool:
	return byte & 0b1100_0000 == 0b1000_0000

def codepoint_length(first_byte: int) -> int:
	if first_byte & 0b1000_0000 == 0b0000_0000:
		return 1
	count = 0
	while first_byte & 0b1000_0000 == 0b1000_0000:
		count += 1
		first_byte <<= 1
	return count

def read_input(lines: Iterator[str]) -> Iterator[list[bytes]]:
	current: list[bytes] = []
	for line in lines:
		if len(line) == 0:
			yield current
			current = []
		else:
			current.append(codecs.decode(line, "hex"))
	yield current

def writeToJS(solution: list[str]):
	import pathlib
	import json
	output_path = pathlib.Path(__file__).parent.joinpath("draw", "map.js")
	with open(output_path, "w", encoding="utf-8") as out_file:
		out_file.write("const treasureMap = ")
		json.dump("\n".join(solution), out_file)
		out_file.write(";")

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
