import os
import psycopg2
import random
import time
from datetime import datetime, timezone


# ----------------------------
# Database connection
# ----------------------------
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", 5432))
)

cursor = conn.cursor()


# ----------------------------
# CONNECTOR
# ----------------------------
def connector():
    """
    Simulerar IoT-data i dictionary-format
    """
    return {
        "type": random.choice(["TEMP", "HUM"]),
        "value": round(random.uniform(20, 30), 2),
        "timestamp": datetime.now(timezone.utc),
        "device": 1
    }


# ----------------------------
# HANDLE MESSAGE (NY)
# ----------------------------
def handle_message(message):

    if message["type"] == "TEMP":
        print("Temperature:", message["value"])

    elif message["type"] == "HUM":
        print("Humidity:", message["value"])

    else:
        print("Unknown message:", message)


# ----------------------------
# PROCESS MESSAGE (samma som innan)
# ----------------------------
def process_message(payload):
    try:
        cursor.execute(
            "INSERT INTO event_data (ts, component_id, temperature, humidity) VALUES (%s, %s, %s, %s)",
            (
                payload["timestamp"],
                payload["device"],
                payload.get("value") if payload["type"] == "TEMP" else None,
                payload.get("value") if payload["type"] == "HUM" else None
            )
        )
        conn.commit()

        print("Stored message")

    except Exception as e:
        print("Error:", e)
        conn.rollback()


# ----------------------------
# MAIN
# ----------------------------
def main():
    while True:
        message = connector()

        print("Från connector:", message)

        handle_message(message)

        process_message(message)

        time.sleep(1)


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    main()