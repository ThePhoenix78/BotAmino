from __future__ import annotations

import typing

from .bot import Bot
from .utils import NO_ICON_URL

__all__ = ("Parameters",)


class Parameters:
    """Represents the event parameters

    Parameters
    ----------
    data : Event
        The event information.
    subClient : Bot
        The community bot instance

    """

    __slots__ = (
        "author",
        "authorIcon",
        "authorId",
        "chatId",
        "comId",
        "info",
        "json",
        "level",
        "message",
        "messageId",
        "replyId",
        "replyMsg",
        "replySrc",
        "reputation",
        "subClient",
    )

    def __init__(self, data: typing.Any, subClient: Bot) -> None:
        self.info = data
        self.subClient = subClient
        # attributes
        self.author: str = data.message.author.nickname
        self.authorIcon: str = data.message.author.icon or NO_ICON_URL
        self.authorId: str = data.message.author.userId
        self.chatId: str = data.message.chatId
        self.comId: int = data.comId
        self.json: dict[str, typing.Any] = data.message.json
        self.level: int = data.message.author.level or 0
        self.message: str = data.message.content or ""
        self.messageId: str = data.message.messageId
        self.replySrc: str | None = None
        self.replyId: str | None = None
        self.replyMsg: str | None = None
        extensions = data.message.extensions
        if extensions and extensions.get("replyMessage"):
            if extensions["replyMessage"].get("mediaValue"):
                self.replySrc = extensions["replyMessage"]["mediaValue"].replace(
                    "_00.", "_hq."
                )
            self.replyId = extensions["replyMessage"]["messageId"]
            self.replyMsg = extensions["replyMessage"]["content"]
        self.reputation: int = data.message.author.reputation or 0
