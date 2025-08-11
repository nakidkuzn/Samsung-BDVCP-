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
