from minesweeper.minesweeper import State
from minesweeper.masked_grid import MaskedTile
from ai.helpers import to_value_list, extract_subgrid

import numpy as np
import random

class AIWithFlags():
	"""
	Artificial intelligence using flags.
	"""

	def __init__(self, model, minesweeper=None, subgrid_radius=2):
		"""
		Create an artificial intelligence using flags.

		:model: A model (trained with flags).
		:minesweeper: A minesweeper game.
		:subgrid_radius: The radius of subgrids with whom the neural network has trained.
		"""

		self.model = model
		self.minesweeper = minesweeper
		self.subgrid_radius = subgrid_radius

	def play_turn(self):
		"""
		Play a turn. The first turn is random.

		:return: The played position and the list of tiles that have been unmasked during this turn if the game is not
			finished. If so, then return State.FINISHED. If there is no minesweeper, then return None. The artificial
			intelligence may insert or remove somes flags during a turn.
		"""

		if not self.minesweeper:
			return None

		if self.minesweeper.state == State.FINISHED:
			return State.FINISHED

		if self.minesweeper.num_masked_tiles == (self.minesweeper.num_rows * self.minesweeper.num_columns):
			# If this is the fist turn.
			return self._play_first_turn()

		self._update_flags()

		only_flags = False
		if self.minesweeper.num_masked_tiles == self.minesweeper.num_flag_tiles:
			# All masked subgrids contain a flag.
			flag_tile_pos = self.minesweeper.flag_tile_positions
			self.minesweeper.remove_all_flags()

			only_flags = True

		pos_list, subgrids = self._compute_subgrids()
		y_pred_list = [y_pred[0] for y_pred in self.model.predict(np.array(subgrids))]

		played_pos = pos_list[np.argmin(y_pred_list)]
		unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])

		if only_flags:
			self.minesweeper.insert_flags(flag_tile_pos)
			# It returns False because some flags were not inserted (these are the unmasked tiles in 'unmasked_tiles').

		return played_pos, unmasked_tiles

	def _play_first_turn(self):
		"""
		Play the first turn (it is random).

		:return: The played position and the list of tiles that have been unmasked during this turn.
		"""

		pos_i = random.randint(0, (self.minesweeper.num_rows - 1))
		pos_j = random.randint(0, (self.minesweeper.num_columns - 1))
		played_pos = (pos_i, pos_j)

		unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])

		return played_pos, unmasked_tiles

	def _update_flags(self):
		"""
		Update the flags.
		"""

		flag_tile_pos = set(self.minesweeper.flag_tile_positions)
		self.minesweeper.remove_all_flags()

		pos_list, subgrids = self._compute_subgrids()
		y_pred_list = [y_pred[0] for y_pred in self.model.predict(np.array(subgrids))]

		for (i, j), y_pred in zip(pos_list, y_pred_list):
			if y_pred > 0.9:
				# Insert a flag at position 'i' and 'j'.
				flag_tile_pos.add((i, j))
			else:
				# Remove the flag at position 'i' and 'j' if there is one.
				try:
					flag_tile_pos.remove((i, j))
				except KeyError:
					pass

		self.minesweeper.insert_flags(flag_tile_pos)
		# It returns False because some flags were not inserted (these are the unmasked tiles in 'unmasked_tiles').

	def _compute_subgrids(self):
		"""
		Compute the subgrids where the tile in the middle is a masked tile.

		:return: The positions of the tile in the middle and the corresponding subgrids.
		"""

		grid = self.minesweeper.grid

		subgrids = []
		pos_list = []
		for i, row in enumerate(grid):
			for j, tile in enumerate(row):
				if tile == MaskedTile.MASKED: # If 'tile' contains a flag, do nothing.
					subgrids.append(to_value_list(extract_subgrid(grid, i, j, self.subgrid_radius)))
					pos_list.append((i, j))

		return pos_list, subgrids

if __name__ == "__main__":
	from minesweeper.minesweeper import Minesweeper
	from ai.helpers import model_file_path

	from keras.models import load_model

	random.seed(40)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	subgrid_radius = 2
	with_flags = True

	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius,
		with_flags=with_flags)
	model = load_model(model_file_name)

	ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)
	ai = AIWithFlags(model, minesweeper=ms, subgrid_radius=subgrid_radius)

	print(ms, "\n\n")
	while ms.state == State.CONTINUE:
		input("Press Enter to play the next turn.")
		
		played_pos, _ = ai.play_turn()

		print("Played position: {}.".format(played_pos))
		print(ms, "\n\n")

	if ms.state == State.LOSS:
		print("Lost!")
	else:
		print("Won!")

	print("Score: {}.".format(ms.score))

	ms.reveal_all_tiles()
	print(ms)
