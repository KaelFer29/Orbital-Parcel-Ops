-- Schema for Orbital Parcel Ops
-- PostgreSQL migration

-- Packages table
CREATE TABLE IF NOT EXISTS packages (
    id SERIAL PRIMARY KEY,
    tracking_number VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    origin VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    weight_kg DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_packages_tracking ON packages(tracking_number);
CREATE INDEX idx_packages_status ON packages(status);

-- Scans table
CREATE TABLE IF NOT EXISTS scans (
    id SERIAL PRIMARY KEY,
    package_id INTEGER NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    location VARCHAR(200) NOT NULL,
    scan_type VARCHAR(50) NOT NULL DEFAULT 'checkpoint',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scans_package ON scans(package_id);
CREATE INDEX idx_scans_created ON scans(created_at DESC);

-- Trigger to update packages.updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_packages_updated_at BEFORE UPDATE
    ON packages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
