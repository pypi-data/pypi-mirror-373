"""
SockStream Package

A Python package for handling socket communications with emit functionality.
"""

from .client_enhanced import EnhancedClient, ClientConfig, ConnectionState
from .server_enhanced import EnhancedServer, ServerConfig, ServerState
from .message_handler import MessageHandler, MessageConfig, Message, MessageType, CompressionType
from .protocol_handler import ProtocolHandler, ProtocolConfig, ProtocolType, MessageFormat, FramingType
from .performance_handler import (
    PerformanceHandler, PerformanceConfig, MultiplexingStrategy, BufferStrategy,
    ConnectionPool, MessageBuffer, ZeroCopyBuffer, StreamReader, StreamWriter,
    AsyncSocketWrapper, performance_context
)
from .security_handler import (
    SecurityHandler, SecurityConfig, SecurityLevel, ValidationType,
    SSLSocketWrapper, MessageSigner, InputValidator, RateLimiter,
    Authenticator, SecurityLogger
)

__version__ = "1.0.2"
__author__ = "Ayam Maximilian"
__email__ = "ayammaxmillian@gmail.com"

__all__ = [
    'EnhancedClient', 'ClientConfig', 'ConnectionState',
    'EnhancedServer', 'ServerConfig', 'ServerState',
    'MessageHandler', 'MessageConfig', 'Message', 'MessageType', 'CompressionType',
    'ProtocolHandler', 'ProtocolConfig', 'ProtocolType', 'MessageFormat', 'FramingType',
    'PerformanceHandler', 'PerformanceConfig', 'MultiplexingStrategy', 'BufferStrategy',
    'ConnectionPool', 'MessageBuffer', 'ZeroCopyBuffer', 'StreamReader', 'StreamWriter',
    'AsyncSocketWrapper', 'performance_context',
    'SecurityHandler', 'SecurityConfig', 'SecurityLevel', 'ValidationType',
    'SSLSocketWrapper', 'MessageSigner', 'InputValidator', 'RateLimiter',
    'Authenticator', 'SecurityLogger'
]