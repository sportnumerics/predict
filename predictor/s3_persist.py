import json
import os
import boto3

s3 = boto3.client('s3')
results_bucket = os.environ['RESULTS_BUCKET_NAME']


def write(key, obj):
    s3.put_object(
        Bucket=results_bucket,
        Key=key,
        Body=json.dumps(obj),
        ContentType='application/json'
    )
