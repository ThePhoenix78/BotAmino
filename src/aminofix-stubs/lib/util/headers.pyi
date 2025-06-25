from typing import Any

__all__ = (
    "ApisHeaders",
    "Tapjoy"
)

class ApisHeaders:
    def __init__(
        self,
        deviceId: str,
        user_agent: str,
        auid: str | None = None,
        sid: str | None = None,
        data: bytes | str | None = None,
        type: str | None = None,
        sig: str | None = None
    ) -> None:
        self.headers: dict[str, str]

class Tapjoy:
    def __init__(self, userId: str)  -> None:
        self.data: dict[str, Any]
    @property
    def headers(self) -> dict[str, str]: ...
