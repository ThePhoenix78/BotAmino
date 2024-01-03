# native packages
from typing import Dict, Literal
from threading import Thread
from time import sleep

__all__ = ('TimeOut',)


class TimeOut:
    """Base class for command timeout plugin"""
    def __init__(self) -> None:
        self.user_timeouts: Dict[str, Dict[Literal["start", "end"], int]] = {}

    def time_user(self, uid: str, end: int = 5) -> None:
        """Create a cooldown for the user"""
        if uid not in self.user_timeouts.keys():
            self.user_timeouts[uid] = {"start": 0, "end": end}
            Thread(target=self.timer, args=(uid,), daemon=True).start()

    def timer(self, uid: str) -> None:
        """Wait until the cooldown"""
        if uid not in self.user_timeouts:
            return
        while self.user_timeouts[uid]["start"] <= self.user_timeouts[uid]["end"]:
            self.user_timeouts[uid]["start"] += 1
            sleep(1)
        del self.user_timeouts[uid]

    def timed_out(self, uid: str) -> bool:
        """Check if the user's cooldown has ended"""
        if uid in self.user_timeouts.keys():
            return self.user_timeouts[uid]["start"] >= self.user_timeouts[uid]["end"]
        return True
