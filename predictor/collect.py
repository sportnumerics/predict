import numpy as np
import copy
from . import util
from scipy.sparse import coo_matrix


def build_team_map(games):
    ids_to_indicies = {}
    indicies_to_teams = {}

    def add_team_if_necessary(team):
        if (team['id'] not in ids_to_indicies):
            index = len(indicies_to_teams)
            ids_to_indicies[team['id']] = index
            indicies_to_teams[index] = team

    for game in games:
        if 'result' not in game:
            continue
        team = game['team']
        opponent = game['opponent']
        add_team_if_necessary(team)
        add_team_if_necessary(opponent)

    return {
        'ids_to_indicies': ids_to_indicies,
        'indicies_to_teams': indicies_to_teams
    }


def build_result_samples(games, team_map):
    results = []
    ids_to_indicies = team_map['ids_to_indicies']

    def create_result(offensive_team_id, defensive_team_id, result):
        return (ids_to_indicies[offensive_team_id],
                ids_to_indicies[defensive_team_id],
                result)

    for game in games:
        team = game['team']
        opponent = game['opponent']

        results.append(
            create_result(
                team['id'],
                opponent['id'],
                game['result']['pointsFor']))
        results.append(
            create_result(
                opponent['id'],
                team['id'],
                game['result']['pointsAgainst']))

    return results


def build_overall_coeffient_matrix(games, team_map):
    ids_to_indicies = team_map['ids_to_indicies']

    data = [1, -1]*len(games)
    i = [i for g in range(0, len(games)) for i in (g, g)]
    j = [ids_to_indicies[i]
         for game in games
         for i in (
             game['team']['id'],
             game['opponent']['id'])]

    return coo_matrix((data, (i, j)))


def build_overall_constants(games, team_map):
    return np.array([
        g['result']['pointsFor'] - g['result']['pointsAgainst']
        for g in games])


def build_offensive_defensive_coefficient_matrix(games, team_map):
    ids_to_indicies = team_map['ids_to_indicies']

    hfa_factors = [hfa for g in games for hfa in ((1, -1) if g['location']['type'] == 'home' else (-1, 1))]
    hfa_i = [i for i in range(0, 2*len(games))]
    hfa_j = [2*len(ids_to_indicies)]*(2*len(games))

    data = [1, -1, 1, -1]*len(games)
    i = [i for g in range(0, 2*len(games)) for i in (g, g)]

    def offensive_offset(id):
        return ids_to_indicies[id]

    def defensive_offset(id):
        return len(ids_to_indicies) + ids_to_indicies[id]

    j = [k for game in games
         for k in (
                offensive_offset(game['team']['id']),
                defensive_offset(game['opponent']['id']),
                offensive_offset(game['opponent']['id']),
                defensive_offset(game['team']['id']))]

    return coo_matrix((data + hfa_factors, (i + hfa_i, j + hfa_j)), shape=(2*len(games), 2*len(ids_to_indicies)+1))


def build_offensive_defensive_constants(games, team_map):
    return np.array([
        p for g in games
        for p in (g['result']['pointsFor'], g['result']['pointsAgainst'])
    ])


def id_for_game(game):
    # if game['location']['type'] == 'home':
    if game['team']['id'] < game['opponent']['id']:
        home_id = game['team']['id']
        away_id = game['opponent']['id']
    else:
        home_id = game['opponent']['id']
        away_id = game['team']['id']

    return '{}_{}_{}'.format(away_id, home_id, game['date'])


def build_teams_dictionary(teams):
    teams_dict = {}

    for team in teams:
        if 'id' in team:
            teams_dict[team['id']] = team
        else:
            print('warning: team without id?: {}'.format(team))

    return teams_dict


def parse_results(result):
    return {
        'pointsFor': int(result['pointsFor']),
        'pointsAgainst': int(result['pointsAgainst'])
    }


def record_from_schedule(schedule):
    wins = 0
    losses = 0
    ties = 0

    for game in schedule:
        if 'result' not in game:
            continue

        result = game['result']

        if result['pointsFor'] > result['pointsAgainst']:
            wins += 1
        elif result['pointsAgainst'] > result['pointsFor']:
            losses += 1
        else:
            ties += 1

    return {
        'wins': wins,
        'losses': losses,
        'ties': ties
    }

def get_all_games(teams, from_date=None):
    games = {}

    for team in teams:
        if 'schedule' not in team:
            continue

        def team_game_to_game(team_game):
            game = copy.deepcopy(team_game)
            game['team'] = {
                'id': team['id'],
                'name': team['name']
            }
            game_date = util.parse_date(game['date'])
            if 'result' in game:
                if not from_date or game_date < from_date:
                    game['result'] = parse_results(game['result'])
                else:
                    del game['result']
            return game

        for team_game in team['schedule']:
            game = team_game_to_game(team_game)
            games[id_for_game(game)] = game

        team['record'] = record_from_schedule(team['schedule'])

    return games


def group_teams_by_games(game_list):
    groups = []

    for game in game_list:
        if 'result' not in game:
            continue
        team_id = game['team']['id']
        opponent_id = game['opponent']['id']
        team_group = group_for_team(groups, team_id)
        opponent_group = group_for_team(groups, opponent_id)
        if (team_group is None and opponent_group is None):
            groups.append({
                'id': len(groups),
                'games': [game],
                'teamIds': set([team_id, opponent_id])
            })
        elif (team_group is None):
            opponent_group['games'].append(game)
            opponent_group['teamIds'].add(team_id)
        elif (opponent_group is None):
            team_group['games'].append(game)
            team_group['teamIds'].add(opponent_id)
        elif (team_group == opponent_group):
            team_group['games'].append(game)
        else:
            groups.remove(opponent_group)
            team_group['games'].append(game)
            team_group['games'].extend(opponent_group['games'])
            team_group['teamIds'].update(opponent_group['teamIds'])

    return groups


def group_for_team(groups, team_id):
    for group in groups:
        if team_id in group['teamIds']:
            return group
    return None
