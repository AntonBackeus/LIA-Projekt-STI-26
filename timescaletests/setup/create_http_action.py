import os
import time
import requests
from requests.auth import HTTPBasicAuth

EMQX_HOST = os.getenv("EMQX_HOST", "emqx")
EMQX_PORT = int(os.getenv("EMQX_PORT", 18083))
EMQX_USER = os.getenv("EMQX_USER", "admin")
EMQX_PASS = os.getenv("EMQX_PASS", "strongpassword")
INGESTION_URL = os.getenv("INGESTION_URL", "http://ingestion:8000/events")

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

def create_http_action():
    print("Creating HTTP action...")
    payload = {
        "name": "timescale_webhook",
        "type": "http",
        "params": {
            "url": INGESTION_URL,
            "method": "POST"
        }
    }
    r = requests.post(f"{BASE_URL}/actions", json=payload, auth=HTTPBasicAuth(EMQX_USER, EMQX_PASS))
    if r.status_code in (200, 201):
        print("HTTP action created successfully")
    else:
        print("Failed to create HTTP action:", r.text)

def create_rule():
    print("Creating rule...")
    payload = {
        "sql": 'SELECT payload.component_id as component_id, payload.temperature as temperature, payload.humidity as humidity, now() as ts FROM "devices/+/events"',
        "actions": [
            {
                "name": "timescale_webhook",
                "params": {}
            }
        ],
        "description": "Insert MQTT payloads into TimescaleDB"
    }
    r = requests.post(f"{BASE_URL}/rules", json=payload, auth=HTTPBasicAuth(EMQX_USER, EMQX_PASS))
    if r.status_code in (200, 201):
        print("Rule created successfully")
    else:
        print("Failed to create rule:", r.text)

if __name__ == "__main__":
    wait_emqx()
    create_http_action()
    create_rule()