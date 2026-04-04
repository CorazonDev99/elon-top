#!/bin/bash
# ─── Oson Reklama Bot — Setup Script ───
# Run: chmod +x setup.sh && ./setup.sh

set -e

echo "🚀 Setting up Elon Top Bot..."

# 1. Install python3-venv if not available
echo "📦 Checking python3-venv..."
sudo apt-get update -qq
sudo apt-get install -y python3-venv python3-full

# 2. Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# 3. Activate and install dependencies
echo "📦 Installing dependencies..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Create systemd service
echo "⚙️ Creating systemd service..."
WORK_DIR=$(pwd)
USER=$(whoami)

sudo tee /etc/systemd/system/elon-top-bot.service > /dev/null << EOF
[Unit]
Description=Oson Reklama Telegram Bot
After=network.target postgresql.service redis.service
Wants=network-online.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${WORK_DIR}
ExecStart=${WORK_DIR}/venv/bin/python -m bot.main
Restart=always
RestartSec=5
StartLimitIntervalSec=60
StartLimitBurst=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=elon-top-bot

# Environment
EnvironmentFile=${WORK_DIR}/.env

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# 5. Enable and start
echo "🔄 Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable elon-top-bot.service
sudo systemctl start elon-top-bot.service

echo ""
echo "✅ Bot setup complete!"
echo ""
echo "📋 Useful commands:"
echo "   sudo systemctl status elon-top-bot    — Check status"
echo "   sudo systemctl restart elon-top-bot   — Restart bot"
echo "   sudo systemctl stop elon-top-bot      — Stop bot"
echo "   sudo journalctl -u elon-top-bot -f    — View logs (live)"
echo ""
