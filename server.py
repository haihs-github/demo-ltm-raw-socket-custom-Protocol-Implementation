# server.py
import socket
import struct
import time
from protocol import parse_packet, create_packet

HOST = "0.0.0.0"
PORT = 9999
BUF = 65535

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"[SERVER] UDP server listening on {HOST}:{PORT}\n")

while True:
    data, addr = sock.recvfrom(BUF)
    hexs = data.hex()
    print(f"[RECV] From {addr} | {len(data)} bytes | raw={hexs}")

    # Try decode as custom protocol (needs at least 8 bytes)
    if len(data) >= 8:
        try:
            version, msg_type, timestamp, payload = parse_packet(data)
            # check length consistency: parse_packet used struct.unpack; ensure payload length matches
            expected_len = len(payload.encode('utf-8', 'ignore'))
            # Note: parse_packet already slices by declared length, so if declared length mismatch,
            # slicing will produce shorter payload but we still treat as custom if declared length <= len(data)-8
            declared_len = struct.unpack("!BBIH", data[:8])[3]
            if declared_len == len(data) - 8:
                ts_readable = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                print(f" -> [CUSTOM] v={version} type={msg_type} time={ts_readable} msg='{payload}'")
                # If text message (type 1), send ACK (custom) back to sender
                if msg_type == 1:
                    ack = create_packet(2, "OK")
                    sock.sendto(ack, addr)
                    print(f"    Sent ACK to {addr}")
                continue
            else:
                # Declared length doesn't match actual remaining bytes -> treat as raw fallback
                print("    Declared length doesn't match actual payload len -> treat as RAW")
        except struct.error:
            # unpack failed -> not custom format
            pass
        except Exception as e:
            # any other parse issue -> ignore and fallback to raw
            pass

    # Fallback: treat as basic/raw UDP message (text)
    try:
        text = data.decode(errors="ignore")
        print(f" -> [BASIC] message: '{text}'")
        # Optionally respond with an ACK basic
        # sock.sendto(b"ACK_BASIC", addr)
    except Exception as e:
        print(" -> [UNKNOWN FORMAT] could not decode as text")
