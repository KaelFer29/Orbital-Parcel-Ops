"""Seed script for populating test data"""

import os
import psycopg2
from psycopg2.extras import execute_values


def main():
    dsn = os.getenv('DATABASE_URL')
    if not dsn:
        print("❌ DATABASE_URL not set")
        return
    
    print("🌱 Seeding database...")
    
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    
    # Seed packages (10 total)
    packages = [
        ('PKG-001', 'in_transit', 'New York, NY', 'Los Angeles, CA', 2.5),
        ('PKG-002', 'pending', 'Chicago, IL', 'Houston, TX', 1.2),
        ('PKG-003', 'delivered', 'Miami, FL', 'Seattle, WA', 3.8),
        ('PKG-004', 'in_transit', 'Boston, MA', 'Denver, CO', 0.9),
        ('PKG-005', 'pending', 'San Francisco, CA', 'Austin, TX', 1.8),
        ('PKG-006', 'in_transit', 'Portland, OR', 'Phoenix, AZ', 4.2),
        ('PKG-007', 'delivered', 'Dallas, TX', 'Atlanta, GA', 2.1),
        ('PKG-008', 'in_transit', 'Philadelphia, PA', 'San Diego, CA', 3.5),
        ('PKG-009', 'pending', 'Detroit, MI', 'Las Vegas, NV', 1.6),
        ('PKG-010', 'delivered', 'Minneapolis, MN', 'Orlando, FL', 2.9),
    ]
    
    execute_values(
        cur,
        "INSERT INTO packages (tracking_number, status, origin, destination, weight_kg) VALUES %s ON CONFLICT (tracking_number) DO NOTHING",
        packages
    )
    
    # Get package IDs for scans
    cur.execute("SELECT id, tracking_number FROM packages ORDER BY id")
    package_map = {row[1]: row[0] for row in cur.fetchall()}
    
    # Seed scans
    scans = [
        (package_map.get('PKG-001'), 'New York Hub', 'departure'),
        (package_map.get('PKG-001'), 'Philadelphia Hub', 'checkpoint'),
        (package_map.get('PKG-003'), 'Miami Hub', 'departure'),
        (package_map.get('PKG-003'), 'Seattle Hub', 'arrival'),
        (package_map.get('PKG-003'), 'Seattle Distribution', 'delivered'),
        (package_map.get('PKG-004'), 'Boston Hub', 'departure'),
        (package_map.get('PKG-006'), 'Portland Hub', 'departure'),
        (package_map.get('PKG-006'), 'Sacramento Hub', 'checkpoint'),
        (package_map.get('PKG-007'), 'Dallas Hub', 'departure'),
        (package_map.get('PKG-007'), 'Atlanta Hub', 'arrival'),
        (package_map.get('PKG-007'), 'Atlanta Distribution', 'delivered'),
        (package_map.get('PKG-008'), 'Philadelphia Hub', 'departure'),
        (package_map.get('PKG-010'), 'Minneapolis Hub', 'departure'),
        (package_map.get('PKG-010'), 'Orlando Hub', 'arrival'),
        (package_map.get('PKG-010'), 'Orlando Distribution', 'delivered'),
    ]
    
    execute_values(
        cur,
        "INSERT INTO scans (package_id, location, scan_type) VALUES %s",
        [s for s in scans if s[0] is not None]
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("✅ Database seeded successfully")


if __name__ == '__main__':
    main()
