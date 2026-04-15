import socket

# Konfiguration
HOST = '0.0.0.0' # Lyssnar på alla nätverksgränssnitt
PORT = 5000      # Porten vi lyssnar på

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
                print(f"Ansluten till robot: {addr}", flush=True)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    # Avkoda och rensa meddelandet
                    error_msg = data.decode('utf-8').strip()
                    
                    if error_msg:
                        print(f"Felmeddelande från robot: {error_msg}", flush=True)
                        
                        # Säkerhetskoll så vi inte kraschar på tomma strängar
                        print(f"Sista tecknet: {error_msg[-1]}", flush=True)
                    else:
                        print("Mottog ett tomt meddelande.", flush=True)

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        print(f"Servern stängdes ner pga fel: {e}", flush=True)
