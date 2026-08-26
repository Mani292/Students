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
        if expected.upper() == code.upper():
            return True
    return False

def calculate_geofence_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two GPS points in meters (Haversine formula).
    """
    import math
    R = 6371000 # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
