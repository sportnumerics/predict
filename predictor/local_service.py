import os
import json


def query_all_teams(year):
    teams = []

    dir = os.path.join('bucket', year)

    for filename in os.listdir(dir):
        full_filename = os.path.join(dir, filename)
        with open(full_filename, 'r') as f:
            team = json.load(f)
            if 'id' not in team:
                print('{} has no id'.format(filename))

        teams.append(team)

    return teams
