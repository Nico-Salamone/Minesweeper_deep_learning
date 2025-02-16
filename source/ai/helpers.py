from minesweeper.grid import Tile, Grid, get_positions
from minesweeper.masked_grid import MaskedTile

import random
import math
import copy

def to_value_list(grid):
	"""
	Convert a grid to a list of values of each tile.

	:grid: A grid (a Grid object or a list of lists of tiles).
	:return: The list of values of each tile.
	"""

	value_list = []
	for row in grid:
		for tile in row:
			try: # If tile is an empty (and has 0 as value), a bomb, a wall or a masked tile.
				tile = tile.value
			except AttributeError: # If tile is an integer (empty tile).
				pass

			value_list.append(tile)

	return value_list

def compute_walls(grid):
	"""
	Compute the thickness of walls from a grid.

	:grid: A grid (a list of tile values, that is an one-dimensional grid).
	:return: the thickness of walls.
	"""

	num_tiles = len(grid)
	edge_size = int(math.sqrt(num_tiles))
	radius = int((edge_size - 1) / 2)

	left_wall = 0
	right_wall = 0
	top_wall = 0
	bottom_wall = 0

	for i in range((radius * edge_size), ((radius * edge_size) + radius)):
		# '(radius * edge_size)' is the position of the tile in the left middle.
		if grid[i] == Tile.WALL:
			left_wall += 1

	for i in range(((radius * edge_size) + radius + 1), ((radius + 1) * edge_size)):
		if grid[i] == Tile.WALL:
			right_wall += 1

	for i in range(radius, (radius * edge_size), edge_size): # 'radius' is the position of the tile in the top middle.
		if grid[i] == Tile.WALL:
			top_wall += 1

	for i in range(((radius + 1) * edge_size) + radius, num_tiles, edge_size):
		if grid[i] == Tile.WALL:
			bottom_wall += 1

	return (left_wall, right_wall, top_wall, bottom_wall)

def generate_random_mask(subgrid, num_masked_tiles, mask_middle_tile=False, mask_bomb_tiles=False,
	flag_bomb_tiles=False, walls=None):
	"""
	Generate a subgrid with a random mask with 'num_masked_tiles' masked tiles.
	If 'num_masked_tiles' is greater than the number of "available" tiles (tiles that can be masked), then
	'num_masked_tiles' is replaced by this number.
	If 'mask_bomb_tile' is True and if the number of the bombs within 'subgrid' is greater than 'num_masked_tiles',
	then only the tiles containing a bomb will be masked.
	The 'mask_bomb_tiles' and 'flag_bomb_tiles' parameters can not be True at the same time. If so, then
	'mask_bomb_tiles' is ignored (as if it is False).
	The wall tiles are not masked.

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_tiles: The number of tiles to mask.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked (therefore
		'num_masked_tiles' - 1 others tiles will then be masked).
	:mask_bomb_tiles: If True, then all tiles that contain a bomb will be masked.
	:flag_bomb_tiles: If True, then the unmasked tiles that contain a bomb will be replaced by a flag tile
		('mask_bomb_tiles' is therefore ignored). The tile in the middle of 'subgrid' will not be replaced if
		'mask_middle_tile' is True.
	:walls: A tuple of four integers. The first one for the thickness of the left wall, the second for the right wall,
		the third for the top wall and the fourth the bottom wall. If None, then the thicknesses will be computed
		(lower performance).
	:return: A subgrid with a random mask (a list of tile values, that is an one-dimensional grid).
	"""

	if num_masked_tiles <= 0:
		raise ValueError("Error: the number of masked tiles must be greater or equals to 1!")

	masked_subgrid = copy.copy(subgrid)

	# Compute somes values about the subgrid.
	num_tiles = len(masked_subgrid)
	edge_size = int(math.sqrt(num_tiles))
	radius = int(edge_size / 2)
	middle_tile_pos = int(num_tiles / 2)
	left_wall, right_wall, top_wall, bottom_wall = compute_walls(masked_subgrid) if (walls == None) else walls

	# Positions to sample.
	pos_to_sample = get_positions(edge_size, edge_size, left_wall, right_wall, top_wall, bottom_wall)
	pos_to_sample = {((i * edge_size) + j) for (i, j) in pos_to_sample}

	masked_tile_pos = []
	pos_to_remove = set()

	if mask_middle_tile:
		# Remove the middle position.
		pos_to_remove.add(middle_tile_pos)
		masked_tile_pos.append(middle_tile_pos)
		num_masked_tiles -= 1

	if mask_bomb_tiles and not flag_bomb_tiles:
		# Remove the positions containing a bomb.
		bomb_tile_pos = []
		for i, tile in enumerate(subgrid):
			if tile == Tile.BOMB:
				if not((i == middle_tile_pos) and mask_middle_tile):
					# Do nothing if 'i' is the position of the tile in the middle of the subgrid and 'mask_middle_tile'
					# is True.
					pos_to_remove.add(i)
					masked_tile_pos.append(i)
					num_masked_tiles -= 1

	# Remove the positions to remove.
	pos_to_sample = pos_to_sample - pos_to_remove

	# Adjust the number of tiles to mask.
	if num_masked_tiles < 0:
		num_masked_tiles = 0
	if num_masked_tiles > len(pos_to_sample):
		num_masked_tiles = len(pos_to_sample)

	# Sample somes positions.
	masked_tile_pos.extend(random.sample(pos_to_sample, num_masked_tiles))

	# Mask the tiles.
	for i in masked_tile_pos:
		masked_subgrid[i] = MaskedTile.MASKED.value

	# Insert the flags.
	if flag_bomb_tiles:
		for i, tile in enumerate(masked_subgrid):
			if tile == Tile.BOMB: # 'tile' is not masked and contains a bomb.
				if not((i == middle_tile_pos) and mask_middle_tile):
					# Do nothing if 'i' is the position of the tile in the middle of the subgrid and 'mask_middle_tile'
					# is True.
					masked_subgrid[i] = MaskedTile.FLAG.value

	return masked_subgrid

