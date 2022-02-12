import math
import numpy as np
from datetime import datetime
from . import utc
from . import collect

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

    hfa = ratings[2*n_teams]

    for i in range(0, n_teams):
        team = team_map['indicies_to_teams'][i]
        results[team['id']] = {
            'offense': ratings[i],
            'defense': ratings[i+offset],
            'overall': overall[i],
            'hfa': hfa
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
                rating += model.predict(i, j) - model.predict(j, i)
        return rating

    return collect_ratings(team_map, rating_function)


def amend_pcd_features(team_map, od_ratings, pcd_model):
    for team in od_ratings['ratings'].values():
        index = team_map['ids_to_indicies'][team['team']['id']]
        team['pcdOffense'] = pcd_model.offensive_factors[:, index].tolist()
        team['pcdDefense'] = pcd_model.defensive_factors[:, index].tolist()
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

        w = math.copysign(1, pf-pa)
        llsW = math.copysign(1, llsPF-llsPA)
        pcdW = math.copysign(1, pcdPF-pcdPA)

        llsCorrect = llsW * w > 0
        pcdCorrect = pcdW * w > 0
        corrections.append(1 if not llsCorrect and pcdCorrect else 0)
        errors.append(1 if not pcdCorrect and llsCorrect else 0)
    return improvements, corrections, errors


def merge_results_with_teams_dict(teams_dict, od_results, groups):
    dt = datetime.now(utc.utc).isoformat()

    for team_id, result in od_results.items():
        result['groupId'] = collect.group_for_team(groups, team_id)['id']
        result['timestamp'] = dt
        if team_id in teams_dict:
            teams_dict[team_id]['ratings'] = result

    return teams_dict


def unseen_games_from_seen_games(all_games, training_games):
    unseen_games = {k:v for (k,v) in all_games.items() if 'result' in v}
    seen_games = {k:v for (k,v) in training_games.items() if 'result' in v}

    print('culling {} seen games from {} total games'.format(
        len(seen_games),
        len(all_games)))

    for game_id, game in seen_games.items():
        if game_id in unseen_games:
            del unseen_games[game_id]

    return unseen_games


def error_per_unseen_game(teams_dict, seen_games):
    total_squared_error = 0
    score_count = 0
    errors = []
    correct_count = 0

    print('evaluating error for {} teams'.format(len(teams_dict)))

    all_games = collect.get_all_games(teams_dict.values())

    unseen_games = unseen_games_from_seen_games(all_games, seen_games)

    for game_id, game in unseen_games.items():
        if (game['team']['id'] not in teams_dict or
                game['opponent']['id'] not in teams_dict) or game_result_is_a_tie(game['result']):
            continue

        home_team = teams_dict[game['team']['id']]
        away_team = teams_dict[game['opponent']['id']]

        if 'ratings' not in home_team or 'ratings' not in away_team:
            continue

        if home_team['ratings']['groupId'] != away_team['ratings']['groupId']:
            continue

        actual_points_home = game['result']['pointsFor']
        actual_points_away = game['result']['pointsAgainst']

        home_team_predicted_points = (home_team['ratings']['offense']
                                      - away_team['ratings']['defense']
                                      + home_team['ratings']['hfa'])
        away_team_predicted_points = (away_team['ratings']['offense']
                                      - home_team['ratings']['defense']
                                      - away_team['ratings']['hfa'])
        game['predicted'] = {}
        game['predicted']['pointsFor'] = home_team_predicted_points
        game['predicted']['pointsAgainst'] = away_team_predicted_points

        home_points_error = abs(actual_points_home
                                - home_team_predicted_points)

        away_points_error = abs(actual_points_away
                                - away_team_predicted_points)

        errors.append(home_points_error)
        errors.append(away_points_error)

        error = (home_points_error**2
                 + away_points_error**2)

        total_squared_error += error
        score_count += 2

        game['error'] = math.sqrt(error / 2)

        if ((actual_points_home - actual_points_away) * (home_team_predicted_points - away_team_predicted_points) > 0):
            correct_count += 1

    average_error = math.sqrt(total_squared_error / score_count)

    games_sorted_by_error = sorted(unseen_games.values(),
                                   key=lambda x: x.get('error', 0),
                                   reverse=True)

    return (average_error, errors, score_count/2, games_sorted_by_error, correct_count)

def game_result_is_a_tie(result):
    return ((result['pointsFor'] == 1 and result['pointsAgainst'] == 0) or
        (result['pointsFor'] == 0 and result['pointsAgainst'] == 1) or
        (result['pointsFor'] == 0 and result['pointsAgainst'] == 0))