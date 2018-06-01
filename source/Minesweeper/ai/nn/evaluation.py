import ai.nn.data_set as ds
from ai.nn.neural_network import format_data_set, get_inputs_real_outputs
from ai.helpers import count_num_masked_tiles, print_grid, data_set_file_path, model_file_path

from keras.models import load_model
import sklearn.metrics as skmet
import numpy as np
import random

def print_loss_metric_functions(model, x, y_true):
	"""
	Print the results of loss and metric functions.

	:model: The model.
	:x: The inputs.
	:y_true: The real outputs.
	"""

	evaluation = model.evaluate(x, y_true, verbose=0)

	print("Results of loss and metric functions:")
	for i, ev in enumerate(evaluation):
		print("\t{}: {:.3f}".format(model.metrics_names[i], ev))

def pivot_value(y_pred, no_bm_subgrids_rate):
	"""
	Compute the pivot value (used in the 'confusion_matrix' function). It is the value that separates 'y_pred' so that
	'no_bm_subgrids_rate' of 'y_pred' is lower than the pivot value (that is the percentile
	'no_bm_subgrids_rate' * 100). These 'y_pred' are predictions that we consider to be subgrids where the middle tile
	does not contain a bomb.

	:y_pred: The outputs predicted by the neural network.
	:no_bm_subgrids_rate: The rate (percentage, ratio) of subgrids whose the tile in the middfle does not contain a
		bomb of the training set.
	:return: The pivot value.
	"""

	return np.percentile(y_pred, (no_bm_subgrids_rate * 100))

def confusion_matrix(y_true, y_pred, pivot_value=0.5):
	"""
	Compute the confusion matrix.

	True positives and false negatives: positives means 1 (bomb in the middle of the subgrid).
	False negatives and true negatives: negatives means 0 (no bomb in the middle of the subgrid).

	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:pivot_value: The pivot value.
	:return: The confusion matrix. This is an array with four components. The first component is the number of true
		negatives, the second is the number of the false positives, the third is the number of the false negatives and
		the fourth is the number of the true positives.
	"""
	
	round_y_pred = lambda y_p: 0 if (y_p <= pivot_value) else 1
	y_pred_rounded = [round_y_pred(y_p) for y_p in y_pred]

	return skmet.confusion_matrix(y_true, y_pred_rounded).ravel()

def accuracy_recall_specificity(conf_mat):
	"""
	Compute the accuracy, the recall and the specificity.

	:conf_mat: The confusion matrix.
	:return: The accuracy, the recall and the specificity.
	"""

	true_negatives, false_positives, false_negatives, true_positives = conf_mat

	positives = true_positives + false_negatives
	negatives = true_negatives + false_positives

	accuracy = (true_positives + true_negatives) / (positives + negatives)
	recall = true_positives / positives
	specificity = true_negatives / negatives

	return accuracy, recall, specificity

def x_confusion_matrix(x, y_true, y_pred, pivot_value=0.5):
	"""
	Distributes the inputs to the tiles of the confusion matrix.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:pivot_value: The pivot value.
	:return: The inputs distributed in the confusion matrix. This is an array with four components. The first component
		contains the inputs lied in the true negative tile, the second component contains the inputs lied in the false
		positive tile, the third component contains the inputs lied in the false negative tile and the fourth component
		contains the inputs lied in the true positive tile.
	"""
	
	round_y_pred = lambda y_p: 0 if (y_p <= pivot_value) else 1
	y_pred_rounded = [round_y_pred(y_p) for y_p in y_pred]

	true_negatives = []
	false_positives = []
	false_negatives = []
	true_positives = []
	for x_t, y_t, y_p in zip(x, y_true, y_pred_rounded):
		if y_t == 1:
			if y_p == 1:
				# True positive.
				
				true_positives.append(x_t)
			else: # 'y_p' = 0.
				# False negative.
				
				false_negatives.append(x_t)
		else: # 'y_t' = 0.
			if y_p == 1:
				# False positive.
				
				false_positives.append(x_t)
			else: # 'y_p' = 0.
				# True negative.
				
				true_negatives.append(x_t)

	return true_negatives, false_positives, false_negatives, true_positives

