from cryptography.fernet import Fernet
import base64
import hashlib
from typing import Optional
from abs_utils.logger import setup_logger


logger = setup_logger(__name__)

class Encryption:
    def __init__(self, key: Optional[str] = None):
        self.key = key

    # Encryption key management
    def get_encryption_key(self):
        """
        Get encryption key from environment variable or generate one if not exists
        
        This should ideally be set in environment variables and consistent across restarts
        Returns:
            A valid Fernet key (32 url-safe base64-encoded bytes)
        """

        if not self.key:
            # For demo only - in production, you should set a permanent key
            # and store it securely in environment variables or a secret manager
            self.key = Fernet.generate_key().decode()
            logger.warning(f"Generated temporary encryption key: {self.key}")
            logger.warning("Set this in your environment as TOKEN_ENCRYPTION_KEY")
            return self.key.encode() if isinstance(self.key, str) else self.key
        
        # If key is not in valid Fernet format, convert it to a valid key
        try:
            # Try to use the key as is - if it's already a valid Fernet key
            if isinstance(self.key, str):
                self.key = self.key.encode()
                
            # Test if it's a valid key
            Fernet(self.key)
            return self.key
        except Exception:
            # Not a valid Fernet key - convert to a valid one
            # Use SHA-256 to get a consistent length, then encode in base64
            if isinstance(self.key, str):
                self.key = self.key.encode()
                
            hashed_key = hashlib.sha256(self.key).digest()
            encoded_key = base64.urlsafe_b64encode(hashed_key)
            
            logger.warning("Converted invalid encryption key to valid Fernet format")
            return encoded_key

    def encrypt_token(self, token: str) -> str:
        """
        Encrypt a token string using Fernet symmetric encryption
        
        Args:
            token: The raw token string to encrypt
            
        Returns:
            The encrypted token as a base64 string
        """
        if not token:
            return token
            
        # Get the encryption key
        key = self.get_encryption_key()
        
        # Create a Fernet cipher
        cipher = Fernet(key)
        
        # Encrypt the token (which must be bytes)
        encrypted_token = cipher.encrypt(token.encode())
        
        # Return as a string for storage
        return encrypted_token.decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt a token string that was encrypted with Fernet
        
        Args:
            encrypted_token: The encrypted token as a base64 string
            
        Returns:
            The original decrypted token string
        """
        if not encrypted_token:
            return encrypted_token
            
        # Get the encryption key
        key = self.get_encryption_key()
        
        # Create a Fernet cipher
        cipher = Fernet(key)
        
        # Decrypt the token (convert string to bytes first)
        decrypted_token = cipher.decrypt(encrypted_token.encode())
        
        # Return as a string
        return decrypted_token.decode()
