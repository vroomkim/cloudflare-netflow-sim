# Cloudflare NetFlow Simulation Generator

This tool simulates NetFlow (v5) traffic to test Cloudflare Magic Network Monitoring using a hybrid PHP/Python architecture.

## Project Structure

- `src/netflow_sim.py`: **Backend Engine**. A Python script that constructs and sends UDP packets mimicking NetFlow v5 data.
- `src/index.php`: **Frontend Dashboard**. A PHP interface to start and stop the background Python process.

## Prerequisites

1. **Python 3**: `sudo apt install python3`
2. **Apache & PHP**: `sudo apt install apache2 php`
3. **Permissions**: The web server user (`www-data`) needs write access to the folder to manage the PID file.

## Installation Guide

1. **Deploy Files**:
   Copy the contents of the `src/` directory to your web root:
   ```bash
   sudo cp src/* /var/www/html/
   ```

2. **Set Permissions**:
   Allow Apache to write the PID file in the directory:
   ```bash
   sudo chown www-data:www-data /var/www/html/index.php
   sudo chown www-data:www-data /var/www/html/netflow_sim.py
   sudo chmod 755 /var/www/html
   ```

## Usage

1. Open your browser: `http://<YOUR_SERVER_IP>/index.php`
2. Enter the **Cloudflare Entry IP** provided in your Cloudflare dashboard.
3. Click **Start**. The dashboard will display the Process ID (PID) of the background generator.

## Traffic Details
The generator simulates traffic from:
- `100.1.1.0/24`
- `212.10.11.0/27`
- Traffic types: HTTP/HTTPS (TCP), DNS (UDP), SSH (TCP), and ICMP.
