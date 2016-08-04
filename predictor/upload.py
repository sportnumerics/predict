import json
import boto3
import os
from datetime import datetime
import io

results_bucket_name = 'sportnumerics-ratings-results'

def upload_to_s3(directory, object):
    object_string = json.dumps(object)
    s3 = boto3.client('s3')
    dt = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = '{}/{}.json'.format(directory, dt)
    s3.upload_fileobj(io.BytesIO(object_string), results_bucket_name, filename)
