import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# --- Configuration ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from the .env file in the data_pipeline directory
# The path is adjusted to go up one level ('..') from the 'MobileWeb' directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'data_pipeline', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Flask App Initialization ---
app = Flask(__name__, static_folder='dist', static_url_path='/')
# This enables Cross-Origin Resource Sharing, allowing your React app to talk to this server
CORS(app) 

# --- Database Configuration & Pool ---
DB_NAME = os.getenv("DB_NAME", "mqtt_data")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost") # Should be localhost when running outside Docker
DB_PORT = os.getenv("DB_PORT", "5432")

db_pool = None

def init_db_pool():
    """Initializes the database connection pool."""
    global db_pool
    try:
        logging.info(f"Connecting to database at {DB_HOST}:{DB_PORT}...")
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 5, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        logging.info("Database connection pool initialized successfully.")
    except psycopg2.OperationalError as e:
        logging.critical(f"CRITICAL: Failed to initialize database pool: {e}")
        exit(1)

@app.route('/')
def serve_react_app():
    """Serves the compiled React frontend."""
    return app.send_static_file('index.html')

@app.route('/api/status')
def get_robot_status():
    """API endpoint to get the latest 'Robot State' for each robot."""
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT ON (robot_address) robot_address, enriched_data, ts
                FROM robot_status_events
                WHERE enriched_data->>'Category' = 'Robot State'
                ORDER BY robot_address, ts DESC;
            """)
            statuses = [dict(row) for row in cursor.fetchall()]
        return jsonify(statuses)
    except Exception as e:
        logging.error(f"Error fetching robot status: {e}")
        return jsonify({"error": "Failed to retrieve data from database"}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

@app.route('/api/errors')
def get_robot_errors():
    """API endpoint to get the latest error for each robot."""
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT ON (robot_address) robot_address, enriched_data, ts
                FROM robot_status_events
                WHERE enriched_data->>'Type' = 'ERROR'
                ORDER BY robot_address, ts DESC;
            """)
            errors = [dict(row) for row in cursor.fetchall()]
        return jsonify(errors)
    except Exception as e:
        logging.error(f"Error fetching robot errors: {e}")
        return jsonify({"error": "Failed to retrieve errors"}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    init_db_pool()
    # Host 0.0.0.0 makes it accessible on your local network
    app.run(host='0.0.0.0', port=80)