-- Create Bikes Table
-- Strava gear IDs are strings (e.g., 'b1234567')
CREATE TABLE IF NOT EXISTS bikes (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    frame_type VARCHAR(50) -- e.g., Mountain, eBike, Road
);

-- Create Rides Table
CREATE TABLE IF NOT EXISTS rides (
    id BIGINT PRIMARY KEY,
    name VARCHAR(255),
    bike_id VARCHAR(50) REFERENCES bikes(id),
    start_date_local TIMESTAMP,
    distance_miles NUMERIC(8, 2),
    moving_time_seconds INT,
    elapsed_time_seconds INT,
    total_elevation_gain_ft NUMERIC(8, 2),
    average_speed_mph NUMERIC(5, 2),
    max_speed_mph NUMERIC(5, 2),
    average_heartrate NUMERIC(5, 2),
    max_heartrate NUMERIC(5, 2),
    suffer_score NUMERIC(5, 2), -- Strava's effort metric
    kudos_count INT
);

-- Create Weather Table
-- Keeping this separate allows you to easily plug in an external weather API later 
-- if you want historical data beyond what Strava natively captures.
CREATE TABLE IF NOT EXISTS weather (
    ride_id BIGINT PRIMARY KEY REFERENCES rides(id) ON DELETE CASCADE,
    temperature_f NUMERIC(5, 2),
    humidity_percent NUMERIC(5, 2),
    wind_speed_mph NUMERIC(5, 2),
    wind_direction VARCHAR(20),
    conditions VARCHAR(100) -- e.g., 'Sunny', 'Humid', 'Overcast'
);