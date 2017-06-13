from predictor import local_persist, s3_persist
import os

if os.environ['STAGE'].lower() == 'local':
    write = local_persist.write
else:
    write = s3_persist.write

def persist(year, division, ratings):
    write(
        'years/{year}/divs/{div}/ratings.json'.format(year = year, div = division),
        { 'ratings': ratings })