"""
Configuration management following industry best practices.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    """Security configuration parameters."""
    
    # Argon2 parameters
    argon2_memory: int = 1048576  # 1GB in KiB
    argon2_time: int = 4
    argon2_parallelism: int = 4
    
    # Passphrase requirements
    min_passphrase_length: int = 12
    require_passphrase_complexity: bool = True
    
    # Audit log settings
    audit_log_max_size: int = 10 * 1024 * 1024  # 10MB
    audit_log_max_files: int = 5
    
    # Security timeouts
    operation_timeout: int = 300  # 5 minutes
    memory_lock_timeout: int = 60  # 1 minute
    
    # Post-quantum settings
    default_pq_algorithm: str = "Dilithium3"
    enable_pq_by_default: bool = True
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """Load configuration from environment variables."""
        return cls(
            argon2_memory=int(os.getenv('DUAL_USB_ARGON2_M', cls.argon2_memory)),
            argon2_time=int(os.getenv('DUAL_USB_ARGON2_T', cls.argon2_time)),
            argon2_parallelism=int(os.getenv('DUAL_USB_ARGON2_P', cls.argon2_parallelism)),
            min_passphrase_length=int(os.getenv('DUAL_USB_MIN_PASSPHRASE', cls.min_passphrase_length)),
            audit_log_max_size=int(os.getenv('DUAL_USB_AUDIT_MAX_SIZE', cls.audit_log_max_size)),
            audit_log_max_files=int(os.getenv('DUAL_USB_AUDIT_MAX_FILES', cls.audit_log_max_files)),
            operation_timeout=int(os.getenv('DUAL_USB_TIMEOUT', cls.operation_timeout)),
            default_pq_algorithm=os.getenv('DUAL_USB_PQ_ALG', cls.default_pq_algorithm),
            enable_pq_by_default=os.getenv('DUAL_USB_ENABLE_PQ', 'true').lower() == 'true',
        )
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.argon2_memory < 1024:  # Minimum 1MB
            raise ValueError("Argon2 memory must be at least 1024 KiB")
        
        if self.argon2_time < 1:
            raise ValueError("Argon2 time must be at least 1")
        
        if self.argon2_parallelism < 1:
            raise ValueError("Argon2 parallelism must be at least 1")
        
        if self.min_passphrase_length < 8:
            raise ValueError("Minimum passphrase length must be at least 8")
        
        if self.audit_log_max_size < 1024:  # Minimum 1KB
            raise ValueError("Audit log max size must be at least 1024 bytes")


def get_config_dir() -> Path:
    """Get the configuration directory following XDG standards."""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
    else:  # Unix-like
        config_dir = Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config'))
    
    return config_dir / 'pqcdualusb'


def get_data_dir() -> Path:
    """Get the data directory following XDG standards."""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    else:  # Unix-like
        data_dir = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local' / 'share'))
    
    return data_dir / 'pqcdualusb'


def ensure_directories() -> None:
    """Ensure configuration and data directories exist."""
    config_dir = get_config_dir()
    data_dir = get_data_dir()
    
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Set restrictive permissions on Unix-like systems
    if os.name != 'nt':
        try:
            config_dir.chmod(0o700)
            data_dir.chmod(0o700)
        except OSError:
            pass
