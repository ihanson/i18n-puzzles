from typing import Iterator, TypeVar
import unicodedata
import bcrypt
import functools

use_test = False

def run(lines: Iterator[str]):
	pw_hashes: dict[str, bytes] = {}
	while len(line := next(lines)) > 0:
		[user, pw_hash] = line.split(" ", 1)
		pw_hashes[user] = pw_hash.encode("utf-8")
	
	count = 0
	for line in lines:
		[user, attempt] = line.split(" ", 1)
		if user in pw_hashes and is_valid_login(attempt, pw_hashes[user]):
			count += 1
	print(count)

def is_valid_login(attempt: str, hashed_pw: bytes) -> bool:
	return any(
		check_password(test_pw, hashed_pw)
		for test_pw in recompositions(attempt)
	)

def recompositions(string: str) -> Iterator[str]:
	nfc_chars = list(unicodedata.normalize("NFC", string))
	composed_indexes = {
		i for (i, char) in enumerate(nfc_chars)
		if char != unicodedata.normalize("NFD", char)
	}
	for test_indexes in subsets(composed_indexes):
		yield "".join([
			(
				unicodedata.normalize("NFD", char)
				if i in test_indexes
				else char
			) for (i, char) in enumerate(nfc_chars)
		])

T = TypeVar("T")
def subsets(superset: set[T]) -> Iterator[set[T]]:
	set_list = list(superset)
	for bitfield in range(1 << len(set_list)):
		yield {
			val for (i, val) in enumerate(set_list)
			if bitfield & (1 << i)
		}

@functools.cache
def check_password(password: str, hashed_pw: bytes) -> bool:
	return bcrypt.checkpw(password.encode("utf-8"), hashed_pw)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
