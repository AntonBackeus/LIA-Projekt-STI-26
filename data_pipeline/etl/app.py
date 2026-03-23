import os                     # För environment variables
import psycopg2               # PostgreSQL-anslutning
import random
import time
from datetime import datetime, timezone


# Databasanslutning
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", 5432))
)

cursor = conn.cursor()  # Cursor för SQL


# Denna funktion innehåller all logik för att spara data i databasen
# Kan anropas direkt utan MQTT
def process_message(payload):
    try:
        cursor.execute(
            "INSERT INTO event_data (ts, component_id, temperature, humidity) VALUES (%s, %s, %s, %s)",
            (
                payload["timestamp"],
                payload["device"],
                payload["temperature"],
                payload["humidity"]
            )
        )
        conn.commit()

        print("Stored message from", payload["device"])

    except Exception as e:
        print("Error processing message:", e)
        conn.rollback()



def main():
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