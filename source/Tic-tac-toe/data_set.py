from functools import lru_cache
import csv

import tic_tac_toe as ttt

@lru_cache(maxsize = None)
def generate_data_set(grid = ttt.initialize_empty_grid()):
	state = ttt.get_grid_state(grid)

	if state == ttt.State.WIN:
		return [(grid, (1, 0, 0))]
	elif state == ttt.State.LOSE:
		return [(grid, (0, 1, 0))]
	elif state == ttt.State.DRAW:
		return [(grid, (0, 0, 1))]
	else: # If the state is continue.
		tree = []
		scores = (0, 0, 0)

		player = ttt.get_player_who_must_play_now(grid)
		empty_tile_indexes = ttt.get_empty_tile_indexes(grid)
		for tile_index in empty_tile_indexes:
			subtree = generate_data_set(ttt.play_turn(grid, player, tile_index))
			subtree_scores = subtree[0][1] # Scores of the root of the subtree.

			tree.extend(subtree)
			scores = tuple(map(lambda x, y: x + y, scores, subtree_scores))

		tree.insert(0, (grid, scores))

	return tree

def remove_duplicates(list_with_duplicates):
	elements_seen = set()
	list_without_duplicates = []
	for element in list_with_duplicates:
		if not element in elements_seen:
			elements_seen.add(element)
			list_without_duplicates.append(element)

	return list_without_duplicates

def write_data_set(data_set, data_set_file_name):
	with open(data_set_file_name, 'w', newline = '') as data_set_file:
		csv_writer = csv.writer(data_set_file, delimiter = ';', quotechar = '\"', quoting = csv.QUOTE_MINIMAL)

		for grid, scores in data_set:
			row = [tile.value for tile in grid]
			row.extend([score for score in scores])

			csv_writer.writerow(row)

def read_data_set(data_set_file_name):
	data_set = []
	with open(data_set_file_name, newline = '') as data_set_file:
		csv_reader = csv.reader(data_set_file, delimiter = ';', quotechar = '\"')

		n = ttt.SIZE
		for row in csv_reader:
			tiles = row[:n]
			grid = tuple(ttt.Tile(int(tile)) for tile in tiles)
			scores = tuple(map(int, row[n : n + 3]))

			data_set.append((grid, scores))

	return data_set

if __name__ == "__main__":
	data_set_file_name = "data_set.csv"

	data_set_with_duplicates = generate_data_set()
	data_set = remove_duplicates(data_set_with_duplicates)

	write_data_set(data_set, data_set_file_name)
	data_set = read_data_set(data_set_file_name)

	#"""
	for grid, scores in data_set:
		ttt.print_grid(grid)
		print(scores, "\n")
	#"""
