from minesweeper.grid import Grid, get_positions
from minesweeper.masked_grid import MaskedGrid

import random
import numpy.random

def generate_masked_grid(num_rows, num_columns, num_bombs):
	"""
	Generate a random grid with mask. This function inserts 'num_bombs' at random positions.

	:num_rows: The number of rows of the grid.
	:num_columns: The number of columns of the grid.
	:num_bombs: The number of bombs.
	:return: A random grid with mask.
	"""

	pos_list = get_positions(num_rows, num_columns)
	bomb_position_list = random.sample(pos_list, num_bombs)

	return MaskedGrid(num_rows, num_columns, bomb_position_list)

def generate_subgrid(subgrid_radius, bomb_middle_tile, num_rows_grid, num_columns_grid, num_bombs_grid):
	"""
	Generate a random subgrid. This function generates a "good" number of bombs and the "good" thickness of walls
	("good" for realistic).

	:subgrid_radius: The radius of the subgrid. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:bomb_middle_tile: If True, then the tile in the middle of the grid will contain a bomb. If False, then this tile
		will not contain a bomb.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the original grid.
	:return: A random subgrid.
	"""

	# This funtion generates a (('num_rows_subgrid' + 2) x ('num_columns_subgrid' + 2)) subgrid ('larger_subgrid') and
	# extract then the ('num_rows_subgrid' x 'num_columns_subgrid') subgrid ('subgrid').

	num_rows_sg = 1 + (2 * subgrid_radius) # 'sg' for subgrid.
	num_columns_sg = num_rows_sg

	# Larger subgrid.
	radius_lg_sg = subgrid_radius + 1 # 'lg_sg' for larger subgrid.
	num_rows_lg_sg = num_rows_sg + 2
	num_columns_lg_sg = num_columns_sg + 2

	# Wall tichness.
	(left_wall_lg_sg, right_wall_lg_sg, top_wall_lg_sg, bottom_wall_lg_sg) = _compute_wall_thickness_subgrid(
		radius_lg_sg, num_rows_grid, num_columns_grid)

	# Position of tiles that are not walls (of the larger subgrid).
	tile_pos_list = get_positions(num_rows_lg_sg, num_columns_lg_sg, left_wall_lg_sg, right_wall_lg_sg, top_wall_lg_sg,
		bottom_wall_lg_sg)
	num_tiles_lg_sg = len(tile_pos_list)

	# Number of bombs.
	num_bombs_lg_sg = _compute_num_bombs_subgrid(num_tiles_lg_sg, num_rows_grid, num_columns_grid, num_bombs_grid)

	# Creation of the larger subgrid.
	middle_tile_pos = (radius_lg_sg, radius_lg_sg)
	tile_pos_list.remove(middle_tile_pos)

	bomb_position_list = []
	if bomb_middle_tile:
		bomb_position_list.append(middle_tile_pos)
		if num_bombs_lg_sg > 0:
			num_bombs_lg_sg -= 1
	else:
		if num_bombs_lg_sg == num_tiles_lg_sg:
			num_bombs_lg_sg -= 1

	bomb_position_list.extend(random.sample(tile_pos_list, num_bombs_lg_sg))

	larger_subgrid = Grid(num_rows_lg_sg, num_columns_lg_sg, bomb_position_list, left_wall_lg_sg, right_wall_lg_sg,
		top_wall_lg_sg, bottom_wall_lg_sg)

	# Subgrid.
	# Wall tichness.
	compute_wall_sg = lambda wall_lg_sg: (wall_lg_sg - 1) if (wall_lg_sg > 0) else 0
	left_wall_sg = compute_wall_sg(left_wall_lg_sg)
	right_wall_sg = compute_wall_sg(right_wall_lg_sg)
	top_wall_sg = compute_wall_sg(top_wall_lg_sg)
	bottom_wall_sg = compute_wall_sg(bottom_wall_lg_sg)

	# Bombs.
	filter_bomb_pos_list = lambda bomb_pos: ((0 < bomb_pos[0] < (num_rows_lg_sg - 1)) and
		(0 < bomb_pos[1] < (num_columns_lg_sg - 1)))
	bomb_position_list = list(filter(filter_bomb_pos_list, larger_subgrid.bomb_position_list))

	# Grid.
	grid = [
		[larger_subgrid.tile_at(i, j) for j in range(1, (num_columns_lg_sg - 1))]
		for i in range(1, (num_rows_lg_sg - 1))
	]

	# Creation of the subgrid.
	subgrid = Grid(num_rows_sg, num_columns_sg, [], left_wall_sg, right_wall_sg, top_wall_sg,
		bottom_wall_sg)
	subgrid._bomb_position_list = bomb_position_list
	subgrid._grid = grid

	return subgrid

def _compute_wall_thickness_subgrid(subgrid_radius, num_rows_grid, num_columns_grid):
	"""
	Compute a random thickness of walls for the subgrids.

	:subgrid_radius: The radius of the subgrid. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:return: A random thickness of the left, right, top and bottom walls.
	"""

	left_wall = 0
	right_wall = 0
	top_wall = 0
	bottom_wall = 0

	prob_left_wall = subgrid_radius / num_columns_grid # Probability that there is a left wall.
	prob_right_wall = prob_left_wall # Probability that there is a right wall.
	prob_top_wall = subgrid_radius / num_rows_grid # Probability that there is a top wall.
	prob_bottom_wall = prob_top_wall # Probability that there is a bottom wall.

	random_num = random.random()
	if random_num < prob_left_wall:
		left_wall = random.randint(1, subgrid_radius)
	elif random_num < (prob_left_wall + prob_right_wall):
		right_wall = random.randint(1, subgrid_radius)

	random_num = random.random()
	if random_num < prob_top_wall:
		top_wall = random.randint(1, subgrid_radius)
	elif random_num < (prob_top_wall + prob_bottom_wall):
		bottom_wall = random.randint(1, subgrid_radius)

	return (left_wall, right_wall, top_wall, bottom_wall)

def _compute_num_bombs_subgrid(num_tiles_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid):
	"""
	Compute a random number of bombs for the subgrids.

	:num_tiles_subgrid: The number of tiles that are not walls of the subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the original grid.
	:return: A random number of bombs between 0 and 'num_tiles_subgrid'.
	"""

	num_tiles_grid = num_rows_grid * num_columns_grid
	tile_ratio = num_tiles_subgrid / num_tiles_grid

	num_bombs_subgrid = 0
	for i in range(num_bombs_grid):
		if random.random() < tile_ratio:
			num_bombs_subgrid += 1

	return num_bombs_subgrid

if __name__ == "__main__":
	num_rows = 10
	num_columns = 10
	num_bombs = 10

	g = generate_masked_grid(num_rows, num_columns, num_bombs)
	print(g)

	g = generate_subgrid(2, False, num_rows, num_columns, num_bombs)
	print(g)

	g = generate_subgrid(2, True, num_rows, num_columns, num_bombs)
	print(g)
