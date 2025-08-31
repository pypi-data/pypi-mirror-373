import socket
import ssl
import json
import threading
import time
from typing import Optional, Dict, Any, Set, List, Union, Callable
from dataclasses import dataclass
from enum import Enum
from .message_handler import MessageHandler, MessageConfig, MessageType
from .protocol_handler import ProtocolHandler, ProtocolConfig, ProtocolType, MessageFormat, FramingType
from .performance_handler import PerformanceHandler, PerformanceConfig, MultiplexingStrategy, BufferStrategy
from .security_handler import SecurityHandler, SecurityConfig, ValidationType


class ServerState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"


@dataclass
class ServerConfig:
    """Configuration for server connection management."""
    max_connections: int = 0 #infinite
    connection_timeout: float = 60.0  # 1 minute
    cleanup_interval: float = 60.0  # 1 minute
    health_check_interval: float = 30.0  # 30 seconds
    enable_connection_monitoring: bool = True
    enable_automatic_cleanup: bool = True
    enable_connection_stats: bool = True
    channel: Optional[str] = None
    
    # Message handling configuration
    enable_message_compression: bool = True
    enable_binary_messages: bool = True
    enable_message_acknowledgment: bool = True
    message_compression_threshold: int = 1024
    message_ack_timeout: float = 5.0
    
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


