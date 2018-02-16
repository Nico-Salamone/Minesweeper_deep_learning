from enum import IntEnum
import itertools
import copy

class Tile(IntEnum):
	"""
	Tile of a grid with walls.
	"""

	EMPTY = 0 # Empty tile. It does not contain bomb (corresponds to the number of adjacent bombs).
	BOMB = -1 # Bomb tile.
	WALL = -2 # Wall tile.

	def __str__(self):
		if self == Tile.EMPTY:
			return str(self.value)
		elif self == Tile.BOMB:
			return '¤'
		elif self == Tile.WALL:
			return '▩'
		
		return ''

	def __eq__(self, other):
		if self is Tile.EMPTY:
			if 0 <= other <= 8:
				return True
			
			return False
		
		return super().__eq__(other)

class Grid:
	"""
	Grid of a minesweeper game with walls.
	"""

	def __init__(self, num_rows, num_columns, bomb_position_list, left_wall=0, right_wall=0,
			top_wall=0, bottom_wall=0):
		"""
		Create a grid.

		:num_rows: A number of rows.
		:num_columns: A number of columns.
		:bomb_position_list: A list of positions of bombs.
		:left_wall: The thickness of the left wall.
		:right_wall: The thickness of the right wall.
		:top_wall: The thickness of the top wall.
		:bottom_wall: The thickness of the bottom wall.
		"""

		num_bombs = len(bomb_position_list)
		if num_bombs > (num_rows * num_columns):
			raise ValueError("Error: the number of bombs ({}) can not be greater than 'num_rows' * 'num_columns' " \
				"({} * {})!".format(num_bombs, num_rows, num_columns))

		if (left_wall + right_wall) >= num_columns:
			raise ValueError("Error: the sum the thickness of the left wall ({}) and the right wall ({}) can not be greater " \
				"than or equal to the number of columns ({})!".format(left_wall, right_wall, num_columns))
		if (top_wall + bottom_wall) >= num_rows:
			raise ValueError("Error: the sum the thickness of the top wall ({}) and the bottom wall ({}) can not be greater " \
				"than or equal to the number of rows ({})!".format(top_wall, bottom_wall, num_rows))

		self._num_rows = num_rows
		self._num_columns = num_columns
		self._bomb_position_list = list(set(bomb_position_list)) # Remove duplicates.
		self._left_wall = left_wall
		self._right_wall = right_wall
		self._top_wall = top_wall
		self._bottom_wall = bottom_wall

		# '_grid' is a grid of numbers whose each tile contains the number of adjacent bombs or 'Tile.BOMB' if this tile
		# contains a bomb or 'Tile.WALL' if this tile contains a wall.
		self._grid = [[0 for j in range(self.num_columns)] for i in range(self.num_rows)]
		self._insert_walls()
		self._insert_bombs()

	@property
	def grid(self):
		"""
		Grid.
		"""

		return copy.deepcopy(self._grid)
	
	@property
	def num_rows(self):
		"""
		Number of rows.
		"""

		return self._num_rows
	
	@property
	def num_columns(self):
		"""
		Number of columns.
		"""

		return self._num_columns

	@property 
	def num_bombs(self):
		"""
		Number of bombs of the grid.
		"""

		return len(self._bomb_position_list)

	@property
	def bomb_position_list(self):
		"""
		List of positions of bombs.
		"""

		return list(self._bomb_position_list)

	@property
	def left_wall(self):
		"""
		Thickness of the left wall.
		"""

		return self._left_wall

	@property
	def right_wall(self):
		"""
		Thickness of the right wall.
		"""

		return self._right_wall

	@property
	def top_wall(self):
		"""
		Thickness of the top wall.
		"""

		return self._top_wall

	@property
	def bottom_wall(self):
		"""
		Thickness of the bottom wall.
		"""

		return self._bottom_wall

	@property
	def num_tiles(self):
		"""
		Number of tiles (without the walls).
		"""

		num_rows = self.num_rows - self.top_wall - self.bottom_wall
		num_columns = self.num_columns - self.left_wall - self.right_wall

		return num_rows * num_columns

	def __str__(self):
		str_grid = []

		str_grid.append("-\t \t")
		for i in range(self.num_columns):
			str_grid.append(str(i))
			str_grid.append('\t')
		str_grid.append("\n\n")

		for i in range(self.num_rows):
			str_grid.append(str(i))
			str_grid.append("\t \t")

			for j in range(self.num_columns):
				str_grid.append(str(self.tile_at(i, j)))
				str_grid.append('\t')
			str_grid.append('\n')

		return ''.join(str_grid)

	def tile_at(self, i, j):
		"""
		Get tile at a position. The returned value is either Tile.WALL, Tile.BOMB or the number of adjacent bombs.
		In this last case, the tile is a Tile.EMPTY.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: Tile.WALL if the tile contains a wall, Tile.BOMB if the tile contains a bomb, the number of adjacent bombs otherwise.
		"""

		return self._grid[i][j]

	def within_boundaries(self, i, j, include_walls = False):
		"""
		Test if a position is within the boundaries.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:include_walls: True if the walls are included, False otherwise.
		:return: True if the position is within the boundaries, False otherwise.
		"""

		if include_walls:
			min_i = 0
			max_i = self.num_rows - 1
			min_j = 0
			max_j = self.num_columns - 1
		else:
			min_i = self.top_wall
			max_i = self.num_rows - self.bottom_wall - 1
			min_j = self.left_wall
			max_j = self.num_columns - self.right_wall - 1

		return (min_i <= i <= max_i) and (min_j <= j <= max_j)

	def adjacent_tiles(self, i, j):
		"""
		Get a list of the adjacent tiles from a position. It does not contain the position outside the grid and
		the position of tiles which contains a wall. It therefore contains positions of the empty and bomb tiles.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: A list of the adjacent tiles of the position.
		"""

		adjacent_tile_list = list(itertools.product([-1, 0, 1], repeat=2))
		adjacent_tile_list.remove((0, 0))
		adjacent_tile_list = [(i + o1, j + o2) for o1, o2 in adjacent_tile_list]
		adjacent_tile_list = list(filter(lambda pos: self.within_boundaries(pos[0], pos[1]), adjacent_tile_list))

		return adjacent_tile_list

	def _insert_walls(self):
		"""
		Insert the walls in the grid of numbers.
		"""

		# 'i' is the iterator of the rows.
		# 'j' is the iterator of the columns.
		
		# Left wall.
		for j in range(self.left_wall):
			for i in range(self.num_rows):
				self._grid[i][j] = Tile.WALL

		# Right wall.
		for j in range(self.num_columns - self.right_wall, self.num_columns):
			for i in range(self.num_rows):
				self._grid[i][j] = Tile.WALL

		# Top wall.
		for i in range(self.top_wall):
			for j in range(self.num_columns):
				self._grid[i][j] = Tile.WALL

		# Bottom wall.
		for i in range(self.num_rows - self.bottom_wall, self.num_rows):
			for j in range(self.num_columns):
				self._grid[i][j] = Tile.WALL
	
	def _insert_bombs(self):
		"""
		Insert the bombs and compute the numbers of adjacent bombs in the grid of numbers.
		"""

		for i, j in self.bomb_position_list:

			if self._grid[i][j] == Tile.WALL:
				raise ValueError("Error: can not put a bomb (at {}, {}) on a wall!".format(i, j))

			self._grid[i][j] = Tile.BOMB
			adjacent_tile_list = self.adjacent_tiles(i, j)
			is_empty_tile = lambda adj_pos: self._grid[adj_pos[0]][adj_pos[1]] == Tile.EMPTY
			# Remove the tiles containing a bomb. 'adjacent_tile_list' therefore contains the adjacent empty tiles.
			for adj_tile in filter(is_empty_tile, adjacent_tile_list):
				self._increment_adjacent_bomb(adj_tile[0], adj_tile[1])

	def _increment_adjacent_bomb(self, i, j, n=1):
		"""
		Increment by 'n' the number of adjacent bombs of a position. The tile of this position must be an empty tile.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:n: The number of adjacent bombs to add (increment).
		"""

		num_tile = self._grid[i][j]
		assert num_tile == Tile.EMPTY, "Error: only empty tiles (that does not contain a bomb or a wall) can be incremented!"

		new_value = num_tile + n
		assert 0 <= new_value <= 8, "Error: the number of adjacent bombs can not be greater than 8!"

		self._grid[i][j] = new_value

if __name__ == "__main__":
	bomb_position_list = [(0, 1), (5, 4), (4, 2), (9, 4), (2, 1), (4, 4), (9, 0), (9, 1), (7, 1), (0, 3), (7, 2), (3, 0)]
	g = Grid(10, 5, bomb_position_list)
	print(g)

	print("\n\n\n")

	bomb_position_list = [(5, 4), (4, 2), (2, 1), (4, 4)]
	g = Grid(10, 5, bomb_position_list, 1, 0, 2, 3)
	print(g)
