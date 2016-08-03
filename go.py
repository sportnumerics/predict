import json, math
from predictor import collect, pcd_model, lls_model, postprocess
import matplotlib.pyplot as plt

# games = collect.get_all_games()
games = {}
with open('games.json') as f:
    games = json.load(f)

games_list = list(games.values())

team_map = collect.build_team_map(games_list)

# LLS overall model
# model = lls_model.Model()
#
# coefficients = collect.build_overall_coeffient_matrix(games, team_map)
#
# constants = collect.build_overall_constants(games, team_map)
#
# model.train(coefficients, constants)
#
# ratings = postprocess.calculate_lls_ratings(team_map, model)
#
# with open('ratings.json', 'w') as f:
#     json.dump(ratings, f, indent=2)

date_cutoff = "2016-05-05T14:00:00.000Z"

def game_before_date_cutoff(g):
    return g['date'] < date_cutoff

def game_after_date_cutoff(g):
    return not game_before_date_cutoff(g)

training_games = list(filter(game_before_date_cutoff, games_list))
test_games = list(filter(game_after_date_cutoff, games_list))

print('Training on {}/{} games'.format(len(training_games), len(games_list)))

# offensive defensive model
l_model = lls_model.Model()

coefficients = collect.build_offensive_defensive_coefficient_matrix(training_games, team_map)

constants = collect.build_offensive_defensive_constants(training_games, team_map)

l_model.train(coefficients, constants)

od_ratings = postprocess.calculate_lss_offensive_defensive_ratings(team_map, l_model)

# PCD Model
p_model = pcd_model.Model(6, len(team_map['ids_to_indicies']), l_model)

all_samples = collect.build_result_samples(training_games, team_map)

history = p_model.train(all_samples)

plt.plot(history)
plt.savefig('progress.png')

pcd_ratings = postprocess.amend_pcd_features(team_map, od_ratings, p_model)

with open('pcd_ratings.json', 'w') as f:
    json.dump(pcd_ratings, f, indent=2)

(improvements, corrections, errors) = postprocess.calculate_pcd_improvement(test_games, team_map, l_model, p_model)

avg_improvement = math.sqrt(sum(map(lambda x: x**2, improvements)))/float(len(improvements))

print('Average PCD improvement per game: {}, with {} games called correctly over LLS ({} called incorrectly)'.format(avg_improvement, sum(corrections), sum(errors)))
