import math
from enum import Enum

SIZE = 9

class Player(Enum):
	X = 1
	O = -1

	def __str__(self):
		if self == Player.X:
			return 'x'
		elif self == Player.O:
			return 'o'

		return None

	@classmethod
	def get_other_player(cls, player):
		if player == Player.X:
			return Player.O
		elif player == Player.O:
			return Player.X

		return None

	@classmethod
	def get_player_who_starts_game(cls):
		# X is player who starts the game.
		return Player.X

class Tile(Enum):
	X = 1
	O = -1
	EMPTY = 0

	def __str__(self):
		if self == Tile.X:
			return 'x'
		elif self == Tile.O:
			return 'o'
		elif self == Tile.EMPTY:
			return '-'

		return None

	@classmethod
	def get_player_from_tile(cls, tile):
		if tile == Tile.X:
			return Player.X
		elif tile == Tile.O:
			return Player.O

		return None

class State(Enum):
	# The state is determined according to X's point of view.
	WIN = Player.X
	LOSE = Player.O
	DRAW = 0
	CONTINUE = 2

	@classmethod
	def get_state_from_winner(cls, winner):
		if winner == Player.X:
			return State.WIN
		elif winner == Player.O:
			return State.LOSE

		return None

def initialize_empty_grid():
	return (Tile.EMPTY, ) * SIZE

def to_string(grid):
	row_column_size = math.sqrt(SIZE)

	grid_str = ""
	for i in range(SIZE):
		end = ""
		if ((i % row_column_size) == (row_column_size - 1)) and (i != SIZE - 1): # End row and not last square.
			end = "\n"

		grid_str += grid[i].__str__() + end

	return grid_str

def print_grid(grid):
	print(to_string(grid))

def get_player_who_must_play_now(grid):
	num_x = grid.count(Tile.X)
	num_o = grid.count(Tile.O)

	first_player_starts = Player.get_player_who_starts_game()

	if num_x == num_o:
		if first_player_starts == Player.X:
			return Player.X
		else:
			return Player.O

	if first_player_starts == Player.X:
		return Player.O

	return Player.X

def get_empty_tile_indexes(grid):
	empty_tile_indexes = []
	for i in range(len(grid)):
		if grid[i] == Tile.EMPTY:
			empty_tile_indexes.append(i)

	return empty_tile_indexes

def play_turn(grid, player, tile_index):
	grid_list = list(grid)

	tile = Tile.X
	if player == Player.O:
		tile = Tile.O

	grid_list[tile_index] = tile

	return tuple(grid_list)

def get_grid_state(grid):
	state = State.CONTINUE
	row_column_size =round(math.sqrt(SIZE))

	# Rows
	for row_index in range(row_column_size):
		i = row_index * row_column_size

		possible_winner = grid[i]
		if possible_winner != Tile.EMPTY:
			for k in range(1, row_column_size):
				j = i + k
				if grid[j] == possible_winner:
					if j == (i + row_column_size - 1): # Last tile of this row (row_index).
						return State.get_state_from_winner(Tile.get_player_from_tile(possible_winner))
				else:
					break

	# Columns
	for column_index in range(row_column_size):
		j = column_index

		possible_winner = grid[j]
		if possible_winner != Tile.EMPTY:
			for k in range(1, row_column_size):
				i = j + (k * row_column_size)
				if grid[i] == possible_winner:
					if i == (j + (row_column_size * (row_column_size - 1))): # Last tile of this column (column_index).
						return State.get_state_from_winner(Tile.get_player_from_tile(possible_winner))
				else:
					break

	# Diagonal
	possible_winner = grid[0]
	if possible_winner != Tile.EMPTY:
		for i in range(1, row_column_size):
			j = i * (row_column_size + 1)

			if grid[j] == possible_winner:
				if j == (SIZE - 1):
					return State.get_state_from_winner(Tile.get_player_from_tile(possible_winner))
			else:
				break

	# Anti-diagonal
	possible_winner = grid[(row_column_size - 1)]
	if possible_winner != Tile.EMPTY:
		for i in range(1, row_column_size):
			j = (row_column_size - 1) + (i * (row_column_size - 1))

			if grid[j] == possible_winner:
				if j == (SIZE - row_column_size):
					return State.get_state_from_winner(Tile.get_player_from_tile(possible_winner))
			else:
				break

	for i in range(SIZE):
		if grid[i] == Tile.EMPTY:
			return State.CONTINUE

	return State.DRAW

if __name__ == "__main__":
	grid = initialize_empty_grid()

	grid = play_turn(grid, Player.X, 0)
	grid = play_turn(grid, Player.O, 2)
	grid = play_turn(grid, Player.X, 1)
	grid = play_turn(grid, Player.O, 4)
	grid = play_turn(grid, Player.X, 8)

	print_grid(grid)
