import numpy as np
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

    return coo_matrix((data, (i, j)))


def build_offensive_defensive_constants(games, team_map):
    return np.array([
        p for g in games
        for p in (g['result']['pointsFor'], g['result']['pointsAgainst'])
    ])


def id_for_game(game):
    if game['location']['type'] == 'home':
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
