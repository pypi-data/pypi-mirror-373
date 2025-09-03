"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Comprehensive tests for cryptographic utilities.
"""

import pytest
import secrets
from pathlib import Path

from exonware.xsystem.security.crypto import (
    AsymmetricEncryption,
    CryptoError,
    SecureHash,
    SecureRandom,
    SecureStorage,
    SymmetricEncryption,
    generate_api_key,
    generate_session_token,
    hash_password,
    verify_password,
)


class TestSecureHash:
    """Test secure hashing utilities."""

    def test_sha256_string(self):
        """Test SHA-256 hashing of string."""
        data = "test data"
        hash1 = SecureHash.sha256(data)
        hash2 = SecureHash.sha256(data)
        
        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 64  # SHA-256 hex length
        assert all(c in '0123456789abcdef' for c in hash1)

    def test_sha256_bytes(self):
        """Test SHA-256 hashing of bytes."""
        data = b"test data"
        hash1 = SecureHash.sha256(data)
        hash2 = SecureHash.sha256("test data")
        
        assert hash1 == hash2  # Same result for string/bytes

    def test_sha512(self):
        """Test SHA-512 hashing."""
        data = "test data"
        hash_val = SecureHash.sha512(data)
        
        assert len(hash_val) == 128  # SHA-512 hex length
        assert all(c in '0123456789abcdef' for c in hash_val)

    def test_blake2b(self):
        """Test BLAKE2b hashing."""
        data = "test data"
        hash1 = SecureHash.blake2b(data)
        hash2 = SecureHash.blake2b(data, key=b"test_key")
        
        assert len(hash1) == 128  # BLAKE2b hex length
        assert hash1 != hash2  # Different with key

    def test_hmac_sha256(self):
        """Test HMAC-SHA256."""
        data = "test data"
        key = "test_key"
        hmac1 = SecureHash.hmac_sha256(data, key)
        hmac2 = SecureHash.hmac_sha256(data, key)
        
        assert hmac1 == hmac2  # Deterministic
        assert len(hmac1) == 64  # SHA-256 hex length

    def test_hmac_verify(self):
        """Test HMAC verification."""
        data = "test data"
        key = "test_key"
        hmac_val = SecureHash.hmac_sha256(data, key)
        
        assert SecureHash.verify_hmac(data, key, hmac_val)
        assert not SecureHash.verify_hmac(data, "wrong_key", hmac_val)
        assert not SecureHash.verify_hmac("wrong_data", key, hmac_val)


class TestSecureRandom:
    """Test secure random generation."""

    def test_token_bytes(self):
        """Test random bytes generation."""
        bytes1 = SecureRandom.token_bytes(32)
        bytes2 = SecureRandom.token_bytes(32)
        
        assert len(bytes1) == 32
        assert len(bytes2) == 32
        assert bytes1 != bytes2  # Should be different

    def test_token_hex(self):
        """Test random hex generation."""
        hex1 = SecureRandom.token_hex(16)
        hex2 = SecureRandom.token_hex(16)
        
        assert len(hex1) == 32  # 16 bytes = 32 hex chars
        assert len(hex2) == 32
        assert hex1 != hex2
        assert all(c in '0123456789abcdef' for c in hex1)

    def test_token_urlsafe(self):
        """Test URL-safe token generation."""
        token1 = SecureRandom.token_urlsafe(32)
        token2 = SecureRandom.token_urlsafe(32)
        
        assert token1 != token2
        # URL-safe characters
        assert all(c.isalnum() or c in '-_' for c in token1)

    def test_randint(self):
        """Test secure random integer."""
        for _ in range(100):
            val = SecureRandom.randint(1, 10)
            assert 1 <= val <= 10

    def test_choice(self):
        """Test secure random choice."""
        options = ['a', 'b', 'c', 'd', 'e']
        choices = [SecureRandom.choice(options) for _ in range(100)]
        
        # Should see variety
        assert len(set(choices)) > 1
        assert all(choice in options for choice in choices)


@pytest.mark.skipif(
    not hasattr(SymmetricEncryption, '_fernet'),
    reason="cryptography library not available"
)
class TestSymmetricEncryption:
    """Test symmetric encryption."""

    def test_key_generation(self):
        """Test encryption key generation."""
        key1 = SymmetricEncryption.generate_key()
        key2 = SymmetricEncryption.generate_key()
        
        assert len(key1) == 44  # Fernet key length (base64)
        assert key1 != key2

    def test_password_key_derivation(self):
        """Test key derivation from password."""
        password = "test_password"
        key1, salt1 = SymmetricEncryption.derive_key_from_password(password)
        key2, salt2 = SymmetricEncryption.derive_key_from_password(password, salt1)
        
        assert key1 == key2  # Same password + salt = same key
        assert salt1 == salt2

    def test_encrypt_decrypt_bytes(self):
        """Test bytes encryption/decryption."""
        enc = SymmetricEncryption()
        data = b"sensitive data"
        
        encrypted = enc.encrypt(data)
        decrypted = enc.decrypt(encrypted)
        
        assert decrypted == data
        assert encrypted != data

    def test_encrypt_decrypt_string(self):
        """Test string encryption/decryption."""
        enc = SymmetricEncryption()
        text = "sensitive text"
        
        encrypted = enc.encrypt_string(text)
        decrypted = enc.decrypt_string(encrypted)
        
        assert decrypted == text
        assert encrypted != text

    def test_encryption_different_keys(self):
        """Test encryption with different keys."""
        enc1 = SymmetricEncryption()
        enc2 = SymmetricEncryption()
        data = "test data"
        
        encrypted1 = enc1.encrypt_string(data)
        encrypted2 = enc2.encrypt_string(data)
        
        assert encrypted1 != encrypted2  # Different keys
        
        with pytest.raises(Exception):  # Should fail with wrong key
            enc1.decrypt_string(encrypted2)


@pytest.mark.skipif(
    not hasattr(AsymmetricEncryption, 'private_key'),
    reason="cryptography library not available"
)
class TestAsymmetricEncryption:
    """Test asymmetric encryption."""

    def test_key_pair_generation(self):
        """Test RSA key pair generation."""
        enc, private_pem, public_pem = AsymmetricEncryption.generate_key_pair()
        
        assert b'BEGIN PRIVATE KEY' in private_pem
        assert b'BEGIN PUBLIC KEY' in public_pem
        assert enc.private_key is not None
        assert enc.public_key is not None

    def test_encrypt_decrypt(self):
        """Test public key encryption and private key decryption."""
        enc, _, _ = AsymmetricEncryption.generate_key_pair()
        data = "sensitive data"
        
        encrypted = enc.encrypt(data)
        decrypted = enc.decrypt(encrypted)
        
        assert decrypted.decode('utf-8') == data
        assert encrypted != data.encode('utf-8')

    def test_sign_verify(self):
        """Test digital signature and verification."""
        enc, _, _ = AsymmetricEncryption.generate_key_pair()
        data = "data to sign"
        
        signature = enc.sign(data)
        assert enc.verify(data, signature)
        assert not enc.verify("tampered data", signature)

    def test_encryption_with_separate_keys(self):
        """Test encryption with public key only."""
        _, private_pem, public_pem = AsymmetricEncryption.generate_key_pair()
        
        # Encrypt with public key only
        enc_pub = AsymmetricEncryption(public_key=public_pem)
        data = "test data"
        encrypted = enc_pub.encrypt(data)
        
        # Decrypt with private key only
        enc_priv = AsymmetricEncryption(private_key=private_pem)
        decrypted = enc_priv.decrypt(encrypted)
        
        assert decrypted.decode('utf-8') == data


class TestSecureStorage:
    """Test secure storage."""

    def test_store_retrieve(self):
        """Test storing and retrieving data."""
        storage = SecureStorage()
        key = "test_key"
        value = {"sensitive": "data", "number": 42}
        
        storage.store(key, value)
        retrieved = storage.retrieve(key)
        
        assert retrieved == value

    def test_store_with_metadata(self):
        """Test storing with metadata."""
        storage = SecureStorage()
        key = "test_key"
        value = "test value"
        metadata = {"type": "sensitive", "level": "high"}
        
        storage.store(key, value, metadata)
        retrieved_metadata = storage.get_metadata(key)
        
        assert retrieved_metadata == metadata

    def test_key_operations(self):
        """Test key existence and deletion."""
        storage = SecureStorage()
        key = "test_key"
        value = "test value"
        
        assert not storage.exists(key)
        
        storage.store(key, value)
        assert storage.exists(key)
        assert key in storage.list_keys()
        
        assert storage.delete(key)
        assert not storage.exists(key)
        assert not storage.delete(key)  # Already deleted

    def test_clear_storage(self):
        """Test clearing all storage."""
        storage = SecureStorage()
        
        storage.store("key1", "value1")
        storage.store("key2", "value2")
        assert len(storage.list_keys()) == 2
        
        storage.clear()
        assert len(storage.list_keys()) == 0

    def test_key_not_found(self):
        """Test retrieving non-existent key."""
        storage = SecureStorage()
        
        with pytest.raises(KeyError):
            storage.retrieve("non_existent")
            
        with pytest.raises(KeyError):
            storage.get_metadata("non_existent")


class TestPasswordUtilities:
    """Test password hashing utilities."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password"
        hashed, salt = hash_password(password)
        
        assert len(hashed) == 64  # SHA-256 hex
        assert len(salt) == 32  # 16 bytes hex
        assert hashed != password

    def test_verify_password(self):
        """Test password verification."""
        password = "test_password"
        hashed, salt = hash_password(password)
        
        assert verify_password(password, hashed, salt)
        assert not verify_password("wrong_password", hashed, salt)

    def test_same_password_different_hashes(self):
        """Test same password produces different hashes with different salts."""
        password = "test_password"
        hashed1, salt1 = hash_password(password)
        hashed2, salt2 = hash_password(password)
        
        assert hashed1 != hashed2  # Different salts
        assert salt1 != salt2


