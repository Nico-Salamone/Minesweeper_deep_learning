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

def compute_errors(model, x, y_true, y_pred, error_function_list):
	# y_true_components and y_pred_components are two-dimensuinal matrix. The first dimension represents the components of one y_true element and the second dimension the grid. 
	# error_function_list contain a list of function computing an error from all y_true and all y_pred.
	# The objets returned is a three-dimensional matrix. The first dimension represents the error, the second the y component and the third the grid.

	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)
	
	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	num_errors = len(error_function_list)
	errors = [[0] * y_size] * num_errors
	for i in range(num_errors): # Error function.
		err_func = error_function_list[i]
		for j in range(y_size): # y size.
			errors[i][j] = err_func(y_true_components[j], y_pred_components[j])

	return errors

"""
def compute_errors(model, x, y_true, y_pred, error_function_list, y_is_primitive = None):
	# error_function_list contain a list of function computing an error from all y_true and all y_pred.

	if y_is_primitive == None:
		if hasattr(y_true[0], "__len__"):
			y_is_primitive = False
		else:
			y_is_primitive = True

	if not y_is_primitive:
		y_size = len(y_true[0])
	else:
		y_size = 1

	num_errors = len(error_function_list)
	errors = [[0] * y_size] * num_errors
	for i in range(num_errors): # Error function.
		err_func = error_function_list[i]
		if y_is_primitive:
			errors[i][0] = err_func(y_true, y_pred.flatten().tolist())
		else:
			for j in range(y_size): # y size.
				errors[i][j] = err_func(y_true[j], y_pred[j].flatten().tolist())

	return errors
"""

def error_bins_data_percentage(errors, num_bins = 10, error_range = None):
	# For each bin 'b', get the percentage of data which are in 'b'.
	# Only for a type of error.
	
	if error_range == None:
		error_range = (min(errors), max(errors))

	counts, bins = np.histogram(np.array(errors), bins = num_bins, range = error_range)
	counts = counts.astype(float)

	n = len(errors)
	data_percentages = [(counts[i] / n) for i in range(len(counts))]

	return (data_percentages, bins)

def mutiple_error_bins_data_percentage(errors, num_bins = 10, error_ranges = None):
	# The errors variable is a list of the errors.
	
	num_errors = len(errors)

	if error_ranges == None:
		error_ranges = [None] * num_errors

	y_size = len(errors[0])

	data_percentages_bins = [[0] * y_size] * num_errors
	for i in range(num_errors):
		for j in range(y_size):
			data_percentages, bins = error_bins_data_percentage(errors[i][j], num_bins, error_ranges[i])
			data_percentages_bins[i][j] = (data_percentages, bins)

	return data_percentages_bins

def get_grid_in_error_range(grids, scores_true, scores_pred, errors, error_range):
	# Get grid, score_true, score_pred and error when error lies in the range.

	min_value = error_range[0]
	max_value = error_range[1]

	grids_in_range = []
	for i in range(len(errors)):
		if min_value <= errors[i] <= max_value:
			grids_in_range.append((grids[i], scores_true[i], scores_pred[i], errors[i]))

	return grids_in_range

def mean_standard_deviation_error_by_num_empty_squares(grids, errors):
	# The nth chunck corresponds to all grids with nth empty squares.
	# For each chuck, compute the mean and the standard deviation for all errors in this chunck.
	# The nth element from grids corresponds to the nth element from errors.
	
	n = len(grids)
	num_chunks = ttt.SIZE + 1

	# Split (grids, errors) by number of empty squares.
	chunks = [[] for i in range(num_chunks)]
	for i in range(n):
		gr = grids[i]
		grid_tiles = tuple(ttt.Tile(tile) for tile in gr)
		err = errors[i]

		num_empty_squares = len(ttt.get_empty_tile_indexes(grid_tiles))
		chunks[num_empty_squares].append(err)

	mean_std_error = [0] * num_chunks
	for i in range(num_chunks):
		mean_std_error[i] = (np.mean(chunks[i]), np.std(chunks[i]))

	return mean_std_error

def mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, errors):
	# The errors variable is a list of the errors.
	
	num_errors = len(errors)
	y_size = len(errors[0])

	mean_std_error = [[0] * y_size] * num_errors
	for i in range(num_errors):
		for j in range(y_size):
			mean_std_error[i][j] = mean_standard_deviation_error_by_num_empty_squares(grids, errors[i][j])

	return mean_std_error

def format_y_true_pred(y_true, y_pred):
	if hasattr(y_true[0], "__len__"):
		y_is_primitive = False

		y_size = len(y_true[0])
	else:
		y_is_primitive = True

		y_size = 1
		y_true = [[y_t] for y_t in y_true]
		y_pred = [[y_p] for y_p in y_pred.flatten().tolist()]

	return y_true, y_pred, y_size, y_is_primitive
		
