import requests

def get_json(url, timeout=10):
    """Fetch JSON from a given URL."""
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
