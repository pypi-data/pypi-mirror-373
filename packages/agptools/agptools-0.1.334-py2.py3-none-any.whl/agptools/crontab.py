import re
import random
import time
from datetime import datetime, timedelta
from datetime import datetime, timezone, tzinfo

from agptools.helpers import DATE


class Crontab:
    STEP = timedelta(seconds=1)

    VALID_SPECS = set(
        ["day", "hour", "min", "minute", "month", "second", "weekday", "year"]
    )
    MAX_CACHE = 100

    def __init__(self, **cron):
        self.t0 = None
        self.cron = {k: cron[k] for k in self.VALID_SPECS.intersection(cron)}
        self.cache = {}

    def now(self):
        now = datetime.now(tz=timezone.utc).replace(microsecond=0)
        return now

    def check(self, now=None):
        "Fires all time that matches from last call"
        now = now or self.now()
        if self.t0:
            # TODO: OPTIMIZE: when now and self.t0 are too far each other
            while self.t0 <= now:
                self.t0 += self.STEP
                for key, pattern in self.cron.items():
                    value = getattr(self.t0, key, None)
                    if value is not None:
                        if not isinstance(value, int):
                            value = value()  # method
                        if not re.match(f"{pattern}$", f"{value}"):
                            break
                else:
                    # all cron (if any) matches
                    return self.t0
        else:
            self.t0 = now.replace(microsecond=0)

    def next_ts(self, dt, check_itself=False):
        # TODO: cache some results and drop random values when if full
        dt = DATE(dt).replace(microsecond=0)
        if not check_itself:
            dt += self.STEP

        dt0 = dt
        if result := self.cache.get(dt):
            return result

        max_steps = int(timedelta(days=365) / self.STEP)
        for _ in range(max_steps):
            for key, pattern in self.cron.items():
                value = getattr(dt, key, None)
                if value is not None:
                    if not isinstance(value, int):
                        value = value()  # method
                    if not re.match(f"{pattern}$", f"{value}"):
                        break
            else:
                if len(self.cache) >= self.MAX_CACHE:
                    L = self.MAX_CACHE - (1 + self.MAX_CACHE // 5)
                    while len(self.cache) > L:
                        self.cache.popitem()

                self.cache[dt0] = dt
                return dt
            dt += self.STEP

        print("can't find the next ts for the whole next year")
        foo = 1


if __name__ == "__main__":
    cron = Crontab(second="0", minute="0|15|30|45")
    while True:
        while not (t := cron.check()):
            time.sleep(random.randint(1, 10))
        print(f"match at: {t}")
