import os
import psycopg2
import random
import time
import uuid
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
# CONNECTOR (simulering)
# ----------------------------
def connector():
    return {
        "type": "STATE",
        "select": random.randint(1, 3),
        "value": random.randint(0, 10),
        "timestamp": datetime.now(timezone.utc),
        "device": 1
    }


# ----------------------------
# INSERT FUNCTIONS (en per attribut)
# ----------------------------
def insert_timestamp(event_id, timestamp):
    cursor.execute(
        "INSERT INTO timestamp_table (event_id, ts) VALUES (%s, %s)",
        (event_id, timestamp)
    )


def insert_device(event_id, device):
    cursor.execute(
        "INSERT INTO device_table (event_id, device_id) VALUES (%s, %s)",
        (event_id, device)
    )


def insert_state_select(event_id, select):
    cursor.execute(
        "INSERT INTO state_select_table (event_id, state_type) VALUES (%s, %s)",
        (event_id, select)
    )


def insert_state_value(event_id, value):
    cursor.execute(
        "INSERT INTO state_value_table (event_id, state_value) VALUES (%s, %s)",
        (event_id, value)
    )


# ----------------------------
# HANDLE MESSAGE (parsing)
# ----------------------------
def handle_message(message):
    if message["type"] == "STATE":
        return {
            "timestamp": message["timestamp"],
            "device": message["device"],
            "select": message["select"],
            "value": message["value"]
        }
    return None


# ----------------------------
# PROCESS MESSAGE (orchestrator)
# ----------------------------
def process_message(payload):
    if payload is None:
        return

    event_id = str(uuid.uuid4())

    try:
        insert_timestamp(event_id, payload["timestamp"])
        insert_device(event_id, payload["device"])
        insert_state_select(event_id, payload["select"])
        insert_state_value(event_id, payload["value"])

        conn.commit()
        print("Stored event:", event_id)

    except Exception as e:
        print("Error:", e)
        conn.rollback()


# ----------------------------
# MAIN
# ----------------------------
def main():
    while True:
        raw_message = connector()

        print("Kommande meddelande:", raw_message)

        parsed = handle_message(raw_message)

        process_message(parsed)

        time.sleep(1)


# ----------------------------
# START
# ----------------------------
if __name__ == "__main__":
    main()


# Se till att få in riktigt data. Det kan du göa genom no-sql