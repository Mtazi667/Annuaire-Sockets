import socket, os, uuid
from typing import Dict, Any, Optional

# ✅ Import absolu depuis le package frère "server"
from server.protocol import send_json, recv_json  # reuse protocol

HOST = os.environ.get("ANNUAIRE_HOST", "127.0.0.1")
PORT = int(os.environ.get("ANNUAIRE_PORT", "5050"))

def call(action: str, payload: Dict[str, Any] = None, admin_token: Optional[str] = None) -> Dict[str, Any]:
    if payload is None:
        payload = {}
    req = {
        "action": action,
        "payload": payload,
        "auth": {"admin_token": admin_token} if admin_token else None,
        "request_id": str(uuid.uuid4())
    }
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0)
        try:
            s.connect((HOST, PORT))
        except OSError:
            return {
                "ok": False,
                "data": None,
                "error": {"code": "CONNECTION", "message": "Serveur indisponible"},
                "request_id": req["request_id"]
            }
        send_json(s, req)
        resp = recv_json(s)
        return resp or {
            "ok": False,
            "data": None,
            "error": {"code": "PROTO", "message": "Reponse vide"},
            "request_id": req["request_id"]
        }
