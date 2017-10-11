import random
import copy
import os
import pickle
import csv

import tic_tac_toe as ttt

def generate_all_boards(player = ttt.X_PLAYER, first_player_played = ttt.X_PLAYER):
	# Score determinated by player
	# score = [w, l, d], where 'w' is the number of victories, 'l' is the number of defeats and 'd' is the numbers of draws of 'player'
	game_score = {}

	board = ttt.initiate_empty_board()
	empty_squares = [i for i in range((ttt.SIZE * ttt.SIZE))]

	generate_all_boards_rec(player, game_score, board, empty_squares, first_player_played)

	return game_score

def generate_all_boards_rec(player, game_score, board, empty_squares, current_player):
	board_in_string = ttt.convert_board_to_string(board)
	if board_in_string in game_score:
		return game_score[board_in_string]

	score = [0] * 3

	winning_player = ttt.check_end_party(board)
	if(not winning_player):
		for i in range(len(empty_squares)):
			board_temp = copy.deepcopy(board)
			empty_squares_temp = copy.copy(empty_squares)

			pos = ttt.get_position_from_num_square(empty_squares_temp.pop(i))
			board_temp[pos[0]][pos[1]] = current_player

			score_temp = generate_all_boards_rec(player, game_score, board_temp, empty_squares_temp, ttt.alternate_players(current_player))
			score = [(score[i] + score_temp[i]) for i in range(len(score))]
	elif(winning_player == ttt.NONE_PLAYER): # Draw
		score[2] += 1
	elif(winning_player == player): # Win
		score[0] += 1
	else: # Lose
		score[1] += 1

	game_score[board_in_string] = score

	return score

def get_game_score():
	game_score_file_name = "game_score.bin"
	
	if os.path.isfile(game_score_file_name):
		game_score = pickle.load(open(game_score_file_name, "rb"))
	else:
		game_score = generate_all_boards()
		pickle.dump(game_score, open(game_score_file_name, "wb"))

	return game_score

def generate_data_set(data_set_size, game_score = get_game_score()):
	all_boards = game_score.keys()

	boards_selected = random.sample(all_boards, data_set_size)
	data_set = [0] * data_set_size

	i = 0
	for board in boards_selected:
		score = game_score[board]
		data_set[i] = (board, (score[0] - score[1]))

		i += 1

	return data_set

def read_data_set(data_set_file_name = "data_set.csv"):
	data_set = []
	with open(data_set_file_name, newline = '') as data_set_file:
		csv_reader = csv.reader(data_set_file, delimiter = ';', quotechar = '\"')

		i = 0
		for row in csv_reader:
			data_set.append((row[0], int(row[1])))

			i += 1

	return data_set

def write_data_set(data_set, data_set_file_name = "data_set.csv"):
	with open(data_set_file_name, 'w', newline = '') as data_set_file:
		csv_writer = csv.writer(data_set_file, delimiter = ';', quotechar = '\"', quoting = csv.QUOTE_MINIMAL)

		for data in data_set:
			csv_writer.writerow([data[0], data[1]])

def get_data_set(data_set_size, data_set_file_name = "data_set.csv"):
	data_set = []
	if os.path.isfile(data_set_file_name):
		data_set = read_data_set(data_set_file_name)

	if not os.path.isfile(data_set_file_name) or (len(data_set) != data_set_size):
		data_set = generate_data_set(data_set_size)
		write_data_set(data_set, data_set_file_name)

	return data_set

if __name__ == "__main__":
	data_set = get_data_set(1000)

	#print(data_set)
