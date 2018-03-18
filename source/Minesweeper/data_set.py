from minesweeper.grid_generation import generate_subgrid
from helpers import to_value_list

import random
import csv

def generate_data_set(radius_subgrids, bomb_middle_tile, num_rows_grid, num_columns_grid, num_bombs_grid, size, seed=None):
	"""
	Generate a random data set of subgrids.

	:radius_subgrids: The radius of the subgrids. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:bomb_middle_tile: If True, then the tile in the middle of the grid will contain a bomb. If False, then this tile will
		not contain a bomb.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the original grid.
	:size: The size of data set.
	:seed: The seed.
	:return: A generator of the data set of subgrids.
	"""

	random.seed(seed)

	return (generate_subgrid(radius_subgrids, bomb_middle_tile, num_rows_grid, num_columns_grid, num_bombs_grid)
		for i in range(size))

def write_data_set(data_set, file_name):
	"""
	Write a subgrid data set.

	:data_set: A subgrid data set.
	:file_name: The file name.
	"""

	with open(file_name, 'w', newline='') as file:
		csv_writer = csv.writer(file, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)

		for subgrid in data_set:
			csv_writer.writerow(to_value_list(subgrid))

def read_data_set(file_name):
	"""
	Read a data set of subgrids.

	:file_name: The file name.
	:return: A generator of the data set of subgrids (a list of tile values, that is an one-dimensional grid).
	"""

	with open(file_name, newline='') as file:
		csv_reader = csv.reader(file, delimiter=';', quotechar='\"')

		for row in csv_reader:
			yield [int(tile) for tile in row]

	return

def data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids, data_set_size, bomb_middle_tile):
	"""
	Get the file name for the data set folling parameters.

	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:radius_subgrids: The radius of subgrids. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:data_set_size: The size of data set.
	:bomb_middle_tile: If True, then the tile in the middle of the subgrids contains a bomb. If False, then this tile does
		not contain a bomb.
	:return: The file name.
	"""

	return "data_set_{}ro_{}c_{}b_{}ra_{}sb_{}bm.csv".format(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids,
		data_set_size, bomb_middle_tile)

if __name__ == "__main__":
	radius_subgrids = 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10

	data_set_size = 500
	seed = 42

	bomb_middle_tile_list = [False, True]
	for bomb_middle_tile in bomb_middle_tile_list:
		file_name = "data_sets/" + data_set_file_name(num_rows_grid, num_columns_grid, num_bombs_grid, radius_subgrids,
			data_set_size, bomb_middle_tile)

		data_set = generate_data_set(radius_subgrids, bomb_middle_tile, num_rows_grid, num_columns_grid, num_bombs_grid,
			data_set_size, seed)

		write_data_set(data_set, file_name)

		"""
		data_set = read_data_set(file_name)

		from helpers import print_grid
		for subgrid in data_set:
			print_grid(subgrid)
			print('')
		"""
