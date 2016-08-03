import json, math
from predictor import collect, lls_model, postprocess, upload

games = collect.get_all_games()

games_list = list(games.values())

team_map = collect.build_team_map(games_list)

# offensive defensive model
l_model = lls_model.Model()

coefficients = collect.build_offensive_defensive_coefficient_matrix(games_list, team_map)

constants = collect.build_offensive_defensive_constants(games_list, team_map)

l_model.train(coefficients, constants)

od_ratings = postprocess.calculate_lss_offensive_defensive_ratings(team_map, l_model)

with open('output/last.json','w') as f:
    json.dump(od_ratings, f, indent=2)

upload.upload_to_s3('linear-v1', od_ratings)
