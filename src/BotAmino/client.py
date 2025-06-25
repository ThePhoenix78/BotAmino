from __future__ import annotations

from .http import HTTPClient
from .typing import Proxies
from .ws import WSClient

__all__ = ("Client",)


# separate the client class because conflicts
# with ws methods for the SubClient
class Client(HTTPClient, WSClient):
    __slots__ = (
        "_account",
        "_agent",
        "_auid",
        "_certificatePath",
        "_chat_events",
        "_channel_events",
        "_deviceId",
        "_error_events",
        "_language",
        "_live_layer_active_events",
        "_live_layer_events",
        "_live_layer_inactive_events",
        "_notification_events",
        "_secret",
        "_sid",
        "_smdeviceId",
        "_profile",
        "_proxies",
        "_timeout",
        "_timezone",
        "_ws",
        "_ws_handlers",
        "_ws_response_listeners",
        "_ws_task_active",
    )

    def __init__(
        self,
        deviceId: str | None = None,
        smdeviceId: str | None = None,
        proxies: Proxies | None = None,
        certificatePath: str | None = None,
        agent: str | None = None,
        language: str | None = None,
        timeout: float | None = None,
        timezone: int | None = None,
    ) -> None:
        super().__init__(
            deviceId=deviceId,
            smdeviceId=smdeviceId,
            proxies=proxies,
            certificatePath=certificatePath,
            agent=agent,
            language=language,
            timeout=timeout,
            timezone=timezone,
        )
        super(HTTPClient, self).__init__()
