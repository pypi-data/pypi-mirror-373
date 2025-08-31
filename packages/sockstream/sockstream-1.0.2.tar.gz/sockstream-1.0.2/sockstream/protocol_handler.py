import socket
import json
import struct
import base64
import hashlib
from typing import Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import google.protobuf.message
    PROTOBUF_AVAILABLE = True
except ImportError:
    PROTOBUF_AVAILABLE = False


class ProtocolType(Enum):
    """Supported protocol types."""
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"


class MessageFormat(Enum):
    """Supported message formats."""
    JSON = "json"
    MSGPACK = "msgpack"
    PROTOBUF = "protobuf"
    RAW = "raw"


class FramingType(Enum):
    """Supported message framing types."""
    LENGTH_PREFIXED = "length_prefixed"
    DELIMITER_BASED = "delimiter_based"
    WEBSOCKET_FRAME = "websocket_frame"
    NONE = "none"


@dataclass
class ProtocolConfig:
    """Configuration for protocol handling."""
    protocol_type: ProtocolType = ProtocolType.TCP
    message_format: MessageFormat = MessageFormat.JSON
    framing_type: FramingType = FramingType.LENGTH_PREFIXED
    delimiter: str = '\n'
    max_message_size: int = 1024 * 1024  # 1MB
    enable_websocket_compression: bool = True
    websocket_mask_key: bool = True
    udp_buffer_size: int = 8192
    tcp_keepalive: bool = True
    tcp_nodelay: bool = True


