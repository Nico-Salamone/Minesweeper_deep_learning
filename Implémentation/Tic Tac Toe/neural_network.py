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

		#x[i] = tuple(tile.value for tile in grid) # Grid.
		x[i] = grid
		y_true[i] = y_true_computation_func(grid, scores)

	return x, y_true

def convert_grid_for_neural_network(grid):
	return tuple([tile.value for tile in grid])

def create_fit_model(x, y_true, output_size = None, model_file_name = None):
	if output_size == None:
		if hasattr(y_true[0], "__len__"):
			output_size = len(y_true[0])
		else:
			output_size = 1

	x = [convert_grid_for_neural_network(grid) for grid in x]

	model = Sequential()
	model.add(Dense(60, input_dim = 9, activation = 'relu'))
	model.add(Dense(180, activation = 'relu'))
	model.add(Dense(70, activation = 'relu'))
	model.add(Dense(output_size, activation = 'relu'))

	model.compile(loss = 'mean_squared_error', optimizer = 'rmsprop', metrics = ['mean_squared_error', 'mean_absolute_error'])

	model.fit(x, y_true, epochs = 100, batch_size = 10)
	#model.fit(x, y_true, epochs = 10, batch_size = 100)
	if model_file_name:
		model.save(model_file_name)

	return model

def get_win_ratio(grid, scores):
	num_wins = scores[0]
	num_losses = scores[1]
	num_draws = scores[2]

	total_games = num_wins + num_losses + num_draws

	return num_wins / total_games

def get_win_loss_draw_ratio(grid, scores):
	num_wins = scores[0]
	num_losses = scores[1]
	num_draws = scores[2]

	total_games = num_wins + num_losses + num_draws

	return ((num_wins / total_games), (num_losses / total_games), (num_draws / total_games))

def compute_errors(model, x, y_true, y_pred, error_function_list):
	# y_true_components and y_pred_components are two-dimensuinal matrix. The first dimension represents the components of one y_true element and the second dimension the grid. 
	# error_function_list contain a list of function computing an error from all y_true and all y_pred.
	# The objets returned is a three-dimensional matrix. The first dimension represents the error, the second the y component and the third the grid.

	y_size = get_y_size(y_true)
	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	num_errors = len(error_function_list)
	errors = [[0] * y_size] * num_errors
	for i in range(num_errors): # Error function.
		err_func = error_function_list[i]
		for j in range(y_size): # y size.
			errors[i][j] = err_func(y_true_components[j], y_pred_components[j])

	return errors

def mean_standard_deviation_errors(errors):
	num_errors = len(errors)
	y_size = get_y_size_from_errors(errors)

	mean_std = [[0] * y_size] * num_errors
	for i in range(num_errors):
		for j in range(y_size):
			mean_std[i][j] = (np.mean(errors[i][j]), np.std(errors[i][j]))

	return mean_std

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

	y_size = get_y_size_from_errors(errors)

	data_percentages_bins = [[0] * y_size] * num_errors
	for i in range(num_errors):
		for j in range(y_size):
			data_percentages, bins = error_bins_data_percentage(errors[i][j], num_bins, error_ranges[i])
			data_percentages_bins[i][j] = (data_percentages, bins)

	return data_percentages_bins

def get_grid_in_error_range(grids, y_true, y_pred, errors, error_range):
	# Get grid, y_true, y_pred and error when error lies in the range.

	min_value = error_range[0]
	max_value = error_range[1]

	grids_in_range = []
	for i in range(len(errors)):
		if min_value <= errors[i] <= max_value:
			grids_in_range.append((grids[i], y_true[i], y_pred[i], errors[i]))

	return grids_in_range

def filter_grids_by_empty_squares(grids, elements = None):
	# elements is a list of elements related to grid (for exemple, y_true, y_pred, errors).
	# The nth grid from grids corresponds to the nth element from elements.
	# The nth bin corresponds to all grids with nth empty squares.

	n = len(grids)
	num_bins = ttt.SIZE + 1

	# Split (grids, errors) by number of empty squares.
	bins = [[] for i in range(num_bins)] 
	for i in range(n):
		grid = grids[i]
		
		num_empty_squares = len(ttt.get_empty_tile_indexes(grid))
		if elements is not None:
			element = elements[i]
			element_to_append = (grid, element)
		else:
			element_to_append = grid
		bins[num_empty_squares].append(element_to_append)

	return bins

