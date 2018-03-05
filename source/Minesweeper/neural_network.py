from minesweeper.grid import Tile
import data_set as ds
from helpers import generate_random_masks, print_grid

from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model
from keras.optimizers import Adam
import random
import numpy as np
import operator
from functools import reduce

def create_model(num_tiles_subgrids):
	"""
	Create and compile a model.

	:num_tiles_subgrids: The number of tiles of subgrids.
	:return: The compiled model.
	"""

	model = Sequential()

	model.add(Dense(300, activation='relu', kernel_initializer='uniform', input_dim=num_tiles_subgrids))
	model.add(Dense(256, activation='relu', kernel_initializer='uniform'))
	model.add(Dense(128, activation='relu', kernel_initializer='uniform'))
	model.add(Dense(1, activation='sigmoid', kernel_initializer='uniform'))

	#optimizer = Adam(lr=0.0001)
	optimizer = 'rmsprop'
	model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mean_squared_error', 'mean_absolute_error', 'accuracy'])

	return model

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

	file_name = "data_sets/" + ds.get_file_name(radius_subgrids, num_rows_grid, num_columns_grid, num_bombs_grid, data_set_size)

	random.seed(seed)
	np.random.seed(int(seed)) # Makes Tensorflow deterministic.

	# Load the data set.
	data_set = list(ds.read_data_set(file_name))

	# Create the model.
	model = create_model(num_tiles_subgrids)

	# Create 'x' and 'y_true' vectors
	x = []
	y_true = []
	for subgrid in data_set:
		x_subgrid = generate_random_masks(subgrid, 5, True)

		mid_tile = subgrid[mid_tile_pos]
		y_true_subgrid = [1 if (mid_tile == Tile.BOMB) else 0] * len(x_subgrid)

		x.append(x_subgrid)
		y_true.append(y_true_subgrid)

	# Train the model.
	for i, (x_subgrid, y_true_subgrid) in enumerate(zip(x, y_true)):
		model.fit(x_subgrid, y_true_subgrid, epochs=1, batch_size=10)
		print("{}/{} subgrids done!".format(i, data_set_size))
		break

	# Flatten 'x' and 'y_true' vectors.
	x = reduce(operator.add, x)
	y_true = reduce(operator.add, y_true)

	# Evaluation.
	evaluation = model.evaluate(x, y_true)
	for i, ev in enumerate(evaluation):
		print("{}: {:.3f}".format(model.metrics_names[i], ev))

	y_pred = model.predict(x)
	print('')

	true_positive = 0 # Positive means 1 (bomb in the middle of the subgrid).
	false_positive = 0
	false_negative = 0 # Negative means 0 (no bomb in the middle of the subgrid).
	true_negative = 0
	for y_t, y_p in zip(y_true, y_pred):
		y_p = round(y_p[0])

		if y_p == 1:
			if y_t == 1:
				true_positive += 1
			else: # 'y_t' is equals to 0.
				false_positive += 1
		else: # 'y_p' is equals to 0.
			if y_t == 1:
				false_negative += 1
			else: # 'y_t' is equals to 0.
				true_negative += 1

	condition_positive = true_positive + false_negative
	condition_negative = false_positive + true_negative
	accuracy = (true_positive + true_negative) / (condition_positive + condition_negative)
	recall = true_positive /  condition_positive

	print("True positive: {}\nFalse positive: {}\nFalse negative: {}\nTrue negative: {}\nAccuracy: {}\nRecall: {}\n".format(true_positive, false_positive,
		false_negative, true_negative, accuracy, recall))

	for x_t, y_t, y_p in zip(x, y_true, y_pred):
		print_grid(x_t)

		print("y_true: {}\ny_pred: {}\n".format(y_t, y_p))
