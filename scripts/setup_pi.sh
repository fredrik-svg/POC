#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Installerar systempaket ..."
sudo apt-get update
sudo apt-get install -y python3-pip portaudio19-dev sox

echo "📦 Installerar Pythonpaket ..."
python3 -m pip install -r pi-client/requirements.txt

if [ ! -f pi-client/.env ]; then
  echo "🔑 Skapar pi-client/.env (kopierar exempel)"
  cp pi-client/.env.example pi-client/.env
  echo "   ➜ Glöm inte att fylla i OPENAI_API_KEY i pi-client/.env"
fi

echo "✅ Klart. Kör: python3 pi-client/pi_realtime_client.py"
