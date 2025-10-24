
import socket, threading, uuid, os, traceback
from .protocol import send_json, recv_json
from .handlers import handle_request

HOST = os.environ.get("ANNUAIRE_HOST","127.0.0.1")
PORT = int(os.environ.get("ANNUAIRE_PORT","5050"))

def client_thread(conn, addr):
    try:
        req = recv_json(conn)
        if not req:
            return
        req.setdefault("request_id", str(uuid.uuid4()))
        resp = handle_request(req)
        send_json(conn, resp)
    except Exception:
        traceback.print_exc()
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()

def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(50)
        print(f"[server] listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=client_thread, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    serve()
