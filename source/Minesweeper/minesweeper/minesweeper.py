from minesweeper.masked_grid import MaskedTile, MaskedGrid
from minesweeper.grid_generation import generate_grid

from enum import Enum

class State(Enum):
	WIN = 1
	LOSS = 2
	CONTINUE = 0 # Unfinished game.

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

		self._grid = generate_grid(num_rows, num_columns, num_bombs)

		self._state = State.CONTINUE
		self._score = 0

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

		return self._grid.num_columns

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

	@property
	def state(self):
		"""
		State of the game.
		"""

		return self._state

	@property
	def score(self):
		"""
		Score of the game.
		"""

		return self._score

	@property
	def highest_possible_score(self):
		"""
		Highest possible score for this game.
		"""

		return (self.num_rows * self.num_columns) - self.num_bombs

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

	def tile_at(self, i, j):
		"""
		Get tile at a position. The returned value is either MaskedTile.MASKED, MaskedTile.BOMB or the number of adjacent bombs.
		In this last case, the tile is a MaskedTile.EMPTY.

		:i: The index of the row of the position.
		:j: The index of the column of the position.
		:return: MaskedTile.MASKED if the tile is masked, MaskedTile.BOMB if the tile contains a bomb, the number of adjacent bombs otherwise.
		"""	

		return self._grid.tile_at(i, j)

	def play_tile(self, i, j):
		"""
		Play on a tile and update the state and the score. It does not do anything if the game is lost.

		:i: The index of the row of the tile.
		:j: The index of the column of the tile.
		:return: A set of the position of played tiles.
		"""

		if self._state == State.LOSS:
			return (self.state, self.score)

		old_num_masked_tiles = self.num_masked_tiles

		played_tiles = self._grid.unmask_tile(i, j)

		# Updating of the score.
		new_num_masked_tiles = self.num_masked_tiles
		self._score += (old_num_masked_tiles - new_num_masked_tiles)

		# Updating of the state.
		if self.tile_at(i, j) == MaskedTile.BOMB:
			self._state = State.LOSS
		elif (self.num_masked_tiles - self.num_bombs) == 0:
			self._state = State.WIN

		return played_tiles

	def reveal_all_tiles(self):
		"""
		Reveal all tiles. The 'num_masked_tiles' counter is equal to 0 and the state is set to State.LOSS after calling this function.
		"""

		self._grid.unmask_all_tiles()
		self._state = State.LOSS
