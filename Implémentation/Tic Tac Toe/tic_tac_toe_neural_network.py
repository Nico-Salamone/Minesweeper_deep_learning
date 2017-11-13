import random
import time
import copy
import os
import csv
import numpy as np
from scipy.stats.stats import pearsonr
#"""
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
#"""

import tic_tac_toe as ttt

def get_end_game_score(board, numWins, numLosses, numDraws):
	score = get_during_game_score(board, numWins, numLosses, numDraws)

	return score

def get_during_game_score(board, numWins, numLosses, numDraws):
	total_remaining_games = numWins + numLosses + numDraws

	return numWins / total_remaining_games

def calculate_score_function(during_game_score_func = get_during_game_score, end_game_score_func = get_end_game_score, player = ttt.Player.X_PLAYER, first_player_played = ttt.Player.X_PLAYER):
	# Score determinated by player
	# counters = [w, l, d], where 'w' is the number of victories, 'l' is the number of defeats and 'd' is the numbers of draws of 'player'
	game_counters = {}

	score_function = {}

	board = ttt.initiate_empty_board()
	empty_squares = [i for i in range((ttt.SIZE * ttt.SIZE))]

	calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, first_player_played, board, empty_squares, None)

	return score_function

def calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, current_player, board, empty_squares, previous_end_game_winner):
	board_string = ttt.convert_board_to_string(board)

	counters = [0] * 3
	game_score_func = during_game_score_func

	now_end_game = False
	if not previous_end_game_winner:
		winner = ttt.check_end_game(board) # if there is not empty squares (the board is filled), then the winner is ttt.NONE_PLAYER (not None)

		if winner: # End game now
			previous_end_game_winner = winner.pop() # Only there is one winner because this function is called round by round
			now_end_game = True
			game_score_func = end_game_score_func

	board_string_with_winner = board_string + str(previous_end_game_winner)
	if board_string_with_winner in game_counters:
		return game_counters[board_string_with_winner]

	if previous_end_game_winner: # Winner at this call or winner at a previous call (an ancestor node)
		game_score_func = end_game_score_func

		if previous_end_game_winner == ttt.Player.NONE_PLAYER: # Draw
			counters[2] += 1
		elif previous_end_game_winner == player: # 'player' win
			counters[0] += 1
		else: # 'player' lose
			counters[1] += 1

	# Exploration of child nodes
	for i in range(len(empty_squares)):
		board_copy = copy.deepcopy(board)
		empty_squares_copy = copy.copy(empty_squares)

		pos = ttt.get_position_from_num_square(empty_squares_copy.pop(i))
		board_copy[pos[0]][pos[1]] = current_player.id

		counters_temp = calculate_score_function_rec(during_game_score_func, end_game_score_func, player, score_function, game_counters, ttt.Player.alternate_players(current_player), board_copy, empty_squares_copy, previous_end_game_winner)
		counters[0] += counters_temp[0]
		counters[1] += counters_temp[1]
		counters[2] += counters_temp[2]

	game_counters[board_string_with_winner] = counters

	if (len(empty_squares) >= 1) and \
			(current_player == ttt.Player.alternate_players(player)) and \
			((not previous_end_game_winner) or (now_end_game)):
		score_function[board_string] = game_score_func(board, counters[0], counters[1], counters[2])

	return counters

def write_data_set(data_set, data_set_file_name = "data_set.csv"):
	with open(data_set_file_name, 'w', newline = '') as data_set_file:
		csv_writer = csv.writer(data_set_file, delimiter = ';', quotechar = '\"', quoting = csv.QUOTE_MINIMAL)

		for board, score in data_set.items():
			squares_score = board.split(' ')
			squares_score.append(score)

			csv_writer.writerow(squares_score)

def read_data_set(data_set_file_name = "data_set.csv"):
	data_set = {}
	with open(data_set_file_name, newline = '') as data_set_file:
		csv_reader = csv.reader(data_set_file, delimiter = ';', quotechar = '\"')

		n = (ttt.SIZE * ttt.SIZE)
		for row in csv_reader:
			squares = row[:n]
			board = ' '.join(str(s) for s in squares)

			data_set[board] = float(row[n])

	return data_set

