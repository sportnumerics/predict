from predictor import local_persist, s3_persist
import os

if os.environ['STAGE'].lower() == 'local':
    write = local_persist.write
else:
    write = s3_persist.write
