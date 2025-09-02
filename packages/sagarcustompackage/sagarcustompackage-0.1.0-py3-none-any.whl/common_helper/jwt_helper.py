import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify


class JWTAuthError(Exception):
    """Custom exception for JWT authentication errors."""
    def __init__(self, message, status_code=401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def create_access_token(
    data: dict,
    expires_delta: timedelta = None,
    secret_key: str = "secret"
) -> str:
    """
    Create a JWT token with optional expiry time.
    Default expiry: 24 hours
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_access_token(token: str, secret_key: str = "secret") -> dict:
    """
    Decode a JWT token and return payload.
    Raises JWTAuthError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTAuthError("Token expired", 401)
    except jwt.InvalidTokenError:
        raise JWTAuthError("Invalid token", 401)


def jwt_required(secret_key: str = "secret"):
    """
    Flask decorator to protect routes with JWT authentication.
    Usage:
        @app.route("/secure")
        @jwt_required(secret_key="mysecret")
        def secure_route(current_user):
            return jsonify({"user": current_user})
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"message": "Authorization token missing"}), 403
            token = auth_header.split(" ")[1]
            try:
                user = decode_access_token(token, secret_key=secret_key)
            except JWTAuthError as e:
                return jsonify({"message": e.message}), e.status_code
            return f(user, *args, **kwargs)
        return wrapper
    return decorator
