"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Cryptographic utilities for secure data handling and protection.
"""

import hashlib
import hmac
import secrets
import time
from base64 import b64decode, b64encode
from typing import Any, Dict, Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

from ..config.logging_setup import get_logger

logger = get_logger("xsystem.security.crypto")


class CryptoError(Exception):
    """Base exception for cryptographic operations."""
    pass


class SecureHash:
    """Secure hashing utilities."""
    
    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """
        Compute SHA-256 hash.

        Args:
            data: Data to hash

        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: Union[str, bytes]) -> str:
        """
        Compute SHA-512 hash.

        Args:
            data: Data to hash

        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def blake2b(data: Union[str, bytes], key: Optional[bytes] = None) -> str:
        """
        Compute BLAKE2b hash.

        Args:
            data: Data to hash
            key: Optional key for keyed hashing

        Returns:
            Hexadecimal hash string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.blake2b(data, key=key).hexdigest()

    @staticmethod
    def hmac_sha256(data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """
        Compute HMAC-SHA256.

        Args:
            data: Data to authenticate
            key: Secret key

        Returns:
            Hexadecimal HMAC string
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    @staticmethod
    def verify_hmac(data: Union[str, bytes], key: Union[str, bytes], expected_hmac: str) -> bool:
        """
        Verify HMAC-SHA256.

        Args:
            data: Data to verify
            key: Secret key
            expected_hmac: Expected HMAC value

        Returns:
            True if HMAC is valid
        """
        computed_hmac = SecureHash.hmac_sha256(data, key)
        return hmac.compare_digest(computed_hmac, expected_hmac)


class SecureRandom:
    """Cryptographically secure random number generation."""
    
    @staticmethod
    def token_bytes(length: int = 32) -> bytes:
        """
        Generate random bytes.

        Args:
            length: Number of bytes to generate

        Returns:
            Random bytes
        """
        return secrets.token_bytes(length)

    @staticmethod
    def token_hex(length: int = 32) -> str:
        """
        Generate random hex string.

        Args:
            length: Number of bytes to generate (hex will be 2x length)

        Returns:
            Random hex string
        """
        return secrets.token_hex(length)

    @staticmethod
    def token_urlsafe(length: int = 32) -> str:
        """
        Generate URL-safe random string.

        Args:
            length: Number of bytes to generate

        Returns:
            URL-safe random string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def randint(min_val: int, max_val: int) -> int:
        """
        Generate random integer in range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            Random integer
        """
        return secrets.randbelow(max_val - min_val + 1) + min_val

    @staticmethod
    def choice(sequence: list) -> Any:
        """
        Choose random element from sequence.

        Args:
            sequence: Sequence to choose from

        Returns:
            Random element
        """
        return secrets.choice(sequence)


class SymmetricEncryption:
    """Symmetric encryption using Fernet (AES-128 in CBC mode with HMAC)."""
    
    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize symmetric encryption.

        Args:
            key: Encryption key (32 bytes) or None to generate new key
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptoError("cryptography library is required. Install with: pip install cryptography")
            
        if key is None:
            key = Fernet.generate_key()
        
        self.key = key
        self._fernet = Fernet(key)

    @classmethod
    def generate_key(cls) -> bytes:
        """Generate new encryption key."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptoError("cryptography library is required. Install with: pip install cryptography")
        return Fernet.generate_key()

    @classmethod
    def derive_key_from_password(cls, password: str, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: Password string
            salt: Salt bytes (16 bytes) or None to generate new salt

        Returns:
            Tuple of (key, salt)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptoError("cryptography library is required. Install with: pip install cryptography")
            
        if salt is None:
            salt = secrets.token_bytes(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = b64encode(kdf.derive(password.encode('utf-8')))
        return key, salt

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self._fernet.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted data
        """
        return self._fernet.decrypt(encrypted_data)

    def encrypt_string(self, text: str) -> str:
        """
        Encrypt string and return base64 encoded result.

        Args:
            text: Text to encrypt

        Returns:
            Base64 encoded encrypted text
        """
        encrypted = self.encrypt(text.encode('utf-8'))
        return b64encode(encrypted).decode('ascii')

    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt base64 encoded encrypted string.

        Args:
            encrypted_text: Base64 encoded encrypted text

        Returns:
            Decrypted text
        """
        encrypted_data = b64decode(encrypted_text.encode('ascii'))
        decrypted = self.decrypt(encrypted_data)
        return decrypted.decode('utf-8')


class AsymmetricEncryption:
    """Asymmetric (RSA) encryption for secure key exchange and digital signatures."""
    
    def __init__(self, private_key: Optional[bytes] = None, public_key: Optional[bytes] = None) -> None:
        """
        Initialize asymmetric encryption.

        Args:
            private_key: Private key in PEM format
            public_key: Public key in PEM format
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptoError("cryptography library is required. Install with: pip install cryptography")
            
        self.private_key = None
        self.public_key = None
        
        if private_key:
            self.private_key = serialization.load_pem_private_key(private_key, password=None)
            
        if public_key:
            self.public_key = serialization.load_pem_public_key(public_key)

    @classmethod
    def generate_key_pair(cls, key_size: int = 2048) -> tuple['AsymmetricEncryption', bytes, bytes]:
        """
        Generate new RSA key pair.

        Args:
            key_size: RSA key size in bits

        Returns:
            Tuple of (encryption instance, private_key_pem, public_key_pem)
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise CryptoError("cryptography library is required. Install with: pip install cryptography")
            
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        instance = cls(private_pem, public_pem)
        return instance, private_pem, public_pem

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data with public key.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data
        """
        if not self.public_key:
            raise CryptoError("Public key not available for encryption")
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data with private key.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted data
        """
        if not self.private_key:
            raise CryptoError("Private key not available for decryption")
            
        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def sign(self, data: Union[str, bytes]) -> bytes:
        """
        Sign data with private key.

        Args:
            data: Data to sign

        Returns:
            Digital signature
        """
        if not self.private_key:
            raise CryptoError("Private key not available for signing")
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        return self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self, data: Union[str, bytes], signature: bytes) -> bool:
        """
        Verify signature with public key.

        Args:
            data: Original data
            signature: Digital signature

        Returns:
            True if signature is valid
        """
        if not self.public_key:
            raise CryptoError("Public key not available for verification")
            
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False


class SecureStorage:
    """Secure storage for sensitive data with encryption and integrity protection."""
    
    def __init__(self, key: Optional[bytes] = None) -> None:
        """
        Initialize secure storage.

        Args:
            key: Encryption key or None to generate new key
        """
        self.encryption = SymmetricEncryption(key)
        self._storage: Dict[str, Dict[str, Any]] = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Store value securely.

        Args:
            key: Storage key
            value: Value to store
            metadata: Optional metadata
        """
        # Serialize value
        import json
        value_json = json.dumps(value)
        
        # Encrypt value
        encrypted_value = self.encryption.encrypt_string(value_json)
        
        # Store with metadata
        self._storage[key] = {
            'value': encrypted_value,
            'metadata': metadata or {},
            'timestamp': time.time(),
        }

    def retrieve(self, key: str) -> Any:
        """
        Retrieve value securely.

        Args:
            key: Storage key

        Returns:
            Stored value

        Raises:
            KeyError: If key not found
        """
        if key not in self._storage:
            raise KeyError(f"Key not found: {key}")
            
        entry = self._storage[key]
        encrypted_value = entry['value']
        
        # Decrypt value
        value_json = self.encryption.decrypt_string(encrypted_value)
        
        # Deserialize value
        import json
        return json.loads(value_json)

    def exists(self, key: str) -> bool:
        """Check if key exists in storage."""
        return key in self._storage

    def delete(self, key: str) -> bool:
        """
        Delete key from storage.

        Args:
            key: Storage key

        Returns:
            True if key was deleted, False if not found
        """
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def list_keys(self) -> list[str]:
        """Get list of all storage keys."""
        return list(self._storage.keys())

    def get_metadata(self, key: str) -> Dict[str, Any]:
        """
        Get metadata for a key.

        Args:
            key: Storage key

        Returns:
            Metadata dictionary

        Raises:
            KeyError: If key not found
        """
        if key not in self._storage:
            raise KeyError(f"Key not found: {key}")
            
        return self._storage[key]['metadata'].copy()

    def clear(self) -> None:
        """Clear all stored data."""
        self._storage.clear()


# Convenience functions
def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Hash password with salt.

    Args:
        password: Password to hash
        salt: Optional salt (will generate if not provided)

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = SecureRandom.token_hex(16)
    
    hashed = SecureHash.sha256(password + salt)
    return hashed, salt


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify password against hash.

    Args:
        password: Password to verify
        hashed_password: Stored password hash
        salt: Salt used for hashing

    Returns:
        True if password is correct
    """
    computed_hash = SecureHash.sha256(password + salt)
    return hmac.compare_digest(computed_hash, hashed_password)


def generate_api_key(length: int = 32) -> str:
    """Generate secure API key."""
    return SecureRandom.token_urlsafe(length)


def generate_session_token(length: int = 32) -> str:
    """Generate secure session token."""
    return SecureRandom.token_urlsafe(length)
