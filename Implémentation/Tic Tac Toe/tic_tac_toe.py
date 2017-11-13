import random
from enum import Enum

SIZE = 3

class Player(Enum):
	X_PLAYER = (1, 'x')
	EMPTY_SQUARE = (0, '-')
	O_PLAYER = (-1, 'o')
	NONE_PLAYER = (2, '.') # If draw

	def __init__(self, player_id, player_symbol):
		self.id = player_id
		self.symbol = player_symbol

	@classmethod
	def get_player_from_symbol(cls, player_symbol):
		for player in cls.__members__.values():
			if player.symbol == player_symbol:
				return player

		return None

	@classmethod
	def get_id_from_symbol(cls, player_symbol):
		player = Player.get_player_from_symbol(player_symbol)

		if player:
			return player.id
		else:
			return None

	@classmethod
	def get_player_from_id(cls, player_id):
		for player in cls.__members__.values():
			if player.id == player_id:
				return player

		return None

	@classmethod
	def get_symbol_from_id(cls, player_id):
		player = Player.get_player_from_id(player_id)

		if player:
			return player.symbol
		else:
			return None

	@classmethod
	def alternate_players(cls, player):
		if player == Player.X_PLAYER:
			return Player.O_PLAYER
		elif player == Player.O_PLAYER:
			return Player.X_PLAYER

		return None

	@classmethod
	def alternate_players_id(cls, player_id):
		player = Player.alternate_players(Player.get_player_from_id(player_id))

		if player:
			return player.id
		else:
			return None

	@classmethod
	def alternate_players_symbol(cls, player_symbol):
		player = Player.alternate_players(Player.get_player_from_symbol(player_symbol))

		if player:
			return player.symbol
		else:
			return None

def print_board(board):
	for i in range(len(board)):
		for j in range(len(board)):
			print(Player.get_symbol_from_id(board[i][j]), end = "")
		print("")

def convert_board_to_string(board):
	return ' '.join(str(square) for row in board for square in row)

def convert_string_to_board(string):
	array = string.split(' ')

	if len(array) != (SIZE * SIZE):
		return None

	board = initiate_empty_board()
	for i in range((SIZE * SIZE)):
		pos = get_position_from_num_square(i)
		board[pos[0]][pos[1]] = int(array[i])

	return board

def initiate_empty_board():
	return [[Player.EMPTY_SQUARE.id for i in range(SIZE)] for i in range(SIZE)]

def get_position_from_num_square(num_square):
	return (num_square // SIZE, num_square % SIZE)

def play_random_ai(player, board, empty_squares):
	if not empty_squares:
		return False

	num_square = random.randint(0, len(empty_squares) - 1)
	pos = get_position_from_num_square(empty_squares.pop(num_square))
	board[pos[0]][pos[1]] = player.id

	return True

def check_end_game(board):
	winning_player = set() 

	# Columns
	for j in range(SIZE):
		player = board[0][j]
		if player != Player.EMPTY_SQUARE.id:
			i = 1
			while (i < SIZE) and (board[i][j] == player):
				i += 1
			if i == SIZE:
				winning_player.add(Player.get_player_from_id(player))

	# Rows
	for i in range(SIZE):
		player = board[i][0]
		if player != Player.EMPTY_SQUARE.id:
			j = 1
			while (j < SIZE) and (board[i][j] == player):
				j += 1
			if j == SIZE:
				winning_player.add(Player.get_player_from_id(player))

	# Diagonals
	player = board[0][0]
	if player != Player.EMPTY_SQUARE.id:
		i = 1
		j = 1
		while (i < SIZE) and (j < SIZE) and (board[i][j] == player):
			i += 1
			j += 1
		if (i == SIZE) and (j == SIZE):
			winning_player.add(Player.get_player_from_id(player))

	# Anti-diagonals
	player = board[SIZE - 1][0]
	if player != Player.EMPTY_SQUARE.id:
		i = SIZE - 2
		j = 1
		while (i >= 0) and (j < SIZE) and (board[i][j] == player):
			i -= 1
			j += 1
		if (i == -1) and (j == SIZE):
			winning_player.add(Player.get_player_from_id(player))

	if len(winning_player) > 0:
		return winning_player

	for i in range(SIZE):
		for j in range(SIZE):
			if board[i][j] == Player.EMPTY_SQUARE.id:
				return None

	winning_player.add(Player.NONE_PLAYER)

	return winning_player

if __name__ == "__main__":
	board = initiate_empty_board()

	board[0][2] = Player.X_PLAYER.id
	board[1][0] = Player.O_PLAYER.id
	board[1][1] = Player.O_PLAYER.id
	board[1][2] = Player.O_PLAYER.id
	board[2][1] = Player.X_PLAYER.id
	board[2][2] = Player.X_PLAYER.id

	print_board(board)
	print(check_end_game(board))

	"""
	board = initiate_empty_board()
	empty_squares = [i for i in range((SIZE * SIZE))]

	current_player = Player.X_PLAYER
	continue_game = True
	print_board(board)
	while continue_game:
		input("")
		play_random_ai(current_player, board, empty_squares)
		current_player = Player.alternate_players(current_player)
		print_board(board)
		if check_end_game(board):
			continue_game = False
	"""
