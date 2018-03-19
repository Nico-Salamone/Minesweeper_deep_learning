import ai.data_set as ds
from ai.neural_network import format_data_set, get_inputs_real_outputs
from ai.helpers import print_grid

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

def confusion_matrix(y_true, y_pred):
	"""
	Compute the confusion matrix.

	True positives and false negatives: positives means 1 (bomb in the middle of the subgrid).
	False negatives and true negatives: negatives means 0 (no bomb in the middle of the subgrid).

	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:return: The confusion matrix. This is a four-dimensional tuple. The first component is the number of true
		negatives, the second is the number of the false positives, the third is the number of the false negatives and
		the fourth is the number of the true positives.
	"""

	y_pred_rounded = [round(y_p) for y_p in y_pred]

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

def histogram_percentage(errors, num_bins=10, error_range=None):
	"""
	Compute the percentage of counts of the histogram of the errors.

	:errors: The errors.
	:num_bins: The number of bins.
	:error_range: The error range.
	:return: The percentage of counts of the histogram of the errors and the bins.
	"""

	if error_range == None:
		error_range = (min(errors), max(errors))

	counts, bins = np.histogram(np.array(errors), bins=num_bins, range=error_range)
	counts = counts.astype(float)

	n = len(errors)
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

def extrat_data_error_range(x, y_true, y_pred, errors, error_range):
	"""
	Extract the data within a range.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:errors: The errors.
	:error_range: The error range.
	:return: A list of inputs, real outputs, ouputs predicted and erros.
	"""

	min_value = error_range[0]
	max_value = error_range[1]

	data_within_range = []
	for x_t, y_t, y_p, e in zip(x, y_true, y_pred, errors):
		if min_value <= e <= max_value:
			data_within_range.append((x_t, y_t, y_p, e))

	return data_within_range

def print_x_y_true_y_pred_err(x, y_true, y_pred, errors=None):
	"""
	Print for each input the real output, the output predicted by the neural network and the error.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:errors: The errors.
	"""

	print_msg = "Inputs, real outputs, outputs predicted and errors:"

	if errors == None:
		print_msg = "Inputs, real outputs and outputs predicted:"
		errors = [None] * len(x)

	print(print_msg)
	for x_t, y_t, y_p, e in zip(x, y_true, y_pred, errors):
		print_grid(x_t)
		print("y_true: {}\ny_pred: {}".format(y_t, y_p))
		if e:
			print("err: {}".format(e))

		print('')

if __name__ == "__main__":
	seed = 42

	radius_subgrids = 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	data_set_size = 500
	num_masked_subgrids = 20

	ds_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid,
		radius_subgrids, data_set_size, False)
	ds_bm_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid,
		radius_subgrids, data_set_size, True)
	# 'bm' for means that the tile in the middle of the subgrids contains a bomb.
	model_file_name = "model.h5"

	random.seed(seed)

	# Load the data set.
	data_set = list(ds.read_data_set(ds_file_name))
	data_set.extend(list(ds.read_data_set(ds_bm_file_name)))
	print("Data set loaded.")

	# Format the data set.
	data_set = format_data_set(data_set, num_masked_subgrids)
	print("Data set formatted.")

	# Get the 'x' and 'y_true' vectors.
	x, y_true = get_inputs_real_outputs(data_set)
	print("Inputs and reak outputs extracted.\n\n\n")

	# Load the model.
	model = load_model(model_file_name)

	# Evaluation.
	y_pred = model.predict(x)
	y_pred = [y_p[0] for y_p in y_pred]

	error_func = lambda y_t, y_p: abs(y_t - y_p)
	errors = errors(y_true, y_pred, error_func)

	print_loss_metric_functions(model, x, y_true)
	print('')

	conf_mat = confusion_matrix(y_true, y_pred)
	true_negatives, false_positives, false_negatives, true_positives = conf_mat
	accuracy, recall, specificity = accuracy_recall_specificity(conf_mat)
	print("Confusion matrix, accuracy, recall and specificity:")
	print("\tTrue positives: {}\n\tFalse positives: {}\n\tFalse negatives: {}\n\tTrue negatives: {}\n\t" \
		"Accuracy: {}\n\tRecall: {}\n\tSpecificity: {}\n".format(true_positives, false_positives, false_negatives,
		true_negatives, accuracy, recall, specificity))

	hist_perc = histogram_percentage(errors, 10, (0.0, 1.0))
	print_histogram_percentage(hist_perc)
	print('')

	#print_x_y_true_y_pred_err(x, y_true, y_pred)

	data_within_range = extrat_data_error_range(x, y_true, y_pred, errors, (0.6, 1.0))
	data_within_range_trans = np.transpose(data_within_range).tolist()
	# 'data_within_range_trans[0]' corresponds to 'x'.
	# 'data_within_range_trans[1]' corresponds to 'y_true'.
	# 'data_within_range_trans[2]' corresponds to 'y_pred'.
	# 'data_within_range_trans[3]' corresponds to 'errors'.
	print_x_y_true_y_pred_err(data_within_range_trans[0], data_within_range_trans[1], data_within_range_trans[2])
