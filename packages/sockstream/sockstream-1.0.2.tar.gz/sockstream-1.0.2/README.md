# SockStream

A comprehensive Python library for advanced socket communications with enterprise-grade features including connection management, message handling, protocol support, performance optimization, and security.

## 🚀 Features

### Core Features
- **Socket Communication**: TCP, UDP, and WebSocket support
- **Event-Driven Architecture**: Easy-to-use event handlers and decorators
- **Channel & Room Management**: Organize communications with server-controlled rooms
- **Cross-Platform**: Windows, Linux, and macOS support

### Connection Management
- **Auto-reconnect** with exponential backoff and jitter
- **Connection pooling** for multiple connections
- **Health checks** and connection monitoring
- **Configurable timeouts** (connect, read, write)
- **Connection statistics** and monitoring

### Message Handling
- **Message queuing** when connection is down
- **Message acknowledgment** system
- **Message compression** (gzip/deflate)
- **Binary data support** (not just JSON)
- **Message batching** for performance
- **Multiple formats**: JSON, Protocol Buffers, MessagePack

### Protocol Support
- **Transport Protocols**: TCP, UDP, WebSocket
- **Message Formats**: JSON, Protocol Buffers, MessagePack
- **Message Framing**: Length-prefixed, delimiter-based
- **Custom protocol handlers**

### Performance Features
- **Async/await** support
- **Connection multiplexing**
- **Message buffering** and streaming
- **Zero-copy** message passing
- **Performance monitoring** and optimization

### Security Features
- **SSL/TLS** encryption
- **Message signing** and verification
- **Input validation** and sanitization
- **Rate limiting** (per-IP and per-user)
- **Authentication** system with bcrypt
- **Security logging** and monitoring

## 📦 Installation

### Installation from PyPI

```bash
# Install from PyPI
pip install sockstream

# Install with performance optimizations (Linux/macOS only)
pip install sockstream[performance]

# Install with all optional dependencies
pip install sockstream[all]
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/ayammaximilian/sockstream.git
cd sockstream

# Install in development mode
pip install -e .
```

### Platform-Specific Dependencies

The package includes optional performance dependencies that are platform-specific:

- **Windows**: Uses standard Python asyncio (no additional dependencies)
- **Linux/macOS**: Can optionally use `uvloop` for enhanced performance

**Note**: `uvloop` is not compatible with Windows. The package automatically handles this by making `uvloop` an optional dependency on Windows systems.

### Manual Installation

If you encounter issues with automatic dependency resolution:

```bash
# Core dependencies
pip install msgpack protobuf cryptography bcrypt

# Performance dependency (Linux/macOS only)
pip install uvloop  # Skip on Windows
```

## 🎯 Quick Start

## 🔌 Enhanced Client Usage

### Basic Enhanced Client

```python
from sockstream import EnhancedClient, ClientConfig

# Create enhanced client with default settings
client = EnhancedClient(
    host='localhost', 
    port=8080, 
    server_channel='chat'  # Server connection filter
)

@client.on('connection_accepted')
def handle_connection(data):
    print(f"✅ Connected: {data}")

@client.on('connection_rejected')
def handle_rejection(data):
    print(f"❌ Rejected: {data}")

@client.on('message')
def handle_message(data):
    print(f"📨 Message: {data}")

@client.on('error')
def handle_error(error_msg):
    print(f"❌ Error: {error_msg}")

# Connect and use
if client.connect():
    client.emit('message', {'text': 'Hello from enhanced client!'})
    client.disconnect()
```

### Advanced Client Configuration

