import random
import copy
import os
import pickle
import csv
from scipy.stats.stats import pearsonr
#from keras.models import Sequential
#from keras.layers import Dense
#from keras.models import load_model

import tic_tac_toe as ttt

def get_end_game_evalution(board, numWins, numLosses, numDraws):
	return 1

def get_during_game_evalution(board, numWins, numLosses, numDraws):
	total_remaining_games = numWins + numLosses + numDraws

	return numWins / total_remaining_games

def calculate_evaluation_function(during_game_evalution_func = get_during_game_evalution, end_game_evalution_func = get_end_game_evalution, player = ttt.X_PLAYER, first_player_played = ttt.X_PLAYER):
	# Score determinated by player
	# score = [w, l, d], where 'w' is the number of victories, 'l' is the number of defeats and 'd' is the numbers of draws of 'player'
	game_score = {}

	evaluation_function = {}

	board = ttt.initiate_empty_board()
	empty_squares = [i for i in range((ttt.SIZE * ttt.SIZE))]

	calculate_evaluation_function_rec(during_game_evalution_func, end_game_evalution_func, player, evaluation_function, game_score, first_player_played, board, empty_squares)

	return evaluation_function

def calculate_evaluation_function_rec(during_game_evalution_func, end_game_evalution_func, player, evaluation_function, game_score, current_player, board, empty_squares):
	board_string = ttt.convert_board_to_string(board)
	if board_string in game_score:
		return game_score[board_string]

	score = [0] * 3

	winning_player = ttt.check_end_game(board)
	if(not winning_player):
		for i in range(len(empty_squares)):
			board_copy = copy.deepcopy(board)
			empty_squares_copy = copy.copy(empty_squares)

			pos = ttt.get_position_from_num_square(empty_squares_copy.pop(i))
			board_copy[pos[0]][pos[1]] = current_player

			score_temp = calculate_evaluation_function_rec(during_game_evalution_func, end_game_evalution_func, player, evaluation_function, game_score, ttt.alternate_players(current_player), board_copy, empty_squares_copy)
			score[0] += score_temp[0]
			score[1] += score_temp[1]
			score[2] += score_temp[2]

		evaluation = during_game_evalution_func(board, score[0], score[1], score[2])
	else: # End game
		if(winning_player == ttt.NONE_PLAYER): # Draw
			score[2] += 1
		elif(winning_player == player): # Win
			score[0] += 1
		else: # Lose
			score[1] += 1

		evaluation = end_game_evalution_func(board, score[0], score[1], score[2])

	game_score[board_string] = score
	evaluation_function[board_string] = evaluation

	return score

def get_evaluation_function():
	evaluation_function_file_name = "evaluation_function.bin"
	
	if os.path.isfile(evaluation_function_file_name):
		evaluation_function = pickle.load(open(evaluation_function_file_name, "rb"))
	else:
		evaluation_function = calculate_evaluation_function()
		pickle.dump(evaluation_function, open(evaluation_function_file_name, "wb"))

	return evaluation_function

def generate_data_set(data_set_size, evaluation_function = get_evaluation_function()):
	boards = evaluation_function.keys()

	boards_selected = random.sample(boards, data_set_size)
	data_set = [0] * data_set_size

	i = 0
	for board in boards_selected:
		data_set[i] = (board, evaluation_function[board])

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
	evaluation_function = calculate_evaluation_function()

	for board, evaluation in evaluation_function.items():
		print(board)
		print(evaluation, "\n")

	"""

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

		model.compile(loss = 'mean_squared_error', optimizer = 'adam', metrics = ['mean_squared_error'])
		#model.compile(loss = 'mean_squared_error', optimizer = 'sgd', metrics = ['mean_squared_error'])

		#model.fit(x, y, epochs = 100, batch_size = 10)
		model.fit(x, y, epochs = 10, batch_size = 100)

		scores = model.evaluate(x, y)
		print("\n{}: {:.2%}".format(model.metrics_names[1], scores[1]))

		#model.save(model_file_name)
	else:
		model = load_model(model_file_name)

	predictions = model.predict(x)
	#print(pearsonr(y, predictions))

	#for i in range(len(x)):
		#print("{}: {} {}".format([ttt.convert_id_to_player(id) for id in x[i]], y[i], predictions[i]))
		#print("%s: %d %d" % ([ttt.convert_id_to_player(id) for id in x[i]], y[i], predictions[i]))

	"""






