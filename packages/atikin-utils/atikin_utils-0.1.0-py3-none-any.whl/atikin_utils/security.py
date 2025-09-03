import hashlib
import secrets
import string

def gen_token(length=32):
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def sha256(text):
    """Return SHA-256 hash of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
