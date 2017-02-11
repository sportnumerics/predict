import json
import boto3
from datetime import datetime
import io
import os

results_bucket_name = os.environ['RESULTS_BUCKET_NAME']

def upload_to_s3(directory, key, object):
    object_string = json.dumps(object)
    s3 = boto3.client('s3')
    filename = '{}/{}'.format(directory, key)
    with open(os.path.join('output',filename), 'w') as f:
        f.write(object_string)
    s3.upload_fileobj(io.BytesIO(object_string), results_bucket_name, filename)
