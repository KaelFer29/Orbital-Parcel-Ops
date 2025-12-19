import json
from app.handlers import ops, packages, scans


def lambda_handler(event, context):
    """
    Simple router for Lambda HTTP integration with API Gateway
    """
    path = event.get('path', '/')
    method = event.get('httpMethod', 'GET')
    
    # Health check
    if path == '/health':
        return ops.health_check(event)
    
    # Packages endpoints
    if path == '/packages':
        if method == 'GET':
            return packages.list_packages(event)
        elif method == 'POST':
            return packages.create_package(event)
    
    if path.startswith('/packages/'):
        if method == 'GET':
            return packages.get_package(event)
        elif method == 'PUT' or method == 'PATCH':
            return packages.update_package(event)
    
    # Scans endpoints
    if path == '/scans':
        if method == 'GET':
            return scans.list_scans(event)
        elif method == 'POST':
            return scans.record_scan(event)
    
    return {
        'statusCode': 404,
        'body': json.dumps({'message': 'Not Found'})
    }