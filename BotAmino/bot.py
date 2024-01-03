# python future feature compatibility (v3.10)
from __future__ import annotations
# native packages
from os import mkdir, path
from time import sleep
from time import time
from random import choice
from json import dump, load
from urllib.request import urlopen
from threading import Thread
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, TYPE_CHECKING, cast, overload
from contextlib import suppress
# external packages
from aminofix import ACM, SubClient
from aminofix.lib.util.exceptions import CheckException
# internal
from .utils import PATH_AMINO, PATH_UTILITIES, print_exception
# only type-checkers
if TYPE_CHECKING:
    from aminofix.lib.util.objects import Community, ThreadList
    from .botamino import BotAmino

__all__ = ('Bot',)


class Bot(SubClient, ACM):
    """Represents a community bot manager

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
        client: BotAmino,
        community: Union[int, str],
        prefix: str = "!",
        bio: Optional[Union[List[str], str]] = None,
        activity: bool = False
    ) -> None:
        self.client = client
        self.marche = True
        self.prefix = prefix
        self.bio_contents = bio
        self.activity = activity
        if isinstance(community, int):
            self.community_id = community
            self.community: Community = self.client.get_community_info(comId=self.community_id)  # type: ignore
            self.community_amino_id = cast(str, self.community.aminoId)
        else:
            self.community_amino_id = community
            informations = self.client.get_from_code(f"http://aminoapps.com/c/{community}")
            self.community_id: int = informations.json["extensions"]["community"]["ndcId"]
            self.community: Community = self.client.get_community_info(comId=self.community_id)  # type: ignore
        self.community_name = self.community.name
        super().__init__(comId=self.community_id, profile=self.client.profile)  # type: ignore
        try:
            self.community_leader_agent_id = cast(str, self.community.agent.userId)
        except Exception:
            self.community_leader_agent_id = "-"
        self.community_staff: List[str] = []
        self.community_leaders: List[str] = []
        self.community_curators: List[str] = []
        with suppress(Exception):
            self.community_leaders.extend(self.get_all_users("leader").profile.userId)
            self.community_curators.extend(self.get_all_users("curator").profile.userId)
        self.community_staff.extend(set(self.community_leaders + self.community_curators))
        if not path.exists(self.community_filename):
            self.create_community_file()
        old_dict = self.get_file_dict()
        new_dict = self.create_dict()
        for k, v in new_dict.items():
            if k not in old_dict:
                old_dict[k] = v
        self.update_file(old_dict)
        self.banned_words: List[str] = self.get_file_info("banned_words")
        self.locked_command: List[str] = self.get_file_info("locked_command")
        self.message_bvn: Optional[str] = self.get_file_info("welcome")
        self.welcome_chat: Optional[str] = self.get_file_info("welcome_chat")
        self.prefix = cast(str, self.get_file_info("prefix"))
        self.favorite_users: List[str] = self.get_file_info("favorite_users")
        self.favorite_chats: List[str] = self.get_file_info("favorite_chats")
        self.update_file()
        self.activity_status("on")
        self.new_users: List[str] = self.get_all_users(start=0, size=30, type="recent").profile.userId

    @property
    def community_filename(self) -> str:
        """Get the bot's community filename"""
        for folder in (PATH_UTILITIES, PATH_AMINO):
            with suppress(OSError):
                mkdir(folder)
        return path.join(PATH_AMINO, f"{self.community_amino_id}.json")

    def create_community_file(self) -> None:
        """Create a new community filename"""
        with open(self.community_filename, 'w', encoding='utf8') as file:
            dump(self.create_dict(), file, indent=4)

    def create_dict(self) -> Dict[str, Any]:
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

    def get_dict(self) -> Dict[str, Any]:
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

    def update_file(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Update the community file data with new information"""
        data = data or self.get_dict()
        with open(self.community_filename, "w") as file:
            dump(data, file, indent=4)

    def get_file_info(self, key: str) -> Any:
        """Get a value in the community file"""
        with open(self.community_filename, "r") as file:
            return load(file)[key]

    def get_file_dict(self) -> Dict[str, Any]:
        """Get the values stored in the community file"""
        with open(self.community_filename, "r") as file:
            return load(file)

    def get_banned_words(self) -> List[str]:
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

    def add_favorite_users(self, value: Union[List[str], str]) -> None:
        """Update the favorite users list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_users.extend(value)
        self.update_file()

    def add_favorite_chats(self, value: Union[List[str], str]) -> None:
        """Update the favorite chats list"""
        if isinstance(value, str):
            value = [value]
        self.favorite_chats.extend(value)
        self.update_file()

    def add_banned_words(self, words: Union[List[str], str]) -> None:
        """Update the banned words list"""
        if isinstance(words, str):
            words = [words]
        self.banned_words.extend(words)
        self.update_file()

    def add_locked_command(self, commands: Union[List[str], str]) -> None:
        """Update the locked command list"""
        if isinstance(commands, str):
            commands = [commands]
        self.locked_command.extend(commands)
        self.update_file()

    def remove_favorite_users(self, value: Union[List[str], str]) -> None:
        """Remove a user from the favorite users list"""
        if isinstance(value, str):
            value = [value]
        for userId in filter(lambda u: u in self.favorite_users, value):
            self.favorite_users.remove(userId)
        self.update_file()

    def remove_favorite_chats(self, value: Union[List[str], str]) -> None:
        """Remove a chat from your favorite chats list"""
        if isinstance(value, str):
            value = [value]
        for chatId in filter(lambda c: c in self.favorite_chats, value):
            self.favorite_chats.remove(chatId)
        self.update_file()

    def remove_banned_words(self, words: Union[List[str], str]) -> None:
        """Remove a word from the banned words list"""
        if isinstance(words, str):
            words = [words]
        for word in filter(lambda w: w in self.banned_words, words):
            self.banned_words.remove(word)
        self.update_file()

    def remove_locked_command(self, commands: Union[List[str], str]) -> None:
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

    def copy_bubble(self, chatId: str, replyId: str, comId: Optional[int] = None) -> None:
        """Copy the message chat-bubble"""
        comId = comId or self.community_id
        headers = self.parse_headers(type='application/octet-stream')
        resourceUrl = self.get_message_info(chatId=chatId, messageId=replyId).json["chatBubble"]["resourceUrl"]
        with urlopen(resourceUrl) as resource:
            data: bytes = resource.read()
        response = self.session.post(f"{self.api}/x{comId}/s/chat/chat-bubble/templates/107147e9-05c5-405f-8553-af65d2823457/generate", data=data, headers=headers, proxies=self.proxies, verify=self.certificatePath)
        with suppress(Exception):
            bubbleId = response.json()['chatBubble']['bubbleId']
            response = self.session.post(f"{self.api}/{comId}/s/chat/chat-bubble/{bubbleId}", data=data, headers=headers, proxies=self.proxies, verify=self.certificatePath)
            _ = response.json()
            return
        CheckException(response.text)

    @overload
    def accept_role(self, rid: str) -> bool: ...
    @overload
    def accept_role(self, rid: str, chatId: Optional[str]) -> bool: ...
    def accept_role(self, rid: str, chatId: Optional[str] = None) -> bool:
        """Accept the host transfer or promotion request"""
        with suppress(Exception):
            self.accept_organizer(cast(str, chatId), rid)
            return True
        with suppress(Exception):
            self.promotion(noticeId=rid)
            return True
        return False

    def get_staff(self, comIdOrAminoId: Union[int, str]) -> List[str]:
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

    def get_user_id(self, name_or_id: str) -> Optional[Tuple[str, str]]:
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

    def ask_all_members(self, message: str, lvl: int = 20, type_bool: int = 1) -> None:
        """Send a message to all members filtered by user level

        Parameters
        ----------
        message: str
            The message to send.
        lvl: int, optional
            The user's level comparison. Default is 20.
        type_booL: int, optional
            The comparison operator: 1 for equality (==), 2 for less than or equal to (<=),
            3 for greater than or equal to (>=). Default is 1.

        """
        def ask(uid):
            with suppress(Exception):
                self.start_chat(uid, message=message)
        size = self.get_all_users(start=0, size=1, type="recent").json['userProfileCount']
        st = 0
        while size > 0:
            value = size
            if value > 100:
                value = 100
            users = self.get_all_users(start=st, size=value)
            if type_bool == 1:
                [ask(user["uid"]) for user in users.json['userProfileList'] if user['level'] == lvl]
            elif type_bool == 2:
                [ask(user["uid"]) for user in users.json['userProfileList'] if user['level'] <= lvl]
            elif type_bool == 3:
                [ask(user["uid"]) for user in users.json['userProfileList'] if user['level'] >= lvl]
            size -= 100
            st += 100

    def ask_amino_staff(self, message: str) -> None:
        """Send a message to community staff members"""
        self.start_chat(userId=self.community_staff, message=message)

    def get_chat_id(self, shortCodeOrTitle: str) -> Optional[str]:
        """Fetch the chat ID from the chat link, title or shortCode"""
        with suppress(Exception):
            link = shortCodeOrTitle if shortCodeOrTitle.startswith('http') else f"http://aminoapps.com/p/{shortCodeOrTitle}"
            return cast(str, self.get_from_code(link).objectId)
        val = self.get_public_chat_threads()
        for title, chat_id in zip(val.title, val.chatId):
            if shortCodeOrTitle == title:
                return chat_id
            if shortCodeOrTitle.lower() in title.lower() or shortCodeOrTitle == chat_id:
                return chat_id
        return None

    def stop_instance(self) -> None:
        """Internal method to stop the bot from running"""
        self.marche = False

    def start_instance(self) -> None:
        """Internal method to start the bot execution"""
        self.marche = True
        Thread(target=self.passive).start()

    def leave_amino(self) -> None:
        """Leave the bot from the community"""
        self.marche = False
        for chatId in self.get_chat_threads().chatId:
            with suppress(Exception):
                self.leave_chat(chatId)
            sleep(1.0)
        self.client.leave_community(comId=self.community_id)  # type: ignore

    def check_new_member(self) -> None:
        """Welcome new community members"""
        if not (self.message_bvn or self.welcome_chat):
            return
        new_list = self.get_all_users(start=0, size=250, type="recent")
        sleep(1)
        self.new_users = self.new_users[:750]
        for name, uid, commentsCount in zip(new_list.profile.nickname, new_list.profile.userId, new_list.profile.commentsCount):
            if commentsCount:
                continue
            if self.message_bvn:
                with suppress(Exception):
                    self.comment(message=self.message_bvn, userId=uid)
                    sleep(2.0)
            if self.welcome_chat:
                with suppress(Exception):
                    self.send_message(self.welcome_chat, message=f"Welcome here \u200e\u200f\u200e\u200f@{name}!\u202c\u202d", mentionUserIds=[uid])
                    sleep(2.0)
            self.new_users.append(uid)

    def welcome_new_member(self) -> None:
        """Welcome new community members"""
        self.check_new_member()

    def feature_chats(self) -> None:
        """Feature all favorite chats"""
        for chatId in self.favorite_chats:
            with suppress(Exception):
                self.favorite(time=1, chatId=chatId)
                sleep(2.0)

    def feature_users(self) -> None:
        """Feature all favorite users"""
        featured = self.get_featured_users().profile.userId
        for userId in self.favorite_users:
            if userId not in featured:
                with suppress(Exception):
                    self.favorite(time=1, userId=userId)
                    sleep(2.0)

    def get_member_level(self, uid: str) -> int:
        """Get user level"""
        return self.get_user_info(uid).level or 0

    def get_member_titles(self, uid: str) -> List[Dict[Literal['title', 'color'], str]]:
        """Get the member titles"""
        with suppress(Exception):
            return self.get_user_info(uid).customTitles or []
        return []

    def get_wallet_amount(self) -> int:
        """Get the total coin balance of this bot"""
        return self.client.get_wallet_amount()

    def generate_transaction_id(self) -> str:
        """Generate a transaction ID"""
        return self.client.generate_transaction_id()

    @overload
    def pay(
        self,
        coins: int,
        *,
        blogId: str,
        transactionId: Optional[str] = None
    ) -> None: ...
    @overload
    def pay(
        self,
        coins: int,
        *,
        chatId: Optional[str] = None,
        transactionId: Optional[str] = None
    ) -> None: ...
    @overload
    def pay(
        self,
        coins: int,
        *,
        objectId: Optional[str] = None,
        transactionId: Optional[str] = None
    ) -> None: ...
    def pay(
        self,
        coins: int,
        *,
        blogId: Optional[str] = None,
        chatId: Optional[str] = None,
        objectId: Optional[str] = None,
        transactionId: Optional[str] = None
    ) -> None:
        """Send props to a blog, chat or wiki"""
        if not transactionId:
            transactionId = self.generate_transaction_id()
        self.send_coins(coins=coins, blogId=blogId, chatId=chatId, objectId=objectId, transactionId=transactionId)  # type: ignore

    @overload
    def favorite(self, time: Literal[1, 2, 3] = 1, *, userId: str) -> None: ...
    @overload
    def favorite(self, time: Literal[1, 2, 3] = 1, *, chatId: str) -> None: ...
    @overload
    def favorite(self, time: Literal[1, 2, 3] = 1, *, blogId: str) -> None: ...
    @overload
    def favorite(self, time: Literal[1, 2, 3] = 1, *, wikiId: str) -> None: ...
    def favorite(self, time: Literal[1, 2, 3] = 1, *, userId: Optional[str] = None, chatId: Optional[str] = None, blogId: Optional[str] = None, wikiId: Optional[str] = None) -> None:
        """Feature a user, chat, blog or wiki"""
        self.feature(time=time, userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)  # type: ignore

    @overload
    def unfavorite(self, *, userId: str): ...
    @overload
    def unfavorite(self, *, chatId: str): ...
    @overload
    def unfavorite(self, *, blogId: str): ...
    @overload
    def unfavorite(self, *, wikiId: str): ...
    def unfavorite(self, userId: Optional[str] = None, chatId: Optional[str] = None, blogId: Optional[str] = None, wikiId: Optional[str] = None) -> None:
        """Unfeature a user, chat, blog or wiki"""
        self.unfeature(userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)  # type: ignore

    @overload
    def join_chatroom(self, chat: str) -> bool: ...
    @overload
    def join_chatroom(self, *, chatId: str) -> bool: ...
    def join_chatroom(self, chat: Optional[str] = None, chatId: Optional[str] = None) -> bool:
        """Join to a chat

        Parameters
        ----------
        chat : str, optional
            The chat link or title
        chatId : str, optional
            The chat ID.

        """
        if chat:
            with suppress(Exception):
                chatId = cast(str, self.get_from_code(chat).objectId)
        if chatId:
            with suppress(Exception):
                self.join_chat(cast(str, chatId))
                return True
        chats = self.get_public_chat_threads()
        if not chat:
            return False
        for title, chat_id in zip(chats.title, chats.chatId):
            if chat == title:
                self.join_chat(chat_id)
                return True
            if chat.lower() in title.lower() or chat == chat_id:
                self.join_chat(chat_id)
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
        for chatId, membersCount in zip(chats.chatId, chats.membersCount):
            if membersCount == 1000:
                continue
            with suppress(Exception):
                self.join_chat(chatId)

    def leave_all_chats(self) -> None:
        """Join all popular chats"""
        for chatId in self.get_public_chat_threads(type="recommended", start=0, size=100).chatId:
            with suppress(Exception):
                self.leave_chat(chatId)

    def follow_user(self, uid: Union[str, List[str]]) -> None:
        """Follow a user or users"""
        self.follow(uid)

    def unfollow_user(self, uid: str) -> None:
        """Unfollow a user"""
        self.unfollow(uid)

    def add_title(self, uid: str, title: str, color: Optional[str] = None) -> None:
        """Add a title to a user"""
        member = self.get_member_titles(uid)
        titles, colors = [title], [color]
        with suppress(TypeError):
            titles = [i['title'] for i in member] + [title]
            colors = [i['color'] for i in member] + [color]
        self.edit_titles(uid, titles, colors)

    def remove_title(self, uid: str, title: str) -> None:
        """Remove a title to a user"""
        customTitles = self.get_member_titles(uid)
        titles = []
        colors = []
        for t in customTitles:
            if title not in t["title"]:
                titles.append(t["title"])
                colors.append(t["color"])
        self.edit_titles(uid, titles, colors)

    def passive(self) -> None:
        """Internal method to perform bot activities"""
        def upt_activity() -> None:
            startTime = int(time())
            with print_exception(Exception):
                self.send_active_obj(startTime=startTime, endTime=startTime + 300)

        def change_bio_and_welcome_members() -> None:
            if self.welcome_chat or self.message_bvn:
                self.welcome_new_member()
            with print_exception(Exception):
                self.activity_status('on')
                if isinstance(self.bio_contents, list):
                    self.edit_profile(content=choice(self.bio_contents))
                elif isinstance(self.bio_contents, str):
                    self.edit_profile(content=self.bio_contents)

        with print_exception(Exception):
            self.feature_chats()
            self.feature_users()
        j = 0
        k = 0
        while self.marche:
            change_bio_and_welcome_members()
            if j >= 240:
                self.feature_chats()
                j = 0
            if k >= 2880:
                with print_exception(Exception):
                    self.feature_users()
                k = 0
            if self.activity:
                upt_activity()
            sleep(30)
            j += 1
            k += 1
