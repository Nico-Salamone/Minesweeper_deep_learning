from minesweeper.grid import Tile, get_positions
from minesweeper.masked_grid import MaskedTile

import random
import math
import copy

def to_value_list(grid):
	"""
	Convert a grid to a list of values of each tile.

	:grid: A grid.
	:return: The list of values of each tile.
	"""

	value_list = []
	for i in range(grid.num_rows):
		for j in range(grid.num_columns):
			tile = grid.tile_at(i, j)
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

	for i in range((radius * edge_size), ((radius * edge_size) + radius)): # '(radius * edge_size)' is the position of the tile in the left middle.
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

def generate_random_mask(subgrid, num_masked_tiles, mask_middle_tile=False, walls=None):
	"""
	Generate a grid with a random mask with 'num_masked_tiles' masked tiles.
	If 'num_masked_tiles' is greater than the number of "available" tiles (tiles that can be masked), then
	'num_masked_tiles' is replaced by this number.
	The wall tiles are not masked.

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_tiles: The number of tiles to mask.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked (therefore 'num_masked_tiles' - 1
		others tiles will then be masked).
	:walls: A tuple of four integers. The first one for the thickness of the left wall, the second for the right wall, the 
		hird for the top wall and the fourth the bottom wall. If None, then the thicknesses are computed (lower performance).
	:return: A subgrid with a random mask (a list of tile values, that is an one-dimensional grid).
	"""

	if num_masked_tiles <= 0:
		raise ValueError("Error: the number of masked tiles must be greater or equals to 1!")

	masked_subgrid = copy.copy(subgrid)

	num_tiles = len(masked_subgrid)
	edge_size = int(math.sqrt(num_tiles))
	radius = int((edge_size - 1) / 2)
	left_wall, right_wall, top_wall, bottom_wall = compute_walls(masked_subgrid) if (walls == None) else walls

	pos = get_positions(edge_size, edge_size, left_wall, right_wall, top_wall, bottom_wall)

	masked_tile_pos = []
	if mask_middle_tile:
		middle_tile_pos = (radius, radius)

		pos.remove(middle_tile_pos)
		masked_tile_pos.append(middle_tile_pos)
		num_masked_tiles -= 1

	if num_masked_tiles > len(pos):
		num_masked_tiles = len(pos)

	masked_tile_pos.extend(random.sample(pos, num_masked_tiles))

	for i, j in masked_tile_pos:
		k = (i * edge_size) + j

		masked_subgrid[k] = MaskedTile.MASKED.value

	return masked_subgrid

def generate_random_masks(subgrid, num_masked_subgrids_by_num_masked_tiles, mask_middle_tile=False):
	"""
	Generate a list of grids with a random mask. First, this function generates 'num_masked_subgrids_by_num_masked_tiles'
	random sugrids with one masked tile (if 'mask_middle_tile' is True, only one grid is generated). Then, it generates
	'num_masked_subgrids_by_num_masked_tiles' random sugrids with two masked tiles. And so on until the number of "available"
	tiles (tiles that can be masked) is reached.
	The wall tiles are not masked.	

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_subgrids_by_num_masked_tiles: The number of grids to generate for each number of masked tiles.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked.
	:return: A list of subgrids with a random mask (a list of tile values, that is an one-dimensional grid).
	"""

	walls = compute_walls(subgrid)
	left_wall, right_wall, top_wall, bottom_wall = walls

	num_tiles = len(subgrid)
	edge_size = int(math.sqrt(num_tiles))
	# Number of tiles that can be masked.
	num_available_tiles = (edge_size - top_wall - bottom_wall) * (edge_size - left_wall - right_wall)

	subgrids = []
	for i in range(1, (num_available_tiles + 1)): # 'i' is the number of tiles to mask.
		# Avoids returning the same masked grid several times.
		if (((i == 1) and mask_middle_tile)) or ((num_available_tiles - i) == 0):
			n = 1
		else:
			n = num_masked_subgrids_by_num_masked_tiles

		for j in range(n):
			subgrids.append(generate_random_mask(subgrid, i, mask_middle_tile, walls))

	return subgrids

def extract_subgrid(grid, i, j, radius):
	"""
	Extrat a subgrid from a grid and a position. The tile at this position is the center of the subgrid.

	:grid: The grid.
	:i: The index of the row of the position.
	:j: The index of the columns of the position.
	:radius: The radius of the subgrid. For example, with a radius of 2, this function will return a 5 by 5 subgrid.
	:return: The subgrid (a list of lists of tiles).
	"""

	num_rows = 1 + (2 * radius)
	num_columns = num_rows

	subgrid = [[MaskedTile.WALL for j in range(num_columns)] for i in range(num_rows)]
	i_min = i - radius
	j_min = j - radius
	for i_subgrid in range(num_rows):
		for j_subgrid in range(num_columns):
			i_grid = i_min + i_subgrid
			j_grid = j_min + j_subgrid
			if grid.within_boundaries(i_grid, j_grid):
				subgrid[i_subgrid][j_subgrid] = grid.tile_at(i_grid, j_grid)

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

if __name__ == "__main__":
	from minesweeper.masked_grid import MaskedGrid
	bomb_position_list = [(5, 4), (4, 2), (2, 1), (4, 4)]
	g = MaskedGrid(10, 5, bomb_position_list, 1, 0, 2, 3)
	g.unmask_tile(2, 4)
	g.unmask_tile(5, 3)
	print(g)

	radius = 2
	sg = extract_subgrid(g, 4, 4, radius)
	print("i = {}\nj = {}".format(radius, radius))
	for row in sg:
		for tile in row:
			print(tile, end='\t')
		print('')



	print('\n\n')
	from minesweeper.grid_generation import generate_subgrid
	radius = 2
	edge_size = (radius * 2) + 1

	sg = generate_subgrid(radius, 10, 10, 10)
	sg2 = to_value_list(sg)
	print(sg)
	print(sg2)

	msgs = generate_random_masks(sg2, 5, True)
	for msg in msgs:
		print_grid(msg)
		print('')
	"""
	msg = generate_random_mask(sg2, 4, True)
	print_grid(msg)
	"""
