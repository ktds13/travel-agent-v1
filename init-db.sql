-- Initialize PostgreSQL database with pgvector extension

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create countries table
CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create country_aliases table
CREATE TABLE IF NOT EXISTS country_aliases (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    alias VARCHAR(100) NOT NULL UNIQUE
);

-- Create regions table
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL
);

-- Create activities table
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Create places table
CREATE TABLE IF NOT EXISTS places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    country INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    region VARCHAR(200),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    raw_text TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create place_activities junction table
CREATE TABLE IF NOT EXISTS place_activities (
    id SERIAL PRIMARY KEY,
    place_id INTEGER NOT NULL REFERENCES places(id) ON DELETE CASCADE,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    UNIQUE(place_id, activity_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_places_country ON places(country);
CREATE INDEX IF NOT EXISTS idx_places_category ON places(category);
CREATE INDEX IF NOT EXISTS idx_places_embedding ON places USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_country_aliases_country_id ON country_aliases(country_id);
CREATE INDEX IF NOT EXISTS idx_place_activities_place_id ON place_activities(place_id);
CREATE INDEX IF NOT EXISTS idx_place_activities_activity_id ON place_activities(activity_id);

-- Insert some common countries (optional seed data)
INSERT INTO countries (name) VALUES
    ('Thailand'),
    ('Singapore'),
    ('Malaysia'),
    ('Indonesia'),
    ('Vietnam'),
    ('Philippines'),
    ('Japan'),
    ('South Korea'),
    ('China'),
    ('India')
ON CONFLICT (name) DO NOTHING;

-- Insert country aliases (optional seed data)
INSERT INTO country_aliases (country_id, alias)
SELECT c.id, a.alias
FROM countries c
CROSS JOIN (VALUES
    ('Thailand', 'TH'),
    ('Singapore', 'SG'),
    ('Malaysia', 'MY'),
    ('Indonesia', 'ID'),
    ('Vietnam', 'VN'),
    ('Philippines', 'PH'),
    ('Japan', 'JP'),
    ('South Korea', 'KR'),
    ('China', 'CN'),
    ('India', 'IN')
) AS a(country_name, alias)
WHERE c.name = a.country_name
ON CONFLICT (alias) DO NOTHING;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_places_updated_at
    BEFORE UPDATE ON places
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE countries IS 'Countries reference table';
COMMENT ON TABLE country_aliases IS 'Alternative names for countries';
COMMENT ON TABLE places IS 'Travel destinations with vector embeddings';
COMMENT ON TABLE activities IS 'Available activities at places';
COMMENT ON TABLE place_activities IS 'Many-to-many relationship between places and activities';
