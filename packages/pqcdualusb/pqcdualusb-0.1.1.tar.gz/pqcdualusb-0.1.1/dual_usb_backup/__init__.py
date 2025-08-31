"""
PostQuantum Dual USB Backup Library
===================================

A secure dual USB backup solution with post-quantum cryptography.

Key Features:
- Dual USB storage prevents single point of failure
- Post-quantum cryptography ready (Dilithium signatures)
- Memory protection with secure cleanup
- Timing attack resistance
- Comprehensive audit logging
- Cross-platform support (Windows, Linux, macOS)

Basic Usage:
    >>> import os
    >>> from pathlib import Path
    >>> from dual_usb_backup import init_dual_usb, verify_dual_setup
    >>> 
    >>> # Generate a secret token
    >>> secret = os.urandom(64)
    >>> 
    >>> # Initialize dual USB setup
    >>> result = init_dual_usb(
    ...     secret,
    ...     Path("/media/primary_usb"),
    ...     Path("/media/backup_usb"),
    ...     passphrase="strong-passphrase"
    ... )
    >>> 
    >>> # Verify the setup
    >>> verified = verify_dual_setup(
    ...     Path(result["primary"]),
    ...     Path(result["backup"]),
    ...     passphrase="strong-passphrase"
    ... )
"""

__version__ = "0.1.0"
__author__ = "Johnson Ajibi"

# Import core functionality from the main module
# Note: This maintains backward compatibility with the current single-file structure
try:
    import sys
    from pathlib import Path
    
    # Add parent directory to path to import dual_usb_backup.py
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    from dual_usb_backup import (
        # Main functions
        init_dual_usb,
        verify_dual_setup,
        restore_from_backup,
        rotate_token,
        
        # Security classes
        SecureMemory,
        ProgressReporter,
        SecurityConfig,
        InputValidator,
        TimingAttackMitigation,
        UsbDriveDetector,
        AuditLogRotator,
        
        # Functions
        verify_audit_log,
        pq_available,
        pq_generate_keypair,
        pq_write_audit_keys,
        
        # CLI
        cli as main,
    )
    
except ImportError as e:
    # Fallback for development/testing
    import warnings
    warnings.warn(f"Could not import dual_usb_backup module: {e}")
    
    # Define minimal interface
    def init_dual_usb(*args, **kwargs):
        raise ImportError("dual_usb_backup module not available")
    
    def verify_dual_setup(*args, **kwargs):
        raise ImportError("dual_usb_backup module not available")

__all__ = [
    "__version__",
    "__author__",
    "init_dual_usb",
    "verify_dual_setup", 
    "restore_from_backup",
    "rotate_token",
    "SecureMemory",
    "ProgressReporter",
    "SecurityConfig",
    "InputValidator", 
    "TimingAttackMitigation",
    "UsbDriveDetector",
    "AuditLogRotator",
    "verify_audit_log",
    "pq_available",
    "pq_generate_keypair",
    "pq_write_audit_keys",
    "main",
]