def sample_data_set(data_set, num_samples, seed = time.time()):
	random.seed(seed)

	sample = {}

	boards_selected = random.sample(data_set.keys(), num_samples)

	for board in boards_selected:
		sample[board] = data_set[board]

	return (sample, seed)

def error_bins(errors, num_bins = 10, value_range = None):
	if value_range == None:
		value_range = (min(errors), max(errors))

	counts, bins = np.histogram(np.array(copy.copy(errors)), bins = num_bins, range = value_range)
	counts = counts.astype(float)

	n = len(errors)
	for i in range(len(counts)):
		counts[i] /= n # Percentage.

	return (counts, bins)

def get_board_index_in_error_range(boards, errors, value_range):
	# Get board and error index whose the error lies in the range.
	# Each board corresponds to an error.

	min_value = value_range[0]
	max_value = value_range[1]

	boards_selected = []
	for i in range(len(errors)):
		if min_value <= errors[i] <= max_value:
			boards_selected.append(i)

	return boards_selected

if __name__ == "__main__":
	seed = 867342
	np.random.seed(seed)

	data_set = calculate_score_function()
	write_data_set(data_set)

	training_set, _ = sample_data_set(data_set, 1000, seed)

	"""
	for board, score in data_set.items():
		ttt.print_board(ttt.convert_string_to_board(board))
		print(score, "\n")
	"""

	#"""
	x = [0] * len(training_set)
	y_true = [0] * len(training_set)
	i = 0
	for board, score in training_set.items():
		x[i] = list(map(int, board.split(' ')))
		y_true[i] = score

		i += 1

	#print(x)
	#print(y)

	model_file_name = "model.h5"
	if not os.path.isfile(model_file_name):
		model = Sequential()
		model.add(Dense(15, input_dim = 9))
		model.add(Dense(29))
		model.add(Dense(1))

		model.compile(loss = 'mean_squared_error', optimizer = 'sgd', metrics = ['mean_squared_error', 'mean_absolute_error'])

		#model.fit(x, y_true, epochs = 100, batch_size = 10)
		model.fit(x, y_true, epochs = 10, batch_size = 100)

		scores = model.evaluate(x, y_true)

		#model.save(model_file_name)
	else:
		model = load_model(model_file_name)

	y_pred = model.predict(x)

	# Mean squared error
	print("\n\n{}:".format(model.metrics_names[1]))
	print("{:.2%}".format(scores[1]))

	# Mean absolute error
	print("\n{}:".format(model.metrics_names[2]))
	print("{:.2%}".format(scores[2]))

	# Correlation coefficient and p-value
	print("\nCorrelation coefficient and p-value:")
	print(pearsonr(y_true, y_pred.flatten()))

	# Error bins
	print("\nError bins:")
	errors = list(map(lambda t, p: abs(t - p), y_true, y_pred.flatten().tolist()))
	percentages, bins = error_bins(errors, 10, (0.0, 1.0))
	for i in range(len(percentages)):
		print("[{:.2f}-{:.2f}]: {:.3%}".format(bins[i], bins[i+1], percentages[i]))

	"""
	# All results (display for each 'x' y_true and y_pred)
	print("\nAll results (display for each 'x' y_true and y_pred):")
	for i in range(len(x)):
		print()
		ttt.print_board(ttt.convert_string_to_board(' '.join(map(str, x[i]))))
		print("Error: {:.2f}".format(errors[i]))
		print("y_true: {:.2f}".format(y_true[i]))
		print("y_pred: {:.2f}".format(y_pred[i][0]))
	"""

	# Boards with a bad prediction
	print("\nBoards with a bad prediction:")
	boards_with_bad_prediction = get_board_index_in_error_range(x, errors, (0.5, 1.0))
	for i in boards_with_bad_prediction:
		print()
		ttt.print_board(ttt.convert_string_to_board(' '.join(map(str, x[i]))))
		print("Error: {:.2f}".format(errors[i]))
		print("y_true: {:.2f}".format(y_true[i]))
		print("y_pred: {:.2f}".format(y_pred[i][0]))
	#"""
