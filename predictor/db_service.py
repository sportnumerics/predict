import os
import boto3
import copy
import json

s3 = boto3.client('s3')
results_bucket = os.environ['RESULTS_BUCKET_NAME']


def parse_results(result):
    return {
        'pointsFor': int(result['pointsFor']),
        'pointsAgainst': int(result['pointsAgainst'])
    }


def get_all_games(teams, id_for_game):
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
            if 'result' in game:
                game['result'] = parse_results(game['result'])
            return game

        for team_game in team['schedule']:
            game = team_game_to_game(team_game)
            if 'result' in game:
                games[id_for_game(game)] = game

    return games


def query_all_teams(year):
    keys = query_all_teams_keys(year)

    def query_team(key_contents):
        key = key_contents['Key']
        query_args = {
            'Bucket': results_bucket,
            'Key': key
        }

        print('getting {}'.format(key))
        response = s3.get_object(**query_args)

        return json.load(response['Body'])

    teams = list(map(query_team, keys))

    return teams


def query_all_teams_keys(year):
    season = str(year)
    continuation_token = None
    keys = []
    query_args = {
        'Bucket': results_bucket,
        'Prefix': '{}/'.format(season)
    }
    while True:
        if continuation_token:
            query_args['ContinuationToken'] = continuation_token

        result = s3.list_objects_v2(**query_args)
        keys.extend(result['Contents'])
        if 'NextContinuationToken' in result:
            continuation_token = result['NextContinuationToken']
        else:
            break

    return keys
