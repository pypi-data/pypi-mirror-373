import ssl
import socket
import hashlib
import hmac
import time
import threading
import json
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict, deque
import secrets
import logging

try:
    import cryptography
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


class SecurityLevel(Enum):
    """Security levels for different operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationType(Enum):
    """Types of input validation."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    EMAIL = "email"
    URL = "url"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"


@dataclass
class SecurityConfig:
    """Configuration for security features."""
    # SSL/TLS settings
    enable_ssl: bool = False
    ssl_cert_file: str = ""
    ssl_key_file: str = ""
    ssl_ca_file: str = ""
    ssl_verify_mode: int = ssl.CERT_REQUIRED
    ssl_check_hostname: bool = True
    ssl_ciphers: str = "HIGH:!aNULL:!MD5:!RC4"
    ssl_protocol: int = ssl.PROTOCOL_TLSv1_2
    
    # Message signing settings
    enable_message_signing: bool = False
    signing_algorithm: str = "HMAC-SHA256"
    signing_key: str = ""
    auto_generate_signing_key: bool = True
    verify_signatures: bool = True
    
    # Input validation settings
    enable_input_validation: bool = True
    strict_validation: bool = False
    max_message_size: int = 1024 * 1024  # 1MB
    allowed_characters: str = r'[\w\s\-_.,!?@#$%^&*()+=<>\[\]{}|\\/:;"\'`~]'
    block_sql_injection: bool = True
    block_xss: bool = True
    
    # Rate limiting settings
    enable_rate_limiting: bool = True
    rate_limit_window: float = 60.0  # 1 minute
    rate_limit_max_requests: int = 100
    rate_limit_by_ip: bool = True
    rate_limit_by_user: bool = False
    rate_limit_strategy: str = "sliding_window"  # fixed_window, sliding_window
    
    # Authentication settings
    enable_authentication: bool = False
    auth_timeout: float = 300.0  # 5 minutes
    max_auth_attempts: int = 3
    password_min_length: int = 8
    require_special_chars: bool = True
    
    # Logging settings
    enable_security_logging: bool = True
    log_suspicious_activity: bool = True
    log_failed_auth: bool = True
    log_rate_limit_violations: bool = True


