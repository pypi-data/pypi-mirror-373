"""
Configuration management for TerminalChat client
"""
import os
from typing import Dict, Any

class Config:
    """Configuration class for TerminalChat client"""
    
    DEFAULT_SERVER = "terminalchat-server-1.onrender.com:443"
    DEFAULT_RECONNECT_ATTEMPTS = 3
    DEFAULT_PING_INTERVAL = 30
    DEFAULT_PING_TIMEOUT = 15
    DEFAULT_CLOSE_TIMEOUT = 15
    DEFAULT_CONNECTION_TIMEOUT = 30
    DEFAULT_MAX_IMAGE_SIZE = 2 * 1024 * 1024  # Reduced to 2MB for better server compatibility
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'} 

    @classmethod
    def get_server_address(cls) -> str:
        """Get server address from environment or default"""
        return os.getenv('TERMINALCHAT_SERVER', cls.DEFAULT_SERVER)
    
    @classmethod
    def get_max_reconnect_attempts(cls) -> int:
        """Get maximum reconnection attempts"""
        try:
            return int(os.getenv('TERMINALCHAT_MAX_RECONNECT', cls.DEFAULT_RECONNECT_ATTEMPTS))
        except (ValueError, TypeError):
            return cls.DEFAULT_RECONNECT_ATTEMPTS
    
    @classmethod
    def get_websocket_config(cls) -> Dict[str, Any]:
        """Get WebSocket connection configuration"""
        return {
            'ping_interval': cls.DEFAULT_PING_INTERVAL,
            'ping_timeout': cls.DEFAULT_PING_TIMEOUT,
            'close_timeout': cls.DEFAULT_CLOSE_TIMEOUT,
            'open_timeout': cls.DEFAULT_CONNECTION_TIMEOUT,
        }
    
    @classmethod
    def is_debug_mode(cls) -> bool:
        """Check if debug mode is enabled"""
        return os.getenv('TERMINALCHAT_DEBUG', '').lower() in ('true', '1', 'yes', 'on')
    
    @classmethod
    def get_log_level(cls) -> str:
        """Get logging level"""
        level = os.getenv('TERMINALCHAT_LOG_LEVEL', 'WARNING').upper()
        return level if level in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') else 'WARNING'
    
    @classmethod
    def get_max_image_size(cls) -> int:
        """Get maximum allowed image size in bytes"""
        try:
            return int(os.getenv('TERMINALCHAT_MAX_IMAGE_SIZE', cls.DEFAULT_MAX_IMAGE_SIZE))
        except (ValueError, TypeError):
            return cls.DEFAULT_MAX_IMAGE_SIZE
    
    @classmethod
    def get_supported_image_formats(cls) -> set:
        """Get supported image formats"""
        return cls.SUPPORTED_IMAGE_FORMATS