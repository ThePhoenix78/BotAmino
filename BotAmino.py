from sys import exit
from json import dumps, load
from time import sleep
from string import hexdigits
from pathlib import Path
from threading import Thread
from contextlib import suppress
from random import sample, choice
from string import punctuation
from unicodedata import normalize
from schedule import every, run_pending

from amino.sub_client import SubClient
from amino.client import Client

# API made by ThePhoenix78
# Big optimisation thanks to SempreLEGIT#1378 ♥

path_utilities = "utilities"
path_amino = f'{path_utilities}/amino_list'
path_download = f'{path_utilities}/download'
path_config = f"{path_utilities}/config.json"
path_client = "client.txt"


for i in (path_utilities, path_download, path_amino):
    Path(i).mkdir(exist_ok=True)


try:
    with open(path_config, "r") as file:
        data = load(file)
        perms_list = data["admin"]
        command_lock = data["lock"]
        del data
except FileNotFoundError:
    with open(path_config, 'w') as file:
        file.write(dumps({"admin": [], "lock": []}, indent=4))
    print("Created config.json!\nYou should put your Amino Id in the list admin\nand the commands you don't want to use in lock")
    perms_list = []
    command_lock = []

try:
    with open(path_client, "r") as file_:
        login = file_.readlines()
except FileNotFoundError:
    with open(path_client, 'w') as file_:
        file_.write('email\npassword')
    print("Please enter your email and password in the file client.txt")
    print("-----end-----")
    exit(1)


client = Client()
client.login(email=login[0].strip(), password=login[1].strip())


def tradlist(sub):
    sublist = []
    for elem in sub:
        with suppress(Exception):
            val = client.get_from_code(f"http://aminoapps.com/u/{elem}").objectId
            sublist.append(val)
            continue
        with suppress(Exception):
            val = client.get_user_info(elem).userId
            sublist.append(val)
            continue
    return sublist


def filter_message(message, code):
    return normalize('NFD', message).encode(code, 'ignore').decode().lower().translate(str.maketrans("", "", punctuation))


def print_exception(exc):
    print(repr(exc))


def is_it_me(uid):
    return uid in ('2137891f-82b5-4811-ac74-308d7a46345b', 'fa1f3678-df94-4445-8ec4-902651140841',
                   'f198e2f4-603c-481a-ab74-efd0f688f666')


class Command:
    def __init__(self):
        self.commands = {}

    def execute(self, commande, data):
        return self.commands[commande](data)

    def get_commands_names(self):
        return self.commands.keys()

    def command(self, command_name):
        def add_command(command_funct):
            self.commands[command_name] = command_funct
            return command_funct
        return add_command


class Parameters:
    __slots__ = ("subClient", "chatId", "authorId", "author", "message", "messageId")

    def __init__(self, data, subClient):
        self.subClient = subClient
        self.chatId = data.message.chatId
        self.authorId = data.message.author.userId
        self.author = data.message.author.nickname
        self.message = data.message.content
        self.messageId = data.message.messageId


