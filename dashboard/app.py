import os
import pandas as pd
import psycopg2
import streamlit as st
from dotenv import load_dotenv

# Page configuration
st.set_page_config(page_title="Strava Stats Dashboard", page_icon="🚴‍♂️", layout="wide")

# Load environment variables (Local development)
load_dotenv(dotenv_path='../.env')

# Database connection function
@st.cache_resource
def init_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        database=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

conn = init_connection()

# Data fetching functions
@st.cache_data(ttl=3600) # Cache data for an hour to keep the app snappy
def get_avg_per_ride():
    query = """
        SELECT 
            b.name AS "Bike Name",
            COUNT(r.id) AS "Total Rides",
            ROUND(AVG(r.distance_miles), 2) AS "Avg Miles per Ride",
            ROUND(AVG(r.moving_time_seconds) / 60.0, 1) AS "Avg Minutes per Ride"
        FROM rides r
        JOIN bikes b ON r.bike_id = b.id
        GROUP BY b.name
        ORDER BY "Total Rides" DESC;
    """
    return pd.read_sql_query(query, conn)

@st.cache_data(ttl=3600)
def get_totals_per_year():
    query = """
        SELECT 
            EXTRACT(YEAR FROM r.start_date_local)::INT AS "Year",
            b.name AS "Bike Name",
            COUNT(r.id) AS "Ride Count",
            ROUND(SUM(r.distance_miles), 2) AS "Total Miles",
            ROUND(SUM(r.moving_time_seconds) / 3600.0, 1) AS "Total Hours",
            ROUND(SUM(r.total_elevation_gain_ft), 0) AS "Total Elevation (ft)"
        FROM rides r
        JOIN bikes b ON r.bike_id = b.id
        GROUP BY "Year", b.name
        ORDER BY "Year" DESC, "Total Miles" DESC;
    """
    return pd.read_sql_query(query, conn)

# --- Dashboard UI ---
st.title("🚴‍♂️ Strava Ride Analytics")
st.markdown("Analyzing ride data across different bike profiles.")

# Section 1: Averages per Bike
st.subheader("Averages per Ride (By Bike)")
df_avg = get_avg_per_ride()
st.dataframe(df_avg, use_container_width=True, hide_index=True)

st.divider()

# Section 2: Yearly Totals per Bike
st.subheader("Total Miles & Time (Per Year, By Bike)")
df_totals = get_totals_per_year()

# Create a filter for the Year
years = df_totals['Year'].unique()
selected_year = st.selectbox("Filter by Year:", ['All Time'] + list(years))

if selected_year != 'All Time':
    df_display = df_totals[df_totals['Year'] == selected_year]
else:
    df_display = df_totals

st.dataframe(df_display, use_container_width=True, hide_index=True)