class EnhancedServer:
    """
    Enhanced server with connection management features:
    - Connection monitoring and health tracking
    - Automatic cleanup of dead connections
    - Connection statistics and metrics
    - Configurable timeouts and limits
    """
    
    def __init__(self, host: str = 'localhost', port: int = 8080, config: Optional[ServerConfig] = None):
        """
        Initialize the enhanced server.
        
        Args:
            host (str): Server host address
            port (int): Server port number
            config (ServerConfig): Server configuration
        """
        self.host = host
        self.port = port
        self.config = config or ServerConfig()
        
        # Server state
        self.state = ServerState.STOPPED
        self.socket: Optional[socket.socket] = None
        self.running = False
        
        # Connection management
        self.clients: Dict[socket.socket, Dict[str, Any]] = {}
        self.client_channels: Dict[str, Set[socket.socket]] = {}
        self.connection_threads: Dict[socket.socket, threading.Thread] = {}
        
        # Room management (server-controlled)
        self.available_rooms: Dict[str, Dict[str, Any]] = {}  # room_name -> room_info
        self.room_members: Dict[str, Set[socket.socket]] = {}  # room_name -> set of client sockets
        self.room_creators: Dict[str, str] = {}  # room_name -> creator info
        
        # Pending join requests for approve-only rooms
        self.pending_join_requests: Dict[str, List[Dict[str, Any]]] = {}  # room_name -> list of pending requests
        
        # Monitoring and cleanup
        self.monitoring_thread: Optional[threading.Thread] = None
        self.cleanup_thread: Optional[threading.Thread] = None
        self.last_cleanup = time.time()
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'current_connections': 0,
            'total_messages_processed': 0,
            'total_channels_created': 0,
            'total_rooms_created': 0,
            'total_rooms_deleted': 0,
            'start_time': 0,
            'uptime': 0
        }
        
        # Event handlers
        self.event_handlers: Dict[str, Any] = {}
        
        # Initialize message handler
        message_config = MessageConfig(
            enable_compression=self.config.enable_message_compression,
            compression_threshold=self.config.message_compression_threshold,
            enable_acknowledgment=self.config.enable_message_acknowledgment,
            ack_timeout=self.config.message_ack_timeout,
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
    
    def start(self) -> bool:
        """
        Start the server with connection monitoring.
        
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if self.state != ServerState.STOPPED:
            return False
        
        self.state = ServerState.STARTING
        
        try:
            # Create server socket using protocol handler
            self.socket = self.protocol_handler.create_server_socket(self.host, self.port)
            
            # Set listen backlog for TCP/WebSocket
            if self.config.protocol_type in [ProtocolType.TCP, ProtocolType.WEBSOCKET]:
                self.socket.listen(self.config.max_connections)
            
            self.running = True
            self.state = ServerState.RUNNING
            self.stats['start_time'] = time.time()
            
            # Start connection acceptance thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            # Start monitoring thread if enabled
            if self.config.enable_connection_monitoring:
                self.monitoring_thread = threading.Thread(target=self._monitor_connections, daemon=True)
                self.monitoring_thread.start()
            
            # Start cleanup thread if enabled
            if self.config.enable_automatic_cleanup:
                self.cleanup_thread = threading.Thread(target=self._cleanup_dead_connections, daemon=True)
                self.cleanup_thread.start()
            
            return True
            
        except Exception as e:
            self.state = ServerState.STOPPED
            self.running = False
            if self.socket:
                self.socket.close()
                self.socket = None
            return False
    
    def stop(self):
        """Stop the server and clean up all connections."""
        if self.state == ServerState.STOPPED:
            return
        
        self.state = ServerState.STOPPING
        self.running = False
        
        # Close all client connections
        for client_socket in list(self.clients.keys()):
            self._disconnect_client(client_socket)
        
        # Close server socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # Clean up performance handler
        if hasattr(self, 'performance_handler') and self.performance_handler:
            self.performance_handler.cleanup()
        
        # Clean up security handler
        if hasattr(self, 'security_handler') and self.security_handler:
            self.security_handler.cleanup()
        
        self.state = ServerState.STOPPED
    
    def _accept_connections(self):
        """Accept incoming connections."""
        while self.running:
            try:
                if not self.socket:
                    break
                
                client_socket, address = self.socket.accept()
                
                # Check connection limit
                if len(self.clients) >= self.config.max_connections:
                    self._reject_connection(client_socket, "Server at maximum capacity")
                    continue
                
                # Handle new connection
                self._handle_client_connection(client_socket, address)
                
            except Exception as e:
                if self.running:
                    # Only log errors if server is still running
                    pass
                break
    
    def _handle_client_connection(self, client_socket: socket.socket, address: tuple):
        """Handle initial client connection with channel filtering."""
        try:
            # Set timeout for initial handshake
            client_socket.settimeout(10.0)
            
            # Wait for first message
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                client_socket.close()
                return
            
            # Process the first message to get client's channel
            try:
                message = json.loads(data.split('\n')[0])
                client_channel = message.get('channel', 'default')
                
                # Check if server has channel filtering enabled
                if self.config.channel is not None and client_channel != self.config.channel:
                    # Send rejection message
                    rejection_msg = {
                        'event': 'connection_rejected',
                        'data': {
                            'reason': 'channel_mismatch',
                            'message': f'Server does not accept channel "{client_channel}"'
                        },
                        'timestamp': time.time()
                    }
                    client_socket.send((json.dumps(rejection_msg) + '\n').encode('utf-8'))
                    client_socket.close()
                    return
                
                # Channel matches or server accepts all channels - accept the connection
                client_socket.settimeout(None)  # Remove timeout
                
                # Add client to clients dict
                self.clients[client_socket] = {
                    'address': address,
                    'joined_channels': set(),
                    'connected_at': time.time(),
                    'channel': client_channel,
                    'last_activity': time.time(),
                    'message_count': 0
                }
                
                # Update statistics
                self.stats['total_connections'] += 1
                self.stats['current_connections'] += 1
                
                # Send acceptance message
                acceptance_msg = {
                    'event': 'connection_accepted',
                    'data': {
                        'channel': client_channel,
                        'message': 'Connection accepted'
                    },
                    'timestamp': time.time()
                }
                client_socket.send((json.dumps(acceptance_msg) + '\n').encode('utf-8'))
                
                # Process any remaining data from the initial message
                remaining_data = ""
                if len(data.split('\n')) > 1:
                    remaining_data = '\n'.join(data.split('\n')[1:])
                
                # Start client message handling thread
                client_thread = threading.Thread(
                    target=self._handle_client_messages, 
                    args=(client_socket, address, remaining_data),
                    daemon=True
                )
                self.connection_threads[client_socket] = client_thread
                client_thread.start()
                
                # Emit connection event
                if 'client_connected' in self.event_handlers:
                    self.event_handlers['client_connected']({
                        'address': address,
                        'channel': client_channel,
                        'total_connections': self.stats['current_connections']
                    })
                
            except json.JSONDecodeError as e:
                # Invalid JSON - reject connection
                rejection_msg = {
                    'event': 'connection_rejected',
                    'data': {
                        'reason': 'invalid_message_format',
                        'message': 'Invalid message format'
                    },
                    'timestamp': time.time()
                }
                client_socket.send((json.dumps(rejection_msg) + '\n').encode('utf-8'))
                client_socket.close()
                
        except socket.timeout:
            client_socket.close()
        except Exception as e:
            client_socket.close()
    
    def _handle_client_messages(self, client_socket: socket.socket, address: tuple, initial_data: str = ""):
        """Handle communication with a specific client."""
        buffer = initial_data
        
        try:
            while self.running and client_socket in self.clients:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                # Update client activity
                if client_socket in self.clients:
                    self.clients[client_socket]['last_activity'] = time.time()
                
                buffer += data
                
                # Process complete messages
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str.strip():
                        self._process_client_message(client_socket, message_str)
                        
        except Exception as e:
            pass
        finally:
            self._disconnect_client(client_socket)
    
    def _process_client_message(self, client_socket: socket.socket, message_str: str):
        """Process a message from a client."""
        try:
            # Use message handler to deserialize
            message = self.message_handler.deserialize_message(message_str)
            event = message.event
            data = message.data
            channel = message.room or 'default'
            
            # Handle acknowledgments first
            if event == 'ack':
                # Send acknowledgment back to client
                ack_msg = {
                    'event': 'ack',
                    'data': {'message_id': data.get('message_id', '')},
                    'timestamp': time.time()
                }
                client_socket.send((json.dumps(ack_msg) + '\n').encode('utf-8'))
                return
            
            # Update message count
            if client_socket in self.clients:
                self.clients[client_socket]['message_count'] += 1
                self.stats['total_messages_processed'] += 1
            
            if event == 'join_channel':
                self._handle_join_channel(client_socket, data)
            elif event == 'leave_channel':
                self._handle_leave_channel(client_socket, data)
            elif event == 'join_room_request':
                self._handle_join_room_request(client_socket, data)
            elif event == 'join_room':
                self._handle_direct_join_room(client_socket, data)
            elif event == 'leave_room_request':
                self._handle_leave_room_request(client_socket, data)
            elif event == 'get_rooms':
                self._handle_get_rooms_request(client_socket)
            elif event == 'ping':
                # Health check response
                pong_msg = {
                    'event': 'pong',
                    'data': {'timestamp': time.time()},
                    'timestamp': time.time()
                }
                client_socket.send((json.dumps(pong_msg) + '\n').encode('utf-8'))
            else:
                # Broadcast message to room if specified, otherwise to channel
                target_room = message.get('room')
                if target_room and target_room in self.available_rooms:
                    self.broadcast_to_room(target_room, event, data, exclude_client=client_socket)
                else:
                    # Broadcast message to channel
                    self._broadcast_to_channel(channel, event, data, exclude_client=client_socket)
                
        except json.JSONDecodeError as e:
            pass
    
    def _handle_join_channel(self, client_socket: socket.socket, data: Dict[str, Any]):
        """Handle client joining a channel."""
        channel = data.get('channel', 'default')
        
        if client_socket in self.clients:
            self.clients[client_socket]['joined_channels'].add(channel)
            
            # Initialize channel if it doesn't exist
            if channel not in self.client_channels:
                self.client_channels[channel] = set()
                self.stats['total_channels_created'] += 1
            
            self.client_channels[channel].add(client_socket)
            
            # Emit join event
            if 'client_joined_channel' in self.event_handlers:
                self.event_handlers['client_joined_channel']({
                    'address': self.clients[client_socket]['address'],
                    'channel': channel,
                    'total_in_channel': len(self.client_channels[channel])
                })
    
    def _handle_leave_channel(self, client_socket: socket.socket, data: Dict[str, Any]):
        """Handle client leaving a channel."""
        channel = data.get('channel', 'default')
        
        if client_socket in self.clients:
            self.clients[client_socket]['joined_channels'].discard(channel)
            
            if channel in self.client_channels:
                self.client_channels[channel].discard(client_socket)
                
                # Remove empty channels
                if not self.client_channels[channel]:
                    del self.client_channels[channel]
                
                # Emit leave event
                if 'client_left_channel' in self.event_handlers:
                    self.event_handlers['client_left_channel']({
                        'address': self.clients[client_socket]['address'],
                        'channel': channel,
                        'total_in_channel': len(self.client_channels.get(channel, set()))
                    })
    
    def _handle_join_room_request(self, client_socket: socket.socket, data: Dict[str, Any]):
        """Handle client request to join a room."""
        room_name = data.get('room', 'default')
        
        # Check if room is approve-only first
        room_info = self.available_rooms.get(room_name, {})
        if room_info.get('approve_only', False):
            # For approve-only rooms, store the request and notify the client
            self._store_join_request(room_name, client_socket, data)
            success_msg = {
                'event': 'room_join_requested',
                'data': {
                    'room': room_name,
                    'message': f'Join request submitted for room: {room_name}. Waiting for approval.',
                    'status': 'pending_approval',
                    'request_id': self._get_request_id(room_name, client_socket)
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(success_msg) + '\n').encode('utf-8'))
            return
        
        # For non-approve-only rooms, try to join normally
        if self.join_room(client_socket, room_name):
            # Send success response
            success_msg = {
                'event': 'room_joined',
                'data': {
                    'room': room_name,
                    'message': f'Successfully joined room: {room_name}'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(success_msg) + '\n').encode('utf-8'))
        else:
            # Send failure response
            failure_msg = {
                'event': 'room_join_failed',
                'data': {
                    'room': room_name,
                    'reason': 'Room not available or full'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(failure_msg) + '\n').encode('utf-8'))
    
    def _handle_direct_join_room(self, client_socket: socket.socket, data: Dict[str, Any]):
        """Handle direct room join attempt (when client uses join_room instead of join_room_request)."""
        room_name = data.get('room', 'default')
        
        # Check if room is approve-only
        room_info = self.available_rooms.get(room_name, {})
        if room_info.get('approve_only', False):
            # Send error message for approve-only rooms
            error_msg = {
                'event': 'room_join_error',
                'data': {
                    'room': room_name,
                    'reason': 'Room requires approval. Use request_join_room command instead.',
                    'error_code': 'APPROVE_ONLY_ROOM'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(error_msg) + '\n').encode('utf-8'))
            return
        
        # For non-approve-only rooms, try to join normally
        if self.join_room(client_socket, room_name):
            # Send success response
            success_msg = {
                'event': 'room_joined',
                'data': {
                    'room': room_name,
                    'message': f'Successfully joined room: {room_name}'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(success_msg) + '\n').encode('utf-8'))
        else:
            # Send failure response
            failure_msg = {
                'event': 'room_join_failed',
                'data': {
                    'room': room_name,
                    'reason': 'Room not available or full'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(failure_msg) + '\n').encode('utf-8'))
    
    def _handle_leave_room_request(self, client_socket: socket.socket, data: Dict[str, Any]):
        """Handle client request to leave a room."""
        room_name = data.get('room', 'default')
        
        if self.leave_room(client_socket, room_name):
            # Send success response
            success_msg = {
                'event': 'room_left',
                'data': {
                    'room': room_name,
                    'message': f'Successfully left room: {room_name}'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(success_msg) + '\n').encode('utf-8'))
        else:
            # Send failure response
            failure_msg = {
                'event': 'room_leave_failed',
                'data': {
                    'room': room_name,
                    'reason': 'Room not found or client not in room'
                },
                'timestamp': time.time()
            }
            client_socket.send((json.dumps(failure_msg) + '\n').encode('utf-8'))
    
    def _handle_get_rooms_request(self, client_socket: socket.socket):
        """Handle client request to get available rooms."""
        rooms_info = self.get_available_rooms()
        
        response_msg = {
            'event': 'rooms_list',
            'data': {
                'rooms': rooms_info,
                'total_rooms': len(rooms_info)
            },
            'timestamp': time.time()
        }
        
        client_socket.send((json.dumps(response_msg) + '\n').encode('utf-8'))
    
    def _broadcast_to_channel(self, channel: str, event: str, data: Any, exclude_client: socket.socket = None):
        """Broadcast a message to all clients in a channel."""
        if channel not in self.client_channels:
            return
        
        message = {
            'event': event,
            'data': data,
            'channel': channel,
            'timestamp': time.time()
        }
        message_str = json.dumps(message) + '\n'
        
        # Send to all clients in channel except excluded one
        for client_socket in self.client_channels[channel]:
            if client_socket != exclude_client and client_socket in self.clients:
                try:
                    client_socket.send(message_str.encode('utf-8'))
                except:
                    # Client connection is dead, will be cleaned up
                    pass
    
    def _disconnect_client(self, client_socket: socket.socket):
        """Disconnect a client and clean up resources."""
        if client_socket not in self.clients:
            return
        
        client_info = self.clients[client_socket]
        
        # Remove from all channels
        for channel in client_info['joined_channels']:
            if channel in self.client_channels:
                self.client_channels[channel].discard(client_socket)
                
                # Remove empty channels
                if not self.client_channels[channel]:
                    del self.client_channels[channel]
        
        # Remove from connection threads
        if client_socket in self.connection_threads:
            del self.connection_threads[client_socket]
        
        # Clean up pending join requests for this client
        self._cleanup_pending_requests_for_client(client_socket)
        
        # Close socket
        try:
            client_socket.close()
        except:
            pass
        
        # Remove from clients dict
        del self.clients[client_socket]
        
        # Update statistics
        self.stats['current_connections'] -= 1
        
        # Emit disconnect event
        if 'client_disconnected' in self.event_handlers:
            self.event_handlers['client_disconnected']({
                'address': client_info['address'],
                'channel': client_info['channel'],
                'uptime': time.time() - client_info['connected_at'],
                'message_count': client_info['message_count'],
                'total_connections': self.stats['current_connections']
            })
    
    def _reject_connection(self, client_socket: socket.socket, reason: str):
        """Reject a connection with a reason."""
        rejection_msg = {
            'event': 'connection_rejected',
            'data': {
                'reason': 'server_rejection',
                'message': reason
            },
            'timestamp': time.time()
        }
        try:
            client_socket.send((json.dumps(rejection_msg) + '\n').encode('utf-8'))
        except:
            pass
        client_socket.close()
    
    def _monitor_connections(self):
        """Monitor connection health and activity."""
        while self.running:
            try:
                time.sleep(self.config.health_check_interval)
                
                current_time = time.time()
                dead_connections = []
                
                # Check for dead connections
                for client_socket, client_info in self.clients.items():
                    # Check if connection is still alive
                    try:
                        # Send a ping to test connection
                        ping_msg = {
                            'event': 'ping',
                            'data': {'timestamp': current_time},
                            'timestamp': current_time
                        }
                        client_socket.send((json.dumps(ping_msg) + '\n').encode('utf-8'))
                    except:
                        dead_connections.append(client_socket)
                        continue
                    
                    # Check for inactive connections
                    if (current_time - client_info['last_activity']) > self.config.connection_timeout:
                        dead_connections.append(client_socket)
                
                # Clean up dead connections
                for client_socket in dead_connections:
                    self._disconnect_client(client_socket)
                
                # Update uptime
                if self.stats['start_time'] > 0:
                    self.stats['uptime'] = current_time - self.stats['start_time']
                
            except Exception as e:
                pass
    
    def _cleanup_dead_connections(self):
        """Periodically clean up dead connections."""
        while self.running:
            try:
                time.sleep(self.config.cleanup_interval)
                
                current_time = time.time()
                if (current_time - self.last_cleanup) < self.config.cleanup_interval:
                    continue
                
                self.last_cleanup = current_time
                
                # Cleanup logic is handled in _monitor_connections
                # This thread just ensures periodic cleanup
                
            except Exception as e:
                pass
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        current_time = time.time()
        return {
            **self.stats,
            'current_state': self.state.value,
            'uptime': current_time - self.stats['start_time'] if self.stats['start_time'] > 0 else 0,
            'channel_count': len(self.client_channels),
            'max_connections': self.config.max_connections,
            'connection_usage_percent': (self.stats['current_connections'] / self.config.max_connections) * 100 if self.config.max_connections > 0 else 0
        }
    
    def get_channel_info(self) -> Dict[str, Any]:
        """Get information about all channels."""
        return {
            channel: {
                'client_count': len(clients),
                'clients': [
                    {
                        'address': self.clients[client_socket]['address'],
                        'connected_at': self.clients[client_socket]['connected_at'],
                        'message_count': self.clients[client_socket]['message_count']
                    }
                    for client_socket in clients
                    if client_socket in self.clients
                ]
            }
            for channel, clients in self.client_channels.items()
        }
    
    def get_client_info(self, client_socket: socket.socket) -> Optional[Dict[str, Any]]:
        """Get information about a specific client."""
        if client_socket not in self.clients:
            return None
        
        client_info = self.clients[client_socket].copy()
        client_info['uptime'] = time.time() - client_info['connected_at']
        return client_info
    
    def is_healthy(self) -> bool:
        """Check if the server is healthy."""
        if self.state != ServerState.RUNNING:
            return False
        
        # Check if we're at capacity
        if self.stats['current_connections'] >= self.config.max_connections:
            return False
        
        # Check if server socket is still valid
        try:
            if not self.socket:
                return False
            # Try to get socket info to check if it's still valid
            self.socket.getsockname()
            return True
        except:
            return False
    
    # Room management methods
    def create_room(self, room_name: str, **room_info) -> bool:
        """
        Create a new room on the server.
        
        Args:
            room_name (str): Name of the room to create
            room_info (Dict[str, Any], optional): Additional room information
                Can include 'approve_only' (bool) to make room require approval
            
        Returns:
            bool: True if room created successfully, False if room already exists
        """
        if room_name in self.available_rooms:
            return False
        
        room_data = room_info or {}
        room_data.update({
            'created_at': time.time(),
            'member_count': 0,
            'max_members': room_data.get('max_members', 0),
            'approve_only': room_data.get('approve_only', False)
        })
        
        self.available_rooms[room_name] = room_data
        self.room_members[room_name] = set()
        self.room_creators[room_name] = f"server_{int(time.time())}"
        self.stats['total_rooms_created'] += 1
        
        return True
    
    def _store_join_request(self, room_name: str, client_socket: socket.socket, data: Dict[str, Any]):
        """Store a join request for an approve-only room."""
        if room_name not in self.pending_join_requests:
            self.pending_join_requests[room_name] = []
        
        request = {
            'client_socket': client_socket,
            'client_address': self.clients[client_socket]['address'],
            'timestamp': time.time(),
            'data': data
        }
        
        self.pending_join_requests[room_name].append(request)
        
        # Emit event for admin notification
        if 'join_request_received' in self.event_handlers:
            self.event_handlers['join_request_received']({
                'room': room_name,
                'client_address': request['client_address'],
                'timestamp': request['timestamp'],
                'total_pending': len(self.pending_join_requests[room_name])
            })
    
    def _get_request_id(self, room_name: str, client_socket: socket.socket) -> str:
        """Generate a unique request ID for tracking."""
        return f"{room_name}_{client_socket.fileno()}_{int(time.time())}"
    
    def approve_join_request(self, room_name: str, client_address: str) -> bool:
        """
        Approve a join request for an approve-only room.
        
        Args:
            room_name (str): Name of the room
            client_address (str): Address of the client to approve
            
        Returns:
            bool: True if approved successfully, False otherwise
        """
        if room_name not in self.pending_join_requests:
            return False
        
        # Find the request by client address
        for i, request in enumerate(self.pending_join_requests[room_name]):
            if request['client_address'] == client_address:
                client_socket = request['client_socket']
                
                # Check if client is still connected
                if client_socket not in self.clients:
                    # Remove expired request
                    self.pending_join_requests[room_name].pop(i)
                    return False
                
                # Try to join the room
                if self.join_room(client_socket, room_name):
                    # Remove the approved request
                    self.pending_join_requests[room_name].pop(i)
                    
                    # Send approval notification to client
                    approval_msg = {
                        'event': 'room_join_approved',
                        'data': {
                            'room': room_name,
                            'message': f'Your join request for room {room_name} has been approved!'
                        },
                        'timestamp': time.time()
                    }
                    client_socket.send((json.dumps(approval_msg) + '\n').encode('utf-8'))
                    
                    return True
        
        return False
    
    def reject_join_request(self, room_name: str, client_address: str, reason: str = "Request denied") -> bool:
        """
        Reject a join request for an approve-only room.
        
        Args:
            room_name (str): Name of the room
            client_address (str): Address of the client to reject
            reason (str): Reason for rejection
            
        Returns:
            bool: True if rejected successfully, False otherwise
        """
        if room_name not in self.pending_join_requests:
            return False
        
        # Find the request by client address
        for i, request in enumerate(self.pending_join_requests[room_name]):
            if request['client_address'] == client_address:
                client_socket = request['client_socket']
                
                # Check if client is still connected
                if client_socket not in self.clients:
                    # Remove expired request
                    self.pending_join_requests[room_name].pop(i)
                    return False
                
                # Send rejection notification to client
                rejection_msg = {
                    'event': 'room_join_rejected',
                    'data': {
                        'room': room_name,
                        'reason': reason,
                        'message': f'Your join request for room {room_name} has been rejected: {reason}'
                    },
                    'timestamp': time.time()
                }
                client_socket.send((json.dumps(rejection_msg) + '\n').encode('utf-8'))
                
                # Remove the rejected request
                self.pending_join_requests[room_name].pop(i)
                return True
        
        return False
    
    def get_pending_join_requests(self, room_name: str = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get pending join requests.
        
        Args:
            room_name (str, optional): Specific room name, or None for all rooms
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Pending requests by room
        """
        if room_name:
            return {room_name: self.pending_join_requests.get(room_name, [])}
        return self.pending_join_requests.copy()
    
    def _cleanup_pending_requests_for_client(self, client_socket: socket.socket):
        """Clean up pending join requests for a disconnected client."""
        client_address = None
        
        # Find the client address from the socket
        for room_name, requests in self.pending_join_requests.items():
            for request in requests:
                if request['client_socket'] == client_socket:
                    client_address = request['client_address']
                    break
            if client_address:
                break
        
        if client_address:
            # Remove all pending requests for this client from all rooms
            for room_name in list(self.pending_join_requests.keys()):
                self.pending_join_requests[room_name] = [
                    req for req in self.pending_join_requests[room_name]
                    if req['client_socket'] != client_socket
                ]
                
                # Remove empty room entries
                if not self.pending_join_requests[room_name]:
                    del self.pending_join_requests[room_name]
            
            # Emit cleanup event
            if 'pending_requests_cleaned_up' in self.event_handlers:
                self.event_handlers['pending_requests_cleaned_up']({
                    'client_address': client_address,
                    'message': f'Cleaned up pending requests for disconnected client: {client_address}'
                })
    
    def delete_room(self, room_name: str) -> bool:
        """
        Delete a room and remove all members.
        
        Args:
            room_name (str): Name of the room to delete
            
        Returns:
            bool: True if room deleted successfully, False if room doesn't exist
        """
        if room_name not in self.available_rooms:
            return False
        
        # Remove all members from the room
        if room_name in self.room_members:
            for client_socket in self.room_members[room_name]:
                if client_socket in self.clients:
                    self.clients[client_socket]['joined_rooms'].discard(room_name)
        
        # Clean up room data
        del self.available_rooms[room_name]
        del self.room_members[room_name]
        if room_name in self.room_creators:
            del self.room_creators[room_name]
        
        self.stats['total_rooms_deleted'] += 1
        return True
    
    def get_available_rooms(self) -> Dict[str, Any]:
        """
        Get information about all available rooms.
        
        Returns:
            Dict[str, Any]: Dictionary of room information
        """
        return {
            room_name: {
                **room_info,
                'member_count': len(self.room_members.get(room_name, set())),
                'creator': self.room_creators.get(room_name, 'unknown')
            }
            for room_name, room_info in self.available_rooms.items()
        }
    
    def join_room(self, client_socket: socket.socket, room_name: str) -> bool:
        """
        Add a client to a room (server-controlled).
        
        Args:
            client_socket (socket.socket): Client socket to add to room
            room_name (str): Name of the room to join
            
        Returns:
            bool: True if client joined successfully, False otherwise
        """
        if room_name not in self.available_rooms:
            return False
        
        if client_socket not in self.clients:
            return False
        
        # Check if room is approve-only
        room_info = self.available_rooms[room_name]
        if room_info.get('approve_only', False):
            return False  # Room requires approval, direct join not allowed
        
        # Check if room is full
        current_members = len(self.room_members[room_name])
        room_info_max_members = room_info.get('max_members', 0)

        if room_info_max_members > 0 and current_members >= room_info_max_members:
            return False
        
        # Add client to room
        self.room_members[room_name].add(client_socket)
        self.clients[client_socket]['joined_rooms'].add(room_name)
        
        # Update room member count
        self.available_rooms[room_name]['member_count'] = len(self.room_members[room_name])
        
        # Emit join event
        if 'client_joined_room' in self.event_handlers:
            self.event_handlers['client_joined_room']({
                'address': self.clients[client_socket]['address'],
                'room': room_name,
                'total_in_room': len(self.room_members[room_name])
            })
        
        return True
    
    def leave_room(self, client_socket: socket.socket, room_name: str) -> bool:
        """
        Remove a client from a room (server-controlled).
        
        Args:
            client_socket (socket.socket): Client socket to remove from room
            room_name (str): Name of the room to leave
            
        Returns:
            bool: True if client left successfully, False otherwise
        """
        if room_name not in self.room_members:
            return False
        
        if client_socket not in self.clients:
            return False
        
        # Remove client from room
        self.room_members[room_name].discard(client_socket)
        self.clients[client_socket]['joined_rooms'].discard(room_name)
        
        # Update room member count
        if room_name in self.available_rooms:
            self.available_rooms[room_name]['member_count'] = len(self.room_members[room_name])
        
        # Emit leave event
        if 'client_left_room' in self.event_handlers:
            self.event_handlers['client_left_room']({
                'address': self.clients[client_socket]['address'],
                'room': room_name,
                'total_in_room': len(self.room_members.get(room_name, set()))
            })
        
        return True
    
    def broadcast_to_room(self, room_name: str, event: str, data: Any, exclude_client: socket.socket = None,
                         requires_ack: bool = False, priority: int = 0, message_type: MessageType = MessageType.JSON):
        """
        Broadcast a message to all clients in a specific room.
        
        Args:
            room_name (str): Room to broadcast to
            event (str): Event name
            data (Any): Event data
            exclude_client (socket.socket, optional): Client to exclude from broadcast
            requires_ack (bool): Whether this message requires acknowledgment
            priority (int): Message priority (higher = more important)
            message_type (MessageType): Type of message (JSON, BINARY, etc.)
        """
        if room_name not in self.room_members:
            return
        
        # Create message using message handler
        message = self.message_handler.create_message(
            event=event,
            data=data,
            room=room_name,
            requires_ack=requires_ack,
            priority=priority
        )
        message.message_type = message_type
        
        # Serialize the message
        message_str = self.message_handler.serialize_message(message)
        
        # Send to all clients in room except excluded one
        for client_socket in self.room_members[room_name]:
            if client_socket != exclude_client and client_socket in self.clients:
                try:
                    client_socket.send(message_str.encode('utf-8'))
                except:
                    # Client connection is dead, will be cleaned up
                    pass
    
    def send_to_client(self, client_socket: socket.socket, event: str, data: Any = None,
                      requires_ack: bool = False, priority: int = 0, message_type: MessageType = MessageType.JSON):
        """Send a message to a specific client."""
        if client_socket not in self.clients:
            return False
        
        # Create message using message handler
        message = self.message_handler.create_message(
            event=event,
            data=data,
            requires_ack=requires_ack,
            priority=priority
        )
        message.message_type = message_type
        
        # Serialize the message
        message_str = self.message_handler.serialize_message(message)
        
        try:
            client_socket.send(message_str.encode('utf-8'))
            return True
        except:
            # Remove dead connection
            self._disconnect_client(client_socket)
            return False
    
    def send_binary_to_client(self, client_socket: socket.socket, event: str, data: bytes,
                             requires_ack: bool = False, priority: int = 0):
        """Send binary data to a specific client."""
        return self.send_to_client(client_socket, event, data, requires_ack, priority, MessageType.BINARY)
    
    def broadcast_binary_to_room(self, room_name: str, event: str, data: bytes,
                                exclude_client: socket.socket = None, requires_ack: bool = False, priority: int = 0):
        """Broadcast binary data to all clients in a room."""
        return self.broadcast_to_room(room_name, event, data, exclude_client, requires_ack, priority, MessageType.BINARY)
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Get message handling statistics."""
        return self.message_handler.get_queue_stats()
    
    # Performance methods
    def add_connection_to_pool(self, sock: socket.socket, weight: float = 1.0) -> bool:
        """Add connection to the multiplexing pool."""
        if self.performance_handler:
            return self.performance_handler.add_connection_to_pool(sock, weight)
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
    
    async def async_send(self, sock: socket.socket, data: bytes) -> bool:
        """Send data asynchronously to a specific client."""
        if self.performance_handler:
            return await self.performance_handler.async_send(sock, data)
        return False
    
    async def async_recv(self, sock: socket.socket, size: int = 4096):
        """Receive data asynchronously from a specific client."""
        if self.performance_handler:
            return await self.performance_handler.async_recv(sock, size)
        return None
    
    def create_stream_reader(self, sock: socket.socket, chunk_size: int = None):
        """Create a stream reader for large data."""
        if self.performance_handler:
            return self.performance_handler.create_stream_reader(sock, chunk_size)
        return None
    
    def create_stream_writer(self, sock: socket.socket, chunk_size: int = None):
        """Create a stream writer for large data."""
        if self.performance_handler:
            return self.performance_handler.create_stream_writer(sock, chunk_size)
        return None
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        if self.performance_handler:
            return self.performance_handler.get_stats()
        return {}
    
    # Security methods
    def wrap_socket_ssl(self, sock: socket.socket, server_side: bool = True) -> socket.socket:
        """Wrap a socket with SSL/TLS."""
        if self.security_handler:
            return self.security_handler.wrap_socket_ssl(sock, server_side)
        return sock
    
    def get_ssl_info(self, sock: socket.socket) -> Dict:
        """Get SSL information from a socket."""
        if self.security_handler:
            return self.security_handler.get_ssl_info(sock)
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
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if an identifier is rate limited."""
        if self.security_handler:
            return self.security_handler.is_rate_limited(identifier)
        return False
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for an identifier."""
        if self.security_handler:
            return self.security_handler.get_remaining_requests(identifier)
        return 100
    
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
    
    # Event handler decorators
    def on(self, event: str):
        """Decorator to register an event handler."""
        def decorator(func):
            self.event_handlers[event] = func
            return func
        return decorator
    
    def client_connected(self, func):
        """Decorator to register a client connected event handler."""
        self.event_handlers['client_connected'] = func
        return func
    
    def client_disconnected(self, func):
        """Decorator to register a client disconnected event handler."""
        self.event_handlers['client_disconnected'] = func
        return func
    
    def client_joined_channel(self, func):
        """Decorator to register a client joined channel event handler."""
        self.event_handlers['client_joined_channel'] = func
        return func
    
    def client_left_channel(self, func):
        """Decorator to register a client left channel event handler."""
        self.event_handlers['client_left_channel'] = func
        return func
    
    def client_joined_room(self, func):
        """Decorator to register a client joined room event handler."""
        self.event_handlers['client_joined_room'] = func
        return func
    
    def client_left_room(self, func):
        """Decorator to register a client left room event handler."""
        self.event_handlers['client_left_room'] = func
        return func