def num_masked_tiles_confusion_matrix(x, y_true, y_pred, pivot_value=0.5):
	"""
	Distributes the inputs to the tiles of the confusion matrix and compute for each tile of this matrix a list of the
	numbers of masked tiles of subgrids lied in this tile.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:pivot_value: The pivot value.
	:return: A list of the numbers of masked tiles lied in each tile of the confusion matrix. This is an array with
		four components. The first component contains a list of the numbers of masked tiles of subgrids lied in the
		true negative tile, the second component contains a list of the numbers of masked tiles of subgrids lied in the
		false positive tile, the third component contains a list of the numbers of masked tiles of subgrids lied in the
		false negative tile and the fourth component contains a list of the numbers of masked tiles of subgrids lied in
		the true positive tile.
	"""

	x_conf_mat = x_confusion_matrix(x, y_true, y_pred, pivot_value)

	num_masked_tiles_conf_mat = []
	for i, cf_tile in enumerate(x_conf_mat):
		num_masked_tiles_conf_mat.append([count_num_masked_tiles(x_t) for x_t in x_conf_mat[i]])

	return num_masked_tiles_conf_mat

def errors(y_true, y_pred, error_func):
	"""
	Compute the errors.

	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:error_func: The error function. It takes one real output and one single output predicted as input and return a
		error from these values.
	:return: A list of errors.
	"""

	return [error_func(y_t, y_p) for y_t, y_p in zip(y_true, y_pred)]

def histogram_percentage(err, num_bins=10, error_range=None):
	"""
	Compute the percentage of counts of the histogram of the errors (error distribution).

	:err: The errors.
	:num_bins: The number of bins.
	:error_range: The error range.
	:return: The percentage of counts of the histogram of the errors and the bins.
	"""

	if error_range == None:
		error_range = (min(err), max(err))

	counts, bins = np.histogram(np.array(err), bins=num_bins, range=error_range)
	counts = counts.astype(float)

	n = len(err)
	perc_counts = [(c / n) for c in counts]

	return (perc_counts, bins)

def print_histogram_percentage(hist_perc):
	"""
	Print the histogram percentage.

	:hist_perc: The histogram percentage.
	"""

	perc_counts, bins = hist_perc

	print("Histogram percentage:")
	for i, pc in enumerate(perc_counts):
		print("\t[{:.2f}-{:.2f}]: {:.3%}".format(bins[i], bins[i+1], pc))

def extrat_data_error_range(x, y_true, y_pred, err, error_range):
	"""
	Extract the data within a range.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:err: The errors.
	:error_range: The error range.
	:return: A list of inputs, real outputs, ouputs predicted and erros.
	"""

	min_value = error_range[0]
	max_value = error_range[1]

	data_within_range = []
	for x_t, y_t, y_p, e in zip(x, y_true, y_pred, err):
		if min_value <= e <= max_value:
			data_within_range.append((x_t, y_t, y_p, e))

	return data_within_range

def print_x_y_true_y_pred_err(x, y_true, y_pred, err=None):
	"""
	Print for each input the real output, the output predicted by the neural network and the error.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:err: The errors.
	"""

	print_msg = "Inputs, real outputs, outputs predicted and errors:"

	if err == None:
		print_msg = "Inputs, real outputs and outputs predicted:"
		err = [None] * len(x)

	print(print_msg)
	for x_t, y_t, y_p, e in zip(x, y_true, y_pred, err):
		print_grid(x_t)
		print("y_true: {}\ny_pred: {}".format(y_t, y_p))
		if e:
			print("err: {}".format(e))

		print('')

