#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install -r backend-minimal/requirements.txt
cp -n backend-minimal/.env.example backend-minimal/.env || true
uvicorn backend-minimal.app:app --host 0.0.0.0 --port 8080 --reload
