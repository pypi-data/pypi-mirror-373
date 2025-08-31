import asyncio
import socket
import threading
import time
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque
import mmap
import io
import contextlib

try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False


class MultiplexingStrategy(Enum):
    """Connection multiplexing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"


class BufferStrategy(Enum):
    """Message buffering strategies."""
    NONE = "none"
    SIMPLE = "simple"
    CHUNKED = "chunked"
    STREAMING = "streaming"


@dataclass
class PerformanceConfig:
    """Configuration for performance features."""
    # Async settings
    enable_async: bool = True
    use_uvloop: bool = False  # Disabled by default for Windows compatibility
    max_concurrent_connections: int = 1000
    
    # Multiplexing settings
    enable_multiplexing: bool = False
    multiplexing_strategy: MultiplexingStrategy = MultiplexingStrategy.ROUND_ROBIN
    max_connections_per_pool: int = 10
    connection_pool_timeout: float = 30.0
    
    # Buffering settings
    enable_buffering: bool = True
    buffer_strategy: BufferStrategy = BufferStrategy.SIMPLE
    buffer_size: int = 8192
    max_buffer_size: int = 1024 * 1024  # 1MB
    flush_interval: float = 0.1
    
    # Zero-copy settings
    enable_zero_copy: bool = True
    use_memory_mapping: bool = True
    shared_memory_size: int = 1024 * 1024  # 1MB
    
    # Streaming settings
    enable_streaming: bool = True
    chunk_size: int = 4096
    max_stream_size: int = 100 * 1024 * 1024  # 100MB


class ConnectionPool:
    """Manages a pool of connections for multiplexing."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.connections: List[socket.socket] = []
        self.connection_weights: Dict[socket.socket, float] = {}
        self.connection_stats: Dict[socket.socket, Dict] = {}
        self.current_index = 0
        self.lock = threading.Lock()
        
    def add_connection(self, sock: socket.socket, weight: float = 1.0):
        """Add a connection to the pool."""
        with self.lock:
            if len(self.connections) < self.config.max_connections_per_pool:
                self.connections.append(sock)
                self.connection_weights[sock] = weight
                self.connection_stats[sock] = {
                    'created': time.time(),
                    'requests': 0,
                    'last_used': time.time(),
                    'response_times': deque(maxlen=100)
                }
                return True
        return False
    
    def remove_connection(self, sock: socket.socket):
        """Remove a connection from the pool."""
        with self.lock:
            if sock in self.connections:
                self.connections.remove(sock)
                self.connection_weights.pop(sock, None)
                self.connection_stats.pop(sock, None)
                return True
        return False
    
    def get_connection(self) -> Optional[socket.socket]:
        """Get a connection based on the multiplexing strategy."""
        with self.lock:
            if not self.connections:
                return None
            
            if self.config.multiplexing_strategy == MultiplexingStrategy.ROUND_ROBIN:
                return self._get_round_robin()
            elif self.config.multiplexing_strategy == MultiplexingStrategy.LEAST_CONNECTIONS:
                return self._get_least_connections()
            elif self.config.multiplexing_strategy == MultiplexingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._get_weighted_round_robin()
            elif self.config.multiplexing_strategy == MultiplexingStrategy.LEAST_RESPONSE_TIME:
                return self._get_least_response_time()
            
            return self.connections[0]
    
    def _get_round_robin(self) -> socket.socket:
        """Get connection using round-robin strategy."""
        conn = self.connections[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.connections)
        self._update_stats(conn)
        return conn
    
    def _get_least_connections(self) -> socket.socket:
        """Get connection with least active requests."""
        conn = min(self.connections, key=lambda c: self.connection_stats[c]['requests'])
        self._update_stats(conn)
        return conn
    
    def _get_weighted_round_robin(self) -> socket.socket:
        """Get connection using weighted round-robin strategy."""
        total_weight = sum(self.connection_weights.values())
        if total_weight == 0:
            return self.connections[0]
        
        # Simple weighted round-robin implementation
        conn = self.connections[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.connections)
        self._update_stats(conn)
        return conn
    
    def _get_least_response_time(self) -> socket.socket:
        """Get connection with lowest average response time."""
        def avg_response_time(conn):
            stats = self.connection_stats[conn]
            if not stats['response_times']:
                return float('inf')
            return sum(stats['response_times']) / len(stats['response_times'])
        
        conn = min(self.connections, key=avg_response_time)
        self._update_stats(conn)
        return conn
    
    def _update_stats(self, sock: socket.socket):
        """Update connection statistics."""
        if sock in self.connection_stats:
            stats = self.connection_stats[sock]
            stats['requests'] += 1
            stats['last_used'] = time.time()
    
    def record_response_time(self, sock: socket.socket, response_time: float):
        """Record response time for a connection."""
        if sock in self.connection_stats:
            self.connection_stats[sock]['response_times'].append(response_time)
    
    def cleanup_expired_connections(self):
        """Remove expired connections from the pool."""
        current_time = time.time()
        expired = []
        
        with self.lock:
            for sock in self.connections:
                stats = self.connection_stats[sock]
                if current_time - stats['last_used'] > self.config.connection_pool_timeout:
                    expired.append(sock)
            
            for sock in expired:
                self.remove_connection(sock)
        
        return len(expired)


