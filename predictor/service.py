import os
from . import local_service, s3_service

service = local_service if 'LOCAL' in os.environ else s3_service
query_all_teams = service.query_all_teams
