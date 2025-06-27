#!/bin/bash
echo "🔧 Setting up virtual env & dependencies..."
sudo apt update -y
sudo apt install python3 python3-venv python3-pip chromium-browser -y

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

echo "✅ Setup selesai. Jalankan dengan: source venv/bin/activate && python3 bot.py"
