import requests
import copy

datasource_url = 'http://localhost:3000'
teams_path = '/teams'
schedule_path = '/teams/{team_id}/schedule'

def build_team_map(games):
    ids_to_indicies = {}
    indicies_to_teams = {}
    results = []

    def add_team_if_necessary(team):
        if (team['id'] not in ids_to_indicies):
            index = len(indicies_to_teams)
            ids_to_indicies[team['id']] = index
            indicies_to_teams[index] = team

    def create_result(offensive_team_id, defensive_team_id, result):
        return (ids_to_indicies[offensive_team_id], ids_to_indicies[defensive_team_id], result)

    for game in games.values():
        team = game['team']
        opponent = game['opponent']
        add_team_if_necessary(team)
        add_team_if_necessary(opponent)

        results.append(create_result(team['id'], opponent['id'], game['result']['pointsFor']))
        results.append(create_result(opponent['id'], team['id'], game['result']['pointsAgainst']))

    return {
        'ids_to_indicies': ids_to_indicies,
        'indicies_to_teams': indicies_to_teams,
        'results': results
    }

def get_all_games():
    teams = get_all_teams()

    games = dict()

    for team in teams:
        for game in get_all_games_for_team(team):
            games[id_for_game(game)] = game

    return games

def get_all_teams():
    response = requests.get(datasource_url + teams_path)

    return response.json()['teams']

def id_for_game(game):
    if game['location']['type'] == 'home':
        home_id = game['team']['id']
        away_id = game['opponent']['id']
    else:
        home_id = game['opponent']['id']
        away_id = game['team']['id']
    return '{}_{}_{}'.format(away_id,home_id,game['date'])

def get_all_games_for_team(team):
    url = datasource_url + schedule_path.format(team_id = team['id'])
    print('requesting {}', url)
    response = requests.get(url)

    team_games = response.json()['schedule']

    def team_game_to_game(team_game):
        game = copy.deepcopy(team_game)
        game['team'] = team
        return game

    return map(team_game_to_game, team_games)
