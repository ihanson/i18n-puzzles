from typing import Iterator, TypeVar
import base64
import functools

use_test = False

def run(lines: Iterator[str]):
	bitstream = decode_bytes(base64.b64decode("".join(lines)))
	bytes_stream = stream_decoded_bytes(bitstream)
	read_bytes: list[int] = []
	while True:
		try:
			read_bytes.append(next(bytes_stream))
		except:
			break
	print(bytes(read_bytes).decode("utf-8"))

def decode_bytes(input_bytes: bytes) -> Iterator[bool]:
	for char in input_bytes.decode("utf-16"):
		yield from bottom_bits(ord(char), 20)

def stream_decoded_bytes(bits: Iterator[bool]) -> Iterator[int]:
	retrieved_bits: list[bool] = []
	while True:
		piece = next_ext_utf8_bits(bits)
		while len(piece) > 28 and not piece[0]:
			piece.pop(0)
		while len(piece) < 28:
			piece.insert(0, False)
		retrieved_bits += piece
		while len(retrieved_bits) >= 8:
			yield byte_from_bits(retrieved_bits[:8])
			retrieved_bits = retrieved_bits[8:]

def byte_from_bits(bits: list[bool]):
	return functools.reduce(
		lambda acc, bit: (acc << 1) + bit,
		bits,
		0
	)

def bottom_bits(number: int, count: int) -> Iterator[bool]:
	for pos in reversed(range(count)):
		yield bool((number >> pos) & 0x01)

def next_ext_utf8_bits(bits: Iterator[bool]) -> list[bool]:
	result: list[bool] = []
	count = 0
	while next(bits):
		count += 1
	result += list(take(bits, 8 - (count + 1)))
	for _ in range(count - 1):
		continuing = list(take(bits, 2))
		assert continuing == [True, False]
		result += list(take(bits, 6))
	return result

def next_byte(bits: Iterator[bool]) -> int:
	number = 0
	for _ in range(8):
		number = (number << 1) + next(bits)
	return number

T = TypeVar("T")
def take(iterator: Iterator[T], count: int) -> Iterator[T]:
	for _ in range(count):
		yield next(iterator)

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="utf-8") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
