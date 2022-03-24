from time import sleep as slp
from threading import Thread
# from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from unicodedata import normalize
from string import punctuation

from .local_amino import objects
from .Bot import Bot


class TimeOut:
    users_dict = {}

    def time_user(self, uid, end: int = 5):
        if uid not in self.users_dict.keys():
            self.users_dict[uid] = {"start": 0, "end": end}
            Thread(target=self.timer, args=[uid]).start()

    def timer(self, uid):
        while self.users_dict[uid]["start"] <= self.users_dict[uid]["end"]:
            self.users_dict[uid]["start"] += 1
            slp(1)
        del self.users_dict[uid]

    def timed_out(self, uid):
        if uid in self.users_dict.keys():
            return self.users_dict[uid]["start"] >= self.users_dict[uid]["end"]
        return True


class BannedWords:
    def filtre_message(self, message, code):
        para = normalize('NFD', message).encode(code, 'ignore').decode("utf8").strip().lower()
        para = para.translate(str.maketrans("", "", punctuation))
        return para

    def check_banned_words(self, args):
        for word in ("ascii", "utf8"):
            with suppress(Exception):
                para = self.filtre_message(args.message, word).split()
                if para != [""]:
                    with suppress(Exception):
                        [args.subClient.delete_message(args.chatId, args.messageId, reason=f"Banned word : {elem}", asStaff=True) for elem in para if elem in args.subClient.banned_words]


class Parameters:
    __slots__ = (
                    "subClient", "chatId", "authorId", "author", "message", "messageId",
                    "authorIcon", "comId", "replySrc", "replyMsg", "replyId", "info"
                 )

    def __init__(self, data: objects.Event, subClient: Bot):
        self.subClient: Bot = subClient
        self.chatId: str = data.message.chatId
        self.authorId: str = data.message.author.userId
        self.author: str = data.message.author.nickname
        self.message: str = data.message.content
        self.messageId: str = data.message.messageId
        self.authorIcon: str = data.message.author.icon
        self.comId: str = data.comId

        self.replySrc: str = None
        self.replyId: str = None
        if data.message.extensions and data.message.extensions.get('replyMessage', None) and data.message.extensions['replyMessage'].get('mediaValue', None):
            self.replySrc = data.message.extensions['replyMessage']['mediaValue'].replace('_00.', '_hq.')
            self.replyId = data.message.extensions['replyMessage']['messageId']

        self.replyMsg: str = None
        if data.message.extensions and data.message.extensions.get('replyMessage', None) and data.message.extensions['replyMessage'].get('content', None):
            self.replyMsg: str = data.message.extensions['replyMessage']['content']
            self.replyId: str = data.message.extensions['replyMessage']['messageId']

        self.info: objects.Event = data
