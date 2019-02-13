import os
from . import s3_persist, local_persist

persistence = local_persist if 'LOCAL' in os.environ else s3_persist


def team_summary(team):
    return {
        'id': team['id'],
        'name': team['name'],
        'ratings': team['ratings'],
        'record': team['record']
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
    team_lists_by_div = create_team_lists_by_div(teams_dict)

    persist_teams(run_name, year, teams_dict, include_run_name)

    persist_team_lists(run_name, year, team_lists_by_div, include_run_name)
