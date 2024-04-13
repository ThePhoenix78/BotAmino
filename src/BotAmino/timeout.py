import threading
import time

__all__ = ('TimeOut',)


class TimeOut:
    """Base class for command timeout plugin"""
    def __init__(self):
        self.user_timeouts = {}

    def time_user(self, uid, end=5):
        """Create a cooldown for the user"""
        if uid not in self.user_timeouts.keys():
            self.user_timeouts[uid] = {"start": 0, "end": end}
            threading.Thread(target=self.timer, args=(uid,), daemon=True).start()

    def timer(self, uid):
        """Wait until the cooldown"""
        if uid not in self.user_timeouts:
            return
        while self.user_timeouts[uid]["start"] <= self.user_timeouts[uid]["end"]:
            self.user_timeouts[uid]["start"] += 1
            time.sleep(1)
        del self.user_timeouts[uid]

    def timed_out(self, uid):
        """Check if the user's cooldown has ended"""
        if uid in self.user_timeouts.keys():
            return self.user_timeouts[uid]["start"] >= self.user_timeouts[uid]["end"]
        return True
