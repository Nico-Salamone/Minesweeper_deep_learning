from minesweeper.masked_grid import MaskedTile
from minesweeper.minesweeper import Minesweeper, State

import random

SEED = None

def parse_input(str_input):
	"""
	Parse an input and get a position.
	Accepted format:
	- "i j";
	- "i,j";
	- "i, j";
	- "i ,j".

	:str_input: The input (a string).
	:return: A position or None if the input is in the wrong format.
	"""

	separators = [' ', ',']
	pos = None
	n = len(separators)
	i = 0
	while not(pos) and (i < n):
		try:
			pos = tuple([int(i) for i in str_input.split(separators[i])])
		except Exception:
			i += 1

	return pos

if __name__ == "__main__":
	random.seed(SEED)

	ms = Minesweeper(10, 5, 6)
	print(ms)

	while ms.state == State.CONTINUE:
		pos = None
		while not pos:
			str_pos = input("Enter a position: ")
			pos = parse_input(str_pos)

			if not pos:
				print("WARNING: bad format. Accepted format: \"i j\", \"i,j\", \"i, j\" and \"i ,j\".")
			elif ms.tile_at(pos[0], pos[1]) != MaskedTile.MASKED:
				print("WARNING: you have already played on this tile!")
				pos = None

		ms.play_tile(pos[0], pos[1])
		print(ms, "\n\n")

	if ms.state == State.LOSS:
		print("You lost!")
	else:
		print("You won!")

	print("Your score: {}.".format(ms.score))

	ms.reveal_all_tiles()
	print(ms)
