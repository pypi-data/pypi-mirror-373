from datetime import datetime, timedelta
import uuid
import bcrypt
import secrets
import string
from abc import ABC, abstractmethod

def generate_random_string(length, alphabet=string.ascii_letters + string.digits):
    """Generate a random string of specified length using the given alphabet."""
    return ''.join(secrets.choice(alphabet) for _ in range(length))

class IDGenerator(ABC):
    @abstractmethod
    def generate(self):
        pass

class UUIDGenerator(IDGenerator):
    def generate(self):
        return str(uuid.uuid4())

class IntegerGenerator(IDGenerator):
    def generate(self):
        return None  # Let the database handle ID generation with SERIAL

class User:
    def __init__(self, username, email, real_name, roles=None, id_generator=None):
        self.id = id_generator.generate() if id_generator else str(uuid.uuid4())
        if self.id is None:  # Let database handle ID generation
            self.id = None
        self.username = username
        self.email = email
        self.real_name = real_name
        self.roles = roles or []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

class Role:
    def __init__(self, name, description=None, id_generator=None):
        self.id = id_generator.generate() if id_generator else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()

class ApiToken:
    def __init__(self, user_id, name, expires_in_days=None):
        self.id = generate_random_string(8)  # 8 character ID
        self.user_id = user_id
        self.name = name
        self.nonce = generate_random_string(32)  # 32 character nonce
        self.token = self._hash_nonce(self.nonce)  # Hash the nonce
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days) if expires_in_days else None
        self.last_used_at = None

    def _hash_nonce(self, nonce):
        """Hash the nonce using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(nonce.encode('utf-8'), salt).decode('utf-8')

    def get_full_token(self):
        """Get the full token string in the format api_IDNONCE."""
        return f"api_{self.id}{self.nonce}"

    @staticmethod
    def parse_token(token_string):
        """Parse a token string into its components."""
        if not token_string.startswith('api_'):
            raise ValueError('Invalid token format')
        
        token_string = token_string[4:]  # Remove 'api_' prefix
        if len(token_string) != 40:  # 8 (id) + 32 (nonce)
            raise ValueError('Invalid token length')
        
        return {
            'id': token_string[:8],
            'nonce': token_string[8:]
        }

    @staticmethod
    def parse_token_id(token_string):
        if len(token_string) == 8:
            return token_string
        if not token_string.startswith('api_'):
            raise ValueError('Invalid token format')
        return token_string[4:][:8]

    def verify_token(self, token_string):
        """Verify if a token string matches this token."""
        try:
            parsed = self.parse_token(token_string)
            if parsed['id'] != self.id:
                return False
            return bcrypt.checkpw(parsed['nonce'].encode('utf-8'), self.token.encode('utf-8'))
        except ValueError:
            return False 