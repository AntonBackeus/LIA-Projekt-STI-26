import os
import json
import paho.mqtt.client as mqtt
import psycopg2


# MQTT konfiguration från environment variables
MQTT_HOST = os.getenv("MQTT_HOST", "emqx")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
DATA_TOPIC = os.getenv("DATA_TOPIC")
CLIENT_ID = os.getenv("CLIENT_ID")


# Databasanslutning
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    port=int(os.getenv("DB_PORT", 5432))
)

cursor = conn.cursor()


# Körs när MQTT-klienten ansluter till brokern
def on_connect(client, userdata, flags, rc):

    if rc == 0:
        print("Connected to MQTT")

        # Prenumererar på topics med QoS 2
        client.subscribe(DATA_TOPIC, qos=2)

    else:
        print("Connection failed:", rc)


# Körs varje gång ett MQTT-meddelande tas emot
def on_message(client, userdata, msg):

    try:
        payload = json.loads(msg.payload.decode())

        cursor.execute(
            "INSERT INTO event_data (ts, component_id, temperature, humidity) VALUES (%s, %s, %s, %s)",
            (payload["timestamp"], payload["device"], payload["temperature"], payload["humidity"])
        )

        conn.commit()

        print("Stored message from", payload["device"])

    except Exception as e:
        print("Error processing message:", e)
        conn.rollback()


# Skapar MQTT-klient med persistent session
client = mqtt.Client(
    client_id=CLIENT_ID,   # måste vara konstant
    clean_session=False    # gör att broker sparar QoS-meddelanden
)


# Automatisk reconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)


# Koppla callbacks
client.on_connect = on_connect
client.on_message = on_message


# Anslut till broker
client.connect(MQTT_HOST, MQTT_PORT, 60)


# Starta klientens loop
client.loop_forever()