
from __future__ import annotations
import json, os, tempfile, uuid, threading, time
from typing import List, Dict, Any

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "members.json")
_lock = threading.RLock()

def _load() -> List[Dict[str, Any]]:
    with _lock:
        if not os.path.exists(DATA_PATH):
            return []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def _atomic_write(data: List[Dict[str, Any]]):
    with _lock:
        d = os.path.dirname(DATA_PATH)
        os.makedirs(d, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=d, prefix="members_", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_PATH)

def _now():
    import datetime
    return datetime.datetime.utcnow().isoformat()+"Z"

def validate_member(m: Dict[str, Any]) -> None:
    # Basic validation rules
    categorie = m.get("categorie")
    if categorie not in ("professeur", "auxiliaire", "etudiant"):
        raise ValueError("categorie invalide")
    if not m.get("prenom") or not m.get("nom") or not m.get("courriel"):
        raise ValueError("prenom/nom/courriel requis")
    if categorie == "etudiant" and not m.get("matricule"):
        raise ValueError("matricule requis pour etudiant")
    if categorie in ("professeur", "auxiliaire") and not m.get("telephone_bureau"):
        raise ValueError("telephone_bureau requis pour professeur/auxiliaire")

def list_by_category(category: str) -> List[Dict[str, Any]]:
    data = _load()
    out = []
    for m in data:
        if m.get("categorie") == category:
            if m.get("liste_rouge"):
                out.append({"nom": m["nom"], "prenom": m["prenom"], "liste_rouge": True})
            else:
                out.append(m)
    return out

def list_profs_by_domain(domain: str) -> List[Dict[str, Any]]:
    data = _load()
    out = []
    for m in data:
        if m.get("categorie") == "professeur" and m.get("domaine") == domain:
            if m.get("liste_rouge"):
                out.append({"nom": m["nom"], "prenom": m["prenom"], "liste_rouge": True})
            else:
                out.append(m)
    return out

def search(term: str) -> List[Dict[str, Any]]:
    term_lower = term.lower()
    data = _load()
    out = []
    for m in data:
        hay = " ".join([m.get("prenom",""), m.get("nom",""), m.get("matricule",""), m.get("courriel","")]).lower()
        if term_lower in hay:
            if m.get("liste_rouge"):
                out.append({"nom": m["nom"], "prenom": m["prenom"], "liste_rouge": True})
            else:
                out.append(m)
    return out

def add(member: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    member = dict(member)
    member.setdefault("id", str(uuid.uuid4()))
    member.setdefault("liste_rouge", False)
    meta = member.setdefault("meta", {})
    now = _now()
    meta["cree_le"] = meta.get("cree_le", now)
    meta["modifie_le"] = now
    validate_member(member)
    data.append(member)
    _atomic_write(data)
    return member

def _find_index(data, member_id: str):
    for i,m in enumerate(data):
        if m.get("id") == member_id:
            return i
    return -1

def delete(member_id: str) -> bool:
    data = _load()
    idx = _find_index(data, member_id)
    if idx < 0:
        return False
    data.pop(idx)
    _atomic_write(data)
    return True

def update(member_id: str, patch: Dict[str, Any]) -> Dict[str, Any] | None:
    data = _load()
    idx = _find_index(data, member_id)
    if idx < 0:
        return None
    data[idx].update(patch)
    data[idx].setdefault("meta", {})
    data[idx]["meta"]["modifie_le"] = _now()
    validate_member(data[idx])
    _atomic_write(data)
    return data[idx]

def redlist(member_id: str, flag: bool) -> Dict[str, Any] | None:
    return update(member_id, {"liste_rouge": flag})
