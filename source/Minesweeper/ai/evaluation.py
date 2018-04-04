from minesweeper.minesweeper import Minesweeper, State

import random

def scores(ai, num_games, num_rows_grid, num_columns_grid, num_bombs_grid, first_round_random=False):
	"""
	Get the scores of an artificial intelligence. This function creates 'num_games' games and the artificial
	intelligence plays on them.

	:ai: An artificial intelligence.
	:num_games: The number of games where the artificial intelligence plays on them.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:first_round_random: If True, then the first round of each game is random. If False, then the first round of each
		game is determined by the artificial intelligence.
	:return: The scores of the artificial intelligence.
	"""

	score_list = []
	for i in range(num_games):
		# It is not possible to lose to the first round.
		state = State.LOSS
		while state == State.LOSS:
			ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)

			if first_round_random:
				pos = (random.randint(0, (num_rows_grid - 1)), random.randint(0, (num_columns_grid - 1)))
			else:
				pos = ai.best_tile_pos(ms.grid)

			ms.play_tile(pos[0], pos[1])
			state = ms.state

		while ms.state == State.CONTINUE:
			pos = ai.best_tile_pos(ms.grid)
			ms.play_tile(pos[0], pos[1])

		score_list.append(ms.score)

	return score_list

if __name__ == "__main__":
	from ai.ai import AI
	from ai.helpers import model_file_path

	from keras.models import load_model
	import numpy as np

	random.seed(42)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	subgrid_radius = 2

	num_games = 1000
	max_score = (num_rows_grid * num_columns_grid) - num_bombs_grid

	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius)
	model = load_model(model_file_name)

	ai = AI(model, subgrid_radius)

	score_list = scores(ai, num_games, num_rows_grid, num_columns_grid, num_bombs_grid, first_round_random=True)
	bad_score_list = list(filter(lambda score: score < max_score, score_list)) # Scores below the maximum score.
	num_win_games = score_list.count(max_score)

	print("Number of games: {}\nNumber of games won: {}\nWin rate: {:.3f}\n".format(num_games, num_win_games,
		(num_win_games / num_games)))

	print("Distribution of all scores:")
	print("Min: {}\nMax: {}\nMean: {:.3f}\nPercentile 25: {}\nPercentile 50 (median): {}\nPercentile 75: {}\n".format(
		min(score_list), max(score_list), np.mean(score_list), np.percentile(score_list, 25),
		np.percentile(score_list, 50), np.percentile(score_list, 75)))

	print("Distribution of scores below the maximum score (scores of losing games):")
	print("Min: {}\nMax: {}\nMean: {:.3f}\nPercentile 25: {}\nPercentile 50 (median): {}\nPercentile 75: {}".format(
		min(bad_score_list), max(bad_score_list), np.mean(bad_score_list), np.percentile(bad_score_list, 25),
		np.percentile(bad_score_list, 50), np.percentile(bad_score_list, 75)))
