from typing import Iterator
import unicodedata

use_test = False
encodings = [
	"latin-1",
	"utf-16", "utf-16-be", "utf-16-le",
	"utf-8", "utf-8-sig"
]

def run(lines: Iterator[str]):
	words: list[str] = []
	while len(line := next(lines)) > 0:
		words.append(decode_word(hex_to_bytes(line)))
	puzzle = [line.strip() for line in lines]
	print(solve_puzzle(words, puzzle))
	

def decode_word(encoded: bytes) -> str:
	results: set[str] = set()
	for encoding in encodings:
		try:
			decoding = encoded.decode(encoding)
			if is_latin_word(decoding):
				results.add(decoding)
		except UnicodeDecodeError:
			pass
	if len(results) != 1:
		print(f"{len(results)} possibilities for {encoded}: {results}")
	return results.pop()

def hex_to_bytes(hex: str) -> bytes:
	return bytes(
		int(hex[i:i + 2], 16)
		for i in range(0, len(hex), 2)
	)

def is_latin_word(word: str) -> bool:
	return all(
		unicodedata.category(char) in ["Lu", "Ll"]
		for char in word
	)

def solve_puzzle(words: list[str], puzzle: list[str], start_puzzle_index:int = 0, used_word_indexes: set[int] = set()) -> int | None:
	if start_puzzle_index == len(puzzle):
		return 0
	match_pattern = puzzle[start_puzzle_index]
	match_indexes = [
		index
		for (index, word) in enumerate(words, 1)
		if index not in used_word_indexes and word_matches(word, match_pattern)
	]
	for index in match_indexes:
		solution = solve_puzzle(words, puzzle, start_puzzle_index+1, used_word_indexes | {index})
		if solution is not None:
			return solution + index
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
