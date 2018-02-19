from grid import Tile, Grid
from masked_grid import MaskedTile, MaskedGrid

import random

if __name__ == "__main__":
	random.seed(5)

	g = gen_grid(7, 7, 4, 2, 0, 1, 0)
	g.unmask_all_tiles()
	print(g)
	g = gen_grid(7, 7, 4, 1, 2, 1, 0)
	g.unmask_all_tiles()
	print(g)
	g = gen_grid(7, 7, 6, 1, 0, 0, 1)
	g.unmask_all_tiles()
	print(g)
