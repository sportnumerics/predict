import json, math
from predictor import collect, model, postprocess

# games = collect.get_all_games()
games = []
with open('games.json') as f:
    games = json.load(f)

team_map = collect.build_team_map(games)

with open('team_map.json','w') as f:
    json.dump(team_map, f, indent=2)

model = model.Model(5, len(team_map['ids_to_indicies']))

all_samples = team_map['results']

bp = math.floor(2*len(all_samples)/3)

training_set = all_samples[:bp]
test_set = all_samples[bp:]

model.train(training_set)

ratings = postprocess.calculate_ratings(team_map, model)

with open('ratings.json', 'w') as f:
    json.dump(ratings, f, indent=2)
