import json
import psycopg2
import os
from datetime import datetime

# =========================
# LOAD LOOKUP
# =========================
def load_lookup():
    try:
        with open("lookup.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error_codes": {}, "states": {}}

LOOKUP = load_lookup()

# =========================
# DB CONNECTION (Uppdaterad för Docker)
# =========================
def connect():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "timescaledb"),
        database=os.getenv("DB_NAME", "your_db"),
        user=os.getenv("DB_USER", "your_user"),
        password=os.getenv("DB_PASS", "your_password"),
        port=os.getenv("DB_PORT", 5432)
    )

# =========================
# ENRICHMENT & INSERT (Oförändrade men använder korrekta fält)
# =========================
def enrich_message(message):
    # Matchar tabellens kolumnnamn i init.sql
    error_msg = LOOKUP["error_codes"].get(str(message.get("error_code")), "Unknown Error")
    state_msg = LOOKUP["states"].get(str(message.get("state")), "Unknown State")

    return {
        "ts": message.get("timestamp", datetime.utcnow()),
        "device_id": message.get("device_id", 1),
        "state": message.get("state"),
        "value": message.get("value"),
        "error_code": message.get("error_code"),
        "error_message": error_msg,
        "state_message": state_msg
    }

def insert_data(conn, data):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO robot_data (
                ts, device_id, event_state, event_value, 
                error_code, error_message, state_message
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data["ts"], data["device_id"], data["state"], data["value"],
            data["error_code"], data["error_message"], data["state_message"]
        ))
    conn.commit()

def process_message(raw_message, conn):
    enriched = enrich_message(raw_message)
    insert_data(conn, enriched)

if __name__ == "__main__":
    conn = connect()
    fake_message = {
        "timestamp": datetime.utcnow(),
        "device_id": 1,
        "state": 5,
        "value": 2.3,
        "error_code": 34
    }
    process_message(fake_message, conn)
    conn.close()