import jwt

token = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImY0YWI1OTQ0LTBkMjktNDFhNC05M2E1LWI4MWU1MmY3Yjc0NSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3hoZWlvdHF1eXB0cmllbHNtaXRvLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2NTczMjFiZS1kZTA4LTRmNzUtYjkwNi0xMjM1YjQ5YWZlYzciLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzY3OTEwNzkzLCJpYXQiOjE3Njc5MDcxOTMsImVtYWlsIjoidmFuc2hraGFuZWphMjAwNEBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoidmFuc2hraGFuZWphMjAwNEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI2NTczMjFiZS1kZTA4LTRmNzUtYjkwNi0xMjM1YjQ5YWZlYzcifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc2NzkwNzE5M31dLCJzZXNzaW9uX2lkIjoiYTZiYjUzYTktY2RjOS00NzNlLWIwNTktYTBiNmU2ZjMzMDljIiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.ZWbaws1IfmdLmNIftAI9nMDcOtPX_PA8at8O5BTyGREHRsvO3aU7WfnJmoZv_UjzQqlDK9FS2y_TDJiFNO0DJg"

# # payload = jwt.decode(token, options={"verify_signature": False})

# # print(payload)

# import jwt
# import requests

# JWKS_URL = "https://xheiotquyptrielsmito.supabase.co/auth/v1/.well-known/jwks.json"
# jwks = requests.get(JWKS_URL).json()

# header = jwt.get_unverified_header(token)
# kid = header["kid"]

# key = next(k for k in jwks["keys"] if k["kid"] == kid)

# payload = jwt.decode(
#     token,
#     key,
#     algorithms=["ES256"],
#     audience="authenticated"
# )

# print("✅ VERIFIED PAYLOAD:", payload)
# /////////////////////////////////////////////////////////

import jwt
import requests
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from jwt.utils import base64url_decode
from dotenv import load_dotenv
import os

# ---------------- CONFIG ---------------- #

SUPABASE_URL = os.getenv("SUPABASE_URL")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"


# ---------------- FETCH JWKS ---------------- #

jwks = requests.get(JWKS_URL).json()

# ---------------- GET MATCHING KEY ---------------- #

header = jwt.get_unverified_header(token)
kid = header["kid"]

jwk = next(k for k in jwks["keys"] if k["kid"] == kid)

# ---------------- JWK → PEM ---------------- #

x = int.from_bytes(base64url_decode(jwk["x"]), "big")
y = int.from_bytes(base64url_decode(jwk["y"]), "big")

public_numbers = ec.EllipticCurvePublicNumbers(
    x,
    y,
    ec.SECP256R1()  # P-256
)

public_key = public_numbers.public_key(default_backend())

pem_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# ---------------- VERIFY JWT ---------------- #

payload = jwt.decode(
    token,
    pem_key,
    algorithms=["ES256"],
    audience="authenticated"
)

print("✅ VERIFIED PAYLOAD:")
print(payload)