def mean_standard_deviation_error_by_num_empty_squares(grids, errors):
	# The nth bin corresponds to all grids with nth empty squares.
	# For each bin, compute the mean and the standard deviation for all errors in this bin.
	# The nth grid from grids corresponds to the nth error from errors.
	
	n = len(grids)

	bins = filter_grids_by_empty_squares(grids, errors)
	num_bins = len(bins)
	for i in range(num_bins):
		bins[i] = [err for (grid, err) in bins[i]]

	mean_std_error = [0] * num_bins
	for i in range(num_bins):
		mean_std_error[i] = (np.mean(bins[i]), np.std(bins[i]))

	return mean_std_error

def mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, errors):
	# The errors variable is a list of the errors.
	
	num_errors = len(errors)
	y_size = get_y_size_from_errors(errors)

	mean_std_error = [[0] * y_size] * num_errors
	for i in range(num_errors):
		for j in range(y_size):
			mean_std_error[i][j] = mean_standard_deviation_error_by_num_empty_squares(grids, errors[i][j])

	return mean_std_error

def get_y_size(y):
	if hasattr(y[0], "__len__"):
		y_size = len(y[0])
	else: # y is primitive.
		y_size = 1

	return y_size

def get_y_size_from_errors(errors):
	return len(errors[0])
		
def sort_by_y_components(y):
	# The output of this function is a two-dimensuinal matrix. The first dimension represents the components of one y element and the second dimension the grid.

	if not hasattr(y[0], "__len__"): # y is primitive.
		y = [[e] for e in y]

	return np.transpose(y).tolist()

def print_loss_metric_functions(model, x, y_true):
	x = [convert_grid_for_neural_network(grid) for grid in x]

	data_evaluation = model.evaluate(x, y_true, batch_size = 1)

	print("\n\n")
	
	for i in range(len(data_evaluation)):
		print("{}: {:.3f}".format(model.metrics_names[i], data_evaluation[i]))

def print_correlation_coefficient_p_value(y_true, y_pred, y_names = None):
	y_size = get_y_size(y_true)

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("Correlation coefficient and p-value:")
	for i in range(y_size):
		print("\t{}: {}".format(y_names[i], pearsonr(y_true_components[i], y_pred_components[i])))

def print_mean_standard_deviation_errors(errors, y_names = None, error_names = None):
	num_errors = len(errors)
	y_size = get_y_size_from_errors(errors)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	mean_std = mean_standard_deviation_errors(errors)

	print("Mean and standard deviation for each error:")
	for i in range(num_errors):
		print("\t{}:".format(error_names[i]))

		for j in range(y_size):
			msd = mean_std[i][j]
			print("\t\t{}: mean error of {:.3f} and standard deviation error of {:.3f}".format(y_names[j], msd[0], msd[1]))

		print()

def print_mutiple_error_bins_data_percentage(errors, y_names = None, error_ranges = None, error_names = None, num_bins = 10):
	num_errors = len(errors)
	y_size = get_y_size_from_errors(errors)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	data_percentages_bins = mutiple_error_bins_data_percentage(errors, num_bins, error_ranges)

	print("Percentage of data which are in the follow bins:")
	for i in range(num_errors):
		print("\t{}:".format(error_names[i]))

		for j in range(y_size):
			print("\t\t{}:".format(y_names[j]))

			data_percentages, bins = data_percentages_bins[i][j]
			for k in range(len(data_percentages)):
				print("\t\t\t[{:.2f}-{:.2f}]: {:.3%}".format(bins[k], bins[k+1], data_percentages[k]))

		print()

