from minesweeper.grid import Tile
import data_set as ds
from helpers import generate_random_masks

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import random
import numpy as np

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

	ds_file_name = "data_sets/" + ds.data_set_file_name(radius_subgrids, num_rows_grid, num_columns_grid, num_bombs_grid, data_set_size)
	model_file_name = "model.h5"

	random.seed(seed)
	np.random.seed(int(seed)) # Makes Tensorflow deterministic.

	# Load the data set.
	data_set = list(ds.read_data_set(ds_file_name))

	# Create the model.
	model = create_model(num_tiles_subgrids)

	# Create the 'x' and 'y_true' vectors
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

	# Save the model.
	model.save(model_file_name)
