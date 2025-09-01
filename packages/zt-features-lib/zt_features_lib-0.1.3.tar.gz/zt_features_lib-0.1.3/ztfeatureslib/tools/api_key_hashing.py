import hashlib
import base64

def hash_key(raw_key: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(raw_key.encode("utf-8"))
    return base64.b64encode(sha256.digest()).decode("utf-8")