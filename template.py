from typing import Iterator

use_test = True

def run(lines: Iterator[str]):
	...

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
