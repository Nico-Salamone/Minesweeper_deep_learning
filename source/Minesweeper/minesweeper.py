from masked_grid import MaskedTile, MaskedGrid

import random

SEED = None

class Minesweeper:
	"""
	Minesweeper game.
	"""

	def __init__(self, num_rows, num_columns, num_bombs):
		"""
		Create a minesweeper game.

		:num_rows: The number of rows of the grid.
		:num_columns: The number of columns of the grid.
		:num_bombs: The number of bombs of the grid.
		"""

		pos_list = [(i, j) for i in range(num_rows) for j in range(num_columns)]
		bomb_position_list = random.sample(pos_list, num_bombs)

		self._grid = MaskedGrid(num_rows, num_columns, bomb_position_list)

	@property
	def num_rows(self):
		"""
		Number of rows.
		"""

		return self._grid.num_rows
	
	@property
	def num_columns(self):
		"""
		Number of columns.
		"""

		return self._grid._num_columns

	@property 
	def num_bombs(self):
		"""
		Number of bombs of the grid.
		"""

		return self._grid.num_bombs

	@property
	def num_masked_tiles(self):
		"""
		Number of masked tiles.
		"""

		return self._grid.num_masked_tiles

	@property
	def grid(self):
		"""
		Grid.
		"""

		return self._grid.grid

	def __str__(self):
		return str(self._grid)

	def within_boundaries(self, i, j):
		"""
		Test if a position is within the boundaries.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: True if the position is within the boundaries, False otherwise.
		"""

		return self._grid.within_boundaries(i, j)

	def is_tile_masked(self, i, j):
		"""
		Test if a tile is masked or not masked.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile is masked, False otherwise.
		"""

		return self._grid.is_tile_masked(i, j)

	def tile_at(self, i, j):
		"""
		Get tile at a position. The returned value is either Tile.MASKED, Tile.BOMB or the number of adjacent bombs.
		In this last case, the tile is a Tile.EMPTY.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: Tile.MASKED if the tile is masked, Tile.BOMB if the tile contains a bomb, the number of adjacent bombs otherwise.
		"""

		if self._grid.is_tile_masked(i, j):
			return MaskedTile.MASKED		

		return MaskedTile.convert_tile_to_masked_tile(self._grid.tile_at(i, j))

	def play_tile(self, i, j):
		"""
		Play on a tile.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: The tile at position 'i' and 'j'.
		"""

		return self._grid.unmask_tiles(i, j)

	def reveal_all_tiles(self):
		"""
		Reveal all tiles. The 'num_masked_tiles' counter is equal to 0 after calling this function.
		"""

		self._grid.unmask_all_tiles()

if __name__ == "__main__":
	random.seed(SEED)
	ms = Minesweeper(10, 5, 6)

	print(ms)

	pos = input("Enter a position: ")
	pos = tuple([int(i) for i in pos.split(' ')])
	tile = ms.play_tile(pos[0], pos[1])
	print(ms, "\n\n")
	while (tile == MaskedTile.EMPTY) and ((ms.num_masked_tiles - ms.num_bombs) > 0):
		pos = input("Enter a position: ")
		pos = tuple([int(i) for i in pos.split(' ')])
		tile = ms.play_tile(pos[0], pos[1])
		print(ms, "\n\n")

	if tile == MaskedTile.BOMB:
		print("You lost!")
	else:
		print("You won!")

	ms.reveal_all_tiles()
	print(ms)
