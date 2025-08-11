
# install.sh - Installation Script
#!/bin/bash

echo "=========================================="
echo "Samsung LH55BECHLGFXGO Video Wall Setup"
echo "=========================================="

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p static_content
mkdir -p uploads
mkdir -p logs
mkdir -p backups

# Set permissions
chmod +x main.py
chmod 755 static_content
chmod 755 uploads
chmod 755 logs

# Create systemd service file
echo "Creating systemd service..."
cat > samsung-video-wall.service << EOF
[Unit]
Description=Samsung LH55BECHLGFXGO Video Wall Control System
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your display IP addresses"
echo "2. Run: python main.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "For system service installation:"
echo "sudo cp samsung-video-wall.service /etc/systemd/system/"
echo "sudo systemctl enable samsung-video-wall"
echo "sudo systemctl start samsung-video-wall"

---
