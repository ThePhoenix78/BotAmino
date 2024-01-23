import typing

from aminofix.lib.util.objects import Event  # type: ignore
from .bot import Bot
from .utils import NO_ICON_URL

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
        self.author = typing.cast(str, data.message.author.nickname)  # type: ignore
        self.authorIcon = typing.cast(typing.Optional[str], data.message.author.icon) or NO_ICON_URL  # type: ignore
        self.authorId = typing.cast(str, data.message.author.userId)  # type: ignore
        self.chatId = typing.cast(str, data.message.chatId)  # type: ignore
        self.comId = typing.cast(int, data.comId)  # type: ignore
        self.info = data
        self.json = typing.cast(typing.Dict[str, typing.Any], data.message.json)
        self.level = typing.cast(typing.Optional[int], data.message.author.level)  # type: ignore
        self.message = typing.cast(str, data.message.content or  '')  # type: ignore
        self.messageId = typing.cast(str, data.message.messageId)  # type: ignore
        self.replySrc = None
        self.replyId = None
        self.replyMsg = None
        extensions = typing.cast(typing.Optional[typing.Dict[str, typing.Any]], data.message.extensions)  # type: ignore
        if extensions and extensions.get('replyMessage'):
            if extensions['replyMessage'].get('mediaValue'):
                self.replySrc = typing.cast(str, extensions['replyMessage']['mediaValue']).replace('_00.', '_hq.')
            self.replyId = typing.cast(str, extensions['replyMessage']['messageId'])
            self.replyMsg = typing.cast(typing.Optional[str], extensions['replyMessage']['content'])
        self.reputation = typing.cast(int, data.message.author.reputation)  # type: ignore
        self.subClient = subClient
