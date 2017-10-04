import random

SIZE = 3

def alternate_players():
	while True:
		yield "x"
		yield "o"

def print_board(board):
	for i in range(len(board)):
		for j in range(len(board)):
			print(board[i][j], end = "")
		print("")

def play_random_ai(player, board, empty_squares):
	if not empty_squares:
		return False

	num_square = random.randint(0, len(empty_squares) - 1)

	board[(num_square // SIZE)][(num_square % SIZE)] = player

	return True

def end_party(board):
	# Columns
	for j in range(SIZE):
		player = board[0][j]
		if player != "-":
			i = 1
			while (i < SIZE) and (board[i][j] == player):
				i += 1
			if i == SIZE:
				print("Winner:", player, "(columns)")
				return player

	# Rows
	for i in range(SIZE):
		player = board[i][0]
		if player != "-":
			j = 1
			while (j < SIZE) and (board[i][j] == player):
				j += 1
			if j == SIZE:
				print("Winner:", player, "(rows)")
				return player

	# Diagonals
	player = board[0][0]
	if player != "-":
		i = 1
		j = 1
		while (i < SIZE) and (j < SIZE) and (board[i][j] == player):
			i += 1
			j += 1
		if (i == SIZE) and (j == SIZE):
			print("Winner:", player, "(diagonals)")
			return player

	# Anti-diagonals
	player = board[SIZE - 1][0]
	if player != "-":
		i = SIZE - 2
		j = 1
		while (i >= 0) and (j < SIZE) and (board[i][j] == player):
			i -= 1
			j += 1
		if (i == -1) and (j == SIZE):
			print("Winner:", player, "(anti-diagonals)")
			return player

	return None

# "x": X player
# "o": O player
# "–": empty box
players = alternate_players()
board = [["-" for i in range(SIZE)] for i in range(SIZE)]
#empty_squares = [(i, j) for i in range(SIZE) for j in range(SIZE)]
empty_squares = [i for i in range((SIZE * SIZE))]

continue_game = True
print_board(board)
while continue_game:
	input("")
	current_player = next(players)
	play_random_ai(current_player, board, empty_squares)
	print_board(board)
	if end_party(board) or not empty_squares:
		continue_game = False

#board = [["x", "x", "o"], ["o", "o", "x"], ["o", "o", "x"]]
#print_board(board)
#end_party(board)
