# LIA-Projekt-STI-26

## Data Pipeline

To use the projects data pipeline you need to have docker running and run "docker compose up -d" in the data pipeline folder.

To test the data pipeline in isolation remove the comment on "mqtt-test-publisher" as that will start creating test data for the pipeline.

To view the data you can connect to timescale via for example DBeaver or another plattform capable of viewing postgres.


Grafana DNS + MobileWeb
To make both apps share port 80:

1. sudo apt install nginx
2. Create /etc/nginx/sites-available/omron:
server { listen 80; server_name OmronGrafana.STI; location / { proxy_pass http://127.0.0.1:3000; } }
server { listen 80; server_name STIRobotstatus.STI; location / { proxy_pass http://127.0.0.1:5001; } }


3. Run sudo ln -s /etc/nginx/sites-available/omron /etc/nginx/sites-enabled/ and sudo systemctl restart nginx

