import random
import numpy as np
from scipy.stats.stats import pearsonr
import time
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model

import tic_tac_toe as ttt
import data_set as ds

def get_data_for_neural_network(training_set, y_true_computation_func):
	# Get data (x, y_true) for training the neural network.
	# x is the grid and y is a value compted by y_true_computation_func.
	# For each x, y_true is computed by sending x to the function y_true_computation_func.
	# This function has two parameters: the grid and the scores.
	
	n = len(training_set)
	
	x = [0] * n
	y_true = [0] * n
	for i in range(n):
		grid = training_set[i][0]
		scores = training_set[i][1]

		x[i] = tuple(tile.value for tile in grid) # Grid.
		y_true[i] = y_true_computation_func(grid, scores)

	return x, y_true

def create_fit_model(x, y_true, output_size = None, model_file_name = None):
	if output_size == None:
		if hasattr(y_true[0], "__len__"):
			output_size = len(y_true[0])
		else:
			output_size = 1

	model = Sequential()
	model.add(Dense(15, input_dim = 9))
	model.add(Dense(29))
	model.add(Dense(output_size))

	model.compile(loss = 'mean_squared_error', optimizer = 'sgd', metrics = ['mean_squared_error', 'mean_absolute_error'])

	#model.fit(x, y_true, epochs = 100, batch_size = 1)
	model.fit(x, y_true, epochs = 10, batch_size = 100)
	if model_file_name:
		model.save(model_file_name)

	return model

def print_loss_metric_functions(model, x, y_true):
	data_evaluation = model.evaluate(x, y_true, batch_size = 1)

	print("\n\n")
	
	for i in range(len(data_evaluation)):
		print("{}: {:.2f}".format(model.metrics_names[i], data_evaluation[i]))

def print_neural_network_results(errors, error_names = None):
	# The errors variable is a list of the errors.
	# For example, the errors variable contains a list of the absolute errors and a list of the relative errors.
	
	num_errors = len(errors)

	if error_names == None:
		error_names = [""] * num_errors
		for i in range(num_errors):
			error_names[i] = "Error #{}".format(i + 1)

def get_win_ratio(grid, scores):
	num_wins = scores[0]
	num_losses = scores[1]
	num_draws = scores[2]

	total_games = num_wins + num_losses + num_draws

	return num_wins / total_games

def error_bins_data_percentage(errors, num_bins = 10, value_range = None):
	# For each bin 'b', get the percentage of data which are in 'b'.
	
	if value_range == None:
		value_range = (min(errors), max(errors))

	counts, bins = np.histogram(np.array(errors), bins = num_bins, range = value_range)
	counts = counts.astype(float)

	n = len(errors)
	data_percentages = [(counts[i] / n) for i in range(len(counts))]

	return (data_percentages, bins)

def get_grid_in_error_range(grids, scores_true, scores_pred, errors, value_range = None):
	# Get grid, score_true, score_pred and error when error lies in the range.
	
	if value_range == None:
		value_range = (min(errors), max(errors))

	min_value = value_range[0]
	max_value = value_range[1]

	grids_in_range = []
	for i in range(len(errors)):
		if min_value <= errors[i] <= max_value:
			grids_in_range.append((grids[i], scores_true[i], scores_pred[i], errors[i]))

	return grids_in_range

if __name__ == "__main__":
	seed = 867342
	#seed = time.time()
	data_set_file_name = "data_set.csv"
	num_samples = 1000
	model_file_name = "model.h5"

	random.seed(seed)
	np.random.seed(int(seed))

	data_set = ds.read_data_set(data_set_file_name)
	#training_set = random.sample(data_set, num_samples)
	training_set = data_set
	x, y_true = get_data_for_neural_network(training_set, get_win_ratio)
	model = create_fit_model(x, y_true)

	# Results

	print_loss_metric_functions(model, x, y_true)

	y_pred = model.predict(x)
	errors = list(map(lambda y_t, y_p: abs(y_t - y_p), y_true, y_pred.flatten().tolist()))

	# Correlation coefficient and p-value.
	print("\nCorrelation coefficient and p-value:")
	print(pearsonr(y_true, y_pred.flatten()))

	# Error bins.
	print("\nThe percentage of data which are in the follow bins:")
	data_percentages, bins = error_bins_data_percentage(errors, 10, (0.0, 1.0))
	for i in range(len(data_percentages)):
		print("[{:.2f}-{:.2f}]: {:.3%}".format(bins[i], bins[i+1], data_percentages[i]))

	"""
	# All results (display, for each x, y_true and y_pred).
	print("\nAll results (display, for each x, y_true and y_pred):")
	for i in range(len(x)):
		grid = tuple(ttt.Tile(tile) for tile in x[i])

		ttt.print_grid(grid)
		print("Error: {:.2f}".format(errors[i]))
		print("y_true: {:.2f}".format(y_true[i]))
		print("y_pred: {:.2f}".format(y_pred[i][0]))
		print()
	"""

	# Grids with a bad prediction
	print("\nGrids with a bad prediction:")
	grids_with_bad_prediction = get_grid_in_error_range(x, y_true, y_pred, errors, (0.5, 1.0))
	for x_gr, y_t, y_p, err in grids_with_bad_prediction:
		grid = tuple(ttt.Tile(tile) for tile in x_gr)

		ttt.print_grid(grid)
		print("Error: {:.2f}".format(err))
		print("y_true: {:.2f}".format(y_t))
		print("y_pred: {:.2f}".format(y_p[0]))
		print()