```python
from sockstream import EnhancedClient, ClientConfig

# Configure connection management
config = ClientConfig(
    # Connection settings
    connect_timeout=5.0,
    read_timeout=30.0,
    write_timeout=10.0,
    
    # Auto-reconnect settings
    enable_auto_reconnect=True,
    max_reconnect_attempts=5,
    initial_reconnect_delay=1.0,
    max_reconnect_delay=60.0,
    reconnect_jitter=0.1,
    
    # Health check settings
    enable_health_checks=True,
    health_check_interval=30.0,
    ping_timeout=5.0,
    
    # Message settings
    enable_message_queuing=True,
    max_queued_messages=100,
    message_retry_attempts=3,
    
    # Performance settings
    use_uvloop=False,  # Set to True on Linux/macOS
    enable_connection_pooling=True,
    max_pool_size=5,
    
    # Security settings
    enable_ssl=False,
    ssl_cert_file="",
    enable_message_signing=False,
    enable_input_validation=True,
    enable_rate_limiting=True
)

# Create enhanced client with configuration
client = EnhancedClient(
    host='localhost', 
    port=8080, 
    server_channel='chat',
    config=config
)
```

### Room Management

```python
# Join rooms for message routing
client.join_room('general')
client.join_room('admin')

# Send messages to specific rooms
client.emit('announcement', {'text': 'Server maintenance'}, room='admin')
client.emit('message', {'text': 'Hello everyone!'}, room='general')

# Request to join approval-only rooms
client.request_join_room('private')
client.request_leave_room('general')

# Get available rooms
rooms = client.get_available_rooms_sync()
print(f"Available rooms: {rooms}")
```

### SSL/TLS Connection

```python
from sockstream import EnhancedClient, ClientConfig

# SSL configuration
config = ClientConfig(
    enable_ssl=True,
    ssl_cert_file="path/to/cert.pem",
    ssl_verify_mode=ssl.CERT_REQUIRED,
    ssl_check_hostname=True
)

client = EnhancedClient(
    host='localhost', 
    port=8443,  # SSL port
    server_channel='secure',
    config=config
)

# SSL info
ssl_info = client.get_ssl_info()
print(f"SSL Protocol: {ssl_info['protocol']}")
print(f"SSL Cipher: {ssl_info['cipher']}")
```

### Message Signing and Validation

```python
# Configure message security
config = ClientConfig(
    enable_message_signing=True,
    signing_algorithm="HMAC-SHA256",
    signing_key="your-secret-key",
    enable_input_validation=True,
    max_message_size=1024 * 1024  # 1MB
)

client = EnhancedClient(
    host='localhost', 
    port=8080, 
    server_channel='secure',
    config=config
)

# Send signed message
client.emit('secure_message', {'data': 'sensitive information'})

# Verify received message
@client.on('message')
def handle_secure_message(data):
    if client.verify_message(data):
        print("✅ Message verified successfully")
    else:
        print("❌ Message verification failed")
```

## 🖥️ Enhanced Server Usage

### Basic Enhanced Server

```python
from sockstream import EnhancedServer, ServerConfig

# Create enhanced server
server = EnhancedServer(
    host='0.0.0.0', 
    port=8080, 
    max_connections=100,
    server_channel='chat'
)

# Event handlers
@server.on('client_connected')
def handle_client_connected(client_info):
    print(f"✅ Client connected: {client_info}")

@server.on('client_disconnected')
def handle_client_disconnected(client_info):
    print(f"❌ Client disconnected: {client_info}")

@server.on('message')
def handle_message(client_info, data):
    print(f"📨 Message from {client_info}: {data}")
    # Broadcast to all clients
    server.broadcast('message', data)

@server.on('join_request_received')
def handle_join_request(client_info, room_name):
    print(f"🔐 Join request for room '{room_name}' from {client_info}")
    # Auto-approve or manually approve
    server.approve_join_request(client_info['id'], room_name)

# Start server
server.start()
```

### Advanced Server Configuration

