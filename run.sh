#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "[config] Stopping existing containers..."
docker compose down

echo "[config] Rebuilding images..."
docker compose build

echo "[config] Starting containers in detached mode..."
docker compose up -d
