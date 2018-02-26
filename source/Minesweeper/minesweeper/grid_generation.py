from minesweeper.grid import Grid, get_positions

import random
import numpy.random

def generate_grid(num_rows, num_columns, num_bombs, left_wall=0, right_wall=0, top_wall=0, bottom_wall=0):
	"""
	Generate a random grid. This function inserts 'num_bombs' at random positions.

	:num_rows: The number of rows of the grid.
	:num_columns: The number of columns of the grid.
	:num_bombs: The number of bombs.
	:left_wall: The thickness of the left wall.
	:right_wall: The thickness of the right wall.
	:top_wall: The thickness of the top wall.
	:bottom_wall: The thickness of the bottom wall.
	:return A random grid.
	"""

	pos_list = get_positions(num_rows, num_columns, left_wall, right_wall, top_wall, bottom_wall)
	bomb_position_list = random.sample(pos_list, num_bombs)

	return Grid(num_rows, num_columns, bomb_position_list, left_wall, right_wall, top_wall, bottom_wall)

def generate_subgrid(radius_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid):
	"""
	Generate a random subgrid. This function generates a "good" number of bombs and the "good" thickness of walls ("good"
	for realistic).

	:radius_subgrid: The radius of the subgrid. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:return A random subgrid.
	"""

	# This funtion generates a (('num_rows_subgrid' + 2) x ('num_columns_subgrid' + 2)) subgrid and extract then
	# the ('num_rows_subgrid' x 'num_columns_subgrid') subgrid.

	num_rows_subgrid = 1 + (2 * radius_subgrid)
	num_columns_subgrid = num_rows_subgrid

	# Larger subgrid.
	radius_larger_subgrid = radius_subgrid + 1
	num_rows_larger_subgrid = num_rows_subgrid + 2
	num_columns_larger_subgrid = num_columns_subgrid + 2

	# Wall tichness.
	(left_wall_larger_subgrid, right_wall_larger_subgrid, top_wall_larger_subgrid, bottom_wall_larger_subgrid) = _compute_wall_thickness_subgrid(
		radius_larger_subgrid, num_rows_grid, num_columns_grid)

	# Number of bombs.
	num_bombs_larger_subgrid = _compute_num_bombs_subgrid(num_rows_larger_subgrid, num_columns_larger_subgrid, left_wall_larger_subgrid,
		right_wall_larger_subgrid, top_wall_larger_subgrid, bottom_wall_larger_subgrid, num_rows_grid, num_columns_grid, num_bombs_grid)

	# Creation of the larger subgrid.
	larger_subgrid = generate_grid(num_rows_larger_subgrid, num_columns_larger_subgrid, num_bombs_larger_subgrid, left_wall_larger_subgrid,
		right_wall_larger_subgrid, top_wall_larger_subgrid, bottom_wall_larger_subgrid)

	# Subgrid.
	# Wall tichness.
	compute_wall_subgrid = lambda wall_larger_subgrid: (wall_larger_subgrid - 1) if (wall_larger_subgrid > 0) else 0
	left_wall_subgrid = compute_wall_subgrid(left_wall_larger_subgrid)
	right_wall_subgrid = compute_wall_subgrid(right_wall_larger_subgrid)
	top_wall_subgrid = compute_wall_subgrid(top_wall_larger_subgrid)
	bottom_wall_subgrid = compute_wall_subgrid(bottom_wall_larger_subgrid)

	# Bombs.
	filter_bomb_pos_list = lambda bomb_pos: ((0 < bomb_pos[0] < (num_rows_larger_subgrid - 1)) and (0 < bomb_pos[1] < (num_columns_larger_subgrid - 1)))
	bomb_position_list = list(filter(filter_bomb_pos_list, larger_subgrid.bomb_position_list))

	# Grid.
	grid = [
		[larger_subgrid.tile_at(i, j) for j in range(1, (num_columns_larger_subgrid - 1))]
		for i in range(1, (num_rows_larger_subgrid - 1))
	]

	# Creation of the subgrid.
	subgrid = Grid(num_rows_subgrid, num_columns_subgrid, [], left_wall_subgrid, right_wall_subgrid, top_wall_subgrid, bottom_wall_subgrid)
	subgrid._bomb_position_list = bomb_position_list
	subgrid._grid = grid

	return subgrid

def _compute_wall_thickness_subgrid(radius_subgrid, num_rows_grid, num_columns_grid):
	"""
	Compute a random thickness of walls for the subgrids.

	:radius_subgrid: The radius of the subgrid. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:return A random thickness of the left, right, top and bottom walls.
	"""

	left_wall = 0
	right_wall = 0
	top_wall = 0
	bottom_wall = 0

	prob_left_wall = radius_subgrid / num_columns_grid # Probability that there is a left wall.
	prob_right_wall = prob_left_wall # Probability that there is a right wall.
	prob_top_wall = radius_subgrid / num_rows_grid # Probability that there is a top wall.
	prob_bottom_wall = prob_top_wall # Probability that there is a bottom wall.

	random_num = random.random()
	if random_num < prob_left_wall:
		left_wall = random.randint(1, radius_subgrid)
	elif random_num < (prob_left_wall + prob_right_wall):
		right_wall = random.randint(1, radius_subgrid)

	random_num = random.random()
	if random_num < prob_top_wall:
		top_wall = random.randint(1, radius_subgrid)
	elif random_num < (prob_top_wall + prob_bottom_wall):
		bottom_wall = random.randint(1, radius_subgrid)

	return (left_wall, right_wall, top_wall, bottom_wall)

def _compute_num_bombs_subgrid(num_rows_subgrid, num_columns_subgrid, left_wall, right_wall, top_wall, bottom_wall, num_rows_grid,
	num_columns_grid, num_bombs_grid):
	"""
	Compute a random number of bombs for the subgrids.

	:num_rows_subgrid: The number of rows of the subgrid.
	:num_columns_subgrid: The number of columns of the subgrid.
	:left_wall: The thickness of the left wall of the subgrid.
	:right_wall: The thickness of the right wall of the subgrid.
	:top_wall: The thickness of the top wall of the subgrid.
	:bottom_wall: The thickness of the bottom wall of the subgrid.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_rows_grid: The number of rows of the original grid.
	:return: A random number of bombs.
	"""

	# Positions of tiles that are not walls (of the subgrid).
	tile_pos_list = get_positions(num_rows_subgrid, num_columns_subgrid, left_wall, right_wall, top_wall, bottom_wall)
	num_tiles_subgrid = len(tile_pos_list)

	# Number of bombs.
	num_tiles_grid = num_rows_grid * num_columns_grid
	prob_bomb_tile = num_bombs_grid / num_tiles_grid # Porbability that one tile contains a bomb.
	mean_num_bombs_subgrid = num_tiles_subgrid * prob_bomb_tile
	percentage_mean_num_bombs_subgrid = mean_num_bombs_subgrid / num_bombs_grid

	num_bombs_subgrid = 0
	for i in range(num_bombs_grid):
		if random.random() < percentage_mean_num_bombs_subgrid:
			num_bombs_subgrid += 1

	return num_bombs_subgrid	

if __name__ == "__main__":
	num_rows = 10
	num_columns = 10
	num_bombs = 10

	g = generate_grid(num_rows, num_columns, num_bombs, 2, 1, 0, 3)
	print(g)

	g = generate_subgrid(2, num_rows, num_columns, num_bombs)
	print(g)
