import json
import re
from app import db, models


def list_packages(event):
    try:
        qs_params = event.get('queryStringParameters') or {}
        limit = int(qs_params.get('limit', 50))
        packages = models.list_packages(db.query, limit)
        return {
            'statusCode': 200,
            'body': json.dumps([dict(p) for p in packages], default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def get_package(event):
    try:
        # Extract ID from path: /packages/{id}
        path = event.get('path', '')
        match = re.match(r'^/packages/([^/]+)$', path)
        package_id = match.group(1) if match else None
        
        if not package_id:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing package ID'})}
        
        package = models.fetch_package(db.query, package_id)
        if not package:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Package not found'})}
        
        return {
            'statusCode': 200,
            'body': json.dumps(dict(package), default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def create_package(event):
    try:
        body = json.loads(event.get('body', '{}'))
        tracking_number = body.get('tracking_number')
        status = body.get('status', 'pending')
        origin = body.get('origin')
        destination = body.get('destination')
        weight_kg = body.get('weight_kg')
        
        if not all([tracking_number, origin, destination]):
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}
        
        package = models.create_package(db.query, tracking_number, status, origin, destination, weight_kg)
        return {
            'statusCode': 201,
            'body': json.dumps(dict(package), default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def update_package(event):
    try:
        # Extract ID from path
        path = event.get('path', '')
        match = re.match(r'^/packages/([^/]+)$', path)
        package_id = match.group(1) if match else None
        body = json.loads(event.get('body', '{}'))
        status = body.get('status')
        
        if not package_id or not status:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required fields'})}
        
        package = models.update_package_status(db.query, package_id, status)
        if not package:
            return {'statusCode': 404, 'body': json.dumps({'error': 'Package not found'})}
        
        return {
            'statusCode': 200,
            'body': json.dumps(dict(package), default=str)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
