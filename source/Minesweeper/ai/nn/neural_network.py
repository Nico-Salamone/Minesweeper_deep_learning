from minesweeper.masked_grid import Tile
import ai.nn.data_set as ds
from ai.helpers import generate_random_masks, data_set_file_path, model_file_path

from keras.models import Sequential
from keras.layers import Dense
import keras.backend as K
import tensorflow as tf
import math
import random
import numpy as np

def custom_mean_squared_error(y_true, y_pred):
	"""
	Custom mean squared error. If 'y_true' is equal to 1 and 'y_pred' is smaller than 0.01, then return mean squared
	error multiplied by 100, else return mean squared error.

	:y_true: The real outputs.
	:y_pred: The outputs predicted by the neural network.
	:return: mean squared error multiplied by 100 if 'y_true' is equal to 1 and 'y_pred' is smaller than 0.01, mean
		squared error otherwise.
	"""

	mse = K.square(y_pred - y_true)
	
	return K.mean(K.switch(K.equal(y_true, 1), # If 'y_true' is equal to 1.
		K.switch(K.less(y_pred, 0.01), # If 'y_pred' is smaller than 0.01.
			mse*100, # Then.
			mse), # Else.
		mse), axis=-1) # Else.

def create_model_1(num_tiles_subgrids):
	"""
	Create and compile the model 1. The model 1 is a simple model composed of three hidden layers containing 300, 256
	and 128 neurons respectively.

	:num_tiles_subgrids: The number of tiles of subgrids.
	:return: The model 1 compiled.
	"""

	model = Sequential()

	model.add(Dense(300, activation='relu', kernel_initializer='random_uniform', input_dim=num_tiles_subgrids))
	model.add(Dense(256, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(128, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(1, activation='sigmoid', kernel_initializer='random_uniform'))

	model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mean_squared_error', 'mean_absolute_error',
		'accuracy'])

	return model

def create_model_2(num_tiles_subgrids):
	"""
	Create and compile the model 2. The model 2 is a complex model composed of four hidden layers containing 600, 1024,
	512 and 256 neurons respectively.

	:num_tiles_subgrids: The number of tiles of subgrids.
	:return: The model 2 compiled.
	"""

	model = Sequential()

	model.add(Dense(600, activation='relu', kernel_initializer='random_uniform', input_dim=num_tiles_subgrids))
	model.add(Dense(1024, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(512, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(256, activation='relu', kernel_initializer='random_uniform'))
	model.add(Dense(1, activation='sigmoid', kernel_initializer='random_uniform'))

	model.compile(loss='mean_squared_error', optimizer='rmsprop', metrics=['mean_squared_error', 'mean_absolute_error',
		'accuracy'])

	return model

def format_data_set(data_set, num_masked_subgrids, with_flags=False):
	"""
	Format the data set for the neural network. For each subgrid of the data set, this function generates
	'num_masked_subgrids' subgrids with a random mask.

	:data_set: The data set.
	:num_masked_subgrids: The number of subgrids with a mask to generate for each subgrid of the data set.
	:with_flags: If True, then the tiles of masked subgrids containing a bomb will contain a flag.
	:return: the formatted data set.
	"""

	if with_flags:
		mask_bomb_tiles = False
	else:
		mask_bomb_tiles = True

	num_tiles = len(data_set[0])
	edge_size = int(math.sqrt(num_tiles))
	radius = int(edge_size / 2)
	mid_tile_pos = (radius * edge_size) + radius

	formatted_data_set = []
	for subgrid in data_set:
		mid_tile = subgrid[mid_tile_pos]
		y_true_subgrid = 1 if (mid_tile == Tile.BOMB) else 0

		masked_subgrids = generate_random_masks(subgrid, num_masked_subgrids, mask_middle_tile=True,
			mask_bomb_tiles=mask_bomb_tiles, flag_bomb_tiles=with_flags)
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

	subgrid_radius = 2
	edge_size_subgrids = (subgrid_radius * 2) + 1
	num_tiles_subgrids = edge_size_subgrids ** 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	num_no_bm_subgrids = 500000
	num_bm_subgrids = 500000
	# 'bm' means that the tile in the middle of the subgrids contains a bomb.
	num_masked_subgrids = 10
	with_flags = True

	ds_no_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, False)
	ds_bm_file_name = data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, True)
	# 'bm' means that the tile in the middle of the subgrids contains a bomb.
	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius,
		with_flags=with_flags)

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
	data_set = format_data_set(data_set, num_masked_subgrids, with_flags=with_flags)
	print("Data set formatted.")

	# Shuffle the data set.
	#random.shuffle(data_set)
	#print("Data set shuffled.")

	# Get the 'x' and 'y_true' vectors.
	x, y_true = get_inputs_real_outputs(data_set)
	print("Inputs and real outputs extracted.")

	# Create the model.
	model = create_model_2(num_tiles_subgrids) # The more complex model.

	# Train the model.
	#model.fit(x, y_true, epochs=1, batch_size=10)
	model.fit(x, y_true, epochs=5, batch_size=2000)
	print("Neural network trained.")

	# Save the model.
	model.save(model_file_name)
