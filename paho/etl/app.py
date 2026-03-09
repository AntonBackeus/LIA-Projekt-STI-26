# Importerar bibliotek för miljövariabler, JSON-hantering, MQTT och PostgreSQL
import os
import json
import paho.mqtt.client as mqtt
import psycopg2
 
 
# Hämtar MQTT-host från environment variabel.
# Om variabeln inte finns används standardvärdet "emqx"
MQTT_HOST = os.getenv("MQTT_HOST", "emqx")
 
# Hämtar MQTT-port från environment variabel.
# Standardporten för MQTT är 1883.
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
 
 
# Skapar en anslutning till TimescaleDB (PostgreSQL)

# Alla värden läses från environment variabler som sätts i docker-compose

conn = psycopg2.connect(

    host=os.getenv("DB_HOST"),        # Databasens host (container-namn i Docker)

    database=os.getenv("DB_NAME"),    # Databasnamn

    user=os.getenv("DB_USER"),        # Databasanvändare

    password=os.getenv("DB_PASS"),     # Databaslösenord

    port=int(os.getenv("DB_PORT", 5432)) # Databasport, standard är 5432

)
 
# Skapar en cursor som används för att köra SQL-kommandon

cursor = conn.cursor()
 
 
# Callback-funktion som körs när klienten ansluter till MQTT-brokern

def on_connect(client, userdata, flags, rc):
 
    # Skriver ut status i loggen

    print("Connected to MQTT")
 
    # Börjar prenumerera på alla topics under "sensors/"

    # '#' betyder wildcard (alla undertopics)

    client.subscribe("sensors/#")
 
 
# Callback-funktion som körs varje gång ett MQTT-meddelande tas emot

def on_message(client, userdata, msg):
 
    # MQTT payload kommer som bytes → dekodas till string → konverteras till JSON

    payload = json.loads(msg.payload.decode())
 
    # Kör en SQL INSERT för att lagra datan i databasen

    cursor.execute(

        "INSERT INTO sensor_data (time, device_id, value) VALUES (NOW(), %s, %s)",
 
        # Hämtar värden från JSON payload

        # %s används för att undvika SQL injection

        (payload["device"], payload["value"])

    )
 
    # Sparar ändringen i databasen

    conn.commit()
 
 
# Skapar en MQTT-klient

client = mqtt.Client()
 
# Kopplar callback-funktionerna till klienten

client.on_connect = on_connect

client.on_message = on_message
 
 
# Ansluter till MQTT-brokern

# 60 = keepalive (sekunder)

client.connect(MQTT_HOST, MQTT_PORT, 60)
 
 
# Startar en loop som håller klienten igång

# Den väntar på nya MQTT-meddelanden kontinuerligt

client.loop_forever()
 