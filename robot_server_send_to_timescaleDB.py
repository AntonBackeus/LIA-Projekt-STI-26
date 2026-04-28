import socket
import json
import os
import psycopg2
from psycopg2 import pool
from datetime import datetime, timezone
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), 'data_pipeline', '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 5000

# Database connection parameters from .env
DB_NAME = os.getenv("DB_NAME", "mqtt_data")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

db_pool = None

# --- Robot Name Mapping ---
ROBOT_NAMES = {
    "100": "Robot1",
    "101": "Robot2"
}

def get_robot_name(ip_address):
    """Looks at the last part of the IP and returns a friendly name."""
    last_octet = ip_address.split('.')[-1]
    if last_octet in ROBOT_NAMES:
        return f"{ROBOT_NAMES[last_octet]} ({ip_address})"
    return ip_address

# --- Global Lookups ---
ERROR_CODES_LOOKUP = {}
STATE_VALUES_BY_SELECT_CODE = {}

def init_db_pool():
    """Initializes the database connection pool on startup."""
    global db_pool
    try:
        db_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20, # Min 1, Max 20 connections
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Database connection pool initialized successfully.", flush=True)
    except psycopg2.Error as e:
        print(f"CRITICAL: Failed to initialize database pool: {e}", flush=True)
        exit(1)

def load_json_lookups():
    """Loads JSON dictionaries into memory."""
    global ERROR_CODES_LOOKUP, STATE_VALUES_BY_SELECT_CODE
    try:
        with open(os.path.join(os.path.dirname(__file__), 'error_code.json'), 'r', encoding='utf-8') as f:
            error_codes_data = json.load(f)
            ERROR_CODES_LOOKUP = {item['Code']: item for item in error_codes_data}
        print("Loaded error_code.json successfully.", flush=True)
    except Exception as e:
        print(f"Error loading error_code.json: {e}", flush=True)

    try:
        with open(os.path.join(os.path.dirname(__file__), 'state_values.json'), 'r', encoding='utf-8') as f:
            state_values_data_list = json.load(f)
            for item in state_values_data_list:
                select_code = item['SelectOrCode']
                if select_code not in STATE_VALUES_BY_SELECT_CODE:
                    STATE_VALUES_BY_SELECT_CODE[select_code] = []
                STATE_VALUES_BY_SELECT_CODE[select_code].append(item)
        print("Loaded state_values.json successfully.", flush=True)
    except Exception as e:
        print(f"Error loading state_values.json: {e}", flush=True)

def get_db_connection_from_pool():
    """Retrieves a connection from the global database pool."""
    global db_pool
    if db_pool is None:
        print("Database pool not initialized.", flush=True)
        return None
    try:
        return db_pool.getconn()
    except psycopg2.Error as e:
        print(f"Error getting connection from pool: {e}", flush=True)
        return None

def insert_robot_status(robot_address, raw_message, enriched_json_data):
    """Inserts the translated event into TimescaleDB."""
    conn = None
    try:
        conn = get_db_connection_from_pool()
        if conn is None: return
        
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO robot_status_events (ts, robot_address, raw_message, enriched_data)
                VALUES (%s, %s, %s, %s);
                """,
                (datetime.now(timezone.utc), robot_address, raw_message, enriched_json_data)
            )
            conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting into TimescaleDB: {e}", flush=True)
        if conn: conn.rollback()
    finally:
        if conn: db_pool.putconn(conn) # Return connection to pool

def parse_hex_value(hex_str):
    if hex_str.upper().startswith('^H'):
        return int(hex_str[2:], 16)
    elif hex_str.lower().startswith('0x'):
        return int(hex_str[2:], 16)
    return None

def lookup_message(message):
    """Translates the raw message using the JSON data."""
    try:
        code_int = int(message)
        if code_int in ERROR_CODES_LOOKUP:
            item = ERROR_CODES_LOOKUP[code_int]
            return {"Type": "ERROR", "Code": code_int, "Category": item['Category'], "Meaning": item['Message']}
    except ValueError:
        pass

    if message.upper().startswith("STATE:"):
        parts = message.split(':', 2)
        if len(parts) == 3:
            try:
                select_or_code_str = parts[1]
                value_str = parts[2]
                select_or_code = int(select_or_code_str)

                if select_or_code in STATE_VALUES_BY_SELECT_CODE:
                    for item in STATE_VALUES_BY_SELECT_CODE[select_or_code]:
                        expected_value = item['Value']

                        if isinstance(expected_value, int):
                            try:
                                if int(value_str) == expected_value:
                                    return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": int(value_str), "Category": item['Category'], "Meaning": item['Meaning']}
                            except ValueError:
                                pass
                        elif isinstance(expected_value, str):
                            if expected_value.lower() == "nonzero":
                                try:
                                    if int(value_str) != 0:
                                        return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": int(value_str), "Category": item['Category'], "Meaning": item['Meaning']}
                                except ValueError:
                                    pass
                            elif expected_value.lower() == "value":
                                return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": value_str, "Category": item['Category'], "Meaning": item['Meaning']}
                            elif expected_value.startswith(('^H', '0x')):
                                parsed_expected_hex = parse_hex_value(expected_value)
                                parsed_actual_hex = parse_hex_value(value_str)
                                if parsed_expected_hex is not None and parsed_actual_hex is not None and parsed_actual_hex == parsed_expected_hex:
                                    return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": value_str, "Category": item['Category'], "Meaning": item['Meaning']}
                            elif value_str.lower() == expected_value.lower():
                                return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": value_str, "Category": item['Category'], "Meaning": item['Meaning']}

                    if STATE_VALUES_BY_SELECT_CODE[select_or_code]:
                        first_item = STATE_VALUES_BY_SELECT_CODE[select_or_code][0]
                        return {"Type": "STATE", "SelectOrCode": select_or_code, "Value": value_str, "Category": first_item['Category'], "Meaning": f"Unknown specific value '{value_str}' for {first_item['Category']} (SelectOrCode: {select_or_code})"}
            except ValueError:
                pass

    return {"Type": "RAW", "Meaning": message, "Category": "Uncategorized"}

def handle_client(client_socket, raw_ip):
    """Handles communication with a single connected robot."""
    robot_name = get_robot_name(raw_ip)
    
    with client_socket:
        print(f"Connected to: {robot_name}", flush=True)
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break # Client disconnected
                
                error_msg = data.decode('utf-8').strip()
                
                if error_msg:
                    enriched_data_dict = lookup_message(error_msg)
                    enriched_json_string = json.dumps(enriched_data_dict)
                    
                    print(f"Received from {robot_name}: '{error_msg}'", flush=True)
                    print(f"Interpreted JSON: {enriched_json_string}", flush=True)
                    
                    insert_robot_status(robot_name, error_msg, enriched_json_string)
                else:
                    print(f"Received an empty message from {robot_name}.", flush=True)
                    
            except ConnectionResetError:
                print(f"Connection reset by {robot_name}.", flush=True)
                break
            except Exception as e:
                print(f"Error handling data from {robot_name}: {e}", flush=True)
                break
                
        print(f"{robot_name} disconnected.", flush=True)

def start_server():
    load_json_lookups()
    init_db_pool() # Initialize the DB connections BEFORE accepting clients

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening started on {HOST}:{PORT}...", flush=True)

        while True:
            client_socket, addr = s.accept()
            raw_ip = addr[0]
            
            # Spin up a new background thread for every robot that connects
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, raw_ip), 
                daemon=True 
            )
            client_thread.start()

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Server shut down due to an error: {e}", flush=True)