import json
import boto
import os
from datetime import datetime
import io

results_bucket_name = 'sportnumerics-ratings-results'

def upload_to_s3(directory, object):
    object_string = json.dumps(object)
    conn = boto.connect_s3(os.environ['AWS_ID'],os.environ['AWS_SECRET'])
    dt = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = '{}/{}.json'.format(directory, dt)
    bucket = conn.get_bucket(results_bucket_name, validate=False)
    key = boto.s3.key.Key(bucket)
    key.key = filename
    key.set_contents_from_string(object_string)