if __name__ == "__main__":
	seed = 42

	subgrid_radius = 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	num_no_bm_subgrids = 5000
	num_bm_subgrids = 5000
	# 'bm' means that the tile in the middle of the subgrids contains a bomb.
	num_masked_subgrids = 10
	with_flags = True

	ds_no_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, False)
	ds_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, True)
	# 'bm' means that the tile in the middle of the subgrids contains a bomb.
	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius,
		with_flags=with_flags)

	random.seed(seed)

	# Load the data set.
	data_set_gen = ds.read_data_set(ds_no_bm_file_name)
	for i in range(int(ds.SIZE / 2)): next(data_set_gen) # Skip the half of the data set.
	data_set = [next(data_set_gen) for i in range(num_no_bm_subgrids)]

	data_set_gen = ds.read_data_set(ds_bm_file_name)
	for i in range(int(ds.SIZE / 2)): next(data_set_gen) # Skip the half of the data set.
	data_set.extend([next(data_set_gen) for i in range(num_bm_subgrids)])
	print("Data set loaded.")

	# Format the data set.
	data_set = format_data_set(data_set, num_masked_subgrids, with_flags=with_flags)
	print("Data set formatted.")

	# Get the 'x' and 'y_true' vectors.
	x, y_true = get_inputs_real_outputs(data_set)
	print("Inputs and real outputs extracted.")

	# Load the model.
	model = load_model(model_file_name)
	# If 'custom_mean_squared_error' custom loss is used.
	#from ai.nn.neural_network import custom_mean_squared_error
	#model = load_model(model_file_name, custom_objects={'custom_mean_squared_error': custom_mean_squared_error})

	# Evaluation.
	y_pred = model.predict(x)
	y_pred = [y_p[0] for y_p in y_pred]

	error_func = lambda y_t, y_p: abs(y_t - y_p)
	err = errors(y_true, y_pred, error_func)
	print("Errors computed.\n\n\n")

	# Print the results of Keras metrics.
	print_loss_metric_functions(model, x, y_true)
	print('')

	# Print the confusion matrix and the results of related metrics.
	pivot = pivot_value(y_pred, 0.5)
	conf_mat = confusion_matrix(y_true, y_pred, pivot)
	conf_mat_names = ["True negatives", "False positives", "False negatives", "True positives"]
	accuracy, recall, specificity = accuracy_recall_specificity(conf_mat)
	num_masked_tiles_conf_mat = num_masked_tiles_confusion_matrix(x, y_true, y_pred, pivot)
	print("Confusion matrix, accuracy, recall and specificity:")
	print("\tPivot: {}".format(pivot))
	for cf_name, cf_tile, ct_nmt_tile in zip(conf_mat_names, conf_mat, num_masked_tiles_conf_mat):
		print("\t{}: {}\n\t\tNumber of masked tiles:\n\t\t\tMin: {}\n\t\t\tMax: {}\n\t\t\tMean: {:.3f}" \
			"\n\t\t\tPercentile 25: {}\n\t\t\tPercentile 50 (median): {}\n\t\t\tPercentile 75: {}".format(cf_name,
				cf_tile, min(ct_nmt_tile), max(ct_nmt_tile), np.mean(ct_nmt_tile), np.percentile(ct_nmt_tile, 25),
				np.percentile(ct_nmt_tile, 50), np.percentile(ct_nmt_tile, 75)))
	print("\tAccuracy: {}\n\tRecall: {}\n\tSpecificity: {}\n".format(accuracy, recall, specificity))

	# Print the error distribution.
	hist_perc = histogram_percentage(err, 10, (0.0, 1.0))
	print_histogram_percentage(hist_perc)
	print('')

	# Print for each input the real output, the output predicted by the neural network and the error.
	#print_x_y_true_y_pred_err(x, y_true, y_pred)

	# Among the bad predictions, print for each one the input, the real output, the output predicted by the neural
	# network and the error.
	data_within_range = extrat_data_error_range(x, y_true, y_pred, err, (0.6, 1.0))
	data_within_range_trans = np.transpose(data_within_range).tolist()
	# 'data_within_range_trans[0]' corresponds to 'x'.
	# 'data_within_range_trans[1]' corresponds to 'y_true'.
	# 'data_within_range_trans[2]' corresponds to 'y_pred'.
	# 'data_within_range_trans[3]' corresponds to 'err'.
	print_x_y_true_y_pred_err(data_within_range_trans[0], data_within_range_trans[1], data_within_range_trans[2])
