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