class TestTokenGeneration:
    """Test API key and session token generation."""

    def test_api_key_generation(self):
        """Test API key generation."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert key1 != key2
        assert len(key1) > 30  # Should be reasonably long

    def test_session_token_generation(self):
        """Test session token generation."""
        token1 = generate_session_token()
        token2 = generate_session_token()
        
        assert token1 != token2
        assert len(token1) > 30  # Should be reasonably long

    def test_custom_length_tokens(self):
        """Test custom length token generation."""
        short_key = generate_api_key(16)
        long_key = generate_api_key(64)
        
        assert len(short_key) < len(long_key)


@pytest.mark.xsystem_unit
class TestCryptoErrorHandling:
    """Test error handling in crypto operations."""

    def test_crypto_error_instantiation(self):
        """Test CryptoError exception."""
        error = CryptoError("test error")
        assert str(error) == "test error"

    def test_invalid_encryption_key(self):
        """Test invalid encryption key handling."""
        with pytest.raises(Exception):  # Fernet will raise on invalid key
            SymmetricEncryption(b"invalid_key")

    def test_decrypt_with_wrong_data(self):
        """Test decryption with invalid data."""
        enc = SymmetricEncryption()
        
        with pytest.raises(Exception):
            enc.decrypt(b"invalid_encrypted_data")
            
        with pytest.raises(Exception):
            enc.decrypt_string("invalid_encrypted_string")


@pytest.mark.xsystem_unit 
class TestCryptoSecurityProperties:
    """Test security properties of crypto operations."""

    def test_encryption_randomness(self):
        """Test that encryption produces random-looking output."""
        enc = SymmetricEncryption()
        data = "test data"
        
        # Encrypt same data multiple times
        encrypted_values = [enc.encrypt_string(data) for _ in range(10)]
        
        # All should be different (due to random IV)
        assert len(set(encrypted_values)) == 10

    def test_hash_consistency(self):
        """Test that hashes are consistent."""
        data = "test data"
        
        hashes = [SecureHash.sha256(data) for _ in range(10)]
        
        # All should be the same
        assert len(set(hashes)) == 1

    def test_random_unpredictability(self):
        """Test that random generation is unpredictable."""
        # Generate many random values
        values = [SecureRandom.token_hex(16) for _ in range(100)]
        
        # Should be all unique
        assert len(set(values)) == 100
        
        # Should not have obvious patterns
        assert not any(val == val[::-1] for val in values)  # No palindromes
        assert not any('0000' in val or 'aaaa' in val for val in values)  # No obvious repeats
