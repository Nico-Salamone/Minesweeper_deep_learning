from minesweeper.grid import Tile
import data_set as ds
from helpers import generate_random_masks, print_grid

from keras.models import load_model
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score
import random

if __name__ == "__main__":
	seed = 42

	radius_subgrids = 2
	edge_size_subgrids = (radius_subgrids * 2) + 1
	num_tiles_subgrids = edge_size_subgrids ** 2
	mid_tile_pos = (radius_subgrids * edge_size_subgrids) + radius_subgrids
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 40
	data_set_size = 1000

	ds_file_name = "data_sets/" + ds.data_set_file_name(radius_subgrids, num_rows_grid, num_columns_grid, num_bombs_grid, data_set_size)
	model_file_name = "model.h5"

	random.seed(seed)

	# Load the data set.
	data_set = list(ds.read_data_set(ds_file_name))

	# Load the model.
	model = load_model(model_file_name)

	# Create the 'x' and 'y_true' vectors
	x = []
	y_true = []
	for subgrid in data_set:
		x_subgrid = generate_random_masks(subgrid, 5, True)

		mid_tile = subgrid[mid_tile_pos]
		y_true_subgrid = [1 if (mid_tile == Tile.BOMB) else 0] * len(x_subgrid)

		x.extend(x_subgrid)
		y_true.extend(y_true_subgrid)

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
