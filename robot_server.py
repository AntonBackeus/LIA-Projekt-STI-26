import socket
import json
import re

# Konfiguration
HOST = '0.0.0.0' # Lyssnar på alla nätverksgränssnitt
PORT = 5000      # Porten vi lyssnar på

# --- Robot Name Mapping ---
ROBOT_NAMES = {
    "100": "Robot1",
    "101": "Robot2"
}

def get_robot_name(ip_address):
    """Kollar på sista delen av IP-adressen och returnerar ett namn."""
    last_octet = ip_address.split('.')[-1]
    if last_octet in ROBOT_NAMES:
        return f"{ROBOT_NAMES[last_octet]} ({ip_address})"
    return ip_address

# 1. Ladda in JSON-filen i minnet innan servern startar
state_dictionary = {}
try:
    with open('state_values.json', 'r', encoding='utf-8') as file:
        json_data = json.load(file)
        
        for item in json_data:
            # Konvertera siffrorna till textsträngar så de matchar nätverkstrafiken
            key = (str(item['SelectOrCode']).strip(), str(item['Value']).strip())
            state_dictionary[key] = str(item['Meaning']).strip()
            
    print("Laddade in state_values.json framgångsrikt!", flush=True)
except Exception as e:
    print(f"Kunde inte ladda JSON-filen. Kontrollera att den ligger i samma mapp. Fel: {e}", flush=True)


def start_server():
    # Använd socket.socket för att skapa en TCP/IP-socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Tillåt omedelbar omstart av servern på samma port
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        s.bind((HOST, PORT))
        s.listen()
        print(f"Lyssning startad på {HOST}:{PORT}...", flush=True)

        while True:
            # Vänta på anslutning
            conn, addr = s.accept()
            raw_ip = addr[0]
            
            # --- Skapa robotens namn baserat på IP ---
            robot_name = get_robot_name(raw_ip)
            
            with conn:
                print(f"\n--- Ansluten till: {robot_name} ---", flush=True)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print(f"\n--- {robot_name} kopplade från ---", flush=True)
                        break
                    
                    # Avkoda och rensa meddelandet
                    incoming_msg = data.decode('utf-8').strip()
                    
                    if incoming_msg:
                        
                        # ----------------------------------------------------
                        # SCENARIO 1: Roboten skickar en STATUS (STATE)
                        # ----------------------------------------------------
                        if " STATE " in incoming_msg:
                            # Använd regex för att plocka ut siffrorna
                            match = re.search(r'SelectOrCode\s+(\d+).*?Value\s+(\d+)', incoming_msg)
                            
                            if match:
                                select_code = match.group(1) 
                                value = match.group(2)       
                                
                                # Slå upp den översatta texten i JSON-ordboken
                                meaning = state_dictionary.get((select_code, value), "Okänd status")
                                
                                print(f"[{robot_name}] Kod: {select_code} | Värde: {value} --> {meaning}", flush=True)
                            else:
                                print(f"[{robot_name}] [Rådata STATE]: {incoming_msg}", flush=True)

                        # ----------------------------------------------------
                        # SCENARIO 2: Roboten skickar ett FEL (ERROR)
                        # ----------------------------------------------------
                        elif " ERROR " in incoming_msg:
                            print(f"\n*** [{robot_name}] [LARM] {incoming_msg} ***\n", flush=True)
                            
                        # ----------------------------------------------------
                        # SCENARIO 3: Något annat okänt meddelande
                        # ----------------------------------------------------
                        else:
                            print(f"[{robot_name}] [Okänt meddelande]: {incoming_msg}", flush=True)

                    else:
                        print(f"[{robot_name}] Mottog ett tomt meddelande.", flush=True)

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Servern stängdes ner pga fel: {e}", flush=True)