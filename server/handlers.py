
from typing import Dict, Any
from . import storage, auth

ADMIN_ACTIONS = {"add","delete","update","redlist","unredlist"}

def handle_request(req: Dict[str, Any]) -> Dict[str, Any]:
    action = req.get("action")
    payload = req.get("payload", {}) or {}
    request_id = req.get("request_id")

    def ok(data): return {"ok": True, "data": data, "error": None, "request_id": request_id}
    def err(code, message): return {"ok": False, "data": None, "error": {"code": code, "message": message}, "request_id": request_id}

    try:
        # Admin gate
        if action in ADMIN_ACTIONS:
            token = (req.get("auth") or {}).get("admin_token")
            if not auth.is_admin(token):
                return err("UNAUTHORIZED", "Admin requis")

        if action == "list_by_category":
            cat = payload.get("category")
            if cat not in ("professeur","auxiliaire","etudiant"):
                return err("VALIDATION", "category invalide")
            return ok(storage.list_by_category(cat))

        if action == "list_profs_by_domain":
            dom = payload.get("domain","")
            return ok(storage.list_profs_by_domain(dom))

        if action == "search":
            term = payload.get("term","")
            return ok(storage.search(term))

        if action == "add":
            member = payload.get("member",{})
            added = storage.add(member)
            return ok(added)

        if action == "delete":
            member_id = payload.get("id","")
            res = storage.delete(member_id)
            if not res:
                return err("NOT_FOUND","id introuvable")
            return ok({"deleted": True})

        if action == "update":
            member_id = payload.get("id","")
            patch = payload.get("patch",{})
            upd = storage.update(member_id, patch)
            if not upd:
                return err("NOT_FOUND","id introuvable")
            return ok(upd)

        if action == "redlist":
            member_id = payload.get("id","")
            upd = storage.redlist(member_id, True)
            if not upd:
                return err("NOT_FOUND","id introuvable")
            return ok(upd)

        if action == "unredlist":
            member_id = payload.get("id","")
            upd = storage.redlist(member_id, False)
            if not upd:
                return err("NOT_FOUND","id introuvable")
            return ok(upd)

        return err("UNKNOWN_ACTION", f"action inconnue: {action}")
    except ValueError as ve:
        return err("VALIDATION", str(ve))
    except Exception as e:
        return err("SERVER_ERROR", str(e))
