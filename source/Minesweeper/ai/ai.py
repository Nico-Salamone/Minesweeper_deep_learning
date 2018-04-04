from minesweeper.masked_grid import MaskedTile
from ai.helpers import to_value_list, extract_subgrid

import numpy as np

class AI():
	"""
	Artificial intelligence.
	"""

	def __init__(self, model, subgrid_radius=2):
		"""
		Create an artificial intelligence.

		:model: A model.
		:subgrid_radius: The radius of subgrids with whom the neural network has trained.
		"""

		self.model = model
		self.subgrid_radius = subgrid_radius

	def best_tile_pos(self, grid):
		"""
		Get the position of the "best" tile, that is the best position to play from the point of view of artificial
		intelligence.

		:grid: The grid (a list of lists of tile values, that is an two-dimensional grid).
		:return: The position of the "best" tile.
		"""
		
		subgrids = []
		pos_list = []
		for i, row in enumerate(grid):
			for j, tile in enumerate(row):
				if tile == MaskedTile.MASKED:
					subgrids.append(to_value_list(extract_subgrid(grid, i, j, self.subgrid_radius)))
					pos_list.append((i, j))

		y_pred_list = [y_pred[0] for y_pred in self.model.predict(subgrids)]

		i_min = np.argmin(y_pred_list)
		best_pos = pos_list[i_min]

		return best_pos

if __name__ == "__main__":
	from minesweeper.minesweeper import Minesweeper, State
	from ai.helpers import model_file_path

	from keras.models import load_model
	import random

	random.seed(42)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	subgrid_radius = 2

	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius)
	model = load_model(model_file_name)

	ai = AI(model, subgrid_radius)

	ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)
	print(ms)

	while ms.state == State.CONTINUE:
		pos = ai.best_tile_pos(ms.grid)
		print("Position: {}".format(pos))

		ms.play_tile(pos[0], pos[1])
		print(ms, "\n\n")

		input("Press Enter to continue...")

	if ms.state == State.LOSS:
		print("Lost!")
	else:
		print("Won!")

	print("Score: {}.".format(ms.score))

	ms.reveal_all_tiles()
	print(ms)
