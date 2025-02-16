from ai.ai_nn import AINN
from minesweeper.minesweeper import State

import numpy as np

class AIWithoutFlags(AINN):
	"""
	Artificial intelligence using a neural network and not using flags.
	"""

	def __init__(self, model, minesweeper=None, subgrid_radius=2):
		"""
		Create an artificial intelligence using a neural network and not using flags.

		:model: A model.
		:minesweeper: A minesweeper game.
		:subgrid_radius: The radius of subgrids with whom the neural network has trained.
		"""

		super().__init__(model, minesweeper=minesweeper, subgrid_radius=subgrid_radius)

	def play_turn(self):
		"""
		Play a turn. The first turn is random.

		:return: The played position and the list of tiles that have been unmasked during this turn if the game is not
			finished. If so, then return State.FINISHED. If there is no minesweeper, then return None.
		"""

		if not self.minesweeper:
			return None

		if self.minesweeper.state == State.FINISHED:
			return State.FINISHED

		if self.minesweeper.num_masked_tiles == (self.minesweeper.num_rows * self.minesweeper.num_columns):
			# If this is the fist turn.
			return self._play_random_turn()

		pos_list, subgrids = self._compute_subgrids()

		y_pred_list = self._evaluate_subgrids(subgrids)
		played_pos = pos_list[np.argmin(y_pred_list)]

		unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])

		return played_pos, unmasked_tiles

if __name__ == "__main__":
	from minesweeper.minesweeper import Minesweeper
	from ai.helpers import model_file_path

	from keras.models import load_model
	import random

	random.seed(40)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	subgrid_radius = 2

	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius)
	model = load_model(model_file_name)

	ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)
	ai = AIWithoutFlags(model, minesweeper=ms, subgrid_radius=subgrid_radius)

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
