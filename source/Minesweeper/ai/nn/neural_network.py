from minesweeper.masked_grid import Tile
import ai.nn.data_set as ds
from ai.helpers import generate_random_masks, data_set_file_path, model_file_path

from keras.models import Sequential
from keras.layers import Dense
import tensorflow as tf
import math
import random
import numpy as np

def create_model(num_tiles_subgrids):
	"""
	Create and compile a model.

	:num_tiles_subgrids: The number of tiles of subgrids.
	:return: The compiled model.
	"""

	model = Sequential()

	model.add(Dense(300, activation='relu', kernel_initializer='random_uniform', input_dim=num_tiles_subgrids))
	model.add(Dense(256, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(128, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(1, activation='sigmoid', kernel_initializer='random_uniform'))

	#from keras.optimizers import Adam
	#optimizer = Adam(lr=0.0001)
	optimizer = 'rmsprop'
	model.compile(loss='mean_squared_error', optimizer=optimizer, metrics=['mean_squared_error', 'mean_absolute_error',
		'accuracy'])

	return model

def format_data_set(data_set, num_masked_subgrids):
	"""
	Format the data set for the neural network. For each subgrid of the data set, this function generates
	'num_masked_subgrids' subgrids with a random mask.

	:data_set: The data set.
	:num_masked_subgrids: The number of subgrids with a mask to generate for each subgrid of the data set.
	:return: the formatted data set.
	"""

	num_tiles = len(data_set[0])
	edge_size = int(math.sqrt(num_tiles))
	radius = int(edge_size / 2)
	mid_tile_pos = (radius * edge_size) + radius

	formatted_data_set = []
	for subgrid in data_set:
		mid_tile = subgrid[mid_tile_pos]
		y_true_subgrid = 1 if (mid_tile == Tile.BOMB) else 0

		masked_subgrids = generate_random_masks(subgrid, num_masked_subgrids, True, True)
		formatted_data_set.extend([(msg, y_true_subgrid) for msg in masked_subgrids])

	return formatted_data_set

def get_inputs_real_outputs(data_set):
	"""
	Get the inputs and the real outputs of the neural network ('x' and 'y_true').

	:data_set: The formatted data set.
	:return: The inputs and the real outputs of the neural network ('x' and 'y_true').
	"""

	data_set_trans = np.transpose(data_set)
	x = list(data_set_trans[0])
	y_true = list(data_set_trans[1])

	return x, y_true

if __name__ == "__main__":
	seed = 42

	radius_subgrids = 2
	edge_size_subgrids = (radius_subgrids * 2) + 1
	num_tiles_subgrids = edge_size_subgrids ** 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	num_no_bm_subgrids = 50000
	num_bm_subgrids = 50000
	# 'bm' for means that the tile in the middle of the subgrids contains a bomb.
	num_masked_subgrids = 10

	ds_no_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids, False)
	ds_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids, True)
	# 'bm' for means that the tile in the middle of the subgrids contains a bomb.
	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids)

	random.seed(seed)
	np.random.seed(int(seed)) # Makes Keras deterministic.
	tf.set_random_seed(seed) # Makes TensorFlow deterministic.

	# Load the data set.
	data_set_gen = ds.read_data_set(ds_no_bm_file_name)
	data_set = [next(data_set_gen) for i in range(num_no_bm_subgrids)]

	data_set_gen = ds.read_data_set(ds_bm_file_name)
	data_set.extend([next(data_set_gen) for i in range(num_bm_subgrids)])
	print("Data set loaded.")

	# Format the data set.
	data_set = format_data_set(data_set, num_masked_subgrids)
	print("Data set formatted.")

	# Shuffle the data set.
	#random.shuffle(data_set)
	#print("Data set shuffled.")

	# Get the 'x' and 'y_true' vectors.
	x, y_true = get_inputs_real_outputs(data_set)
	print("Inputs and real outputs extracted.")

	# Create the model.
	model = create_model(num_tiles_subgrids)

	# Train the model.
	model.fit(x, y_true, epochs=1, batch_size=10)
	print("Neural network trained.")

	# Save the model.
	model.save(model_file_name)
