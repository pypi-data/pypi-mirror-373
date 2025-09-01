import base64
import requests
from datetime import datetime
from dotenv import dotenv_values

# ---------------------------------------------------------------------
# Admin Portal Login
# ---------------------------------------------------------------------

ADMIN_LOGIN_CACHE = {}

def adminlogin(env_path, format=None):
    """
    Logs into the Ferma Admin Portal and caches the token in ADMIN_LOGIN_CACHE.
    """
    creds = dotenv_values(env_path)

    if format == "ENCODED":
        username = base64.b64decode(creds.get("FERMA_USERNAME")).decode()
        password = base64.b64decode(creds.get("FERMA_PASSWORD")).decode()
    else:
        username = creds.get("FERMA_USERNAME")
        password = creds.get("FERMA_PASSWORD")

    if not username or not password:
        raise ValueError("Missing FERMA_USERNAME or FERMA_PASSWORD in env file")

    cache_key = (username, password)
    if cache_key in ADMIN_LOGIN_CACHE:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: (Cache) Ferma Admin Portal Login successful")
        return ADMIN_LOGIN_CACHE[cache_key]

    resp = requests.post(
        "https://admin-portal.ferma.ai/users/login",
        json={"username": username, "password": password, "persist": 1}
    )

    if resp.status_code == 200:
        token = resp.json().get("accessToken")
        if not token:
            raise RuntimeError("Admin login failed: No token returned")

        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0"
        }
        ADMIN_LOGIN_CACHE[cache_key] = headers
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Ferma Admin Portal Login successful")
        return headers
    else:
        raise RuntimeError(f"Admin login failed: HTTP {resp.status_code}")


# ---------------------------------------------------------------------
# Support Portal Login
# ---------------------------------------------------------------------

session = None

def supportlogin(env_path):
    global session
    
    login_headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://support.ferma.ai/main/login"
    }
    
    creds = dotenv_values(env_path)
    session = requests.Session()
    session.get("https://support.ferma.ai/main/login")

    login_data = {
        "username": creds.get("FERMA_USERNAME"),
        "password": creds.get("FERMA_PASSWORD")
    }
    response = session.post("https://support.ferma.ai/main/validate", data=login_data, headers=login_headers)
    
    if response.status_code == 200:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Ferma Support Portal Login successful")
        return session
    else:
        raise Exception(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Login failed - Invalid credentials or server error")