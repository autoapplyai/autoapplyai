#!/bin/bash

set -e  # Exit immediately on error

echo "🔧 Fixing config..."
chmod +x fix_config.sh
./fix_config.sh

echo "📂 Verifying jobs.json..."
if [ ! -s jobs.json ]; then
  echo "⚠️ jobs.json not found or empty—using static fallback."
  cp config/job_list.json jobs.json
fi

echo "🚀 Running application script..."
python generate_application.py

