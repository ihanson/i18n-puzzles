from typing import Iterator
import fractions

use_test = False
numerals = {
	"一": 1, # ichi
	"二": 2, # ni
	"三": 3, # san
	"四": 4, # yon
	"五": 5, # go
	"六": 6, # roku
	"七": 7, # nana
	"八": 8, # hachi
	"九": 9, # kyu
	"十": 10, # ju
	"百": 100, # hyaku
	"千": 1_000, # sen
	"万": 10_000, # man
	"億": 100_000_000 # ichioku
}
length_units = {
	"毛": fractions.Fraction(1, 10_000), # mo
	"厘": fractions.Fraction(1, 1_000), # rin
	"分": fractions.Fraction(1, 100), # bu
	"寸": fractions.Fraction(1, 10), # sun
	"尺": fractions.Fraction(1), # shaku,
	"間": fractions.Fraction(6), # ken
	"丈": fractions.Fraction(10), # jo
	"町": fractions.Fraction(360), # cho
	"里": fractions.Fraction(12_960) # ri
}

def run(lines: Iterator[str]):
	print(sum(
		int(parse_area_sqm(line))
		for line in lines
	))

def parse_area_sqm(area_line: str) -> int:
	(width, height) = split_on(area_line, "\xd7")
	return (
		parse_japanese_length_meters(width.strip())
		* parse_japanese_length_meters(height.strip())
	)

def parse_japanese_numeral(numeral: str) -> int:
	if len(numeral) == 0:
		return 0
	if numeral in numerals:
		return numerals[numeral]
	rest = numeral
	(ichioku, rest) = partial_parse_numeral(rest, "億")
	(man, rest) = partial_parse_numeral(rest, "万")
	(sen, rest) = partial_parse_numeral(rest, "千")
	(hyaku, rest) = partial_parse_numeral(rest, "百")
	(ju, rest) = partial_parse_numeral(rest, "十")
	return (
		ichioku
		+ man
		+ sen
		+ hyaku
		+ ju
		+ parse_japanese_numeral(rest)
	)

def partial_parse_numeral(numeral: str, multiplier: str) -> tuple[int, str]:
	if multiplier not in numeral:
		return (0, numeral)
	(mult_value, rest) = split_on(numeral, multiplier)
	return (
		(parse_japanese_numeral(mult_value) if len(mult_value) > 0 else 1)
		* numerals[multiplier],
		rest
	)

def parse_japanese_length_meters(length: str) -> int:
	return (
		parse_japanese_numeral(length[:-1])
		* length_units[length[-1]]
		* fractions.Fraction(10, 33)
	)

def split_on(string: str, split: str) -> tuple[str, str]:
	if split not in string:
		return ("", string)
	index = string.index(split)
	return (string[:index], string[index + 1:])

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
