
import requests
import datetime
import base64
from urllib.parse import urlparse
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv
import os

# Configuration
load_dotenv()
api_key = os.getenv("KALSHI_API_KEY")
if not api_key:
    raise RuntimeError("KALSHI_API_KEY environment variable is not set")

BASE_URL = os.getenv("KALSHI_API_URL")

# Load private key from file
key_path = "private_key.pem"
if not os.path.exists(key_path):
    raise RuntimeError(f"private key file not found: {key_path}")
with open(key_path, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

def create_signature(private_key, timestamp, method, path):
    """Create the request signature."""
    # Strip query parameters before signing
    path_without_query = path.split('?')[0]
    message = f"{timestamp}{method}{path_without_query}".encode('utf-8')
    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def get(path, private_key=private_key, api_key_id=api_key, base_url=BASE_URL):
    """Make an authenticated GET request to the Kalshi API."""
    timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
    sign_path = urlparse(base_url + path).path
    signature = create_signature(private_key, timestamp, "GET", sign_path)

    headers = {
        'KALSHI-ACCESS-KEY': api_key_id,
        'KALSHI-ACCESS-SIGNATURE': signature,
        'KALSHI-ACCESS-TIMESTAMP': timestamp
    }

    resp = requests.get(base_url + path, headers=headers, timeout=10)
    if resp.status_code != 200:
        # surface error body for debugging
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise RuntimeError(f"API request failed: {resp.status_code} - {err}")
    return resp

def post(path, data, private_key=private_key, api_key_id=api_key, base_url=BASE_URL):
    """Make an authenticated POST request to the Kalshi API."""
    timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
    sign_path = urlparse(base_url + path).path
    signature = create_signature(private_key, timestamp, "POST", sign_path)

    headers = {
        'KALSHI-ACCESS-KEY': api_key_id,
        'KALSHI-ACCESS-SIGNATURE': signature,
        'KALSHI-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
    }

    return requests.post(base_url + path, headers=headers, json=data, timeout=10)
