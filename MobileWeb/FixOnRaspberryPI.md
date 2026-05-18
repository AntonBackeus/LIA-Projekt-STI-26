# LIA-Projekt-STI-26

This project is an IoT data pipeline and monitoring system for Omron robots. It collects data via a TCP server, stores it in TimescaleDB, and visualizes it through a mobile-friendly web app and Grafana dashboards.

## Project Setup and Tutorial

Follow these steps to get the entire project running on your local machine.

### 1. Prerequisites

Make sure you have the following software installed:
-   **Docker** and **Docker Compose**: To run the database and Grafana.
-   **Python 3.8+**: To run the backend servers.
-   **Node.js 18+** and **npm**: To run the frontend development server.

### 2. Backend and Database Setup

The backend consists of the TimescaleDB database, Grafana, the TCP data ingestion server, and the web API server.

**A. Start the Database and Grafana:**

Navigate to the `data_pipeline` directory and start the services using Docker Compose.

```bash
cd data_pipeline
docker compose up -d
```
This will start TimescaleDB on port `5432` and Grafana on port `3000`.

**B. Install Python Dependencies:**

On the Raspberry Pi, you can install the required packages globally.

```bash
# Navigate to the project root

# Install required packages globally using sudo
# The --break-system-packages flag is required on recent Raspberry Pi OS versions
sudo pip3 install -r requirements.txt --break-system-packages
```

**C. Run the Backend Servers:**

You need to run two separate Python scripts. Open two terminals for this.

-   **Terminal 1: TCP Data Server** (Listens for robot data)
    ```bash
    python robot_server_send_to_timescaleDB.py
    ```
-   **Terminal 2: Mobile Web API Server** (Serves the API for the frontend)
    ```bash
    python MobileWeb/mobile_web_server.py
    ```

### 3. Accessing the System

Once all services are running, you can access them here:
-   **Mobile Web App**: See Frontend Setup below.
-   **Grafana Dashboard**: `http://localhost:3000` (login with user `admin` and password `grafana`). The Omron dashboard is pre-loaded.
-   **TimescaleDB**: Connect using a tool like DBeaver with the credentials from `data_pipeline/.env`.

### 4. Frontend Setup (Development)

The frontend is a React application built with Vite.

**A. Navigate to the `MobileWeb` directory and install dependencies:**
```bash
cd MobileWeb
npm install
```

**B. Start the development server:**
```bash
npm run dev
```
This will start the frontend on `http://localhost:5173` (or another port). You can now access the mobile web app here.

---

## Deployment on Raspberry Pi (Optional)

To create a more professional setup on a device like a Raspberry Pi, you can use `nginx` as a reverse proxy. This allows you to access the web apps with custom local domains (`Robot.STI`, `Grafana.STI`) instead of remembering IP addresses and ports.

`nginx` would be configured to:
1.  Listen for all web traffic on port 80.
2.  Route `http://Robot.STI` requests to the Flask mobile web server (running on port 5001).
3.  Route `http://Grafana.STI` requests to the Grafana instance (running on port 3000).

To make this work, you must also edit the `hosts` file on your client computer to point these domains to the Raspberry Pi's IP address.