def print_all_grids_with_result(x, y_true, y_pred, errors, y_names = None, error_names = None):
	num_errors = len(errors)
	y_size = get_y_size(y_true)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("All results (for each x, display y_true, y_pred and errors):")
	for i in range(len(x)):
		grid = x[i]

		print('\t' + '\n\t'.join(ttt.to_string(grid).split('\n'))) # Print the grid with tabulation.
		for j in range(y_size):
			print("\t{}:".format(y_names[j]))

			print("\t\ty_true: {:.2f}".format(y_true_components[j][i]))
			print("\t\ty_pred: {:.2f}".format(y_pred_components[j][i]))
			for k in range(num_errors):
				print("\t\t{}: {:.2f}".format(error_names[k], errors[k][j][i]))

		print()

def print_grid_in_error_range(x, y_true, y_pred, errors, error_range, y_names = None, error_names = None):
	num_errors = len(errors)
	y_size = get_y_size(y_true)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	y_true_components = sort_by_y_components(y_true)
	y_pred_components = sort_by_y_components(y_pred)

	print("Grids whose the error lies in [{}, {}]:".format(*error_range))
	for i in range(num_errors):
		print("\t{}:".format(error_names[i]))

		for j in range(y_size):
			print("\t\t{}:".format(y_names[j]))

			grids_in_error_range = get_grid_in_error_range(x, y_true_components[j], y_pred_components[j], errors[i][j], error_range)
			for grid, y_t, y_p, err in grids_in_error_range:
				print('\t\t\t' + '\n\t\t\t'.join(ttt.to_string(grid).split('\n'))) # Print the grid with tabulation.
				print("\t\t\ty_true: {:.2f}".format(y_t))
				print("\t\t\ty_pred: {:.2f}".format(y_p))
				print("\t\t\t{}: {:.2f}".format(y_names[j], err))

				print()

def print_mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, errors, y_names = None, error_names = None):
	num_errors = len(errors)
	y_size = get_y_size_from_errors(errors)

	if error_names == None:
		error_names = ["Error #{}".format(i + 1) for i in range(num_errors)]

	if y_names == None:
		y_names = ["Output #{}".format(i + 1) for i in range(y_size)]

	mean_std_error = mutiple_mean_standard_deviation_error_by_num_empty_squares(grids, errors)

	print("Mean and standard deviation error by number of empty squares:")
	for i in range(num_errors):
		print("\t{}:".format(error_names[i]))

		for j in range(y_size):
			print("\t\t{}:".format(y_names[j]))

			msd = mean_std_error[i][j]
			for k in range(len(msd)):
				print("\t\t\t{} empty squares: mean error of {:.3f} and standard deviation error of {:.3f}".format(k, msd[k][0], msd[k][1]))

		print()

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
	#x, y_true = get_data_for_neural_network(training_set, get_win_ratio)
	x, y_true = get_data_for_neural_network(training_set, get_win_loss_draw_ratio)
	model = create_fit_model(x, y_true, model_file_name = model_file_name)
	y_pred = model.predict([convert_grid_for_neural_network(grid) for grid in x], batch_size = 1)

	# Results
	error_function_list = [lambda y_t, y_p: list(map(lambda t, p: abs(t - p), y_t, y_p))]
	#error_ranges = [(0.0, 1.0)]
	#y_names = ["Win ratio"]
	error_ranges = [(0.0, 1.0)] * 3
	y_names = ["Win ratio", "Loss ratio", "Draw ratio"]
	error_names = ["Absolute error"]

	errors = compute_errors(model, x, y_true, y_pred, error_function_list)

	print_loss_metric_functions(model, x, y_true)
	print()
	print_correlation_coefficient_p_value(y_true, y_pred, y_names = y_names)
	print()
	print_mean_standard_deviation_errors(errors, y_names = y_names, error_names = error_names)
	print_mutiple_error_bins_data_percentage(errors, error_ranges = error_ranges, y_names = y_names, error_names = error_names)
	#print_all_grids_with_result(x, y_true, y_pred, errors, y_names = y_names, error_names = error_names)
	print_grid_in_error_range(x, y_true, y_pred, errors, (0.5, 1.0), y_names = y_names, error_names = error_names)
	print_mutiple_mean_standard_deviation_error_by_num_empty_squares(x, errors, y_names = y_names, error_names = error_names)
