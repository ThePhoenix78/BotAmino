import sys
import os
import txt2pdf

from gtts import gTTS, lang
from json import dumps, load
from time import sleep
from string import hexdigits
from string import punctuation
from random import choice, randint, sample
from pathlib import Path
from threading import Thread
from contextlib import suppress
from unicodedata import normalize

from pdf2image import convert_from_path
from youtube_dl import YoutubeDL
from amino.client import Client
from amino.sub_client import SubClient

# Big optimisation thanks to SempreLEGIT#1378 ♥

version = "1.7.0"
print(f"version : {version}")

path_utilities = "utilities"
path_amino = 'utilities/amino_list'
path_picture = 'utilities/pictures'
path_sound = 'utilities/sound'
path_download = 'utilities/download'
path_config = "utilities/config.json"
path_client = "client.txt"

for i in (path_utilities, path_picture, path_sound, path_download, path_amino):
    Path(i).mkdir(exist_ok=True)


class Parameters:
    __slots__ = ("subClient", "chatId", "authorId", "author", "message", "messageId")

    def __init__(self, data):
        self.subClient = communaute[data.json["ndcId"]]
        self.chatId = data.message.chatId
        self.authorId = data.message.author.userId
        self.author = data.message.author.nickname
        self.message = data.message.content
        self.messageId = data.message.messageId


