from typing import Any, Dict, Optional
import os
import requests
import jwt
from jwt.utils import base64url_decode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

security = HTTPBearer()

_JWKS_CACHE: Optional[Dict[str, Any]] = None


def _jwks_url() -> str:
    """Build JWKS URL from SUPABASE_URL."""
    supabase_url = os.getenv("SUPABASE_URL")
    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is not set in environment")
    return f"{supabase_url}/auth/v1/.well-known/jwks.json"


def _get_jwks() -> Dict[str, Any]:
    """Fetch and cache JWKS."""
    global _JWKS_CACHE
    if _JWKS_CACHE is not None:
        return _JWKS_CACHE
    resp = requests.get(_jwks_url(), timeout=10)
    resp.raise_for_status()
    _JWKS_CACHE = resp.json()
    return _JWKS_CACHE


def _pem_from_token_header(token: str) -> bytes:
    """Derive PEM public key from token header using JWKS."""
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("JWT header missing 'kid'")

    jwks = _get_jwks()
    try:
        jwk = next(k for k in jwks["keys"] if k.get("kid") == kid)
    except StopIteration:
        raise ValueError("No matching JWK found for token 'kid'")

    x = int.from_bytes(base64url_decode(jwk["x"]), "big")
    y = int.from_bytes(base64url_decode(jwk["y"]), "big")

    public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
    public_key = public_numbers.public_key(default_backend())

    pem_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_key


def verify_jwt(token: str, *, audience: Optional[str] = None) -> Dict[str, Any]:
    """Verify Supabase ES256 JWT and return payload."""
    pem_key = _pem_from_token_header(token)
    aud = audience or os.getenv("SUPABASE_JWT_AUD", "authenticated")
    payload = jwt.decode(token, pem_key, algorithms=["ES256"], audience=aud)
    return payload


def extract_user_info(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract common user fields from payload."""
    app_meta = payload.get("app_metadata", {}) or {}
    user_meta = payload.get("user_metadata", {}) or {}

    return {
        "sub": payload.get("sub"),
        "email": payload.get("email") or user_meta.get("email"),
        "email_verified": user_meta.get("email_verified"),
        "phone": payload.get("phone") or user_meta.get("phone"),
        "phone_verified": user_meta.get("phone_verified"),
        "role": payload.get("role") or app_meta.get("role"),
        "aal": payload.get("aal"),
        "amr": payload.get("amr"),
        "session_id": payload.get("session_id"),
        "is_anonymous": payload.get("is_anonymous"),
        "app_metadata": app_meta,
        "user_metadata": user_meta,
        "iss": payload.get("iss"),
        "aud": payload.get("aud"),
        "iat": payload.get("iat"),
        "exp": payload.get("exp"),
    }


def get_current_user_email(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Extract and verify user email from JWT token."""
    try:
        token = credentials.credentials
        payload = verify_jwt(token)
        
        # Try to get email from payload or user_metadata
        user_meta = payload.get("user_metadata", {}) or {}
        email = payload.get("email") or user_meta.get("email")
        
        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")
        
        return email
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication token: {str(e)}")
