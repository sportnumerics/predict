import json
from predictor import collect, lls_model, postprocess, db_persist as persistence
import os

prediction_year = os.environ['PREDICTION_YEAR']

def run(year=prediction_year):
    print('Processing year {}'.format(year))
    for x in [1,2,3]:
        run_division(year, x)

def run_division(year, division=1):
    games = collect.get_all_games(year, division)

    games_list = list(games.values())

    team_map = collect.build_team_map(games_list)

    # offensive defensive model
    l_model = lls_model.Model()

    coefficients = collect.build_offensive_defensive_coefficient_matrix(games_list, team_map)

    constants = collect.build_offensive_defensive_constants(games_list, team_map)

    l_model.train(coefficients, constants)

    od_ratings = postprocess.calculate_lss_offensive_defensive_ratings(team_map, l_model)

    persistence.persist(year, division, od_ratings)

    print('Done processing division {}'.format(division))
