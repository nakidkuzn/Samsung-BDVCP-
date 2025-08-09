import os
from typing import Dict, Any

class Config:
    """Main configuration class"""
    
    # Server Configuration
    HOST = os.getenv('VIDEO_WALL_HOST', '0.0.0.0')
    PORT = int(os.getenv('VIDEO_WALL_PORT', 5000))
    DEBUG = os.getenv('VIDEO_WALL_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('VIDEO_WALL_SECRET_KEY', 'your-secret-key-change-this')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'video_wall.db')
    
    # Display Configuration
    DISPLAY_CONFIGS = {
        1: {
            'name': 'Display 1 - Main',
            'ip_address': '192.168.1.101',
            'port': 1515,
            'protocol': 'tcp',
            'brand': 'samsung',  # samsung, lg, sony, etc.
            'model': 'ME75C'
        },
        2: {
            'name': 'Display 2 - Left',
            'ip_address': '192.168.1.102',
            'port': 1515,
            'protocol': 'tcp',
            'brand': 'samsung',
            'model': 'ME75C'
        },
        3: {
            'name': 'Display 3 - Right',
            'ip_address': '192.168.1.103',
            'port': 1515,
            'protocol': 'tcp',
            'brand': 'samsung',
            'model': 'ME75C'
        },
        4: {
            'name': 'Display 4 - Bottom',
            'ip_address': '192.168.1.104',
            'port': 1515,
            'protocol': 'tcp',
            'brand': 'samsung',
            'model': 'ME75C'
        }
    }
    
    # MagicInfo Configuration
    MAGICINFO_CONFIG = {
        'enabled': os.getenv('MAGICINFO_ENABLED', 'False').lower() == 'true',
        'server_url': os.getenv('MAGICINFO_SERVER_URL', 'http://your-magicinfo-server'),
        'username': os.getenv('MAGICINFO_USERNAME', 'admin'),
        'password': os.getenv('MAGICINFO_PASSWORD', 'password'),
        'timeout': 30
    }
    
    # OptiSigns Configuration
    OPTISIGNS_CONFIG = {
        'enabled': os.getenv('OPTISIGNS_ENABLED', 'False').lower() == 'true',
        'api_key': os.getenv('OPTISIGNS_API_KEY', 'your-api-key'),
        'organization_id': os.getenv('OPTISIGNS_ORG_ID', 'your-org-id'),
        'timeout': 30
    }
    
    # Content Storage Configuration
    CONTENT_STORAGE = {
        'local_path': os.getenv('CONTENT_PATH', './content'),
        'max_file_size': 100 * 1024 * 1024,  # 100MB
        'allowed_extensions': ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'webm'],
        'thumbnail_size': (200, 150)
    }
    
    # Network Configuration
    NETWORK_CONFIG = {
        'timeout': 10,
        'retry_attempts': 3,
        'status_check_interval': 30,
        'heartbeat_interval': 60
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'file': os.getenv('LOG_FILE', 'video_wall.log'),
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
