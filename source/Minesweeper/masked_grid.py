from grid import Tile, Grid

from enum import IntEnum

class MaskedTile(IntEnum):
	"""
	Tile of a grid with walls and mask.
	"""

	EMPTY = Tile.EMPTY.value # Empty tile. It does not contain bomb (corresponds to the number of adjacent bombs).
	BOMB = Tile.BOMB.value # Bomb tile.
	WALL = Tile.WALL.value # Wall tile.
	MASKED = -3 # Masked tile.

	def __str__(self):
		if self == MaskedTile.MASKED:
			return '▣'
		
		return Tile(self.value).__str__()

	def __eq__(self, other):
		if self is MaskedTile.MASKED:
			return super().__eq__(other)
		
		return Tile(self.value) == other

	@classmethod
	def convert_tile_to_masked_tile(cls, tile):
		"""
		Convert a tile (Tile object) to a masked tile (MaskedTile object).

		:tile: The tile (Tile object).
		:return: The masked tile (MaskedTile object).
		"""

		if tile == Tile.EMPTY:
			return tile
		
		return MaskedTile(tile.value)

class MaskedGrid(Grid):
	"""
	Grid with walls and mask (including the visibilities).
	"""

	def __init__(self, num_rows, num_columns, bomb_position_list, left_wall=0, right_wall=0,
			top_wall=0, bottom_wall=0):
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

		get_mask_at = lambda pos: True if (self.tile_at(pos[0], pos[1]) != Tile.WALL) else False
		# '_masked_grid' is the mask of the grid: True if the tile at position (i, j) is masked, False othewise.
		# By default, all tiles is masked except the walls.
		self._masked_grid = [[get_mask_at((i, j)) for j in range(self.num_columns)] for i in range(self.num_rows)]

		self._num_masked_tiles = self.num_tiles
	
	@property
	def num_masked_tiles(self):
		"""
		Number of masked tiles.
		"""

		return self._num_masked_tiles

	@property
	def grid(self):
		"""
		Grid with mask (what the user see).
		"""

		grid = [[MaskedTile.MASKED for j in range(self.num_columns)] for i in range(self.num_rows)]
		for i, row in enumerate(self._masked_grid):
			for j, masked in enumerate(row):
				if not masked:
					grid[i][j] = MaskedTile.convert_tile_to_masked_tile(self.tile_at(i, j))

		return grid
	
	def __str__(self):
		str_grid = []

		str_grid.append("-\t \t")
		for i in range(self._num_columns):
			str_grid.append(str(i))
			str_grid.append('\t')
		str_grid.append("\n\n")

		for i, row in enumerate(self.grid):
			str_grid.append(str(i))
			str_grid.append("\t \t")

			for tile in row:
				str_grid.append(str(tile))
				str_grid.append('\t')
			str_grid.append('\n')

		return ''.join(str_grid)

	def is_tile_masked(self, i, j):
		"""
		Test if a tile is masked or not masked.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile is masked, False otherwise.
		"""

		return self._masked_grid[i][j]

	def unmask_tiles(self, i, j):
		"""
		Unmask on a tile and all the empty tiles around.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: The tile at position 'i' and 'j'.
		"""

		tile = self.tile_at(i, j)

		already_unmasked = self._unmask_tile(i, j)
		if already_unmasked:
			raise ValueError("Error: the tile (at {}, {}) is already unmasked or is a wall!".format(i, j))

		if (tile != Tile.EMPTY) or (tile > 0):
			return tile

		# Explore and unmask the empty tiles around 'tile'.
		tiles_to_explore = set()
		tiles_to_explore.update(self.adjacent_tiles(i, j))
		while tiles_to_explore: # While 'tiles_to_explore' contains positions.
			i_temp, j_temp = tiles_to_explore.pop()
			tile_temp = self.tile_at(i_temp, j_temp) # 'tile_temp' is a empty tile.

			already_unmasked = self._unmask_tile(i_temp, j_temp)
			if not(already_unmasked) and (tile_temp == 0):
				tiles_to_explore.update(self.adjacent_tiles(i_temp, j_temp))

		return tile

	def unmask_all_tiles(self):
		"""
		Unmask all tiles. The 'num_masked_tiles' counter is equal to 0 after calling this function.
		"""

		for i in range(self.num_rows):
			for j in range(self.num_columns):
				self._unmask_tile(i, j)

	def _unmask_tile(self, i, j):
		"""
		Unmask one tile at position 'i' and 'j'. It reveal the tile in this position and decrements by one the varaible 'num_masked_tiles'.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: True if the tile has already been unmasked, False otherwise.
		"""

		if self._masked_grid[i][j]:
			self._masked_grid[i][j] = False
			self._num_masked_tiles -= 1

			return False

		return True

if __name__ == "__main__":
	bomb_position_list = [(0, 1), (5, 4), (4, 2), (9, 4), (2, 1), (4, 4), (9, 0), (9, 1), (7, 1), (0, 3), (7, 2), (3, 0)]
	g = MaskedGrid(10, 5, bomb_position_list)
	print(g)
	g.unmask_tiles(0, 0)
	print(g)
	g.unmask_tiles(2, 4)
	print(g)
	g.unmask_tiles(5, 3)
	print(g)

	print("\n\n\n")

	bomb_position_list = [(5, 4), (4, 2), (2, 1), (4, 4)]
	g = MaskedGrid(10, 5, bomb_position_list, 1, 0, 2, 3)
	print(g)
	g.unmask_tiles(2, 4)
	print(g)
	g.unmask_tiles(5, 3)
	print(g)
