import requests
import json

from time import sleep as slp
from sys import exit
from json import dumps
from pathlib import Path
from threading import Thread
# from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from uuid import uuid4

from .local_amino import Client
from .commands import *
from .extensions import *
from .Bot import Bot


# this is Slimakoi's API with some of my patches

# API made by ThePhoenix78
# Big optimisation thanks to SempreLEGIT#1378 ♥
# small very small changes by meliodas
# if login method is not working use sid

path_utilities = "utilities"
path_amino = f'{path_utilities}/amino_list'
path_client = "client.txt"
NoneType = type(None)


with suppress(Exception):
    for i in (path_utilities, path_amino):
        Path(i).mkdir(exist_ok=True)


def print_exception(exc):
    print(repr(exc))


class BotAmino(Command, Client, TimeOut, BannedWords):
    def __init__(self, email: str = None, password: str = None, sid: str = None,  proxies: dict = None, deviceId: str = "32255726EEA11E60ACD268CA4DD36C8E6517144FCD24D7A53B144DE77B57980B26386188009D2BDEDE", certificatePath: str = None):
        Command.__init__(self)
        Client.__init__(self, proxies=proxies, deviceId=deviceId, certificatePath=certificatePath)

        if email and password:
            self.login(email=email, password=password)
        elif sid:
            self.login_sid(SID=sid)
        else:
            try:
                with open(path_client, "r") as file_:
                    para = file_.readlines()
                self.login(email=para[0].strip(), password=para[1].strip())
            except FileNotFoundError:
                with open(path_client, 'w') as file_:
                    file_.write('email\npassword')
                print("Please enter your email and password in the file client.txt")
                print("-----end-----")
                exit(1)

        self.communaute = {}
        self.botId = self.userId
        self.len_community = 0
        self.perms_list = []
        self.prefix = "!"
        self.activity = False
        self.wait = 0
        self.bio = None
        self.self_callable = False
        self.no_command_message = ""
        self.spam_message = "You are spamming, be careful"
        self.lock_message = "Command locked sorry"
        self.launched = False

    def tradlist(self, sub):
        sublist = []
        for elem in sub:
            with suppress(Exception):
                val = self.get_from_code(f"http://aminoapps.com/u/{elem}").objectId
                sublist.append(val)
                continue
            sublist.append(elem)
        return sublist

    def send_data(self, data):
        self.send(data)

    def add_community(self, comId):
        self.communaute[comId] = Bot(self, comId, self.prefix, self.bio, self.activity)

    def get_community(self, comId):
        return self.communaute[comId]

    def is_it_bot(self, uid):
        return uid == self.botId and not self.self_callable

    def is_it_admin(self, uid):
        return uid in self.perms_list

    def get_wallet_amount(self):
        return self.get_wallet_info().totalCoins

    def generate_transaction_id(self):
        return str(uuid4())

    def start_screen_room(self, comId: str, chatId: str, joinType: int=1):
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        data = dumps(data)
        self.send(data)

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
        data = dumps(data)
        self.send(data)

    def join_screen_room(self, comId: str, chatId: str, joinType: int=1):
        data = {
            "o":
                {
                    "ndcId": int(comId),
                    "threadId": chatId,
                    "joinRole": 2,
                    "id": "72446"
                },
            "t": 112
        }
        data = dumps(data)
        self.send(data)

    def start_voice_room(self, comId: str, chatId: str, joinType: int=1):
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        data = dumps(data)
        self.send(data)
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "channelType": 1,
                "id": "2154531"  # Need to change?
            },
            "t": 108
        }
        data = dumps(data)
        self.send(data)

    def end_voice_room(self, comId: str, chatId: str, joinType: int = 2):
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"  # Need to change?
            },
            "t": 112
        }
        data = dumps(data)
        self.send(data)

    def show_online(self, comId):
        data = {
            "o": {
                "actions": ["Browsing"],
                "target": f"ndc://x{comId}/",
                "ndcId": int(comId),
                "id": "82333"
            },
            "t":304}
        data = dumps(data)
        slp(2)
        self.send(data)

    def upload_bubble(self,file,comId):
        data=file
        response = requests.post(f"https://service.narvii.com/api/v1/x{comId}/s/chat/chat-bubble/templates/107147e9-05c5-405f-8553-af65d2823457/generate", data=data, headers=self.headers)
        bid=json.loads(response.text)['chatBubble']['bubbleId']
        print(bid)
        response = requests.post(f"https://service.narvii.com/api/v1/x{comId}/s/chat/chat-bubble/{bid}", data=data, headers=self.headers)
        if response.status_code !=200:
            return json.loads(response.text)
        else: return bid

    def check(self, args, *can, id_=None):
        id_ = id_ if id_ else args.authorId
        foo = {'staff': args.subClient.is_in_staff,
               'bot': self.is_it_bot}

        for i in can:
            if foo[i](id_):
                return True

    def check_all(self):
        amino_list = self.sub_clients()
        for com in amino_list.comId:
            try:
                self.communaute[com].check_in()
            except Exception:
                pass

    def threadLaunch(self, commu, passive: bool=False):
        self.communaute[commu] = Bot(self, commu, self.prefix, self.bio, passive)
        slp(30)
        if passive:
            self.communaute[commu].passive()

    def launch(self, passive: bool = False):
        amino_list = self.sub_clients()
        self.len_community = len(amino_list.comId)
        [Thread(target=self.threadLaunch, args=[commu, passive]).start() for commu in amino_list.comId]

        if self.launched:
            return

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
            self.launch_on_event()

        self.launched = True

    def single_launch(self, commu, passive: bool = False):
        amino_list = self.sub_clients()
        self.len_community = len(amino_list.comId)
        Thread(target=self.threadLaunch, args=[commu, passive]).start()

        if self.launched:
            return

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

        self.launched = True

    def message_analyse(self, data, type):
        try:
            commuId = data.comId
            subClient = self.get_community(commuId)
        except Exception:
            return

        args = Parameters(data, subClient)
        Thread(target=self.execute, args=[type, args, type]).start()

    def on_member_event(self, data, type):
        try:
            commuId = data.comId
            subClient = self.get_community(commuId)
        except Exception:
            return

        args = Parameters(data, subClient)

        if not self.check(args, "bot"):
            Thread(target=self.execute, args=[type, args, type]).start()

    def launch_text_message(self):
        @self.event("on_text_message")
        def on_text_message(data):
            try:
                commuId = data.comId
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)

            if "on_message" in self.commands.keys():
                Thread(target=self.execute, args=["on_message", args, "on_message"]).start()

            if not self.check(args, 'staff', 'bot') and subClient.banned_words:
                self.check_banned_words(args)

            if not self.timed_out(args.authorId) and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                subClient.send_message(args.chatId, self.spam_message)
                return

            elif "command" in self.commands.keys() and args.message.startswith(subClient.prefix) and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}")
                command = args.message.lower().split()[0][len(subClient.prefix):]

                if command in subClient.locked_command:
                    subClient.send_message(args.chatId, self.lock_message)
                    return

                args.message = ' '.join(args.message.split()[1:])
                self.time_user(args.authorId, self.wait)
                if command.lower() in self.commands["command"].keys():
                    Thread(target=self.execute, args=[command, args]).start()

                elif self.no_command_message:
                    subClient.send_message(args.chatId, self.no_command_message)
                return

            elif "answer" in self.commands.keys() and args.message.lower() in self.commands["answer"] and not self.check(args, "bot"):
                print(f"{args.author} : {args.message}")
                self.time_user(args.authorId, self.wait)
                Thread(target=self.execute, args=[args.message.lower(), args, "answer"]).start()
                return

    def launch_other_message(self):
        for type_name in ("on_strike_message", "on_voice_chat_not_answered",
                          "on_voice_chat_not_cancelled", "on_voice_chat_not_declined",
                          "on_video_chat_not_answered", "on_video_chat_not_cancelled",
                          "on_video_chat_not_declined", "on_voice_chat_start", "on_video_chat_start",
                          "on_voice_chat_end", "on_video_chat_end", "on_screen_room_start",
                          "on_screen_room_end", "on_avatar_chat_start", "on_avatar_chat_end"):

            @self.event(type_name)
            def on_other_message(data):
                self.message_analyse(data, "on_other")

    def launch_all_message(self):
        for x in (self.chat_methods):
            @self.event(self.chat_methods[x].__name__)
            def on_all_message(data):
                self.message_analyse(data, "on_all")

    def launch_delete_message(self):
        @self.event("on_delete_message")
        def on_delete_message(data):
            self.message_analyse(data, "on_delete")

    def launch_removed_message(self):
        for type_name in ("on_chat_removed_message", "on_text_message_force_removed", "on_text_message_removed_by_admin", "on_delete_message"):
            @self.event(type_name)
            def on_chat_removed(data):
                self.message_analyse(data, "on_remove")

    def launch_on_member_join_chat(self):
        @self.event("on_group_member_join")
        def on_group_member_join(data):
            self.on_member_event(data, "on_member_join_chat")

    def launch_on_member_leave_chat(self):
        @self.event("on_group_member_leave")
        def on_group_member_leave(data):
            self.on_member_event(data, "on_member_leave_chat")

    def launch_on_event(self):
        for k, v in self.commands["on_event"].items():
            @self.event(k)
            def _function(data):
                v(data)


