"""
Helpers for progress bars and ETA estimation.
"""

import random
import time
from datetime import datetime, timedelta
from .logs import logger

log = logger(__name__)


# ----------------------------------------------------------
# Progress
# ----------------------------------------------------------
class Progress:
    "A class to measure the progress of an algorithm"

    def __init__(self, x0=0, N=10, label=""):
        self.n0 = 0
        self.n1 = 0
        self.n2 = 0
        self.x = x0
        self.N = N
        self.samples = []
        self.t0 = 0
        self.t1 = 0
        self.t2 = 0
        self.freq = 600
        self.speed = 0
        self.data = {}
        self.label = label or f"uid:{random.randint(0, 1000)}"

    def set(self, x, force=False, **data):
        "Set the progress"
        self.x = x
        self._step(force, **data)

    def restart(self, N, freq=60):
        self.t0 = self.t1 = time.time()
        self.freq = freq
        self.t2 = self.t1 + self.freq
        self.N = N

    def eta(self, out=True):
        speed = self.current_speed()
        remain = max(self.N - self.x, 1)

        seconds = remain / speed
        when = datetime.now() + timedelta(seconds=seconds)
        if out:
            log.info("[%s / %s]: %s", self.x, self.N, when)
        return when

    def current_speed(self):
        elapsed = time.time() - self.t0
        done = max(self.x, 1)
        self.speed = done / elapsed
        return self.speed

    def update(self, n=1, force=False, **data):
        "Update the progress"
        self.x += n
        self.n2 += n
        self._step(force, **data)

    def closer(self):
        t1 = time.time()
        if t1 < self.t2:
            self.t2 = (t1 + self.t2) / 2

    def _step(self, force=False, **data):
        "Update the progress"
        t1 = time.time()
        self.data.update(data)
        sample = t1, self.x

        self.samples.append(sample)
        if len(self.samples) > 200:
            self.samples = self.samples[100:]

        if force or t1 > self.t2:
            elapsed = t1 - self.t1
            self.speed = self.n2 / elapsed
            self.t1 = t1
            self.t2 = t1 + self.freq
            self.n2 = 0
            log.info(
                "[%s] Speed: %s items/sec: %s: %s",
                self.label,
                f"{self.speed:.2f}",
                self.data,
                self.x,
            )
