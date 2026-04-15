import socket
import json
import re

# Konfiguration
HOST = '0.0.0.0' # Lyssnar på alla nätverksgränssnitt
PORT = 5000      # Porten vi lyssnar på

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
            with conn:
                print(f"\n--- Ansluten till robot: {addr} ---", flush=True)
                while True:
                    data = conn.recv(1024)
                    if not data:
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
                                
                                print(f"[INFO] Kod: {select_code} | Värde: {value} --> {meaning}", flush=True)
                            else:
                                print(f"[Rådata STATE]: {incoming_msg}", flush=True)

                        # ----------------------------------------------------
                        # SCENARIO 2: Roboten skickar ett FEL (ERROR)
                        # ----------------------------------------------------
                        elif " ERROR " in incoming_msg:
                            print(f"\n*** [LARM] {incoming_msg} ***\n", flush=True)
                            
                        # ----------------------------------------------------
                        # SCENARIO 3: Något annat okänt meddelande
                        # ----------------------------------------------------
                        else:
                            print(f"[Okänt meddelande]: {incoming_msg}", flush=True)

                    else:
                        print("Mottog ett tomt meddelande.", flush=True)

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Servern stängdes ner pga fel: {e}", flush=True)