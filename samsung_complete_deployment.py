# requirements.txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-SocketIO==5.3.6
python-socketio==5.8.0
requests==2.31.0
PyYAML==6.0.1
schedule==1.2.0

# config.yaml - Samsung LH55BECHLGFXGO Configuration
system:
  name: "Samsung LH55BECHLGFXGO Video Wall Control System"
  version: "1.0.0"
  debug: false

displays:
  1:
    name: "Samsung LH55BECHLGFXGO-01"
    ip: "192.168.1.101"
    port: 1515
    protocol: "tcp"
    model: "LH55BECHLGFXGO"
    location: "Main Display"
    serial_number: ""
  2:
    name: "Samsung LH55BECHLGFXGO-02"
    ip: "192.168.1.102"
    port: 1515
    protocol: "tcp"
    model: "LH55BECHLGFXGO"
    location: "Left Display"
    serial_number: ""
  3:
    name: "Samsung LH55BECHLGFXGO-03"
    ip: "192.168.1.103"
    port: 1515
    protocol: "tcp"
    model: "LH55BECHLGFXGO"
    location: "Right Display"
    serial_number: ""
  4:
    name: "Samsung LH55BECHLGFXGO-04"
    ip: "192.168.1.104"
    port: 1515
    protocol: "tcp"
    model: "LH55BECHLGFXGO"
    location: "Bottom Display"
    serial_number: ""

server:
  host: "0.0.0.0"
  port: 5000
  secret_key: "samsung-lh55bechlgfxgo-2024"

magicinfo:
  enabled: false
  server_url: ""
  username: "admin"
  password: ""
  api_key: ""

optisigns:
  enabled: false
  server_url: ""
  api_key: ""
  username: "admin"
  password: ""

content:
  static_path: "./static_content"
  upload_path: "./uploads"
  max_file_size_mb: 500
  allowed_extensions: [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi", ".mov", ".webm", ".html"]

monitoring:
  health_check_interval: 30
  temperature_warning_threshold: 60
  temperature_critical_threshold: 70
  max_error_count: 5
  log_retention_days: 30

video_wall:
  enabled: false
  default_layout: "2x2"
  bezel_compensation: true
  auto_power_management: true
  max_grid_size: "10x10"

---

# main.py - Complete Application Entry Point
#!/usr/bin/env python3
"""
Samsung LH55BECHLGFXGO Video Wall Control System
Complete application entry point
"""

import sys
import os
import asyncio
import signal
import threading
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all components
from clean_video_wall_system import *
from samsung_lh55_api_endpoints import *

# Web interface route
@app.route('/')
def index():
    """Serve the main web interface"""
    try:
        # Read the web interface HTML file
        html_file = project_root / 'samsung_lh55_web_interface.html'
        
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Fallback inline HTML if file not found
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Samsung LH55BECHLGFXGO Control</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center; background: linear-gradient(135deg, #1565C0, #1428A0);">
                <h1 style="color: white;">Samsung LH55BECHLGFXGO Video Wall Control System</h1>
                <p style="color: white; font-size: 1.2rem;">System is running. Web interface file not found.</p>
                <p style="color: white;">Please ensure 'samsung_lh55_web_interface.html' is in the project directory.</p>
                <div style="margin-top: 30px;">
                    <a href="/api/displays" style="color: #E3F2FD; text-decoration: none; padding: 10px 20px; border: 2px solid white; border-radius: 5px;">View API</a>
                </div>
            </body>
            </html>
            """
    except Exception as e:
        return f"<html><body><h1>Error loading interface: {str(e)}</h1></body></html>"

# Health check endpoint
@app.route('/health')
def health_check():
    """System health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system': 'Samsung LH55BECHLGFXGO Video Wall Control',
        'version': config.get('system.version', '1.0.0'),
        'displays_configured': len(display_controllers),
        'timestamp': datetime.now().isoformat()
    })

# Static file serving
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    static_dir = Path(config.get('content.static_path', './static_content'))
    return send_from_directory(static_dir, filename)

