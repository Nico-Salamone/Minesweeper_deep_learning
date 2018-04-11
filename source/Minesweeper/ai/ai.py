from abc import ABCMeta, abstractmethod
import random

class AI(metaclass=ABCMeta):
	"""
	Artificial intelligence.
	"""

	def __init__(self, minesweeper=None):
		"""
		Create an artificial intelligence.

		:minesweeper: A minesweeper game.
		"""

		self.minesweeper = minesweeper

	@abstractmethod
	def play_turn(self):
		"""
		Play a turn.

		:return: The played position and the list of tiles that have been unmasked during this turn if the game is not
			finished. If so, then return State.FINISHED. If there is no minesweeper, then return None.
		"""

		raise NotImplementedError("Error: the 'play_trun()' method is not implemented!")

	def _play_random_turn(self):
		"""
		Play a random turn.

		:return: The played position and the list of tiles that have been unmasked during this turn.
		"""

		played_pos = random.choice(self.minesweeper.masked_tile_positions)
		unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])

		return played_pos, unmasked_tiles
