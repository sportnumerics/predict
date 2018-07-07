import os
from . import s3_persist, local_persist

persistence = local_persist if os.environ['LOCAL'] else s3_persist


def team_summary(team):
    return {
        'id': team['id'],
        'name': team['name'],
        'ratings': team['ratings']
    }


def create_team_lists_by_div(teams_dict):
    team_lists_by_div = {}

    for team_id, team in teams_dict.items():
        if 'ratings' not in team:
            continue
        div = team['div']
        if div not in team_lists_by_div:
            team_lists_by_div[div] = {
                'id': div,
                'teams': []
            }

        team_lists_by_div[div]['teams'].append(team_summary(team))

    return team_lists_by_div


def persist_teams(run_name, year, teams_dict):
    for team_id, team in teams_dict.items():
        key = '{}/team/{}/{}.json'.format(run_name, year, team_id)
        persistence.write(key, team)


def persist_team_lists(run_name, year, team_lists_by_div):
    for div_id, div in team_lists_by_div.items():
        key = '{}/div/{}.json'.format(run_name, div_id)
        persistence.write(key, div)


def persist(run_name, year, teams_dict):
    team_lists_by_div = create_team_lists_by_div(teams_dict)

    persist_teams(run_name, year, teams_dict)

    persist_team_lists(run_name, year, team_lists_by_div)