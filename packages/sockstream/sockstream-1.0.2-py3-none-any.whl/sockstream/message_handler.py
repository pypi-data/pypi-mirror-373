import json
import gzip
import zlib
import base64
import time
import uuid
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class MessageType(Enum):
    """Types of messages that can be sent."""
    JSON = "json"
    BINARY = "binary"
    COMPRESSED = "compressed"
    BATCH = "batch"


class CompressionType(Enum):
    """Types of compression available."""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"


@dataclass
class Message:
    """Represents a message with metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event: str = ""
    data: Any = None
    room: Optional[str] = None
    message_type: MessageType = MessageType.JSON
    compression: CompressionType = CompressionType.NONE
    timestamp: float = field(default_factory=time.time)
    requires_ack: bool = False
    ack_received: bool = False
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0  # Higher number = higher priority


@dataclass
class MessageConfig:
    """Configuration for message handling."""
    enable_compression: bool = True
    compression_threshold: int = 1024  # Only compress messages larger than this
    default_compression: CompressionType = CompressionType.GZIP
    enable_batching: bool = True
    batch_size: int = 10
    batch_timeout: float = 0.1  # seconds
    enable_acknowledgment: bool = True
    ack_timeout: float = 5.0  # seconds
    max_queue_size: int = 1000
    enable_binary: bool = True
    binary_encoding: str = "base64"


class MessageHandler:
    """
    Handles message processing, compression, batching, and acknowledgment.
    """
    
    def __init__(self, config: MessageConfig):
        self.config = config
        self.message_queue: List[Message] = []
        self.pending_acks: Dict[str, Message] = {}
        self.batch_buffer: List[Message] = []
        self.batch_timer: Optional[threading.Timer] = None
        self.batch_lock = threading.Lock()
        self.ack_callbacks: Dict[str, Callable] = {}
        
    def create_message(self, event: str, data: Any = None, room: Optional[str] = None, 
                      requires_ack: bool = False, priority: int = 0) -> Message:
        """Create a new message with appropriate metadata."""
        return Message(
            event=event,
            data=data,
            room=room,
            requires_ack=requires_ack,
            priority=priority
        )
    
    def compress_data(self, data: Union[str, bytes], compression_type: CompressionType) -> bytes:
        """Compress data using the specified compression method."""
        if compression_type == CompressionType.NONE:
            return data.encode('utf-8') if isinstance(data, str) else data
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if compression_type == CompressionType.GZIP:
            return gzip.compress(data)
        elif compression_type == CompressionType.DEFLATE:
            return zlib.compress(data)
        else:
            return data
    
    def decompress_data(self, data: bytes, compression_type: CompressionType) -> bytes:
        """Decompress data using the specified compression method."""
        if compression_type == CompressionType.NONE:
            return data
        
        try:
            if compression_type == CompressionType.GZIP:
                return gzip.decompress(data)
            elif compression_type == CompressionType.DEFLATE:
                return zlib.decompress(data)
        except Exception:
            return data
        
        return data
    
    def encode_binary(self, data: bytes) -> str:
        """Encode binary data to string for transmission."""
        if self.config.binary_encoding == "base64":
            return base64.b64encode(data).decode('utf-8')
        else:
            return data.decode('utf-8', errors='ignore')
    
    def decode_binary(self, data: str) -> bytes:
        """Decode binary data from string."""
        if self.config.binary_encoding == "base64":
            return base64.b64decode(data.encode('utf-8'))
        else:
            return data.encode('utf-8')
    
    def should_compress(self, data: Union[str, bytes]) -> bool:
        """Determine if data should be compressed."""
        if not self.config.enable_compression:
            return False
        
        data_size = len(data) if isinstance(data, bytes) else len(data.encode('utf-8'))
        return data_size > self.config.compression_threshold
    
    def serialize_message(self, message: Message) -> str:
        """Serialize a message to string format for transmission."""
        # Determine if compression is needed
        if message.message_type == MessageType.BINARY:
            # Binary data - encode and optionally compress
            if isinstance(message.data, bytes):
                if self.should_compress(message.data):
                    compressed_data = self.compress_data(message.data, self.config.default_compression)
                    message.compression = self.config.default_compression
                    message.data = self.encode_binary(compressed_data)
                else:
                    message.data = self.encode_binary(message.data)
            else:
                message.data = str(message.data)
        
        elif message.message_type == MessageType.JSON:
            # JSON data - convert to string and optionally compress
            json_str = json.dumps(message.data)
            if self.should_compress(json_str):
                compressed_data = self.compress_data(json_str, self.config.default_compression)
                message.compression = self.config.default_compression
                message.data = self.encode_binary(compressed_data)
        
        # Create the final message structure
        serialized = {
            'id': message.id,
            'event': message.event,
            'data': message.data,
            'room': message.room,
            'message_type': message.message_type.value,
            'compression': message.compression.value,
            'timestamp': message.timestamp,
            'requires_ack': message.requires_ack
        }
        
        return json.dumps(serialized) + '\n'
    
    def deserialize_message(self, message_str: str) -> Message:
        """Deserialize a message from string format."""
        try:
            data = json.loads(message_str)
            
            # Create message object
            message = Message(
                id=data.get('id', str(uuid.uuid4())),
                event=data.get('event', ''),
                data=data.get('data'),
                room=data.get('room'),
                message_type=MessageType(data.get('message_type', 'json')),
                compression=CompressionType(data.get('compression', 'none')),
                timestamp=data.get('timestamp', time.time()),
                requires_ack=data.get('requires_ack', False)
            )
            
            # Handle decompression
            if message.compression != CompressionType.NONE:
                if message.message_type == MessageType.BINARY:
                    # Binary data - decode and decompress
                    decoded_data = self.decode_binary(message.data)
                    decompressed_data = self.decompress_data(decoded_data, message.compression)
                    message.data = decompressed_data
                else:
                    # JSON data - decompress and parse
                    decoded_data = self.decode_binary(message.data)
                    decompressed_data = self.decompress_data(decoded_data, message.compression)
                    try:
                        message.data = json.loads(decompressed_data.decode('utf-8'))
                    except:
                        message.data = decompressed_data.decode('utf-8', errors='ignore')
            
            return message
            
        except Exception as e:
            # Return error message
            return Message(
                event='error',
                data=f'Failed to deserialize message: {str(e)}',
                message_type=MessageType.JSON
            )
    
    def add_to_batch(self, message: Message) -> bool:
        """Add a message to the current batch."""
        if not self.config.enable_batching:
            return False
        
        with self.batch_lock:
            self.batch_buffer.append(message)
            
            # Start batch timer if this is the first message
            if len(self.batch_buffer) == 1:
                self.batch_timer = threading.Timer(self.config.batch_timeout, self.flush_batch)
                self.batch_timer.start()
            
            # Flush if batch is full
            if len(self.batch_buffer) >= self.config.batch_size:
                self.flush_batch()
                return True
        
        return False
    
    def flush_batch(self):
        """Flush the current batch of messages."""
        with self.batch_lock:
            if not self.batch_buffer:
                return
            
            # Cancel timer if it's still running
            if self.batch_timer:
                self.batch_timer.cancel()
                self.batch_timer = None
            
            # Create batch message
            batch_message = Message(
                event='batch',
                data=[msg.data for msg in self.batch_buffer],
                message_type=MessageType.BATCH
            )
            
            # Clear buffer
            self.batch_buffer.clear()
            
            # Return the batch message for processing
            return batch_message
    
    def queue_message(self, message: Message) -> bool:
        """Add a message to the queue."""
        if len(self.message_queue) >= self.config.max_queue_size:
            return False
        
        # Sort by priority (higher priority first)
        self.message_queue.append(message)
        self.message_queue.sort(key=lambda x: x.priority, reverse=True)
        return True
    
    def get_next_message(self) -> Optional[Message]:
        """Get the next message from the queue."""
        if not self.message_queue:
            return None
        
        return self.message_queue.pop(0)
    
    def add_ack_callback(self, message_id: str, callback: Callable):
        """Add a callback for when a message is acknowledged."""
        self.ack_callbacks[message_id] = callback
    
    def handle_ack(self, message_id: str):
        """Handle acknowledgment of a message."""
        if message_id in self.pending_acks:
            message = self.pending_acks.pop(message_id)
            message.ack_received = True
            
            # Call the callback if it exists
            if message_id in self.ack_callbacks:
                callback = self.ack_callbacks.pop(message_id)
                try:
                    callback(message)
                except Exception:
                    pass
    
    def mark_for_ack(self, message: Message):
        """Mark a message as requiring acknowledgment."""
        if message.requires_ack:
            self.pending_acks[message.id] = message
    
    def cleanup_expired_acks(self, timeout: float = None):
        """Clean up expired acknowledgments."""
        if timeout is None:
            timeout = self.config.ack_timeout
        
        current_time = time.time()
        expired_ids = []
        
        for msg_id, message in self.pending_acks.items():
            if current_time - message.timestamp > timeout:
                expired_ids.append(msg_id)
        
        for msg_id in expired_ids:
            message = self.pending_acks.pop(msg_id)
            if msg_id in self.ack_callbacks:
                callback = self.ack_callbacks.pop(msg_id)
                try:
                    callback(message)  # Call with expired message
                except Exception:
                    pass
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get statistics about the message queue."""
        return {
            'queue_size': len(self.message_queue),
            'pending_acks': len(self.pending_acks),
            'batch_buffer_size': len(self.batch_buffer),
            'total_ack_callbacks': len(self.ack_callbacks)
        }
