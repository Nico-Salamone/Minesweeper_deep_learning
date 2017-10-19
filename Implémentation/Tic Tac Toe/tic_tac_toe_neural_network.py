import random
import copy
import os
import pickle
import csv
from scipy.stats.stats import pearsonr
#"""
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
#"""

import tic_tac_toe as ttt

def get_end_game_score(board, numWins, numLosses, numDraws):
	if (numWins == 0) and (numLosses == 0):
		return 0.5

	score = get_during_game_score(board, numWins, numLosses, numDraws)

	if numLosses == 0:
		score *= numWins
	else:
		score *= numWins / numLosses

	if score > 1:
		score = 1
	elif score < 0:
		score = 0

	return score

def get_during_game_score(board, numWins, numLosses, numDraws):
	total_remaining_games = numWins + numLosses + numDraws

	return numWins / total_remaining_games

def calculate_score_function(during_game_score_func = get_during_game_score, end_game_score_func = get_end_game_score, player = ttt.X_PLAYER, first_player_played = ttt.X_PLAYER):
	# Score determinated by player
	# counters = [w, l, d], where 'w' is the number of victories, 'l' is the number of defeats and 'd' is the numbers of draws of 'player'
	game_counters = {}

	score_function = {}

	board = ttt.initiate_empty_board()
	empty_squares = [i for i in range((ttt.SIZE * ttt.SIZE))]

	calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, first_player_played, board, empty_squares, False)

	return score_function

def calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, current_player, board, empty_squares, previous_end_game):
	board_string = ttt.convert_board_to_string(board)
	if board_string in game_counters:
		return game_counters[board_string]

	counters = [0] * 3
	game_score_func = during_game_score_func

	now_end_game = False
	if (not previous_end_game) and (ttt.check_end_game(board)): # End game now
		previous_end_game = True
		now_end_game = True
		game_score_func = end_game_score_func

	if(len(empty_squares) == 0): # No empty squares (the board is filled)
		winning_player = ttt.check_end_game(board)
		if(winning_player == ttt.NONE_PLAYER): # Draw
			counters[2] += 1
		else:
			if(ttt.alternate_players(player) in winning_player): # Lose
				counters[1] += 1
			elif(player in winning_player): # Win
				counters[0] += 1
	else:
		for i in range(len(empty_squares)): # Exploration of child nodes
			board_copy = copy.deepcopy(board)
			empty_squares_copy = copy.copy(empty_squares)

			pos = ttt.get_position_from_num_square(empty_squares_copy.pop(i))
			board_copy[pos[0]][pos[1]] = current_player

			counters_temp = calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, ttt.alternate_players(current_player), board_copy, empty_squares_copy, previous_end_game)
			counters[0] += counters_temp[0]
			counters[1] += counters_temp[1]
			counters[2] += counters_temp[2]

	game_counters[board_string] = counters
	if (len(empty_squares) >= 2) and \
			(current_player == ttt.alternate_players(player)) and \
			((not previous_end_game) or (now_end_game)):
		score_function[board_string] = game_score_func(board, counters[0], counters[1], counters[2])

	return counters

def get_score_function():
	score_function_file_name = "score_function.bin"
	
	if os.path.isfile(score_function_file_name):
		score_function = pickle.load(open(score_function_file_name, "rb"))
	else:
		score_function = calculate_score_function()
		pickle.dump(score_function, open(score_function_file_name, "wb"))

	return score_function

def generate_data_set(data_set_size, score_function = None):
	if score_function == None:
		score_function = get_score_function()

	boards = score_function.keys()

	boards_selected = random.sample(boards, data_set_size)
	data_set = [0] * data_set_size

	i = 0
	for board in boards_selected:
		data_set[i] = (board, score_function[board])

		i += 1

	return data_set

def read_data_set(data_set_file_name = "data_set.csv"):
	data_set = []
	with open(data_set_file_name, newline = '') as data_set_file:
		csv_reader = csv.reader(data_set_file, delimiter = ';', quotechar = '\"')

		i = 0
		for row in csv_reader:
			data_set.append((row[0], float(row[1])))

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
	"""
	score_function = calculate_score_function()

	for board, score in score_function.items():
		ttt.print_board(ttt.convert_string_to_board(board))
		print(score, "\n")
	"""

	#"""
	data_set = get_data_set(1000)

	#print(data_set)
	
	x = [0] * len(data_set)
	y = [0] * len(data_set)
	i = 0
	for data in data_set:
		x[i] = [ttt.convert_player_to_id(p) for p in list(data[0])]
		y[i] = data[1]

		i += 1

	#print(x)
	#print(y)

	model_file_name = "model.h5"
	if not os.path.isfile(model_file_name):
		model = Sequential()
		model.add(Dense(10, input_dim = 9))
		model.add(Dense(29))
		model.add(Dense(1))

		#model.compile(loss = 'mean_squared_error', optimizer = 'adam', metrics = ['mean_squared_error'])
		model.compile(loss = 'mean_squared_error', optimizer = 'sgd', metrics = ['mean_squared_error'])

		model.fit(x, y, epochs = 100, batch_size = 10)
		#model.fit(x, y, epochs = 10, batch_size = 100)

		scores = model.evaluate(x, y)
		print("\n{}: {:.2%}".format(model.metrics_names[1], scores[1]))

		#model.save(model_file_name)
	else:
		model = load_model(model_file_name)

	predictions = model.predict(x)
	#print(pearsonr(y, predictions))

	for i in range(len(x)):
		print("%s: %.2f %.2f" % ([ttt.convert_id_to_player(id) for id in x[i]], y[i], predictions[i]))
		#print("{}: {} {}".format([ttt.convert_id_to_player(id) for id in x[i]], y[i], predictions[i]))
	#"""
