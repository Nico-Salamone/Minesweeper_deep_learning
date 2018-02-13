from masked_grid import MaskedTile, MaskedGrid

import random

SEED = None

class Minesweeper(MaskedGrid):
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

		pos_list = [(i, j) for i in range(num_rows) for j in range(num_columns)]
		bomb_position_list = random.sample(pos_list, num_bombs)

		super().__init__(num_rows, num_columns, bomb_position_list)

if __name__ == "__main__":
	random.seed(SEED)
	ms = Minesweeper(10, 5, 6)

	print(ms)

	pos = input("Enter a position: ")
	pos = tuple([int(i) for i in pos.split(' ')])
	tile = ms.unmask_tiles(pos[0], pos[1])
	print(ms, "\n\n")
	while (tile == MaskedTile.EMPTY) and ((ms.num_masked_tiles - ms.num_bombs) > 0):
		pos = input("Enter a position: ")
		pos = tuple([int(i) for i in pos.split(' ')])
		tile = ms.unmask_tiles(pos[0], pos[1])
		print(ms, "\n\n")

	if tile == MaskedTile.BOMB:
		print("You lost!")
	else:
		print("You won!")

	ms.unmask_all_tiles()
	print(ms)
