import json
import os
import boto3

s3 = boto3.client('s3')


def write(key, obj):
    results_bucket = os.environ['RESULTS_BUCKET_NAME']
    s3.put_object(
        Bucket=results_bucket,
        Key=key,
        Body=json.dumps(obj),
        ContentType='application/json'
    )
