#from grid import Tile, Grid
#from masked_grid import MaskedTile, MaskedGrid
from minesweeper.grid_generation import generate_subgrid
from helpers import to_value_list

import random
import csv

def generate_data_set(radius_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid, size, seed=None):
	"""
	Generate a random data set of subgrids.

	:radius_subgrid: The radius of the subgrid. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:size: The size of data set.
	:seed: The seed.
	:return: The data set of subgrids.
	"""

	random.seed(seed)

	return [generate_subgrid(radius_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid) for i in range(size)]

def write_data_set(data_set, file_name):
	"""
	Write a subgrid data set.

	:data_set: A subgrid data set.
	:file_name: The file name.
	"""

	with open(file_name, 'w', newline = '') as file:
		csv_writer = csv.writer(file, delimiter = ';', quotechar = '\"', quoting = csv.QUOTE_MINIMAL)

		for subgrid in data_set:
			csv_writer.writerow(to_value_list(subgrid))

def read_data_set(file_name):
	"""
	Read a subgrid data set.

	:file_name: The file name.
	:return: The subgrid data set.
	"""

	data_set = []
	with open(file_name, newline = '') as file:
		csv_reader = csv.reader(file, delimiter = ';', quotechar = '\"')

		for row in csv_reader:
			data_set.append([int(tile) for tile in row])

	return data_set

if __name__ == "__main__":
	radius_subgrid = 2
	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10

	data_set_size = 100000
	seed = 42

	file_name = "data_set_{}ra_{}ro_{}c_{}b_{}sb.csv".format(radius_subgrid, num_rows_grid, num_columns_grid,
		num_bombs_grid, data_set_size)

	data_set = generate_data_set(radius_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid,
		data_set_size, seed)

	write_data_set(data_set, file_name)
	data_set = read_data_set(file_name)

	"""
	for subgrid in data_set:
		print(subgrid)
	"""
