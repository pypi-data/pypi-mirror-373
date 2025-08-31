import socket
import ssl
import json
import threading
import time
import random
from typing import Optional, Callable, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum
from .message_handler import MessageHandler, MessageConfig, Message, MessageType
from .protocol_handler import ProtocolHandler, ProtocolConfig, ProtocolType, MessageFormat, FramingType
from .performance_handler import PerformanceHandler, PerformanceConfig, MultiplexingStrategy, BufferStrategy
from .security_handler import SecurityHandler, SecurityConfig, ValidationType


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


@dataclass
class ClientConfig:
    """Configuration for connection management."""
    connect_timeout: float = 5.0
    read_timeout: float = 30.0
    write_timeout: float = 10.0
    max_reconnect_attempts: int = 5
    initial_reconnect_delay: float = 1.0
    max_reconnect_delay: float = 60.0
    reconnect_backoff_multiplier: float = 2.0
    health_check_interval: float = 30.0
    health_check_timeout: float = 5.0
    enable_auto_reconnect: bool = True
    enable_health_checks: bool = True
    
    # Message handling configuration
    enable_message_queuing: bool = True
    enable_message_acknowledgment: bool = True
    enable_message_compression: bool = True
    enable_binary_messages: bool = True
    enable_message_batching: bool = True
    message_ack_timeout: float = 5.0
    message_compression_threshold: int = 1024
    message_batch_size: int = 10
    message_batch_timeout: float = 0.1
    max_message_queue_size: int = 1000
    
    # Protocol configuration
    protocol_type: ProtocolType = ProtocolType.TCP
    message_format: MessageFormat = MessageFormat.JSON
    framing_type: FramingType = FramingType.LENGTH_PREFIXED
    delimiter: str = '\n'
    max_message_size: int = 1024 * 1024  # 1MB
    udp_buffer_size: int = 8192
    tcp_keepalive: bool = True
    tcp_nodelay: bool = True
    
    # Performance configuration
    enable_async: bool = True
    use_uvloop: bool = False  # Disabled by default for Windows compatibility
    max_concurrent_connections: int = 1000
    enable_multiplexing: bool = False
    multiplexing_strategy: MultiplexingStrategy = MultiplexingStrategy.ROUND_ROBIN
    max_connections_per_pool: int = 10
    connection_pool_timeout: float = 30.0
    enable_buffering: bool = True
    buffer_strategy: BufferStrategy = BufferStrategy.SIMPLE
    buffer_size: int = 8192
    max_buffer_size: int = 1024 * 1024  # 1MB
    flush_interval: float = 0.1
    enable_zero_copy: bool = True
    use_memory_mapping: bool = True
    shared_memory_size: int = 1024 * 1024  # 1MB
    enable_streaming: bool = True
    chunk_size: int = 4096
    max_stream_size: int = 100 * 1024 * 1024  # 100MB
    
    # Security configuration
    enable_ssl: bool = False
    ssl_cert_file: str = ""
    ssl_key_file: str = ""
    ssl_ca_file: str = ""
    ssl_verify_mode: int = ssl.CERT_REQUIRED
    ssl_check_hostname: bool = True
    ssl_ciphers: str = "HIGH:!aNULL:!MD5:!RC4"
    ssl_protocol: int = ssl.PROTOCOL_TLSv1_2
    enable_message_signing: bool = False
    signing_algorithm: str = "HMAC-SHA256"
    signing_key: str = ""
    auto_generate_signing_key: bool = True
    verify_signatures: bool = True
    enable_input_validation: bool = True
    strict_validation: bool = False
    max_message_size: int = 1024 * 1024  # 1MB
    allowed_characters: str = r'[\w\s\-_.,!?@#$%^&*()+=<>\[\]{}|\\/:;"\'`~]'
    block_sql_injection: bool = True
    block_xss: bool = True
    enable_rate_limiting: bool = True
    rate_limit_window: float = 60.0  # 1 minute
    rate_limit_max_requests: int = 100
    rate_limit_by_ip: bool = True
    rate_limit_by_user: bool = False
    rate_limit_strategy: str = "sliding_window"
    enable_authentication: bool = False
    auth_timeout: float = 300.0  # 5 minutes
    max_auth_attempts: int = 3
    password_min_length: int = 8
    require_special_chars: bool = True
    enable_security_logging: bool = True
    log_suspicious_activity: bool = True
    log_failed_auth: bool = True
    log_rate_limit_violations: bool = True


