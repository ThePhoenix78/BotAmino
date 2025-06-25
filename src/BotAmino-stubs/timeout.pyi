from typing import Literal

__all__ = ('TimeOut',)


class TimeOut:
    def __init__(self) -> None:
        self.user_timeouts: dict[str, dict[Literal["start", "end"], int]]
    def time_user(self, uid: str, end: int = 5) -> None: ...
    def timer(self, uid: str) -> None: ...
    def timed_out(self, uid: str) -> bool: ...
