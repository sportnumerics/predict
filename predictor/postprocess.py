import copy, math
import numpy as np

def collect_ratings(team_map, rating_function):
    n_teams = len(team_map['indicies_to_teams'])

    results = []

    for i in range(0, n_teams):
        results.append({
            'team': team_map['indicies_to_teams'][i],
            'rating': rating_function(i)
        })

    return sorted(results, key=lambda x: -x['rating'])

def calculate_lls_ratings(team_map, model):
    ratings = model.corrected_ratings()

    def rating_function(i):
        return ratings[i]

    return collect_ratings(team_map, rating_function)

def calculate_lss_offensive_defensive_ratings(team_map, model):
    n_teams = len(team_map['indicies_to_teams'])
    offset = len(team_map['ids_to_indicies'])

    results = {}

    ratings = model.corrected_ratings()

    overall = ratings[0:n_teams] + ratings[offset:n_teams+offset]
    overall = overall - np.amax(overall)

    for i in range(0, n_teams):
        team = team_map['indicies_to_teams'][i]
        results[team['id']] = {
            'team': team,
            'offense': ratings[i],
            'defense': ratings[i+offset],
            'overall': overall[i]
        }

    return results

def calculate_pcd_ratings(team_map, model):
    # rating is determined by how well a team would do if it played all other
    # opponents, in terms of number of wins and score differential

    n_teams = len(team_map['indicies_to_teams'])

    def rating_function(i):
        rating = 0
        for j in range(i, n_teams):
            if (i != j):
                rating += model.predict(i,j) - model.predict(j,i)
        return rating

    return collect_ratings(team_map, rating_function)

def amend_pcd_features(team_map, od_ratings, pcd_model):
    for team in od_ratings['ratings'].values():
        index = team_map['ids_to_indicies'][team['team']['id']]
        team['pcdOffense'] = pcd_model.offensive_factors[:,index].tolist()
        team['pcdDefense'] = pcd_model.defensive_factors[:,index].tolist()
    return od_ratings

def predict_games(samples, team_map, model):
    predictions = []
    for sample in samples:
        prediction = model.predict(sample[0], sample[1])
        predictions.append({
            'team': team_map['indicies_to_teams'][sample[0]],
            'opponent': team_map['indicies_to_teams'][sample[1]],
            'actual': sample[2],
            'predicted': prediction
        })
    return predictions

def calculate_pcd_improvement(games, team_map, lls_model, pcd_model):
    improvements = []
    corrections = []
    errors = []
    for game in games:
        team_index = team_map['ids_to_indicies'][game['team']['id']]
        opponent_index = team_map['ids_to_indicies'][game['opponent']['id']]
        pf = game['result']['pointsFor']
        pa = game['result']['pointsAgainst']
        llsPF = lls_model.predict(team_index, opponent_index)
        llsPA = lls_model.predict(opponent_index, team_index)
        pcdPF = pcd_model.predict(team_index, opponent_index)
        pcdPA = pcd_model.predict(opponent_index, team_index)
        llsError = abs(llsPF - pf) + abs(llsPA - pa)
        pcdError = abs(pcdPF - pf) + abs(pcdPA - pa)
        improvements.append(llsError - pcdError)


        w = math.copysign(1,pf-pa)
        llsW = math.copysign(1,llsPF-llsPA)
        pcdW = math.copysign(1,pcdPF-pcdPA)

        llsCorrect = llsW * w > 0
        pcdCorrect = pcdW * w > 0
        corrections.append(1 if not llsCorrect and pcdCorrect else 0)
        errors.append(1 if not pcdCorrect and llsCorrect else 0)
    return improvements, corrections, errors
