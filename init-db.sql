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

-- Create accommodations table
CREATE TABLE IF NOT EXISTS accommodations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(50),  -- hotel, hostel, resort, guesthouse, airbnb, villa
    place_id INTEGER REFERENCES places(id) ON DELETE SET NULL,  -- Link to nearby place
    region VARCHAR(200),
    country INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    price_range VARCHAR(20),  -- budget, mid-range, luxury
    price_min DECIMAL(10,2),
    price_max DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    rating DECIMAL(3,2),  -- 0.00 to 5.00
    amenities TEXT,  -- JSON array of amenities
    description TEXT,
    contact_info TEXT,
    raw_text TEXT,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create amenities table for structured data
CREATE TABLE IF NOT EXISTS amenities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50)  -- wifi, parking, food, facilities, etc.
);

-- Create accommodation_amenities junction table
CREATE TABLE IF NOT EXISTS accommodation_amenities (
    id SERIAL PRIMARY KEY,
    accommodation_id INTEGER NOT NULL REFERENCES accommodations(id) ON DELETE CASCADE,
    amenity_id INTEGER NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    UNIQUE(accommodation_id, amenity_id)
);

-- Create indexes for accommodations
CREATE INDEX IF NOT EXISTS idx_accommodations_type ON accommodations(type);
CREATE INDEX IF NOT EXISTS idx_accommodations_country ON accommodations(country);
CREATE INDEX IF NOT EXISTS idx_accommodations_price_range ON accommodations(price_range);
CREATE INDEX IF NOT EXISTS idx_accommodations_rating ON accommodations(rating);
CREATE INDEX IF NOT EXISTS idx_accommodations_place_id ON accommodations(place_id);
CREATE INDEX IF NOT EXISTS idx_accommodations_location ON accommodations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_accommodations_embedding ON accommodations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);
CREATE INDEX IF NOT EXISTS idx_accommodation_amenities_accommodation_id ON accommodation_amenities(accommodation_id);
CREATE INDEX IF NOT EXISTS idx_accommodation_amenities_amenity_id ON accommodation_amenities(amenity_id);

-- Trigger to update accommodations updated_at
CREATE TRIGGER update_accommodations_updated_at
    BEFORE UPDATE ON accommodations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert common amenities
INSERT INTO amenities (name, category) VALUES
    ('WiFi', 'connectivity'),
    ('Free WiFi', 'connectivity'),
    ('Parking', 'parking'),
    ('Free Parking', 'parking'),
    ('Swimming Pool', 'facilities'),
    ('Gym', 'facilities'),
    ('Spa', 'facilities'),
    ('Restaurant', 'food'),
    ('Breakfast Included', 'food'),
    ('Bar', 'food'),
    ('Air Conditioning', 'comfort'),
    ('Room Service', 'service'),
    ('24-Hour Front Desk', 'service'),
    ('Concierge', 'service'),
    ('Airport Shuttle', 'transport'),
    ('Laundry Service', 'service'),
    ('Pet Friendly', 'policy'),
    ('Family Rooms', 'room-type'),
    ('Non-Smoking Rooms', 'policy'),
    ('Wheelchair Accessible', 'accessibility')
ON CONFLICT (name) DO NOTHING;

-- Sample accommodation data for Chiang Mai area
-- First, get country_id for Thailand
DO $$
DECLARE
    thailand_id INTEGER;
