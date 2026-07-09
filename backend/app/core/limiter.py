import time
from collections import defaultdict
from typing import Optional
from backend.app.core.config import settings


class TokenBucketLimiter:
    """基于 Redis 的令牌桶限流器（无 Redis 时使用内存版本）"""

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._enabled: bool = False

    def _clean_bucket(self, key: str, max_time: float) -> None:
        now = time.time()
        self._buckets[key] = [t for t in self._buckets[key] if now - t < max_time]

    async def check_rate_limit(self, identifier: str, rate: int = 60) -> bool:
        key = f"rl:{identifier}"
        now = time.time()
        window = 60.0
        self._clean_bucket(key, window)
        if len(self._buckets[key]) >= rate:
            return False
        self._buckets[key].append(now)
        return True


limiter = TokenBucketLimiter()
