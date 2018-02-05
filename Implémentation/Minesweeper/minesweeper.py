from enum import Enum
import random

class Tile(Enum):
	"""
	Tile of a grid.
	"""

	INVISIBLE = -3 # Invisible tile.
	BOMB = -2 # Bomb tile.
	FLAG = -1 # Flag tile.
	EMPTY0 = 0 # Empty tile. It does not contain bomb, it contains a number.
	EMPTY1 = 1
	EMPTY2 = 2
	EMPTY3 = 3
	EMPTY4 = 4
	EMPTY5 = 5
	EMPTY6 = 6
	EMPTY7 = 7
	EMPTY8 = 8

	def __str__(self):
		if self == Tile.INVISIBLE:
			return '⬛︎'
		elif self == Tile.BOMB:
			return 'B'
		elif self == Tile.FLAG:
			return 'F'
		elif (self == Tile.EMPTY0) or (self == Tile.EMPTY1) or (self == Tile.EMPTY2) or (self == Tile.EMPTY3) or \
			(self == Tile.EMPTY4) or (self == Tile.EMPTY5) or (self == Tile.EMPTY6) or (self == Tile.EMPTY7) or \
			(self == Tile.EMPTY8):
			return str(self.value)

		return None

# class Visibility(Enum):
# 	"""
# 	Visibility of a tile.
# 	"""

# 	VISIBLE = 1 # Visible tile.
# 	INVISIBLE = -1 # Invisible tile.

# 	def __str__(self):
# 		if self == Visibility.VISIBLE:
# 			return '⬜︎'
# 		elif self == Visibility.INVISIBLE:
# 			return '⬛︎'

# 		return None

class State(Enum):
	WIN = 1
	LOSE = 2
	CONTINUE = 0 # Unfinished game.

class Grid:
	"""
	Grid of a minesweeper game.
	"""

	def __init__(self, n, m, num_bombs):
		"""
		Create a grid.

		:n: A number of rows.
		:m: A number of columns.
		:num_bombs: A number of bombs.
		"""

		if num_bombs > (n * m):
			raise ValueError("Error: the number of bombs can not be greater than (n * m)!")

		self.n = n
		self.m = m
		self.num_bombs = num_bombs
		self._num_tiles_to_return = (self.n * self.m) - self.num_bombs # Number of tiles to return to win the game.

		self._grid = [[Tile.EMPTY0 for j in range(self.m)] for i in range(self.n)]
		self._insert_bombs()
		self._visibility_grid = [[False for j in range(self.m)] for i in range(self.n)]
		#self._visibility_grid = [[Visibility.I for j in range(self.m)] for i in range(self.n)]
	
	def _insert_bombs(self):
		"""
		Insert bombs in the grid.
		"""

		pos_list = [(i, j) for i in range(self.n) for j in range(self.m)]
		bomb_pos = random.sample(pos_list, self.num_bombs)

		for pos in bomb_pos:
			i = pos[0]
			j = pos[1]

			self._grid[i][j] = Tile.BOMB
			for adj_tile in self._filter_by_empty_tiles(self._get_adjacent_tiles(i, j)):
				self._increment_adjacent_bomb(adj_tile[0], adj_tile[1])

	def _get_adjacent_tiles(self, i, j):
		"""
		Get the adjacent tiles from a position.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: A list of the adjacent tiles of the position.
		"""

		pos_list = []
		for offset in range(3):
			pos_list.append((i - 1, j - 1 + offset))
			pos_list.append((i + 1, j - 1 + offset))
		pos_list.append((i, j - 1))
		pos_list.append((i, j + 1))

		adjacent_tile_list = []
		for pos in pos_list:
			i_temp = pos[0]
			j_temp = pos[1]
			if (0 <= i_temp < self.n) and (0 <= j_temp < self.m):
				adjacent_tile_list.append(pos)

		return adjacent_tile_list

	def _filter_by_empty_tiles(self, position_list):
		"""
		Filter by the empty tiles.

		:position_list: The list of positions to filter.
		:return: The list of positions containing only the empty tiles.
		"""

		position_list_filtered = []
		for pos in position_list:
			tile = self._grid[pos[0]][pos[1]]

			if (tile == Tile.EMPTY0) or (tile == Tile.EMPTY1) or (tile == Tile.EMPTY2) or (tile == Tile.EMPTY3) or \
				(tile == Tile.EMPTY4) or (tile == Tile.EMPTY5) or (tile == Tile.EMPTY6) or (tile == Tile.EMPTY7) or \
				(tile == Tile.EMPTY8):
				position_list_filtered.append(pos)

		return position_list_filtered

	def _increment_adjacent_bomb(self, i, j, n = 1):
		"""
		Increment by 'n' the number of adjacent bombs of a position.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:n: The number of adjacent bombs to add (increment).
		"""

		tile = self._grid[i][j]

		if not((tile == Tile.EMPTY0) or (tile == Tile.EMPTY1) or (tile == Tile.EMPTY2) or (tile == Tile.EMPTY3) or
			(tile == Tile.EMPTY4) or (tile == Tile.EMPTY5) or (tile == Tile.EMPTY6) or (tile == Tile.EMPTY7) or
			(tile == Tile.EMPTY8)):
			raise ValueError("Error: only empty tiles can be incremented!")

		new_value = tile.value + n

		if new_value > 8:
			raise ValueError("Error: the number of adjacent bombs can not be greater than 8!")

		self._grid[i][j] = Tile(new_value)
	
	def __str__(self):
		str_grid = ""
		current_grid = self.get_current_grid()
		for row in current_grid:
			for tile in row:
				str_grid += str(tile) + '\t'
			str_grid += '\n'

		return str_grid

	def get_current_grid(self):
		"""
		Get the current grid (what the user see).

		:return: The current grid.
		"""

		current_grid = [[Tile.INVISIBLE for j in range(self.m)] for i in range(self.n)]
		for i, row in enumerate(self._visibility_grid):
			for j, visibility in enumerate(row):
				current_grid[i][j] = self._grid[i][j] if visibility == True else Tile.INVISIBLE

		return current_grid

	def _print_grid(self):
		"""
		Print the grid with all the visibilities (used for the debugging).
		"""

		str_grid = ""
		for row in self._grid:
			for tile in row:
				str_grid += str(tile) + '\t'
			str_grid += '\n'

		print(str_grid)

	def return_tile(self, i, j):
		"""
		Return a tile.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: The state of the game.
		"""

		if self._grid[i][j] == Tile.BOMB:
			return State.LOSE

		self._visibility_grid[i][j] = True
		self._num_tiles_to_return -= 1

		if self._num_tiles_to_return == 0:
			return State.WIN

		return State.CONTINUE

	# def insert_flag(self, i, j):
	# 	"""
	# 	Insert a flag.

	# 	:i: The index of the row of the flag.
	# 	:j: The index of the column of the flag.
	# 	:return: The state of the game.
	# 	"""

if __name__ == "__main__":
	#random.seed(5)
	g = Grid(10, 5, 10)

	print(g)
