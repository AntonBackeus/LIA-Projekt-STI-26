# Raspberry Pi Deployment Guide

This guide provides step-by-step instructions to deploy the entire LIA-Projekt-STI-26 stack on a Raspberry Pi running the latest Raspberry Pi OS (64-bit).

This setup will:
- Run the database (TimescaleDB) and Grafana in Docker.
- Run the Python TCP server and Web API server as persistent background services.
- Build and serve the React frontend for production.
- Configure `nginx` as a reverse proxy for custom domains (`Robot.STI` and `Grafana.STI`).

---

### Step 1: Install Prerequisites

First, open a terminal on your Raspberry Pi and run the following commands to install all necessary software.

```bash
# Update your system
sudo apt update && sudo apt upgrade -y

# Install Git, Python, Pip, and Nginx
sudo apt install -y git python3-pip python3-venv nginx curl

# Install Node.js and npm (using NodeSource for a modern version)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs npm

# Install Docker and Docker Compose
curl -sSL https://get.docker.com | sh
sudo usermod -aG docker ${USER}
sudo apt install -y docker-compose-v2
```
**Important:** After installing Docker, you must **log out and log back in** for the group changes to take effect.

---

### Step 2: Get the Project Code

Clone the project repository from your version control system (e.g., GitHub) into your home directory.

```bash
cd ~
git clone <your-repository-url> LIA-Projekt-STI-26
cd LIA-Projekt-STI-26
```

---

### Step 3: Start Backend Infrastructure (Docker)

Navigate to the `data_pipeline` directory and start the TimescaleDB and Grafana containers.

```bash
cd data_pipeline
docker compose up -d
```

---

### Step 4: Build the Frontend for Production

The mobile web app needs to be compiled into static files that our Flask server can serve.

```bash
# Navigate to the MobileWeb directory
cd ~/LIA-Projekt-STI-26/MobileWeb

# Install Node.js dependencies
npm install

# Build the production-ready static files (this creates a 'dist' folder)
npm run build
```

---

### Step 5: Configure Nginx Reverse Proxy

Create an `nginx` configuration file to route your custom domains.

```bash
# Create and open the config file with nano editor
sudo nano /etc/nginx/sites-available/omron-proxy
```

Paste the following content into the file, then press `Ctrl+X`, `Y`, and `Enter` to save and exit.

```nginx
server {
    listen 80;
    server_name Robot.STI;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

server {
    listen 80;
    server_name Grafana.STI;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Now, enable the site and restart `nginx`:

```bash
# Enable the new site configuration
sudo ln -s /etc/nginx/sites-available/omron-proxy /etc/nginx/sites-enabled/

# Test the configuration for errors
sudo nginx -t

# If the test is successful, restart nginx
sudo systemctl restart nginx
```

---

### Step 6: Install Python Dependencies

Install the required Python packages globally.

```bash
# Navigate to the project root directory
cd ~/LIA-Projekt-STI-26

# Install the Python packages globally using sudo
# The --break-system-packages flag is required on recent Raspberry Pi OS versions
sudo pip3 install -r requirements.txt --break-system-packages
```

---

### Step 7: Run Python Servers as `systemd` Services

To ensure the Python servers run reliably in the background and restart automatically, we will set them up as `systemd` services.

**A. Create the TCP Server Service:**

```bash
# Create and open the service file
sudo nano /etc/systemd/system/robot-tcp-server.service
```
Paste this content. Change `User` and `Group` if your username is not `pi`.
```ini
[Unit]
Description=Omron Robot TCP Data Server
After=network.target

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/LIA-Projekt-STI-26
ExecStart=/usr/bin/python3 /home/pi/LIA-Projekt-STI-26/robot_server_send_to_timescaleDB.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**B. Create the Web Server Service:**

```bash
sudo nano /etc/systemd/system/robot-web-server.service
```
Paste this content. This service will wait for Docker to be ready.
```ini
[Unit]
Description=Omron Robot Mobile Web API Server
After=docker.service
Requires=docker.service

[Service]
User=pi
Group=pi
WorkingDirectory=/home/pi/LIA-Projekt-STI-26
ExecStart=/usr/bin/python3 /home/pi/LIA-Projekt-STI-26/MobileWeb/mobile_web_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**C. Enable and Start the Services:**

```bash
# Reload systemd to recognize the new files
sudo systemctl daemon-reload

# Enable the services to start on boot
sudo systemctl enable robot-tcp-server.service robot-web-server.service

# Start the services now
sudo systemctl start robot-tcp-server.service robot-web-server.service

# Check their status (optional)
sudo systemctl status robot-tcp-server.service robot-web-server.service
```

---

### Step 7: Final Client-Side Configuration

1.  Find your Raspberry Pi's IP address by running `ip a` in the terminal.
2.  On your **personal computer** (not the Pi), edit your `hosts` file to map the domains to the Pi's IP.
    -   **Windows:** `C:\Windows\System32\drivers\etc\hosts`
    -   **macOS/Linux:** `/etc/hosts`
3.  Add these lines, replacing `192.168.1.123` with your Pi's actual IP:
    ```
    192.168.1.123   Robot.STI
    192.168.1.123   Grafana.STI
    ```

Your deployment is now complete! You can access the mobile app at `http://Robot.STI` and Grafana at `http://Grafana.STI` from your computer.