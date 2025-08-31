"""
Custom exceptions for the dual USB backup library.
"""


class DualUSBError(Exception):
    """Base exception for all dual USB backup operations."""
    pass


class SecurityError(DualUSBError):
    """Raised when security constraints are violated."""
    pass


class ValidationError(DualUSBError):
    """Raised when input validation fails."""
    pass


class AuditError(DualUSBError):
    """Raised when audit log operations fail."""
    pass


class USBError(DualUSBError):
    """Raised when USB device operations fail."""
    pass


class CryptographyError(DualUSBError):
    """Raised when cryptographic operations fail."""
    pass


class ConfigurationError(DualUSBError):
    """Raised when configuration is invalid."""
    pass
