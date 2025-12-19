import os
import json


def load_env():
    # placeholder for environment loading
    return {k: v for k, v in os.environ.items()}


def json_response(obj, status=200):
    return {
        'statusCode': status,
        'body': json.dumps(obj)
    }