```python
from sockstream import EnhancedServer, ServerConfig

# Configure server
config = ServerConfig(
    # Connection settings
    max_connections=1000,
    connection_timeout=300.0,
    idle_timeout=600.0,
    
    # Performance settings
    use_uvloop=False,  # Set to True on Linux/macOS
    enable_connection_pooling=True,
    max_pool_size=50,
    
    # Security settings
    enable_ssl=False,
    ssl_cert_file="",
    ssl_key_file="",
    enable_message_signing=True,
    enable_input_validation=True,
    enable_rate_limiting=True,
    rate_limit_max_requests=1000,
    rate_limit_window=60.0,
    
    # Monitoring settings
    enable_monitoring=True,
    monitoring_interval=30.0
)

# Create enhanced server with configuration
server = EnhancedServer(
    host='0.0.0.0', 
    port=8080, 
    max_connections=1000,
    server_channel='production',
    config=config
)
```

### Room Management

```python
# Create rooms
server.create_room('general', approve_only=False)
server.create_room('admin', approve_only=True)
server.create_room('private', approve_only=True)

# Join clients to rooms
server.join_room('client_123', 'general')

# Broadcast to specific rooms
server.broadcast_to_room('announcement', {'text': 'Server restart'}, 'admin')

# Get room information
rooms = server.get_available_rooms()
print(f"Available rooms: {rooms}")

# Delete rooms
server.delete_room('old_room')
```

### SSL/TLS Server

```python
from sockstream import EnhancedServer, ServerConfig

# SSL configuration
config = ServerConfig(
    enable_ssl=True,
    ssl_cert_file="path/to/server.crt",
    ssl_key_file="path/to/server.key",
    ssl_ca_file="path/to/ca.crt",
    ssl_verify_mode=ssl.CERT_REQUIRED
)

server = EnhancedServer(
    host='0.0.0.0', 
    port=8443,  # SSL port
    max_connections=100,
    server_channel='secure',
    config=config
)

# SSL info
ssl_info = server.get_ssl_info()
print(f"SSL Protocol: {ssl_info['protocol']}")
print(f"SSL Cipher: {ssl_info['cipher']}")
```

### Authentication and Rate Limiting

```python
# Configure authentication
config = ServerConfig(
    enable_authentication=True,
    auth_timeout=300.0,
    max_auth_attempts=3,
    enable_rate_limiting=True,
    rate_limit_by_ip=True,
    rate_limit_by_user=True,
    rate_limit_max_requests=100,
    rate_limit_window=60.0
)

server = EnhancedServer(
    host='0.0.0.0', 
    port=8080, 
    max_connections=100,
    server_channel='secure',
    config=config
)

# Add users
server.add_user('admin', 'secure_password_123', permissions=['admin'])
server.add_user('user1', 'password123', permissions=['user'])

# Check permissions
if server.has_permission('admin', 'admin'):
    server.broadcast('admin_message', {'text': 'Admin broadcast'})
```

## 📊 Performance Features

### Async/Await Support

```python
import asyncio
from sockstream import AsyncSocketWrapper, StreamReader, StreamWriter

async def async_client():
    # Create async socket wrapper
    socket_wrapper = AsyncSocketWrapper('localhost', 8080)
    await socket_wrapper.connect()
    
    # Create reader/writer
    reader = StreamReader(socket_wrapper)
    writer = StreamWriter(socket_wrapper)
    
    # Send message
    await writer.write_json({'type': 'hello', 'data': 'async message'})
    
    # Read response
    response = await reader.read_json()
    print(f"Response: {response}")
    
    await socket_wrapper.close()

# Run async client
asyncio.run(async_client())
```

### Connection Multiplexing

```python
from sockstream import ConnectionPool, MultiplexingStrategy

# Create connection pool
pool = ConnectionPool(
    host='localhost',
    port=8080,
    max_connections=10,
    strategy=MultiplexingStrategy.ROUND_ROBIN
)

# Get connection from pool
connection = pool.get_connection()
try:
    connection.emit('message', {'text': 'Hello from pool'})
finally:
    pool.return_connection(connection)
```

### Message Batching

