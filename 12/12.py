from typing import TypeVar, Iterator
from collections.abc import Callable
import re
import unicodedata
import functools
import itertools

use_test = False

PhonebookEntry = tuple[str, str, str]
LettersSplitter = Callable[[str], Iterator[str]]
LettersComparator = Callable[[str, str], int]
NamePreprocessor = Callable[[str, str], tuple[str, str]]

phonebook_line = re.compile(r"(?P<last>[^,]*), (?P<first>[^:]*): (?P<phone>\d+)")
ligatures = {
	"Æ": "Ae",
	"æ": "ae",
	"Œ": "Oe",
	"œ": "oe",
	"ẞ": "Ss",
	"ß": "ss"
}

def run(lines: Iterator[str]):
	phonebook = [parse_line(line) for line in lines]
	sorted_en = sorted(phonebook, key=phonebook_key(letters_en, compare_letters_en))
	sorted_sv = sorted(phonebook, key=phonebook_key(letters_sv, compare_letters_sv))
	sorted_nl = sorted(phonebook, key=phonebook_key(letters_nl, compare_letters_nl, preprocess_names_nl))
	print(
		int(phone_number(mid_value(sorted_en)))
		* int(phone_number(mid_value(sorted_sv)))
		* int(phone_number(mid_value(sorted_nl)))
	)

def phone_number(entry: PhonebookEntry) -> str:
	(_, _, number) = entry
	return number

def parse_line(line: str) -> PhonebookEntry:
	match = phonebook_line.fullmatch(line)
	return (
		match.group("last"),
		match.group("first"),
		match.group("phone")
	)

def phonebook_key(
		letters_splitter: LettersSplitter,
		letters_comparator: LettersComparator,
		preprocess_name: NamePreprocessor = lambda last, first: (last, first)
	):
	def comp(entry1: PhonebookEntry, entry2: PhonebookEntry) -> int:
		(entry1_last, entry1_first, _) = entry1
		(entry2_last, entry2_first, _) = entry2
		(entry1_last, entry1_first) = preprocess_name(entry1_last, entry1_first)
		(entry2_last, entry2_first) = preprocess_name(entry2_last, entry2_first)
		return (
			comp_text(entry1_last, entry2_last, letters_splitter, letters_comparator)
			or comp_text(entry1_first, entry2_first, letters_splitter, letters_comparator)
		)

	return functools.cmp_to_key(comp)

def comp_text(text1: str, text2: str, letters_splitter: LettersSplitter, letters_comparator: LettersComparator) -> int:
		for (letter1, letter2) in zip(
			extend_iterator(letters_splitter(text1)),
			extend_iterator(letters_splitter(text2)),
		):
			if letter1 is None:
				return -1 if letter2 is not None else 0
			if letter2 is None:
				return 1
			comp_result = letters_comparator(letter1, letter2)
			if comp_result != 0:
				return comp_result

T = TypeVar("T")
def extend_iterator(iter: Iterator[T]) -> Iterator[T | None]:
	yield from iter
	yield from itertools.repeat(None)

def combined_characters(text: str) -> Iterator[str]:
	current = []
	for char in unicodedata.normalize("NFKD", text):
		if unicodedata.combining(char) == 0:
			if len(current) > 0:
				yield unicodedata.normalize("NFC", "".join(current))
				current.clear()
		current.append(char)
	yield unicodedata.normalize("NFC", "".join(current))

def letters_en(text: str) -> Iterator[str]:
	for char in combined_characters(text):
		stripped = strip_diacritics(char)
		if stripped in ligatures:
			yield from ligatures[stripped]
		elif is_latin_letter_az(stripped):
			yield stripped
		elif char.isalpha():
			raise ValueError(f"Unhandled English letter: {char}")

def compare_letters_en(letter1: str, letter2: str) -> int:
	return (
		letter_index_en(letter1.upper())
		- letter_index_en(letter2.upper())
	)

def letter_index_en(letter: str) -> int:
	return "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(letter)

def letters_sv(text: str) -> Iterator[str]:
	for char in combined_characters(text):
		stripped = strip_diacritics(char)
		if char in ["Å", "å", "Ä", "ä", "Ö", "ö", "Æ", "æ", "Ø", "ø"]:
			yield char
		elif stripped in ligatures:
			yield from ligatures[stripped]
		elif is_latin_letter_az(stripped):
			yield stripped
		elif char.isalpha():
			raise ValueError(f"Unhandled Swedish letter: {char}")

def compare_letters_sv(letter1: str, letter2: str) -> int:
	return (
		letter_index_sv(normalize_letter_sv(letter1))
		- letter_index_sv(normalize_letter_sv(letter2))
	)

def letter_index_sv(letter: str) -> int:
	return "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ".index(letter)

def normalize_letter_sv(letter: str) -> str:
	match letter:
		case "Æ" | "æ": return "Ä"
		case "Ø" | "ø": return "Ö"
		case _: return letter.upper()

def letters_nl(text: str) -> Iterator[str]:
	combined = list(combined_characters(text))
	index = 0
	while index < len(combined):
		char = combined[index]
		char2 = "".join(combined[index:(index + 2)])
		index += 1
		stripped = strip_diacritics(char)
		if char2 == "IJ" or char2 == "ij":
			yield char2
			index += 1
		elif stripped in ligatures:
			yield from ligatures[stripped]
		elif is_latin_letter_az(stripped):
			yield stripped
		elif char.isalpha():
			raise ValueError(f"Unhandled English letter: {char}")

def compare_letters_nl(letter1: str, letter2: str) -> int:
	return (
		letter_index_nl(normalize_letter_nl(letter1))
		- letter_index_nl(normalize_letter_nl(letter2))
	)

def letter_index_nl(letter: str) -> int:
	return "ABCDEFGHIJKLMNOPQRSTUVWXYZ".index(letter)

def compare_letters_nl(letter1: str, letter2: str) -> int:
	return ord(normalize_letter_nl(letter1)) - ord(normalize_letter_nl(letter2))

def normalize_letter_nl(letter: str) -> str:
	match letter:
		case "IJ" | "ij": return "Y"
		case _: return letter.upper()

def preprocess_names_nl(last: str, first: str) -> tuple[str, str]:
	return (remove_prefix(last), first)

def remove_prefix(name: str) -> str:
	for (i, char) in enumerate(name):
		if char.isupper():
			return name[i:]
	return name

def strip_diacritics(char: str) -> str:
	norm = unicodedata.normalize("NFKD", char)
	stripped = "".join(
		strip_diacritics_rune(rune) for rune in norm
		if unicodedata.combining(rune) == 0
	)
	return unicodedata.normalize("NFC", stripped)

def strip_diacritics_rune(rune: str) -> str:
	match rune:
		case "Ø": return "O"
		case "ø": return "o"
		case "\u0131": return "i"
		case _: return rune

def is_latin_letter_az(char: str) -> bool:
	return (
		len(char) == 1 and (
			(0x41 <= ord(char) <= 0x5a)
			or (0x61 <= ord(char) <= 0x7a)
		)
	)

def mid_value(arr: list[T]) -> T:
	count = len(arr)
	if count % 2 == 0:
		raise Exception("No middle element")
	return arr[count // 2]

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion