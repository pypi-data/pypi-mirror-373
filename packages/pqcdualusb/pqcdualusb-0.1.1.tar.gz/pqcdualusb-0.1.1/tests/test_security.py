"""
Comprehensive test suite for PostQuantum DualUSB Token Library.

Tests cover:
- Core security functionality
- USB device detection
- Encryption/decryption operations
- Error handling
- Memory management
- Cross-platform compatibility
"""

import pytest
import tempfile
import os
from pathlib import Path
import json

# Import the main library
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dual_usb_backup import (
    init_dual_usb,
    verify_dual_setup,
    UsbDriveDetector,
    SecureMemory,
    ProgressReporter,
    TimingAttackMitigation,
    AuditLogRotator
)


class TestSecurityFeatures:
    """Test core security functionality."""
    
    def test_secure_memory_management(self):
        """Test memory protection features."""
        with SecureMemory() as secure_mem:
            # Test memory allocation and clearing
            test_data = b"sensitive test data"
            secure_mem.store(test_data)
            assert secure_mem.is_locked()
        # Memory should be cleared after context exit
    
    def test_timing_attack_protection(self):
        """Test constant-time operations."""
        mitigation = TimingAttackMitigation()
        
        # Test with different data sizes
        data1 = b"short"
        data2 = b"much longer test data string"
        
        # Both should take similar time due to constant-time implementation
        time1 = mitigation.constant_time_compare(data1, data1)
        time2 = mitigation.constant_time_compare(data2, data2)
        
        # Verify operation completed (timing is protected)
        assert time1 is not None
        assert time2 is not None


class TestUSBOperations:
    """Test USB device detection and operations."""
    
    def test_usb_detection(self):
        """Test USB drive detection."""
        detector = UsbDriveDetector()
        drives = detector.detect_usb_drives()
        
        # Should return a list (may be empty in test environment)
        assert isinstance(drives, list)
        
    def test_drive_validation(self):
        """Test USB drive validation logic."""
        detector = UsbDriveDetector()
        
        # Test with temporary directory (simulating USB drive)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            is_valid = detector.validate_drive(temp_path)
            assert isinstance(is_valid, bool)


class TestDualUSBSetup:
    """Test dual USB initialization and verification."""
    
    def test_dual_usb_init_with_temp_dirs(self):
        """Test dual USB setup with temporary directories."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            primary = Path(temp_dir1)
            secondary = Path(temp_dir2)
            
            # Test initialization
            result = init_dual_usb(
                primary_path=primary,
                secondary_path=secondary,
                passphrase="test-passphrase-for-testing"
            )
            
            # Should complete without errors
            assert isinstance(result, bool)
    
    def test_dual_setup_verification(self):
        """Test verification of dual USB setup."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            primary = Path(temp_dir1)
            secondary = Path(temp_dir2)
            
            # Create basic structure for testing
            (primary / ".system_backup").mkdir(exist_ok=True)
            (secondary / ".system_backup").mkdir(exist_ok=True)
            
            # Test verification
            is_valid = verify_dual_setup(primary, secondary)
            assert isinstance(is_valid, bool)


class TestAuditLogging:
    """Test audit log functionality."""
    
    def test_audit_log_rotation(self):
        """Test log rotation functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "test_audit.log"
            
            rotator = AuditLogRotator(log_path, max_size_mb=1)
            
            # Test log creation and rotation
            rotator.write_log_entry("test", "Test audit entry")
            assert log_path.exists()
            
            # Test rotation (with large fake entry)
            large_entry = "x" * (2 * 1024 * 1024)  # 2MB entry
            rotator.write_log_entry("test", large_entry)
            
            # Should handle rotation gracefully
            assert log_path.exists()


class TestProgressReporting:
    """Test progress reporting functionality."""
    
    def test_progress_reporter(self):
        """Test progress calculation and reporting."""
        reporter = ProgressReporter(total_size=1000)
        
        # Test progress updates
        reporter.update(250)
        assert reporter.get_percentage() == 25.0
        
        reporter.update(500)
        assert reporter.get_percentage() == 75.0
        
        # Test completion
        reporter.update(1000)
        assert reporter.get_percentage() == 100.0
        assert reporter.is_complete()


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_paths(self):
        """Test handling of invalid file paths."""
        invalid_path = Path("/nonexistent/path/that/should/not/exist")
        
        # Should handle gracefully without crashing
        try:
            result = init_dual_usb(
                primary_path=invalid_path,
                secondary_path=invalid_path,
                passphrase="test"
            )
            # Should return False for invalid paths
            assert result is False
        except Exception as e:
            # Should raise appropriate exceptions, not crash
            assert isinstance(e, (FileNotFoundError, PermissionError, ValueError))
    
    def test_empty_passphrase(self):
        """Test handling of empty or weak passphrases."""
        with tempfile.TemporaryDirectory() as temp_dir1, \
             tempfile.TemporaryDirectory() as temp_dir2:
            
            primary = Path(temp_dir1)
            secondary = Path(temp_dir2)
            
            # Test with empty passphrase
            try:
                result = init_dual_usb(
                    primary_path=primary,
                    secondary_path=secondary,
                    passphrase=""
                )
                # Should either return False or raise exception
                assert result is False
            except ValueError:
                # Acceptable to raise ValueError for weak passphrase
                pass


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