# Background monitoring task
def start_background_monitoring():
    """Start background monitoring tasks"""
    def monitoring_loop():
        """Background monitoring loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def monitor():
            logger.info("Starting background monitoring for Samsung LH55BECHLGFXGO displays")
            
            while True:
                try:
                    # Health check all displays
                    for display_id, controller in display_controllers.items():
                        try:
                            health = await controller.health_check()
                            
                            # Update database
                            with get_db() as conn:
                                conn.execute('''
                                    INSERT OR REPLACE INTO display_status 
                                    (id, name, ip, online, responsive, temperature, last_update)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    display_id,
                                    controller.status.name,
                                    controller.ip,
                                    health.get('connection', {}).get('status') == 'connected',
                                    health.get('power', {}).get('responsive', False),
                                    health.get('temperature', {}).get('value'),
                                    datetime.now()
                                ))
                                conn.commit()
                            
                            # Temperature alerts
                            temp = health.get('temperature', {}).get('value')
                            if temp and temp > config.get('monitoring.temperature_critical_threshold', 70):
                                logger.critical(f"CRITICAL: Display {display_id} temperature: {temp}°C")
                                socketio.emit('critical_alert', {
                                    'type': 'temperature',
                                    'display_id': display_id,
                                    'temperature': temp,
                                    'message': f'Display {display_id} temperature critical: {temp}°C'
                                })
                            elif temp and temp > config.get('monitoring.temperature_warning_threshold', 60):
                                logger.warning(f"WARNING: Display {display_id} temperature: {temp}°C")
                                
                        except Exception as e:
                            logger.error(f"Health check failed for display {display_id}: {e}")
                    
                    # Wait for next check
                    await asyncio.sleep(config.get('monitoring.health_check_interval', 30))
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    await asyncio.sleep(60)  # Wait longer on error
        
        loop.run_until_complete(monitor())
    
    monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
    monitoring_thread.start()
    logger.info("Background monitoring thread started")

# Graceful shutdown handler
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    
    # Close all display connections
    async def cleanup():
        for controller in display_controllers.values():
            try:
                await controller.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting from display: {e}")
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cleanup())
    except:
        pass
    
    sys.exit(0)

def main():
    """Main application entry point"""
    print("=" * 60)
    print("Samsung LH55BECHLGFXGO Video Wall Control System")
    print("=" * 60)
    print(f"Model: LH55BECHLGFXGO (55\" BEC Series)")
    print(f"Configuration: {config.config_file}")
    print(f"Displays: {len(display_controllers)}")
    print(f"Server: http://0.0.0.0:{config.get('server.port', 5000)}")
    print("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create required directories
    Path(config.get('content.static_path', './static_content')).mkdir(exist_ok=True)
    Path(config.get('content.upload_path', './uploads')).mkdir(exist_ok=True)
    Path('./logs').mkdir(exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Initialize displays
    initialize_displays()
    
    # Start background monitoring
    start_background_monitoring()
    
    # Run the application
    try:
        socketio.run(
            app,
            host=config.get('server.host', '0.0.0.0'),
            port=config.get('server.port', 5000),
            debug=config.get('system.debug', False),
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

---

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

# docker-compose.yml - Docker Deployment
version: '3.8'

services:
  samsung-video-wall:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./static_content:/app/static_content
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./samsung_video_wall.db:/app/samsung_video_wall.db
    environment:
      - PYTHONPATH=/app
      - FLASK_ENV=production
    restart: unless-stopped
    networks:
      - video-wall-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static_content:/usr/share/nginx/html/static:ro
    depends_on:
      - samsung-video-wall
    restart: unless-stopped
    networks:
      - video-wall-network

networks:
  video-wall-network:
    driver: bridge

---

# Dockerfile
FROM python:3.11-slim

LABEL maintainer="Video Wall Admin"
LABEL description="Samsung LH55BECHLGFXGO Video Wall Control System"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p static_content uploads logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application
CMD ["python", "main.py"]

---

# nginx.conf - Production Web Server Configuration
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 500M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/javascript application/xml+rss 
               application/json;
    
    upstream samsung_video_wall {
        server samsung-video-wall:5000;
    }
    
    server {
        listen 80;
        server_name _;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Static content
        location /static/ {
            alias /usr/share/nginx/html/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # API endpoints
        location /api/ {
            proxy_pass http://samsung_video_wall;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }
        
        # WebSocket support for real-time updates
        location /socket.io/ {
            proxy_pass http://samsung_video_wall;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check
        location /health {
            proxy_pass http://samsung_video_wall;
            access_log off;
        }
        
        # Main application
        location / {
            proxy_pass http://samsung_video_wall;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

---

# README.md - Complete Documentation
# Samsung LH55BECHLGFXGO Video Wall Control System

A comprehensive control system specifically designed for Samsung LH55BECHLGFXGO business displays, featuring tablet-optimized web interface and full MDC protocol support.

## 🖥️ Display Specifications

**Samsung LH55BECHLGFXGO Features:**
- **Screen Size:** 55" (1396mm diagonal)
- **Resolution:** 1920 × 1080 (Full HD)
- **Brightness:** 700 cd/m²
- **Contrast Ratio:** 4000:1
- **Viewing Angle:** 178°/178°
- **Response Time:** 8ms
- **Video Wall Support:** Up to 10×10 grid
- **Bezel Width:** 1.7mm
- **Operating Temperature:** 0°C ~ 40°C

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Network access to Samsung LH55BECHLGFXGO displays
- Displays configured for MDC control (TCP/IP, port 1515)

### Installation

1. **Clone and setup:**
```bash
git clone <repository>
cd samsung-lh55bechlgfxgo-control
chmod +x install.sh
./install.sh
```

2. **Configure displays:**
```bash
# Edit config.yaml with your display IP addresses
nano config.yaml
```

3. **Run the system:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python main.py
```

4. **Access the interface:**
```
http://localhost:5000
```

## 📱 Tablet Interface Features

### Display Control
- **Individual Control:** Power, volume, input source, picture settings
- **Real-time Status:** Temperature monitoring, connection status
- **Picture Adjustment:** Brightness, contrast, picture modes
- **Input Management:** HDMI1/2, DVI-D, DisplayPort, RGB, Component, USB

### Video Wall Management
- **Layout Configuration:** Automatic grid layouts (1×1 to 10×10)
- **Test Patterns:** Visual verification of display positioning
- **Bezel Compensation:** Automatic adjustment for seamless content
- **Position Mapping:** Precise display positioning in grid

### Bulk Operations
- **Power Management:** Power all displays ON/OFF simultaneously
- **Volume Control:** Synchronized volume and mute controls
- **Input Switching:** Change all displays to same input source
- **Picture Settings:** Apply same picture mode and settings to all displays

### System Monitoring
- **Temperature Tracking:** Real-time thermal monitoring with alerts
- **Health Dashboard:** Connection status, error tracking, uptime
- **Alert System:** Critical temperature and connectivity warnings
- **Performance Metrics:** System statistics and efficiency monitoring

## 🔧 Configuration

### Display Setup

Each Samsung LH55BECHLGFXGO display must be configured for network control:

1. **Enable MDC Protocol:**
   - Menu → System → MDC → On
   - Set unique Display ID (1-99)
   - Configure network settings

2. **Network Configuration:**
   - Assign static IP addresses
   - Ensure port 1515 is accessible
   - Configure in config.yaml

```yaml
displays:
  1:
    name: "Samsung LH55BECHLGFXGO-01"
    ip: "192.168.1.101"
    port: 1515
    model: "LH55BECHLGFXGO"
    location: "Main Display"
```

### Video Wall Physical Setup

For optimal video wall performance:

1. **Physical Mounting:** Ensure minimal gaps between displays
2. **Bezel Alignment:** Precise alignment for seamless content
3. **Network Topology:** Dedicated network switch recommended
4. **Power Management:** Individual power control or centralized PDU

### Advanced Configuration

```yaml
video_wall:
  enabled: true
  default_layout: "2x2"
  bezel_compensation: true
  auto_power_management: true
  max_grid_size: "10x10"

monitoring:
  health_check_interval: 30
  temperature_warning_threshold: 60
  temperature_critical_threshold: 70
  max_error_count: 5
```

## 🌐 API Documentation

### Display Control Endpoints

```bash
# Power control
POST /api/displays/{id}/power
Body: {"action": "on|off|toggle|status"}

# Volume control
POST /api/displays/{id}/volume
Body: {"volume": 0-100, "mute": true/false}

# Input source
POST /api/displays/{id}/input
Body: {"input": "HDMI1|HDMI2|DVI|DISPLAY_PORT|RGB|COMPONENT|USB"}

# Picture settings
POST /api/displays/{id}/picture
Body: {"mode": "STANDARD|MOVIE|DYNAMIC|NATURAL|CALIBRATED", "brightness": 0-100, "contrast": 0-100}
```

### Video Wall Endpoints

```bash
# Get available layouts
GET /api/video-wall/layouts

# Apply layout
POST /api/video-wall/apply
Body: {"layout_name": "2x2"}

# Test layout
POST /api/video-wall/test
Body: {"layout_name": "2x2", "duration": 15}

# Disable video wall
POST /api/video-wall/disable
```

### Bulk Operations

```bash
# Bulk power control
POST /api/displays/bulk/power
Body: {"action": "on|off", "display_ids": [1,2,3,4]}

# Bulk volume control
POST /api/displays/bulk/volume
Body: {"volume": 0-100, "mute": true/false, "display_ids": [1,2,3,4]}
```

### Monitoring

```bash
# System health
GET /api/monitoring/health

# Get alerts
GET /api/monitoring/alerts?level=error&hours=24

# Display details
GET /api/displays/{id}
```

## 🔍 Troubleshooting

### Common Issues

**Display Not Responding:**
1. Check network connectivity: `ping 192.168.1.101`
2. Verify MDC is enabled in display menu
3. Confirm Display ID matches configuration
4. Check firewall settings on port 1515

**Video Wall Layout Issues:**
1. Ensure all displays are online
2. Verify physical arrangement matches software layout
3. Check bezel compensation settings
4. Test with simple 2×2 layout first

**Temperature Warnings:**
1. Check display ventilation
2. Verify ambient temperature < 40°C
3. Clean display air filters
4. Reduce brightness if necessary

**Web Interface Not Loading:**
1. Check server is running: `systemctl status samsung-video-wall`
2. Verify port 5000 is accessible
3. Check logs: `tail -f logs/video_wall.log`
4. Restart service: `systemctl restart samsung-video-wall`

### Log Analysis

```bash
# View real-time logs
tail -f logs/video_wall.log

# Check system logs
journalctl -u samsung-video-wall -f

# Database queries
sqlite3 samsung_video_wall.db "SELECT * FROM display_status;"
```

## 🏗️ Production Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f samsung-video-wall

# Update configuration
docker-compose restart samsung-video-wall
```

### Systemd Service

```bash
# Install as system service
sudo cp samsung-video-wall.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable samsung-video-wall
sudo systemctl start samsung-video-wall

# Check status
sudo systemctl status samsung-video-wall
```

### Nginx Reverse Proxy

For production environments with SSL:

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/samsung-video-wall
sudo ln -s /etc/nginx/sites-available/samsung-video-wall /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Performance Optimization

### Network Optimization
- **Dedicated VLAN:** Isolate video wall traffic
- **QoS Configuration:** Prioritize control traffic
- **Bandwidth Planning:** 1Mbps per display for control
- **Latency Optimization:** < 10ms network latency recommended

### System Resources
- **CPU Usage:** ~2% per display during normal operation
- **Memory Usage:** ~100MB base + 50MB per display
- **Storage:** ~1GB for system + logs
- **Network:** < 1Mbps per display for telemetry

## 🔒 Security Considerations

### Network Security
- **Firewall Rules:** Restrict access to management ports
- **VPN Access:** Remote management through VPN only
- **Authentication:** Implement user authentication for production
- **HTTPS:** Enable SSL/TLS for web interface

### Access Control
```bash
# Create user authentication (example)
# Add to main.py:
from flask_login import LoginManager, login_required

@app.route('/admin')
@login_required
def admin_panel():
    return render_template('admin.html')
```

## 📈 Monitoring & Maintenance

### Daily Checks
- Display temperature monitoring
- Connection status verification
- Error log review
- Performance metrics analysis

### Weekly Maintenance
- Database cleanup (old logs)
- System backup
- Software updates check
- Network connectivity test

### Monthly Tasks
- Full system diagnostic
- Display firmware updates
- Configuration backup
- Performance optimization review

## 🆘 Support

### Technical Support
- **Documentation:** This README and inline code comments
- **Logs:** Comprehensive logging for troubleshooting
- **API Testing:** Built-in health checks and diagnostics
- **Community:** GitHub issues for bug reports and features

### Emergency Procedures
1. **System Failure:** Restart service, check logs
2. **Display Offline:** Verify network, restart display
3. **Critical Temperature:** Immediate shutdown, check cooling
4. **Data Loss:** Restore from backup, reinitialize database

---

**Samsung LH55BECHLGFXGO Video Wall Control System**  
Version 1.0.0 | Professional Business Display Management  
Optimized for 55" BEC Series with 10×10 Grid Support