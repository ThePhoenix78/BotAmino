from __future__ import annotations

import threading
import time
import typing

__all__ = ('TimeOut',)

TIMER_INTERVAL = 0.5


class TimeOut:
    """Base class for command timeout plugin"""
    def __init__(self) -> None:
        self.user_timeouts: dict[str, dict[typing.Literal["start", "end"], float]] = {}

    def time_user(self, userId: str, end: float = 5) -> None:
        """Create a cooldown for the user"""
        if userId not in self.user_timeouts.keys():
            self.user_timeouts[userId] = {"start": 0, "end": end}
            threading.Thread(target=self.timer, args=(userId,), daemon=True).start()

    def timer(self, userId: str) -> None:
        """Wait until the cooldown"""
        if userId not in self.user_timeouts:
            return
        while self.user_timeouts[userId]["start"] <= self.user_timeouts[userId]["end"]:
            self.user_timeouts[userId]["start"] += TIMER_INTERVAL
            time.sleep(TIMER_INTERVAL)
        del self.user_timeouts[userId]

    def timed_out(self, userId: str) -> bool:
        """Check if the user's cooldown has ended"""
        if userId in self.user_timeouts.keys():
            return self.user_timeouts[userId]["start"] >= self.user_timeouts[userId]["end"]
        return True
