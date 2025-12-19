import os
import urllib.parse
import pg8000.dbapi


def get_connection():
    dsn = os.getenv('DATABASE_URL')
    if not dsn:
        raise RuntimeError('DATABASE_URL not set')
    
    # Parse DATABASE_URL: postgresql://user:password@host:port/dbname
    parsed = urllib.parse.urlparse(dsn)
    conn = pg8000.dbapi.connect(
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/')
    )
    return conn


def query(sql, params=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql, params or ())
            if cur.description:
                # Fetch as dicts
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            conn.commit()
            return []
        finally:
            cur.close()
    finally:
        conn.close()
