import os
import time
import random
import json
import urllib.request
import operator
import threading
import typing
import contextlib

from aminofix import ACM, SubClient  # type: ignore
from aminofix.lib.util.exceptions import CheckException  # type: ignore
from aminofix.lib.util.objects import ThreadList, UserProfile  # type: ignore

from .utils import PATH_AMINO, PATH_UTILITIES, print_exception
if typing.TYPE_CHECKING:
    from .botamino import BotAmino

__all__ = ('Bot',)


class Bot(SubClient, ACM):  # type: ignore
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

    def __init__(
        self,
        client: 'BotAmino',
        community: typing.Union[int, str],
        prefix: str = "!",
        bio: typing.Optional[typing.Union[typing.List[str], str]] = None,
        activity: bool = False
    ) -> None:
        self.client = client
        self.prefix = prefix
        self.bio_contents = bio
        self.activity = activity
        self.marche = True
        comId, aminoId = None, None
        if isinstance(community, int):
            comId = community
        else:
            aminoId = community
        # ACM initializer not required
        super().__init__(  # type: ignore
            comId=comId,  # type: ignore
            aminoId=aminoId,  # type: ignore
            profile=client.profile,
            deviceId=client.device_id,
            autoDevice=client.autoDevice,
            proxies=client.proxies,  # # type: ignore
            certificatePath=client.certificatePath  # type: ignore
        )
        self.community_amino_id = typing.cast(str, self.community.aminoId)  # type: ignore
        self.community_id = typing.cast(int, self.community.comId)  # type: ignore
        self.community_leader_agent_id = typing.cast(str, self.community.agent.userId)  # type: ignore
        self.community_name = typing.cast(str, self.community.name)  # type: ignore
        # Set up bot for community staff
        self.community_leaders: typing.List[str] = []
        self.community_curators: typing.List[str] = []
        with contextlib.suppress(Exception):
            self.community_leaders.extend(self.get_all_users("leader").profile.userId)  # type: ignore
            self.community_curators.extend(self.get_all_users("curator").profile.userId)  # type: ignore
        self.community_staff: typing.List[str] = list(set(self.community_leaders + self.community_curators))
        # Set up bot for community files
        if not os.path.exists(self.community_filename):
            self.create_community_file()
        config = self.get_file_dict()
        for key, value in self.create_dict().items():
            config.setdefault(key, value)
        self.update_file(config)
        # Set up community config
        self.banned_words = self.get_file_info("banned_words")
        self.locked_command = self.get_file_info("locked_command")
        self.message_bvn = self.get_file_info("welcome")
        self.welcome_chat = self.get_file_info("welcome_chat")
        self.prefix = self.get_file_info("prefix")
        self.favorite_users = self.get_file_info("favorite_users")
        self.favorite_chats = self.get_file_info("favorite_chats")
        self.update_file()
        self.activity_status("on")
        self.new_users = typing.cast(typing.List[str], self.get_all_users(start=0, size=30, type="recent").profile.userId)  # type: ignore

        # fixed SubClient annotations
        self.comId: int
        # fixed Client annotations
        self.certificatePath: typing.Optional[str]
        self.device_id: str
        self.json: typing.Dict[str, typing.Any]
        self.proxies: typing.Optional[typing.Dict[str, str]]
        self.secret: typing.Optional[str]
        self.sid: str
        self.userId: str
        self.account: UserProfile  # type: ignore  # incorrect object (account not profile)
        self.profile: UserProfile  # type: ignore

    @property
    def community_filename(self) -> str:
        """Get the bot's community filename"""
        for folder in (PATH_UTILITIES, PATH_AMINO):
            with contextlib.suppress(OSError):
                os.mkdir(folder)
        return os.path.join(PATH_AMINO, f"{self.community_amino_id}.json")

    def create_community_file(self) -> None:
        """Create a new community filename"""
        with open(self.community_filename, 'w', encoding='utf8') as file:
            json.dump(self.create_dict(), file, indent=4)

    def update_file(self, data: typing.Optional[typing.Dict[str, typing.Any]] = None) -> None:
        """Update the community file data with new information"""
        data = data or self.get_dict()
        with open(self.community_filename, "w") as file:
            json.dump(data, file, indent=4)

    def create_dict(self) -> typing.Dict[str, typing.Any]:
        """Create an empty dataset for a community file"""
        return {
            "welcome": None,
            "prefix": self.prefix,
            "welcome_chat": None,
            "locked_command": [],
            "favorite_users": [],
            "favorite_chats": [],
            "banned_words": []
        }

    def get_dict(self) -> typing.Dict[str, typing.Any]:
        """Create a full dataset for a community file"""
        return {
            "welcome": self.message_bvn,
            "prefix": self.prefix,
            "welcome_chat": self.welcome_chat,
            "locked_command": self.locked_command,
            "favorite_users": self.favorite_users,
            "favorite_chats": self.favorite_chats,
            "banned_words": self.banned_words
        }

    @typing.overload
    def get_file_info(self, key: typing.Literal["prefix"]) -> str: ...
    @typing.overload
    def get_file_info(self, key: typing.Literal["welcome", "welcome_chat"]) -> typing.Optional[str]: ...
    @typing.overload
    def get_file_info(self, key: typing.Literal["banned_words", "favorite_users", "favorite_chats", "locked_command"]) -> typing.List[str]: ...
    def get_file_info(self, key: str) -> typing.Any:
        """Get a value in the community file"""
        return self.get_file_dict()[key]

    def get_file_dict(self) -> typing.Dict[str, typing.Any]:
        """Get the values stored in the community file"""
        with open(self.community_filename, "r") as file:
            return typing.cast(typing.Dict[str, typing.Any], json.load(file))

    def get_banned_words(self) -> typing.List[str]:
        """Get the banned words list"""
        return self.banned_words

    def set_prefix(self, prefix: str) -> None:
        """Set a new command prefix"""
        self.prefix = prefix
        self.update_file()

    def set_welcome_message(self, message: str) -> None:
        """Set a new welcome message"""
        self.message_bvn = message.replace('"', '“')
        self.update_file()

    def set_welcome_chat(self, chatId: str) -> None:
        """Set a new welcome chat"""
        self.welcome_chat = chatId
        self.update_file()

    def add_favorite_users(self, value: typing.Union[typing.List[str], str]) -> None:
        """Update the favorite users list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_users.extend(value)
        self.update_file()

    def add_favorite_chats(self, value: typing.Union[typing.List[str], str]) -> None:
        """Update the favorite chats list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_chats.extend(value)
        self.update_file()

    def add_banned_words(self, words: typing.Union[typing.List[str], str]) -> None:
        """Update the banned words list"""
        if isinstance(words, str):
            words = [words]
        self.banned_words.extend(words)
        self.update_file()

    def add_locked_command(self, commands: typing.Union[typing.List[str], str]) -> None:
        """Update the locked command list"""
        if isinstance(commands, str):
            commands = [commands]
        self.locked_command.extend(commands)
        self.update_file()

    def remove_favorite_users(self, value: typing.Union[typing.List[str], str]) -> None:
        """Remove a user from the favorite users list"""
        if isinstance(value, str):
            value = [value]
        for userId in filter(lambda u: u in self.favorite_users, value):
            self.favorite_users.remove(userId)
        self.update_file()

    def remove_favorite_chats(self, value: typing.Union[typing.List[str], str]) -> None:
        """Remove a chat from your favorite chats list"""
        if isinstance(value, str):
            value = [value]
        for chatId in filter(lambda c: c in self.favorite_chats, value):
            self.favorite_chats.remove(chatId)
        self.update_file()

    def remove_banned_words(self, words: typing.Union[typing.List[str], str]) -> None:
        """Remove a word from the banned words list"""
        if isinstance(words, str):
            words = [words]
        for word in filter(lambda w: w in self.banned_words, words):
            self.banned_words.remove(word)
        self.update_file()

    def remove_locked_command(self, commands: typing.Union[typing.List[str], str]) -> None:
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

    def is_in_staff(self, uid: str) -> bool:
        """Check if the user is a community staff member"""
        return uid in self.community_staff

    def is_leader(self, uid: str) -> bool:
        """Check if the user is a community leader"""
        return uid in self.community_leaders

    def is_curator(self, uid: str) -> bool:
        """Check if the user is a community curator"""
        return uid in self.community_curators

    def is_agent(self, uid: str) -> bool:
        """Check if the user is the community leader-agent"""
        return uid == self.community_leader_agent_id

    def copy_bubble(self, chatId: str, replyId: str, comId: typing.Optional[int] = None) -> None:
        """Copy the message chat-bubble"""
        comId = comId or self.community_id
        headers = typing.cast(typing.Dict[str, typing.Any], self.parse_headers(type='application/octet-stream'))  # type: ignore
        resourceUrl = self.get_message_info(chatId=chatId, messageId=replyId).json["chatBubble"]["resourceUrl"]
        with urllib.request.urlopen(resourceUrl) as resource:
            data = typing.cast(bytes, resource.read())
        response = self.session.post(f"{self.api}/x{comId}/s/chat/chat-bubble/templates/107147e9-05c5-405f-8553-af65d2823457/generate", data=data, headers=headers, proxies=self.proxies, verify=self.certificatePath)
        with contextlib.suppress(Exception):
            bubbleId = response.json()['chatBubble']['bubbleId']
            response = self.session.post(f"{self.api}/{comId}/s/chat/chat-bubble/{bubbleId}", data=data, headers=headers, proxies=self.proxies, verify=self.certificatePath)
            _ = response.json()
            return
        CheckException(response.text)

    @typing.overload
    def accept_role(self, rid: str) -> bool: ...
    @typing.overload
    def accept_role(self, rid: str, chatId: typing.Optional[str]) -> bool: ...
    def accept_role(self, rid: str, chatId: typing.Optional[str] = None) -> bool:
        """Accept the host transfer or promotion request"""
        with contextlib.suppress(Exception):
            self.accept_organizer(typing.cast(str, chatId), rid)
            return True
        with contextlib.suppress(Exception):
            self.promotion(noticeId=rid)
            return True
        return False

    def get_staff(self, comIdOrAminoId: typing.Union[int, str]) -> typing.List[str]:
        """Get the community staff user IDs"""
        if isinstance(comIdOrAminoId, int):
            if comIdOrAminoId in self.client.communaute:
                return self.client.get_community(comIdOrAminoId).community_staff.copy()
            community = self.client.get_community_info(comIdOrAminoId)  # type: ignore
        else:
            informations = self.client.get_from_code(f"http://aminoapps.com/c/{comIdOrAminoId}")
            community = self.client.get_community_info(informations.comId)  # type: ignore
        try:
            community_staff_list = community.json["communityHeadList"]
            community_staff = [elem["uid"] for elem in community_staff_list]
        except KeyError:
            community_staff = []
        return community_staff

    def get_user_id(self, name_or_id: str) -> typing.Optional[typing.Tuple[str, str]]:
        """Fetch the user ID from a nickname or userId"""
        members = self.get_all_users(size=1).json['userProfileCount']
        start = 0
        lower_name = None
        while start <= members:
            users = self.get_all_users(start=start, size=100).json['userProfileList']
            for user in users:
                name = user['nickname']
                uid = user['uid']
                if name_or_id == name or name_or_id == uid:
                    return (name, uid)
                if not lower_name and name_or_id.lower() in name.lower():
                    lower_name = (name, uid)
            start += 100
        return lower_name if lower_name else None

    def ask_all_members(self, message: str, lvl: int = 20, type_bool: typing.Literal[1, 2, 3] = 1) -> None:
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
            values = typing.cast(typing.Iterable[typing.Tuple[str, int, int]], zip(users.profile.userId, users.profile.level, users.profile.privilegeOfChatInviteRequest))  # type: ignore
            op = operator.eq if type_bool == 1 else operator.le if type_bool == 2 else operator.ge
            userIds = [userId for userId, level, permission in values if op(level, lvl) and permission in [None, 1]]
            for userId in userIds:
                with contextlib.suppress(Exception):
                    self.start_chat(userId, message=message)  # type: ignore
                time.sleep(1)
            start += size
            userProfileCount = typing.cast(int, users.userProfileCount)

    def ask_amino_staff(self, message: str) -> None:
        """Send a message to community staff members"""
        self.start_chat(userId=self.community_staff, message=message)  # type: ignore

    def get_chat_id(self, linkOrTitle: str) -> typing.Optional[str]:
        """Fetch the chat ID from the chat link, title or shortCode"""
        with contextlib.suppress(Exception):
            link = linkOrTitle if linkOrTitle.startswith('http') else f"http://aminoapps.com/p/{linkOrTitle}"
            return typing.cast(str, self.get_from_code(link).objectId)  # type: ignore
        val = self.get_public_chat_threads()
        for title, chatId in typing.cast(typing.Iterable[typing.Tuple[str, str]], zip(val.title, val.chatId)):  # type: ignore
            if linkOrTitle == title or linkOrTitle.lower() in title.lower() or linkOrTitle == chatId:
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
        for chatId in typing.cast(typing.List[str], self.get_chat_threads().chatId):  # type: ignore
            with contextlib.suppress(Exception):
                self.leave_chat(chatId)
            time.sleep(1.0)
        self.client.leave_community(comId=self.community_id)  # type: ignore

    def check_new_member(self) -> None:
        """Welcome new community members"""
        if not (self.message_bvn or self.welcome_chat):
            return
        new_list = self.get_all_users(start=0, size=250, type="recent")
        time.sleep(1)
        self.new_users = self.new_users[:750]
        values = typing.cast(typing.Iterable[typing.Tuple[str, str, int]], zip(new_list.profile.nickname, new_list.profile.userId, new_list.profile.commentsCount))  # type: ignore
        for name, uid, commentsCount in values:
            if commentsCount:
                continue
            if self.message_bvn:
                with contextlib.suppress(Exception):
                    self.comment(message=self.message_bvn, userId=uid)
                    time.sleep(2.0)
            if self.welcome_chat:
                with contextlib.suppress(Exception):
                    self.send_message(self.welcome_chat, message=f"Welcome here \u200e\u200f\u200e\u200f@{name}!\u202c\u202d", mentionUserIds=[uid])  # type: ignore
                    time.sleep(2.0)
            self.new_users.append(uid)

    def welcome_new_member(self) -> None:
        """Welcome new community members"""
        self.check_new_member()

    def feature_chats(self) -> None:
        """Feature all favorite chats"""
        if not self.is_in_staff(self.userId):
            return
        for chatId in self.favorite_chats:
            with contextlib.suppress(Exception):
                self.favorite(time=1, chatId=chatId)
                time.sleep(5)

    def feature_users(self) -> None:
        """Feature all favorite users"""
        if not self.is_in_staff(self.userId):
            return
        featured = typing.cast(typing.List[str], self.get_featured_users().profile.userId)  # type: ignore
        for userId in self.favorite_users:
            if userId not in featured:
                with contextlib.suppress(Exception):
                    self.favorite(time=1, userId=userId)
                    time.sleep(2.0)

    def get_member_level(self, uid: str) -> int:
        """Get user level"""
        return self.get_user_info(uid).level or 0  # type: ignore

    def get_member_titles(self, uid: str) -> typing.List[typing.Dict[typing.Literal['title', 'color'], str]]:
        """Get the member titles"""
        with contextlib.suppress(Exception):
            return self.get_user_info(uid).customTitles or []  # type: ignore
        return []

    def get_wallet_amount(self) -> int:
        """Get the total coin balance of this bot"""
        return self.client.get_wallet_amount()

    def generate_transaction_id(self) -> str:
        """Generate a transaction ID"""
        return self.client.generate_transaction_id()

    @typing.overload
    def pay(
        self,
        coins: int,
        *,
        blogId: str,
        transactionId: typing.Optional[str] = None
    ) -> None: ...
    @typing.overload
    def pay(
        self,
        coins: int,
        *,
        chatId: typing.Optional[str] = None,
        transactionId: typing.Optional[str] = None
    ) -> None: ...
    @typing.overload
    def pay(
        self,
        coins: int,
        *,
        objectId: typing.Optional[str] = None,
        transactionId: typing.Optional[str] = None
    ) -> None: ...
    def pay(
        self,
        coins: int,
        *,
        blogId: typing.Optional[str] = None,
        chatId: typing.Optional[str] = None,
        objectId: typing.Optional[str] = None,
        transactionId: typing.Optional[str] = None
    ) -> None:
        """Send props to a blog, chat or wiki"""
        if not transactionId:
            transactionId = self.generate_transaction_id()
        self.send_coins(coins=coins, blogId=blogId, chatId=chatId, objectId=objectId, transactionId=transactionId)  # type: ignore

    @typing.overload
    def favorite(self, time: typing.Literal[1, 2, 3] = 1, *, userId: str) -> None: ...
    @typing.overload
    def favorite(self, time: typing.Literal[1, 2, 3] = 1, *, chatId: str) -> None: ...
    @typing.overload
    def favorite(self, time: typing.Literal[1, 2, 3] = 1, *, blogId: str) -> None: ...
    @typing.overload
    def favorite(self, time: typing.Literal[1, 2, 3] = 1, *, wikiId: str) -> None: ...
    def favorite(self, time: typing.Literal[1, 2, 3] = 1, *, userId: typing.Optional[str] = None, chatId: typing.Optional[str] = None, blogId: typing.Optional[str] = None, wikiId: typing.Optional[str] = None) -> None:
        """Feature a user, chat, blog or wiki"""
        self.feature(time=time, userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)  # type: ignore

    @typing.overload
    def unfavorite(self, *, userId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, chatId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, blogId: str) -> None: ...
    @typing.overload
    def unfavorite(self, *, wikiId: str) -> None: ...
    def unfavorite(self, userId: typing.Optional[str] = None, chatId: typing.Optional[str] = None, blogId: typing.Optional[str] = None, wikiId: typing.Optional[str] = None) -> None:
        """Unfeature a user, chat, blog or wiki"""
        self.unfeature(userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)  # type: ignore

    @typing.overload
    def join_chatroom(self, chat: str) -> bool: ...
    @typing.overload
    def join_chatroom(self, *, chatId: str) -> bool: ...
    def join_chatroom(self, chat: typing.Optional[str] = None, chatId: typing.Optional[str] = None) -> bool:
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
                chatId = typing.cast(str, self.get_from_code(chat).objectId)  # type: ignore
        if chatId:
            with contextlib.suppress(Exception):
                self.join_chat(typing.cast(str, chatId))  # type: ignore
                return True
        chats = self.get_public_chat_threads()
        if not chat:
            return False
        for title, chatId in typing.cast(typing.Iterable[typing.Tuple[str, str]], zip(chats.title, chats.chatId)):  # type: ignore
            if chat == title:
                self.join_chat(chatId)
                return True
            if chat.lower() in title.lower() or chat == chatId:
                self.join_chat(chatId)
                return True
        return False

    def start_screen_room(self, chatId: str, joinType: int = 1) -> None:
        """Start a screening room in the chat

        Parameters
        ----------
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        self.client.start_screen_room(comId=self.community_id, chatId=chatId, joinType=joinType)

    def start_video_chat(self, chatId: str, joinType: int = 1) -> None:
        """Start a live stream in the chat

        Parameters
        ----------
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        self.client.join_video_chat(comId=self.community_id, chatId=chatId, joinType=joinType)  # type: ignore

    def start_voice_room(self, chatId: str, joinType: int = 1) -> None:
        """Start a voice room in the chat

        Parameters
        ----------
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        self.client.join_voice_chat(comId=self.community_id, chatId=chatId, joinType=joinType)  # type: ignore

    def join_screen_room(self, chatId: str, joinType: int = 1) -> None:
        """Join in the screening room

        Parameters
        ----------
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        self.client.join_video_chat_as_viewer(comId=self.community_id, chatId=chatId, joinType=joinType)  # type: ignore

    def get_chats(self, type: str = "recommended", start: int = 0, size: int = 250) -> ThreadList:
        """Get public chats"""
        return self.get_public_chat_threads(type=type, start=start, size=size)

    def join_all_chat(self) -> None:
        """Join all popular chats"""
        chats = self.get_public_chat_threads(type="recommended", start=0, size=100)
        values = typing.cast(typing.Iterable[typing.Tuple[str, int]], zip(chats.chatId, chats.membersCount))  # type: ignore
        for chatId, membersCount in values:
            if membersCount == 1000:
                continue
            with contextlib.suppress(Exception):
                self.join_chat(chatId)

    def leave_all_chats(self) -> None:
        """Join all popular chats"""
        chats = self.get_public_chat_threads(type="recommended", start=0, size=100)
        for chatId in typing.cast(typing.List[str], chats.chatId):  # type: ignore
            with contextlib.suppress(Exception):
                self.leave_chat(chatId)
            time.sleep(1)

    def follow_user(self, uid: typing.Union[str, typing.List[str]]) -> None:
        """Follow a user or users"""
        self.follow(uid)  # type: ignore

    def unfollow_user(self, uid: str) -> None:
        """Unfollow a user"""
        self.unfollow(uid)

    def add_title(self, uid: str, title: str, color: typing.Optional[str] = None) -> None:
        """Add a title to a user

        Parameters
        ----------
        uid : str
            The user ID to add the title.
        title : str
            The title name.
        color : str, optional
            The hex color for the new title. e.g (#ffffff). Default is #ffffff.

        """
        color = color or "#ffffff"
        member = self.get_member_titles(uid)
        titles, colors = [title], [color]
        with contextlib.suppress(TypeError):
            titles = [i['title'] for i in member] + [title]
            colors = [i['color'] for i in member] + [color]
        self.edit_titles(uid, titles, colors)  # type: ignore

    def remove_title(self, uid: str, title: str) -> None:
        """Remove a title to a user

        Parameters
        ----------
        uid : str
            The user ID to remove a title.
        title : str
            The title name to remove.

        """
        customTitles = self.get_member_titles(uid)
        titles: typing.List[str] = []
        colors: typing.List[str] = []
        for t in customTitles:
            if title not in t["title"]:
                titles.append(t["title"])
                colors.append(t["color"])
        self.edit_titles(uid, titles, colors)  # type: ignore

    def passive(self) -> None:
        """Internal method to perform bot activities"""
        with print_exception(Exception):
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
                    self.edit_profile(content=random.choice(bio_contents))  # type: ignore
                elif isinstance(bio_contents, str):
                    self.edit_profile(content=bio_contents)  # type: ignore
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
                    self.send_active_obj(startTime=startTime, endTime=startTime + 300)  # type: ignore
            time.sleep(30)
            j += 1
            k += 1
