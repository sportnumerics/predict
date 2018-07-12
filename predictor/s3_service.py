import os
import boto3
import json

s3_client = boto3.client('s3')

def query_all_teams(year):
    results_bucket = os.environ['TEAMS_BUCKET_NAME']
    keys = query_all_teams_keys(year)

    def query_team(key_contents):
        key = key_contents['Key']
        query_args = {
            'Bucket': results_bucket,
            'Key': key
        }

        print('getting {}'.format(key))
        response = s3_client.get_object(**query_args)

        return json.load(response['Body'])

    teams = list(map(query_team, keys))

    return teams


def query_all_teams_keys(year):
    results_bucket = os.environ['TEAMS_BUCKET_NAME']
    season = str(year)
    continuation_token = None
    keys = []
    query_args = {
        'Bucket': results_bucket,
        'Prefix': '{}/teams/'.format(season)
    }
    while True:
        if continuation_token:
            query_args['ContinuationToken'] = continuation_token

        result = s3_client.list_objects_v2(**query_args)
        keys.extend(result['Contents'])
        if 'NextContinuationToken' in result:
            continuation_token = result['NextContinuationToken']
        else:
            break

    return keys


def copy_divisions(run_name, year):
    key = '{}/divisions.json'.format(year)
    source = {
        'Bucket': os.environ['TEAMS_BUCKET_NAME'],
        'Key': key
    }
    s3_resource = boto3.resource('s3')
    dest = s3_resource.Bucket(os.environ['RESULTS_BUCKET_NAME'])
    dest.copy(source, key)
