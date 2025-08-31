# PostQuantum DualUSB Token Library

**Enterprise-grade dual USB backup system with post-quantum cryptography protection**

[![PyPI version](https://badge.fury.io/py/pqcdualusb.svg)](https://badge.fury.io/py/pqcdualusb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/pqcdualusb)](https://pepy.tech/project/pqcdualusb)

## What is pqcdualusb?

PostQuantum DualUSB Token Library is a Python package that implements quantum-resistant dual USB token storage with advanced security features. It's designed for organizations and individuals who need maximum protection for sensitive data against both current and future quantum computing threats.

## Why choose pqcdualusb?

### 🛡️ **Quantum-Resistant Security**
- **Post-quantum cryptography** using Dilithium digital signatures
- **Future-proof protection** against quantum computer attacks  
- **NIST-approved algorithms** following latest standards

### 🔐 **Dual USB Architecture**
- **Split secret design** - no single point of failure
- **Physical separation** of authentication tokens
- **Hardware binding** prevents USB drive cloning

### 💎 **Enterprise Features**
- **Memory protection** with secure allocation and cleanup
- **Timing attack resistance** with constant-time operations
- **Comprehensive audit logging** with tamper-evident chains
- **Cross-platform support** for Windows, Linux, and macOS

## Quick Start

```bash
# Install the library
pip install pqcdualusb

# Initialize dual USB setup
pqcdualusb init --primary /media/usb1 --secondary /media/usb2

# Create encrypted backup
pqcdualusb backup --data "sensitive.json" --passphrase "strong-passphrase"

# Restore from backup
pqcdualusb restore --backup-file backup.enc --restore-primary /media/usb_new
```

## Python API Example

```python
from pqcdualusb import init_dual_usb, verify_dual_setup
from pathlib import Path

# Set up dual USB security
primary = Path("/media/usb_primary")
secondary = Path("/media/usb_backup")

success = init_dual_usb(
    primary_path=primary,
    secondary_path=secondary,
    passphrase="your-secure-passphrase"
)

if success:
    print("Dual USB setup complete!")
    is_valid = verify_dual_setup(primary, secondary)
    print(f"Setup verification: {is_valid}")
```

## Use Cases

- **Offline password managers** with air-gapped security
- **Cryptocurrency wallet protection** with dual redundancy
- **Enterprise key custody** solutions
- **Secure document archival** with quantum protection
- **Development environments** requiring secure key storage

## Security Features

| Component | Algorithm | Quantum Resistant |
|-----------|-----------|-------------------|
| Encryption | AES-256-GCM | ✅ |
| Key Derivation | Argon2id | ✅ |
| Digital Signatures | Dilithium | ✅ |
| Authentication | HMAC-SHA256 | ✅ |
| Memory Protection | OS-level locking | ✅ |

## Performance

- **USB Detection**: < 1 second
- **Token Creation**: < 5 seconds
- **Backup/Restore**: 1-10 seconds  
- **Memory Usage**: < 100MB peak

## Requirements

- Python 3.8 or higher
- Windows, Linux, or macOS
- Two USB drives for dual storage setup

## Links

- **GitHub Repository**: https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library
- **Documentation**: Full README with examples
- **Security Policy**: Responsible disclosure process
- **Issue Tracker**: Bug reports and feature requests
- **Releases**: Version history and changelogs

## License

MIT License - see LICENSE file for details.

---

**Secure your digital assets with quantum-resistant protection!**
