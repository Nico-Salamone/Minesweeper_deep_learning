from tile import Tile
from grid import Grid

import random

class Minesweeper:
	"""
	Minesweeper game.
	"""

	def __init__(self, num_rows, num_columns, num_bombs):
		"""
		Create a minesweeper game.

		:n: The number of rows of the grid.
		:m: The number of columns of the grid.
		:num_bombs: The number of bombs of the grid.
		"""

		if num_bombs > (num_rows * num_columns):
			raise ValueError("Error: the number of bombs can not be greater than (n * m)!")

		pos_list = [(i, j) for i in range(num_rows) for j in range(num_columns)]
		bomb_position_list = random.sample(pos_list, num_bombs)

		self._grid = Grid(num_rows, num_columns, bomb_position_list)

		self._num_remaining_hidden_empty_tiles = (self.num_rows * self.num_columns) - self.get_number_bombs()
		self._visibility_grid = [[False for j in range(self.num_columns)] for i in range(self.num_rows)]
	
	@property
	def num_rows(self):
		return self._grid.num_rows
	
	@property
	def num_columns(self):
		return self._grid.num_columns

	@property
	def num_remaining_hidden_empty_tiles(self):
		return self._num_remaining_hidden_empty_tiles

	def get_number_bombs(self):
		"""
		Get the number of bombs of the grid.

		:return: The number of bombs of the grid.
		"""

		return len(self._grid.bomb_position_list)
	
	def __str__(self):
		str_grid = []
		current_grid = self.get_current_grid()
		for row in current_grid:
			for tile in row:
				str_grid.append(str(tile))
				str_grid.append('\t')
			str_grid += '\n'

		return ''.join(str_grid)

	def get_current_grid(self):
		"""
		Get the current grid (what the user see).

		:return: The current grid.
		"""

		current_grid = [[Tile.INVISIBLE for j in range(self.num_columns)] for i in range(self.num_rows)]
		for i, row in enumerate(self._visibility_grid):
			for j, visibility in enumerate(row):
				if visibility == True:
					current_grid[i][j] = self._grid.get_tile(i, j)

		return current_grid

	def is_tile_visible(self, i, j):
		"""
		Test if a tile is visible or invisible.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile is visible, false otherwise.
		"""

		return self._visibility_grid[i][j]

	def play_tile(self, i, j):
		"""
		Play on a tile.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: The tile at position 'i' and 'j'.
		"""

		tile = self._grid.get_tile(i, j)

		already_revealed = self._reveal_tile(i, j)
		if (not already_revealed) and (tile == Tile.EMPTY) and (tile == 0):
			# Explore and reveal the empty tiles around 'tile'.
			tiles_to_explore = set()
			tiles_to_explore.update(self._grid.adjacent_tiles(i, j))
			while tiles_to_explore: # While 'tiles_to_explore' contains positions.
				i_temp, j_temp = tiles_to_explore.pop()
				tile_temp = self._grid.get_tile(i_temp, j_temp) # 'tile_temp' is a empty tile.

				already_revealed = self._reveal_tile(i_temp, j_temp)

				if (not already_revealed) and (tile_temp == 0):
					tiles_to_explore.update(self._grid.adjacent_tiles(i_temp, j_temp))

		return tile

	def _reveal_tile(self, i, j):
		"""
		Reveal a tile. It makes a tile visible and decrements by one the varaible 'num_remaining_hidden_empty_tiles'.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile has already been revealed, false otherwise.
		"""

		if not self._visibility_grid[i][j]:
			self._visibility_grid[i][j] = True
			if self._grid.get_tile(i, j) == Tile.EMPTY:
				self._num_remaining_hidden_empty_tiles -= 1

			return False

		return True

	def reveal_all_tiles(self):
		"""
		Reveal all tiles. The 'num_remaining_hidden_empty_tiles' counter is equal to 0 after calling this function.
		"""

		for i in range(self.num_rows):
			for j in range(self.num_columns):
				self._reveal_tile(i, j)

if __name__ == "__main__":
	#random.seed(5)
	ms = Minesweeper(10, 5, 6)

	print(ms)

	pos = input("Enter a position: ")
	pos = tuple([int(i) for i in pos.split(' ')])
	tile = ms.play_tile(pos[0], pos[1])
	print(ms)
	while (tile == Tile.EMPTY) and (ms.num_remaining_hidden_empty_tiles > 0):
		pos = input("Enter a position: ")
		pos = tuple([int(i) for i in pos.split(' ')])
		tile = ms.play_tile(pos[0], pos[1])
		print(ms)

	if tile == Tile.BOMB:
		print("You lost!")

		ms.reveal_all_tiles()
		print(ms)
	else:
		print("You won!")
