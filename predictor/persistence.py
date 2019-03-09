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