class BotAmino(Command):
    def __init__(self):
        super().__init__()
        self.client = client
        self.client = Client()
        self.client.login(email=login[0].strip(), password=login[1].strip())
        self.communaute = {}
        self.botId = client.userId
        self.len_community = 0
        self.perms_list = []
        self.prefix = "!"

    def get_community(self, comId):
        return self.communaute[comId]

    def is_it_bot(self, uid):
        return uid == self.botId

    def is_it_admin(self, uid):
        return uid in self.perms_list

    def check(self, args, *can, id_=None):
        id_ = id_ if id_ else args.authorId
        foo = {'staff': args.subClient.is_in_staff,
               'me': is_it_me,
               'admin': self.is_it_admin,
               'bot': self.is_it_bot}

        for i in can:
            if foo[i](id_):
                return True

    def add_community(self, comId):
        self.communaute[comId] = Bot(self.client, comId, self.prefix)

    def commands_list(self):
        return [elem for elem in self.commands.keys()]

    def run(self, comId):
        self.communaute[comId].run()

    def threadLaunch(self, commu):
        with suppress(Exception):
            self.add_community(commu)
            self.run(commu)

    def launch(self):
        for command in command_lock:
            if command in self.commands.keys():
                del self.commands[command]

        self.perms_list = tradlist(perms_list)

        amino_list = self.client.sub_clients()
        self.len_community = len([Thread(target=self.threadLaunch, args=[commu]).start() for commu in amino_list.comId])

        @client.callbacks.event("on_text_message")
        def on_text_message(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)
            print(f"{args.author} : {args.message}")

            if args.chatId in subClient.only_view and not (self.check(args, 'me', 'admin', "staff")) and self.check(args, "staff", id_=self.botId):
                subClient.delete_message(args.chatId, args.messageId, "Read-only chat", asStaff=True)
                return

            if not self.check(args, 'staff', 'me', 'admin', "bot") and subClient.banned_words:
                with suppress(Exception):
                    para = filter_message(args.message, "ascii").split()

                    if para != [""]:
                        for elem in para:
                            if elem in subClient.banned_words:
                                with suppress(Exception):
                                    subClient.delete_message(args.chatId, args.messageId, "Banned word", asStaff=True)
                                return

                with suppress(Exception):
                    para = filter_message(args.message, "utf8").split()

                    if para != [""]:
                        for elem in para:
                            if elem in subClient.banned_words:
                                with suppress(Exception):
                                    subClient.delete_message(args.chatId, args.messageId, "Banned word", asStaff=True)
                                return

            if args.message.startswith(subClient.prefix) and not self.check(args, "bot"):

                command = args.message.split()[0][len(subClient.prefix):]
                args.message = ' '.join(args.message.split()[1:])

                if command in subClient.locked_command and not self.check(args, 'staff', 'me', 'admin'):
                    return
                if command in subClient.admin_locked_command and not (self.check(args, 'me', 'admin')):
                    return
                if not subClient.is_level_good(args.authorId) and not self.check(args, 'staff', 'me', 'admin'):
                    subClient.send_message(args.chatId, f"You don't have the level for that ({subClient.level})")
                    return
            else:
                return

            with suppress(Exception):
                [Thread(target=values, args=[args]).start() for key, values in self.commands.items() if command == key.lower()]

        @client.callbacks.event("on_image_message")
        def on_image_message(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)

            if args.chatId in subClient.only_view and not (self.check(args, "staff", "me", "admin")) and self.check(args, "staff", id_=self.botId):
                subClient.delete_message(args.chatId, args.messageId, reason="Read-only chat", asStaff=True)

        @client.callbacks.event("on_voice_message")
        def on_voice_message(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)

            if args.chatId in subClient.only_view and not (self.check(args, "staff", "me", "admin")) and self.check(args, "staff", id_=self.botId):
                subClient.delete_message(args.chatId, args.messageId, reason="Read-only chat", asStaff=True)

        @client.callbacks.event("on_sticker_message")
        def on_sticker_message(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)

            if args.chatId in subClient.only_view and not (self.check(args, "staff", "me", "admin")) and self.check(args, "staff", id_=self.botId):
                subClient.delete_message(args.chatId, args.messageId, reason="Read-only chat", asStaff=True)

        @client.callbacks.event("on_chat_invite")
        def on_chat_invite(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)

            subClient.join_chat(chatId=args.chatId)
            subClient.send_message(args.chatId, f"Hello!\n[B]I am a bot, if you have any question ask a staff member!\nHow can I help you?\n(you can do {subClient.prefix}help if you need help)")

        @client.callbacks.event("on_group_member_join")
        def on_group_member_join(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)
            if subClient.group_message_welcome:
                subClient.send_message(args.chatId, f"{subClient.group_message_welcome}")

        @client.callbacks.event("on_group_member_leave")
        def on_group_member_leave(data):
            try:
                commuId = data.json["ndcId"]
                subClient = self.get_community(commuId)
            except Exception:
                return

            args = Parameters(data, subClient)
            if subClient.group_message_goodbye:
                subClient.send_message(args.chatId, f"{subClient.group_message_welcome}")


