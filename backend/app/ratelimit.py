"""Per-user limit on write requests, so a script can't flood the database.

In-memory, so it assumes one API process (the Docker image runs one).
"""

import time
from collections import defaultdict, deque

from fastapi import Depends

from app.errors import rate_limited
from app.models import User
from app.security import get_current_user

WRITES_PER_MINUTE = 30

_recent: dict[int, deque[float]] = defaultdict(deque)


async def limit_writes(user: User = Depends(get_current_user)) -> User:
    now = time.monotonic()
    window = _recent[user.id]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= WRITES_PER_MINUTE:
        raise rate_limited()
    window.append(now)
    return user
