import secrets
import time

def generate_session_token() -> str:
    """Generates a secure random session token."""
    return secrets.token_hex(16)

def generate_totp_code(secret: str, interval: int = 15) -> str:
    """
    Generates a dynamic TOTP code based on current time window.
    Default interval is 15 seconds to enforce short-lived dynamic QR codes.
    """
    time_window = int(time.time() // interval)
    combined = f"{secret}:{time_window}"
    import hashlib
    return hashlib.sha256(combined.encode()).hexdigest()[:6].upper()

def verify_totp_code(secret: str, code: str, interval: int = 15, valid_windows: int = 1) -> bool:
    """
    Verifies TOTP code allowing for current window and adjacent windows to handle slight network skew.
    """
    current_window = int(time.time() // interval)
    import hashlib
    for w in range(current_window - valid_windows, current_window + valid_windows + 1):
        combined = f"{secret}:{w}"
        expected = hashlib.sha256(combined.encode()).hexdigest()[:6].upper()
        if expected == code:
            return True
    return False