class EnhancedClient:
    """
    Enhanced client with connection management features:
    - Auto-reconnect with exponential backoff
    - Connection pooling
    - Health checks and monitoring
    - Configurable timeouts
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080, server_channel: str = 'default', 
                 config: Optional[ClientConfig] = None):
        """
        Initialize the enhanced client.
        
        Args:
            host (str): Server host address
            port (int): Server port number
            server_channel (str): Server channel to connect to (connection filter)
            config (ClientConfig): Connection configuration
        """
        self.host = host
        self.port = port
        self.server_channel = server_channel  # Server's connection filter
        self.config = config or ClientConfig()
        
        # Connection state
        self.socket: Optional[socket.socket] = None
        self.state = ConnectionState.DISCONNECTED
        self.connection_accepted = False
        self.event_handlers: Dict[str, Callable] = {}
        self.receive_thread: Optional[threading.Thread] = None
        self.health_check_thread: Optional[threading.Thread] = None
        self.running = False
        self.joined_rooms: List[str] = []  # Rooms within the connection
        self._rooms_response: Optional[Dict[str, Any]] = None  # For storing room responses
        
        # Connection management
        self.reconnect_attempts = 0
        self.last_health_check = 0
        self.last_activity = 0
        self.connection_start_time = 0
        self.message_queue: List[Dict] = []
        self.connection_pool: List[socket.socket] = []
        self.max_pool_size = 5
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'failed_connections': 0,
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'total_reconnects': 0,
            'uptime': 0
        }
        
        # Initialize message handler
        message_config = MessageConfig(
            enable_compression=self.config.enable_message_compression,
            compression_threshold=self.config.message_compression_threshold,
            enable_batching=self.config.enable_message_batching,
            batch_size=self.config.message_batch_size,
            batch_timeout=self.config.message_batch_timeout,
            enable_acknowledgment=self.config.enable_message_acknowledgment,
            ack_timeout=self.config.message_ack_timeout,
            max_queue_size=self.config.max_message_queue_size,
            enable_binary=self.config.enable_binary_messages
        )
        self.message_handler = MessageHandler(message_config)
        
        # Initialize protocol handler
        protocol_config = ProtocolConfig(
            protocol_type=self.config.protocol_type,
            message_format=self.config.message_format,
            framing_type=self.config.framing_type,
            delimiter=self.config.delimiter,
            max_message_size=self.config.max_message_size,
            udp_buffer_size=self.config.udp_buffer_size,
            tcp_keepalive=self.config.tcp_keepalive,
            tcp_nodelay=self.config.tcp_nodelay
        )
        self.protocol_handler = ProtocolHandler(protocol_config)
        
        # Initialize performance handler
        performance_config = PerformanceConfig(
            enable_async=self.config.enable_async,
            use_uvloop=self.config.use_uvloop,
            max_concurrent_connections=self.config.max_concurrent_connections,
            enable_multiplexing=self.config.enable_multiplexing,
            multiplexing_strategy=self.config.multiplexing_strategy,
            max_connections_per_pool=self.config.max_connections_per_pool,
            connection_pool_timeout=self.config.connection_pool_timeout,
            enable_buffering=self.config.enable_buffering,
            buffer_strategy=self.config.buffer_strategy,
            buffer_size=self.config.buffer_size,
            max_buffer_size=self.config.max_buffer_size,
            flush_interval=self.config.flush_interval,
            enable_zero_copy=self.config.enable_zero_copy,
            use_memory_mapping=self.config.use_memory_mapping,
            shared_memory_size=self.config.shared_memory_size,
            enable_streaming=self.config.enable_streaming,
            chunk_size=self.config.chunk_size,
            max_stream_size=self.config.max_stream_size
        )
        self.performance_handler = PerformanceHandler(performance_config)
        
        # Initialize security handler
        security_config = SecurityConfig(
            enable_ssl=self.config.enable_ssl,
            ssl_cert_file=self.config.ssl_cert_file,
            ssl_key_file=self.config.ssl_key_file,
            ssl_ca_file=self.config.ssl_ca_file,
            ssl_verify_mode=self.config.ssl_verify_mode,
            ssl_check_hostname=self.config.ssl_check_hostname,
            ssl_ciphers=self.config.ssl_ciphers,
            ssl_protocol=self.config.ssl_protocol,
            enable_message_signing=self.config.enable_message_signing,
            signing_algorithm=self.config.signing_algorithm,
            signing_key=self.config.signing_key,
            auto_generate_signing_key=self.config.auto_generate_signing_key,
            verify_signatures=self.config.verify_signatures,
            enable_input_validation=self.config.enable_input_validation,
            strict_validation=self.config.strict_validation,
            max_message_size=self.config.max_message_size,
            allowed_characters=self.config.allowed_characters,
            block_sql_injection=self.config.block_sql_injection,
            block_xss=self.config.block_xss,
            enable_rate_limiting=self.config.enable_rate_limiting,
            rate_limit_window=self.config.rate_limit_window,
            rate_limit_max_requests=self.config.rate_limit_max_requests,
            rate_limit_by_ip=self.config.rate_limit_by_ip,
            rate_limit_by_user=self.config.rate_limit_by_user,
            rate_limit_strategy=self.config.rate_limit_strategy,
            enable_authentication=self.config.enable_authentication,
            auth_timeout=self.config.auth_timeout,
            max_auth_attempts=self.config.max_auth_attempts,
            password_min_length=self.config.password_min_length,
            require_special_chars=self.config.require_special_chars,
            enable_security_logging=self.config.enable_security_logging,
            log_suspicious_activity=self.config.log_suspicious_activity,
            log_failed_auth=self.config.log_failed_auth,
            log_rate_limit_violations=self.config.log_rate_limit_violations
        )
        self.security_handler = SecurityHandler(security_config)
    
    def connect(self) -> bool:
        """
        Connect to server with auto-reconnect support.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        return self._connect_with_retry()
    
    def _connect_with_retry(self) -> bool:
        """Connect with retry logic and exponential backoff."""
        self.state = ConnectionState.CONNECTING
        
        while self.reconnect_attempts < self.config.max_reconnect_attempts:
            try:
                if self._attempt_connection():
                    self.state = ConnectionState.CONNECTED
                    self.reconnect_attempts = 0
                    self.connection_start_time = time.time()
                    self.stats['total_connections'] += 1
                    return True
                
            except Exception as e:
                self.stats['failed_connections'] += 1
                if 'error' in self.event_handlers:
                    self.event_handlers['error'](f"Connection attempt {self.reconnect_attempts + 1} failed: {e}")
            
            self.reconnect_attempts += 1
            
            if self.reconnect_attempts < self.config.max_reconnect_attempts:
                delay = self._calculate_reconnect_delay()
                if 'reconnecting' in self.event_handlers:
                    self.event_handlers['reconnecting']({
                        'attempt': self.reconnect_attempts,
                        'delay': delay,
                        'max_attempts': self.config.max_reconnect_attempts
                    })
                
                time.sleep(delay)
        
        self.state = ConnectionState.DISCONNECTED
        if 'connection_failed' in self.event_handlers:
            self.event_handlers['connection_failed']({
                'attempts': self.reconnect_attempts,
                'host': self.host,
                'port': self.port
            })
        return False
    
    def _attempt_connection(self) -> bool:
        """Attempt a single connection."""
        try:
            # Try to get socket from pool first
            if self.connection_pool:
                self.socket = self.connection_pool.pop()
            else:
                # Create socket using protocol handler
                self.socket = self.protocol_handler.create_client_socket()
            
            # Set timeouts
            self.socket.settimeout(self.config.connect_timeout)
            
            # Connect to server using protocol handler
            if not self.protocol_handler.connect_client(self.socket, self.host, self.port):
                return False
            
            # Set read/write timeouts
            self.socket.settimeout(self.config.read_timeout)
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            # Start health check thread if enabled
            if self.config.enable_health_checks:
                self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
                self.health_check_thread.start()
            
            # Send initial message with server channel info
            initial_message = {
                'event': 'connect',
                'data': {'server_channel': self.server_channel},
                'channel': self.server_channel,  # For backward compatibility
                'timestamp': time.time()
            }
            message_str = json.dumps(initial_message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            
            # Wait for server response
            start_time = time.time()
            while time.time() - start_time < self.config.connect_timeout:
                if self.connection_accepted:
                    self.connection_accepted = True
                    return True
                elif not self.running:  # Connection was rejected
                    return False
                time.sleep(0.1)
            
            # Timeout waiting for server response
            self.disconnect()
            if 'error' in self.event_handlers:
                self.event_handlers['error']("Connection timeout - no response from server")
            return False
            
        except Exception as e:
            self.connection_accepted = False
            if 'error' in self.event_handlers:
                self.event_handlers['error'](str(e))
            return False
    
    def _calculate_reconnect_delay(self) -> float:
        """Calculate reconnect delay with exponential backoff and jitter."""
        base_delay = self.config.initial_reconnect_delay * (self.config.reconnect_backoff_multiplier ** (self.reconnect_attempts - 1))
        delay = min(base_delay, self.config.max_reconnect_delay)
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0.8, 1.2)
        return delay * jitter
    
    def _health_check_loop(self):
        """Health check loop to monitor connection health."""
        while self.running and self.state == ConnectionState.CONNECTED:
            try:
                time.sleep(self.config.health_check_interval)
                if not self._perform_health_check():
                    if self.config.enable_auto_reconnect and self.state != ConnectionState.DISCONNECTED:
                        self._handle_connection_loss()
                    break
            except Exception as e:
                if 'error' in self.event_handlers:
                    self.event_handlers['error'](f"Health check error: {e}")
    
    def _perform_health_check(self) -> bool:
        """Perform a health check on the connection."""
        try:
            if not self.socket:
                return False
            
            # Send a ping message
            ping_message = {
                'event': 'ping',
                'data': {'timestamp': time.time()},
                'timestamp': time.time()
            }
            message_str = json.dumps(ping_message) + '\n'
            
            # Set a short timeout for the ping
            original_timeout = self.socket.gettimeout()
            self.socket.settimeout(self.config.health_check_timeout)
            
            self.socket.send(message_str.encode('utf-8'))
            
            # Wait for pong response
            start_time = time.time()
            while time.time() - start_time < self.config.health_check_timeout:
                try:
                    data = self.socket.recv(1024)
                    if data:
                        # Reset timeout
                        self.socket.settimeout(original_timeout)
                        self.last_health_check = time.time()
                        return True
                except socket.timeout:
                    break
            
            # Reset timeout
            self.socket.settimeout(original_timeout)
            return False
            
        except Exception:
            return False
    
    def _handle_connection_loss(self):
        """Handle connection loss and initiate reconnection."""
        # Don't reconnect if we explicitly disconnected
        if self.state == ConnectionState.DISCONNECTED:
            return
            
        self.state = ConnectionState.RECONNECTING
        self.stats['total_reconnects'] += 1
        
        if 'connection_lost' in self.event_handlers:
            self.event_handlers['connection_lost']({
                'host': self.host,
                'port': self.port,
                'uptime': time.time() - self.connection_start_time
            })
        
        # Queue any pending messages
        if self.message_queue:
            if 'messages_queued' in self.event_handlers:
                self.event_handlers['messages_queued']({
                    'count': len(self.message_queue)
                })
        
        # Attempt reconnection
        if self._connect_with_retry():
            # Resend queued messages
            self._resend_queued_messages()
            
            if 'connection_restored' in self.event_handlers:
                self.event_handlers['connection_restored']({
                    'reconnect_attempts': self.reconnect_attempts
                })
    
    def _resend_queued_messages(self):
        """Resend messages that were queued during disconnection."""
        while self.message_queue and self.state == ConnectionState.CONNECTED:
            message = self.message_queue.pop(0)
            try:
                self.emit(message['event'], message['data'], room=message.get('room'))
            except Exception as e:
                if 'error' in self.event_handlers:
                    self.event_handlers['error'](f"Failed to resend queued message: {e}")
    
    def _receive_loop(self):
        """Receive loop for handling incoming messages."""
        while self.running:
            try:
                if not self.socket:
                    break
                
                # Receive messages using protocol handler
                messages = self.protocol_handler.receive_message(self.socket)
                
                if not messages:
                    continue
                
                self.last_activity = time.time()
                self.stats['total_messages_received'] += len(messages)
                
                # Process each message
                for message in messages:
                    if isinstance(message, str):
                        self._process_message(message)
                    elif isinstance(message, dict):
                        # Convert dict to JSON string for processing
                        self._process_message(json.dumps(message))
                    else:
                        # Handle other message types
                        self._process_message(str(message))
                        
            except socket.timeout:
                continue
            except Exception as e:
                try:
                    if 'error' in self.event_handlers:
                        self.event_handlers['error'](str(e))
                except:
                    pass
                break
        
        # Connection lost - only auto-reconnect if we didn't explicitly disconnect
        if self.config.enable_auto_reconnect and self.state != ConnectionState.DISCONNECTED:
            self._handle_connection_loss()
    
    def _process_message(self, message_str: str):
        """Process a received message."""
        try:
            # Use message handler to deserialize
            message = self.message_handler.deserialize_message(message_str)
            event = message.event
            data = message.data
            
            # Handle acknowledgments first
            if event == 'ack':
                self.message_handler.handle_ack(data.get('message_id', ''))
                return
            
            if event == 'connection_accepted':
                self.connection_accepted = True
            elif event == 'connection_rejected':
                self.running = False
            elif event == 'pong':
                # Health check response
                pass
            elif event == 'room_joined':
                # Room join successful
                room_name = data.get('room')
                if room_name and room_name not in self.joined_rooms:
                    self.joined_rooms.append(room_name)
            elif event == 'room_join_requested':
                # Room join request submitted (for approve-only rooms)
                room_name = data.get('room')
                status = data.get('status')
                message = data.get('message')
                request_id = data.get('request_id')
                
                # Log the request
                if 'room_join_requested' in self.event_handlers:
                    self.event_handlers['room_join_requested']({
                        'room': room_name,
                        'status': status,
                        'message': message,
                        'request_id': request_id
                    })
            elif event == 'room_join_approved':
                # Room join request approved
                room_name = data.get('room')
                message = data.get('message')
                
                # Add to joined rooms
                if room_name and room_name not in self.joined_rooms:
                    self.joined_rooms.append(room_name)
                
                # Log the approval
                if 'room_join_approved' in self.event_handlers:
                    self.event_handlers['room_join_approved']({
                        'room': room_name,
                        'message': message
                    })
            elif event == 'room_join_rejected':
                # Room join request rejected
                room_name = data.get('room')
                reason = data.get('reason')
                message = data.get('message')
                
                # Log the rejection
                if 'room_join_rejected' in self.event_handlers:
                    self.event_handlers['room_join_rejected']({
                        'room': room_name,
                        'reason': reason,
                        'message': message
                    })
            elif event == 'room_left':
                # Room leave successful
                room_name = data.get('room')
                if room_name and room_name in self.joined_rooms:
                    self.joined_rooms.remove(room_name)
            elif event == 'room_join_error':
                # Room join error (e.g., approve-only room)
                room_name = data.get('room')
                error_code = data.get('error_code')
                reason = data.get('reason', 'Unknown error')
                
                # Log the error
                if 'error' in self.event_handlers:
                    self.event_handlers['error'](f"Room join error for {room_name}: {reason}")
                
                # If it's an approve-only room, suggest using request_join_room
                if error_code == 'APPROVE_ONLY_ROOM':
                    if 'approve_only_room_error' in self.event_handlers:
                        self.event_handlers['approve_only_room_error']({
                            'room': room_name,
                            'reason': reason,
                            'suggestion': 'Use request_join_room() instead of join_room()'
                        })
            elif event == 'room_join_failed':
                # Room join failed (e.g., room full, not available)
                room_name = data.get('room')
                reason = data.get('reason', 'Unknown error')
                
                # Log the error
                if 'error' in self.event_handlers:
                    self.event_handlers['error'](f"Room join failed for {room_name}: {reason}")
                
                # Check if it's an approve-only room error
                if 'approve_only' in reason.lower() or 'approval' in reason.lower():
                    if 'approve_only_room_error' in self.event_handlers:
                        self.event_handlers['approve_only_room_error']({
                            'room': room_name,
                            'reason': reason,
                            'suggestion': 'Use request_join_room() instead of join_room()'
                        })
            elif event == 'batch':
                # Process batched messages
                if isinstance(data, list):
                    for item in data:
                        # Process each item in the batch
                        if isinstance(item, dict) and 'event' in item:
                            self._process_message(json.dumps(item))
            elif event == 'rooms_list':
                # Available rooms list received
                self._rooms_response = data.get('rooms', {})
            
            # Emit event to handlers
            if event in self.event_handlers:
                self.event_handlers[event](data)
                
        except json.JSONDecodeError:
            pass
    
    def emit(self, event: str, data: Any = None, room: str = None, 
             requires_ack: bool = False, priority: int = 0, message_type: MessageType = MessageType.JSON):
        """
        Emit an event with data to a specific room.
        
        Args:
            event (str): Event name to emit
            data (Any): Data to send with the event
            room (str, optional): Room to emit to (if None, uses server_channel)
            requires_ack (bool): Whether this message requires acknowledgment
            priority (int): Message priority (higher = more important)
            message_type (MessageType): Type of message (JSON, BINARY, etc.)
        """
        # Create message using message handler
        message = self.message_handler.create_message(
            event=event,
            data=data,
            room=room or self.server_channel,
            requires_ack=requires_ack,
            priority=priority
        )
        message.message_type = message_type
        
        if self.state != ConnectionState.CONNECTED or not self.socket:
            # Queue message if auto-reconnect is enabled
            if self.config.enable_auto_reconnect and self.config.enable_message_queuing:
                self.message_handler.queue_message(message)
                return
            else:
                raise ConnectionError("Not connected to server")
        
        # Try to add to batch first
        if self.config.enable_message_batching:
            if self.message_handler.add_to_batch(message):
                return  # Message was batched
        
        # Send message immediately
        self._send_message(message)
    
    def emit_binary(self, event: str, data: bytes, room: str = None, 
                    requires_ack: bool = False, priority: int = 0):
        """Emit binary data as a message."""
        return self.emit(event, data, room, requires_ack, priority, MessageType.BINARY)
    
    def emit_with_ack(self, event: str, data: Any = None, room: str = None, 
                      priority: int = 0, callback: Optional[Callable] = None):
        """Emit a message that requires acknowledgment."""
        message = self.emit(event, data, room, True, priority)
        
        if callback:
            self.message_handler.add_ack_callback(message.id, callback)
        
        return message
    
    def _send_message(self, message: Message):
        """Send a message using the message handler."""
        try:
            # Serialize the message
            message_str = self.message_handler.serialize_message(message)
            
            # Mark for acknowledgment if needed
            if message.requires_ack:
                self.message_handler.mark_for_ack(message)
            
            # Send the message using protocol handler
            if not self.protocol_handler.send_message(self.socket, message_str):
                raise Exception("Failed to send message via protocol handler")
            
            self.stats['total_messages_sent'] += 1
            self.last_activity = time.time()
            
        except Exception as e:
            # Emit error event
            if 'error' in self.event_handlers:
                self.event_handlers['error'](str(e))
            # Only auto-reconnect if we didn't explicitly disconnect
            if self.config.enable_auto_reconnect and self.state != ConnectionState.DISCONNECTED:
                self._handle_connection_loss()
    
    def get_available_rooms(self) -> Dict[str, Any]:
        """
        Get list of available rooms from the server.
        
        Returns:
            Dict[str, Any]: Dictionary of available rooms and their info
        """
        if self.state != ConnectionState.CONNECTED or not self.socket:
            return {}
        
        # Request room list from server
        self.emit('get_rooms', {})
        
        # For now, return empty dict - in a real implementation,
        # you'd wait for the server response
        return {}
    
    def get_available_rooms_sync(self) -> Dict[str, Any]:
        """
        Get list of available rooms from the server (synchronous).
        This method waits for the server response.
        
        Returns:
            Dict[str, Any]: Dictionary of available rooms and their info
        """
        if self.state != ConnectionState.CONNECTED or not self.socket:
            return {}
        
        # Store the response
        self._rooms_response = None
        
        # Request room list from server
        self.emit('get_rooms', {})
        
        # Wait for response (with timeout)
        start_time = time.time()
        while self._rooms_response is None and time.time() - start_time < 5.0:
            time.sleep(0.1)
        
        return self._rooms_response or {}
    
    def request_join_room(self, room: str) -> bool:
        """
        Request to join a room (server-controlled).
        
        Args:
            room (str): Room name to join
            
        Returns:
            bool: True if request sent successfully, False otherwise
        """
        if self.state != ConnectionState.CONNECTED or not self.socket:
            return False
        
        self.emit('join_room_request', {'room': room})
        return True
    
    def request_leave_room(self, room: str) -> bool:
        """
        Request to leave a room (server-controlled).
        
        Args:
            room (str): Room name to leave
            
        Returns:
            bool: True if request sent successfully, False otherwise
        """
        if self.state != ConnectionState.CONNECTED or not self.socket:
            return False
        
        self.emit('leave_room_request', {'room': room})
        return True
    
    def join_room(self, room: str) -> bool:
        """
        Join a room within the current connection.
        
        Args:
            room (str): Room name to join
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room not in self.joined_rooms:
            self.joined_rooms.append(room)
            self.emit('join_room', {'room': room}, room=room)
        return True
    
    def leave_room(self, room: str) -> bool:
        """
        Leave a room within the current connection.
        
        Args:
            room (str): Room name to leave
            
        Returns:
            bool: True if successful, False otherwise
        """
        if room in self.joined_rooms:
            self.joined_rooms.remove(room)
            self.emit('leave_room', {'room': room}, room=room)
        return True
    
    def disconnect(self):
        """Disconnect from the server and clean up resources."""
        self.state = ConnectionState.DISCONNECTED
        self.running = False
        self.connection_accepted = False
        
        # Close socket immediately
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Wait for threads to finish (with timeout)
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        
        if self.health_check_thread and self.health_check_thread.is_alive():
            self.health_check_thread.join(timeout=1.0)
        
        # Clear message queue
        self.message_queue.clear()
        
        # Clear connection pool
        for sock in self.connection_pool:
            try:
                sock.close()
            except:
                pass
        self.connection_pool.clear()
        
        # Clean up performance handler
        if hasattr(self, 'performance_handler') and self.performance_handler:
            self.performance_handler.cleanup()
        
        # Clean up security handler
        if hasattr(self, 'security_handler') and self.security_handler:
            self.security_handler.cleanup()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        current_time = time.time()
        return {
            **self.stats,
            'current_state': self.state.value,
            'reconnect_attempts': self.reconnect_attempts,
            'uptime': current_time - self.connection_start_time if self.connection_start_time else 0,
            'last_health_check': current_time - self.last_health_check if self.last_health_check else 0,
            'last_activity': current_time - self.last_activity if self.last_activity else 0,
            'pool_size': len(self.connection_pool),
            'queued_messages': len(self.message_queue)
        }
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get message handling statistics."""
        return self.message_handler.get_queue_stats()
    
    def flush_message_batch(self):
        """Force flush the current message batch."""
        return self.message_handler.flush_batch()
    
    def cleanup_expired_acks(self):
        """Clean up expired acknowledgments."""
        self.message_handler.cleanup_expired_acks()
    
    # Performance methods
    def add_connection_to_pool(self, weight: float = 1.0) -> bool:
        """Add current connection to the multiplexing pool."""
        if self.socket and self.performance_handler:
            return self.performance_handler.add_connection_to_pool(self.socket, weight)
        return False
    
    def get_connection_from_pool(self):
        """Get a connection from the multiplexing pool."""
        if self.performance_handler:
            return self.performance_handler.get_connection_from_pool()
        return None
    
    def buffer_message(self, message: Any, priority: int = 0):
        """Buffer a message for later sending."""
        if self.performance_handler:
            self.performance_handler.buffer_message(message, priority)
    
    def add_buffer_flush_callback(self, callback: Callable):
        """Add callback for when message buffer is flushed."""
        if self.performance_handler:
            self.performance_handler.add_buffer_flush_callback(callback)
    
    def force_buffer_flush(self):
        """Force flush the message buffer."""
        if self.performance_handler:
            self.performance_handler.force_buffer_flush()
    
    def write_zero_copy(self, data: bytes):
        """Write data using zero-copy buffer."""
        if self.performance_handler:
            return self.performance_handler.write_zero_copy(data)
        return None
    
    def read_zero_copy(self, offset: int, size: int):
        """Read data using zero-copy buffer."""
        if self.performance_handler:
            return self.performance_handler.read_zero_copy(offset, size)
        return None
    
    async def async_send(self, data: bytes) -> bool:
        """Send data asynchronously."""
        if self.socket and self.performance_handler:
            return await self.performance_handler.async_send(self.socket, data)
        return False
    
    async def async_recv(self, size: int = 4096):
        """Receive data asynchronously."""
        if self.socket and self.performance_handler:
            return await self.performance_handler.async_recv(self.socket, size)
        return None
    
    def create_stream_reader(self, chunk_size: int = None):
        """Create a stream reader for large data."""
        if self.socket and self.performance_handler:
            return self.performance_handler.create_stream_reader(self.socket, chunk_size)
        return None
    
    def create_stream_writer(self, chunk_size: int = None):
        """Create a stream writer for large data."""
        if self.socket and self.performance_handler:
            return self.performance_handler.create_stream_writer(self.socket, chunk_size)
        return None
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        if self.performance_handler:
            return self.performance_handler.get_stats()
        return {}
    
    # Security methods
    def wrap_socket_ssl(self, server_side: bool = False) -> socket.socket:
        """Wrap current socket with SSL/TLS."""
        if self.socket and self.security_handler:
            return self.security_handler.wrap_socket_ssl(self.socket, server_side)
        return self.socket
    
    def get_ssl_info(self) -> Dict:
        """Get SSL information from current socket."""
        if self.socket and self.security_handler:
            return self.security_handler.get_ssl_info(self.socket)
        return {}
    
    def sign_message(self, message: Union[str, bytes, dict]) -> str:
        """Sign a message."""
        if self.security_handler:
            return self.security_handler.sign_message(message)
        return ""
    
    def verify_message(self, message: Union[str, bytes, dict], signature: str) -> bool:
        """Verify a message signature."""
        if self.security_handler:
            return self.security_handler.verify_message(message, signature)
        return True
    
    def validate_input(self, data: Any, validation_type: ValidationType = ValidationType.STRING) -> bool:
        """Validate input data."""
        if self.security_handler:
            return self.security_handler.validate_input(data, validation_type)
        return True
    
    def sanitize_input(self, data: Any) -> Any:
        """Sanitize input data."""
        if self.security_handler:
            return self.security_handler.sanitize_input(data)
        return data
    
    def is_rate_limited(self, identifier: str = None) -> bool:
        """Check if current connection is rate limited."""
        if not self.security_handler:
            return False
        
        if identifier is None:
            identifier = f"{self.host}:{self.port}"
        
        return self.security_handler.is_rate_limited(identifier)
    
    def get_remaining_requests(self, identifier: str = None) -> int:
        """Get remaining requests for current connection."""
        if not self.security_handler:
            return 100
        
        if identifier is None:
            identifier = f"{self.host}:{self.port}"
        
        return self.security_handler.get_remaining_requests(identifier)
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user."""
        if self.security_handler:
            return self.security_handler.authenticate_user(username, password)
        return True
    
    def create_user_session(self, username: str) -> str:
        """Create a session for a user."""
        if self.security_handler:
            return self.security_handler.create_user_session(username)
        return ""
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate a session."""
        if self.security_handler:
            return self.security_handler.validate_session(session_id)
        return {}
    
    def has_permission(self, session_id: str, permission: str) -> bool:
        """Check if a session has a specific permission."""
        if self.security_handler:
            return self.security_handler.has_permission(session_id, permission)
        return True
    
    def add_user(self, username: str, password: str, permissions: List[str] = None) -> bool:
        """Add a new user."""
        if self.security_handler:
            return self.security_handler.add_user(username, password, permissions)
        return True
    
    def log_security_event(self, event: str, level: str = "INFO", details: Dict = None):
        """Log a security event."""
        if self.security_handler:
            self.security_handler.log_security_event(event, level, details)
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        if self.security_handler:
            return self.security_handler.get_security_stats()
        return {}
    
    def is_healthy(self) -> bool:
        """Check if the connection is healthy."""
        if self.state != ConnectionState.CONNECTED:
            return False
        
        if not self.config.enable_health_checks:
            return True
        
        current_time = time.time()
        return (current_time - self.last_health_check) < (self.config.health_check_interval * 2)
    
    # Event handler decorators
    def on(self, event: str):
        """Decorator to register an event handler."""
        def decorator(func: Callable):
            self.event_handlers[event] = func
            return func
        return decorator
    
    def error(self, func: Callable):
        """Decorator to register an error handler."""
        self.event_handlers['error'] = func
        return func
    
    def connect_event(self, func: Callable):
        """Decorator to register a connect event handler."""
        self.event_handlers['connect'] = func
        return func
    
    def disconnect_event(self, func: Callable):
        """Decorator to register a disconnect event handler."""
        self.event_handlers['disconnect'] = func
        return func
