
from datetime import datetime

def parse_date(date_string):
    if not date_string:
        return None
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")