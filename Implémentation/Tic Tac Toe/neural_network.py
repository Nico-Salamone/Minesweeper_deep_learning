import random
import numpy as np
from scipy.stats.stats import pearsonr
import time
from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model

import tic_tac_toe as ttt
import data_set as ds

def get_win_ratio(scores):
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

def get_grid_indexes_in_error_range(grids, errors, value_range):
	# Get grid and error indexes whose the error lies in the range.
	# Each grid corresponds to an error (the i th grid corresponds to the i th error).

	min_value = value_range[0]
	max_value = value_range[1]

	grids_in_range = []
	for i in range(len(errors)):
		if min_value <= errors[i] <= max_value:
			grids_in_range.append(i)

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
	training_set = random.sample(data_set, len(data_set))

	x = [0] * len(training_set)
	y_true = [0] * len(training_set)
	for i in range(len(training_set)):
		grid = training_set[i][0]
		scores = training_set[i][1]

		x[i] = tuple(tile.value for tile in grid) # Grid.
		y_true[i] = get_win_ratio(scores) # Ratio of wins.

	model = Sequential()
	model.add(Dense(15, input_dim = 9))
	model.add(Dense(29))
	model.add(Dense(1))

	model.compile(loss = 'mean_squared_error', optimizer = 'sgd', metrics = ['mean_squared_error', 'mean_absolute_error'])

	#model.fit(x, y_true, epochs = 100, batch_size = 1)
	model.fit(x, y_true, epochs = 10, batch_size = 100)
	model.save(model_file_name)

	data_evaluation = model.evaluate(x, y_true)
	y_pred = model.predict(x)

	# Mean squared error.
	print("\n\n{}:".format(model.metrics_names[1]))
	print("{:.2%}".format(data_evaluation[1]))

	# Mean absolute error.
	print("\n{}:".format(model.metrics_names[2]))
	print("{:.2%}".format(data_evaluation[2]))

	# Correlation coefficient and p-value.
	print("\nCorrelation coefficient and p-value:")
	print(pearsonr(y_true, y_pred.flatten()))

	# Error bins.
	print("\nError bins:")
	errors = list(map(lambda y_t, y_p: abs(y_t - y_p), y_true, y_pred.flatten().tolist()))
	data_percentages, bins = error_bins_data_percentage(errors, 10, (0.0, 1.0))
	for i in range(len(data_percentages)):
		print("[{:.2f}-{:.2f}]: {:.3%}".format(bins[i], bins[i+1], data_percentages[i]))

	"""
	# All results (display, for each x, y_true and y_pred).
	print("\nAll results (display, for each x, y_true and y_pred):")
	for i in range(len(x)):
		grid = tuple(ttt.Tile(tile) for tile in x[i])

		print()
		ttt.print_grid(grid)
		print("Error: {:.2f}".format(errors[i]))
		print("y_true: {:.2f}".format(y_true[i]))
		print("y_pred: {:.2f}".format(y_pred[i][0]))
	"""

	# Grids with a bad prediction
	print("\nGrids with a bad prediction:")
	grids_with_bad_prediction_indexex = get_grid_indexes_in_error_range(x, errors, (0.5, 1.0))
	for i in grids_with_bad_prediction_indexex:
		grid = tuple(ttt.Tile(tile) for tile in x[i])

		print()
		ttt.print_grid(grid)
		print("Error: {:.2f}".format(errors[i]))
		print("y_true: {:.2f}".format(y_true[i]))
		print("y_pred: {:.2f}".format(y_pred[i][0]))
