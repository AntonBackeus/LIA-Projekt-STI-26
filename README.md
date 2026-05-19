# LIA-Projekt-STI-26

This project is an IoT data pipeline and monitoring system for Omron robots. It collects data via a TCP server, stores it in TimescaleDB, and visualizes it through a mobile-friendly web app and Grafana dashboards.

---

## Local Development Setup

Follow these steps to get the entire project running on your local development machine (e.g., Windows/macOS).

### 1. Prerequisites

Make sure you have the following software installed:
-   **Docker** and **Docker Compose**: To run the database and Grafana.
-   **Python 3.8+**: To run the backend servers.
-   **Node.js 20+** and **npm**: To run the frontend development server.

### 2. Backend and Database Setup

**A. Start the Database and Grafana:**

Navigate to the `data_pipeline` directory and start the services using Docker Compose.

```bash
cd data_pipeline
docker compose up -d
```

**B. Install Python Dependencies:**

It's highly recommended to use a Python virtual environment for local development.

```bash
# From the project root, create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install required packages
pip install -r requirements.txt
```

**C. Run the Backend Servers:**

Open two separate terminals for this.

-   **Terminal 1: TCP Data Server** (Listens for robot data)
    ```bash
    python robot_server_send_to_timescaleDB.py
    ```
-   **Terminal 2: Mobile Web API Server** (Serves the API for the frontend)
    ```bash
    python MobileWeb/mobile_web_server.py
    ```

### 3. Frontend Setup (Development)

**A. Navigate to the `MobileWeb` directory and install dependencies:**
```bash
cd MobileWeb
npm install
```

**B. Start the development server:**
```bash
npm run dev
```
This will start the frontend on `http://localhost:5173`. The Vite proxy will handle API requests.

---

## Raspberry Pi Production Deployment

This guide provides step-by-step instructions to deploy the entire stack on a Raspberry Pi running the latest Raspberry Pi OS (64-bit).

### Step 1: Install Prerequisites

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
**Important:** After installing Docker, you must **log out and log back in**.

### Step 2: Get Project Code

```bash
cd ~
git clone <your-repository-url> LIA-Projekt-STI-26
cd LIA-Projekt-STI-26
```

### Step 3: Start Docker Services

```bash
cd data_pipeline
docker compose up -d
```

### Step 4: Build Frontend

```bash
cd ~/LIA-Projekt-STI-26/MobileWeb
npm install
npm run build
```

### Step 5: Configure Nginx

Create `/etc/nginx/sites-available/omron-proxy` with the content from the `Deployment.md` guide, then run:

```bash
sudo ln -s /etc/nginx/sites-available/omron-proxy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Install Python Dependencies

```bash
cd ~/LIA-Projekt-STI-26
sudo pip3 install -r requirements.txt --break-system-packages
```

### Step 7: Run Python Servers as Services

Create the `robot-tcp-server.service` and `robot-web-server.service` files in `/etc/systemd/system/` using the templates in `Deployment.md`. **Remember to replace `<your_username>` with your actual username.**

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now robot-tcp-server.service robot-web-server.service
```

### Step 8: Final Client-Side Configuration

On your **personal computer**, edit your `hosts` file to map your Pi's IP address to the custom domains.

```
<your_pi_ip_address>   Robot.STI
<your_pi_ip_address>   Grafana.STI
```

Your deployment is now complete. Access the mobile app at `http://Robot.STI` and Grafana at `http://Grafana.STI`.

This section explains how to use `nginx` on the Raspberry Pi as a reverse proxy. This lets you access web apps with custom domains (`Robot.STI`, `Grafana.STI`) instead of IP addresses and ports.

`nginx` will be configured to:
1.  Listen for all web traffic on port 80.
2.  Route `http://Robot.STI` requests to the Flask mobile web server (running on port 5001).
3.  Route `http://Grafana.STI` requests to the Grafana instance (running on port 3000).

This simplifies access for a more professional setup. To make this work, you must also edit the `hosts` file on your computer to point these domains to the Raspberry Pi's IP address.
