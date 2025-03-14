from typing import Iterator
from unidecode import unidecode
import re

use_test = False

def run(lines: Iterator[str]):
	print(sum(is_valid(password) for password in lines))

def is_valid(password: str):
	normalized = unidecode(password).lower()
	return (
		4 <= len(password) <= 12
		and any(char.isdigit() for char in password)
		and any(char in "aeiou" for char in normalized)
		and any(char in "bcdfghjklmnpqrstvwxyz" for char in normalized)
		and re.search(r"(.).*\1", normalized) is None
	)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
