
from collections import namedtuple
from typing import Iterator, Self

BoxChar = namedtuple("BoxChar", ["N", "E", "S", "W"])

def rotate_box_char_cw(char: BoxChar) -> BoxChar:
	return BoxChar(char.W, char.N, char.E, char.S)

def has_single_orientation(char: BoxChar) -> bool:
	return char == rotate_box_char_cw(char)

def edge_counts(char: BoxChar) -> set[int]:
	return set(char)

def rotations(char: BoxChar) -> Iterator[tuple[int, BoxChar]]:
	rotation = char
	seen: set[BoxChar] = set()
	for count in range(4):
		if rotation not in seen:
			yield (count, rotation)
			seen.add(rotation)
		rotation = rotate_box_char_cw(rotation)

def box_char_matches(center: BoxChar, north: BoxChar, east: BoxChar, south: BoxChar, west: BoxChar) -> bool:
	return (
		center.N == north.S
		and center.E == east.W
		and center.S == south.N
		and center.W == west.E
	)

# (N, E, S, W)
box_chars = {
	" ": BoxChar(0, 0, 0, 0),
	"│": BoxChar(1, 0, 1, 0),
	"┤": BoxChar(1, 0, 1, 1),
	"╡": BoxChar(1, 0, 1, 2),
	"╢": BoxChar(2, 0, 2, 1),
	"╖": BoxChar(0, 0, 2, 1),
	"╕": BoxChar(0, 0, 1, 2),
	"╣": BoxChar(2, 0, 2, 2),
	"║": BoxChar(2, 0, 2, 0),
	"╗": BoxChar(0, 0, 2, 2),
	"╝": BoxChar(2, 0, 0, 2),
	"╜": BoxChar(2, 0, 0, 1),
	"╛": BoxChar(1, 0, 0, 2),
	"┐": BoxChar(0, 0, 1, 1),
	"└": BoxChar(1, 1, 0, 0),
	"┴": BoxChar(1, 1, 0, 1),
	"┬": BoxChar(0, 1, 1, 1),
	"├": BoxChar(1, 1, 1, 0),
	"─": BoxChar(0, 1, 0, 1),
	"┼": BoxChar(1, 1, 1, 1),
	"╞": BoxChar(1, 2, 1, 0),
	"╟": BoxChar(2, 1, 2, 0),
	"╚": BoxChar(2, 2, 0, 0),
	"╔": BoxChar(0, 2, 2, 0),
	"╩": BoxChar(2, 2, 0, 2),
	"╦": BoxChar(0, 2, 2, 2),
	"╠": BoxChar(2, 2, 2, 0),
	"═": BoxChar(0, 2, 0, 2),
	"╬": BoxChar(2, 2, 2, 2),
	"╧": BoxChar(1, 2, 0, 2),
	"╨": BoxChar(2, 1, 0, 1),
	"╤": BoxChar(0, 2, 1, 2),
	"╥": BoxChar(0, 1, 2, 1),
	"╙": BoxChar(2, 1, 0, 0),
	"╘": BoxChar(1, 2, 0, 0),
	"╒": BoxChar(0, 2, 1, 0),
	"╓": BoxChar(0, 1, 2, 0),
	"╫": BoxChar(2, 1, 2, 1),
	"╪": BoxChar(1, 2, 1, 2),
	"┘": BoxChar(1, 0, 0, 1),
	"┌": BoxChar(0, 1, 1, 0)
}

reverse_map = {bc: char for (char, bc) in box_chars.items()}