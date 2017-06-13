import os
import boto3
import copy
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
teams_table = dynamodb.Table(os.environ['TEAMS_TABLE_NAME'])

def parse_results(result):
    return {
        'pointsFor': int(result['pointsFor']),
        'pointsAgainst': int(result['pointsAgainst'])
    }

def get_all_games(year, division, id_for_game):
    teams = query_all_teams(year, division)

    def team_to_games(acc, team):
        def team_game_to_game(team_game):
            game = copy.deepcopy(team_game)
            game['team'] = team['team']
            if 'result' in game:
                game['result'] = parse_results(game['result'])
            return game

        acc.update({
            id_for_game(game):game
            for game
            in map(team_game_to_game, team['schedule'])
            if 'result' in game
        })
        return acc

    games = reduce(team_to_games, teams, dict())
    print 'Obtained games:', games
    return games

def query_all_teams(year, division):
    season = str(year)
    div = str(division)
    last_evaluated_key = None
    items = []
    query_args = {
        'IndexName': 'schedule',
        'KeyConditionExpression': Key('season').eq(season) & Key('div').eq(div)
    }
    while True:
        if last_evaluated_key:
            query_args['LastEvaluatedKey'] = last_evaluated_key
        elif 'LastEvaluatedKey' in query_args:
            del query_args['LastEvaluatedKey']

        result = teams_table.query(**query_args)
        items.extend(result['Items'])
        if 'LastEvaluatedKey' in result:
            last_evaluated_key = result['LastEvaluatedKey']
        else:
            break

    return items
