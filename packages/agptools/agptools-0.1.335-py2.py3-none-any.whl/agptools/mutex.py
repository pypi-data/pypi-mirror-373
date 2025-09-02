import time
import asyncio

from .helpers import DATE
from .logs import logger

log = logger(__name__)


# ----------------------------------
# Mutex Operations
# ----------------------------------
class TimedMutex:
    MUTEX_DELAY = 10.0

    def __init__(self):
        self.lock_start = 0
        self.locked_time = 0

    async def lock(self, **info):
        while (t0 := time.time()) < self.locked_time:
            log.debug("[%s] wait for mutex: %s: %s", self, DATE(self.locked_time), info)
            await asyncio.sleep(self.MUTEX_DELAY)

        self.lock_start = t0
        log.error("[%s] got the mutext: %s: %s", self, DATE(self.lock_start), info)
        await self.update(**info)

    async def update(self, **info):
        self.locked_time = time.time() + 13 * self.MUTEX_DELAY
        log.debug("[%s] mutex updated: %s: %s", self, DATE(self.locked_time), info)
        await asyncio.sleep(0.05)

    async def clean(self, **info):
        elapsed = time.time() - self.lock_start
        log.error("[%s] mutex cleaned before: %s secs: %s", self, elapsed, info)

        self.lock_start = 0
        self.locked_time = 0
