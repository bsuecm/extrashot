"""
Authentication Service - Manages user authentication and credentials
"""
import os
import json
import hashlib
import secrets
from typing import Optional, Dict
from threading import Lock
import logging

logger = logging.getLogger(__name__)

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'


class AuthService:
    """Simple session-based authentication service"""

    def __init__(self, credentials_file: str):
        self.credentials_file = credentials_file
        self.lock = Lock()
        self.sessions: Dict[str, str] = {}  # token -> username
        self._ensure_credentials_file()

    def _ensure_credentials_file(self):
        """Create credentials file with defaults if it doesn't exist"""
        if not os.path.exists(self.credentials_file):
            self._save_credentials({
                'username': DEFAULT_USERNAME,
                'password_hash': self._hash_password(DEFAULT_PASSWORD)
            })
            logger.info(f"Created default credentials file: {self.credentials_file}")

    def _hash_password(self, password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _load_credentials(self) -> Dict:
        """Load credentials from file"""
        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return {
                'username': DEFAULT_USERNAME,
                'password_hash': self._hash_password(DEFAULT_PASSWORD)
            }

    def _save_credentials(self, credentials: Dict):
        """Save credentials to file"""
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2)

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """
        Authenticate user and return session token if successful
        Returns None if authentication fails
        """
        with self.lock:
            credentials = self._load_credentials()
            password_hash = self._hash_password(password)

            if username == credentials['username'] and password_hash == credentials['password_hash']:
                # Generate session token
                token = secrets.token_hex(32)
                self.sessions[token] = username
                logger.info(f"User '{username}' authenticated successfully")
                return token

            logger.warning(f"Failed authentication attempt for user '{username}'")
            return None

    def validate_session(self, token: str) -> Optional[str]:
        """
        Validate session token and return username if valid
        Returns None if token is invalid
        """
        with self.lock:
            return self.sessions.get(token)

    def logout(self, token: str) -> bool:
        """Invalidate session token"""
        with self.lock:
            if token in self.sessions:
                del self.sessions[token]
                return True
            return False

    def change_credentials(self, token: str, new_username: str, new_password: str,
                          current_password: str) -> Dict:
        """
        Change username and/or password
        Requires current password for verification
        """
        with self.lock:
            # Verify session
            if token not in self.sessions:
                return {'success': False, 'error': 'Invalid session'}

            # Verify current password
            credentials = self._load_credentials()
            if self._hash_password(current_password) != credentials['password_hash']:
                return {'success': False, 'error': 'Current password is incorrect'}

            # Update credentials
            new_credentials = {
                'username': new_username or credentials['username'],
                'password_hash': self._hash_password(new_password) if new_password else credentials['password_hash']
            }
            self._save_credentials(new_credentials)

            # Update session with new username
            self.sessions[token] = new_credentials['username']

            logger.info(f"Credentials updated for user '{new_credentials['username']}'")
            return {'success': True}

    def get_username(self, token: str) -> Optional[str]:
        """Get username for a session token"""
        with self.lock:
            return self.sessions.get(token)
