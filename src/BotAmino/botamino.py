import contextlib
import json
import os
import threading
import time
import uuid
# external
from aminofix import Client
# internal
from .bannedwords import BannedWords
from .bot import Bot
from .commands import CommandHandler
from .parameters import Parameters
from .timeout import TimeOut
from .utils import PATH_CLIENT, safe_exit

__all__ = ('BotAmino',)

OTHERS_EVENTS = (
    "on_avatar_chat_end",
    "on_avatar_chat_start",
    "on_screen_room_end",
    "on_screen_room_start",
    "on_strike_message",
    "on_voice_chat_end",
    "on_voice_chat_start",
    "on_voice_chat_not_answered",
    "on_voice_chat_cancelled",
    "on_voice_chat_declined",
    "on_video_chat_end",
    "on_video_chat_start",
    "on_video_chat_not_answered",
    "on_video_chat_cancelled",
    "on_video_chat_declined"
)
REMOVE_EVENTS = (
    "on_chat_removed_message",
    "on_delete_message",
    "on_text_message_force_removed",
    "on_text_message_removed_by_admin"
)


class BotAmino(CommandHandler, Client, TimeOut, BannedWords):
    """Create a new bot for amino.

    This class provides different useful functionalities for a robot,
    for handling managers, conditionals, commands, responses, events, ...

    Parameters
    ----------
    email : `str`, `optional`
        The amino account email. Default is `None`.
    password : `str`, `optional`
        The amino account password. Default is `None`.
    sid : `str`, `optional`
        The account session ID. Default is `None`.
    deviceId : `str`, `optional`
        The session device ID. Default is `None`.
    proxies : `dict[str, str]`, `optional`
        The session proxies. Default is `None`.
    certificatePath : `str`, `optional`
        The proxies certificate path. Default is `None`.
    parser_feature : `{'default', 'quotedkey'}`, `optional`
        Command parser feature.
        `default` : Capture quoted positional and key arguments
        `quotedkey` : allows the key to be enclosed in quotes
    language : `str`, `optional`
        The amino language. Default is `en`.

    """
    def __init__(
        self,
        email=None,
        password=None,
        sid=None,
        deviceId=None,
        proxies=None,
        certificatePath=None,
        parser_feature='default',
        language='en'
    ):
        self.parser_feature = parser_feature
        self.language = language
        CommandHandler.__init__(self)
        Client.__init__(self, deviceId=deviceId, proxies=proxies, certificatePath=certificatePath)
        TimeOut.__init__(self)
        BannedWords.__init__(self)
        if not email:
            email = os.getenv("EMAIL")
        if not password:
            password = os.getenv("PASSWORD")
        if not deviceId:
            deviceId = os.getenv("DEVICE") or os.getenv("DEVICEID")
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
                safe_exit(1)
        self.lock = threading.Lock()
        self.botId = self.userId
        self.communaute = {}
        self.perms_list = []
        self.prefix = "!"
        self.wait = 0
        self.admin_user = ""
        self.bio = None
        self.self_callable = False
        self.no_command_message = ""
        self.spam_message = "You are spamming, be careful"
        self.lock_message = "Command locked sorry"
        self.launched = False

    def parse_headers(self, data=None, type=None):
        headers = super().parse_headers(data=data, type=type)
        headers["NDCLANG"] = self.language
        return headers

    @property
    def len_community(self):
        """Launched communities"""
        return len(self.communaute)

    def tradlist(self, aminoIdOrLink):
        """Get a list of user IDs from an iterable of Amino links"""
        uidList = []
        for aminoId in [aminoIdOrLink] if isinstance(aminoIdOrLink, str) else aminoIdOrLink:
            amino_link = aminoId if aminoId.startswith('http') else f"http://aminoapps.com/u/{aminoId}"
            with contextlib.suppress(Exception):
                userId = self.get_from_code(amino_link).objectId
                uidList.append(userId)
                continue
            uidList.append(aminoId)
        return uidList

    def add_community(self, comId, activity):
        """Set a bot instance for the given community"""
        self.communaute[comId] = Bot(self, comId, self.prefix, self.bio, activity)

    def get_community(self, comId):
        """Get the bot instance for a given community"""
        return self.communaute[comId]

    def is_it_bot(self, uid):
        """Check if the user is this bot"""
        return uid == self.botId and not self.self_callable

    def is_it_admin(self, uid):
        """Check if the user is an admin of this bot"""
        return uid in self.perms_list or uid == self.admin_user

    def get_wallet_amount(self):
        """Get the total coin balance of this bot"""
        return self.get_wallet_info().totalCoins or 0

    def generate_transaction_id(self):
        """Generate a transaction ID"""
        return str(uuid.uuid4())

    def show_online(self, comId):
        """Browse the community home"""
        self.send(json.dumps({
            "o": {
                "actions": ["Browsing"],
                "target": f"ndc://x{comId}/",
                "ndcId": comId,
                "id": "82333"
            },
            "t":304
        }))

    def check(self, args, *can, id_=None):
        """Check if the user is this bot or staff member"""
        id_ = id_ if id_ else args.authorId
        foo = {
            'admin': self.is_it_admin,
            'bot': self.is_it_bot,
            'agent': args.subClient.is_agent,
            'curator': args.subClient.is_curator,
            'leader': args.subClient.is_leader,
            'staff': args.subClient.is_in_staff
        }
        for i in can:
            if foo[i](id_):
                return True
        return False

    def check_all(self):
        """Check-in in the bot's launched communities"""
        for bot in self.communaute.values():
            with contextlib.suppress(Exception):
                bot.check_in()
            time.sleep(5)

    def threadLaunch(self, comId, passive=False):
        """Launch the bot in a community"""
        if comId not in self.communaute:
            self.add_community(comId, passive)
        with self.lock:
            if not self.launched:
                self.launch_events()
                self.launched = True
        if passive:
            threading.Thread(target=self.get_community(comId).passive).start()

    def launch(self, passive=False):
        """Launch the bot in the last 25 joined communities."""
        amino_list = self.sub_clients()
        for comId in amino_list.comId:
            self.threadLaunch(comId, passive)

    def single_launch(self, comId, passive=False):
        """Launch the bot in a community asynchronously"""
        self.threadLaunch(comId, passive)

    def launch_events(self) -> None:
        """Launch the bot events"""
        if self.category_exist("command") or self.category_exist("answer"):
            self.launch_text_message()
        if self.category_exist("on_member_join_chat"):
            self.launch_on_member_join_chat()
        if self.category_exist("on_member_leave_chat"):
            self.launch_on_member_leave_chat()
        if self.category_exist("on_other"):
            self.launch_other_message()
        if self.category_exist("on_remove"):
            self.launch_removed_message()
        if self.category_exist("on_delete"):
            self.launch_delete_message()
        if self.category_exist("on_all"):
            self.launch_all_message()
        if self.category_exist("on_event"):
            self.launch_all_events()

    def message_analyse(self, name, data, category):
        """Run the chat-message event parser"""
        try:
            subClient = self.get_community(data.comId)
        except Exception:
            return
        args = Parameters(data, subClient)
        threading.Thread(target=self.execute, args=(name, args, category,)).start()

    def on_member_event(self, data, category):
        """Internal method to execute the on_member_event event"""
        try:
            subClient = self.get_community(data.comId)
        except Exception:
            return
        args = Parameters(data, subClient)
        if not self.check(args, "bot"):
            threading.Thread(target=self.execute, args=[category, args, category]).start()

    def launch_text_message(self):
        """Internal method to launch on_text_message event"""
        def text_message(data):
            try:
                subClient = self.get_community(data.comId)
            except Exception:
                return
            args = Parameters(data, subClient)
            # event execution: on_message
            if self.category_exist("on_message"):
                threading.Thread(target=self.execute, args=("on_message", args, "on_message",)).start()
            # banned word check
            if not self.check(args, 'staff', 'bot') and subClient.banned_words:
                self.check_banned_words(args, args.subClient.is_in_staff(self.botId))
            # command timeout check
            if not self.timed_out(args.authorId) and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                subClient.send_message(args.chatId, self.spam_message)
                return
            # command execution
            elif self.category_exist("command") and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}".removesuffix("\n"))
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
                if self.get_command_info(command.lower()):
                    threading.Thread(target=self.execute, args=[command, args]).start()
                # unmatched command
                elif self.no_command_message:
                    subClient.send_message(args.chatId, self.no_command_message)
                return
            # answer execution
            elif self.category_exist("answer") and self.get_answer_info(args.message.lower()) and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}".removesuffix("\n"))
                # post-answer timeout addition
                if self.admin_user != args.authorId:
                    self.time_user(args.authorId, self.wait)
                threading.Thread(target=self.execute, args=[args.message.lower(), args, "answer"]).start()
                return

        @self.event("on_text_message")
        def _(data):
            text_message(data)

    def launch_other_message(self):
        """Internal method to launch on_other event"""
        for event_name in OTHERS_EVENTS:
            @self.event(event_name)
            def _(data):
                self.message_analyse("on_other", data, "on_other")

    def launch_all_message(self):
        """Internal method to launch on_all event"""
        for chat_method in self.chat_methods.values():
            @self.event(chat_method.__name__)
            def _(data):
                self.message_analyse("on_all", data, "on_all")

    def launch_delete_message(self):
        """Internal method to launch on_delete event"""
        @self.event("on_delete_message")
        def _(data):
            self.message_analyse("on_delete", data, "on_delete")

    def launch_removed_message(self):
        """Internal method to launch on_remove event"""
        for type_name in REMOVE_EVENTS:
            @self.event(type_name)
            def _(data):
                self.message_analyse("on_remove", data, "on_remove")

    def launch_on_member_join_chat(self):
        """Internal method to launch on_member_join_chat event"""
        @self.event("on_group_member_join")
        def _(data):
            self.on_member_event(data, "on_member_join_chat")

    def launch_on_member_leave_chat(self):
        """Internal method to launch on_member_leave_chat event"""
        @self.event("on_group_member_leave")
        def _(data):
            self.on_member_event(data, "on_member_leave_chat")

    def launch_all_events(self):
        """Internal method to launch on_event event"""
        for chat_method in self.chat_methods.values():
            @self.event(chat_method.__name__)
            def _(data):
                self.message_analyse(chat_method.__name__, data, "on_event")