class BotAmino:
    def __init__(self, client, community, inv: str = None):
        self.client = client
        self.marche = True

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

        for key, value in new_dict.items():
            if key not in old_dict:
                old_dict[key] = value

        for key, value in old_dict.items():
            if key not in new_dict:
                del old_dict[key]

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
        self.subclient.activity_status("on")
        new_users = self.subclient.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]
        if self.welcome_chat or self.message_bvn:
            with suppress(Exception):
                Thread(target=self.check_new_member).start()

    def create_community_file(self):
        with open(f'{path_amino}/{self.community_amino_id}.json', 'w', encoding='utf8') as file:
            dict = self.create_dict()
            file.write(dumps(dict, sort_keys=False, indent=4))

    def create_dict(self):
        return {"welcome": "", "banned_words": [], "locked_command": [], "admin_locked_command": [], "prefix": "!", "only_view": [], "welcome_chat": "", "level": 0, "favorite_users": [], "favorite_chats": []}

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
            self.subclient.accept_organizer(cid)
            return True
        with suppress(Exception):
            self.subclient.promotion(noticeId=rid)
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

    def get_user_id(self, user_name):
        size = self.subclient.get_all_users(start=0, size=1, type="recent").json['userProfileCount']
        size2 = size

        st = 0
        while size > 0:
            value = size
            if value > 100:
                value = 100

            users = self.subclient.get_all_users(start=st, size=value)
            for user in users.json['userProfileList']:
                if user_name == user['nickname'] or user_name == user['uid']:
                    return (user["nickname"], user['uid'])
            size -= 100
            st += 100

        size = size2

        st = 0
        while size > 0:
            value = size
            if value > 100:
                value = 100

            users = self.subclient.get_all_users(start=st, size=value)
            for user in users.json['userProfileList']:
                if user_name.lower() in user['nickname'].lower():
                    return (user["nickname"], user['uid'])
            size -= 100
            st += 100

        return False

    def ask_all_members(self, message, lvl: int = 20, type_bool: int = 1):
        size = self.subclient.get_all_users(start=0, size=1, type="recent").json['userProfileCount']
        st = 0

        while size > 0:
            value = size
            if value > 100:
                value = 100
            users = self.subclient.get_all_users(start=st, size=value)
            if type_bool == 1:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] == lvl]
            elif type_bool == 2:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
            elif type_bool == 3:
                user_lvl_list = [user['uid'] for user in users.json['userProfileList'] if user['level'] >= lvl]
            self.subclient.start_chat(userId=user_lvl_list, message=message)
            size -= 100
            st += 100

    def ask_amino_staff(self, message):
        self.subclient.start_chat(userId=self.community_staff, message=message)

    def get_chat_id(self, chat: str = None):
        with suppress(Exception):
            return self.subclient.get_from_code(f"http://aminoapps.com/c/{chat}").objectId

        val = self.subclient.get_public_chat_threads()
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
        for elem in self.subclient.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def check_new_member(self):
        if not (self.message_bvn and self.welcome_chat):
            return
        new_list = self.subclient.get_all_users(start=0, size=25, type="recent")
        new_member = [(elem["nickname"], elem["uid"]) for elem in new_list.json["userProfileList"]]
        for elem in new_member:
            name, uid = elem[0], elem[1]
            try:
                val = self.subclient.get_wall_comments(userId=uid, sorting='newest').commentId
            except Exception:
                val = True

            if not val and self.message_bvn:
                with suppress(Exception):
                    self.subclient.comment(message=self.message_bvn, userId=uid)
            if not val and self.welcome_chat:
                with suppress(Exception):
                    self.send_message(chatId=self.welcome_chat, message=f"Welcome here ‎‏‎‏@{name}!‬‭", mentionUserIds=[uid])

        new_users = self.subclient.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]

    def welcome_new_member(self):
        new_list = self.subclient.get_all_users(start=0, size=25, type="recent")
        new_member = [(elem["nickname"], elem["uid"]) for elem in new_list.json["userProfileList"]]

        for elem in new_member:
            name, uid = elem[0], elem[1]

            try:
                val = self.subclient.get_wall_comments(userId=uid, sorting='newest').commentId
            except Exception:
                val = True

            if not val and uid not in self.new_users and self.message_bvn:
                with suppress(Exception):
                    self.subclient.comment(message=self.message_bvn, userId=uid)

            if uid not in self.new_users and self.welcome_chat:
                with suppress(Exception):
                    self.send_message(chatId=self.welcome_chat, message=f"Welcome here ‎‏‎‏@{name}!‬‭", mentionUserIds=[uid])

        new_users = self.subclient.get_all_users(start=0, size=30, type="recent")
        self.new_users = [elem["uid"] for elem in new_users.json["userProfileList"]]

    def feature_chats(self):
        for elem in self.favorite_chats:
            with suppress(Exception):
                self.favorite(time=2, chatId=elem)

    def feature_users(self):
        featured = [elem["uid"] for elem in self.subclient.get_featured_users().json["userProfileList"]]
        for elem in self.favorite_users:
            if elem not in featured:
                with suppress(Exception):
                    self.favorite(time=1, userId=elem)

    def get_member_level(self, uid):
        return self.subclient.get_user_info(userId=uid).level

    def is_level_good(self, uid):
        return self.subclient.get_user_info(userId=uid).level >= self.level

    def get_member_titles(self, uid):
        with suppress(Exception):
            return self.subclient.get_user_info(userId=uid).customTitles
        return False

    def get_member_info(self, uid):
        return self.subclient.get_user_info(userId=uid)

    def get_wallet_info(self):
        return self.client.get_wallet_info().json

    def get_wallet_amount(self):
        return self.client.get_wallet_info().totalCoins

    def pay(self, coins: int = 0, blogId: str = None, chatId: str = None, objectId: str = None, transactionId: str = None):
        if not transactionId:
            transactionId = f"{''.join(sample([lst for lst in hexdigits[:-6]], 8))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 4))}-{''.join(sample([lst for lst in hexdigits[:-6]], 12))}"
        self.subclient.send_coins(coins=coins, blogId=blogId, chatId=chatId, objectId=objectId, transactionId=transactionId)

    def delete_message(self, chatId: str, messageId: str, reason: str = "Clear", asStaff: bool = False):
        self.subclient.delete_message(chatId, messageId, asStaff, reason)

    def send_message(self, chatId: str = None, message: str = "None", messageType: str = None, file: str = None, fileType: str = None, replyTo: str = None, mentionUserIds: str = None):
        self.subclient.send_message(chatId=chatId, message=message, file=file, fileType=fileType, replyTo=replyTo, messageType=messageType, mentionUserIds=mentionUserIds)

    def favorite(self, time: int = 1, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        self.subclient.feature(time=time, userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)

    def unfavorite(self, userId: str = None, chatId: str = None, blogId: str = None, wikiId: str = None):
        self.subclient.unfeature(userId=userId, chatId=chatId, blogId=blogId, wikiId=wikiId)

    def join_chat(self, chat: str = None, chatId: str = None):
        if chat:
            chat = chat.replace("http:aminoapps.com/p/", "")
        else:
            with suppress(Exception):
                self.subclient.join_chat(chatId)
                return ""

            with suppress(Exception):
                chati = self.subclient.get_from_code(f"http://aminoapps.com/c/{chat}").objectId
                self.subclient.join_chat(chati)
                return chat

        chats = self.subclient.get_public_chat_threads()
        for title, chat_id in zip(chats.title, chats.chatId):
            if chat == title:
                self.subclient.join_chat(chat_id)
                return title

        chats = self.subclient.get_public_chat_threads()
        for title, chat_id in zip(chats.title, chats.chatId):
            if chat.lower() in title.lower() or chat == chat_id:
                self.subclient.join_chat(chat_id)
                return title

        return False

    def get_chats(self):
        return self.subclient.get_public_chat_threads()

    def join_all_chat(self):
        for elem in self.subclient.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.subclient.join_chat(elem)

    def leave_chat(self, chat: str):
        self.subclient.leave_chat(chat)

    def leave_all_chats(self):
        for elem in self.subclient.get_public_chat_threads().chatId:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def follow_user(self, uid):
        self.subclient.follow(userId=[uid])

    def unfollow_user(self, uid):
        self.subclient.unfollow(userId=uid)

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
            self.subclient.edit_titles(uid, tlist, clist)
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
            self.subclient.edit_titles(uid, tlist, clist)
        return True

    def passive(self):
        i = 30
        j = 470
        k = 7170
        m = 86370
        o = 0
        activities = [f"{self.prefix}cookie for cookies", "Hello everyone!", f"{self.prefix}help for help"]
        while self.marche:
            if i >= 60:
                if self.welcome_chat or self.message_bvn:
                    Thread(target=self.welcome_new_member).start()
                with suppress(Exception):
                    self.subclient.activity_status('on')
                    self.subclient.edit_profile(content=activities[o])
                i = 0
                o += 1
                if o > len(activities)-1:
                    o = 0
            if j >= 500:
                if self.welcome_chat or self.message_bvn:
                    with suppress(Exception):
                        Thread(target=self.check_new_member).start()
                j = 0

            if k >= 7200 and self.favorite_chats:
                with suppress(Exception):
                    Thread(target=self.feature_chats).start()
                k = 0

            if m >= 86400 and self.favorite_users:
                with suppress(Exception):
                    Thread(target=self.feature_users).start()
                m = 0

            k += 10
            m += 10
            j += 10
            i += 10

            sleep(10)

    def run(self):
        Thread(target=self.passive).start()


def print_exception(exc):
    print(repr(exc))


def is_it_bot(uid):
    return uid == botId


def is_it_me(uid):
    return uid in ('2137891f-82b5-4811-ac74-308d7a46345b', 'fa1f3678-df94-4445-8ec4-902651140841',
                   'f198e2f4-603c-481a-ab74-efd0f688f666')


def is_it_admin(uid):
    return uid in perms_list


def join_community(comId: str = None, inv: str = None):
    if inv:
        try:
            client.request_join_community(comId=comId, message='Cookie for everyone!!')
            return True
        except Exception as e:
            print_exception(e)
    else:
        try:
            client.join_community(comId=comId, invitationId=inv)
            return True
        except Exception as e:
            print_exception(e)


def join_amino(args):
    invit = None
    if taille_commu >= 20 and not (is_it_me(args.authorId) or is_it_admin(args.authorId)):
        args.subClient.send_message(args.chatId, "The bot has joined too many communities!")
        return

    staff = args.subClient.get_staff(args.message)
    if not staff:
        args.subClient.send_message(args.chatId, "Wrong amino ID!")
        return

    if args.authorId not in staff and not is_it_me(args.authorId):
        args.subClient.send_message(args.chatId, "You need to be in the community's staff!")
        return

    try:
        test = args.message.strip().split()
        amino_c = test[0]
        invit = test[1]
        invit = invit.replace("http://aminoapps.com/invite/", "")
    except Exception:
        amino_c = args.message
        invit = None

    try:
        val = args.subClient.client.get_from_code(f"http://aminoapps.com/c/{amino_c}")
        comId = val.json["extensions"]["community"]["ndcId"]
    except Exception:
        return

    isJoined = val.json["extensions"]["isCurrentUserJoined"]
    if not isJoined:
        size = val.json['extensions']['community']['membersCount']
        if size < 100 and not is_it_me(args.authorId):
            args.subClient.send_message(args.chatId, "Your community must have at least 100 members")
            return

        join_community(comId, invit)
        val = client.get_from_code(f"http://aminoapps.com/c/{amino_c}")
        isJoined = val.json["extensions"]["isCurrentUserJoined"]
        if isJoined:
            communaute[comId] = BotAmino(client=client, community=args.message)
            communaute[comId].run()
            auth = communaute[comId].subclient.get_user_info(args.message).nickname
            communaute[comId].ask_amino_staff(f"Hello! I am a bot and i can do a lot of stuff!\nI've been invited here by {auth}.\nIf you need help, you can do !help.\nEnjoy^^")
            args.subClient.send_message(args.chatId, "Joined!")
            return
        args.subClient.send_message(args.chatId, "Waiting for join!")
        return
    else:
        args.subClient.send_message(args.chatId, "Allready joined!")
        return

    args.subClient.send_message(args.chatId, "Something went wrong!")


def title(args):
    if args.subClient.is_in_staff(botId):
        color = None
        try:
            elem = args.message.strip().split("color=")
            args.message, color = elem[0], elem[1].strip()
            if not color.startswith("#"):
                color = "#"+color
            val = args.subClient.add_title(args.authorId, args.message, color)
        except Exception:
            val = args.subClient.add_title(args.authorId, args.message)

        if val:
            args.subClient.send_message(args.chatId, f"The titles of {args.author} has changed")


def cookie(args):
    args.subClient.send_message(args.chatId, f"Here is a cookie for {args.author} 🍪")


def ramen(args):
    args.subClient.send_message(args.chatId, f"Here are some ramen for {args.author} 🍜")


def dice(args):
    if not args.message:
        args.subClient.send_message(args.chatId, f"🎲 -{randint(1, 20)},(1-20)- 🎲")
    else:
        try:
            n1, n2 = map(int, args.message.split('d'))
            times = n1 if n1 < 20 else 20
            max_num = n2 if n2 < 1_000_000 else 1_000_000
            numbers = [randint(1, (max_num)) for _ in range(times)]

            args.subClient.send_message(args.chatId, f'🎲 -{sum(numbers)},[ {" ".join(map(str, numbers))}](1-{max_num})- 🎲')
        except Exception as e:
            print_exception(e)


def join(args):
    val = args.subClient.join_chat(args.message, args.chatId)
    if val or val == "":
        args.subClient.send_message(args.chatId, f"Chat {val} joined".strip())
    else:
        args.subClient.send_message(args.chatId, "No chat joined")


def join_all(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.join_all_chat()
        args.subClient.send_message(args.chatId, "All chat joined")


def leave_all(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.send_message(args.chatId, "Leaving all chat...")
        args.subClient.leave_all_chats()


def leave(args):
    if args.message and (is_it_me(args.authorId) or is_it_admin(args.authorId)):
        chat_ide = args.subClient.get_chat_id(args.message)
        if chat_ide:
            args.chatId = chat_ide
    args.subClient.leave_chat(args.chatId)


def clear(args):
    if (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        if args.subClient.is_in_staff(args.botId):
            value = True
        else:
            value = False
        size = 1
        msg = ""
        val = ""
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)
        if "chat=" in args.message and is_it_me(args.authorId):
            chat_name = args.message.rsplit("chat=", 1).pop()
            chat_ide = args.subClient.get_chat_id(chat_name)
            if chat_ide:
                args.chatId = chat_ide
            args.message = " ".join(args.message.strip().split()[:-1])

        with suppress(Exception):
            size = int(args.message.strip().split(' ').pop())
            msg = ' '.join(args.message.strip().split(' ')[:-1])

        if size > 50 and not is_it_me(args.authorId):
            size = 50

        if msg:
            with suppress(Exception):
                val = args.subClient.get_user_id(msg)

        messages = args.subClient.subclient.get_chat_messages(chatId=args.chatId, size=size)

        for message, authorId in zip(messages.messageId, messages.author.userId):
            with suppress(Exception):
                if not val:
                    args.subClient.delete_message(args.chatId, message, asStaff=value)
                elif authorId == val[1]:
                    args.subClient.delete_message(args.chatId, message, asStaff=value)


def spam(args):
    try:
        size = int(args.message.strip().split().pop())
        msg = " ".join(args.message.strip().split()[:-1])
    except ValueError:
        size = 1
        msg = args.message

    if size > 10 and not (is_it_me(args.authorId) or is_it_admin(args.authorId)):
        size = 10

    for _ in range(size):
        with suppress(Exception):
            args.subClient.send_message(args.chatId, msg)


def mention(args):
    try:
        size = int(args.message.strip().split().pop())
        args.message = " ".join(args.message.strip().split()[:-1])
    except ValueError:
        size = 1

    val = args.subClient.get_user_id(args.message)
    if not val:
        args.subClient.send_message(chatId=args.chatId, message="Username not found")
        return

    if size > 5 and not (is_it_me(args.authorId) or is_it_admin(args.authorId)):
        size = 5

    if val:
        for _ in range(size):
            with suppress(Exception):
                args.subClient.send_message(chatId=args.chatId, message=f"‎‏‎‏@{val[0]}‬‭", mentionUserIds=[val[1]])


def mentionall(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if args.message and is_it_me(args.authorId):
            chat_ide = args.subClient.get_chat_id(args.message)
            if chat_ide:
                args.chatId = chat_ide
            args.message = " ".join(args.message.strip().split()[:-1])

        mention = [userId for userId in args.subClient.subclient.get_chat_users(chatId=args.chatId).userId]
        test = "".join(["‎‏‎‏‬‭" for user in args.subClient.subclient.get_chat_users(chatId=args.chatId).userId])

        with suppress(Exception):
            args.subClient.send_message(chatId=args.chatId, message=f"@everyone{test}", mentionUserIds=mention)


def msg(args):
    value = 0
    size = 1
    ment = None
    with suppress(Exception):
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=False)

    if "chat=" in args.message and is_it_me(args.authorId):
        chat_name = args.message.rsplit("chat=", 1).pop()
        chat_ide = args.subClient.get_chat_id(chat_name)
        if chat_ide:
            args.chatId = chat_ide
        args.message = " ".join(args.message.strip().split()[:-1])

    try:
        size = int(args.message.split().pop())
        args.message = " ".join(args.message.strip().split()[:-1])
    except ValueError:
        size = 0

    try:
        value = int(args.message.split().pop())
        args.message = " ".join(args.message.strip().split()[:-1])
    except ValueError:
        value = size
        size = 1

    if not args.message and value == 1:
        args.message = f"‎‏‎‏@{args.author}‬‭"
        ment = args.authorId

    if size > 10 and not (is_it_me(args.authorId) or is_it_admin(args.authorId)):
        size = 10

    for _ in range(size):
        with suppress(Exception):
            args.subClient.send_message(chatId=args.chatId, message=f"{args.message}", messageType=value, mentionUserIds=ment)


def add_banned_word(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if not args.message or args.message in args.subClient.banned_words:
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_banned_words(args.message)
        args.subClient.send_message(args.chatId, "Banned word list updated")


def remove_banned_word(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if not args.message:
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.remove_banned_words(args.message)
        args.subClient.send_message(args.chatId, "Banned word list updated")


def banned_word_list(args):
    val = ""
    if args.subClient.banned_words:
        for elem in args.subClient.banned_words:
            val += elem + "\n"
    else:
        val = "No words in the list"
    args.subClient.send_message(args.chatId, val)


def sw(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.set_welcome_message(args.message)
        args.subClient.send_message(args.chatId, "Welcome message changed")


def get_chats(args):
    val = args.subClient.get_chats()
    for title, _ in zip(val.title, val.chatId):
        args.subClient.send_message(args.chatId, title)


def chat_id(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = args.subClient.get_chats()
        for title, chat_id in zip(val.title, val.chatId):
            if args.message.lower() in title.lower():
                args.subClient.send_message(args.chatId, f"{title} | {chat_id}")


def leave_amino(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.send_message(args.chatId, "Leaving the amino!")
        args.subClient.leave_community()
    del communaute[args.subClient.community_id]


def prank(args):
    with suppress(Exception):
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)

    transactionId = "5b3964da-a83d-c4d0-daf3-6e259d10fbc3"
    if args.message and is_it_me(args.authorId):
        chat_ide = args.subClient.get_chat_id(args.message)
        if chat_ide:
            args.chatId = chat_ide
    for _ in range(10):
        args.subClient.pay(coins=500, chatId=args.chatId, transactionId=transactionId)


def image(args):
    val = os.listdir("pictures")
    if val:
        file = choice(val)
        with suppress(Exception):
            with open(path_picture+file, 'rb') as fp:
                args.subClient.send_message(args.chatId, file=fp, fileType="image")
    else:
        args.subClient.send_message(args.chatId, "Error! No file")


def audio(args):
    val = os.listdir("sound")
    if val:
        file = choice(val)
        with suppress(Exception):
            with open(path_sound+file, 'rb') as fp:
                args.subClient.send_message(args.chatId, file=fp, fileType="audio")
    else:
        args.subClient.send_message(args.chatId, "Error! No file")


def telecharger(url):
    music = None
    if ("=" in url and "/" in url and " " not in url) or ("/" in url and " " not in url):
        if "=" in url and "/" in url:
            music = url.rsplit("=", 1)[-1]
        elif "/" in url:
            music = url.rsplit("/")[-1]

        if music in os.listdir(path_sound):
            return music

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            'extract-audio': True,
            'outtmpl': f"{path_download}/{music}.webm",
            }

        with YoutubeDL(ydl_opts) as ydl:
            video_length = ydl.extract_info(url, download=True).get('duration')
            ydl.cache.remove()

        url = music+".mp3"

        return url, video_length
    return False, False


def decoupe(musical, temps):
    size = 170
    with open(musical, "rb") as fichier:
        nombre_ligne = len(fichier.readlines())

    if temps < 180 or temps > 540:
        return False

    decoupage = int(size*nombre_ligne / temps)

    t = 0
    file_list = []
    for a in range(0, nombre_ligne, decoupage):
        b = a + decoupage
        if b >= nombre_ligne:
            b = nombre_ligne

        with open(musical, "rb") as fichier:
            lignes = fichier.readlines()[a:b]

        with open(musical.replace(".mp3", "PART"+str(t)+".mp3"),  "wb") as mus:
            for ligne in lignes:
                mus.write(ligne)

        file_list.append(musical.replace(".mp3", "PART"+str(t)+".mp3"))
        t += 1
    return file_list


def convert(args):
    music, size = telecharger(args.message)
    if music:
        music = f"{path_download}/{music}"
        val = decoupe(music, size)

        if not val:
            try:
                with open(music, 'rb') as fp:
                    args.subClient.send_message(args.chatId, file=fp, fileType="audio")
            except Exception:
                args.subClient.send_message(args.chatId, "Error! File too heavy (9 min max)")
            os.remove(music)
            return

        os.remove(music)
        for elem in val:
            with suppress(Exception):
                with open(elem, 'rb') as fp:
                    args.subClient.send_message(args.chatId, file=fp, fileType="audio")
            os.remove(elem)
        return
    args.subClient.send_message(args.chatId, "Error! Wrong link")


def helper(args):
    if not args.message:
        args.subClient.send_message(args.chatId, helpMsg)
    elif args.message == "msg":
        args.subClient.send_message(args.chatId, help_message)
    elif args.message == "ask":
        args.subClient.send_message(args.chatId, helpAsk)
    else:
        args.subClient.send_message(args.chatId, "No help is available for this command")


def reboot(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.send_message(args.chatId, "Restarting Bot")
        os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])


def stop(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.send_message(args.chatId, "Stopping Bot")
        os.execv(sys.executable, ["None", "None"])


def uinfo(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = ""
        val2 = ""
        uid = ""
        with suppress(Exception):
            val = args.subClient.client.get_user_info(args.message)
            val2 = args.subClient.subclient.get_user_info(args.message)

        if not val:
            uid = args.subClient.get_user_id(args.message)
            if uid:
                val = args.subClient.client.get_user_info(uid[1])
                val2 = args.subClient.subclient.get_user_info(uid[1])

        if not val:
            with suppress(Exception):
                lin = args.subClient.client.get_from_code(f"http://aminoapps.com/u/{args.message}").json["extensions"]["linkInfo"]["objectId"]
                val = args.subClient.client.get_user_info(lin)

            with suppress(Exception):
                val2 = args.subClient.subclient.get_user_info(lin)

        with suppress(Exception):
            with open("elJson.json", "w") as file:
                file.write(dumps(val.json, sort_keys=True, indent=4))

        with suppress(Exception):
            with open("elJson2.json", "w") as file:
                file.write(dumps(val2.json, sort_keys=True, indent=4))

        for i in ("elJson.json", "elJson2.json"):
            if os.path.getsize(i):
                txt2pdf.callPDF(i, "result.pdf")
                pages = convert_from_path('result.pdf', 150)
                file = 'result.jpg'
                for page in pages:
                    page.save(file,  'JPEG')
                    with open(file, 'rb') as fp:
                        args.subClient.send_message(args.chatId, file=fp, fileType="image")
                    os.remove(file)
                os.remove("result.pdf")

        if not os.path.getsize("elJson.json") and not os.path.getsize("elJson.json"):
            args.subClient.send_message(args.chatId, "Error!")


def cinfo(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = ""
        with suppress(Exception):
            val = args.subClient.client.get_from_code(f"http://aminoapps.com/c/{args.message}")

        with suppress(Exception):
            with open("elJson.json", "w") as file:
                file.write(dumps(val.json, sort_keys=True, indent=4))

        if os.path.getsize("elJson.json"):
            txt2pdf.callPDF("elJson.json", "result.pdf")
            pages = convert_from_path('result.pdf', 150)
            for page in pages:
                file = 'result.jpg'
                page.save(file,  'JPEG')
                with open(file, 'rb') as fp:
                    args.subClient.send_message(args.chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize("elJson.json"):
            args.subClient.send_message(args.chatId, "Error!")


def sendinfo(args):
    if (is_it_admin(args.authorId) or is_it_me(args.authorId)) and args.message != "":
        arguments = args.message.strip().split()
        for eljson in ('elJson.json', 'elJson2.json'):
            if Path(eljson).exists():
                arg = arguments.copy()
                with open(eljson, 'r') as file:
                    val = load(file)
                try:
                    memoire = val[arg.pop(0)]
                except Exception:
                    args.subClient.send_message(args.chatId, 'Wrong key!')
                if arg:
                    for elem in arg:
                        try:
                            memoire = memoire[str(elem)]
                        except Exception:
                            args.subClient.send_message(args.chatId, 'Wrong key!')
                args.subClient.send_message(args.chatId, memoire)


def get_global(args):
    val = args.subClient.get_user_id(args.message)[1]
    if val:
        ide = args.subClient.client.get_user_info(val).aminoId
        args.subClient.send_message(args.chatId, f"http://aminoapps.com/u/{ide}")
    else:
        args.subClient.send_message(args.chatId, "Error!")


def follow(args):
    args.subClient.follow_user(args.authorId)
    args.subClient.send_message(args.chatId, "Now following you!")


def unfollow(args):
    args.subClient.unfollow_user(args.authorId)
    args.subClient.send_message(args.chatId, "Unfollow!")


def stop_amino(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.stop_instance()
        del communaute[args.subClient.community_id]


def block(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = args.subClient.get_user_id(args.message)
        if val:
            args.subClient.client.block(val[1])
            args.subClient.send_message(args.chatId, f"User {val[0]} blocked!")


def unblock(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = args.subClient.client.get_blocked_users()
        for aminoId, userId in zip(val.aminoId, val.userId):
            if args.message in aminoId:
                args.subClient.client.unblock(userId)
                args.subClient.send_message(args.chatId, f"User {aminoId} unblocked!")


def accept(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if args.subClient.accept_role("", args.chatId):
            args.subClient.send_message(args.chatId, "Accepted!")
            return
        val = args.subClient.subclient.get_notices(start=0, size=25)
        for elem in val:
            print(elem["title"])
        ans = None
        res = None

        for elem in val:
            if 'become' in elem['title'] or "host" in elem['title']:
                res = elem['noticeId']
            if res:
                ans = args.subClient.accept_role(res)
            if ans:
                args.subClient.send_message(args.chatId, "Accepted!")
                return
        else:
            args.subClient.send_message(args.chatId, "Error!")


def say(args):
    audio_file = f"{path_download}/ttp{randint(1,500)}.mp3"
    langue = list(lang.tts_langs().keys())
    if not args.message:
        args.message = args.subClient.subclient.get_chat_messages(chatId=args.chatId, size=2).content[1]
    gTTS(text=args.message, lang=choice(langue), slow=False).save(audio_file)
    try:
        with open(audio_file, 'rb') as fp:
            args.subClient.send_message(args.chatId, file=fp, fileType="audio")
    except Exception:
        args.subClient.send_message(args.chatId, "Too heavy!")
    os.remove(audio_file)


def ask_thing(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        lvl = ""
        boolean = 1
        if "lvl=" in args.message:
            lvl = args.message.rsplit("lvl=", 1)[1].strip().split(" ", 1)[0]
            args.message = args.message.replace("lvl="+lvl, "").strip()
        elif "lvl<" in args.message:
            lvl = args.message.rsplit("lvl<", 1)[1].strip().split(" ", 1)[0]
            args.message = args.message.replace("lvl<"+lvl, "").strip()
            boolean = 2
        elif "lvl>" in args.message:
            lvl = args.message.rsplit("lvl>", 1)[1].strip().split(" ", 1)[0]
            args.message = args.message.replace("lvl>"+lvl, "").strip()
            boolean = 3
        try:
            lvl = int(lvl)
        except ValueError:
            lvl = 20

        args.subClient.ask_all_members(args.message+f"\n[CUI]This message was sent by {args.author}\n[CUI]I am a bot and have a nice day^^", lvl, boolean)
        args.subClient.send_message(args.chatId, "Asking...")


def ask_staff(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        amino_list = client.sub_clients()
        for commu in amino_list.comId:
            communaute[commu].ask_amino_staff(message=args.message)
        args.subClient.send_message(args.chatId, "Asking...")


def prefix(args):
    if args.message:
        args.subClient.set_prefix(args.message)
        args.subClient.send_message(args.chatId, f"prefix set as {args.message}")


def lock_command(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if not args.message or args.message in args.subClient.locked_command or args.message not in commands_dict.keys() or args.message in ("lock", "unlock"):
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_locked_command(args.message)
        args.subClient.send_message(args.chatId, "Locked command list updated")


def unlock_command(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        if args.message:
            try:
                args.message = args.message.lower().strip().split()
            except Exception:
                args.message = [args.message.lower().strip()]
            args.subClient.remove_locked_command(args.message)
            args.subClient.send_message(args.chatId, "Locked command list updated")


def locked_command_list(args):
    val = ""
    if args.subClient.locked_command:
        for elem in args.subClient.locked_command:
            val += elem+"\n"
    else:
        val = "No locked command"
    args.subClient.send_message(args.chatId, val)


def admin_lock_command(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        if not args.message or args.message not in commands_dict.keys() or args.message == "alock":
            return

        command = args.subClient.admin_locked_command
        args.message = [args.message]

        if args.message[0] in command:
            args.subClient.remove_admin_locked_command(args.message)
        else:
            args.subClient.add_admin_locked_command(args.message)

        args.subClient.send_message(args.chatId, "Locked command list updated")


def locked_admin_command_list(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        val = ""
        if args.subClient.admin_locked_command:
            for elem in args.subClient.admin_locked_command:
                val += elem+"\n"
        else:
            val = "No locked command"
        args.subClient.send_message(args.chatId, val)


def read_only(args):
    if args.subClient.is_in_staff(args.botId) and (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        chats = args.subClient.only_view
        if args.chatId not in chats:
            args.subClient.add_only_view(args.chatId)
            args.subClient.send_message(args.chatId, "This chat is now in only-view mode")
        else:
            args.subClient.remove_only_view(args.chatId)
            args.subClient.send_message(args.chatId, "This chat is no longer in only-view mode")
        return
    elif not args.subClient.is_in_staff(botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def keep_favorite_users(args):
    if args.subClient.is_in_staff(botId) and (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        users = args.subClient.favorite_users
        try:
            val = args.subClient.get_user_id(args.message)
            user, userId = val[0], val[1]
        except Exception:
            args.subClient.send_message(args.chatId, "Error, user not found!")
            return
        if userId not in users:
            args.subClient.add_favorite_users(userId)
            args.subClient.send_message(args.chatId, f"Added {user} to favorite users")
            with suppress(Exception):
                args.subClient.favorite(time=1, userId=userId)
        return
    elif not args.subClient.is_in_staff(botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def unkeep_favorite_users(args):
    if args.subClient.is_in_staff(botId) and (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        users = args.subClient.favorite_users
        try:
            val = args.subClient.get_user_id(args.message)
            user, userId = val[0], val[1]
        except Exception:
            args.subClient.send_message(args.chatId, "Error, user not found!")
            return
        if userId in users:
            args.subClient.remove_favorite_users(userId)
            args.subClient.send_message(args.chatId, f"Removed {user} to favorite users")
            with suppress(Exception):
                args.subClient.unfavorite(userId=userId)
        return
    elif not args.subClient.is_in_staff(botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def keep_favorite_chats(args):
    if args.subClient.is_in_staff(botId) and (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        chats = args.subClient.favorite_chats
        val = args.subClient.get_chats()

        for title, chatId in zip(val.title, val.chatId):
            if args.message == title and chatId not in chats:
                args.subClient.add_favorite_chats(args.chatId)
                args.subClient.send_message(args.chatId, f"Added {title} to favorite chats")
                with suppress(Exception):
                    args.subClient.favorite(time=1, chatId=args.chatId)
                return

        for title, chatId in zip(val.title, val.chatId):
            if args.message.lower() in title.lower() and chatId not in chats:
                args.subClient.add_favorite_chats(chatId)
                args.subClient.send_message(args.chatId, f"Added {title} to favorite chats")
                with suppress(Exception):
                    args.subClient.favorite(time=1, chatId=chatId)
                return
    elif not args.subClient.is_in_staff(botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def unkeep_favorite_chats(args):
    if args.subClient.is_in_staff(botId) and (args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
        chats = args.subClient.favorite_chats
        val = args.subClient.get_chats()

        for title, chatid in zip(val.title, val.chatId):
            if args.message == title and chatid in chats:
                args.subClient.remove_favorite_chats(chatid)
                args.subClient.unfavorite(chatId=chatid)
                args.subClient.send_message(args.chatId, f"Removed {title} to favorite chats")
                return

        for title, chatid in zip(val.title, val.chatId):
            if args.message.lower() in title.lower() and chatid in chats:
                args.subClient.remove_favorite_chats(chatid)
                args.subClient.unfavorite(chatId=chatid)
                args.subClient.send_message(args.chatId, f"Removed {title} to favorite chats")
                return

    elif not args.subClient.is_in_staff(args.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def welcome_channel(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.set_welcome_chat(args.chatId)
        args.subClient.send_message(args.chatId, "Welcome channel set!")


def unwelcome_channel(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        args.subClient.unset_welcome_chat()
        args.subClient.send_message(args.chatId, "Welcome channel unset!")


def level(args):
    if args.subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId):
        try:
            args.message = int(args.message)
        except Exception:
            args.subClient.send_message(args.chatId, "Error, wrong level")
            return
        if args.message > 20:
            args.message = 20
        if args.message < 0:
            args.message = 0
        args.subClient.set_level(args.message)
        args.subClient.send_message(args.chatId, f"Level set to {args.message}!")


def taxe(args):
    if is_it_me(args.authorId) or is_it_admin(args.authorId):
        coins = args.subClient.get_wallet_amount()
        if coins >= 1:
            amt = 0
            while coins > 500:
                args.subClient.pay(500, chatId=args.chatId)
                coins -= 500
                amt += 500
            args.subClient.pay(int(coins), chatId=args.chatId)
            args.subClient.send_message(args.chatId, f"Sending {coins+amt} coins...")
        else:
            args.subClient.send_message(args.chatId, "Account is empty!")


commands_dict = {"help": helper, "title": title, "dice": dice, "join": join, "ramen": ramen, "level": level,
                 "cookie": cookie, "leave": leave, "abw": add_banned_word, "rbw": remove_banned_word,
                 "bwl": banned_word_list, "llock": locked_command_list, "view": read_only, "taxe": taxe,
                 "clear": clear, "joinall": join_all, "leaveall": leave_all, "reboot": reboot,
                 "stop": stop, "spam": spam, "mention": mention, "msg": msg, "alock": admin_lock_command,
                 "uinfo": uinfo, "cinfo": cinfo, "joinamino": join_amino, "chatlist": get_chats, "sw": sw,
                 "accept": accept, "chat_id": chat_id, "prank": prank, "prefix": prefix, "allock": locked_admin_command_list,
                 "leaveamino": leave_amino, "sendinfo": sendinfo, "image": image, "all": mentionall,
                 "block": block, "unblock": unblock, "follow": follow, "unfollow": unfollow, "unwelcome": unwelcome_channel,
                 "stop_amino": stop_amino, "block": block, "unblock": unblock, "welcome": welcome_channel,
                 "ask": ask_thing, "askstaff": ask_staff, "lock": lock_command, "unlock": unlock_command,
                 "global": get_global, "audio": audio, "convert": convert, "say": say,
                 "keepu": keep_favorite_users, "unkeepu": unkeep_favorite_users, "keepc": keep_favorite_chats, "unkeepc": unkeep_favorite_chats}


helpMsg = f"""
[CB]-- COMMON COMMAND --

• help (command)\t:  show this or the help associated to the command
• title (title)\t:  edit titles*
• dice (xdy)\t:  return x dice y (1d20) per default
• join (chat)\t:  join the specified channel
• mention (user)\t: mention an user
• spam (amount)\t: spam an message (limited to 10)
• msg (type)\t: send a "special" message (limited to 10)
• bwl\t:  the list of banneds words*
• llock\t: the list of locked commands
• chatlist\t: the list of public chats
• global (user)\t: give the global profile of the user
• leave\t:  leave the current channel
• follow\t: follow you
• unfollow\t: unfollow you
• convert (url)\t: will convert and send the music from the url (9 min max)
• audio\t: will send audio
• image\t: will send an image
• say\t: will say the message in audio
• ramen\t:  give ramens!
• cookie\t:  give a cookie!
\n
[CB]-- STAFF COMMAND --

• accept\t: accept the staff role
• abw (word list)\t:  add a banned word to the list*
• rbw (word list)\t:  remove a banned word from the list*
• sw (message)\t:  set the welcome message for new members (will start as soon as the welcome message is set)
• welcome\t:  set the welcome channel**
• unwelcome\t:  unset the welcome channel**
• ask (message)(lvl=)\t: ask to all level (lvl) something**
• clear (amount)\t:  clear the specified amount of message from the chat (max 50)*
• joinall\t:  join all public channels
• leaveall\t:  leave all public channels
• leaveamino\t: leave the community
• all\t: mention all the users of a channel
• lock (command)\t: lock the command (nobody can use it)
• unlock (command)\t: remove the lock for the command
• view\t: set or unset the current channel to read-only*
• prefix (prefix)\t: set the prefix for the amino
• level (level)\t: set the level required for the commands
• keepu (user)\t: keep in favorite an user*
• unkeepu (user)\t: remove from favorite an user*
• keepc (chat)\t: keep in favorite a chat*
• unkeepc (chat)\t: remove from favorite a chat*
\n
[CB]-- SPECIAL --

• joinamino (amino id): join the amino (you need to be in the amino's staff)**
• uinfo (user): will give informations about the user²
• cinfo (aminoId): will give informations about the community²
• sendinfo (args): send the info from uinfo or cinfo²
• alock (command): lock or unlock the command for everyone except the owenr of the bot²
• allock\t: the list of the admin locked commands²

[CB]-- NOTE --

*(only work if bot is in staff)
**(In developpement)
²(only for devlopper or bot owner)

[CI]You want to support my work? You can give me AC!^^

[C]-- all commands are available for the owner of the bot --
[C]-- Bot made by @The_Phoenix --
[C]--Version : {version}--
"""


help_message = """
--MESSAGES--

0 - BASE
1 - STRIKE
50 - UNSUPPORTED_MESSAGE
57 - REJECTED_VOICE_CHAT
58 - MISSED_VOICE_CHAT
59 - CANCELED_VOICE_CHAT
100 - DELETED_MESSAGE
101 - JOINED_CHAT
102 - LEFT_CHAT
103 - STARTED_CHAT
104 - CHANGED_BACKGROUND
105 - EDITED_CHAT
106 - EDITED_CHAT_ICON
107 - STARTED_VOICE_CHAT
109 - UNSUPPORTED_MESSAGE
110 - ENDED_VOICE_CHAT
113 - EDITED_CHAT_DESCRIPTION
114 - ENABLED_LIVE_MODE
115 - DISABLED_LIVE_MODE
116 - NEW_CHAT_HOST
124 - INVITE_ONLY_CHANGED
125 - ENABLED_VIEW_ONLY
126 - DISABLED_VIEW_ONLY

- chat="chatname": will send the message in the specified chat
"""

helpAsk = """
Example :
- !ask Hello! Can you read this : [poll | http://aminoapp/poll]? Have a nice day!^^ lvl=6
"""

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
    sys.exit(1)

identifiant = login[0].strip()
mdp = login[1].strip()

client = Client()
client.login(email=identifiant, password=mdp)
botId = client.userId
amino_list = client.sub_clients()

communaute = {}
taille_commu = 0

for command in command_lock:
    if command in commands_dict.keys():
        del commands_dict[command]


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


perms_list = tradlist(perms_list)


def threadLaunch(commu):
    with suppress(Exception):
        commi = BotAmino(client=client, community=commu)
        communaute[commi.community_id] = commi
        communaute[commi.community_id].run()


taille_commu = len([Thread(target=threadLaunch, args=[commu]).start() for commu in amino_list.comId])


def filtre_message(message, code):
    para = normalize('NFD', message).encode(code, 'ignore').decode("utf8").strip().lower()
    para = para.translate(str.maketrans("", "", punctuation))
    return para


@client.callbacks.event("on_text_message")
def on_text_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    args = Parameters(data)
    # print(f"{data.message.author.nickname} : {message}")

    if args.chatId in subClient.only_view and not (subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)) and subClient.is_in_staff(botId):
        subClient.delete_message(args.chatId, args.messageId, "Read-only chat", asStaff=True)
        return

    if not (is_it_me(args.authorId) or is_it_admin(args.authorId) or is_it_bot(args.authorId)) and not subClient.is_in_staff(args.authorId) and subClient.banned_words:
        with suppress(Exception):
            para = filtre_message(args.message, "ascii").split()

            if para != [""]:
                for elem in para:
                    if elem in subClient.banned_words:
                        with suppress(Exception):
                            subClient.delete_message(args.chatId, args.messageId, "Banned word", asStaff=True)
                        return

        with suppress(Exception):
            para = filtre_message(args.message, "utf8").split()

            if para != [""]:
                for elem in para:
                    if elem in subClient.banned_words:
                        with suppress(Exception):
                            subClient.delete_message(args.chatId, args.messageId, "Banned word", asStaff=True)
                        return

    if args.message.startswith(subClient.prefix) and not is_it_bot(args.authorId):

        command = args.message.split()[0][len(subClient.prefix):]
        args.message = ' '.join(args.message.split()[1:])

        if command in subClient.locked_command and not (subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
            return
        if command in subClient.admin_locked_command and not (is_it_me(args.authorId) or is_it_admin(args.authorId)):
            return
        if not subClient.is_level_good(args.authorId) and not (subClient.is_in_staff(args.authorId) or is_it_me(args.authorId) or is_it_admin(args.authorId)):
            subClient.send_message(args.chatId, f"You don't have the level for that ({subClient.level})")
            return
    else:
        return

    with suppress(Exception):
        [Thread(target=values, args=[args]).start() for key, values in commands_dict.items() if command == key.lower()]


@client.callbacks.event("on_image_message")
def on_image_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    chatId = data.message.chatId
    authorId = data.message.author.userId
    messageId = data.message.messageId

    if chatId in subClient.only_view and not (subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId)) and subClient.is_in_staff(botId):
        subClient.delete_message(chatId, messageId, "Read-only chat", asStaff=True)


@client.callbacks.event("on_voice_message")
def on_voice_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    chatId = data.message.chatId
    authorId = data.message.author.userId
    messageId = data.message.messageId

    if chatId in subClient.only_view and not (subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId)) and subClient.is_in_staff(botId):
        subClient.delete_message(chatId, messageId, "Read-only chat", asStaff=True)


@client.callbacks.event("on_sticker_message")
def on_sticker_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    chatId = data.message.chatId
    authorId = data.message.author.userId
    messageId = data.message.messageId

    if chatId in subClient.only_view and not (subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId)) and subClient.is_in_staff(botId):
        subClient.delete_message(chatId, messageId, "Read-only chat", asStaff=True)


@client.callbacks.event("on_chat_invite")
def on_chat_invite(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    chatId = data.message.chatId

    subClient.join_chat(chatId=chatId)
    subClient.send_message(chatId, f"Hello!\nI am a bot, if you have any question ask a staff member!^^\nHow can I help you?\n(you can do {subClient.prefix}help for help)")


print("Ready")
