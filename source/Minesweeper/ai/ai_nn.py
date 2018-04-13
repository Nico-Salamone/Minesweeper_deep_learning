from ai.ai import AI
from minesweeper.masked_grid import MaskedTile
from ai.helpers import to_value_list, extract_subgrid

from abc import ABCMeta, abstractmethod
import numpy as np

class AINN(AI, metaclass=ABCMeta):
	"""
	Artificial intelligence using a neural network.
	"""

	def __init__(self, model, minesweeper=None, subgrid_radius=2):
		"""
		Create an artificial intelligence using a neural network.

		:model: A model.
		:minesweeper: A minesweeper game.
		:subgrid_radius: The radius of subgrids with whom the neural network has trained.
		"""

		super().__init__(minesweeper=minesweeper)
		self.model = model
		self.subgrid_radius = subgrid_radius
		self._evaluated_subgrid_cache = {}

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
				if tile == MaskedTile.MASKED:
					subgrids.append(to_value_list(extract_subgrid(grid, i, j, self.subgrid_radius)))
					pos_list.append((i, j))

		return pos_list, subgrids

	def _evaluate_subgrids(self, subgrids):
		"""
		Evaluate subgrids.

		:subgrids: The subgrids.
		:return: The evaluation of each subgrid, that is the predicted values by the neural network for theses subgrids.
		"""

		subgrids = [tuple(subgrid) for subgrid in subgrids] # It makes the subgrids hashable.

		# Add the subgrids that are not in the cache ('self._evaluated_subgrid_cache').
		subgrids_to_evaluate = [
			subgrid for subgrid in set(subgrids)
			if subgrid not in self._evaluated_subgrid_cache
		]

		if subgrids_to_evaluate: # If 'subgrids_to_evaluate' is not empty.
			y_pred_list = self.model.predict(np.array(subgrids_to_evaluate)).flatten()
			self._evaluated_subgrid_cache.update(dict(zip(subgrids_to_evaluate, y_pred_list)))

		# Evaluate the subgrids.
		return [self._evaluated_subgrid_cache[subgrid] for subgrid in subgrids]
