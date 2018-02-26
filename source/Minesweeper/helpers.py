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

	for i in range((radius * edge_size), ((radius * edge_size) + radius)):
		if grid[i] == Tile.WALL:
			left_wall += 1

	for i in range(((radius * edge_size) + radius + 1), ((radius + 1) * edge_size)):
		if grid[i] == Tile.WALL:
			right_wall += 1

	for i in range(radius, (radius * edge_size), edge_size):
		if grid[i] == Tile.WALL:
			top_wall += 1

	for i in range(((radius + 1) * edge_size) + radius, num_tiles, edge_size):
		if grid[i] == Tile.WALL:
			bottom_wall += 1

	return (left_wall, right_wall, top_wall, bottom_wall)

def generate_random_mask(subgrid, min_masked_tiles=0, max_masked_tiles=None):
	"""
	Generate a list of grids with a mask.
	The tile in the middle of 'subgrid' is masked and this tile is added to a list. Then, this function rands a number 'n'
	between 'min_masked_tiles' and 'max_masked_tiles'. Then, it masks a tile randomly and adds it to the list (2 tiles are
	masked). Then, it masks again a tile randomly and adds it to the list (3 tiles is masked). It repeats this until 'n' + 1
	tiles are masked. If 'n' is greater than the the number of 'availabe' tiles (tiles that can be masked), then 'n' is
	replaced by this number.
	The wall tiles are not masked.

	:subgrid: The subgrid (a list of tile values, that is an one-dimensional grid).
	:min_masked_tiles: The minimum number of tiles to mask.
	:max_masked_tiles: The maximum number of tiles to mask.
	:return: A list of grids with a mask (a list of tile values, that is an one-dimensional grid).
	"""

	num_tiles = len(subgrid)
	edge_size = int(math.sqrt(num_tiles))
	radius = int((edge_size - 1) / 2)
	left_wall, right_wall, top_wall, bottom_wall = compute_walls(subgrid)

	if max_masked_tiles == None:
		max_masked_tiles = num_tiles - 1 # The tile in the middle of the grid can not be masked.

	pos = get_positions(edge_size, edge_size, left_wall, right_wall, top_wall, bottom_wall)
	pos.remove((radius, radius)) # Tile in the middle of the grid.

	num_masked_tiles = random.randint(min_masked_tiles, max_masked_tiles)
	if num_masked_tiles > len(pos):
		num_masked_tiles = len(pos)

	masked_tiles_pos = [(radius, radius)]
	masked_tiles_pos.extend(random.sample(pos, num_masked_tiles))

	masked_subgrids = []
	for i, j in masked_tiles_pos:
		k = (i * edge_size) + j

		subgrid = copy.copy(subgrid)
		subgrid[k] = MaskedTile.MASKED.value
		masked_subgrids.append(subgrid)

	return masked_subgrids

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

	g = generate_subgrid(radius, 10, 10, 10)
	g2 = to_value_list(g)

	print(g)
	print(g2)
	for msg in generate_random_mask(g2, 3, 16):
		for i in range(len(msg)):
			print(msg[i], end='\t')
			if (i > 0) and ((i + 1) % edge_size == 0):
				print('')
		print('')
