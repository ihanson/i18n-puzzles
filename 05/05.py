from typing import Iterator

use_test = False

def run(lines: Iterator[str]):
	park = [list(line) for line in lines]
	(x, y) = (0, 0)
	count = 0
	while y < len(park):
		if park[y][x] == "💩":
			count += 1
		(x, y) = ((x + 2) % len(park[y]), y + 1)
	print(count)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
