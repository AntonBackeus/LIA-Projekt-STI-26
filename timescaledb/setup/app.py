import os
import time
import requests
from requests.auth import HTTPBasicAuth

EMQX_HOST = os.getenv("EMQX_HOST", "emqx")
EMQX_PORT = os.getenv("EMQX_PORT", 18083)
EMQX_USER = os.getenv("EMQX_USER", "admin")
EMQX_PASS = os.getenv("EMQX_PASS", "secret")

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "secret")

BASE_URL = f"http://{EMQX_HOST}:{EMQX_PORT}/api/v5"

def wait_emqx():
    print("Waiting for EMQX to be ready...")
    while True:
        try:
            r = requests.get(f"{BASE_URL}/status", auth=HTTPBasicAuth(EMQX_USER, EMQX_PASS))
            if r.status_code == 200:
                print("EMQX ready!")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)

def create_timescale_connector():
    print("Creating TimescaleDB connector...")
    payload = {
        "connector": "timescaledb",
        "server": f"{DB_HOST}:{DB_PORT}",
        "username": DB_USER,
        "password": DB_PASS,
        "database": DB_NAME,
        "ssl": {"enable": False},
        "name": "timescale"
    }
    r = requests.post(f"{BASE_URL}/bridge/postgresql", json=payload, auth=HTTPBasicAuth(EMQX_USER, EMQX_PASS))
    if r.status_code in (200, 201):
        print("Timescale connector created successfully.")
    else:
        print("Failed to create connector:", r.text)

def create_rule():
    print("Creating rule...")
    payload = {
        "sql": 'SELECT payload.component_id as component_id, payload.temperature as temperature, payload.humidity as humidity, now() as ts FROM "devices/+/events"',
        "actions": [
            {
                "name": "timescale",
                "params": {}
            }
        ],
        "description": "Auto rule to insert MQTT data into TimescaleDB"
    }
    r = requests.post(f"{BASE_URL}/rules", json=payload, auth=HTTPBasicAuth(EMQX_USER, EMQX_PASS))
    if r.status_code in (200, 201):
        print("Rule created successfully.")
    else:
        print("Failed to create rule:", r.text)

if __name__ == "__main__":
    wait_emqx()
    create_timescale_connector()
    create_rule()