import os
from typing import Optional

def is_admin(admin_token: Optional[str]) -> bool:
    expected = os.environ.get("ADMIN_PASSWORD", "")
    return bool(admin_token) and expected and admin_token == expected
