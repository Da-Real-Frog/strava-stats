# Strava Stats Dashboard 🚴‍♂️📊

Experimeneting with my Strava data

** Well, my ultimate goal was to start using AI/LLM to look at my data, and starva just gave me an easy button by publising an MCP, so i will switch gear and start integrating it, might make a new project...

*** This is 90% vibe coode, so beware as I can guarantee it is unsecure and unreliable **

## 🏗 Architecture

The project is built with a modular, containerized architecture:

1. **Data Warehouse (PostgreSQL):** Acts as the central hub for all structured data, including relational mapping between rides, specific gear (bikes), and future weather data.
2. **Data Ingestion Pipeline (Python):** A robust script that interacts with the Strava v3 API. It handles OAuth 2.0 token refreshes, incremental data loading (to avoid duplicate API calls), and historical backfilling.
3. **Frontend Dashboard (Streamlit):** A containerized Python web application that serves interactive tables and data visualizations, showing metrics like average miles/time per ride and total miles/time per year, seamlessly categorized by bike.

## 🛠 Tech Stack
* **Language:** Python 3.11+
* **Database:** PostgreSQL 15 (Alpine)
* **Frontend:** Streamlit & Pandas
* **Infrastructure:** Docker & Docker Compose
* **API:** Strava API v3

## 📂 Project Structure
```text
strava-stats/
├── db/
│   └── init.sql              # Database schema and table creation scripts
├── ingestion/
│   ├── Dockerfile            # Container build instructions for the ingestion app
│   ├── requirements.txt      # Python dependencies (requests, psycopg2, dotenv)
│   └── ingest.py             # The core data extraction and loading script
├── dashboard/
│   ├── Dockerfile            # Container build instructions for the Streamlit app
│   ├── requirements.txt      # Python dependencies (streamlit, pandas, psycopg2)
│   └── app.py                # The interactive data dashboard script
├── .gitignore                # Ensures secrets and virtual environments stay local
├── docker-compose.yml        # Orchestrates the local database and app containers
└── README.md
🚀 Local Development Setup
This project is developed using Visual Studio Code on macOS.

Prerequisites

Docker Desktop installed and running

Python 3.9+ installed locally

A Strava Developer Application (for API Credentials)

1. Environment Variables

Create a .env file in the root directory (this file is git-ignored for security):

Code snippet
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_scoped_refresh_token

POSTGRES_USER=strava_user
POSTGRES_PASSWORD=supersecretpassword
POSTGRES_DB=strava_datalake
POSTGRES_HOST=db # Use 'localhost' if running python scripts outside of Docker
Note: Your Strava refresh token must have activity:read_all scope.

2. Run the Full Stack (Database & Dashboard)

You can spin up the PostgreSQL database and the Streamlit dashboard simultaneously using Docker Compose:

Bash
docker-compose up -d --build
Once running, open your web browser and navigate to http://localhost:8501 to view the dashboard.

3. Run the Ingestion Pipeline

To backfill your historical data or run an incremental update locally (fetching new rides from Strava):

Bash
cd ingestion
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure POSTGRES_HOST=localhost in your .env temporarily while running locally
python ingest.py
☁️ Deployment Strategy
Local: Fully supported via docker-compose.yml.

Cloud (Planned): Built to be deployed on the Render.com free tier, utilizing continuous deployment directly from this public GitHub repository.
