# native packages
from contextlib import suppress
from json import dumps
from os import _exit as force_exit
from threading import Thread
from time import sleep
from typing import Dict, List, Literal, Optional, cast
from uuid import uuid4
# external packages
from aminofix import Client
from aminofix.lib.util import Event, gen_deviceId
# internal
from .bannedwords import BannedWords
from .bot import Bot
from .command import Command
from .parameters import Parameters
from .timeout import TimeOut
from .utils import PATH_CLIENT, CallbackCategory

__all__ = ('BotAmino',)

DEFAULT_DEVICE_ID = gen_deviceId()
OTHERS_EVENTS = (
    "on_avatar_chat_end",
    "on_avatar_chat_start",
    "on_screen_room_end",
    "on_screen_room_start",
    "on_strike_message",
    "on_voice_chat_end",
    "on_voice_chat_start",
    "on_voice_chat_not_answered",
    "on_voice_chat_not_cancelled",
    "on_voice_chat_not_declined",
    "on_video_chat_end",
    "on_video_chat_start",
    "on_video_chat_not_answered",
    "on_video_chat_not_cancelled",
    "on_video_chat_not_declined"
)
REMOVE_EVENTS = (
    "on_chat_removed_message",
    "on_delete_message",
    "on_text_message_force_removed",
    "on_text_message_removed_by_admin"
)


