import json
import os


def write(key, obj):
    filename = os.path.join('output', key)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=2)
