from collections import defaultdict
from time import time
from fastapi import HTTPException, Request

_attempts: dict[str, list[float]] = defaultdict(list)


def check_auth_rate_limit(request: Request, max_attempts: int = 5, window_seconds: int = 60):
    ip = request.client.host
    now = time()
    _attempts[ip] = [t for t in _attempts[ip] if now - t < window_seconds]
    if len(_attempts[ip]) >= max_attempts:
        raise HTTPException(429, "Too many requests. Try again in a minute.")
    _attempts[ip].append(now)
