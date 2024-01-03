# python future feature compatibility (v3.10)
from __future__ import annotations
# native packages
from typing import Any, Dict, Optional, TYPE_CHECKING, cast
# internal
from .utils import NO_ICON_URL
# only type-checkers
if TYPE_CHECKING:
    from .bot import Bot
    from aminofix.lib.util.objects import Event

__all__ = ('Parameters',)


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
        "subClient"
    )

    def __init__(self, data: Event, subClient: Bot) -> None:
        self.author = cast(str, data.message.author.nickname)
        self.authorIcon = cast(Optional[str], data.message.author.icon) or NO_ICON_URL
        self.authorId = cast(str, data.message.author.userId)
        self.chatId = cast(str, data.message.chatId)
        self.comId = cast(int, data.comId)
        self.info = data
        self.json = cast(Dict[str, Any], data.message.json)
        self.level = cast(Optional[int], data.message.author.level)
        self.message = cast(str, data.message.content or  '')
        self.messageId = cast(str, data.message.messageId)
        self.replySrc = None
        self.replyId = None
        self.replyMsg = None
        if data.message.extensions and data.message.extensions.get('replyMessage'):
            self.replyId = cast(str, data.message.extensions['replyMessage']['messageId'])
            self.replyMsg = cast(Optional[str], data.message.extensions['replyMessage']['content'])
            if data.message.extensions['replyMessage'].get('mediaValue'):
                self.replySrc = cast(str, data.message.extensions['replyMessage']['mediaValue'].replace('_00.', '_hq.'))
        self.reputation = cast(int, data.message.author.reputation)
        self.subClient = subClient