```python
from sockstream import MessageBuffer, BufferStrategy

# Create message buffer
buffer = MessageBuffer(
    strategy=BufferStrategy.TIME_BASED,
    batch_size=100,
    batch_timeout=1.0
)

# Add messages to buffer
for i in range(50):
    buffer.add_message({'id': i, 'data': f'message_{i}'})

# Process batched messages
batches = buffer.get_batches()
for batch in batches:
    print(f"Processing batch of {len(batch)} messages")
```

## 🔒 Security Features

### Message Signing

```python
from sockstream import MessageSigner

# Create message signer
signer = MessageSigner(
    signing_algorithm="HMAC-SHA256",
    signing_key="your-secret-key",
    verify_signatures=True
)

# Sign message
message = {'data': 'sensitive information'}
signed_message = signer.sign_message(message)

# Verify message
if signer.verify_message(signed_message):
    print("✅ Message verified")
else:
    print("❌ Message verification failed")
```

### Input Validation

```python
from sockstream import InputValidator

# Create input validator
validator = InputValidator(
    strict_validation=True,
    max_message_size=1024 * 1024,  # 1MB
    block_sql_injection=True,
    block_xss=True
)

# Validate input
message = {'user_input': 'SELECT * FROM users; DROP TABLE users;'}
if validator.validate_input(message):
    print("✅ Input validated")
else:
    print("❌ Input validation failed")

# Sanitize input
sanitized = validator.sanitize_input(message)
print(f"Sanitized: {sanitized}")
```

### Rate Limiting

```python
from sockstream import RateLimiter

# Create rate limiter
limiter = RateLimiter(
    rate_limit_window=60.0,
    rate_limit_max_requests=100,
    rate_limit_by_ip=True,
    rate_limit_by_user=True
)

# Check rate limit
client_ip = '192.168.1.100'
user_id = 'user123'

if limiter.is_allowed(client_ip, user_id):
    print("✅ Request allowed")
    # Process request
else:
    print("❌ Rate limit exceeded")
    remaining = limiter.get_remaining_requests(client_ip, user_id)
    print(f"Remaining requests: {remaining}")
```

## 📝 Complete Examples

### Chat Application

```python
# server.py
from sockstream import EnhancedServer, ServerConfig

config = ServerConfig(
    enable_ssl=False,
    enable_message_signing=True,
    enable_input_validation=True,
    enable_rate_limiting=True
)

server = EnhancedServer(
    host='0.0.0.0', 
    port=8080, 
    max_connections=100,
    server_channel='chat',
    config=config
)

# Create chat rooms
server.create_room('general', approve_only=False)
server.create_room('admin', approve_only=True)

@server.on('client_connected')
def handle_client_connected(client_info):
    print(f"✅ {client_info['address']} joined the chat")
    server.broadcast_to_room('system', {'text': f'{client_info["address"]} joined'}, 'general')

@server.on('client_disconnected')
def handle_client_disconnected(client_info):
    print(f"❌ {client_info['address']} left the chat")
    server.broadcast_to_room('system', {'text': f'{client_info["address"]} left'}, 'general')

@server.on('message')
def handle_message(client_info, data):
    room = data.get('room', 'general')
    message_data = {
        'user': client_info['address'],
        'text': data['text'],
        'timestamp': data.get('timestamp')
    }
    server.broadcast_to_room('message', message_data, room)

@server.on('join_request_received')
def handle_join_request(client_info, room_name):
    if room_name == 'admin':
        # Manual approval for admin room
        print(f"🔐 Admin room join request from {client_info['address']}")
        # You can implement approval logic here
    else:
        # Auto-approve for other rooms
        server.approve_join_request(client_info['id'], room_name)

server.start()
```

