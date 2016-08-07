import json
import boto3
from datetime import datetime
import io

results_bucket_name = 'sportnumerics-ratings-results'

def upload_to_s3(directory, object):
    object_string = json.dumps(object)
    s3 = boto3.client('s3')
    filename = '{}/ratings.json'.format(directory)
    s3.upload_fileobj(io.BytesIO(object_string), results_bucket_name, filename)
