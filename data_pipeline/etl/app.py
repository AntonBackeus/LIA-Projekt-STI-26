import os                                   # Used to import environment variables
import psycopg2                             # Used to connect to PostgreSQL database
import random                               # Can be removed once fake data generation is removed
import time                                 # Can be removed once fake data generation is removed
from datetime import datetime, timezone     # Used to get current timestamp


# PostgreSQL connection setup using environment variables
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", 5432))
)

cursor = conn.cursor()  # Connector variable for executing SQL commands


# Example function to process incoming messages and store them in the database
def process_message(payload):
    try:
        # Insert the data into the database, modify to match the new table structure and column names later
        cursor.execute(
            "INSERT INTO event_data (ts, component_id, temperature, humidity) VALUES (%s, %s, %s, %s)",
            (
                payload["timestamp"],
                payload["device"],
                payload["temperature"],
                payload["humidity"]
            )
        )
        conn.commit() # Saves the changes to the database

        print("Stored message from", payload["device"]) #Keep for logging, can help a future user debug

    except Exception as e:
        print("Error processing message:", e) #Keep for logging, can help a future user debug
        conn.rollback() # Reverts the changes to the database because of the error



def main(): # Data generation test, remove once IOT function is working and sorting algorithm is implemented
            # Sorting algorithm might need to insert a timestamp to the message and format it into a dict if AUT doesnt solve it
    container_id = 1
    while True:
        data = {
            "device": container_id,
            "timestamp": datetime.now(timezone.utc),
            "temperature": round(random.uniform(18.0,25.0),2),
            "humidity": round(random.uniform(30.0,60.0),2)
        }
        process_message(data)
        time.sleep(1)

main()