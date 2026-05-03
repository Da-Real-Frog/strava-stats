import os
import requests
import psycopg2
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../.env')

# Strava API settings
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

# Database settings
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_HOST')

def get_strava_token():
    """Requests a fresh access token from Strava."""
    auth_url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token',
        'f': 'json'
    }
    
    print("Requesting fresh Strava access token...")
    response = requests.post(auth_url, data=payload)
    return response.json().get('access_token')

def get_latest_ride_epoch(cur):
    """Finds the most recent ride in the DB and returns an overlapping epoch timestamp."""
    cur.execute("SELECT MAX(start_date_local) FROM rides;")
    latest_date = cur.fetchone()[0]
    
    if latest_date:
        # Subtract 7 days to create a safe overlap window for timezones.
        safe_date = latest_date - timedelta(days=7)
        timestamp = int(safe_date.timestamp())
        print(f"Found existing data. Fetching rides updated after: {safe_date.date()} (Epoch: {timestamp})")
        return timestamp
    
    print("Database is empty. Fetching entire ride history...")
    return 0 

def fetch_new_rides(access_token, after_timestamp):
    """Fetches activities from Strava that occurred after the given timestamp."""
    activities_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + access_token}
    
    all_rides = []
    page = 1
    per_page = 200 
    
    while True:
        param = {'per_page': per_page, 'page': page, 'after': after_timestamp}
        response = requests.get(activities_url, headers=header, params=param)
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.text}")
            break
            
        rides_page = response.json()
        
        if not rides_page:
            break
            
        all_rides.extend(rides_page)
        print(f"Fetched page {page} ({len(rides_page)} rides)...")
        page += 1
        
    print(f"Finished fetching! Found {len(all_rides)} new or overlapping activities.")
    return all_rides

def fetch_gear(access_token, gear_id):
    """Fetches specific bike details from Strava."""
    gear_url = f"https://www.strava.com/api/v3/gear/{gear_id}"
    header = {'Authorization': 'Bearer ' + access_token}
    return requests.get(gear_url, headers=header).json()

def ingest_data():
    conn = None
    try:
        # 1. Connect to Database first
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()
        print("Connected to PostgreSQL database.")
        
        # 2. Get the timestamp to start fetching from
        after_timestamp = get_latest_ride_epoch(cur)
        
        # 3. Authenticate and fetch data
        token = get_strava_token()
        rides = fetch_new_rides(token, after_timestamp)
        
        if not rides:
            print("No new rides to insert. Database is up to date.")
            return

        # 4. Insert data into the database
        known_bikes = set()
        
        for ride in rides:
            if ride.get('type') in ['Ride', 'MountainBikeRide', 'EBikeRide', 'VirtualRide']:
                bike_id = ride.get('gear_id')
                
                # Check and insert the bike if it's new
                if bike_id and bike_id not in known_bikes:
                    cur.execute("SELECT id FROM bikes WHERE id = %s", (bike_id,))
                    if not cur.fetchone():
                        print(f"Fetching details for new bike ID: {bike_id}...")
                        gear_info = fetch_gear(token, bike_id)
                        bike_name = gear_info.get('name', 'Unknown Bike')
                        
                        cur.execute("""
                            INSERT INTO bikes (id, name, frame_type) 
                            VALUES (%s, %s, %s)
                            ON CONFLICT (id) DO NOTHING;
                        """, (bike_id, bike_name, 'Unknown'))
                    known_bikes.add(bike_id)
                
                # Insert or Update the ride
                insert_query = """
                    INSERT INTO rides (
                        id, name, bike_id, start_date_local, distance_miles, 
                        moving_time_seconds, elapsed_time_seconds, total_elevation_gain_ft, 
                        average_speed_mph, max_speed_mph, average_heartrate, max_heartrate, suffer_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        distance_miles = EXCLUDED.distance_miles;
                """
                
                distance_miles = ride.get('distance', 0) * 0.000621371
                elevation_ft = ride.get('total_elevation_gain', 0) * 3.28084
                avg_speed_mph = ride.get('average_speed', 0) * 2.23694
                max_speed_mph = ride.get('max_speed', 0) * 2.23694
                
                cur.execute(insert_query, (
                    ride['id'],
                    ride['name'],
                    bike_id, 
                    ride['start_date_local'],
                    distance_miles,
                    ride['moving_time'],
                    ride['elapsed_time'],
                    elevation_ft,
                    avg_speed_mph,
                    max_speed_mph,
                    ride.get('average_heartrate'),
                    ride.get('max_heartrate'),
                    ride.get('suffer_score')
                ))
        
        conn.commit()
        print("Successfully ingested data into the database.")
        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Database error: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    ingest_data()