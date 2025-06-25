from __future__ import annotations

import contextlib
import json
import operator
import os
import random
import threading
import time
import typing
import urllib.request

from .acm import ACM
from .subclient import SubClient
from .utils import PATH_AMINO, PATH_UTILITIES, print_exception

if typing.TYPE_CHECKING:
    from .botamino import BotAmino

__all__ = ("Bot",)


class Bot(SubClient, ACM):
    """Represents a community bot

    Supports ACM and Community methods.

    Parameters
    ----------
    client : BotAmino
        The global bot instance.
    community : int, str
        The community ID or the aminoID.
    prefix : str, optional
        The command prefix. Default is '!'.
    bio : list[str], str, optional
        The bot's profile bio. Default is None.
    activity : bool, optional
        The bot can send activity time.

    """

    __slots__ = (
        # httpclient
        "_account",
        "_agent",
        "_auid",
        "_certificatePath",
        "_comId",
        "_community",
        "_client",
        "_deviceId",
        "_language",
        "_secret",
        "_sid",
        "_smdeviceId",
        "_profile",
        "_proxies",
        "_timeout",
        "_timezone",
    )

    lock = threading.Lock()

    @property
    def community_amino_id(self) -> str:
        return self.community.aminoId

    @property
    def community_id(self) -> int:
        return self.community.comId

    @property
    def community_leader_agent_id(self) -> str:
        return self.community.agent.userId

    @property
    def community_name(self) -> str:
        return self.community.name

    @property  # type: ignore
    def client(self) -> BotAmino:
        return getattr(self, "_client")

    @client.setter
    def client(self, value: "BotAmino") -> None:  # type: ignore
        setattr(self, "_client", value)

    def __init__(
        self,
        client: BotAmino,
        community: str | int,
        prefix: str = "!",
        bio: list[str] | str | None = None,
        activity: bool = False,
    ):
        self.client = client
        self.prefix: str = prefix
        self.bio_contents: list[str] | str | None = bio
        self.activity: bool = activity
        self.marche: bool = True
        comId, aminoId = None, None
        if isinstance(community, int):
            comId = community
        else:
            aminoId = community
        # ACM initializer not required
        super().__init__(comId=comId, aminoId=aminoId, client=client)
        # Set up bot for community staff
        self.community_leaders: list[str] = []
        self.community_curators: list[str] = []
        with contextlib.suppress(Exception):
            self.community_leaders.extend(self.get_all_users("leader").profile.userId)
            self.community_curators.extend(self.get_all_users("curator").profile.userId)
        self.community_staff = list(
            set(self.community_leaders + self.community_curators)
        )
        # Set up bot for community files
        if not os.path.exists(self.community_filename):
            self.create_community_file()
        config = self.get_file_dict()
        for key, value in self.create_dict().items():
            config.setdefault(key, value)
        self.update_file(config)
        # Set up community config
        self.banned_words: list[str] = self.get_file_info("banned_words")
        self.locked_command: list[str] = self.get_file_info("locked_command")
        self.message_bvn: str | None = self.get_file_info("welcome")
        self.welcome_chat: str | None = self.get_file_info("welcome_chat")
        self.favorite_users: list[str] = self.get_file_info("favorite_users")
        self.favorite_chats: list[str] = self.get_file_info("favorite_chats")
        self.update_file()
        with contextlib.suppress(Exception):
            self.activity_status("on")
        self.new_users: list[str] = self.get_all_users(
            start=0, size=30, type="recent"
        ).profile.userId

    @property
    def community_filename(self) -> str:
        """Get the bot's community filename"""
        for folder in (PATH_UTILITIES, PATH_AMINO):
            with contextlib.suppress(OSError):
                os.mkdir(folder)
        return os.path.join(PATH_AMINO, f"{self.community_amino_id}.json")

    def create_community_file(self) -> None:
        """Create a new community filename"""
        with open(self.community_filename, "w", encoding="utf8") as file:
            json.dump(self.create_dict(), file, indent=4)

    def update_file(self, data: dict[str, typing.Any] | None = None):
        """Update the community file data with new information"""
        data = data or self.get_dict()
        with open(self.community_filename, "w") as file:
            json.dump(data, file, indent=4)

    def create_dict(self) -> dict[str, typing.Any]:
        """Create an empty dataset for a community file"""
        return {
            "welcome": None,
            "prefix": self.prefix,
            "welcome_chat": None,
            "locked_command": [],
            "favorite_users": [],
            "favorite_chats": [],
            "banned_words": [],
        }

    def get_dict(self) -> dict[str, typing.Any]:
        """Create a full dataset for a community file"""
        return {
            "welcome": self.message_bvn,
            "prefix": self.prefix,
            "welcome_chat": self.welcome_chat,
            "locked_command": self.locked_command,
            "favorite_users": self.favorite_users,
            "favorite_chats": self.favorite_chats,
            "banned_words": self.banned_words,
        }

    @typing.overload
    def get_file_info(self, key: typing.Literal["prefix"]) -> str: ...
    @typing.overload
    def get_file_info(
        self, key: typing.Literal["welcome", "welcome_chat"]
    ) -> str | None: ...
    @typing.overload
    def get_file_info(
        self,
        key: typing.Literal[
            "banned_words", "favorite_users", "favorite_chats", "locked_command"
        ],
    ) -> list[str]: ...
    def get_file_info(self, key: typing.Any) -> typing.Any:
        """Get a value in the community file"""
        return self.get_file_dict()[key]

    def get_file_dict(self) -> dict[str, typing.Any]:
        """Get the values stored in the community file"""
        with open(self.community_filename, "r") as file:
            return json.load(file)

    def get_banned_words(self) -> list[str]:
        """Get the banned words list"""
        return self.banned_words

    def set_prefix(self, prefix: str) -> None:
        """Set a new command prefix"""
        self.prefix = prefix
        self.update_file()

    def set_welcome_message(self, message: str | None) -> None:
        """Set a new welcome message"""
        self.message_bvn = message
        self.update_file()

    def set_welcome_chat(self, chatId: str) -> None:
        """Set a new welcome chat"""
        self.welcome_chat = chatId
        self.update_file()

    def add_favorite_users(self, value: typing.Iterable[str] | str) -> None:
        """Update the favorite users list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_users.extend(value)
        self.update_file()

    def add_favorite_chats(self, value: typing.Iterable[str] | str) -> None:
        """Update the favorite chats list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_chats.extend(value)
        self.update_file()

    def add_banned_words(self, words: typing.Iterable[str] | str) -> None:
        """Update the banned words list"""
        if isinstance(words, str):
            words = [words]
        self.banned_words.extend(words)
        self.update_file()

    def add_locked_command(self, commands: typing.Iterable[str] | str) -> None:
        """Update the locked command list"""
        if isinstance(commands, str):
            commands = [commands]
        self.locked_command.extend(commands)
        self.update_file()

    def remove_favorite_users(self, value: typing.Iterable[str] | str) -> None:
        """Remove a user from the favorite users list"""
        if isinstance(value, str):
            value = [value]
        for userId in filter(lambda u: u in self.favorite_users, value):
            self.favorite_users.remove(userId)
        self.update_file()

    def remove_favorite_chats(self, value: typing.Iterable[str] | str) -> None:
        """Remove a chat from your favorite chats list"""
        if isinstance(value, str):
            value = [value]
        for chatId in filter(lambda c: c in self.favorite_chats, value):
            self.favorite_chats.remove(chatId)
        self.update_file()

    def remove_banned_words(self, words: typing.Iterable[str] | str) -> None:
        """Remove a word from the banned words list"""
        if isinstance(words, str):
            words = [words]
        for word in filter(lambda w: w in self.banned_words, words):
            self.banned_words.remove(word)
        self.update_file()

    def remove_locked_command(self, commands: typing.Iterable[str] | str) -> None:
        """Remove a command from the locked commands list"""
        if isinstance(commands, str):
            commands = [commands]
        for command in filter(lambda c: c in self.locked_command, commands):
            self.locked_command.remove(command)
        self.update_file()

    def unset_welcome_chat(self) -> None:
        """Remove the welcome chat"""
        self.welcome_chat = None
        self.update_file()

    def is_in_staff(self, userId: str) -> bool:
        """Check if the user is a community staff member"""
        return userId in self.community_staff

    def is_leader(self, userId: str) -> bool:
        """Check if the user is a community leader"""
        return userId in self.community_leaders

    def is_curator(self, userId: str) -> bool:
        """Check if the user is a community curator"""
        return userId in self.community_curators

    def is_agent(self, userId: str) -> bool:
        """Check if the user is the community leader-agent"""
        return userId == self.community_leader_agent_id

    def copy_bubble(self, chatId: str, replyId: str, comId: int | None = None):
        """Copy the message chat-bubble"""
        comId = comId or self.community_id
        resourceUrl = self.get_message_info(chatId=chatId, messageId=replyId).json[
            "chatBubble"
        ]["resourceUrl"]
        with urllib.request.urlopen(resourceUrl) as resource:
            data = resource.read()
        response = self.request(
            "POST",
            "chat/chat-bubble/templates/107147e9-05c5-405f-8553-af65d2823457/generate",
            data=data,
            content_type="application/octet-stream",
            comId=self.comId,
        )
        bubbleId = response["chatBubble"]["bubbleId"]
        response = self.request(
            "POST",
            f"chat/chat-bubble/{bubbleId}",
            content_type="application/octet-stream",
            data=data,
            comId=comId,
        )

    def accept_role(self, requestId: str, chatId: str | None = None):
        """Accept the host transfer or promotion request"""
        with contextlib.suppress(Exception):
            if chatId:
                self.accept_host(chatId, requestId)
                return True
        with contextlib.suppress(Exception):
            self.promotion(noticeId=requestId)
            return True
        return False

    def get_staff(self, comIdOrAminoId: int | str) -> list[str]:
        """Get the community staff user IDs"""
        if isinstance(comIdOrAminoId, int):
            bot = self.client.get_community(comIdOrAminoId)
            if bot:
                return bot.community_staff.copy()
            community = self.client.get_community_info(comIdOrAminoId)
        else:
            informations = self.client.get_from_code(
                f"http://aminoapps.com/c/{comIdOrAminoId}"
            )
            community = self.client.get_community_info(informations.comId)
        try:
            community_staff_list = community.json["communityHeadList"]
            community_staff = [elem["uid"] for elem in community_staff_list]
        except KeyError:
            community_staff = []
        return community_staff

    def get_user_id(self, name_or_id: str) -> tuple[str, str] | None:
        """Fetch the user ID from a nickname or userId"""
        members = self.get_all_users(size=1).json["userProfileCount"]
        start = 0
        lower_name = None
        while start <= members:
            users = self.get_all_users(start=start, size=100).json["userProfileList"]
            for user in users:
                name = user["nickname"]
                uid = user["uid"]
                if name_or_id == name or name_or_id == uid:
                    return (name, uid)
                if not lower_name and name_or_id.lower() in name.lower():
                    lower_name = (name, uid)
            start += 100
        return lower_name if lower_name else None

    def ask_all_members(
        self, message: str, lvl: int = 20, type_bool: typing.Literal[1, 2, 3] = 1
    ) -> None:
        """Send a message to all members filtered by user level

        Parameters
        ----------
        message: str
            The message to send.
        lvl: int, optional
            The user's level comparison. Default is 20.
        type_booL: int, optional
            The comparison operator. Default is `1`.
            `1` : equality (==)
            `2` : less than or equal to (<=)
            `3` : greater than or equal to (>=)

        """
        start, size, userProfileCount = 0, 250, 250
        while start >= userProfileCount:
            users = self.get_all_users(start=start, size=size)
            values = zip(
                users.profile.userId,
                users.profile.level,
                users.profile.privilegeOfChatInviteRequest,
            )
            op = (
                operator.eq
                if type_bool == 1
                else operator.le if type_bool == 2 else operator.ge
            )
            userIds = [
                userId
                for userId, level, permission in values
                if op(level, lvl) and permission in [None, 1]
            ]
            for userId in userIds:
                with contextlib.suppress(Exception):
                    self.start_chat(userId, message=message)
                time.sleep(1)
            start += size
            userProfileCount = users.profileCount

    def ask_amino_staff(self, message: str) -> None:
        """Send a message to community staff members"""
        self.start_chat(userId=self.community_staff, message=message)

    def get_chat_id(self, linkOrTitle: str) -> str | None:
        """Fetch the chat ID from the chat link, title or shortCode"""
        with contextlib.suppress(Exception):
            link = (
                linkOrTitle
                if linkOrTitle.startswith("http")
                else f"http://aminoapps.com/p/{linkOrTitle}"
            )
            return self.get_from_code(link).objectId
        val = self.get_public_chat_threads()
        for title, chatId in zip(val.title, val.chatId):
            if (
                linkOrTitle == title
                or linkOrTitle.lower() in title.lower()
                or linkOrTitle == chatId
            ):
                return chatId
        return None

    def stop_instance(self) -> None:
        """Internal method to stop the bot from running"""
        self.marche = False

    def start_instance(self) -> None:
        """Internal method to start the bot execution"""
        self.marche = True
        threading.Thread(target=self.passive).start()

    def leave_amino(self) -> None:
        """Leave the bot from the community"""
        self.marche = False
        for chatId in self.joined_chats().chats.chatId:
            with contextlib.suppress(Exception):
                self.leave_chat(chatId)
            time.sleep(1.0)
        self.client.leave_community(comId=self.community_id)

    def check_new_member(self) -> None:
        """Welcome new community members"""
        with self.lock:
            if not (self.message_bvn or self.welcome_chat):
                return
            new_list = self.get_all_users(start=0, size=250, type="recent")
            time.sleep(1)
            self.new_users = self.new_users[:750]
            values = zip(
                new_list.profile.nickname,
                new_list.profile.userId,
                new_list.profile.commentsCount,
            )
            for name, uid, commentsCount in values:
                if commentsCount:
                    continue
                if self.message_bvn:
                    with contextlib.suppress(Exception):
                        self.comment(message=self.message_bvn, userId=uid)
                        time.sleep(3)
                if self.welcome_chat:
                    with contextlib.suppress(Exception):
                        self.send_message(
                            self.welcome_chat,
                            message=f"Welcome here \u200e\u200f\u200e\u200f@{name}!\u202c\u202d",
                            mentionUserIds=[uid],
                        )
                        time.sleep(3)
                self.new_users.append(uid)

    def welcome_new_member(self) -> None:
        """Welcome new community members"""
        self.check_new_member()

    def feature_chats(self) -> None:
        """Feature all favorite chats"""
        with self.lock:
            if not self.is_in_staff(self.userId):
                return
            for chatId in self.favorite_chats:
                with contextlib.suppress(Exception):
                    self.favorite(1, chatId=chatId)
                    time.sleep(5)

    def feature_users(self) -> None:
        """Feature all favorite users"""
        with self.lock:
            if not self.is_in_staff(self.userId):
                return
            featured = self.get_featured_users().profile.userId
            for userId in self.favorite_users:
                if userId not in featured:
                    with contextlib.suppress(Exception):
                        self.favorite(time=1, userId=userId)
                        time.sleep(5)

    def update_bot_profile(self) -> None:
        """Update the bot profile"""
        with self.lock:
            profile = self.profile
            bio = self.bio_contents
            if not bio:
                return
            if isinstance(bio, str):
                content = bio
            else:
                content = random.choice(bio)
            if content != profile.content:
                self.edit_profile(content=content)

    def get_member_level(self, userId: str) -> int:
        """Get user level"""
        return self.get_user_info(userId).level or 0

    def get_member_titles(
        self, userId: str
    ) -> list[dict[typing.Literal["title", "color"], str | None]]:
        """Get the member titles"""
        with contextlib.suppress(Exception):
            return self.get_user_info(userId).customTitles or []
        return []

    def get_wallet_amount(self) -> int:
        """Get the total coin balance of this bot"""
        return self.client.get_wallet_amount()

    def generate_transaction_id(self) -> str:
        """Generate a transaction ID"""
        return self.client.generate_transaction_id()

    @typing.overload
    def pay(
        self, coins: int, *, blogId: str, transactionId: str | None = None
    ) -> None: ...
    @typing.overload
    def pay(
        self, coins: int, *, chatId: str | None = None, transactionId: str | None = None
    ) -> None: ...
    @typing.overload
    def pay(
        self,
        coins: int,
        *,
        objectId: str | None = None,
        transactionId: str | None = None,
    ) -> None: ...
    def pay(
        self,
        coins: int,
        *,
        blogId: str | None = None,
        chatId: str | None = None,
        objectId: str | None = None,
        transactionId: str | None = None,
    ) -> None:
        """Send props to a blog, chat or wiki"""
        if not transactionId:
            transactionId = self.generate_transaction_id()
        self.send_coins(
            coins=coins,
            blogId=blogId,
            chatId=chatId,
            objectId=objectId,
            transactionId=transactionId,
        )

    @typing.overload
    def favorite(
        self, duration: typing.Literal[1, 2, 3] = 1, *, userId: str
    ) -> None: ...
    @typing.overload
    def favorite(
        self, duration: typing.Literal[1, 2, 3] = 1, *, chatId: str
    ) -> None: ...
    @typing.overload
    def favorite(
        self, duration: typing.Literal[1, 2, 3] = 1, *, blogId: str
    ) -> None: ...
    @typing.overload
    def favorite(
        self, duration: typing.Literal[1, 2, 3] = 1, *, wikiId: str
    ) -> None: ...
    def favorite(
        self,
        duration: typing.Literal[1, 2, 3] = 1,
        *,
        userId: str | None = None,
        chatId: str | None = None,
        blogId: str | None = None,
        wikiId: str | None = None,
    ) -> None:
        """Feature a user, chat, blog or wiki"""
        self.feature(
            duration=duration,
            userId=userId,
            chatId=chatId,
            blogId=blogId,
            wikiId=wikiId,
        )

    @typing.overload
    def unfavorite(self, *, userId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, chatId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, blogId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, wikiId: str) -> None: ...
    def unfavorite(
        self,
        userId: str | None = None,
        chatId: str | None = None,
        blogId: str | None = None,
        wikiId: str | None = None,
    ) -> None:
        """Unfeature a user, chat, blog or wiki"""
        self.unfeature(userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)

    @typing.overload
    def join_chatroom(self, chat: str) -> bool: ...
    @typing.overload
    def join_chatroom(self, *, chatId: str) -> bool: ...
    def join_chatroom(self, chat: str | None = None, chatId: str | None = None) -> bool:
        """Join to a chat

        Parameters
        ----------
        chat : str, optional
            The chat link or title
        chatId : str, optional
            The chat ID.

        """
        if chat:
            with contextlib.suppress(Exception):
                chatId = self.get_from_code(chat).objectId
        if chatId:
            with contextlib.suppress(Exception):
                self.join_chat(chatId)
                return True
        chats = self.get_public_chat_threads()
        if not chat:
            return False
        for title, chatId in zip(chats.title, chats.chatId):
            if chat == title:
                self.join_chat(chatId)
                return True
            if chat.lower() in title.lower() or chat == chatId:
                self.join_chat(chatId)
                return True
        return False

    # start_voice_chat
    # end_voice_chat
    # start_avatar_chat
    # end_avatar_chat
    # start_video_chat
    # end_video_chat
    # start_screen_room
    # end_screen_room
    # join_voice_chat
    # join_avatar_chat
    # join_video_chat
    # join_screen_room

    def get_chats(self, type: str = "recommended", start: int = 0, size: int = 25):
        """Get public chats"""
        return self.get_public_chat_threads(type=type, start=start, size=size)

    def join_all_chat(self) -> None:
        """Join all popular chats"""
        chats = self.get_public_chat_threads(type="recommended", start=0, size=100)
        values = zip(chats.chatId, chats.membersCount)
        for chatId, membersCount in values:
            if membersCount == 1000:
                continue
            with contextlib.suppress(Exception):
                self.join_chat(chatId)

    def leave_all_chats(self) -> None:
        """Join all popular chats"""
        chats = self.get_public_chat_threads(type="recommended", start=0, size=100)
        for chatId in chats.chatId:
            with contextlib.suppress(Exception):
                self.leave_chat(chatId)
            time.sleep(1)

    def follow_user(self, userId: str) -> None:
        """Follow a user or users"""
        self.follow(userId)

    def unfollow_user(self, userId: str):
        """Unfollow a user"""
        self.unfollow(userId)

    def add_title(self, userId: str, title: str, color: str | None = None) -> None:
        """Add a title to a user

        Parameters
        ----------
        userId : str
            The user ID to add the title.
        title : str
            The title name.
        color : str, optional
            The hex color for the new title. e.g (#ffffff). Default is #ffffff.

        """
        color = color or "#ffffff"
        member = self.get_member_titles(userId)
        titles, colors = [title], [color]
        with contextlib.suppress(TypeError):
            titles = [i["title"] for i in member] + [title]
            colors = [i["color"] for i in member] + [color]
        self.edit_titles(userId, titles, colors)

    def remove_title(self, userId: str, title: str) -> None:
        """Remove a title to a user

        Parameters
        ----------
        userId : str
            The user ID to remove a title.
        title : str
            The title name to remove.

        """
        customTitles = self.get_member_titles(userId)
        titles = []
        colors = []
        for t in customTitles:
            if title not in t["title"]:
                titles.append(t["title"])
                colors.append(t["color"])
        self.edit_titles(userId, titles, colors)

    def passive(self) -> None:
        """Internal method to perform bot activities"""
        with print_exception(Exception):
            self.update_bot_profile()
            self.feature_chats()
            self.feature_users()
        j = 0
        k = 0
        while self.marche:
            if self.welcome_chat or self.message_bvn:
                self.welcome_new_member()
            with print_exception(Exception):
                bio_contents = self.bio_contents
                if isinstance(bio_contents, list):
                    self.edit_profile(content=random.choice(bio_contents))
                elif isinstance(bio_contents, str):
                    self.edit_profile(content=bio_contents)
            if j >= 240:
                self.feature_chats()
                j = 0
            if k >= 2880:
                with print_exception(Exception):
                    self.feature_users()
                k = 0
            if self.activity:
                startTime = int(time.time())
                with print_exception(Exception):
                    self.send_active_obj(startTime=startTime, endTime=startTime + 300)
            time.sleep(30)
            j += 1
            k += 1
