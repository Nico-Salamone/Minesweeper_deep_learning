import random
import copy
import pickle
import os

X_PLAYER = "x"
O_PLAYER = "o"
NONE_PLAYER = "." # If draw
EMPTY_SQUARE = "-"

SIZE = 3

def alternate_players(player):
	if player == X_PLAYER:
		return O_PLAYER
	if player == O_PLAYER:
		return X_PLAYER

	return None

def print_board(board):
	for i in range(len(board)):
		for j in range(len(board)):
			print(board[i][j], end = "")
		print("")

def initiate_empty_board():
	return [[EMPTY_SQUARE for i in range(SIZE)] for i in range(SIZE)]

def get_position_from_num_square(num_square):
	return (num_square // SIZE, num_square % SIZE)

def convert_board_to_string(board):
	return "".join(str(square) for row in board for square in row)

def convert_string_to_board(string):
	if len(string) != (SIZE * SIZE):
		return None

	board = initiate_empty_board()
	for i in range((SIZE * SIZE)):
		pos = get_position_from_num_square(i)
		board[pos[0]][pos[1]] = string[i]

	return board

def play_random_ai(player, board, empty_squares):
	if not empty_squares:
		return False

	num_square = random.randint(0, len(empty_squares) - 1)
	pos = get_position_from_num_square(empty_squares.pop(num_square))
	board[pos[0]][pos[1]] = player

	return True

def check_end_party(board):
	# Columns
	for j in range(SIZE):
		player = board[0][j]
		if player != EMPTY_SQUARE:
			i = 1
			while (i < SIZE) and (board[i][j] == player):
				i += 1
			if i == SIZE:
				return player

	# Rows
	for i in range(SIZE):
		player = board[i][0]
		if player != EMPTY_SQUARE:
			j = 1
			while (j < SIZE) and (board[i][j] == player):
				j += 1
			if j == SIZE:
				return player

	# Diagonals
	player = board[0][0]
	if player != EMPTY_SQUARE:
		i = 1
		j = 1
		while (i < SIZE) and (j < SIZE) and (board[i][j] == player):
			i += 1
			j += 1
		if (i == SIZE) and (j == SIZE):
			return player

	# Anti-diagonals
	player = board[SIZE - 1][0]
	if player != EMPTY_SQUARE:
		i = SIZE - 2
		j = 1
		while (i >= 0) and (j < SIZE) and (board[i][j] == player):
			i -= 1
			j += 1
		if (i == -1) and (j == SIZE):
			return player

	for i in range(SIZE):
		for j in range(SIZE):
			if board[i][j] == EMPTY_SQUARE:
				return False

	return NONE_PLAYER

def generate_all_boards(player = X_PLAYER, first_player_played = X_PLAYER):
	# Score determinated by player
	# score = [w, l, d], where 'w' is the number of victories, 'l' is the number of defeats and 'd' is the numbers of draws of 'player'
	game_score = {}

	board = initiate_empty_board()
	empty_squares = [i for i in range((SIZE * SIZE))]

	generate_all_boards_rec(player, game_score, board, empty_squares, first_player_played)

	return game_score

def generate_all_boards_rec(player, game_score, board, empty_squares, current_player):
	score = [0] * 3

	winning_player = check_end_party(board)
	if(not winning_player):
		for i in range(len(empty_squares)):
			board_temp = copy.deepcopy(board)
			empty_squares_temp = copy.copy(empty_squares)

			pos = get_position_from_num_square(empty_squares_temp.pop(i))
			board_temp[pos[0]][pos[1]] = current_player

			score_temp = generate_all_boards_rec(player, game_score, board_temp, empty_squares_temp, alternate_players(current_player))
			score = [(score[i] + score_temp[i]) for i in range(len(score))]
	elif(winning_player == NONE_PLAYER): # Draw
		score[2] += 1
	elif(winning_player == player): # Win
		score[0] += 1
	else: # Lose
		score[1] += 1

	game_score[convert_board_to_string(board)] = score

	return score

if __name__ == "__main__":
	game_score_file_name = "game_score.bin"
	
	if os.path.isfile(game_score_file_name):
		game_score = pickle.load(open(game_score_file_name, "rb"))
	else:
		game_score = generate_all_boards()
		pickle.dump(game_score, open(game_score_file_name, "wb"))

	print(game_score)

	"""
	board = initiate_empty_board()
	empty_squares = [i for i in range((SIZE * SIZE))]

	current_player = X_PLAYER
	continue_game = True
	print_board(board)
	while continue_game:
		input("")
		play_random_ai(current_player, board, empty_squares)
		current_player = alternate_players(current_player)
		print_board(board)
		if check_end_party(board):
			continue_game = False
	"""
