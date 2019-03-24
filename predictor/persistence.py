import os
from . import s3_persist, local_persist, util

persistence = local_persist if 'LOCAL' in os.environ else s3_persist


def team_summary(team):
    return {
        'id': team['id'],
        'name': team['name'],
        'ratings': team['ratings'],
        'record': team['record']
    }

def team_summaries_by_div(teams_by_div):
    team_lists_by_div = {}

    for div_id, teams in teams_by_div.items():
        team_lists_by_div[div_id] = {
            'id': div_id,
            'teams': list(map(team_summary, teams))
        }

    return team_lists_by_div


def split_teams_into_divs(teams_dict):
    teams_by_div = {}

    for team_id, team in teams_dict.items():
        if 'ratings' not in team:
            continue
        div_teams = teams_by_div.setdefault(team['div'], [])
        div_teams.append(team)

    for div_id, div_teams in teams_by_div.items():
        for i, team in enumerate(sorted(div_teams, key=lambda x: -x['ratings']['overall'])):
            team['rank'] = i + 1

    return teams_by_div


def persist_teams(run_name, year, teams_dict, include_run_name=False):
    for team_id, team in teams_dict.items():
        prefix = run_name if include_run_name else year
        key = '{}/teams/{}.json'.format(prefix, team_id)
        persistence.write(key, team)


def persist_team_lists(run_name,
                       year,
                       team_lists_by_div,
                       include_run_name=False):
    for div_id, div in team_lists_by_div.items():
        prefix = run_name if include_run_name else year
        key = '{}/divs/{}.json'.format(prefix, div_id)
        persistence.write(key, div)


def persist(run_name, year, teams_dict, include_run_name):
    teams_by_div = split_teams_into_divs(teams_dict)

    team_summaries = team_summaries_by_div(teams_by_div)

    persist_teams(run_name, year, teams_dict, include_run_name)

    persist_team_lists(run_name, year, team_summaries, include_run_name)


def enrich_game_team_with_team(game_team, teams_dict):
    team_id = game_team['id']
    if team_id in teams_dict:
        team = teams_dict[team_id]
        if 'rank' in team:
            game_team['rank'] = team['rank']
        if 'ratings' in team:
            game_team['ratings'] = team['ratings']
        game_team['div'] = team['div']


def add_team_info_to_games(games_list, teams_dict):
    for game in games_list:
        enrich_game_team_with_team(game['team'], teams_dict)
        enrich_game_team_with_team(game['opponent'], teams_dict)


def game_divs(game):
    divs = set()
    if 'div' in game['team']:
        divs.add(game['team']['div'])
    if 'div' in game['opponent']:
        divs.add(game['opponent']['div'])
    if len(divs) == 2:
        divs.add('cross_divisional')
    return divs

def split_games_by_div_and_day(games_list):
    result = {}
    for game in games_list:
        game_date = util.parse_date(game['date'])
        divs = game_divs(game)
        for div in divs:
            div = result.setdefault(div, {})
            day = div.setdefault(game_date.date().isoformat(), [])
            day.append(game)
    return result

def persist_upcoming_games(run_name, year, games_list, teams_dict, include_run_name=False):
    add_team_info_to_games(games_list, teams_dict)
    games_by_div_and_day = split_games_by_div_and_day(games_list)
    prefix = run_name if include_run_name else year
    for div, games_by_day in games_by_div_and_day.items():
        index = {d: len(g) for (d, g) in games_by_day.items()}
        persistence.write('{}/divs/{}/games/index.json'.format(prefix, div), index)
        for day, games in games_by_day.items():
            key = '{}/divs/{}/games/{}.json'.format(prefix, div, day)
            persistence.write(key, games)