class SSLSocketWrapper:
    """Wrapper for SSL/TLS socket operations."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.ssl_context = None
        self._initialize_ssl_context()
    
    def _initialize_ssl_context(self):
        """Initialize SSL context."""
        if not self.config.enable_ssl:
            return
        
        try:
            self.ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cafile=self.config.ssl_ca_file if self.config.ssl_ca_file else None
            )
            
            # Set SSL options
            self.ssl_context.verify_mode = self.config.ssl_verify_mode
            self.ssl_context.check_hostname = self.config.ssl_check_hostname
            self.ssl_context.set_ciphers(self.config.ssl_ciphers)
            self.ssl_context.minimum_version = self.config.ssl_protocol
            
            # Load certificate and key for server
            if self.config.ssl_cert_file and self.config.ssl_key_file:
                self.ssl_context.load_cert_chain(
                    certfile=self.config.ssl_cert_file,
                    keyfile=self.config.ssl_key_file
                )
            
        except Exception as e:
            logging.error(f"Failed to initialize SSL context: {e}")
            self.config.enable_ssl = False
    
    def wrap_socket(self, sock: socket.socket, server_side: bool = False) -> socket.socket:
        """Wrap a socket with SSL/TLS."""
        if not self.config.enable_ssl or not self.ssl_context:
            return sock
        
        try:
            return self.ssl_context.wrap_socket(
                sock,
                server_side=server_side,
                do_handshake_on_connect=True
            )
        except Exception as e:
            logging.error(f"Failed to wrap socket with SSL: {e}")
            return sock
    
    def get_ssl_info(self, sock: socket.socket) -> Dict:
        """Get SSL information from socket."""
        if not hasattr(sock, 'version'):
            return {}
        
        try:
            return {
                'version': sock.version(),
                'cipher': sock.cipher(),
                'compression': sock.compression(),
                'server_hostname': getattr(sock, 'server_hostname', None)
            }
        except Exception:
            return {}


class MessageSigner:
    """Handles message signing and verification."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.signing_key = self._get_signing_key()
        self.signature_cache = {}
        self.cache_size = 1000
        self.cache_lock = threading.Lock()
    
    def _get_signing_key(self) -> bytes:
        """Get or generate signing key."""
        if self.config.signing_key:
            return self.config.signing_key.encode('utf-8')
        
        if self.config.auto_generate_signing_key:
            # Generate a secure random key
            return secrets.token_bytes(32)
        
        raise ValueError("No signing key provided and auto-generation is disabled")
    
    def sign_message(self, message: Union[str, bytes, dict]) -> str:
        """Sign a message and return the signature."""
        if not self.config.enable_message_signing:
            return ""
        
        # Convert message to bytes
        if isinstance(message, dict):
            message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
        elif isinstance(message, str):
            message_bytes = message.encode('utf-8')
        elif isinstance(message, bytes):
            message_bytes = message
        else:
            message_bytes = str(message).encode('utf-8')
        
        # Create signature
        if self.config.signing_algorithm == "HMAC-SHA256":
            signature = hmac.new(
                self.signing_key,
                message_bytes,
                hashlib.sha256
            ).hexdigest()
        elif self.config.signing_algorithm == "HMAC-SHA512":
            signature = hmac.new(
                self.signing_key,
                message_bytes,
                hashlib.sha512
            ).hexdigest()
        else:
            raise ValueError(f"Unsupported signing algorithm: {self.config.signing_algorithm}")
        
        # Cache signature
        self._cache_signature(message_bytes, signature)
        
        return signature
    
    def verify_signature(self, message: Union[str, bytes, dict], signature: str) -> bool:
        """Verify a message signature."""
        if not self.config.enable_message_signing or not self.config.verify_signatures:
            return True
        
        # Check cache first
        if isinstance(message, dict):
            message_bytes = json.dumps(message, sort_keys=True).encode('utf-8')
        elif isinstance(message, str):
            message_bytes = message.encode('utf-8')
        elif isinstance(message, bytes):
            message_bytes = message
        else:
            message_bytes = str(message).encode('utf-8')
        
        cached_signature = self._get_cached_signature(message_bytes)
        if cached_signature and cached_signature == signature:
            return True
        
        # Verify signature
        expected_signature = self.sign_message(message)
        return hmac.compare_digest(signature, expected_signature)
    
    def _cache_signature(self, message_bytes: bytes, signature: str):
        """Cache a signature."""
        with self.cache_lock:
            if len(self.signature_cache) >= self.cache_size:
                # Remove oldest entry
                self.signature_cache.pop(next(iter(self.signature_cache)))
            
            message_hash = hashlib.sha256(message_bytes).hexdigest()
            self.signature_cache[message_hash] = signature
    
    def _get_cached_signature(self, message_bytes: bytes) -> Optional[str]:
        """Get cached signature."""
        with self.cache_lock:
            message_hash = hashlib.sha256(message_bytes).hexdigest()
            return self.signature_cache.get(message_hash)


