# Minimal SQL queries; avoid heavy ORMs

# Packages
GET_PACKAGE_BY_ID = "SELECT * FROM packages WHERE id = %s;"
LIST_PACKAGES = "SELECT * FROM packages ORDER BY created_at DESC LIMIT %s;"
CREATE_PACKAGE = """
    INSERT INTO packages (tracking_number, status, origin, destination, weight_kg, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW())
    RETURNING *;
"""
UPDATE_PACKAGE_STATUS = "UPDATE packages SET status = %s, updated_at = NOW() WHERE id = %s RETURNING *;"

# Scans
LIST_SCANS_RECENT = "SELECT * FROM scans ORDER BY created_at DESC LIMIT %s;"
GET_SCANS_BY_PACKAGE = "SELECT * FROM scans WHERE package_id = %s ORDER BY created_at DESC;"
CREATE_SCAN = """
    INSERT INTO scans (package_id, location, scan_type, created_at)
    VALUES (%s, %s, %s, NOW())
    RETURNING *;
"""


def fetch_package(conn_query, package_id):
    rows = conn_query(GET_PACKAGE_BY_ID, (package_id,))
    return rows[0] if rows else None


def list_packages(conn_query, limit=50):
    return conn_query(LIST_PACKAGES, (limit,))


def create_package(conn_query, tracking_number, status, origin, destination, weight_kg):
    rows = conn_query(CREATE_PACKAGE, (tracking_number, status, origin, destination, weight_kg))
    return rows[0] if rows else None


def update_package_status(conn_query, package_id, status):
    rows = conn_query(UPDATE_PACKAGE_STATUS, (status, package_id))
    return rows[0] if rows else None


def list_recent_scans(conn_query, limit=50):
    return conn_query(LIST_SCANS_RECENT, (limit,))


def get_scans_by_package(conn_query, package_id):
    return conn_query(GET_SCANS_BY_PACKAGE, (package_id,))


def create_scan(conn_query, package_id, location, scan_type):
    rows = conn_query(CREATE_SCAN, (package_id, location, scan_type))
    return rows[0] if rows else None
