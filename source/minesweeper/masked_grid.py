from minesweeper.grid import Tile, Grid, get_positions

from enum import IntEnum

class MaskedTile(IntEnum):
	"""
	Tile of a grid with walls and mask.
	"""

	EMPTY = Tile.EMPTY.value # Empty tile. It does not contain bomb (corresponds to the number of adjacent bombs).
	BOMB = Tile.BOMB.value # Bomb tile.
	WALL = Tile.WALL.value # Wall tile.
	MASKED = -3 # Masked tile.
	FLAG = -4 # Flag tile.

	def __str__(self):
		if self == MaskedTile.MASKED:
			return '▣'
		elif self == MaskedTile.FLAG:
			return '⚐'
		
		return Tile(self.value).__str__()

	def __eq__(self, other):
		if (self is MaskedTile.MASKED) or (self is MaskedTile.FLAG):
			return super().__eq__(other)
		
		return Tile(self.value) == other

	def __hash__(self):
		return hash(self.value)

assert MaskedTile.MASKED not in Tile.__members__.values()

class MaskedGrid(Grid):
	"""
	Grid with walls and mask (including the visibilities).
	"""

	def __init__(self, num_rows, num_columns, bomb_position_list, left_wall=0, right_wall=0, top_wall=0,
		bottom_wall=0):
		"""
		Create a minesweeper game.

		:num_rows: The number of rows of the grid.
		:num_columns: The number of columns of the grid.
		:bomb_position_list: A list of positions of bombs.
		:left_wall: The thickness of the left wall.
		:right_wall: The thickness of the right wall.
		:top_wall: The thickness of the top wall.
		:bottom_wall: The thickness of the bottom wall.
		"""

		super().__init__(num_rows, num_columns, bomb_position_list, left_wall, right_wall,
			top_wall, bottom_wall)

		tile_at = super().tile_at
		# '_masked_grid' is the mask of the grid: True if the tile at position (i, j) is masked, False othewise.
		# By default, all tiles is masked except the walls.
		self._masked_grid = [
			[(tile_at(i, j) != Tile.WALL) for j in range(self.num_columns)]
			for i in range(self.num_rows)
		]

		self._masked_tile_positions = set(get_positions(num_rows, num_columns, left_wall, right_wall, top_wall,
			bottom_wall))
		self._flag_tile_positions = set()

	@property
	def grid(self):
		"""
		Grid with mask (what the user see).
		"""

		grid = super().grid
		for i, row in enumerate(self._masked_grid):
			for j, masked in enumerate(row):
				if masked:
					grid[i][j] = MaskedTile.MASKED

		for i, j in self._flag_tile_positions:
			grid[i][j] = MaskedTile.FLAG

		return grid
	
	@property
	def num_masked_tiles(self):
		"""
		Number of masked tiles.
		"""

		return len(self._masked_tile_positions)

	@property
	def masked_tile_positions(self):
		"""
		Positions of masked tiles.
		"""

		return list(self._masked_tile_positions)

	@property
	def num_flag_tiles(self):
		"""
		Number of flag tiles.
		"""

		return len(self._flag_tile_positions)

	@property
	def flag_tile_positions(self):
		"""
		Positions of flag tiles.
		"""

		return list(self._flag_tile_positions)
	
	def __str__(self):
		return super().__str__()

	def __eq__(self, other):
		return self.grid == other.grid

	def __hash__(self):
		return hash(tuple(map(tuple, self.grid)))

	def __iter__(self):
		"""
		Iterate on rows of the grid.
		"""

		return (row for row in self.grid)

	def tile_at(self, i, j):
		"""
		Get tile at a position. The returned value is either Tile.MASKED, Tile.WALL, Tile.BOMB or the number of
		adjacent bombs.
		In this last case, the tile is a Tile.EMPTY.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: Tile.MASKED if the tile is masked, Tile.WALL if the tile contains a wall,
			Tile.BOMB if the tile contains a bomb, the number of adjacent bombs otherwise.
		"""

		if self._masked_grid[i][j]:
			if (i, j) in self._flag_tile_positions:
				return MaskedTile.FLAG
			return MaskedTile.MASKED

		return super().tile_at(i, j)

	def unmask_tile(self, i, j):
		"""
		Unmask on a tile and all the empty tiles around.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: A set of the position of unmasked tiles.
		"""

		unmasked_tiles = set()
		tile = super().tile_at(i, j)

		was_unmasked = self._unmask_tile(i, j)
		if not was_unmasked:
			print(self._masked_tile_positions)
			if not ((i, j) in self._masked_tile_positions):
				raise ValueError("Error: the tile (at {}, {}) is already unmasked or is a wall!".format(i, j))

			if (i, j) in self._flag_tile_positions:
				raise ValueError("Error: the tile (at {}, {}) contains a flag!".format(i, j))

		unmasked_tiles.add((i, j))

		# In this step, tile is not masked and does not contain a flag.

		if (tile != MaskedTile.EMPTY) or (tile > 0):
			return unmasked_tiles

		# Explore and unmask the empty tiles around 'tile'.
		tiles_to_explore = set()
		tiles_to_explore.update(self.adjacent_tiles(i, j))
		while tiles_to_explore: # While 'tiles_to_explore' contains positions.
			i_temp, j_temp = tiles_to_explore.pop()
			tile_temp = super().tile_at(i_temp, j_temp) # 'tile_temp' is an empty tile.

			was_unmasked = self._unmask_tile(i_temp, j_temp)
			unmasked_tiles.add((i_temp, j_temp))
			if was_unmasked and (tile_temp == 0):
				tiles_to_explore.update(self.adjacent_tiles(i_temp, j_temp))

		return unmasked_tiles

	def unmask_all_tiles(self):
		"""
		Unmask all tiles. The 'num_masked_tiles' counter is equal to 0 after calling this function.
		"""

		self.remove_all_flags()

		for i in range(self.num_rows):
			for j in range(self.num_columns):
				self._unmask_tile(i, j)

	def insert_flag(self, i, j):
		"""
		Insert a flag at position 'i' and 'j'.
		The tile at this position must be masked. If it is not, then this function returns False.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the flag was added, False otherwise.
		"""

		if self.tile_at(i, j) == MaskedTile.MASKED:
			self._flag_tile_positions.add((i, j))

			return True

		return False

	def insert_flags(self, position_list):
		"""
		Insert a flag for position 'i' and 'j' of 'position_list'.
		The tiles at these positions must be masked. If it is not, then this function returns False.

		:position_list: The list of positions of flags.
		:return: True if the all flags were added, False otherwise (some flags were not added).
		"""

		all_flags_added = True
		for i, j in position_list:
			flag_added = self.insert_flag(i, j)
			all_flags_added = all_flags_added and flag_added

		return all_flags_added

	def remove_flag(self, i, j):
		"""
		Remove a flag at position 'i' and 'j'.
		The tile at this position must contain a flag. If it is not, then this function returns False.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the flag was removed, False otherwise.
		"""

		try: # If this position contains a flag, then remove it.
			self._flag_tile_positions.remove((i, j))
		except KeyError:
			return False

		return True

	def remove_all_flags(self):
		"""
		Remove all flags.
		"""

		self._flag_tile_positions.clear()

	def _unmask_tile(self, i, j):
		"""
		Unmask one tile at position 'i' and 'j'. It reveals the tile in this position and decrements by one the
		variable 'num_masked_tiles'.
		The tile at this position must be masked and it does must not contain a flag. If it is not, then this function
		returns False.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile was unmasked, False otherwise.
		"""

		if not(self._masked_grid[i][j]) or ((i, j) in self._flag_tile_positions):
			return False

		self._masked_grid[i][j] = False
		self._masked_tile_positions.remove((i, j))

		return True

