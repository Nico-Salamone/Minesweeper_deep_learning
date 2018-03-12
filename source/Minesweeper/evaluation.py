import data_set as ds
from neural_network import format_data_set, get_inputs
from helpers import print_grid

from keras.models import load_model
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
import random

if __name__ == "__main__":
	seed = 42

	radius_subgrids = 2
	num_rows_grid = 10
	num_columns_grid = 10
	prob_bomb_tile = 0.3
	data_set_size = 500
	num_masked_subgrids = 20

	ds_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, radius_subgrids, prob_bomb_tile,
		data_set_size, False)
	ds_bm_file_name = "data_sets/" + ds.data_set_file_name(num_rows_grid, num_columns_grid, radius_subgrids, prob_bomb_tile,
		data_set_size, True) # 'bm' for means that the tile in the middle of the subgrids contains a bomb.
	model_file_name = "model.h5"

	random.seed(seed)

	# Load the data set.
	data_set = list(ds.read_data_set(ds_file_name))
	data_set.extend(list(ds.read_data_set(ds_bm_file_name)))

	# Format the data set.
	data_set = format_data_set(data_set, num_masked_subgrids)

	# Get the 'x' and 'y_true' vectors.
	x, y_true = get_inputs(data_set)

	# Load the model.
	model = load_model(model_file_name)

	# Evaluation.
	evaluation = model.evaluate(x, y_true)
	for i, ev in enumerate(evaluation):
		print("{}: {:.3f}".format(model.metrics_names[i], ev))

	y_pred = model.predict(x)
	print('')

	y_pred_rounded = [round(y_p[0]) for y_p in y_pred]

	true_negative, false_positive, false_negative, true_positive = confusion_matrix(y_true, y_pred_rounded).ravel()
	# 'true_positive' and 'false_negative': positive means 1 (bomb in the middle of the subgrid).
	# 'false_negative' and 'true_negative': negative means 0 (no bomb in the middle of the subgrid).
	accuracy = accuracy_score(y_true, y_pred_rounded)
	recall = recall_score(y_true, y_pred_rounded)

	print("True positive: {}\nFalse positive: {}\nFalse negative: {}\nTrue negative: {}\nAccuracy: {}\nRecall: {}\n".format(true_positive,
		false_positive, false_negative, true_negative, accuracy, recall))

	for x_t, y_t, y_p in zip(x, y_true, y_pred):
		print_grid(x_t)

		print("y_true: {}\ny_pred: {}\n".format(y_t, y_p))
