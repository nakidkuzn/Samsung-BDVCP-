# install.sh - Installation script
#!/bin/bash

echo "Video Wall Control System Installation"
echo "====================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✓ Python $python_version is compatible"
else
    echo "✗ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p content logs data static

# Copy configuration files
echo "Setting up configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file - please update with your settings"
fi

# Initialize database
echo "Initializing database..."
python -c "from app import init_database; init_database()"

# Set permissions
chmod +x start.sh

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your display IP addresses and credentials"
echo "2. Configure your displays in the web interface"
echo "3. Start the server with: ./start.sh"
echo "4. Access the control panel at: http://localhost:5000"
echo ""
