import json

def health_check(event):
    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'ok'})
    }
