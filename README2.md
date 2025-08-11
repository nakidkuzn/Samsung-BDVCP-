# Samsung-BDVCP
Media Wall Control Hub for Samsung Business Display 2x2 Matrix

# README.md - Setup and usage documentation
# Video Wall Control System

A comprehensive video wall control system with web-based interface for managing multiple displays, content deployment, and integration with digital signage platforms.

## Features

- **Multi-Display Control**: Power, volume, input source management
- **Content Management**: Static images, videos, streaming content
- **Platform Integration**: MagicInfo, OptiSigns, custom URLs
- **Real-time Monitoring**: Live status updates via WebSockets
- **Scheduling**: Automated content deployment
- **REST API**: Complete API for external integrations
- **Responsive UI**: Tablet-optimized control interface

## Quick Start

1. **Clone and Install**:
   ```bash
   git clone <repository>
   cd video-wall-control
   chmod +x install.sh
   ./install.sh
   ```

2. **Configure**:
   ```bash
   # Update .env file with your settings
   nano .env
   ```

3. **Start Server**:
   ```bash
   ./start.sh
   ```

4. **Access Interface**:
   Open http://localhost:5000 in your browser

## Display Compatibility

### Samsung Displays
- Uses MDC (Multi Display Control) protocol
- Supports ME, QM, PM series
- TCP/IP connection on port 1515

### LG Displays
- Uses HTTP API
- Supports webOS displays
- Connection via HTTP REST API

### Custom Integration
- Easily extensible for other brands
- Implement BaseDisplayController class

## Configuration

### Display Setup
Update `DISPLAY_CONFIGS` in config.py or use the web interface:

```python
DISPLAY_CONFIGS = {
    1: {
        'name': 'Main Display',
        'ip_address': '192.168.1.101',
        'brand': 'samsung',
        'model': 'ME75C'
    }
}
```

### Network Requirements
- Displays must be on same network as server
- Enable MDC/Network control on displays
- Configure static IP addresses for displays

## API Documentation

### Display Control
```
POST /api/displays/{id}/power
POST /api/displays/{id}/volume
POST /api/displays/{id}/input
GET  /api/displays/{id}/status
```

### Content Management
```
POST /api/content/deploy
GET  /api/content/library
POST /api/schedule
```

### Integration APIs
```
GET /api/magicinfo/channels
GET /api/optisigns/playlists
```

## Production Deployment

### Docker Deployment
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

### System Service
```bash
# Install as system service
sudo cp video-wall.service /etc/systemd/system/
sudo systemctl enable video-wall
sudo systemctl start video-wall
```

## Troubleshooting

### Common Issues

1. **Display Not Responding**:
   - Check network connectivity
   - Verify MDC is enabled on display
   - Confirm IP address and port

2. **Content Not Deploying**:
   - Verify content URLs are accessible
   - Check display input source
   - Review logs for errors

3. **WebSocket Disconnections**:
   - Check firewall settings
   - Verify proxy configuration
   - Monitor server resources

### Logs
- Application logs: `logs/video_wall.log`
- Docker logs: `docker-compose logs`
- System logs: `journalctl -u video-wall`

## Support

For technical support and feature requests, please refer to the documentation or create an issue in the repository.
