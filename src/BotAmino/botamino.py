import contextlib
import threading
import time
import typing
import uuid
import dotenv

from .bannedwords import BannedWords
from .bot import Bot
from .client import Client
from .command import Command
from .errors import APIError, EmailAlreadyTaken
from .parameters import Parameters
from .timeout import TimeOut
from .typing import CallbackCategory, ParserFeature, Proxies
from .utils import decode_sid, safe_exit

__all__ = ("BotAmino",)

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
    "on_video_chat_not_declined",
)
REMOVE_EVENTS = (
    "on_chat_removed_message",
    "on_delete_message",
    "on_text_message_force_removed",
    "on_text_message_removed_by_admin",
)


class LoginInfo(typing.NamedTuple):
    email: typing.Optional[str]
    password: typing.Optional[str]
    secret: typing.Optional[str]
    sid: typing.Optional[str]


class BotAmino(Client, Command, TimeOut, BannedWords):
    """Create a new bot for amino.

    This class provides different useful functionalities for a robot,
    for handling managers, conditionals, commands, responses, events, ...

    Parameters
    ----------
    email : `str`, `optional`
        The amino account email. Default is `None`.
    password : `str`, `optional`
        The amino account password. Default is `None`.
    secret
    sid : `str`, `optional`
        The account session ID. Default is `None`.
    deviceId : `str`, `optional`
        The session device ID. Default is `None`.
    proxies : `dict[str, str]`, `optional`
        The session proxies. Default is `None`.
    certificatePath : `str`, `optional`
        The proxies certificate path. Default is `None`.
    timeout
    parser_feature : `{'default', 'quotedkey'}`, `optional`
        Command parser feature.
        `default` : Capture quoted positional and key arguments
        `quotedkey` : allows the key to be enclosed in quotes
    language
    env_file
    prefix
    bio
    cooldown
    no_command_message
    spam_message
    lock_message
    admin_user
    language : `str`, `optional`
        The amino language. Default is `en`.

    """

    @property
    def botId(self) -> typing.Optional[str]:
        return self.userId

    @property
    def wait(self) -> typing.Optional[float]:
        return self.cooldown

    @wait.setter
    def wait(self, value: typing.Optional[float]) -> None:
        self.cooldown = value

    def __init__(
        self,
        email: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        secret: typing.Optional[str] = None,
        sid: typing.Optional[str] = None,
        deviceId: typing.Optional[str] = None,
        proxies: typing.Optional[Proxies] = None,
        certificatePath: typing.Optional[str] = None,
        timeout: typing.Optional[float] = None,
        parser_feature: ParserFeature = "default",
        language: typing.Optional[str] = None,
        env_file: str = ".env",
        prefix: str = "!",
        bio: typing.Optional[typing.Union[typing.List[str], str]] = None,
        cooldown: typing.Optional[float] = None,
        no_command_message: typing.Optional[str] = None,
        spam_message: typing.Optional[str] = None,
        lock_message: typing.Optional[str] = None,
        admin_user: typing.Optional[str] = None,
    ) -> None:
        Command.__init__(self)
        TimeOut.__init__(self)
        BannedWords.__init__(self)
        Client.__init__(
            self,
            deviceId=deviceId,
            proxies=proxies,
            certificatePath=certificatePath,
            language=language,
            timeout=timeout,
        )
        if not (email or sid):
            env = dotenv.dotenv_values(env_file)
            email = env.get("EMAIL")
            password = env.get("PASSWORD")
            secret = env.get("SECRET")
            sid = env.get("SID")
        if email:
            try:
                self.register_check(email)
            except EmailAlreadyTaken:
                pass
            else:
                raise RuntimeError(
                    "The email provided does not have an account"
                ) from None
        elif sid:
            if decode_sid(sid).expired:
                raise RuntimeError("sid has expired")
        elif not secret:
            with open(env_file, "w") as f:
                f.write("EMAIL=\nPASSWORD=\nSECRET=\nSID=\n")
                print(f"Please the account info in the file {env_file!r}")
                print("-----end-----")
                safe_exit()
        self.communities: typing.Dict[int, Bot] = {}
        self.perms_list: typing.List[str] = []
        self.launched = False
        self.login_info = LoginInfo(email, password, secret, sid)
        self.env_file = env_file
        self.parser_feature: ParserFeature = parser_feature
        self.prefix = prefix
        self.cooldown = cooldown
        self.bio = bio
        self.admin_user = admin_user
        self.no_command_message = no_command_message
        self.spam_message = spam_message or "You are spamming, be careful"
        self.lock_message = lock_message or "Command locked sorry"
        self.self_callable = False

    @property
    def communaute(self) -> typing.Dict[int, Bot]:
        """Old attr name of launched communities"""
        return self.communities

    @property
    def len_community(self) -> int:
        """Launched communities"""
        return len(self.communities)

    def tradlist(
        self, aminoIdOrLink: typing.Union[typing.Iterable[str], str]
    ) -> typing.List[str]:
        """Get a list of user IDs from an iterable of Amino links"""
        userIdList: typing.List[str] = []
        for aminoId in (
            [aminoIdOrLink] if isinstance(aminoIdOrLink, str) else aminoIdOrLink
        ):
            amino_link = (
                aminoId
                if aminoId.startswith("http")
                else f"http://aminoapps.com/u/{aminoId}"
            )
            with contextlib.suppress(APIError):
                info = self.get_from_link(amino_link)
                userIdList.append(info.objectId)
                continue
            userIdList.append(aminoId)
        return userIdList

    def add_community(self, comId: int, activity: bool) -> Bot:
        """Set a bot instance for the given community"""
        if comId in self.communities:
            return self.communities[comId]
        return self.communities.setdefault(
            comId, Bot(self, comId, self.prefix, self.bio, activity)
        )

    def get_community(self, comId: int) -> typing.Optional[Bot]:
        """Get the bot instance for a given community"""
        return self.communities.get(comId)

    def is_it_bot(self, userId: str) -> bool:
        """Check if the user is this bot"""
        return userId == self.botId

    def is_it_admin(self, userId: str) -> bool:
        """Check if the user is an admin of this bot"""
        return userId in self.perms_list or userId == self.admin_user

    def get_wallet_amount(self) -> int:
        """Get the total coin balance of this bot"""
        return self.get_wallet_info().totalCoins

    def generate_transaction_id(self) -> str:
        """Generate a transaction ID"""
        return str(uuid.uuid4())

    def check(
        self,
        args: Parameters,
        *can: typing.Literal["admin", "bot", "staff", "leader", "curator", "agent"],
        userId: typing.Optional[str] = None,
    ):
        """Check if the user is this bot or staff member"""
        userId = userId or args.authorId
        foo = {
            "admin": self.is_it_admin,
            "bot": self.is_it_bot,
            "staff": args.subClient.is_in_staff,
            "leader": args.subClient.is_leader,
            "curator": args.subClient.is_curator,
            "agent": args.subClient.is_agent,
        }
        for name in can:
            if foo[name](userId):
                return True
        return False

    def check_all(self) -> None:
        """Check-in in the bot's launched communities"""
        for bot in self.communities.values():
            with contextlib.suppress(Exception):
                bot.check_in()
            time.sleep(5)

    def threadLaunch(self, comId: int, passive: bool = False) -> None:
        """Launch the bot in a community"""
        if comId not in self.communities:
            bot = self.add_community(comId, passive)
        else:
            bot = self.communities[comId]
        time.sleep(30)
        if not self.launched:
            self.launch_events()
            self.launched = True
        if passive:
            bot.passive()

    def launch(self, passive: bool = False) -> None:
        """Launch the bot in the last 25 joined communities."""
        joined = self.joined_communities(size=25)
        for comId in joined.communities.comId:
            threading.Thread(
                target=self.threadLaunch,
                args=(
                    comId,
                    passive,
                ),
            ).start()

    def single_launch(self, comId: int, passive: bool = False) -> None:
        """Launch the bot in a community asynchronously"""
        threading.Thread(target=self.threadLaunch, args=[comId, passive]).start()

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

    def message_analyse(
        self, key: typing.Any, data: Parameters, category: CallbackCategory
    ) -> None:
        """Run the chat-message event parser"""
        subClient = self.get_community(data.comId)
        if not subClient:
            return
        args = Parameters(data, subClient)
        threading.Thread(
            target=self.execute,
            args=(
                key,
                args,
                category,
            ),
        ).start()

    def on_member_event(self, data: Parameters, category: CallbackCategory) -> None:
        """Internal method to execute the on_member_event event"""
        subClient = self.get_community(data.comId)
        if not subClient:
            return
        args = Parameters(data, subClient)
        if not self.check(args, "bot"):
            threading.Thread(
                target=self.execute, args=[category, args, category]
            ).start()

    def launch_text_message(self):
        """Internal method to launch on_text_message event"""

        @self.on_text_message
        def _(data: typing.Any) -> None:
            subClient = self.get_community(data.comId)
            if not subClient:
                return
            args = Parameters(data, subClient)
            # event execution: on_message
            if self.categorie_exist("on_message"):
                threading.Thread(
                    target=self.execute,
                    args=(
                        "on_message",
                        args,
                        "on_message",
                    ),
                ).start()
            # banned word check
            if not self.check(args, "staff", "bot") and subClient.banned_words:
                botId = typing.cast(str, self.botId)
                self.check_banned_words(args, args.subClient.is_in_staff(botId))
            if self.check(args, "bot"):
                return
            # command timeout check
            if not self.timed_out(args.authorId) and args.message.startswith(
                subClient.prefix
            ):
                subClient.send_message(args.chatId, self.spam_message)
                return
            # command execution
            elif self.categorie_exist("command") and args.message.startswith(
                subClient.prefix
            ):
                print(f"{args.author} : {args.message}")
                command = args.message.lower().split()[0][len(subClient.prefix) :]
                # locked command check
                if command in subClient.locked_command:
                    subClient.send_message(args.chatId, self.lock_message)
                    return
                # command message formatting
                args.message = " ".join(args.message.split()[1:])
                # post-command timeout addition
                if self.admin_user != args.authorId and self.wait:
                    self.time_user(args.authorId, self.wait)
                # matched command
                if command.lower() in self.commands["command"].keys():
                    threading.Thread(target=self.execute, args=[command, args]).start()
                # unmatched command
                elif self.no_command_message:
                    subClient.send_message(args.chatId, self.no_command_message)
                return
            # answer execution
            elif (
                self.categorie_exist("answer")
                and args.message.lower() in self.commands["answer"]
            ):
                print(f"{args.author} : {args.message}")
                # post-answer timeout addition
                if self.admin_user != args.authorId and self.wait:
                    self.time_user(args.authorId, self.wait)
                threading.Thread(
                    target=self.execute, args=[args.message.lower(), args, "answer"]
                ).start()
                return

    def launch_other_message(self) -> None:
        """Internal method to launch on_other event"""

        @self.on_strike_message
        @self.on_voice_call
        @self.on_video_call
        @self.on_avatar_call
        @self.on_screen_room
        def _(data: typing.Any) -> None:
            self.message_analyse("on_other", data, "on_other")

    def launch_all_message(self):
        """Internal method to launch on_all event"""

        @self.on_chat_message
        def _(data: typing.Any) -> None:
            self.message_analyse("on_all", data, "on_all")

    def launch_delete_message(self):
        """Internal method to launch on_delete event"""

        @self.on_deleted_message
        def _(data: typing.Any) -> None:
            self.message_analyse("on_delete", data, "on_delete")

    def launch_removed_message(self):
        """Internal method to launch on_remove event"""

        @self.on_forced_deleted_message
        @self.on_deleted_message_by_mod
        def _(data: typing.Any) -> None:
            self.message_analyse("on_remove", data, "on_remove")

    def launch_on_member_join_chat(self):
        """Internal method to launch on_member_join_chat event"""

        @self.on_chat_member_join
        def _(data: typing.Any) -> None:
            self.on_member_event(data, "on_member_join_chat")

    def launch_on_member_leave_chat(self):
        """Internal method to launch on_member_leave_chat event"""

        @self.on_chat_member_left
        def _(data: typing.Any) -> None:
            self.on_member_event(data, "on_member_leave_chat")

    def launch_all_events(self):
        """Internal method to launch on_event event"""

        @self.on_error_message
        @self.on_notification_message
        @self.on_channel_message
        @self.on_chat_message
        def _(data: typing.Any):
            self.message_analyse("on_event", data, "on_event")
