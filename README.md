# LIA-Projekt-STI-26: Övervakning av Omron-robotar

Detta projekt är ett system för att samla in och övervaka data från Omron-robotar. Det hämtar status och felmeddelanden i realtid via en Python TCP-server, sparar datan i en TimescaleDB-databas och visar upp den i en mobilanpassad webbapplikation (React) samt i Grafana.

**GitHub Repository:** [LIA-Projekt-STI-26](https://github.com/AntonBackeus/LIA-Projekt-STI-26)  
**Aktuell Branch:** [RaspberryPi's-VS](https://github.com/AntonBackeus/LIA-Projekt-STI-26/tree/RaspberryPi's-VS)

---

## Inloggningsuppgifter

**RaspberryPI-1**
usr: raspberrypi-1
pass: rasberrypi-1

**Gmail:**
raspberrysti1@gmail.com

**RemoteControl**
link: https://connect.raspberrypi.com/devices
Email: raspberrysti1@gmail.com
Password: STIraspberrystu1

---
### Länkar
Så länge din dator är ansluten till STI wifi då kan du nå systemet via dessa länkar i din webbläsare:
* **Mobil Webbapp:** http://robotserver.local
* **Grafana:** http://robotserver.local:3000 (Standardinloggning: admin / grafana)





## Lathund för att hantera systemet

Allt på Raspberry Pi är inställt på att starta automatiskt när strömmen slås på. Om du behöver felsöka eller starta om något manuellt kan du använda kommandona nedan.

### 1. Python-servrarna (TCP & Webb-API)

Dessa körs i bakgrunden på din Raspberry Pi som inbyggda tjänster (systemd).
Själva inställningsfilerna för dessa hittar du i mappen: `/etc/systemd/system/`
 
 ## tcp_server.service 
 -- Lyssnar på Omron-robotarna och sparar data i databasen.
 ## mobileweb-server.service
 -- Skickar informationen från databasen till webbappen.

**Hur du läser loggarna i realtid:**
```bash
# Se loggar för TCP-servern (Tryck CTRL+C för att avsluta)
sudo journalctl -u tcp_server.service -f

# Se loggar för Webb-API-servern (Tryck CTRL+C för att avsluta)
sudo journalctl -u mobileweb-server.service -f
```

**Hur du startar om servrarna:**
```bash
sudo systemctl restart tcp_server.service
sudo systemctl restart mobileweb-server.service
```

### 2. Databasen och Grafana (Docker)

TimescaleDB (databasen) och Grafana (graferna) körs inuti Docker.

**Hur du läser Docker-loggarna:**
```bash
# Gå först till rätt mapp!
cd ~/LIA-Projekt-STI-26/data_pipeline

# Se loggar för Grafana (Tryck CTRL+C för att avsluta)
docker compose logs -f grafana

# Se loggar för databasen (Tryck CTRL+C för att avsluta)
docker compose logs -f timescaledb
```

**Hur du startar om Docker:**
```bash
# Gå först till rätt mapp!
cd ~/LIA-Projekt-STI-26/data_pipeline

# Snabb omstart av alla Docker-tjänster
docker compose restart

# ELLER, för att stänga av helt och starta från noll:
docker compose down
docker compose up -d
```

### 3. Nginx (Domäner och omdirigering)

Nginx hanterar omdirigeringen av nätverkstrafiken för dina anpassade domäner.
Inställningsfilen för domänerna hittar du på följande sökväg:
`/etc/nginx/sites-available/robot`

**Hur du ändrar i domänfilen:**
För att öppna och redigera inställningsfilen använder du textredigeraren nano:
```bash
sudo nano /etc/nginx/sites-available/robot
```
*(När du är klar: Tryck CTRL+X, sedan Y, och tryck Enter för att spara).*

**Hur du startar om Nginx:**
Om du gör ändringar i domäninställningarna måste Nginx startas om för att de ska börja gälla.
```bash
sudo systemctl restart nginx
```

