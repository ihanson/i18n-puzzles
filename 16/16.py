from typing import Iterator, Self
import box_drawing

use_test = False

def run(lines: Iterator[str]):
	(top_left, bottom_right) = (
		((0, 0), (7, 11)) if use_test
		else ((4, 7), (19, 72))
	)
	game = PipesGrid.from_screen(list(lines), top_left, bottom_right)
	rotations = game.lock_known()
	print(game)
	if game.all_locked():
		print(f"Solved in {rotations} rotations")

class PipeGameError(Exception):
	pass

class GameCell(object):
	def clone(self) -> Self:
		raise NotImplementedError()
	
	@property
	def box_char(self) -> box_drawing.BoxChar:
		raise NotImplementedError()

	@property
	def is_locked(self) -> bool:
		raise NotImplementedError()

class BackgroundCell(GameCell):
	def __init__(self, char: str):
		if len(char) != 1:
			raise ValueError("Background cell must have exactly one character")
		self.__char = char
	
	def __str__(self) -> str:
		return self.__char
	
	@property
	def box_char(self) -> box_drawing.BoxChar:
		return box_drawing.BoxChar(0, 0, 0, 0)
	
	@property
	def is_locked(self) -> bool:
		return True
	
	def clone(self) -> Self:
		return self

class PipeCell(GameCell):
	def __init__(self, box_char: box_drawing.BoxChar, locked: bool = False):
		self.__box_char = box_char
		self.__locked = locked or box_drawing.has_single_orientation(box_char)
	
	def __str__(self) -> str:
		return box_drawing.reverse_map[self.box_char]
	
	@property
	def box_char(self) -> box_drawing.BoxChar:
		return self.__box_char

	@property
	def is_locked(self) -> bool:
		return self.__locked
	
	def rotate_cw(self, count=1) -> int:
		if self.is_locked:
			raise PipeGameError("Cannot rotate locked cell")
		for _ in range(count):
			self.__box_char = box_drawing.rotate_box_char_cw(self.box_char)
		return count
	
	def lock(self):
		self.__locked = True
	
	def clone(self) -> Self:
		return PipeCell(self.__box_char, self.__locked)

class PipesGrid(object):
	def __init__(self, grid: list[list[GameCell]]):
		self.__grid = list(list(cell.clone() for cell in row) for row in grid)
	
	def clone(self) -> Self:
		return PipesGrid(self.__grid)
	
	def lock_known(self) -> int:
		total_rotations = 0
		while (rotations := self.__expand_locked()) != 0:
			total_rotations += rotations
		return total_rotations
	
	def all_locked(self) -> bool:
		return all(
			all(cell.is_locked for cell in row)
			for row in self.__grid
		)
	
	def __expand_locked(self) -> int:
		total_rotations = 0
		for (y, row) in enumerate(self.__grid):
			for (x, cell) in enumerate(row):
				if isinstance(cell, PipeCell) and not cell.is_locked:
					rotations = list(possible_valid_rotations(
						cell,
						self.cell_at(y - 1, x),
						self.cell_at(y, x + 1),
						self.cell_at(y + 1, x),
						self.cell_at(y, x - 1)
					))
					if len(rotations) == 0:
						raise PipeGameError("No valid rotations")
					if len(rotations) == 1:
						total_rotations += cell.rotate_cw(rotations[0])
						cell.lock()
		return total_rotations

	def cell_at(self, y: int, x: int) -> GameCell:
		return self.__grid[y][x] if (
			0 <= y < len(self.__grid)
			and 0 <= x < len(self.__grid[y])
		) else BackgroundCell(" ")

	def __str__(self) -> str:
		return "\n".join(
			"".join(str(cell) for cell in row)
			for row in self.__grid
		)
	
	@staticmethod
	def from_screen(screen: list[str], top_left: tuple[int, int], bottom_right: tuple[int, int]):
		(top_left_y, top_left_x) = top_left
		(bottom_right_y, bottom_right_x) = bottom_right
		return PipesGrid(
			[
				PipeCell(
					box_drawing.box_chars[char],
					(y, x) in [top_left, bottom_right]
				)
				if (
					top_left_x <= x <= bottom_right_x
					and top_left_y <= y <= bottom_right_y
					and char in box_drawing.box_chars
				)
				else BackgroundCell(char)
				for (x, char) in enumerate(row)
			]
			for (y, row) in enumerate(screen)
		)

def possible_valid_rotations(
		cell: GameCell,
		north: GameCell,
		east: GameCell,
		south: GameCell,
		west: GameCell
	) -> Iterator[int]:
	north_edges = box_drawing.edge_counts(north.box_char) if not north.is_locked else {north.box_char.S}
	east_edges = box_drawing.edge_counts(east.box_char) if not east.is_locked else {east.box_char.W}
	south_edges = box_drawing.edge_counts(south.box_char) if not south.is_locked else {south.box_char.N}
	west_edges = box_drawing.edge_counts(west.box_char) if not west.is_locked else {west.box_char.E}
	
	for (rotation_count, rotated) in box_drawing.rotations(cell.box_char):
		if (
			rotated.N in north_edges
			and rotated.E in east_edges
			and rotated.S in south_edges
			and rotated.W in west_edges
		):
			yield rotation_count

#region Common code
if __name__ == "__main__":
	import pathlib
	input_path = pathlib.Path(__file__).parent.joinpath("test-input.txt" if use_test else "input.txt")
	with open(input_path, encoding="cp437") as in_file:
		run(line.rstrip("\n") for line in in_file)
#endregion
