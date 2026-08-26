import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token

def test_security():
    print("Testing password hashing...")
    pwd = "SecretPassword123!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False
    print("Password hashing PASSED.")

    print("Testing JWT access token creation & decoding...")
    access_token = create_access_token(subject=1, role="STUDENT")
    decoded_access = decode_token(access_token)
    assert decoded_access is not None
    assert decoded_access["sub"] == "1"
    assert decoded_access["role"] == "STUDENT"
    assert decoded_access["type"] == "access"
    print("Access token verification PASSED.")

    print("Testing JWT refresh token creation & decoding...")
    refresh_token = create_refresh_token(subject=1, role="STUDENT")
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh is not None
    assert decoded_refresh["sub"] == "1"
    assert decoded_refresh["type"] == "refresh"
    print("Refresh token verification PASSED.")

if __name__ == "__main__":
    test_security()
