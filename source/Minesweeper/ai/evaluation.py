from minesweeper.minesweeper import Minesweeper, State

import random

def scores(ai, num_games, num_rows_grid, num_columns_grid, num_bombs_grid):
	"""
	Get the scores of an artificial intelligence. This function creates 'num_games' games and the artificial
	intelligence plays on them.

	:ai: An artificial intelligence.
	:num_games: The number of games where the artificial intelligence plays on them.
	:num_rows_grid: The number of rows of the original grid.
	:num_columns_grid: The number of columns of the original grid.
	:num_bombs_grid: The number of bombs of the grid.
	:return: The scores of the artificial intelligence.
	"""

	score_list = []
	for i in range(num_games):
		# It is not possible to lose to the first turn.
		state = State.LOSS
		while state == State.LOSS:
			ms = Minesweeper(num_rows_grid, num_columns_grid, num_bombs_grid)
			ai.minesweeper = ms

			ai.play_turn()
			state = ms.state

		while ms.state == State.CONTINUE:
			ai.play_turn()

		score_list.append(ms.score)

	return score_list

if __name__ == "__main__":
	from ai.random_ai import RandomAI
	from ai.ai_without_flags import AIWithoutFlags
	from ai.ai_with_flags import AIWithFlags
	from ai.ai_with_flags2 import AIWithFlags2
	from ai.helpers import model_file_path

	from keras.models import load_model
	import numpy as np

	random.seed(42)

	num_rows_grid = 10
	num_columns_grid = 10
	num_bombs_grid = 10
	subgrid_radius = 2
	with_flags = True

	num_games = 1000
	max_score = (num_rows_grid * num_columns_grid) - num_bombs_grid

	model_file_name = model_file_path(num_rows_grid, num_columns_grid, num_bombs_grid, subgrid_radius,
		with_flags=with_flags)
	model = load_model(model_file_name)
	# If 'custom_mean_squared_error' custom loss is used.
	#from ai.nn.neural_network import custom_mean_squared_error
	#model = load_model(model_file_name, custom_objects={'custom_mean_squared_error': custom_mean_squared_error})

	if not with_flags:
		ai = AIWithoutFlags(model, subgrid_radius=subgrid_radius)
	else:
		ai = AIWithFlags(model, subgrid_radius=subgrid_radius, playful_level=1.15, flag_threshold=0.96)

	score_list = scores(ai, num_games, num_rows_grid, num_columns_grid, num_bombs_grid)
	losing_games_score_list = list(filter(lambda score: score < max_score, score_list))
	# List of scores of losing games (scores below the maximum score).
	num_win_games = score_list.count(max_score)

	# Print the number of games, the number of games won and the win rate.
	print("Number of games: {}\nNumber of games won: {}\nWin rate: {:.3f}\n".format(num_games, num_win_games,
		(num_win_games / num_games)))

	# Print the distribution of all scores.
	print("Distribution of all scores:")
	print("Min: {}\nMax: {}\nMean: {:.3f}\nPercentile 25: {}\nPercentile 50 (median): {}\nPercentile 75: {}\n".format(
		min(score_list), max(score_list), np.mean(score_list), np.percentile(score_list, 25),
		np.percentile(score_list, 50), np.percentile(score_list, 75)))

	# Print the distribution of scores below the maximum score (scores of losing games).
	print("Distribution of scores below the maximum score (scores of losing games):")
	print("Min: {}\nMax: {}\nMean: {:.3f}\nPercentile 25: {}\nPercentile 50 (median): {}\nPercentile 75: {}".format(
		min(losing_games_score_list), max(losing_games_score_list), np.mean(losing_games_score_list),
		np.percentile(losing_games_score_list, 25), np.percentile(losing_games_score_list, 50),
		np.percentile(losing_games_score_list, 75)))