class BotAmino(Command, Client, TimeOut, BannedWords):
    """Create a new bot for amino.

    This class provides different useful functionalities for a robot,
    for handling managers, conditionals, commands, responses, events, ...

    Parameters
    ----------
    email : str, optional
        The amino account email. Default is None.
    password : str, optional
        The amino account password. Default is None.
    sid : str, optional
        The account session ID. Default is None.
    deviceId : str, optional
        The session device ID. Default is None.
    proxies : dict[str, str], optional
        The session proxies. Default is None.
    certificatePath : str, optional
        The proxies certificate path. Default is None.

    """
    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        sid: Optional[str] = None,
        deviceId: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
        certificatePath: Optional[str] = None
    ) -> None:
        deviceId = deviceId or DEFAULT_DEVICE_ID
        Command.__init__(self)
        Client.__init__(self, deviceId=deviceId, certificatePath=certificatePath, proxies=proxies or {})
        TimeOut.__init__(self)
        BannedWords.__init__(self)
        if email and password:
            self.login(email=email, password=password)
        elif sid:
            self.login_sid(sid)
        else:
            try:
                with open(PATH_CLIENT, "r") as f:
                    email, password, *_ = f.readlines()
                self.login(email=email.strip(), password=password.strip())
            except FileNotFoundError:
                with open(PATH_CLIENT, 'w') as f:
                    f.write('email\npassword')
                print(f"Please enter your email and password in the file {PATH_CLIENT}")
                print("-----end-----")
                force_exit(1)
        self.communaute: Dict[int, Bot] = {}
        self.botId: Optional[str] = self.userId
        self.perms_list: List[str] = []
        self.prefix = "!"
        self.activity = False
        self.wait = 0
        self.admin_user = ""
        self.bio = None
        self.self_callable = False
        self.no_command_message = ""
        self.spam_message = "You are spamming, be careful"
        self.lock_message = "Command locked sorry"
        self.launched = False

    @property
    def len_community(self) -> int:
        """Launched communities"""
        return len(self.communaute)

    def tradlist(self, aminoIdList: List[str]) -> List[str]:
        uidList = []
        for aminoId in aminoIdList:
            with suppress(Exception):
                userId = self.get_from_code(f"http://aminoapps.com/u/{aminoId}").objectId
                uidList.append(userId)
                continue
            uidList.append(aminoId)
        return uidList

    def add_community(self, comId: int) -> None:
        """Set a bot instance for the given community"""
        self.communaute[comId] = Bot(self, comId, self.prefix, self.bio, self.activity)

    def get_community(self, comId: int) -> Bot:
        """Get the bot instance for a given community"""
        return self.communaute[comId]

    def is_it_bot(self, uid: str) -> bool:
        """Check if the user is this bot"""
        return uid == self.botId and not self.self_callable

    def is_it_admin(self, uid: str) -> bool:
        """Check if the user is an admin of this bot"""
        return uid in self.perms_list

    def get_wallet_amount(self) -> int:
        """Get the total coin balance of this bot"""
        return self.get_wallet_info().totalCoins or 0

    def generate_transaction_id(self) -> str:
        """Generate a transaction ID"""
        return str(uuid4())

    def start_video_chat(self, comId: int, chatId: str, joinType: int = 1) -> None:
        """Start a live stream in the chat

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        self.send(dumps(data))
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": joinType,
                "channelType": 4,
                "id": "2154531"  # Need to change?
            },
            "t": 108
        }
        self.send(dumps(data))

    def start_screen_room(self, comId: int, chatId: str, joinType: int = 1) -> None:
        """Start a screening room in the chat

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        self.send(dumps(data))
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": joinType,
                "channelType": 5,
                "id": "2154531"  # Need to change?
            },
            "t": 108
        }
        self.send(dumps(data))

    def join_screen_room(self, comId: int, chatId: str) -> None:
        """Join in the screening room as viewer

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.

        """
        self.join_video_chat_as_viewer(comId, chatId)  # type: ignore

    def start_voice_room(self, comId: int, chatId: str, joinType: int = 1) -> None:
        """Start a voice room in the chat

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.
        joinType : int
            The bot's join role: 1 for owner, 2 for viewer.

        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        self.send(dumps(data))
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "channelType": 1,
                "id": "2154531"  # Need to change?
            },
            "t": 108
        }
        self.send(dumps(data))

    def end_voice_room(self, comId: int, chatId: str) -> None:
        """End the voice room in the chat

        Parameters
        ----------
        comId : int
            The community ID of the chat.
        chatId : str
            The ID of the chat.

        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": 2,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        self.send(dumps(data))

    def show_online(self, comId: int) -> None:
        """Browse the community home"""
        data = {
            "o": {
                "actions": ["Browsing"],
                "target": f"ndc://x{comId}/",
                "ndcId": comId,
                "id": "82333"
            },
            "t":304
        }
        self.send(dumps(data))

    def check(self, args: Parameters, *can: Literal['bot', 'staff'], id_=None) -> bool:
        """Check if the user is a bot or staff member"""
        id_ = id_ if id_ else args.authorId
        foo = {'staff': args.subClient.is_in_staff,
               'bot': self.is_it_bot}
        for i in can:
            if foo[i](id_):
                return True
        return False

    def check_all(self) -> None:
        """Check-in in the bot's launched communities"""
        for bot in self.communaute.values():
            with suppress(Exception):
                bot.check_in()
            sleep(5)

    def threadLaunch(self, comId: int, passive: bool = False) -> None:
        """Launch the bot in a community"""
        if comId not in self.communaute:
            self.communaute[comId] = Bot(self, comId, self.prefix, self.bio, passive)
        sleep(30)
        if not self.launched:
            self.launch_events()
            self.launched = True
        if passive:
            self.communaute[comId].passive()

    def launch(self, passive: bool = False) -> None:
        """Launch the bot in the last 25 joined communities."""
        amino_list = self.sub_clients()
        for comId in amino_list.comId:
            Thread(target=self.threadLaunch, args=(comId, passive,)).start()

    def single_launch(self, comId: int, passive: bool = False) -> None:
        """Launch the bot in a community asynchronously"""
        Thread(target=self.threadLaunch, args=[comId, passive]).start()

    def launch_events(self) -> None:
        """Launch the bot events"""
        if self.categorie_exist("command") or self.categorie_exist("answer"):
            self.launch_text_message()
        if self.categorie_exist("on_member_join_chat"):
            self.launch_on_member_join_chat()
        if self.categorie_exist("on_member_leave_chat"):
            self.launch_on_member_leave_chat()
        if self.categorie_exist("on_other"):
            self.launch_other_message()
        if self.categorie_exist("on_remove"):
            self.launch_removed_message()
        if self.categorie_exist("on_delete"):
            self.launch_delete_message()
        if self.categorie_exist("on_all"):
            self.launch_all_message()
        if self.categorie_exist("on_event"):
            self.launch_all_events()

    def message_analyse(self, data: Event, category: CallbackCategory) -> None:
        """Run the chat-message event parser"""
        try:
            subClient = self.get_community(cast(int, data.comId))
        except Exception:
            return
        args = Parameters(data, subClient)
        Thread(target=self.execute, args=(category, args, category,)).start()

    def on_member_event(self, data: Event, category: CallbackCategory) -> None:
        """Internal method to execute the on_member_event event"""
        try:
            subClient = self.get_community(cast(int, data.comId))
        except Exception:
            return
        args = Parameters(data, subClient)
        if not self.check(args, "bot"):
            Thread(target=self.execute, args=[category, args, category]).start()

    def launch_all_events(self) -> None:
        """Internal method to launch on_event event"""
        for chat_method in self.chat_methods.values():
            @self.event(chat_method.__name__)
            def on_all_message(data: Event) -> None:
                self.message_analyse(data, "on_event")

    def launch_text_message(self) -> None:
        """Internal method to launch on_text_message event"""
        def text_message(data: Event) -> None:
            try:
                subClient = self.get_community(cast(int, data.comId))
            except Exception:
                return
            args = Parameters(data, subClient)
            # event execution: on_message
            if self.categorie_exist("on_message"):
                Thread(target=self.execute, args=("on_message", args, "on_message",)).start()
            # banned word check
            if self.check(args, 'staff', 'bot') and subClient.banned_words:
                self.check_banned_words(args, args.subClient.is_in_staff(cast(str, self.botId)))
            # command timeout check
            if not self.timed_out(args.authorId) and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                subClient.send_message(args.chatId, self.spam_message)
                return
            # command execution
            elif self.categorie_exist("command") and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}")
                command = args.message.lower().split()[0][len(subClient.prefix):]
                # locked command check
                if command in subClient.locked_command:
                    subClient.send_message(args.chatId, self.lock_message)
                    return
                # command message formatting
                args.message = ' '.join(args.message.split()[1:])
                # post-command timeout addition
                if self.admin_user != args.authorId:
                    self.time_user(args.authorId, self.wait)
                # matched command
                if command.lower() in self.commands["command"].keys():
                    Thread(target=self.execute, args=[command, args]).start()
                # unmatched command
                elif self.no_command_message:
                    subClient.send_message(args.chatId, self.no_command_message)
                return
            # answer execution
            elif self.categorie_exist("answer") and args.message.lower() in self.commands["answer"] and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}")
                # post-answer timeout addition
                if self.admin_user != args.authorId:
                    self.time_user(args.authorId, self.wait)
                Thread(target=self.execute, args=[args.message.lower(), args, "answer"]).start()
                return

        @self.event("on_text_message")
        def on_text_message(data: Event) -> None:
            text_message(data)

    def launch_other_message(self) -> None:
        """Internal method to launch on_other event"""
        for event_name in OTHERS_EVENTS:
            @self.event(event_name)
            def on_other_message(data: Event) -> None:
                self.message_analyse(data, "on_other")

    def launch_all_message(self):
        """Internal method to launch on_all event"""
        for chat_method in self.chat_methods.values():
            @self.event(chat_method.__name__)
            def on_all_message(data: Event) -> None:
                self.message_analyse(data, "on_all")

    def launch_delete_message(self) -> None:
        """Internal method to launch on_delete event"""
        @self.event("on_delete_message")
        def on_delete_message(data: Event) -> None:
            self.message_analyse(data, "on_delete")

    def launch_removed_message(self) -> None:
        """Internal method to launch on_remove event"""
        for type_name in REMOVE_EVENTS:
            @self.event(type_name)
            def on_chat_removed(data: Event) -> None:
                self.message_analyse(data, "on_remove")

    def launch_on_member_join_chat(self) -> None:
        """Internal method to launch on_member_join_chat event"""
        @self.event("on_group_member_join")
        def on_group_member_join(data: Event) -> None:
            self.on_member_event(data, "on_member_join_chat")

    def launch_on_member_leave_chat(self) -> None:
        """Internal method to launch on_member_leave_chat event"""
        @self.event("on_group_member_leave")
        def on_group_member_leave(data: Event) -> None:
            self.on_member_event(data, "on_member_leave_chat")
