import base64
import hashlib


def md5_base64(user_query):
    md5_hash = hashlib.md5(user_query.encode()).digest()
    b64_encoded = base64.b64encode(md5_hash).decode()
    safe_name = b64_encoded.replace('/', '_').replace('+', '-')
    return safe_name
