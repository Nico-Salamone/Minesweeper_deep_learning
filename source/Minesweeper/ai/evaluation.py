import ai.data_set as ds
from ai.neural_network import format_data_set, get_inputs
from ai.helpers import print_grid

from keras.models import load_model
import sklearn.metrics as skmet
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
		print("{}: {:.3f}".format(model.metrics_names[i], ev))

def confusion_matrix(y_true, y_pred):
	"""
	Compute the confusion matrix.

	True positives and false negatives: positives means 1 (bomb in the middle of the subgrid).
	False negatives and true negatives: negatives means 0 (no bomb in the middle of the subgrid).

	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:return: The confusion matrix. This is a four-dimensional tuple. The first component is the number of true negatives,
		the second is the number of the false positives, the third is the number of the false negatives and the fourth is
		the number of the true positives.
	"""

	y_pred_rounded = [round(y_p[0]) for y_p in y_pred]

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

def print_x_y_true_x_pred(x, y_true, x_pred):
	"""
	Print for each input the real outputs and the outputs predicted by the neural network.

	:x: The inputs.
	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	"""

	print("All results (for each input, display the real outputs and the outputs predicted by the neural network):")
	for x_t, y_t, y_p in zip(x, y_true, y_pred):
		print_grid(x_t)

		print("y_true: {}\ny_pred: {}\n".format(y_t, y_p))

if __name__ == "__main__":
	seed = 42

	radius_subgrids = 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	data_set_size = 500
	num_masked_subgrids = 20

	ds_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids,
			data_set_size, False)
	ds_bm_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids,
			data_set_size, True) # 'bm' for means that the tile in the middle of the subgrids contains a bomb.
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
	x, y_true = get_inputs(data_set)
	print("Inputs and outputs extracted.\n\n\n")

	# Load the model.
	model = load_model(model_file_name)

	# Evaluation.
	y_pred = model.predict(x)

	print_loss_metric_functions(model, x, y_true)
	print('')

	conf_mat = confusion_matrix(y_true, y_pred)
	true_negatives, false_positives, false_negatives, true_positives = conf_mat
	accuracy, recall, specificity = accuracy_recall_specificity(conf_mat)
	print("Confusion matrix, accuracy, recall and specificity:")
	print("True positives: {}\nFalse positives: {}\nFalse negatives: {}\nTrue negatives: {}\nAccuracy: {}\nRecall: {}\n"
		"Specificity: {}\n".format(true_positives, false_positives, false_negatives, true_negatives, accuracy, recall,
			specificity))

	print_x_y_true_x_pred(x, y_true, y_pred)
