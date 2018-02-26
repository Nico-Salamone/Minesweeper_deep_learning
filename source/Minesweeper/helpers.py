from minesweeper.masked_grid import MaskedTile

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
	from masked_grid import MaskedGrid
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