class MessageBuffer:
    """Handles message buffering and streaming."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.buffer = deque()
        self.buffer_size = 0
        self.lock = threading.Lock()
        self.flush_timer = None
        self.flush_callbacks: List[Callable] = []
        
    def add_message(self, message: Any, priority: int = 0):
        """Add a message to the buffer."""
        with self.lock:
            if self.buffer_size >= self.config.max_buffer_size:
                # Remove oldest message if buffer is full
                if self.buffer:
                    old_msg = self.buffer.popleft()
                    self.buffer_size -= len(str(old_msg))
            
            # Add new message with priority
            self.buffer.append((priority, time.time(), message))
            self.buffer_size += len(str(message))
            
            # Sort by priority (higher priority first)
            self.buffer = deque(sorted(self.buffer, key=lambda x: (-x[0], x[1])))
            
            # Schedule flush if not already scheduled
            if self.flush_timer is None:
                self.flush_timer = threading.Timer(self.config.flush_interval, self._flush_buffer)
                self.flush_timer.start()
    
    def _flush_buffer(self):
        """Flush buffered messages."""
        with self.lock:
            self.flush_timer = None
            
            if not self.buffer:
                return
            
            # Get all messages
            messages = [msg[2] for msg in self.buffer]
            self.buffer.clear()
            self.buffer_size = 0
            
            # Call flush callbacks
            for callback in self.flush_callbacks:
                try:
                    callback(messages)
                except Exception as e:
                    print(f"Error in flush callback: {e}")
    
    def add_flush_callback(self, callback: Callable):
        """Add a callback to be called when buffer is flushed."""
        self.flush_callbacks.append(callback)
    
    def force_flush(self):
        """Force flush the buffer immediately."""
        if self.flush_timer:
            self.flush_timer.cancel()
        self._flush_buffer()
    
    def get_stats(self) -> Dict:
        """Get buffer statistics."""
        with self.lock:
            return {
                'buffer_size': self.buffer_size,
                'message_count': len(self.buffer),
                'max_buffer_size': self.config.max_buffer_size
            }


class ZeroCopyBuffer:
    """Handles zero-copy message passing using memory mapping."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.shared_memory = None
        self.memory_map = None
        self.buffer_offset = 0
        self.lock = threading.Lock()
        
        if config.use_memory_mapping:
            self._initialize_shared_memory()
    
    def _initialize_shared_memory(self):
        """Initialize shared memory for zero-copy operations."""
        try:
            # Create a temporary file for memory mapping
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b'\x00' * self.config.shared_memory_size)
            temp_file.flush()
            
            # Memory map the file
            self.shared_memory = open(temp_file.name, 'r+b')
            self.memory_map = mmap.mmap(
                self.shared_memory.fileno(),
                self.config.shared_memory_size,
                access=mmap.ACCESS_WRITE
            )
            
            # Clean up temp file
            import os
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"Failed to initialize shared memory: {e}")
            self.config.use_memory_mapping = False
    
    def write_message(self, data: bytes) -> Optional[Tuple[int, int]]:
        """Write message to shared memory and return offset and size."""
        if not self.config.use_memory_mapping or not self.memory_map:
            return None
        
        with self.lock:
            message_size = len(data)
            
            # Check if we have enough space
            if self.buffer_offset + message_size > self.config.shared_memory_size:
                # Reset buffer if full
                self.buffer_offset = 0
            
            # Write message
            offset = self.buffer_offset
            self.memory_map.seek(offset)
            self.memory_map.write(data)
            self.buffer_offset += message_size
            
            return (offset, message_size)
    
    def read_message(self, offset: int, size: int) -> Optional[bytes]:
        """Read message from shared memory."""
        if not self.config.use_memory_mapping or not self.memory_map:
            return None
        
        try:
            self.memory_map.seek(offset)
            return self.memory_map.read(size)
        except Exception as e:
            print(f"Error reading from shared memory: {e}")
            return None
    
    def cleanup(self):
        """Clean up shared memory resources."""
        if self.memory_map:
            self.memory_map.close()
        if self.shared_memory:
            self.shared_memory.close()


