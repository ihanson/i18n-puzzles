from typing import Iterator

use_test = False

def run(lines: Iterator[str]):
	words = []
	line_num = 0
	while len(word := next(lines)) > 0:
		line_num += 1
		words.append(fix_mojibake(word, line_num))
	puzzle = [line.strip() for line in lines]
	print(solve_puzzle(words, puzzle))

def fix_mojibake(word, line_num):
	if line_num % 3 == 0:
		word = word.encode("latin-1").decode("utf-8")
	if line_num % 5 == 0:
		word = word.encode("latin-1").decode("utf-8")
	return word

def solve_puzzle(words, puzzle, start_puzzle_index=0, used_word_indexes=set()):
	if start_puzzle_index == len(puzzle):
		return 0
	match_pattern = puzzle[start_puzzle_index]
	match_indexes = [
		index
		for (index, word) in enumerate(words)
		if index not in used_word_indexes and word_matches(word, match_pattern)
	]
	for index in match_indexes:
		solution = solve_puzzle(words, puzzle, start_puzzle_index+1, used_word_indexes | {index})
		if solution is not None:
			return solution + (index + 1)
	return None

def word_matches(word: str, pattern: str):
	if len(word) != len(pattern):
		return False
	return all(
		pattern_char == "." or pattern_char.upper() == word_char.upper()
		for (word_char, pattern_char) in zip(word, pattern)
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
