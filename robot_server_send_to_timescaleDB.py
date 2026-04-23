import socket
import json
import psycopg2
from datetime import datetime
import re 

# --- Configuration ---
HOST = '0.0.0.0' 
PORT = 5000      

DB_NAME = "mqtt_data"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_HOST = "localhost" 
DB_PORT = "5432"

# --- Global Lookups ---
ERROR_CODES_LOOKUP = {}
STATE_VALUES_DATA = [] 

def load_json_lookups():
    global ERROR_CODES_LOOKUP, STATE_VALUES_DATA
    try:
        with open('error_code.json', 'r', encoding='utf-8') as f:
            error_codes_data = json.load(f)
            ERROR_CODES_LOOKUP = {item['Code']: item for item in error_codes_data}
        print("Loaded error_code.json successfully.", flush=True)
    except FileNotFoundError:
        print("Error: error_code.json not found.", flush=True)
    except json.JSONDecodeError as e:
        print(f"Error decoding error_code.json: {e}", flush=True)

    try:
        with open('state_values.json', 'r', encoding='utf-8') as f:
            STATE_VALUES_DATA = json.load(f)
        print("Loaded state_values.json successfully.", flush=True)
    except FileNotFoundError:
        print("Error: state_values.json not found.", flush=True)
    except json.JSONDecodeError as e:
        print(f"Error decoding state_values.json: {e}", flush=True)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected to TimescaleDB successfully.", flush=True)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to TimescaleDB: {e}", flush=True)
        return None

def insert_robot_status(conn, robot_address, raw_message, message_type, code, category, meaning):
    # AUTO-RECONNECT LOGIC: Check if connection is dead
    if conn is None or conn.closed != 0:
        print("Database connection lost. Attempting to reconnect...", flush=True)
        conn = get_db_connection()
        if not conn:
            print("Reconnect failed. Skipping insertion.", flush=True)
            return conn # Return the failed connection state

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO robot_status_events (ts, robot_address, raw_message, message_type, code, category, meaning)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (datetime.now(), robot_address, raw_message, message_type, str(code) if code is not None else None, category, meaning)
            )
            conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting into TimescaleDB: {e}", flush=True)
        if conn and conn.closed == 0:
            conn.rollback() 
            
    return conn # Return the connection so the main loop can keep tracking it

def parse_hex_value(hex_str):
    if hex_str.upper().startswith('^H'):
        return int(hex_str[2:], 16)
    elif hex_str.lower().startswith('0x'):
        return int(hex_str[2:], 16)
    return None

def lookup_message(message):
    try:
        code_int = int(message)
        if code_int in ERROR_CODES_LOOKUP:
            item = ERROR_CODES_LOOKUP[code_int]
            return 'ERROR', code_int, item['Category'], item['Message']
    except ValueError:
        pass 

    if message.upper().startswith("STATE:"):
        parts = message.split(':', 2) 
        if len(parts) == 3:
            try:
                select_or_code_str = parts[1]
                value_str = parts[2]
                select_or_code = int(select_or_code_str)

                for item in STATE_VALUES_DATA:
                    if item['SelectOrCode'] == select_or_code:
                        expected_value = item['Value']

                        if isinstance(expected_value, int):
                            try:
                                if int(value_str) == expected_value:
                                    return 'STATE', int(value_str), item['Category'], item['Meaning']
                            except ValueError:
                                pass 
                        elif isinstance(expected_value, str):
                            if expected_value.lower() == "nonzero":
                                try:
                                    if int(value_str) != 0:
                                        return 'STATE', int(value_str), item['Category'], item['Meaning']
                                except ValueError:
                                    pass
                            elif expected_value.lower() == "value": 
                                return 'STATE', value_str, item['Category'], item['Meaning']
                            elif expected_value.startswith(('^H', '0x')): 
                                parsed_expected_hex = parse_hex_value(expected_value)
                                parsed_actual_hex = parse_hex_value(value_str)
                                if parsed_expected_hex is not None and parsed_actual_hex is not None and parsed_actual_hex == parsed_expected_hex:
                                    return 'STATE', value_str, item['Category'], item['Meaning']
                            elif value_str.lower() == expected_value.lower(): 
                                return 'STATE', value_str, item['Category'], item['Meaning']

                for item in STATE_VALUES_DATA:
                    if item['SelectOrCode'] == select_or_code:
                        return 'STATE', value_str, item['Category'], f"Unknown specific value '{value_str}' for {item['Category']} (SelectOrCode: {select_or_code})"

            except ValueError:
                pass 

    return 'RAW', None, 'Uncategorized', message

def start_server():
    load_json_lookups() 
    db_conn = get_db_connection() 

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"Listening started på {HOST}:{PORT}...", flush=True)

            while True:
                conn, addr = s.accept()
                robot_address = addr[0] 
                with conn: 
                    print(f"Connected to robot: {robot_address}", flush=True)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        
                        error_msg = data.decode('utf-8').strip()
                        
                        if error_msg:
                            message_type, code, category, meaning = lookup_message(error_msg)
                            
                            print(f"Received from {robot_address}: '{error_msg}'", flush=True)
                            print(f"Interpreted: Type={message_type}, Code={code}, Category='{category}', Meaning='{meaning}'", flush=True)
                            
                            # Capture the potentially reconnected db_conn
                            db_conn = insert_robot_status(db_conn, robot_address, error_msg, message_type, code, category, meaning)
                        else:
                            print(f"Received an empty message from {robot_address}.", flush=True)
                    print(f"Robot {robot_address} disconnected.", flush=True)
    finally:
        # Moved inside start_server so db_conn is accessible
        if db_conn and db_conn.closed == 0:
            db_conn.close()
            print("Database connection closed.", flush=True)

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Server shut down due to an error: {e}", flush=True)