class InputValidator:
    """Handles input validation and sanitization."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.validation_patterns = self._initialize_patterns()
        self.sql_patterns = self._initialize_sql_patterns()
        self.xss_patterns = self._initialize_xss_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """Initialize validation patterns."""
        return {
            ValidationType.STRING: re.compile(r'^[\w\s\-_.,!?@#$%^&*()+=<>\[\]{}|\\/:;"\'`~]*$'),
            ValidationType.INTEGER: re.compile(r'^-?\d+$'),
            ValidationType.FLOAT: re.compile(r'^-?\d+\.?\d*$'),
            ValidationType.BOOLEAN: re.compile(r'^(true|false|True|False|1|0)$'),
            ValidationType.EMAIL: re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            ValidationType.URL: re.compile(r'^https?://[^\s/$.?#].[^\s]*$'),
            ValidationType.IP_ADDRESS: re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        }
    
    def _initialize_sql_patterns(self) -> List[re.Pattern]:
        """Initialize SQL injection patterns."""
        return [
            re.compile(r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|OR|AND)\b)', re.IGNORECASE),
            re.compile(r'(\b(WHERE|FROM|INTO|VALUES|SET|JOIN|GROUP BY|ORDER BY)\b)', re.IGNORECASE),
            re.compile(r'(\b(script|javascript|vbscript|onload|onerror|onclick)\b)', re.IGNORECASE),
            re.compile(r'(\b(union|select|insert|update|delete|drop|create|alter|exec)\b)', re.IGNORECASE)
        ]
    
    def _initialize_xss_patterns(self) -> List[re.Pattern]:
        """Initialize XSS patterns."""
        return [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
            re.compile(r'<embed[^>]*>', re.IGNORECASE),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'vbscript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE)
        ]
    
    def validate_input(self, data: Any, validation_type: ValidationType = ValidationType.STRING) -> bool:
        """Validate input data."""
        if not self.config.enable_input_validation:
            return True
        
        if data is None:
            return True
        
        # Convert to string for validation
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        # Check message size
        if len(data_str) > self.config.max_message_size:
            return False
        
        # Check for SQL injection
        if self.config.block_sql_injection:
            for pattern in self.sql_patterns:
                if pattern.search(data_str):
                    return False
        
        # Check for XSS
        if self.config.block_xss:
            for pattern in self.xss_patterns:
                if pattern.search(data_str):
                    return False
        
        # Type-specific validation
        if validation_type in self.validation_patterns:
            pattern = self.validation_patterns[validation_type]
            if not pattern.match(data_str):
                return False
        
        return True
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data."""
        if not self.config.enable_input_validation:
            return data
        
        if isinstance(data, str):
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', data)
            return sanitized
        
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        
        elif isinstance(data, list):
            return [self.sanitize_input(item) for item in data]
        
        return data
    
    def validate_json(self, json_str: str) -> bool:
        """Validate JSON string."""
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, TypeError):
            return False


