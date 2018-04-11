from ai.ai import AI
from minesweeper.masked_grid import MaskedTile
from ai.helpers import to_value_list, extract_subgrid

from abc import ABCMeta, abstractmethod

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
