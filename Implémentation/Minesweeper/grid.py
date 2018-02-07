from tile import Tile

import itertools

class Grid:
	"""
	Grid of a minesweeper game.
	"""

	def __init__(self, num_rows, num_columns, bomb_position_list):
		"""
		Create a grid.

		:n: A number of rows.
		:m: A number of columns.
		:bomb_position_list: A list of positions of bombs.
		"""

		if len(bomb_position_list) > (num_rows * num_columns):
			raise ValueError("Error: the number of bombs can not be greater than (n * m)!")

		self._num_rows = num_rows
		self._num_columns = num_columns
		self._bomb_position_list = list(set(bomb_position_list)) # Remove duplicates.

		# '_number_grid' is a grid of numbers whose each tile contains the number of adjacent bombs ('Tile.BOMB' if this tile contain a bomb).
		self._number_grid = [[0 for j in range(self._num_columns)] for i in range(self._num_rows)]
		self._insert_bombs()
	
	@property
	def num_rows(self):
		return self._num_rows
	
	@property
	def num_columns(self):
		return self._num_columns

	@property
	def bomb_position_list(self):
		return self._bomb_position_list
	
	def _insert_bombs(self):
		"""
		Insert the bombs and compute the numbers of adjacent bombs in the grid of numbers.
		"""

		for bomb_pos in self._bomb_position_list:
			i = bomb_pos[0]
			j = bomb_pos[1]

			self._number_grid[i][j] = Tile.BOMB
			adjacent_tile_list = self.adjacent_tiles(i, j)
			# Remove the tiles containing a bomb. 'adjacent_tile_list' therefore contains the adjacent empty tiles.
			adjacent_tile_list = filter(lambda adj_pos: self._number_grid[adj_pos[0]][adj_pos[1]] == Tile.EMPTY, adjacent_tile_list)
			for adj_tile in adjacent_tile_list:
				self._increment_adjacent_bomb(adj_tile[0], adj_tile[1])

	def adjacent_tiles(self, i, j):
		"""
		Get the adjacent tiles from a position.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: A list of the adjacent tiles of the position.
		"""

		adjacent_tile_list = list(itertools.product([-1, 0, 1], repeat = 2))
		adjacent_tile_list.remove((0, 0))
		adjacent_tile_list = [(i + o1, j + o2) for o1, o2 in adjacent_tile_list]
		adjacent_tile_list = list(filter(lambda pos: self.is_pos_in_grid(pos[0], pos[1]), adjacent_tile_list))

		return adjacent_tile_list

	def is_pos_in_grid(self, i, j):
		"""
		Test if a position is inside the grid.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: True if the position is inside the grid, false otherwise.
		"""

		return (0 <= i < self._num_rows) and (0 <= j < self._num_columns)

	def _increment_adjacent_bomb(self, i, j, n = 1):
		"""
		Increment by 'n' the number of adjacent bombs of a position. The tile of this position must be an empty tile.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:n: The number of adjacent bombs to add (increment).
		"""

		num_tile = self._number_grid[i][j]

		if num_tile == -1:
			raise ValueError("Error: only empty tiles (that does not contain a bomb) can be incremented!")

		new_value = num_tile + n
		assert 0 <= new_value <= 8, "Error: the number of adjacent bombs can not be greater than 8!"

		self._number_grid[i][j] = new_value
	
	def __str__(self):
		str_grid = []
		for row in self._number_grid:
			for tile in row:
				str_grid.append(str(tile))
				str_grid.append('\t')
			str_grid.append('\n')

		return ''.join(str_grid)

	def get_tile(self, i, j):
		"""
		Get tile from a position. The returned value is either Tile.BOMB or the number of adjacent bombs.
		In this last case, the tile is a Tile.EMPTY.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: Tile.BOMB if the tile contains a bomb, the number of adjacent bombs otherwise.
		"""

		return self._number_grid[i][j]

if __name__ == "__main__":
	#bomb_position_list = [(0, 1), (5, 4), (7, 3), (9, 4), (1, 1), (4, 4)]
	bomb_position_list = [(0, 1), (5, 4), (7, 3), (9, 4), (1, 1), (4, 4), (9, 0), (9, 1), (7, 1), (0, 3), (7, 2), (3, 0), (5, 0)]
	g = Grid(10, 5, bomb_position_list)

	print(g)
