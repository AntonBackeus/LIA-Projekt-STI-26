import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'data_pipeline', '.env')
load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__, static_folder='dist', static_url_path='/')
CORS(app) 

DB_NAME = os.getenv("DB_NAME", "mqtt_data")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

db_pool = None

def init_db_pool():
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
    return app.send_static_file('index.html')

@app.route('/api/Status_and_errors')
def get_robot_status_and_errors():
    conn = None
    try:
        conn = db_pool.getconn()
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                WITH latest_statuses AS (
                    SELECT DISTINCT ON (robot_address)
                        robot_address,
                        enriched_data AS status_data,
                        ts AS status_ts
                    FROM robot_status_events
                    WHERE enriched_data->>'Category' = 'Robot State'
                    ORDER BY robot_address, ts DESC
                ),
                latest_errors AS (
                    SELECT DISTINCT ON (robot_address)
                        robot_address,
                        enriched_data AS error_data,
                        ts AS error_ts
                    FROM robot_status_events
                    WHERE enriched_data->>'Type' = 'ERROR'
                    ORDER BY robot_address, ts DESC
                )
                SELECT
                    COALESCE(s.robot_address, e.robot_address) AS robot_address,
                    s.status_data,
                    s.status_ts,
                    e.error_data,
                    e.error_ts
                FROM latest_statuses s
                FULL OUTER JOIN latest_errors e ON s.robot_address = e.robot_address;
            """)
            results = [dict(row) for row in cursor.fetchall()]
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error fetching robot status: {e}")
        return jsonify({"error": "Failed to retrieve data from database"}), 500
    finally:
        if conn:
            db_pool.putconn(conn)

if __name__ == '__main__':
    init_db_pool()
    app.run(host='0.0.0.0', port=5001)