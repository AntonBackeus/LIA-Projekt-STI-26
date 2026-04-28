import os                     # För environment variables
import psycopg2               # PostgreSQL-anslutning
import random
import time
import json
from datetime import datetime, timezone


# Connector 
def connector():
    """
    Simulera data från robotarm.
    """
    return {
        "device": 1,
        "timestamp": datetime.now(timezone.utc),
        "temperature": round(random.uniform(18.0, 25.0), 2),
        "humidity": round(random.uniform(30.0, 60.0), 2)
    }

# This function handles the logic for saving data to the database
def process_message(conn, payload):
    # Convert the payload to a format that fits the 'robot_status_events' table.
    # We will store the sensor data as a JSON string in the 'enriched_data' column.
    enriched_data = {
        "Type": "SENSOR_READING",
        "Category": "Environment",
        "Meaning": "Simulated temperature and humidity reading",
        "Temperature": payload["temperature"],
        "Humidity": payload["humidity"]
    }
    enriched_json_string = json.dumps(enriched_data)
    raw_message = f"temp:{payload['temperature']},humid:{payload['humidity']}"
    robot_address = f"SimulatedDevice-{payload['device']}"

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO robot_status_events (ts, robot_address, raw_message, enriched_data)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    payload["timestamp"],
                    robot_address,
                    raw_message,
                    enriched_json_string
                )
            )
            conn.commit()
        print(f"Stored sensor data from {robot_address}")

    except psycopg2.Error as e:
        print(f"Error processing message: {e}")
        conn.rollback()


def main():
    """Main function to connect to DB and process data in a loop."""
    try:
        # Use a 'with' statement for robust connection handling
        with psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=int(os.getenv("DB_PORT", 5432))
        ) as conn:
            print("Successfully connected to the database. Starting data generation loop...")
            while True:
                data = connector()
                print("Från connector:", data)
                process_message(conn, data)
                time.sleep(5)  # Fixed: Sleep for 5 seconds
    except psycopg2.OperationalError as e:
        print(f"CRITICAL: Could not connect to the database: {e}")
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting.")

# Use an execution guard to make the script reusable
if __name__ == "__main__":
    main()