def generate_random_masks(subgrid, num_masked_subgrids, mask_middle_tile=False, mask_bomb_tiles=False,
	flag_bomb_tiles=False):
	"""
	Generate a list of subgrids with a random mask. For each one, between 1 and ('num_available_tiles' - 1) tiles are
	masked, where 'num_available_tiles' is the number of "available" tiles (tiles that can be masked).

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_subgrids: The number of subgrids with a random mask to generate.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked.
	:mask_bomb_tiles: If True, then the tiles that contain a bomb will be masked.
	:flag_bomb_tiles: If True, then the unmasked tiles that contain a bomb will be replaced by a flag tile
		('mask_bomb_tiles' is therefore ignored). The tile in the middle of 'subgrid' will not be replaced if
		'mask_middle_tile' is True.
	:return: A list of subgrids with a random mask (a list of tile values, that is an one-dimensional grid).
	"""
 
 	# Compute the thickness of the walls.
	walls = compute_walls(subgrid)
	left_wall, right_wall, top_wall, bottom_wall = walls

	num_tiles = len(subgrid)
	edge_size = int(math.sqrt(num_tiles))
	# Number of tiles that can be masked.
	num_available_tiles = (edge_size - top_wall - bottom_wall) * (edge_size - left_wall - right_wall)

	subgrids = []
	for i in range(num_masked_subgrids):
		num_masked_tiles = random.randint(1, (num_available_tiles - 1))
		masked_grid = generate_random_mask(subgrid, num_masked_tiles, mask_middle_tile, mask_bomb_tiles,
			flag_bomb_tiles, walls)
		subgrids.append(masked_grid)

	return subgrids

def count_num_masked_tiles(subgrid):
	"""
	Count the number of masked tiles of a subgrid.

	:sugrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:return: The number of masked tiles of the subgrid.
	"""

	num_masked_tiles = 0
	for tile in subgrid:
		if (tile == MaskedTile.MASKED) or (tile == MaskedTile.FLAG):
			num_masked_tiles += 1

	return num_masked_tiles

def count_num_empty_tiles_not_masked(subgrid):
	"""
	Count the number of empty tiles that are not masked of a subgrid.

	:sugrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:return: The number of empty tiles that are not masked of the subgrid.
	"""

	num_empty_tiles_not_masked = 0
	for tile in subgrid:
		if tile == MaskedTile.EMPTY:
			num_empty_tiles_not_masked += 1

	return num_empty_tiles_not_masked

