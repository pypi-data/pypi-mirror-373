"""
Secure Storage Utility for SNID SAGE
=====================================

Provides secure storage for sensitive information like API keys using encryption.
Uses platform keyring when available, falls back to encrypted file storage.
"""

import os
import json
import base64
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import cryptography, fall back to basic storage if not available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from snid_sage.shared.utils.logging import get_logger
    _LOGGER = get_logger('secure_storage')
except ImportError:
    import logging
    _LOGGER = logging.getLogger('secure_storage')


class SecureStorage:
    """Secure storage for sensitive configuration data"""
    
    def __init__(self, app_name: str = "SNID_SAGE"):
        self.app_name = app_name
        self._storage_dir = self._get_storage_directory()
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Try to use system keyring first
        self._use_keyring = self._test_keyring()
        
        if not self._use_keyring:
            _LOGGER.info("System keyring not available, using encrypted file storage")
    
    def _get_storage_directory(self) -> Path:
        """Get secure storage directory"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home())) / self.app_name
        else:  # Unix-like systems
            config_dir = Path.home() / '.config' / self.app_name.lower()
        
        return config_dir / 'secure'
    
    def _test_keyring(self) -> bool:
        """Test if system keyring is available"""
        try:
            import keyring
            # Test storing and retrieving a value
            test_key = f"{self.app_name}_test"
            keyring.set_password(self.app_name, test_key, "test_value")
            retrieved = keyring.get_password(self.app_name, test_key)
            keyring.delete_password(self.app_name, test_key)
            return retrieved == "test_value"
        except Exception as e:
            _LOGGER.debug(f"Keyring test failed: {e}")
            return False
    
    def _get_encryption_key(self, identifier: str) -> bytes:
        """Generate encryption key from machine-specific data"""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("Cryptography library not available")
            
        # Use machine-specific information to derive key
        machine_info = f"{os.environ.get('USERNAME', 'user')}-{os.environ.get('COMPUTERNAME', 'machine')}"
        password = f"{self.app_name}-{identifier}-{machine_info}".encode()
        
        
        salt = hashlib.sha256(f"{self.app_name}-{identifier}".encode()).digest()[:16]
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def store_secure(self, identifier: str, value: str) -> bool:
        """Store a value securely"""
        try:
            if self._use_keyring:
                return self._store_keyring(identifier, value)
            else:
                return self._store_encrypted_file(identifier, value)
        except Exception as e:
            _LOGGER.error(f"Failed to store secure value for {identifier}: {e}")
            return False
    
    def retrieve_secure(self, identifier: str) -> Optional[str]:
        """Retrieve a stored secure value"""
        try:
            if self._use_keyring:
                return self._retrieve_keyring(identifier)
            else:
                return self._retrieve_encrypted_file(identifier)
        except Exception as e:
            _LOGGER.error(f"Failed to retrieve secure value for {identifier}: {e}")
            return None
    
    def delete_secure(self, identifier: str) -> bool:
        """Delete a stored secure value"""
        try:
            if self._use_keyring:
                return self._delete_keyring(identifier)
            else:
                return self._delete_encrypted_file(identifier)
        except Exception as e:
            _LOGGER.error(f"Failed to delete secure value for {identifier}: {e}")
            return False
    
    def _store_keyring(self, identifier: str, value: str) -> bool:
        """Store using system keyring"""
        try:
            import keyring
            keyring.set_password(self.app_name, identifier, value)
            return True
        except Exception as e:
            _LOGGER.error(f"Keyring storage failed: {e}")
            return False
    
    def _retrieve_keyring(self, identifier: str) -> Optional[str]:
        """Retrieve using system keyring"""
        try:
            import keyring
            return keyring.get_password(self.app_name, identifier)
        except Exception as e:
            _LOGGER.error(f"Keyring retrieval failed: {e}")
            return None
    
    def _delete_keyring(self, identifier: str) -> bool:
        """Delete using system keyring"""
        try:
            import keyring
            keyring.delete_password(self.app_name, identifier)
            return True
        except Exception as e:
            _LOGGER.error(f"Keyring deletion failed: {e}")
            return False
    
    def _store_encrypted_file(self, identifier: str, value: str) -> bool:
        """Store using encrypted file"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                _LOGGER.warning("Cryptography not available, storing with basic obfuscation")
                return self._store_obfuscated_file(identifier, value)
                
            key = self._get_encryption_key(identifier)
            fernet = Fernet(key)
            encrypted_value = fernet.encrypt(value.encode())
            
            storage_file = self._storage_dir / f"{identifier}.enc"
            with open(storage_file, 'wb') as f:
                f.write(encrypted_value)
            
            # Set restrictive permissions (owner only)
            os.chmod(storage_file, 0o600)
            return True
        except Exception as e:
            _LOGGER.error(f"Encrypted file storage failed: {e}")
            return False
    
    def _retrieve_encrypted_file(self, identifier: str) -> Optional[str]:
        """Retrieve using encrypted file"""
        try:
            storage_file = self._storage_dir / f"{identifier}.enc"
            if not storage_file.exists():
                # Try obfuscated file if encrypted doesn't exist
                return self._retrieve_obfuscated_file(identifier)
            
            if not CRYPTOGRAPHY_AVAILABLE:
                return self._retrieve_obfuscated_file(identifier)
            
            key = self._get_encryption_key(identifier)
            fernet = Fernet(key)
            
            with open(storage_file, 'rb') as f:
                encrypted_value = f.read()
            
            decrypted_value = fernet.decrypt(encrypted_value)
            return decrypted_value.decode()
        except Exception as e:
            _LOGGER.error(f"Encrypted file retrieval failed: {e}")
            # Try obfuscated fallback
            return self._retrieve_obfuscated_file(identifier)
    
    def _delete_encrypted_file(self, identifier: str) -> bool:
        """Delete encrypted file"""
        try:
            storage_file = self._storage_dir / f"{identifier}.enc"
            if storage_file.exists():
                storage_file.unlink()
            # Also try to delete obfuscated file
            self._delete_obfuscated_file(identifier)
            return True
        except Exception as e:
            _LOGGER.error(f"Encrypted file deletion failed: {e}")
            return False
    
    def _store_obfuscated_file(self, identifier: str, value: str) -> bool:
        """Store using basic obfuscation (not secure, but better than plain text)"""
        try:
            # Simple base64 obfuscation (NOT SECURE)
            obfuscated = base64.b64encode(value.encode()).decode()
            
            storage_file = self._storage_dir / f"{identifier}.obf"
            with open(storage_file, 'w') as f:
                f.write(obfuscated)
            
            # Set restrictive permissions (owner only)
            os.chmod(storage_file, 0o600)
            _LOGGER.warning(f"API key stored with basic obfuscation (not secure). Consider installing 'cryptography' package.")
            return True
        except Exception as e:
            _LOGGER.error(f"Obfuscated file storage failed: {e}")
            return False
    
    def _retrieve_obfuscated_file(self, identifier: str) -> Optional[str]:
        """Retrieve using basic obfuscation"""
        try:
            storage_file = self._storage_dir / f"{identifier}.obf"
            if not storage_file.exists():
                return None
            
            with open(storage_file, 'r') as f:
                obfuscated = f.read()
            
            # Simple base64 deobfuscation
            value = base64.b64decode(obfuscated).decode()
            return value
        except Exception as e:
            _LOGGER.error(f"Obfuscated file retrieval failed: {e}")
            return None
    
    def _delete_obfuscated_file(self, identifier: str) -> bool:
        """Delete obfuscated file"""
        try:
            storage_file = self._storage_dir / f"{identifier}.obf"
            if storage_file.exists():
                storage_file.unlink()
            return True
        except Exception as e:
            _LOGGER.error(f"Obfuscated file deletion failed: {e}")
            return False


# Global instance
_secure_storage = None

def get_secure_storage() -> SecureStorage:
    """Get the global secure storage instance"""
    global _secure_storage
    if _secure_storage is None:
        _secure_storage = SecureStorage()
    return _secure_storage


def store_api_key(service: str, api_key: str) -> bool:
    """Store an API key securely"""
    storage = get_secure_storage()
    return storage.store_secure(f"api_key_{service}", api_key)


def retrieve_api_key(service: str) -> Optional[str]:
    """Retrieve an API key securely"""
    storage = get_secure_storage()
    return storage.retrieve_secure(f"api_key_{service}")


def delete_api_key(service: str) -> bool:
    """Delete an API key securely"""
    storage = get_secure_storage()
    return storage.delete_secure(f"api_key_{service}")