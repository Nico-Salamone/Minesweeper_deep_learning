from minesweeper.masked_grid import MaskedTile
from minesweeper.minesweeper import Minesweeper, State
from ai.random_ai import RandomAI
from ai.ai_without_flags import AIWithoutFlags
from ai.ai_with_flags import AIWithFlags
from ai.ai_with_flags2 import AIWithFlags2
from ai.helpers import model_file_path

from enum import Enum
from keras.models import load_model
import random

SEED = None
NUM_ROWS_GRID = 10
NUM_COLUMNS_GRID = 10
NUM_BOMBS_GRID = 10
SUBGRID_RADIUS = 2

AI_WITH_FLAGS_PLAYFUL_LEVEL = 1.15
AI_WITH_FLAGS_FLAG_THREASHOLD = 0.96

class Mode(Enum):
	PLAYER = 1
	RANDOM_AI = 2
	AI_WITHOUT_FLAGS = 3
	AI_WITH_FLAGS = 4
	AI_WITH_FLAGS2 = 5

	@classmethod
	def is_player_mode(cls, mode):
		"""
		Allow to know if a mode is a player mode or not.

		:mode: The mode.
		:return: True if the mode is a player mode, False otherwise.
		"""

		if (mode == Mode.PLAYER):
			return True

		return False

	@classmethod
	def is_ai_mode(cls, mode):
		"""
		Allow to know if a mode is an artificial intelligence mode or not.

		:mode: The mode.
		:return: True if the mode is an artificial intelligence mode, False otherwise.
		"""

		if (mode == Mode.RANDOM_AI) or (mode == Mode.AI_WITHOUT_FLAGS) or (mode == Mode.AI_WITH_FLAGS) or \
			(mode == Mode.AI_WITH_FLAGS2):

			return True

		return False

def print_welcome():
	"""
	Print the welcome message.
	"""

	print("Welcome to the minesweeper game!")
	print("This game is composed of five modes:\n- 1. Player: it's the classic mode of the minesweeper with a human" \
		" as player.\n- 2. Random artificial intelligence: a random AI plays the game.\n- 3. Artificial intelligence" \
		" without flags: an AI plays the game and uses no flags.\n- 4. Artificial intelligence with flags: an AI" \
		" plays the game and uses flags.\n- 5. Artificial intelligence with flags 2: a variant of the \"Artificial" \
		" intelligence with flags\" mode.")

def select_mode():
	"""
	Ask the user to choose a mode.

	:return: An artificial intelligence.
	"""

	mode_values = [mode.value for mode in Mode]
	mode_values_str_list = []
	for mode_value in mode_values:
		mode_values_str_list.extend(["\"", str(mode_value), "\"", ", "])
	mode_values_str = ''.join(mode_values_str_list[:-1])

	bad_input = True
	while bad_input:
		mode_value = input("Select a mode: ")
		try:
			mode = Mode(int(mode_value[0]))
			bad_input = False
		except:
			print("WARNING: bad format. Accepted format: " + mode_values_str + ".\n")

	return mode

def create_ai(mode, minesweeper):
	"""
	Create an artificial intelligence from a mode and a minesweeper game.

	:mode: The mode.
	:minesweeper: The minesweeper game.
	:return: The artificial intelligence (or none if the mode is not an artificial intelligence mode).
	"""

	if not Mode.is_ai_mode(mode):
		return None

	if mode == Mode.RANDOM_AI:
		ai = RandomAI(minesweeper=minesweeper)
	elif mode == Mode.AI_WITHOUT_FLAGS:
		model_file_name = model_file_path(NUM_ROWS_GRID, NUM_COLUMNS_GRID, NUM_BOMBS_GRID, SUBGRID_RADIUS,
			with_flags=False)
		model = load_model(model_file_name)
		ai = AIWithoutFlags(model, minesweeper=minesweeper, subgrid_radius=SUBGRID_RADIUS)
	elif mode == Mode.AI_WITH_FLAGS:
		model_file_name = model_file_path(NUM_ROWS_GRID, NUM_COLUMNS_GRID, NUM_BOMBS_GRID, SUBGRID_RADIUS,
			with_flags=True)
		model = load_model(model_file_name)
		ai = AIWithFlags(model, minesweeper=minesweeper, subgrid_radius=SUBGRID_RADIUS,
			playful_level=AI_WITH_FLAGS_PLAYFUL_LEVEL, flag_threshold=AI_WITH_FLAGS_FLAG_THREASHOLD)
	elif mode == Mode.AI_WITH_FLAGS2:
		model_file_name = model_file_path(NUM_ROWS_GRID, NUM_COLUMNS_GRID, NUM_BOMBS_GRID, SUBGRID_RADIUS,
			with_flags=True)
		model = load_model(model_file_name)
		ai = AIWithFlags2(model, minesweeper=minesweeper, subgrid_radius=SUBGRID_RADIUS)

	return ai

def get_pos_user(minesweeper):
	"""
	Get the position inputs by the user.

	:minesweeper: The minesweeper game.
	:return: The position (a tuple of two integers).
	"""

	pos = None
	while not pos:
		str_pos = input("Enter a position: ")
		pos = _parse_pos_user(str_pos)

		if not pos:
			print("WARNING: bad format. Accepted format: \"i j\", \"i,j\", \"i, j\" and \"i ,j\".\n")
		elif minesweeper.tile_at(pos[0], pos[1]) != MaskedTile.MASKED:
			print("WARNING: you have to player on a masked tile!\n")
			pos = None

	return pos

def _parse_pos_user(str_input):
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
			pos = tuple([int(j) for j in str_input.split(separators[i])])
		except:
			i += 1

	if not(pos) or (len(pos) != 2):
		return None

	return pos

if __name__ == "__main__":
	random.seed(SEED)

	print_welcome()
	print("\n\n")
	mode = select_mode()
	print('')

	ms = Minesweeper(NUM_ROWS_GRID, NUM_COLUMNS_GRID, NUM_BOMBS_GRID)
	ai = create_ai(mode, ms)

	print(ms, "\n\n")
	while ms.state == State.CONTINUE:
		if not ai: # If the "Player" mode is selected.
			pos = get_pos_user(ms)
			ms.play_tile(pos[0], pos[1])
		else: # If an "AI" mode is selected.
			input("Press Enter to play the next turn.")

			played_pos, _ = ai.play_turn()

			insert_flag_str = ""
			if ms.tile_at(played_pos[0], played_pos[1]) == MaskedTile.FLAG:
				insert_flag_str = " (insert a flag)"
			print("Played position by the AI: {}{}.".format(played_pos, insert_flag_str))

		print(ms, "\n\n")

	if ms.state == State.LOSS:
		print("Lost!")
	else:
		print("Won!")

	print("Score: {}.".format(ms.score))

	ms.reveal_all_tiles()
	print(ms)