class ProtocolHandler:
    """
    Handles different protocols, message formats, and framing methods.
    """
    
    def __init__(self, config: ProtocolConfig):
        self.config = config
        self.buffer = b''
        self.websocket_handshake_complete = False
        
    def create_socket(self, protocol_type: ProtocolType = None) -> socket.socket:
        """Create a socket for the specified protocol."""
        protocol = protocol_type or self.config.protocol_type
        
        if protocol == ProtocolType.TCP:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.config.tcp_nodelay:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if self.config.tcp_keepalive:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            return sock
        
        elif protocol == ProtocolType.UDP:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.config.udp_buffer_size)
            return sock
        
        elif protocol == ProtocolType.WEBSOCKET:
            # WebSocket uses TCP socket initially
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.config.tcp_nodelay:
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            return sock
        
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
    
    def serialize_message(self, data: Any) -> bytes:
        """Serialize data using the configured message format."""
        if self.config.message_format == MessageFormat.JSON:
            return json.dumps(data).encode('utf-8')
        
        elif self.config.message_format == MessageFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ImportError("MessagePack not available. Install with: pip install msgpack")
            return msgpack.packb(data)
        
        elif self.config.message_format == MessageFormat.PROTOBUF:
            if not PROTOBUF_AVAILABLE:
                raise ImportError("Protocol Buffers not available. Install with: pip install protobuf")
            if hasattr(data, 'SerializeToString'):
                return data.SerializeToString()
            else:
                raise ValueError("Data must be a protobuf message")
        
        elif self.config.message_format == MessageFormat.RAW:
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode('utf-8')
            else:
                return str(data).encode('utf-8')
        
        else:
            raise ValueError(f"Unsupported message format: {self.config.message_format}")
    
    def deserialize_message(self, data: bytes) -> Any:
        """Deserialize data using the configured message format."""
        if self.config.message_format == MessageFormat.JSON:
            return json.loads(data.decode('utf-8'))
        
        elif self.config.message_format == MessageFormat.MSGPACK:
            if not MSGPACK_AVAILABLE:
                raise ImportError("MessagePack not available. Install with: pip install msgpack")
            return msgpack.unpackb(data, raw=False)
        
        elif self.config.message_format == MessageFormat.PROTOBUF:
            if not PROTOBUF_AVAILABLE:
                raise ImportError("Protocol Buffers not available. Install with: pip install protobuf")
            # This would need a specific protobuf message class
            # For now, return raw bytes
            return data
        
        elif self.config.message_format == MessageFormat.RAW:
            return data
        
        else:
            raise ValueError(f"Unsupported message format: {self.config.message_format}")
    
    def frame_message(self, data: bytes) -> bytes:
        """Frame a message using the configured framing method."""
        if self.config.framing_type == FramingType.LENGTH_PREFIXED:
            # 4-byte length prefix (big-endian)
            length = len(data)
            return struct.pack('>I', length) + data
        
        elif self.config.framing_type == FramingType.DELIMITER_BASED:
            # Add delimiter to end of message
            delimiter = self.config.delimiter.encode('utf-8')
            return data + delimiter
        
        elif self.config.framing_type == FramingType.WEBSOCKET_FRAME:
            return self._create_websocket_frame(data)
        
        elif self.config.framing_type == FramingType.NONE:
            return data
        
        else:
            raise ValueError(f"Unsupported framing type: {self.config.framing_type}")
    
    def unframe_message(self, data: bytes) -> List[bytes]:
        """Extract complete messages from framed data."""
        messages = []
        
        if self.config.framing_type == FramingType.LENGTH_PREFIXED:
            messages = self._unframe_length_prefixed(data)
        
        elif self.config.framing_type == FramingType.DELIMITER_BASED:
            messages = self._unframe_delimiter_based(data)
        
        elif self.config.framing_type == FramingType.WEBSOCKET_FRAME:
            messages = self._unframe_websocket(data)
        
        elif self.config.framing_type == FramingType.NONE:
            if data:
                messages = [data]
        
        return messages
    
    def _unframe_length_prefixed(self, data: bytes) -> List[bytes]:
        """Extract length-prefixed messages."""
        messages = []
        self.buffer += data
        
        while len(self.buffer) >= 4:
            # Read message length
            length = struct.unpack('>I', self.buffer[:4])[0]
            
            if length > self.config.max_message_size:
                raise ValueError(f"Message too large: {length} bytes")
            
            # Check if we have the complete message
            if len(self.buffer) >= 4 + length:
                message = self.buffer[4:4 + length]
                messages.append(message)
                self.buffer = self.buffer[4 + length:]
            else:
                break
        
        return messages
    
    def _unframe_delimiter_based(self, data: bytes) -> List[bytes]:
        """Extract delimiter-based messages."""
        messages = []
        self.buffer += data
        delimiter = self.config.delimiter.encode('utf-8')
        
        while delimiter in self.buffer:
            # Find delimiter position
            pos = self.buffer.find(delimiter)
            
            # Extract message
            message = self.buffer[:pos]
            if message:  # Don't add empty messages
                messages.append(message)
            
            # Remove message and delimiter from buffer
            self.buffer = self.buffer[pos + len(delimiter):]
        
        return messages
    
    def _unframe_websocket(self, data: bytes) -> List[bytes]:
        """Extract WebSocket frames."""
        messages = []
        self.buffer += data
        
        while len(self.buffer) >= 2:
            # Parse WebSocket frame header
            first_byte = self.buffer[0]
            second_byte = self.buffer[1]
            
            fin = (first_byte & 0x80) != 0
            opcode = first_byte & 0x0F
            masked = (second_byte & 0x80) != 0
            payload_length = second_byte & 0x7F
            
            # Determine actual payload length
            if payload_length == 126:
                if len(self.buffer) < 4:
                    break
                payload_length = struct.unpack('>H', self.buffer[2:4])[0]
                header_length = 4
            elif payload_length == 127:
                if len(self.buffer) < 10:
                    break
                payload_length = struct.unpack('>Q', self.buffer[2:10])[0]
                header_length = 10
            else:
                header_length = 2
            
            # Check if we have the complete frame
            total_length = header_length + payload_length
            if masked:
                total_length += 4  # Mask key
            
            if len(self.buffer) < total_length:
                break
            
            # Extract frame
            frame = self.buffer[:total_length]
            self.buffer = self.buffer[total_length:]
            
            # Handle different opcodes
            if opcode == 0x1:  # Text frame
                payload = self._extract_websocket_payload(frame, masked)
                messages.append(payload)
            elif opcode == 0x2:  # Binary frame
                payload = self._extract_websocket_payload(frame, masked)
                messages.append(payload)
            elif opcode == 0x8:  # Close frame
                # Handle close frame
                pass
            elif opcode == 0x9:  # Ping frame
                # Handle ping frame
                pass
            elif opcode == 0xA:  # Pong frame
                # Handle pong frame
                pass
        
        return messages
    
    def _extract_websocket_payload(self, frame: bytes, masked: bool) -> bytes:
        """Extract payload from WebSocket frame."""
        if len(frame) < 2:
            return b''
        
        payload_length = frame[1] & 0x7F
        offset = 2
        
        if payload_length == 126:
            payload_length = struct.unpack('>H', frame[2:4])[0]
            offset = 4
        elif payload_length == 127:
            payload_length = struct.unpack('>Q', frame[2:10])[0]
            offset = 10
        
        if masked:
            mask_key = frame[offset:offset + 4]
            offset += 4
            payload = frame[offset:offset + payload_length]
            
            # Unmask payload
            unmasked = bytearray(payload_length)
            for i in range(payload_length):
                unmasked[i] = payload[i] ^ mask_key[i % 4]
            return bytes(unmasked)
        else:
            return frame[offset:offset + payload_length]
    
    def _create_websocket_frame(self, data: bytes) -> bytes:
        """Create a WebSocket frame."""
        length = len(data)
        frame = bytearray()
        
        # First byte: FIN=1, RSV=0, Opcode=2 (binary)
        frame.append(0x82)
        
        # Second byte: MASK=0, Payload length
        if length < 126:
            frame.append(length)
        elif length < 65536:
            frame.append(126)
            frame.extend(struct.pack('>H', length))
        else:
            frame.append(127)
            frame.extend(struct.pack('>Q', length))
        
        # Add payload
        frame.extend(data)
        
        return bytes(frame)
    
    def handle_websocket_handshake(self, request: str) -> str:
        """Handle WebSocket handshake and return response."""
        lines = request.split('\n')
        headers = {}
        
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                headers[key.strip()] = value.strip()
        
        # Extract WebSocket key
        ws_key = headers.get('Sec-WebSocket-Key', '')
        
        if not ws_key:
            return self._create_http_response(400, 'Bad Request')
        
        # Generate accept key
        ws_accept = base64.b64encode(
            hashlib.sha1((ws_key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()
        ).decode()
        
        # Create response
        response = (
            'HTTP/1.1 101 Switching Protocols\r\n'
            'Upgrade: websocket\r\n'
            'Connection: Upgrade\r\n'
            f'Sec-WebSocket-Accept: {ws_accept}\r\n'
            '\r\n'
        )
        
        self.websocket_handshake_complete = True
        return response
    
    def _create_http_response(self, status_code: int, status_text: str) -> str:
        """Create an HTTP response."""
        return (
            f'HTTP/1.1 {status_code} {status_text}\r\n'
            'Content-Type: text/plain\r\n'
            'Content-Length: 0\r\n'
            '\r\n'
        )
    
    def send_message(self, sock: socket.socket, data: Any, address: Tuple[str, int] = None) -> bool:
        """Send a message using the configured protocol."""
        try:
            # Serialize the message
            serialized = self.serialize_message(data)
            
            # Frame the message
            framed = self.frame_message(serialized)
            
            # Send based on protocol
            if self.config.protocol_type == ProtocolType.UDP:
                if address:
                    sock.sendto(framed, address)
                else:
                    sock.send(framed)
            else:
                sock.send(framed)
            
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def receive_message(self, sock: socket.socket, address: Tuple[str, int] = None) -> List[Any]:
        """Receive messages using the configured protocol."""
        try:
            # Receive data based on protocol
            if self.config.protocol_type == ProtocolType.UDP:
                if address:
                    data, addr = sock.recvfrom(self.config.udp_buffer_size)
                else:
                    data = sock.recv(self.config.udp_buffer_size)
            else:
                data = sock.recv(4096)
            
            if not data:
                return []
            
            # Handle WebSocket handshake
            if (self.config.protocol_type == ProtocolType.WEBSOCKET and 
                not self.websocket_handshake_complete):
                request = data.decode('utf-8', errors='ignore')
                if 'GET' in request and 'Upgrade: websocket' in request:
                    response = self.handle_websocket_handshake(request)
                    sock.send(response.encode('utf-8'))
                    return []
            
            # Unframe messages
            raw_messages = self.unframe_message(data)
            
            # Deserialize messages
            messages = []
            for raw_msg in raw_messages:
                try:
                    deserialized = self.deserialize_message(raw_msg)
                    messages.append(deserialized)
                except Exception as e:
                    print(f"Error deserializing message: {e}")
            
            return messages
            
        except Exception as e:
            print(f"Error receiving message: {e}")
            return []
    
    def create_server_socket(self, host: str, port: int) -> socket.socket:
        """Create a server socket for the configured protocol."""
        sock = self.create_socket()
        
        if self.config.protocol_type in [ProtocolType.TCP, ProtocolType.WEBSOCKET]:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.listen(5)
        elif self.config.protocol_type == ProtocolType.UDP:
            sock.bind((host, port))
        
        return sock
    
    def create_client_socket(self) -> socket.socket:
        """Create a client socket for the configured protocol."""
        return self.create_socket()
    
    def connect_client(self, sock: socket.socket, host: str, port: int) -> bool:
        """Connect a client socket."""
        try:
            if self.config.protocol_type in [ProtocolType.TCP, ProtocolType.WEBSOCKET]:
                sock.connect((host, port))
                
                # Handle WebSocket handshake
                if self.config.protocol_type == ProtocolType.WEBSOCKET:
                    key = base64.b64encode(b'websocket-key').decode()
                    request = (
                        f'GET / HTTP/1.1\r\n'
                        f'Host: {host}:{port}\r\n'
                        f'Upgrade: websocket\r\n'
                        f'Connection: Upgrade\r\n'
                        f'Sec-WebSocket-Key: {key}\r\n'
                        f'Sec-WebSocket-Version: 13\r\n'
                        f'\r\n'
                    )
                    sock.send(request.encode('utf-8'))
                    
                    # Read response
                    response = sock.recv(1024).decode('utf-8')
                    if '101 Switching Protocols' in response:
                        self.websocket_handshake_complete = True
                    else:
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error connecting: {e}")
            return False
