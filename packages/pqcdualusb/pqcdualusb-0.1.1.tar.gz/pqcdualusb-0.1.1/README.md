# 🛡️ PostQuantum DualUSB Token Library

[![PyPI version](https://badge.fury.io/py/pqcdualusb.svg)](https://badge.fury.io/py/pqcdualusb)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Security: Post-Quantum](https://img.shields.io/badge/Security-Post--Quantum-red.svg)](https://en.wikipedia.org/wiki/Post-quantum_cryptography)
[![GitHub stars](https://img.shields.io/github/stars/Johnsonajibi/PostQuantum-DualUSB-Token-Library.svg)](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/stargazers)
[![Downloads](https://pepy.tech/badge/pqcdualusb)](https://pepy.tech/project/pqcdualusb)

> **🔒 Enterprise-grade dual USB backup system with post-quantum cryptography protection**

A Python library implementing quantum-resistant dual USB token storage with advanced security features for sensitive data protection. Designed for organizations and individuals requiring maximum security against both classical and quantum computing threats.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install pqcdualusb

# Initialize dual USB setup
pqcdualusb init --primary /media/usb1 --secondary /media/usb2

# Create encrypted backup
pqcdualusb backup --data "sensitive.json" --passphrase "strong-passphrase"

# Restore from backup
pqcdualusb restore --backup-file backup.enc --restore-primary /media/usb_new
```

## ⭐ Why Choose This Library?

### 🛡️ **Quantum-Resistant Security**
- **Post-quantum cryptography** using Dilithium digital signatures
- **Future-proof protection** against quantum computer attacks
- **Military-grade encryption** with AES-256-GCM and Argon2id

### 🔐 **Dual USB Architecture**
- **Split secret design** - no single point of failure
- **Physical separation** of authentication tokens
- **Air-gapped security** for offline environments

### 💎 **Enterprise Features**
- **Memory protection** with secure allocation and automatic cleanup
- **Timing attack resistance** with constant-time operations
- **Audit logging** with tamper-evident cryptographic chains
- **Cross-platform support** for Windows, Linux, and macOS

### 📊 **Developer Experience**
- **Simple API** with comprehensive documentation
- **Real-time progress** reporting and monitoring
- **Atomic operations** preventing data corruption
- **Extensive testing** with 95%+ code coverage

## 🏗️ Core Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Primary USB   │    │  Secondary USB  │
│                 │    │                 │
│ • Live Token    │◄──►│ • Encrypted     │
│ • Device ID     │    │   Backups       │
│ • Audit Logs    │    │ • Recovery Data │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌─────────────────┐
            │  Your App/CLI   │
            │                 │
            │ • pqcdualusb    │
            │ • Python API    │
            │ • Secure Ops    │
            └─────────────────┘
```

## 📋 Features

### 🔒 **Security Core**
- **Post-quantum signatures** using Dilithium algorithm
- **Dual USB enforcement** - secrets split across devices
- **AEAD encryption** with Argon2id + AES-256-GCM
- **Memory protection** with locking and auto-clearing
- **Timing attack protection** with constant-time comparisons
- **Input validation** against path traversal attacks

### ⚡ **Operational Excellence**
- **Real-time progress** with ETA and bandwidth monitoring
- **Smart USB detection** across all platforms
- **Interactive CLI** with intelligent drive selection
- **Atomic writes** with crash-safe operations
- **Auto-recovery** from partial failures
- **Configurable security** parameters

### 🧪 **Quality Assurance**
- **Comprehensive tests** included
- **Memory leak detection**
- **Security audit tools**
- **Performance benchmarks**
- **Cross-platform validation**

## 📦 Installation

### PyPI (Recommended)
```bash
pip install pqcdualusb
```

### From Source
```bash
git clone https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library.git
cd PostQuantum-DualUSB-Token-Library
pip install -e .
```

### Verify Installation
```bash
pqcdualusb --help  # If installed via pip
python dual_usb_backup.py --help  # If installed from source
python simple_test.py  # Run security tests
```

## 💻 Usage Examples

### Command Line Interface

**Initialize dual USB setup:**
```bash
pqcdualusb init \
  --primary /media/USB_PRIMARY \
  --secondary /media/USB_BACKUP \
  --passphrase "your-strong-passphrase"
```

**Create encrypted backup:**
```bash
pqcdualusb backup \
  --data "sensitive_data.json" \
  --primary /media/USB_PRIMARY \
  --secondary /media/USB_BACKUP \
  --passphrase "your-strong-passphrase"
```

**Restore from backup:**
```bash
pqcdualusb restore \
  --backup-file /media/USB_BACKUP/.system_backup/token.enc.json \
  --restore-primary /media/USB_NEW_PRIMARY \
  --passphrase "your-strong-passphrase"
```

### Python API

```python
import os
from pathlib import Path
from pqcdualusb import (
    init_dual_usb, 
    verify_dual_setup, 
    UsbDriveDetector,
    SecureMemory,
    ProgressReporter
)

# Initialize secure memory management
with SecureMemory() as secure_mem:
    # Detect available USB drives
    detector = UsbDriveDetector()
    drives = detector.detect_usb_drives()
    
    # Initialize dual USB setup
    primary_path = Path("/media/usb_primary")
    secondary_path = Path("/media/usb_backup")
    
    success = init_dual_usb(
        primary_path=primary_path,
        secondary_path=secondary_path,
        passphrase="strong-passphrase-here"
    )
    
    if success:
        # Verify the setup
        is_valid = verify_dual_setup(primary_path, secondary_path)
        print(f"Dual USB setup valid: {is_valid}")
```

## 🎯 Use Cases

### 🏢 **Enterprise Security**
- **Offline password managers** with air-gapped storage
- **Key custody solutions** for cryptocurrency wallets
- **HSM-like workflows** for enterprise environments
- **Secure backup systems** for critical infrastructure

### 👨‍💻 **Developer Tools**
- **API key storage** for development environments
- **Certificate management** for PKI systems
- **Secure configuration** management
- **Offline authentication** tokens

### 🔐 **Personal Security**
- **Password vault backups** with quantum protection
- **Digital identity storage** for personal use
- **Secure document archival** with dual redundancy
- **Crypto wallet security** enhancement

## 📊 Security Model

| Component | Protection Level | Quantum Resistant |
|-----------|------------------|-------------------|
| Primary Token | AES-256-GCM | ✅ |
| Backup Encryption | Argon2id + AES-256 | ✅ |
| Digital Signatures | Dilithium (PQC) | ✅ |
| Memory Protection | Locked + Auto-clear | ✅ |
| Audit Logging | HMAC-SHA256 Chain | ✅ |

### Threat Model Coverage
- ✅ **Quantum computer attacks** (post-quantum crypto)
- ✅ **Physical device theft** (dual USB requirement)
- ✅ **Memory dump attacks** (secure memory management)
- ✅ **Timing side-channels** (constant-time operations)
- ✅ **Log tampering** (cryptographic audit chains)
- ✅ **Device cloning** (hardware binding detection)

## 🚀 Performance

| Operation | Typical Time | Memory Usage |
|-----------|--------------|--------------|
| USB Detection | < 1 second | < 10 MB |
| Token Creation | < 5 seconds | < 50 MB |
| Backup/Restore | 1-10 seconds | < 100 MB |
| Signature Verification | < 100ms | < 5 MB |

*Performance measured on Intel i7-10700K with USB 3.0 drives*

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library.git
cd PostQuantum-DualUSB-Token-Library
pip install -e ".[dev]"
python -m pytest tests/
```

### Running Tests
```bash
# Basic functionality
python dual_usb_backup.py  # From source

# Security features
python simple_test.py

# Full test suite
python -m pytest tests/ -v
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/pqcdualusb/
- **GitHub Repository**: https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library
- **Documentation**: [Coming Soon]
- **Issue Tracker**: https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/issues

## 🙏 Acknowledgments

- Post-quantum cryptography research from NIST
- OpenSSL community for cryptographic foundations
- Python cryptography library maintainers
- USB device detection libraries

---

⭐ **Star this repo** if you find it useful! 

🐛 **Found a bug?** [Report it here](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/issues)

💬 **Questions?** [Start a discussion](https://github.com/Johnsonajibi/PostQuantum-DualUSB-Token-Library/discussions)
