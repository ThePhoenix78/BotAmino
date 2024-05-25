from typing import Any
from aminofix.lib.util.objects import Event
from .bot import Bot

__all__ = ('Parameters',)


class Parameters:
    def __init__(self, data: Event, subClient: Bot) -> None:
        self.author: str
        self.authorIcon: str
        self.authorId: str
        self.chatId: str
        self.comId: int
        self.info: Event
        self.json: dict[str, Any]
        self.level: int
        self.message: str
        self.messageId: str
        self.replySrc: str | None
        self.replyId: str | None
        self.replyMsg: str | None
        self.reputation: int
        self.subClient: Bot
