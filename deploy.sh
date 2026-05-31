#!/bin/bash
set -e
echo "=== UTD24 Deploy ==="

if ! command -v docker &> /dev/null; then
    echo Install Docker...
    curl -fsSL https://get.docker.com | sh
fi

if ! docker compose version &> /dev/null 2>&1; then
    echo Install Docker Compose...
    apt-get update -qq && apt-get install -y -qq docker-compose-plugin
fi

REPO_URL="${REPO_URL:-https://github.com/YOU/utd-from-here.git}"
APP_DIR="$HOME/utd-from-here"

if [ -d "$APP_DIR" ]; then
    cd "$APP_DIR" && git pull
else
    git clone "$REPO_URL" "$APP_DIR" && cd "$APP_DIR"
fi

if [ ! -f .env ]; then
    cp .env.example .env
    PW=$(openssl rand -hex 16 2>/dev/null || echo "utd24_$(date +%s)")
    sed -i "s/POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$PW/" .env
fi

docker compose down 2>/dev/null
docker compose up -d --build

IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_IP")
echo "Done! http://$IP:8000"

