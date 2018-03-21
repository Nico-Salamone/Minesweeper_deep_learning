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

	if isinstance(grid, Grid):
		grid_object = True

		num_rows = grid.num_rows
		num_columns = grid.num_columns
	else:
		grid_object = False

		num_rows = len(grid)
		num_columns = len(grid[0])

	value_list = []
	for i in range(num_rows):
		for j in range(num_columns):
			if grid_object:
				tile = grid.tile_at(i, j)
			else:
				tile = grid[i][j]

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

def generate_random_mask(subgrid, num_masked_tiles, mask_middle_tile=False, mask_bomb_tiles=False, walls=None):
	"""
	Generate a subgrid with a random mask with 'num_masked_tiles' masked tiles.
	If 'num_masked_tiles' is greater than the number of "available" tiles (tiles that can be masked), then
	'num_masked_tiles' is replaced by this number.
	If 'mask_bomb_tile' is True and if the number of the bombs within 'subgrid' is greater than 'num_masked_tiles',
	then only the tiles containing a bomb will be masked.
	The wall tiles are not masked.

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_tiles: The number of tiles to mask.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked (therefore
		'num_masked_tiles' - 1 others tiles will then be masked).
	:mask_bomb_tiles: If True, then the tiles that contain a bomb will be masked.
	:walls: A tuple of four integers. The first one for the thickness of the left wall, the second for the right wall,
		the third for the top wall and the fourth the bottom wall. If None, then the thicknesses will be computed
		(lower performance).
	:return: A subgrid with a random mask (a list of tile values, that is an one-dimensional grid).
	"""

	if num_masked_tiles <= 0:
		raise ValueError("Error: the number of masked tiles must be greater or equals to 1!")

	masked_subgrid = copy.copy(subgrid)

	num_tiles = len(masked_subgrid)
	edge_size = int(math.sqrt(num_tiles))
	radius = int(edge_size / 2)
	middle_tile_pos = int(num_tiles / 2)
	left_wall, right_wall, top_wall, bottom_wall = compute_walls(masked_subgrid) if (walls == None) else walls

	pos_to_sample = get_positions(edge_size, edge_size, left_wall, right_wall, top_wall, bottom_wall)
	pos_to_sample = {((i * edge_size) + j) for (i, j) in pos_to_sample}

	masked_tile_pos = []
	pos_to_remove = set()

	if mask_middle_tile:
		pos_to_remove.add(middle_tile_pos)
		masked_tile_pos.append(middle_tile_pos)
		num_masked_tiles -= 1

	if mask_bomb_tiles:
		bomb_tile_pos = []
		for i, tile in enumerate(subgrid):
			if tile == Tile.BOMB:
				if not((i == middle_tile_pos) and mask_middle_tile): # If not add above.
					pos_to_remove.add(i)
					masked_tile_pos.append(i)
					num_masked_tiles -= 1

	pos_to_sample = pos_to_sample - pos_to_remove

	if num_masked_tiles < 0:
		num_masked_tiles = 0
	if num_masked_tiles > len(pos_to_sample):
		num_masked_tiles = len(pos_to_sample)

	masked_tile_pos.extend(random.sample(pos_to_sample, num_masked_tiles))

	for i in masked_tile_pos:
		masked_subgrid[i] = MaskedTile.MASKED.value

	return masked_subgrid

def generate_random_masks(subgrid, num_masked_subgrids, mask_middle_tile=False, mask_bomb_tiles=False):
	"""
	Generate a list of subgrids with a random mask. For each one, between 1 and ('num_available_tiles' - 1) tiles are
	masked, where 'num_available_tiles' is the number of "available" tiles (tiles that can be masked).

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:num_masked_subgrids: The number of subgrids with a random mask to generate.
	:mask_middle_tile: If True, then the tile in the middle of 'subgrid' will be masked.
	:mask_bomb_tiles: If True, then the tiles that contain a bomb will be masked.
	:return: A list of subgrids with a random mask (a list of tile values, that is an one-dimensional grid).
	"""

	walls = compute_walls(subgrid)
	left_wall, right_wall, top_wall, bottom_wall = walls

	num_tiles = len(subgrid)
	edge_size = int(math.sqrt(num_tiles))
	# Number of tiles that can be masked.
	num_available_tiles = (edge_size - top_wall - bottom_wall) * (edge_size - left_wall - right_wall)

	subgrids = []
	for i in range(num_masked_subgrids):
		num_masked_tiles = random.randint(1, (num_available_tiles - 1))
		masked_grid = generate_random_mask(subgrid, num_masked_tiles, mask_middle_tile, mask_bomb_tiles, walls)
		subgrids.append(masked_grid)

	return subgrids

def compute_num_masked_tiles(subgrid):
	"""
	Compute the number of masked tiles of a subgrid.

	:sugrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:return: The number of masked tiles of the subgrid.
	"""

	num_masked_tiles = 0
	for tile in subgrid:
		if tile == MaskedTile.MASKED:
			num_masked_tiles += 1

	return num_masked_tiles

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
	sg2 = to_value_list(sg)
	print(sg2)
	print(compute_num_masked_tiles(sg2))
	print_grid(sg2)



	print('\n\n')
	from minesweeper.grid_generation import generate_subgrid
	radius = 2

	sg = generate_subgrid(radius, False, 10, 10, 10)
	sg2 = to_value_list(sg)
	print(sg2)
	print_grid(sg2)
	print('')

	msgs = generate_random_masks(sg2, 5, True, True)
	for msg in msgs:
		print_grid(msg)
		print('')
