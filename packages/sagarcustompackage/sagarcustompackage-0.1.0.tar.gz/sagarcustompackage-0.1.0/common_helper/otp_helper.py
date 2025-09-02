import base64, hashlib, hmac, json
from datetime import datetime, timedelta
import requests


def b64url_encode(b: bytes) -> str: 
    """URL‑safe Base‑64 without padding."""
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)

# ---------- create ----------
def generate_hash(phone: str, otp: str, SECRET_KEY: str = "secret", expiry_minutes: int = 5) -> str:
    payload = {
        "phone": phone,
        "otp": otp,
        "expiry": (datetime.utcnow() + timedelta(minutes=expiry_minutes)).isoformat()
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    payload_b64 = b64url_encode(payload_json)

    # Sign the *encoded* payload – keeps signing input 100 % deterministic
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).digest()
    signature_b64 = b64url_encode(signature)

    token = f"{payload_b64}.{signature_b64}"      # <payload>.<signature>
    return token

# ---------- verify ----------
def decode_hash(token: str, SECRET_KEY: str = "secret"):
    try:
        payload_b64, sig_b64 = token.split(".", 1)
        expected_sig = hmac.new(
            SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256
        ).digest()

        # Constant‑time compare
        if not hmac.compare_digest(b64url_decode(sig_b64), expected_sig):
            return None, "Invalid signature"

        data = json.loads(b64url_decode(payload_b64).decode())
        data["expiry"] = datetime.fromisoformat(data["expiry"])
        return data, None
    except Exception as exc:
        return None, str(exc)

def validate_otp(token: str, phone: str, otp: str):
    data, err = decode_hash(token)
    if err:
        return False, err
    if data["phone"] != phone:
        return False, "Phone number mismatch"
    if data["otp"] != otp:
        return False, "Invalid OTP"
    if datetime.utcnow() > data["expiry"]:
        return False, "OTP expired"
    return True, "OTP verified"