if __name__ == "__main__":
	bomb_position_list = [(0, 1), (5, 4), (4, 2), (9, 4), (2, 1), (4, 4), (9, 0), (9, 1), (7, 1), (0, 3), (7, 2),
		(3, 0)]
	g = MaskedGrid(10, 5, bomb_position_list)
	print(g)
	unmasked_tiles = g.unmask_tile(0, 0)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(2, 4)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(5, 3)
	print("{}{}\n".format(g, unmasked_tiles))

	print("\n\n\n")

	bomb_position_list = [(5, 4), (4, 2), (2, 1), (4, 4)]
	g = MaskedGrid(10, 5, bomb_position_list, 1, 0, 2, 3)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(2, 4)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(5, 3)
	print("{}{}\n".format(g, unmasked_tiles))

	print("\n\n\n")

	bomb_position_list = [(1, 0), (5, 4), (5, 2), (9, 4), (5, 1), (5, 4), (9, 0), (9, 1), (7, 1), (0, 3), (7, 2),
		(3, 0)]
	g = MaskedGrid(10, 5, bomb_position_list)
	print(g)
	g.insert_flag(0, 1)
	g.insert_flag(3, 4)
	g.insert_flag(4, 2)
	print(g)
	unmasked_tiles = g.unmask_tile(0, 0)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(2, 4)
	print("{}{}\n".format(g, unmasked_tiles))
	unmasked_tiles = g.unmask_tile(5, 3)
	print("{}{}\n".format(g, unmasked_tiles))
	g.unmask_all_tiles()
	print(g)
