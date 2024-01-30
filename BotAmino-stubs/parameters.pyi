from typing import Any, Dict, Optional
from aminofix.lib.util.objects import Event  # type: ignore
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
        self.json: Dict[str, Any]
        self.level: int
        self.message: str
        self.messageId: str
        self.replySrc: Optional[str]
        self.replyId: Optional[str]
        self.replyMsg: Optional[str]
        self.reputation: int
        self.subClient: Bot
