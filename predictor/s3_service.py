import os
import requests
import copy

datasource_url = os.environ['DATASOURCE_HOST']
teams_path = '/years/{year}/divs/{div_id}/teams'
schedule_path = '/years/{year}/teams/{team_id}/schedule'


def get_all_teams(year, division):
    response = requests.get(datasource_url + teams_path.format(year = year, div_id = division))

    return response.json()['teams']

def get_all_games_for_team(year, team):
    url = datasource_url + schedule_path.format(year = year, team_id = team['id'])
    response = requests.get(url)

    team_games = response.json()['schedule']

    def team_game_to_game(team_game):
        game = copy.deepcopy(team_game)
        game['team'] = team
        return game

    return map(team_game_to_game, team_games)

def get_all_games(year, division, id_for_game):
    teams = get_all_teams(year, division)

    games = dict()

    for team in teams:
        for game in get_all_games_for_team(year, team):
            games[id_for_game(game)] = game

    return {k:v for k,v in games.iteritems() if 'result' in v}