class Bot(SubClient):
    def __init__(self, client, community, prefix: str = "!"):
        self.client = client
        self.marche = True
        self.prefix = prefix
        self.group_message_welcome = ""
        self.group_message_goodbye = ""

        if isinstance(community, int):
            self.community_id = community
            self.community = self.client.get_community_info(comId=self.community_id)
            self.community_amino_id = self.community.aminoId
        else:
            self.community_amino_id = community
            self.informations = self.client.get_from_code(f"http://aminoapps.com/c/{community}")
            self.community_id = self.informations.json["extensions"]["community"]["ndcId"]
            self.community = self.client.get_community_info(comId=self.community_id)

        self.community_name = self.community.name

        super().__init__(self.community_id, self.client.profile)

        try:
            self.community_leader_agent_id = self.community.json["agent"]["uid"]
        except Exception:
            self.community_leader_agent_id = "-"

        try:
            self.community_staff_list = self.community.json["communityHeadList"]
        except Exception:
            self.community_staff_list = ""

        if self.community_staff_list:
            self.community_leaders = [elem["uid"] for elem in self.community_staff_list if elem["role"] in (100, 102)]
            self.community_curators = [elem["uid"] for elem in self.community_staff_list if elem["role"] == 101]
            self.community_staff = [elem["uid"] for elem in self.community_staff_list]

        if not Path(f'{path_amino}/{self.community_amino_id}.json').exists():
            self.create_community_file()

        old_dict = self.get_file_dict()
        new_dict = self.create_dict()

        {**new_dict, **{i:e for i, e in old_dict.items() if i in new_dict}}

        self.update_file(old_dict)

        self.subclient = SubClient(comId=self.community_id, profile=client.profile)

        self.banned_words = self.get_file_info("banned_words")
        self.message_bvn = self.get_file_info("welcome")
        self.locked_command = self.get_file_info("locked_command")
        self.admin_locked_command = self.get_file_info("admin_locked_command")
        self.welcome_chat = self.get_file_info("welcome_chat")
        self.only_view = self.get_file_info("only_view")
        self.prefix = self.get_file_info("prefix")
        self.level = self.get_file_info("level")
        self.favorite_users = self.get_file_info("favorite_users")
        self.favorite_chats = self.get_file_info("favorite_chats")
        self.activity_status("on")
        new_users = self.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]
        if self.welcome_chat or self.message_bvn:
            with suppress(Exception):
                Thread(target=self.check_new_member).start()

    def create_community_file(self):
        with open(f'{path_amino}/{self.community_amino_id}.json', 'w', encoding='utf8') as file:
            dict = self.create_dict()
            file.write(dumps(dict, sort_keys=False, indent=4))

    def create_dict(self):
        return {"welcome": "", "banned_words": [], "locked_command": [], "admin_locked_command": [], "prefix": self.prefix, "only_view": [], "welcome_chat": "", "level": 0, "favorite_users": [], "favorite_chats": []}

    def get_dict(self):
        return {"welcome": self.message_bvn, "banned_words": self.banned_words, "locked_command": self.locked_command, "admin_locked_command": self.admin_locked_command, "prefix": self.prefix, "only_view": self.only_view, "welcome_chat": self.welcome_chat, "level": self.level, "favorite_users": self.favorite_users, "favorite_chats": self.favorite_chats}

    def update_file(self, dict=None):
        if not dict:
            dict = self.get_dict()
        with open(f"{path_amino}/{self.community_amino_id}.json", "w", encoding="utf8") as file:
            file.write(dumps(dict, sort_keys=False, indent=4))

    def get_file_info(self, info: str = None):
        with open(f"{path_amino}/{self.community_amino_id}.json", "r", encoding="utf8") as file:
            return load(file)[info]

    def get_file_dict(self, info: str = None):
        with open(f"{path_amino}/{self.community_amino_id}.json", "r", encoding="utf8") as file:
            return load(file)

    def set_prefix(self, prefix: str):
        self.prefix = prefix
        self.update_file()

    def set_level(self, level: int):
        self.level = level
        self.update_file()

    def set_welcome_message(self, message: str):
        self.message_bvn = message.replace('"', '“')
        self.update_file()

    def set_welcome_chat(self, chatId: str):
        self.welcome_chat = chatId
        self.update_file()

    def add_locked_command(self, liste: list):
        self.locked_command.extend(liste)
        self.update_file()

    def add_admin_locked_command(self, liste: list):
        self.admin_locked_command.extend(liste)
        self.update_file()

    def add_banned_words(self, liste: list):
        self.banned_words.extend(liste)
        self.update_file()

    def add_only_view(self, chatId: str):
        self.only_view.append(chatId)
        self.update_file()

    def add_favorite_users(self, value: str):
        self.favorite_users.append(value)
        self.update_file()

    def add_favorite_chats(self, value: str):
        self.favorite_chats.append(value)
        self.update_file()

    def remove_locked_command(self, liste: list):
        [self.locked_command.remove(elem) for elem in liste if elem in self.locked_command]
        self.update_file()

    def remove_admin_locked_command(self, liste: list):
        [self.admin_locked_command.remove(elem) for elem in liste if elem in self.admin_locked_command]
        self.update_file()

    def remove_banned_words(self, liste: list):
        [self.banned_words.remove(elem) for elem in liste if elem in self.banned_words]
        self.update_file()

    def remove_favorite_users(self, value: str):
        liste = [value]
        [self.favorite_users.remove(elem) for elem in liste if elem in self.favorite_users]
        self.update_file()

    def remove_favorite_chats(self, value: str):
        liste = [value]
        [self.favorite_chats.remove(elem) for elem in liste if elem in self.favorite_chats]
        self.update_file()

    def remove_only_view(self, chatId: str):
        self.only_view.remove(chatId)
        self.update_file()

    def unset_welcome_chat(self):
        self.welcome_chat = ""
        self.update_file()

    def is_in_staff(self, uid):
        return uid in self.community_staff

    def is_leader(self, uid):
        return uid in self.community_leaders

    def is_curator(self, uid):
        return uid in self.community_curators

    def is_agent(self, uid):
        return uid == self.community_leader_agent_id

    def accept_role(self, rid: str = None, cid: str = None):
        with suppress(Exception):
            self.accept_organizer(cid)
            return True
        with suppress(Exception):
            self.promotion(noticeId=rid)
            return True
        return False

    def get_staff(self, community):
        if isinstance(community, int):
            with suppress(Exception):
                community = self.client.get_community_info(com_id=community)
        else:
            try:
                informations = self.client.get_from_code(f"http://aminoapps.com/c/{community}")
            except Exception:
                return False

            community_id = informations.json["extensions"]["community"]["ndcId"]
            community = self.client.get_community_info(comId=community_id)

        try:
            community_staff_list = community.json["communityHeadList"]
            community_staff = [elem["uid"] for elem in community_staff_list]
        except Exception:
            community_staff_list = ""
        else:
            return community_staff

    def get_user_id(self, name_or_id):
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

    def ask_all_members(self, message, lvl: int = 20, type_bool: int = 1):
        size = self.get_all_users(start=0, size=1, type="recent").json['userProfileCount']
        st = 0

        while size > 0:
            value = size
            if value > 100:
                value = 100
            users = self.get_all_users(start=st, size=value)
            if type_bool == 1:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] == lvl]
            elif type_bool == 2:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
            elif type_bool == 3:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] >= lvl]
            self.start_chat(userId=user_lvl_list, message=message)
            size -= 100
            st += 100

    def ask_amino_staff(self, message):
        self.start_chat(userId=self.community_staff, message=message)

    def get_chat_id(self, chat: str = None):
        with suppress(Exception):
            return self.get_from_code(f"http://aminoapps.com/c/{chat}").objectId

        val = self.get_public_chat_threads()
        for title, chat_id in zip(val.title, val.chatId):
            if chat == title:
                return chat_id

        for title, chat_id in zip(val.title, val.chatId):
            if chat.lower() in title.lower() or chat == chat_id:
                return chat_id
        return False

    def stop_instance(self):
        self.marche = False

    def leave_community(self):
        self.client.leave_community(comId=self.community_id)
        self.marche = False
        for elem in self.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.leave_chat(elem)

    def check_new_member(self):
        if not (self.message_bvn and self.welcome_chat):
            return
        new_list = self.get_all_users(start=0, size=25, type="recent")
        new_member = [(elem["nickname"], elem["uid"]) for elem in new_list.json["userProfileList"]]
        for elem in new_member:
            name, uid = elem[0], elem[1]
            try:
                val = self.get_wall_comments(userId=uid, sorting='newest').commentId
            except Exception:
                val = True

            if not val and self.message_bvn:
                with suppress(Exception):
                    self.comment(message=self.message_bvn, userId=uid)
            if not val and self.welcome_chat:
                with suppress(Exception):
                    self.send_message(chatId=self.welcome_chat, message=f"Welcome here ‎‏‎‏@{name}!‬‭", mentionUserIds=[uid])

        new_users = self.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]

    def welcome_new_member(self):
        new_list = self.get_all_users(start=0, size=25, type="recent")
        new_member = [(elem["nickname"], elem["uid"]) for elem in new_list.json["userProfileList"]]

        for elem in new_member:
            name, uid = elem[0], elem[1]

            try:
                val = self.get_wall_comments(userId=uid, sorting='newest').commentId
            except Exception:
                val = True

            if not val and uid not in self.new_users and self.message_bvn:
                with suppress(Exception):
                    self.comment(message=self.message_bvn, userId=uid)

            if uid not in self.new_users and self.welcome_chat:
                with suppress(Exception):
                    self.send_message(chatId=self.welcome_chat, message=f"Welcome here ‎‏‎‏@{name}!‬‭", mentionUserIds=[uid])

        new_users = self.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]

    def feature_chats(self):
        for elem in self.favorite_chats:
            with suppress(Exception):
                self.favorite(time=2, chatId=elem)

    def feature_users(self):
        featured = [elem["uid"] for elem in self.get_featured_users().json["userProfileList"]]
        for elem in self.favorite_users:
            if elem not in featured:
                with suppress(Exception):
                    self.favorite(time=1, userId=elem)

    def get_member_level(self, uid):
        return self.get_user_info(userId=uid).level

    def is_level_good(self, uid):
        return self.get_user_info(userId=uid).level >= self.level

    def get_member_titles(self, uid):
        with suppress(Exception):
            return self.get_user_info(userId=uid).customTitles
        return False

    def get_member_info(self, uid):
        return self.get_user_info(userId=uid)

    def get_wallet_info(self):
        return self.client.get_wallet_info().json

    def get_wallet_amount(self):
        return self.client.get_wallet_info().totalCoins

    def pay(self, coins: int = 0, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
        if not transactionId:
            transactionId = f"{''.join(sample([lst for lst in hexdigits[:-6]], 8))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 12))}"
        self.send_coins(coins=coins, blogId=blogId, chatId=chatId, objectId=objectId, transactionId=transactionId)

    def favorite(self, time: int = 1, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        self.feature(time=time, userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)

    def unfavorite(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        self.unfeature(userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)

    def join_chat(self, chat: str = None, chatId: str = None):
        if not chat:
            with suppress(Exception):
                self.join_chat(chatId)
                return ""

        with suppress(Exception):
            chati = self.get_from_code(f"{chat}").objectId
            self.join_chat(chati)
            return chat

        chats = self.get_public_chat_threads()
        for title, chat_id in zip(chats.title, chats.chatId):
            if chat == title:
                self.join_chat(chat_id)
                return title

        chats = self.get_public_chat_threads()
        for title, chat_id in zip(chats.title, chats.chatId):
            if chat.lower() in title.lower() or chat == chat_id:
                self.join_chat(chat_id)
                return title

        return False

    def get_chats(self):
        return self.get_public_chat_threads()

    def join_all_chat(self):
        for elem in self.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.join_chat(elem)

    def leave_chat(self, chat: str):
        self.leave_chat(chat)

    def leave_all_chats(self):
        for elem in self.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.leave_chat(elem)

    def follow_user(self, uid):
        self.follow(userId=[uid])

    def unfollow_user(self, uid):
        self.unfollow(userId=uid)

    def add_title(self, uid, title: str, color: str = None):
        member = self.get_member_titles(uid)
        tlist = []
        clist = []
        with suppress(Exception):
            tlist = [elem['title'] for elem in member]
            clist = [elem['color'] for elem in member]
        tlist.append(title)
        clist.append(color)

        with suppress(Exception):
            self.edit_titles(uid, tlist, clist)
        return True

    def remove_title(self, uid, title: str):
        member = self.get_member_titles(uid)
        tlist = []
        clist = []
        for elem in member:
            tlist.append(elem["title"])
            clist.append(elem["color"])

        if title in tlist:
            nb = tlist.index(title)
            tlist.pop(nb)
            clist.pop(nb)
            self.edit_titles(uid, tlist, clist)
        return True

    def passive(self):
        bio_contents = [f"{self.prefix}cookie for cookies", "Hello everyone!", f"{self.prefix}help for help"]

        def change_bio_and_welcome_members():
            if self.welcome_chat or self.message_bvn:
                Thread(target=self.welcome_new_member).start()
            try:
                self.activity_status('on')
                self.edit_profile(content=choice(bio_contents))
            except Exception as e:
                print_exception(e)

        def feature_chats():
            try:
                Thread(target=self.feature_chats).start()
            except Exception as e:
                print_exception(e)

        def feature_users():
            try:
                Thread(target=self.feature_users).start()
            except Exception as e:
                print_exception(e)

        sleep(30)
        change_bio_and_welcome_members()
        feature_chats()
        feature_users()

        every().minute.do(change_bio_and_welcome_members)
        every(2).hours.do(feature_chats)
        every().day.do(feature_users)

        while self.marche:
            run_pending()
            sleep(10)

    def run(self):
        Thread(target=self.passive).start()