BEGIN
    SELECT id INTO thailand_id FROM countries WHERE name = 'Thailand';
    
    -- Insert sample accommodations near Chiang Mai attractions
    INSERT INTO accommodations (name, type, region, country, latitude, longitude, price_range, price_min, price_max, rating, amenities, description, contact_info, raw_text) VALUES
    
    -- Near Doi Suthep
    ('Mountain View Resort Doi Suthep', 'resort', 'Chiang Mai', thailand_id, 18.8050, 98.9219, 'luxury', 150.00, 300.00, 4.7, '["Free WiFi", "Swimming Pool", "Restaurant", "Spa", "Mountain View"]', 'Luxury resort with stunning mountain views near Doi Suthep temple. Features traditional Thai architecture and modern amenities.', '+66 53 123 456', 'Mountain View Resort near Doi Suthep offers luxury accommodation with beautiful views, swimming pool, spa, and excellent restaurant serving Thai and international cuisine.'),
    
    ('Doi Kham Boutique Hotel', 'hotel', 'Chiang Mai', thailand_id, 18.7234, 98.9456, 'mid-range', 40.00, 80.00, 4.3, '["Free WiFi", "Free Parking", "Breakfast Included", "Garden View"]', 'Charming boutique hotel near Doi Kham temple with peaceful garden setting.', '+66 53 234 567', 'Doi Kham Boutique Hotel is a peaceful mid-range hotel located near the famous Doi Kham temple. The hotel features comfortable rooms with garden views, free breakfast, and parking.'),
    
    ('Suthep Mountain Lodge', 'guesthouse', 'Chiang Mai', thailand_id, 18.8100, 98.9150, 'budget', 15.00, 35.00, 4.0, '["Free WiFi", "Free Parking", "Mountain View"]', 'Budget-friendly guesthouse perfect for hikers and nature lovers near Doi Suthep.', '+66 53 345 678', 'Suthep Mountain Lodge offers affordable accommodation for travelers exploring Doi Suthep. Clean rooms, friendly staff, and great location for hiking.'),
    
    -- Near Doi Inthanon
    ('Inthanon Highland Resort', 'resort', 'Chiang Mai', thailand_id, 18.5550, 98.4880, 'luxury', 200.00, 400.00, 4.8, '["Free WiFi", "Swimming Pool", "Restaurant", "Spa", "Fireplace", "Mountain View"]', 'Premium resort at high altitude near Doi Inthanon National Park with breathtaking views.', '+66 53 456 789', 'Inthanon Highland Resort is a luxury mountain resort offering spectacular views of Doi Inthanon. Features include heated rooms with fireplaces, spa facilities, and gourmet dining.'),
    
    ('Doi Inthanon View Hotel', 'hotel', 'Chiang Mai', thailand_id, 18.5300, 98.4650, 'mid-range', 50.00, 100.00, 4.4, '["Free WiFi", "Restaurant", "Breakfast Included", "Hiking Tours"]', 'Comfortable hotel near Doi Inthanon with tour services to waterfalls and peaks.', '+66 53 567 890', 'Doi Inthanon View Hotel provides comfortable accommodation with easy access to Doi Inthanon National Park. The hotel organizes hiking tours and waterfall visits.'),
    
    -- Near Chiang Dao
    ('Chiang Dao Nest', 'resort', 'Chiang Dao', thailand_id, 19.3620, 98.9640, 'mid-range', 60.00, 120.00, 4.6, '["Free WiFi", "Restaurant", "Pool", "Rice Field View", "Bicycle Rental"]', 'Eco-friendly resort surrounded by rice fields with views of Chiang Dao mountain.', '+66 53 678 901', 'Chiang Dao Nest is an eco-resort set among rice fields with stunning views of Chiang Dao mountain. Offers bicycle tours, organic restaurant, and peaceful atmosphere.'),
    
    ('Doi Luang Homestay', 'guesthouse', 'Chiang Dao', thailand_id, 19.3800, 98.9550, 'budget', 20.00, 40.00, 4.2, '["Free WiFi", "Breakfast Included", "Mountain View", "Local Experience"]', 'Authentic homestay experience with local Karen hill tribe family near Chiang Dao.', '+66 85 123 4567', 'Doi Luang Homestay offers authentic local experience staying with Karen hill tribe family. Simple but clean rooms, home-cooked meals, and cultural immersion near Chiang Dao mountain.'),
    
    -- Near Mae Kampong
    ('Mae Kampong Valley Resort', 'resort', 'Mae On', thailand_id, 18.8670, 99.1350, 'mid-range', 45.00, 90.00, 4.5, '["Free WiFi", "Restaurant", "Waterfall View", "Coffee Plantation Tours"]', 'Charming resort in Mae Kampong village known for coffee plantations and waterfalls.', '+66 53 789 012', 'Mae Kampong Valley Resort is nestled in the famous coffee village of Mae Kampong. Enjoy waterfall hikes, coffee plantation tours, and traditional village atmosphere.'),
    
    ('Kampong Hill Lodge', 'guesthouse', 'Mae On', thailand_id, 18.8620, 99.1400, 'budget', 18.00, 35.00, 4.1, '["Free WiFi", "Breakfast Included", "Forest View"]', 'Cozy lodge in the forest near Mae Kampong waterfall with traditional wooden bungalows.', '+66 86 234 5678', 'Kampong Hill Lodge features traditional wooden bungalows surrounded by forest near Mae Kampong waterfall. Great for nature lovers and budget travelers.'),
    
    -- Near Old City Chiang Mai
    ('Chiang Mai Heritage Hotel', 'hotel', 'Chiang Mai Old City', thailand_id, 18.7883, 98.9853, 'luxury', 100.00, 250.00, 4.7, '["Free WiFi", "Swimming Pool", "Spa", "Restaurant", "Temple Views"]', 'Boutique luxury hotel in Chiang Mai Old City with traditional Lanna architecture.', '+66 53 890 123', 'Chiang Mai Heritage Hotel combines traditional Lanna architecture with modern luxury in the heart of Old City. Close to temples, night markets, and cultural attractions.'),
    
    ('Old City Boutique Hostel', 'hostel', 'Chiang Mai Old City', thailand_id, 18.7900, 98.9900, 'budget', 8.00, 25.00, 4.3, '["Free WiFi", "Common Area", "Breakfast Included", "Walking Tours"]', 'Social hostel perfect for backpackers in the heart of Chiang Mai Old City.', '+66 87 345 6789', 'Old City Boutique Hostel is a vibrant backpacker hostel offering dorms and private rooms. Features include daily walking tours, social events, and rooftop terrace.'),
    
    -- Near Huay Tung Tao Lake
    ('Lake View Villa Huay Tung Tao', 'villa', 'Mae Rim', thailand_id, 18.8450, 98.9050, 'luxury', 180.00, 350.00, 4.8, '["Free WiFi", "Private Pool", "Kitchen", "Lake View", "BBQ"]', 'Private villas with lake views and individual pools near Huay Tung Tao.', '+66 53 901 234', 'Lake View Villa offers luxurious private villas each with its own swimming pool overlooking Huay Tung Tao Lake. Perfect for families and groups seeking privacy and nature.'),
    
    ('Tung Tao Lakeside Resort', 'resort', 'Mae Rim', thailand_id, 18.8400, 98.9100, 'mid-range', 55.00, 110.00, 4.4, '["Free WiFi", "Restaurant", "Lake Access", "Kayaking", "Fishing"]', 'Peaceful resort by Huay Tung Tao Lake with water activities and mountain views.', '+66 53 012 345', 'Tung Tao Lakeside Resort is located directly on Huay Tung Tao Lake offering kayaking, fishing, and swimming. Enjoy fresh seafood at the lakeside restaurant with mountain backdrop.')
    
    ON CONFLICT DO NOTHING;
    
END $$;

COMMENT ON TABLE countries IS 'Countries reference table';
COMMENT ON TABLE country_aliases IS 'Alternative names for countries';
COMMENT ON TABLE places IS 'Travel destinations with vector embeddings';
COMMENT ON TABLE activities IS 'Available activities at places';
COMMENT ON TABLE place_activities IS 'Many-to-many relationship between places and activities';
COMMENT ON TABLE accommodations IS 'Hotels, hostels, resorts and other accommodations near travel destinations';
COMMENT ON TABLE amenities IS 'Available amenities at accommodations';
COMMENT ON TABLE accommodation_amenities IS 'Many-to-many relationship between accommodations and amenities';
