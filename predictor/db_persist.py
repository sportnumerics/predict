import boto3
import os
import json

s3 = boto3.client('s3')
results_bucket = os.environ['RESULTS_BUCKET_NAME']


def persist(year, teams_dict):
    for team_id, team in teams_dict.items():
        key = '{}/{}'.format(year, team_id)
        value = json.dumps(team)
        print('[dry run] setting {} = {}'.format(key, value))
        # s3.put_object(
        #     Bucket=results_bucket,
        #     Key=key,
        #     Body=json.dumps(serialize_rating(rating, dt))
        # )
