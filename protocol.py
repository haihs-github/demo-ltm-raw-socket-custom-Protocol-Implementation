# protocol.py
import struct
import time

# Cấu trúc packet: | Version (1B) | Type (1B) | Timestamp (4B) | Length (2B) | Payload (N bytes) |

def create_packet(msg_type: int, message: str, version: int = 1) -> bytes:
    """
    Tạo gói tin tùy chỉnh theo format trên.
    msg_type: 1 = message, 2 = ACK
    """
    payload = message.encode()
    timestamp = int(time.time())
    length = len(payload)
    header = struct.pack("!BBIH", version, msg_type, timestamp, length)
    return header + payload


def parse_packet(data: bytes):
    """
    Giải mã gói tin: trả về (version, msg_type, timestamp, payload)
    Nếu data quá ngắn hoặc không đúng format, có thể ném exception.
    """
    version, msg_type, timestamp, length = struct.unpack("!BBIH", data[:8])
    payload = data[8:8+length].decode(errors="ignore")
    return version, msg_type, timestamp, payload
