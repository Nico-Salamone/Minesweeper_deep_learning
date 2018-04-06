from minesweeper.minesweeper import State

import numpy as np
import random

class RandomAI():
	"""
	Random artificial intelligence.
	"""

	def __init__(self, minesweeper=None):
		"""
		Create an random artificial intelligence.

		:minesweeper: A minesweeper game.
		"""

		self.minesweeper = minesweeper

	def play_turn(self):
		"""
		Play a turn (it is random).

		:return: The played position and the list of tiles that have been unmasked during this turn if the game is not
			finished. If so, then return State.FINISHED. If there is no minesweeper, then return None.
		"""

		if not self.minesweeper:
			return None

		if self.minesweeper.state == State.FINISHED:
			return State.FINISHED

		played_pos = random.choice(self.minesweeper.masked_tile_positions)
		unmasked_tiles = self.minesweeper.play_tile(played_pos[0], played_pos[1])

		return played_pos, unmasked_tiles

if __name__ == "__main__":
	from minesweeper.minesweeper import Minesweeper

	random.seed(40)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10

	ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)
	ai = RandomAI(minesweeper=ms)

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
