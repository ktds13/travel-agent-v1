-- Create accommodations table for SQL Server
USE TravelAgentDB;
GO

-- Drop table if exists
IF OBJECT_ID('dbo.accommodations', 'U') IS NOT NULL
    DROP TABLE dbo.accommodations;
GO

-- Create accommodations table
CREATE TABLE accommodations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NOT NULL,
    type NVARCHAR(50),  -- hotel, hostel, resort, guesthouse, villa
    region NVARCHAR(100),
    country NVARCHAR(100) DEFAULT 'Thailand',
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    address NVARCHAR(MAX),
    price_range NVARCHAR(20),  -- budget, mid-range, luxury
    price_min DECIMAL(10, 2),
    price_max DECIMAL(10, 2),
    currency NVARCHAR(10) DEFAULT 'USD',
    rating DECIMAL(3, 2),
    total_reviews INT DEFAULT 0,
    amenities NVARCHAR(MAX),  -- JSON array
    description NVARCHAR(MAX),
    website NVARCHAR(255),
    contact_info NVARCHAR(MAX),  -- JSON object
    check_in_time NVARCHAR(20),
    check_out_time NVARCHAR(20),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);
GO

-- Create indexes
CREATE INDEX idx_accommodations_region ON accommodations(region);
CREATE INDEX idx_accommodations_type ON accommodations(type);
CREATE INDEX idx_accommodations_price_range ON accommodations(price_range);
CREATE INDEX idx_accommodations_rating ON accommodations(rating);
CREATE INDEX idx_accommodations_location ON accommodations(latitude, longitude);
GO

-- Insert sample data
INSERT INTO accommodations (name, type, region, latitude, longitude, price_range, price_min, price_max, rating, amenities, description, contact_info)
VALUES
-- Near Doi Suthep
('Mountain View Resort', 'resort', 'Chiang Mai', 18.8040, 98.9220, 'mid-range', 60, 120, 4.5, 
'["wifi", "pool", "restaurant", "parking", "mountain_view"]',
'Beautiful resort with stunning mountain views near Doi Suthep temple. Perfect for nature lovers.',
'{"phone": "+66-53-123456", "email": "info@mountainview.com"}'),

('Doi Suthep Boutique Hotel', 'hotel', 'Chiang Mai', 18.8050, 98.9210, 'luxury', 150, 300, 4.7,
'["wifi", "pool", "spa", "restaurant", "gym", "mountain_view"]',
'Luxury boutique hotel offering premium amenities and breathtaking temple views.',
'{"phone": "+66-53-234567", "email": "reservations@doisuthephotel.com"}'),

-- Near Doi Kham
('Doi Kham Garden Resort', 'resort', 'Chiang Mai', 18.7380, 98.9050, 'mid-range', 50, 100, 4.4,
'["wifi", "pool", "restaurant", "parking", "garden"]',
'Peaceful resort surrounded by lush gardens and agricultural landscapes of Doi Kham.',
'{"phone": "+66-53-345678", "email": "info@doikhamgarden.com"}'),

('Royal Orchid Villa', 'villa', 'Chiang Mai', 18.7400, 98.9070, 'luxury', 200, 400, 4.8,
'["wifi", "pool", "kitchen", "parking", "garden", "mountain_view"]',
'Exclusive villa with private pool and orchid gardens in the peaceful Doi Kham area.',
'{"phone": "+66-53-456789", "email": "bookings@royalorchid.com"}'),

-- Near Doi Inthanon
('Inthanon Highland Resort', 'resort', 'Chom Thong', 18.5400, 98.4870, 'mid-range', 70, 150, 4.6,
'["wifi", "restaurant", "parking", "mountain_view", "hiking"]',
'Mountain resort near Thailand''s highest peak. Perfect base for exploring Doi Inthanon National Park.',
'{"phone": "+66-53-567890", "email": "info@inthanonhighland.com"}'),

-- Near Chiang Dao
('Chiang Dao Nest', 'guesthouse', 'Chiang Dao', 19.3980, 98.9640, 'budget', 15, 40, 4.3,
'["wifi", "restaurant", "parking", "mountain_view"]',
'Cozy guesthouse popular with trekkers and nature enthusiasts exploring Chiang Dao.',
'{"phone": "+66-53-678901", "email": "stay@chiangdaonest.com"}'),

('Malee''s Nature Lodge', 'resort', 'Chiang Dao', 19.4000, 98.9650, 'mid-range', 45, 90, 4.5,
'["wifi", "pool", "restaurant", "parking", "mountain_view", "hiking"]',
'Eco-friendly lodge offering comfortable rooms and guided mountain treks.',
'{"phone": "+66-53-789012", "email": "info@maleelogde.com"}'),

-- Near Mae Kampong
('Mae Kampong Homestay', 'guesthouse', 'Mae On', 18.8530, 99.1540, 'budget', 20, 50, 4.2,
'["wifi", "parking", "local_experience"]',
'Authentic village homestay experience with local families in beautiful Mae Kampong.',
'{"phone": "+66-89-123456", "email": "maekampong@gmail.com"}'),

('Coffee Valley Resort', 'resort', 'Mae On', 18.8550, 99.1560, 'mid-range', 55, 110, 4.4,
'["wifi", "restaurant", "parking", "coffee_shop", "hiking"]',
'Charming resort nestled among coffee plantations with waterfall views.',
'{"phone": "+66-53-890123", "email": "stay@coffeevalley.com"}'),

-- Old City Chiang Mai
('Old City Boutique Hostel', 'hostel', 'Chiang Mai Old City', 18.7880, 98.9850, 'budget', 8, 25, 4.0,
'["wifi", "shared_kitchen", "common_area", "lockers"]',
'Social hostel in the heart of Old City, walking distance to temples and night markets.',
'{"phone": "+66-53-901234", "email": "hello@oldcityhostel.com"}'),

('Heritage Hotel Chiang Mai', 'hotel', 'Chiang Mai Old City', 18.7900, 98.9870, 'luxury', 120, 250, 4.6,
'["wifi", "pool", "restaurant", "spa", "gym"]',
'Elegant hotel combining traditional Lanna architecture with modern luxury.',
'{"phone": "+66-53-012345", "email": "reservations@heritagechiangmai.com"}'),

-- Near Huay Tung Tao Lake
('Lakeside Bungalows', 'guesthouse', 'Mae Rim', 18.8650, 98.9350, 'budget', 25, 60, 4.1,
'["wifi", "restaurant", "parking", "lake_view"]',
'Simple bungalows with direct lake access, perfect for relaxation and fishing.',
'{"phone": "+66-89-234567", "email": "lakeside@huaytungtao.com"}'),

('Huay Tung Tao Resort & Spa', 'resort', 'Mae Rim', 18.8670, 98.9370, 'luxury', 180, 350, 4.7,
'["wifi", "pool", "spa", "restaurant", "gym", "lake_view", "water_sports"]',
'Premium lakeside resort offering water activities and world-class spa treatments.',
'{"phone": "+66-53-123789", "email": "info@huaytungtaoresort.com"}');
GO

-- Verify data
SELECT COUNT(*) as TotalAccommodations FROM accommodations;
SELECT type, COUNT(*) as Count FROM accommodations GROUP BY type;
GO

PRINT 'Accommodations table created and seeded with 13 sample records!';