class AsyncSocketWrapper:
    """Async wrapper for socket operations."""
    
    def __init__(self, sock: socket.socket, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.socket = sock
        self.loop = loop or asyncio.get_event_loop()
        self._reader = None
        self._writer = None
        
    async def connect(self, host: str, port: int):
        """Async connect."""
        try:
            self._reader, self._writer = await asyncio.open_connection(host, port)
            return True
        except Exception as e:
            print(f"Async connect error: {e}")
            return False
    
    async def send(self, data: bytes):
        """Async send."""
        if self._writer:
            self._writer.write(data)
            await self._writer.drain()
        else:
            # Fallback to synchronous send
            self.socket.send(data)
    
    async def recv(self, size: int = 4096) -> bytes:
        """Async receive."""
        if self._reader:
            return await self._reader.read(size)
        else:
            # Fallback to synchronous recv
            return self.socket.recv(size)
    
    async def close(self):
        """Async close."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
        else:
            self.socket.close()


class PerformanceHandler:
    """Main performance handler that coordinates all performance features."""
    
    def __init__(self, config: PerformanceConfig):
        self.config = config
        self.connection_pool = ConnectionPool(config) if config.enable_multiplexing else None
        self.message_buffer = MessageBuffer(config) if config.enable_buffering else None
        self.zero_copy_buffer = ZeroCopyBuffer(config) if config.enable_zero_copy else None
        self.loop = None
        
        # Initialize async event loop if enabled
        if config.enable_async:
            self._initialize_async_loop()
    
    def _initialize_async_loop(self):
        """Initialize async event loop with optional uvloop."""
        try:
            if self.config.use_uvloop and UVLOOP_AVAILABLE:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
        except Exception as e:
            print(f"Failed to initialize async loop: {e}")
            self.config.enable_async = False
    
    def add_connection_to_pool(self, sock: socket.socket, weight: float = 1.0) -> bool:
        """Add connection to the multiplexing pool."""
        if self.connection_pool:
            return self.connection_pool.add_connection(sock, weight)
        return False
    
    def get_connection_from_pool(self) -> Optional[socket.socket]:
        """Get connection from the multiplexing pool."""
        if self.connection_pool:
            return self.connection_pool.get_connection()
        return None
    
    def buffer_message(self, message: Any, priority: int = 0):
        """Buffer a message for later sending."""
        if self.message_buffer:
            self.message_buffer.add_message(message, priority)
    
    def add_buffer_flush_callback(self, callback: Callable):
        """Add callback for when message buffer is flushed."""
        if self.message_buffer:
            self.message_buffer.add_flush_callback(callback)
    
    def force_buffer_flush(self):
        """Force flush the message buffer."""
        if self.message_buffer:
            self.message_buffer.force_flush()
    
    def write_zero_copy(self, data: bytes) -> Optional[Tuple[int, int]]:
        """Write data using zero-copy buffer."""
        if self.zero_copy_buffer:
            return self.zero_copy_buffer.write_message(data)
        return None
    
    def read_zero_copy(self, offset: int, size: int) -> Optional[bytes]:
        """Read data using zero-copy buffer."""
        if self.zero_copy_buffer:
            return self.zero_copy_buffer.read_message(offset, size)
        return None
    
    async def async_send(self, sock: socket.socket, data: bytes) -> bool:
        """Send data asynchronously."""
        if not self.config.enable_async:
            return False
        
        try:
            wrapper = AsyncSocketWrapper(sock, self.loop)
            await wrapper.send(data)
            return True
        except Exception as e:
            print(f"Async send error: {e}")
            return False
    
    async def async_recv(self, sock: socket.socket, size: int = 4096) -> Optional[bytes]:
        """Receive data asynchronously."""
        if not self.config.enable_async:
            return None
        
        try:
            wrapper = AsyncSocketWrapper(sock, self.loop)
            return await wrapper.recv(size)
        except Exception as e:
            print(f"Async recv error: {e}")
            return None
    
    def create_stream_reader(self, sock: socket.socket, chunk_size: int = None) -> 'StreamReader':
        """Create a stream reader for large data."""
        chunk_size = chunk_size or self.config.chunk_size
        return StreamReader(sock, chunk_size, self.config.max_stream_size)
    
    def create_stream_writer(self, sock: socket.socket, chunk_size: int = None) -> 'StreamWriter':
        """Create a stream writer for large data."""
        chunk_size = chunk_size or self.config.chunk_size
        return StreamWriter(sock, chunk_size)
    
    def get_stats(self) -> Dict:
        """Get performance statistics."""
        stats = {
            'async_enabled': self.config.enable_async,
            'multiplexing_enabled': self.config.enable_multiplexing,
            'buffering_enabled': self.config.enable_buffering,
            'zero_copy_enabled': self.config.enable_zero_copy
        }
        
        if self.connection_pool:
            stats['connection_pool'] = {
                'active_connections': len(self.connection_pool.connections),
                'max_connections': self.config.max_connections_per_pool
            }
        
        if self.message_buffer:
            stats['message_buffer'] = self.message_buffer.get_stats()
        
        return stats
    
    def cleanup(self):
        """Clean up all resources."""
        if self.zero_copy_buffer:
            self.zero_copy_buffer.cleanup()
        
        if self.connection_pool:
            self.connection_pool.cleanup_expired_connections()
        
        if self.loop and not self.loop.is_closed():
            self.loop.close()


class StreamReader:
    """Stream reader for handling large data in chunks."""
    
    def __init__(self, sock: socket.socket, chunk_size: int, max_size: int):
        self.socket = sock
        self.chunk_size = chunk_size
        self.max_size = max_size
        self.total_read = 0
        self.buffer = io.BytesIO()
    
    def read_chunk(self) -> Optional[bytes]:
        """Read a single chunk of data."""
        if self.total_read >= self.max_size:
            raise ValueError(f"Stream size limit exceeded: {self.max_size}")
        
        chunk = self.socket.recv(min(self.chunk_size, self.max_size - self.total_read))
        if chunk:
            self.total_read += len(chunk)
            self.buffer.write(chunk)
        
        return chunk
    
    def read_all(self) -> bytes:
        """Read all available data."""
        while True:
            chunk = self.read_chunk()
            if not chunk:
                break
        
        return self.buffer.getvalue()
    
    def read_until_size(self, target_size: int) -> bytes:
        """Read until a specific size is reached."""
        while self.total_read < target_size:
            chunk = self.read_chunk()
            if not chunk:
                break
        
        return self.buffer.getvalue()
    
    def get_progress(self) -> float:
        """Get reading progress as percentage."""
        return (self.total_read / self.max_size) * 100 if self.max_size > 0 else 0


class StreamWriter:
    """Stream writer for handling large data in chunks."""
    
    def __init__(self, sock: socket.socket, chunk_size: int):
        self.socket = sock
        self.chunk_size = chunk_size
        self.total_written = 0
    
    def write_chunk(self, data: bytes) -> int:
        """Write a single chunk of data."""
        written = 0
        for i in range(0, len(data), self.chunk_size):
            chunk = data[i:i + self.chunk_size]
            written += self.socket.send(chunk)
        
        self.total_written += written
        return written
    
    def write_stream(self, data_stream: io.IOBase) -> int:
        """Write data from a stream."""
        total_written = 0
        
        while True:
            chunk = data_stream.read(self.chunk_size)
            if not chunk:
                break
            
            written = self.socket.send(chunk)
            total_written += written
            self.total_written += written
        
        return total_written
    
    def write_file(self, file_path: str) -> int:
        """Write data from a file."""
        with open(file_path, 'rb') as f:
            return self.write_stream(f)


@contextlib.contextmanager
def performance_context(config: PerformanceConfig):
    """Context manager for performance features."""
    handler = PerformanceHandler(config)
    try:
        yield handler
    finally:
        handler.cleanup()