def extract_subgrid(grid, i, j, subgrid_radius):
	"""
	Extrat a subgrid from a grid and a position. The tile at this position is the center of the subgrid.

	:grid: The grid (a list of lists of tiles).
	:i: The index of the row of the position.
	:j: The index of the columns of the position.
	:subgrid_radius: The radius of the subgrid. For example, with a radius of 2, this function will return a 5 by 5
		subgrid.
	:return: The subgrid (a list of lists of tiles, that is an two-dimensional grid).
	"""

	num_rows = 1 + (2 * subgrid_radius)
	num_columns = num_rows

	subgrid = []
	i_min = i - subgrid_radius
	j_min = j - subgrid_radius
	for i_subgrid in range(num_rows):
		row = []
		for j_subgrid in range(num_columns):
			i_grid = i_min + i_subgrid
			j_grid = j_min + j_subgrid
			
			if (0 <= i_grid < len(grid)) and (0 <= j_grid < len(grid[0])):
				tile = grid[i_grid][j_grid]
			else:
				tile = MaskedTile.WALL

			row.append(tile)

		subgrid.append(row)

	return subgrid

def print_grid(grid):
	"""
	Print a grid.

	:grid: The grid (a list of tile values, that is an one-dimensional grid).
	"""

	num_tiles = len(grid)
	edge_size = int(math.sqrt(num_tiles))

	for i, tile in enumerate(grid):
		try: # If tile is an empty (and has 0 as value), a bomb, a wall or a masked tile.
			tile = MaskedTile(tile)
		except ValueError: # If tile is an integer (empty tile).
			pass

		print(tile, end='\t')

		if (i > 0) and ((i + 1) % edge_size == 0):
			print('')

def data_set_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, bomb_middle_tile,
	without_duplicates=False, folder_path="ai/nn/data_sets/"):
	"""
	Get the path of the data set folling parameters.

	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:subgrid_radius: The radius of subgrids. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:bomb_middle_tile: If True, then the tile in the middle of the subgrids contains a bomb. If False, then this tile
		does not contain a bomb.
	:without_duplicates: If True, then the data set is without duplicates. If False, then it is with duplicates.
	:folder_path: The path of the folder including the file.
	:return: The path of the data set.
	"""

	without_duplicates_str = "_wod" if without_duplicates else ""

	return folder_path + "data_set_{}ro_{}c_{}b_{}ra_{}bm{}.csv".format(num_rows_grid, num_columns_grid, num_bombs_grid,
		subgrid_radius, bomb_middle_tile, without_duplicates_str)

def model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius, with_flags=False,
	folder_path="ai/nn/models/"):
	"""
	Get the path of the model folling parameters.

	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:subgrid_radius: The radius of subgrids. For example, with a radius of 2, the subgrid is a 5 by 5 subgrid.
	:with_flags: If True, then the tiles of masked subgrids containing a bomb will contain a flag.
	:folder_path: The path of the folder including the file.
	:return: The path of the model.
	"""

	with_flags_str = "_wf" if with_flags else ""

	return folder_path + "model_{}ro_{}c_{}b_{}ra{}.h5".format(num_rows_grid, num_columns_grid, num_bombs_grid,
		subgrid_radius, with_flags_str)

if __name__ == "__main__":
	from minesweeper.masked_grid import MaskedGrid

	random.seed(42)

	# Test the 'extract_subgrid', 'to_value_list', 'count_num_masked_tiles' and 'print_grid' functions.
	bomb_position_list = [(5, 4), (4, 2), (2, 1), (4, 4)]
	g = MaskedGrid(10, 5, bomb_position_list, left_wall=1, right_wall=0, top_wall=2, bottom_wall=3)
	g.unmask_tile(2, 4)
	g.unmask_tile(5, 3)
	g.insert_flag(4, 2)
	print(g)

	radius = 2
	sg = extract_subgrid(g.grid, 4, 4, radius)
	sg2 = to_value_list(sg)
	print(sg2)
	print(count_num_masked_tiles(sg2))
	print_grid(sg2)
	print('\n\n')

	# Test the 'generate_random_masks' function.
	from minesweeper.grid_generation import generate_subgrid
	radius = 2

	sg = generate_subgrid(radius, False, 10, 10, 10)
	sg2 = to_value_list(sg)
	print(sg2)
	print_grid(sg2)
	print('\n')

	msgs = generate_random_masks(sg2, 5, mask_middle_tile=True, mask_bomb_tiles=True)
	for msg in msgs:
		print_grid(msg)
		print('')

	print('')

	msgs = generate_random_masks(sg2, 5, mask_middle_tile=True, flag_bomb_tiles=True)
	for msg in msgs:
		print_grid(msg)
		print('')