def sort_by_y_components(y):
	# The output of this function is a two-dimensuinal matrix. The first dimension represents the components of one y element and the second dimension the grid.

	return np.transpose(y).tolist()

def print_loss_metric_functions(model, x, y_true):
	data_evaluation = model.evaluate(x, y_true, batch_size = 1)

	print("\n\n")
	
	for i in range(len(data_evaluation)):
		print("{}: {:.3f}".format(model.metrics_names[i], data_evaluation[i]))

def print_correlation_coefficient_p_value(y_true, y_pred, y_names = None):
	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	# Sort y_true and y_pred by components.
	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("Correlation coefficient and p-value:")
	for i in range(y_size):
		print("{}: {}".format(y_names[i], pearsonr(y_true_components[i], y_pred_components[i])))

def print_mutiple_error_bins_data_percentage(y_true, y_pred, errors, y_names = None, error_ranges = None, error_names = None, num_bins = 10):
	num_errors = len(errors)

	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	data_percentages_bins = mutiple_error_bins_data_percentage(errors, num_bins, error_ranges)

	print("The percentage of data which are in the follow bins:")
	for i in range(num_errors):
		print("{}:".format(error_names[i]))

		for j in range(y_size):
			print("{}:".format(y_names[j]))

			data_percentages, bins = data_percentages_bins[i][j]
			for i in range(len(data_percentages)):
				print("[{:.2f}-{:.2f}]: {:.3%}".format(bins[i], bins[i+1], data_percentages[i]))

		print()

def print_all_grids_with_result(x, y_true, y_pred, errors, y_names = None, error_names = None):
	num_errors = len(errors)

	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("All results (for each x, display y_true, y_pred and errors):")
	for i in range(len(x)):
		grid = tuple(ttt.Tile(tile) for tile in x[i])

		ttt.print_grid(grid)
		for j in range(y_size):
			print("{}:".format(y_names[j]))

			print("y_true: {:.2f}".format(y_true_components[j][i]))
			print("y_pred: {:.2f}".format(y_pred_components[j][i]))
			for k in range(num_errors):
				print("{}: {:.2f}".format(error_names[k], errors[k][j][i]))

		print()

def print_grid_in_error_range(x, y_true, y_pred, errors, error_range, y_names = None, error_names = None):
	num_errors = len(errors)

	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("Grids whose the error lies in [{}, {}]:".format(*error_range))
	for i in range(num_errors):
		print("{}:".format(error_names[i]))

		for j in range(y_size):
			print("{}:".format(y_names[j]))

			grids_in_error_range = get_grid_in_error_range(x, y_true_components[j], y_pred_components[j], errors[i][j], error_range)
			for x_gr, y_t, y_p, err in grids_in_error_range:
				grid = tuple(ttt.Tile(tile) for tile in x_gr)

				ttt.print_grid(grid)
				print("y_true: {:.2f}".format(y_t))
				print("y_pred: {:.2f}".format(y_p))
				print("{}: {:.2f}".format(y_names[j], err))

				print()

def print_mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, y_true, y_pred, errors, y_names = None, error_names = None):
	num_errors = len(errors)

	y_true, y_pred, y_size, y_is_primitive = format_y_true_pred(y_true, y_pred)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	mean_std_error = mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, errors)

	print("Mean and standard deviation error by number of empty squares:")
	for i in range(num_errors):
		print("{}:".format(error_names[i]))

		for j in range(y_size):
			print("{}:".format(y_names[j]))

			msd = mean_std_error[i][j]
			for i in range(len(msd)):
				print("{} empty squares: mean error of {:.3f} and standard deviation error of {:.3f}".format(i, msd[i][0], msd[i][1]))

		print()

def get_win_ratio(grid, scores):
	num_wins = scores[0]
	num_losses = scores[1]
	num_draws = scores[2]

	total_games = num_wins + num_losses + num_draws

	return num_wins / total_games

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
	y_pred = model.predict(x, batch_size = 1)

	# Results
	error_function_list = [lambda y_t, y_p: list(map(lambda t, p: abs(t - p), y_t, y_p))]
	error_ranges = [(0.0, 1.0)]
	y_names = ["Victory ratio"]
	error_names = ["Absolute error"]

	errors = compute_errors(model, x, y_true, y_pred, error_function_list)
	
	print_loss_metric_functions(model, x, y_true)
	print()
	print_correlation_coefficient_p_value(y_true, y_pred, y_names = y_names)
	print()
	print_mutiple_error_bins_data_percentage(y_true, y_pred, errors, error_ranges = error_ranges, y_names = y_names, error_names = error_names)
	#print_all_grids_with_result(x, y_true, y_pred, errors, y_names = y_names, error_names = error_names)
	print_grid_in_error_range(x, y_true, y_pred, errors, (0.5, 1.0), y_names = y_names, error_names = error_names)
	print_mutiple_mean_standard_deviation_error_by_num_empty_squares(x, y_true, y_pred, errors, y_names = y_names, error_names = error_names)
