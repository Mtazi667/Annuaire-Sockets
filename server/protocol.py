
import json
import socket

ENCODING = "utf-8"
DELIM = "\n"  # line-delimited JSON

def send_json(sock: socket.socket, obj: dict) -> None:
    data = json.dumps(obj, ensure_ascii=False).encode(ENCODING) + DELIM.encode(ENCODING)
    sock.sendall(data)

def recv_json(sock: socket.socket) -> dict:
    """Receive a single JSON object delimited by newline."""
    buf = bytearray()
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
        if b"\n" in chunk:
            break
    # handle multiple lines (take first)
    line = bytes(buf).split(b"\n")[0]
    if not line:
        return {}
    return json.loads(line.decode(ENCODING))
