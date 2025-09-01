from typing import List
from urllib.parse import urlparse


def is_url_scheme(s: str, schemes: List[str]) -> bool:
    try:
        u = urlparse(s)
        return bool(u.netloc) and (u.scheme in schemes)
    except Exception as e:
        return False
