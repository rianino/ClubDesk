#!/bin/bash
# ClubDesk — VPS Bootstrap Script
# Run on a fresh Ubuntu 22.04+ VPS to set up n8n with Docker and Caddy reverse proxy.
#
# Usage:
#   chmod +x setup.sh
#   sudo ./setup.sh
#
# Prerequisites: SSH access to a VPS with a domain pointed to its IP.

set -euo pipefail

echo "=== ClubDesk VPS Setup ==="

# --- 1. System updates ---
echo "[1/6] Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

# --- 2. Install Docker ---
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed."
else
    echo "Docker already installed."
fi

# --- 3. Install Docker Compose ---
echo "[3/6] Installing Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    apt-get install -y -qq docker-compose-plugin
    echo "Docker Compose installed."
else
    echo "Docker Compose already installed."
fi

# --- 4. Create project directory ---
echo "[4/6] Setting up project directory..."
PROJECT_DIR="/opt/clubdesk"
mkdir -p "$PROJECT_DIR"

echo "Copy your docker-compose.yml, Caddyfile, and .env to $PROJECT_DIR"
echo "  cp docker/docker-compose.yml $PROJECT_DIR/"
echo "  cp docker/Caddyfile $PROJECT_DIR/"
echo "  cp docker/.env.example $PROJECT_DIR/.env  (then edit with real values)"

# --- 5. Firewall ---
echo "[5/6] Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
    echo "Firewall configured (80, 443, 22 open)."
else
    echo "ufw not found — configure your firewall manually for ports 80, 443, 22."
fi

# --- 6. UptimeRobot reminder ---
echo "[6/6] Setup complete!"
echo ""
echo "=== NEXT STEPS ==="
echo "1. Point your domain DNS A record to this server's IP address."
echo "2. Edit $PROJECT_DIR/.env with your actual values:"
echo "     N8N_PASSWORD=your-strong-password"
echo "     WEBHOOK_URL=https://n8n.yourdomain.com/"
echo "3. Edit $PROJECT_DIR/Caddyfile — replace 'n8n.yourdomain.com' with your domain."
echo "4. Start the stack:"
echo "     cd $PROJECT_DIR && docker compose up -d"
echo "5. Access n8n at https://n8n.yourdomain.com"
echo "6. Sign up for UptimeRobot (free) and add a monitor for your n8n URL."
echo ""
echo "Done!"
