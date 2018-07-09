import os
import json


def query_all_teams(year):
    teams = []

    dir = os.path.join('bucket', year, 'teams')

    for filename in os.listdir(dir):
        full_filename = os.path.join(dir, filename)
        with open(full_filename, 'r') as f:
            team = json.load(f)
            if 'id' not in team:
                print('{} has no id'.format(filename))

        teams.append(team)

    return teams


def copy_divisions(run_name, year):
    src_filename = os.path.join('bucket', year, 'divisions.json')
    dst_filename = os.path.join('output', run_name, 'divisions.json')

    if not os.path.exists(os.path.dirname(dst_filename)):
        os.makedirs(os.path.dirname(dst_filename))
    with open(src_filename, 'rb') as src, open(dst_filename, 'wb') as dst:
        dst.write(src.read())
