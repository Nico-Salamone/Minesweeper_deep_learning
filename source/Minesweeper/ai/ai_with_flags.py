from ai.ai_nn import AINN
from minesweeper.minesweeper import State

import numpy as np

class AIWithFlags(AINN):
	"""
	Artificial intelligence using a neural network and using flags.
	"""

	def __init__(self, model, minesweeper=None, subgrid_radius=2, playful_level=1, flag_threshold=0.9):
		"""
		Create an artificial intelligence using a neural network and using flags.

		:model: A model (trained with flags).
		:minesweeper: A minesweeper game.
		:subgrid_radius: The radius of subgrids with whom the neural network has trained.
		:playful_level: The playful level. The higher this value is and the more artificial intelligence will prefer to
			play on a masked tile rather than insert a flag. Conversely, the lower this value is, the less artificial
			intelligence will prefer to play on a tile rather than insert a flag (flags will be used more often). The
			neural value is 1 (the artificial intelligence has no preference between playing on a tile and inserting a
			flag). The minimum value for this parameter is 0 (the artificial intelligence will always insert flags) and
			the maximum value is 2 (no flags will be used).
		:flag_threshold: The minimal threshold to insert a flag. For each tile, the artificial intelligence compute a
			particular value which is interpreted as the probability that this tile contains a bomb. If this value is
			less than 'flag_threshold', then the artificial intelligence will not insert a flag on this tile. The
			minimum value for this parameter is 0 (the artificial intelligence will always insert flags) and the
			maximum value is 1 (no flags will be used).
		"""

		super().__init__(model, minesweeper=minesweeper, subgrid_radius=subgrid_radius)
		self.playful_level = playful_level
		self.flag_threshold = flag_threshold

	def play_turn(self):
		"""
		Play a turn. The first turn is random.

		:return: The played position and the list of tiles that have been unmasked during this turn if the game is not
			finished. If so, then return State.FINISHED. If there is no minesweeper, then return None. The artificial
			intelligence may insert a flag on the tile at the played position.
		"""

		if not self.minesweeper:
			return None

		if self.minesweeper.state == State.FINISHED:
			return State.FINISHED

		if self.minesweeper.num_masked_tiles == (self.minesweeper.num_rows * self.minesweeper.num_columns):
			# If this is the fist turn.
			return self._play_random_turn()

		only_flags = False
		if self.minesweeper.num_masked_tiles == self.minesweeper.num_flag_tiles:
			# All masked tiles contain a flag.
			flag_tile_pos = self.minesweeper.flag_tile_positions
			self.minesweeper.remove_all_flags()

			only_flags = True

		pos_list, subgrids = self._compute_subgrids()

		y_pred_list = self._evaluate_subgrids(subgrids)
		
		i_min = np.argmin(y_pred_list)
		i_max = np.argmax(y_pred_list)
		if only_flags or (y_pred_list[i_min] < (self.playful_level - y_pred_list[i_max])) or \
			(y_pred_list[i_max] <= self.flag_threshold):
			# If all masked tiles contain a flag, or
			# 'min(y_pred_list)' is less than 'self.playful_level' minus 'max(y_pred_list)' (the artificial
			# intelligence prefers to play on a masked tile), or
			# 'max(y_pred_list)' is less than 'self.flag_threshold', then
			# play on a masked tile.

			played_pos = pos_list[i_min]
			unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])
		else:
			# If 'min(y_pred_list)' is greater than 'self.playful_level' minus 'max(y_pred_list)' (the artificial
			# intelligence prefers to insert a flag), and
			# 'max(y_pred_list)' is greater than 'self.flag_threshold', then
			# insert a flag.

			played_pos = pos_list[i_max]
			unmasked_tiles = []
			self.minesweeper.insert_flag(played_pos[0], played_pos[1])

		if only_flags:
			self.minesweeper.insert_flags(flag_tile_pos)
			# It returns False because some flags were not inserted (these are the unmasked tiles in 'unmasked_tiles').

		return played_pos, unmasked_tiles

if __name__ == "__main__":
	from minesweeper.minesweeper import Minesweeper
	from minesweeper.masked_grid import MaskedTile
	from ai.helpers import model_file_path

	from keras.models import load_model
	import random

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

		insert_flag_str = ""
		if ms.tile_at(played_pos[0], played_pos[1]) == MaskedTile.FLAG:
			insert_flag_str = " (insert a flag)"
		print("Played position: {}{}.".format(played_pos, insert_flag_str))
		print(ms, "\n\n")

	if ms.state == State.LOSS:
		print("Lost!")
	else:
		print("Won!")

	print("Score: {}.".format(ms.score))

	ms.reveal_all_tiles()
	print(ms)
