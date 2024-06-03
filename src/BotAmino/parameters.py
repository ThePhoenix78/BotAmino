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

    def __init__(self, data, subClient):
        self.author = data.message.author.nickname
        self.authorIcon = data.message.author.icon or NO_ICON_URL
        self.authorId = data.message.author.userId
        self.chatId = data.message.chatId
        self.comId = data.comId
        self.info = data
        self.json = data.message.json
        self.level = data.message.author.level or 0
        self.message = data.message.content or  ''
        self.messageId = data.message.messageId
        self.replySrc = None
        self.replyId = None
        self.replyMsg = None
        extensions = data.message.extensions
        if extensions and extensions.get('replyMessage'):
            if extensions['replyMessage'].get('mediaValue'):
                self.replySrc = extensions['replyMessage']['mediaValue'].replace('_00.', '_hq.')
            self.replyId = extensions['replyMessage']['messageId']
            self.replyMsg = extensions['replyMessage'].get('content')
        self.reputation = data.message.author.reputation
        self.subClient = subClient