class RateLimiter:
    """Handles rate limiting for connections and requests."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rate_limits = defaultdict(lambda: deque())
        self.lock = threading.Lock()
        self.cleanup_timer = None
        self._start_cleanup_timer()
    
    def _start_cleanup_timer(self):
        """Start cleanup timer for expired rate limit entries."""
        def cleanup():
            while True:
                time.sleep(self.config.rate_limit_window)
                self._cleanup_expired_entries()
        
        self.cleanup_timer = threading.Thread(target=cleanup, daemon=True)
        self.cleanup_timer.start()
    
    def _cleanup_expired_entries(self):
        """Clean up expired rate limit entries."""
        current_time = time.time()
        with self.lock:
            for key in list(self.rate_limits.keys()):
                # Remove expired entries
                while self.rate_limits[key] and current_time - self.rate_limits[key][0] > self.config.rate_limit_window:
                    self.rate_limits[key].popleft()
                
                # Remove empty entries
                if not self.rate_limits[key]:
                    del self.rate_limits[key]
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if a request is allowed based on rate limiting."""
        if not self.config.enable_rate_limiting:
            return True
        
        current_time = time.time()
        
        with self.lock:
            # Get current requests for this identifier
            requests = self.rate_limits[identifier]
            
            # Remove expired entries
            while requests and current_time - requests[0] > self.config.rate_limit_window:
                requests.popleft()
            
            # Check if limit exceeded
            if len(requests) >= self.config.rate_limit_max_requests:
                return False
            
            # Add current request
            requests.append(current_time)
            return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for an identifier."""
        if not self.config.enable_rate_limiting:
            return self.config.rate_limit_max_requests
        
        current_time = time.time()
        
        with self.lock:
            requests = self.rate_limits[identifier]
            
            # Remove expired entries
            while requests and current_time - requests[0] > self.config.rate_limit_window:
                requests.popleft()
            
            return max(0, self.config.rate_limit_max_requests - len(requests))
    
    def reset_limits(self, identifier: str):
        """Reset rate limits for an identifier."""
        with self.lock:
            if identifier in self.rate_limits:
                del self.rate_limits[identifier]
    
    def get_stats(self) -> Dict:
        """Get rate limiting statistics."""
        with self.lock:
            return {
                'active_identifiers': len(self.rate_limits),
                'total_requests': sum(len(requests) for requests in self.rate_limits.values()),
                'rate_limit_window': self.config.rate_limit_window,
                'max_requests': self.config.rate_limit_max_requests
            }


class Authenticator:
    """Handles authentication and authorization."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.users = {}
        self.sessions = {}
        self.failed_attempts = defaultdict(int)
        self.lock = threading.Lock()
    
    def add_user(self, username: str, password: str, permissions: List[str] = None) -> bool:
        """Add a new user."""
        if not self.config.enable_authentication:
            return True
        
        if not self._validate_password(password):
            return False
        
        with self.lock:
            if username in self.users:
                return False
            
            # Hash password
            if BCRYPT_AVAILABLE:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            else:
                # Fallback to simple hash
                hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            
            self.users[username] = {
                'password': hashed_password,
                'permissions': permissions or [],
                'created': time.time(),
                'last_login': None
            }
            
            return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        if not self.config.enable_authentication:
            return True
        
        with self.lock:
            # Check failed attempts
            if self.failed_attempts[username] >= self.config.max_auth_attempts:
                return False
            
            if username not in self.users:
                self.failed_attempts[username] += 1
                return False
            
            user = self.users[username]
            
            # Verify password
            if BCRYPT_AVAILABLE:
                is_valid = bcrypt.checkpw(password.encode('utf-8'), user['password'])
            else:
                # Fallback to simple hash
                expected_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                is_valid = hmac.compare_digest(user['password'], expected_hash)
            
            if is_valid:
                # Reset failed attempts
                self.failed_attempts[username] = 0
                user['last_login'] = time.time()
                return True
            else:
                self.failed_attempts[username] += 1
                return False
    
    def create_session(self, username: str) -> str:
        """Create a session for a user."""
        if not self.config.enable_authentication:
            return ""
        
        session_id = secrets.token_urlsafe(32)
        
        with self.lock:
            self.sessions[session_id] = {
                'username': username,
                'created': time.time(),
                'permissions': self.users.get(username, {}).get('permissions', [])
            }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate a session."""
        if not self.config.enable_authentication:
            return {}
        
        with self.lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            
            # Check if session expired
            if time.time() - session['created'] > self.config.auth_timeout:
                del self.sessions[session_id]
                return None
            
            return session
    
    def has_permission(self, session_id: str, permission: str) -> bool:
        """Check if a session has a specific permission."""
        session = self.validate_session(session_id)
        if not session:
            return False
        
        return permission in session.get('permissions', [])
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < self.config.password_min_length:
            return False
        
        if self.config.require_special_chars:
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                return False
        
        return True
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        current_time = time.time()
        
        with self.lock:
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if current_time - session['created'] > self.config.auth_timeout
            ]
            
            for session_id in expired_sessions:
                del self.sessions[session_id]


class SecurityLogger:
    """Handles security-related logging."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = logging.getLogger('sockstream.security')
        self.logger.setLevel(logging.INFO)
        
        # Add handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_suspicious_activity(self, activity: str, details: Dict = None):
        """Log suspicious activity."""
        if not self.config.enable_security_logging or not self.config.log_suspicious_activity:
            return
        
        message = f"Suspicious activity detected: {activity}"
        if details:
            message += f" - Details: {details}"
        
        self.logger.warning(message)
    
    def log_failed_auth(self, username: str, ip_address: str = None):
        """Log failed authentication attempt."""
        if not self.config.enable_security_logging or not self.config.log_failed_auth:
            return
        
        message = f"Failed authentication attempt for user: {username}"
        if ip_address:
            message += f" from IP: {ip_address}"
        
        self.logger.warning(message)
    
    def log_rate_limit_violation(self, identifier: str, ip_address: str = None):
        """Log rate limit violation."""
        if not self.config.enable_security_logging or not self.config.log_rate_limit_violations:
            return
        
        message = f"Rate limit violation for: {identifier}"
        if ip_address:
            message += f" from IP: {ip_address}"
        
        self.logger.warning(message)
    
    def log_security_event(self, event: str, level: str = "INFO", details: Dict = None):
        """Log general security event."""
        if not self.config.enable_security_logging:
            return
        
        message = f"Security event: {event}"
        if details:
            message += f" - Details: {details}"
        
        if level.upper() == "WARNING":
            self.logger.warning(message)
        elif level.upper() == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)