```python
# client.py
from sockstream import EnhancedClient, ClientConfig
import time

config = ClientConfig(
    enable_auto_reconnect=True,
    enable_health_checks=True,
    enable_message_signing=True,
    enable_input_validation=True
)

client = EnhancedClient(
    host='localhost', 
    port=8080, 
    server_channel='chat',
    config=config
)

@client.on('connection_accepted')
def handle_connection(data):
    print(f"✅ Connected to chat server")
    # Join general room
    client.join_room('general')
    # Request to join admin room
    client.request_join_room('admin')

@client.on('message')
def handle_message(data):
    if data['type'] == 'message':
        print(f"💬 {data['user']}: {data['text']}")
    elif data['type'] == 'system':
        print(f"ℹ️  {data['text']}")

@client.on('error')
def handle_error(error_msg):
    print(f"❌ Error: {error_msg}")

# Connect and chat
if client.connect():
    print("🔌 Connected! Type your messages:")
    
    try:
        while True:
            message = input("> ")
            if message.lower() == 'quit':
                break
            
            client.emit('message', {
                'text': message,
                'room': 'general',
                'timestamp': time.time()
            })
    except KeyboardInterrupt:
        pass
    
    client.disconnect()
    print("👋 Disconnected")
```

### File Transfer Server

```python
# file_server.py
from sockstream import EnhancedServer, ServerConfig
import os

config = ServerConfig(
    enable_ssl=True,
    ssl_cert_file="server.crt",
    ssl_key_file="server.key",
    enable_message_signing=True,
    max_message_size=100 * 1024 * 1024  # 100MB
)

server = EnhancedServer(
    host='0.0.0.0', 
    port=8443, 
    max_connections=50,
    server_channel='file_transfer',
    config=config
)

@server.on('client_connected')
def handle_client_connected(client_info):
    print(f"✅ File transfer client connected: {client_info['address']}")

@server.on('file_upload_request')
def handle_file_upload(client_info, data):
    filename = data['filename']
    file_size = data['size']
    
    print(f"📁 File upload request: {filename} ({file_size} bytes)")
    
    # Create upload directory
    os.makedirs('uploads', exist_ok=True)
    
    # Send approval
    server.send_to_client(client_info['id'], 'file_upload_approved', {
        'filename': filename,
        'upload_id': f"upload_{client_info['id']}_{int(time.time())}"
    })

@server.on('file_chunk')
def handle_file_chunk(client_info, data):
    upload_id = data['upload_id']
    chunk_data = data['chunk']
    chunk_index = data['index']
    
    # Save chunk to file
    with open(f"uploads/{upload_id}.part", 'ab') as f:
        f.write(chunk_data)
    
    # Send acknowledgment
    server.send_to_client(client_info['id'], 'chunk_received', {
        'upload_id': upload_id,
        'chunk_index': chunk_index
    })

server.start()
```

## 🧪 Testing

### Run Examples

```bash
# Test security features
python example_security_features.py

# Test performance features
python example_performance_features.py

# Test basic functionality
python -c "
from sockstream import EnhancedClient, EnhancedServer
print('✅ SockStream imported successfully!')
"
```

### Installation Test

```bash
# Run comprehensive installation test
python test_installation.py
```

## 📚 API Reference

### Core Classes

- **`EnhancedClient`**: Advanced client with connection management
- **`EnhancedServer`**: Advanced server with monitoring and control
- **`ClientConfig`**: Client configuration options
- **`ServerConfig`**: Server configuration options

### Handler Classes

- **`MessageHandler`**: Message processing and management
- **`ProtocolHandler`**: Protocol support and message framing
- **`PerformanceHandler`**: Performance optimization features
- **`SecurityHandler`**: Security features and validation

### Enums and Types

- **`ConnectionState`**: Client connection states
- **`ServerState`**: Server states
- **`MessageType`**: Message types
- **`CompressionType`**: Compression algorithms
- **`ProtocolType`**: Transport protocols
- **`SecurityLevel`**: Security levels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the examples and API reference
- **Security**: Report security issues privately

---

**SockStream** - Advanced socket communication made simple and secure! 🚀🔒
