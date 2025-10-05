# client.py
import socket
import time
from protocol import create_packet, parse_packet

SERVER_IP = "127.0.0.1"   # đổi nếu server ở máy khác
SERVER_PORT = 9999
BUF = 65535

# Dùng 1 socket UDP datagram để gửi & nhận (ephemeral port được hệ điều hành cấp)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)  # timeout để chờ ACK

print("=== UDP DUAL CLIENT ===")
print(f"Sending to {SERVER_IP}:{SERVER_PORT}")
print("Type message and press ENTER. 'exit' to quit.\n")

while True:
    msg = input("You: ")
    if msg.lower() == "exit":
        break

    # 1) SEND BASIC UDP (plain text)
    try:
        sock.sendto(msg.encode('utf-8'), (SERVER_IP, SERVER_PORT))
        print("[UDP BASIC] Sent")
    except Exception as e:
        print("[ERR] sending basic UDP:", e)

    # small pause to separate packets visually in capture
    time.sleep(0.05)

    # 2) SEND CUSTOM UDP (header + payload)
    try:
        custom = create_packet(1, msg)  # type=1 => message
        sock.sendto(custom, (SERVER_IP, SERVER_PORT))
        print("[UDP CUSTOM] Sent (with header)")
    except Exception as e:
        print("[ERR] sending custom UDP:", e)

    # 3) Try to receive ACK (custom) coming back (server sends custom ACK)
    got_ack = False
    start = time.time()
    while True:
        try:
            data, addr = sock.recvfrom(BUF)
            # try parse as custom
            try:
                v, t, ts, payload = parse_packet(data)
                if t == 2:  # ACK
                    print(f"[ACK RECEIVED] {payload} (from {addr})")
                    got_ack = True
                    break
                else:
                    # might be some other custom message
                    print(f"[RECV] custom type={t} payload='{payload}'")
            except Exception:
                # not custom -> print raw
                try:
                    print("[RECV] raw data:", data.decode(errors="ignore"))
                except:
                    print("[RECV] raw bytes:", data.hex())
        except socket.timeout:
            break
        # safety timeout break
        if time.time() - start > 2.0:
            break

    if not got_ack:
        print("[NO ACK] No custom ACK received (timeout)\n")
    else:
        print()