class SecurityHandler:
    """Main security handler that coordinates all security features."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.ssl_wrapper = SSLSocketWrapper(config)
        self.message_signer = MessageSigner(config)
        self.input_validator = InputValidator(config)
        self.rate_limiter = RateLimiter(config)
        self.authenticator = Authenticator(config)
        self.logger = SecurityLogger(config)
    
    def wrap_socket_ssl(self, sock: socket.socket, server_side: bool = False) -> socket.socket:
        """Wrap a socket with SSL/TLS."""
        return self.ssl_wrapper.wrap_socket(sock, server_side)
    
    def get_ssl_info(self, sock: socket.socket) -> Dict:
        """Get SSL information from socket."""
        return self.ssl_wrapper.get_ssl_info(sock)
    
    def sign_message(self, message: Union[str, bytes, dict]) -> str:
        """Sign a message."""
        return self.message_signer.sign_message(message)
    
    def verify_message(self, message: Union[str, bytes, dict], signature: str) -> bool:
        """Verify a message signature."""
        return self.message_signer.verify_signature(message, signature)
    
    def validate_input(self, data: Any, validation_type: ValidationType = ValidationType.STRING) -> bool:
        """Validate input data."""
        return self.input_validator.validate_input(data, validation_type)
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data."""
        return self.input_validator.sanitize_input(data)
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if an identifier is rate limited."""
        return not self.rate_limiter.is_allowed(identifier)
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for an identifier."""
        return self.rate_limiter.get_remaining_requests(identifier)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        return self.authenticator.authenticate(username, password)
    
    def create_user_session(self, username: str) -> str:
        """Create a session for a user."""
        return self.authenticator.create_session(username)
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate a session."""
        return self.authenticator.validate_session(session_id)
    
    def has_permission(self, session_id: str, permission: str) -> bool:
        """Check if a session has a specific permission."""
        return self.authenticator.has_permission(session_id, permission)
    
    def add_user(self, username: str, password: str, permissions: List[str] = None) -> bool:
        """Add a new user."""
        return self.authenticator.add_user(username, password, permissions)
    
    def log_security_event(self, event: str, level: str = "INFO", details: Dict = None):
        """Log a security event."""
        self.logger.log_security_event(event, level, details)
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        return {
            'ssl_enabled': self.config.enable_ssl,
            'message_signing_enabled': self.config.enable_message_signing,
            'input_validation_enabled': self.config.enable_input_validation,
            'rate_limiting_enabled': self.config.enable_rate_limiting,
            'authentication_enabled': self.config.enable_authentication,
            'rate_limiting_stats': self.rate_limiter.get_stats(),
            'active_sessions': len(self.authenticator.sessions),
            'total_users': len(self.authenticator.users)
        }
    
    def cleanup(self):
        """Clean up security resources."""
        self.authenticator.cleanup_expired_sessions()
        self.rate_limiter._cleanup_expired_entries()
