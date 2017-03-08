import json
import boto3
import io
import os

def write(key, object):
    results_bucket_name = os.environ['RESULTS_BUCKET_NAME']
    
    object_string = json.dumps(object)
    s3 = boto3.client('s3')
    s3.upload_fileobj(io.BytesIO(object_string), results_bucket_name, key)
