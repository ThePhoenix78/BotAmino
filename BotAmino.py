from json import dumps, load
from time import sleep
from string import hexdigits
from pathlib import Path
from threading import Thread
from contextlib import suppress
from random import sample
from amino.sub_client import SubClient


path_utilities = "utilities"
path_amino = f'{path_utilities}/amino_list'
path_picture = f'{path_utilities}/pictures'
path_sound = f'{path_utilities}/sound'
path_download = f'{path_utilities}/download'
path_config = f"{path_utilities}/config.json"
path_eljson1 = f"{path_utilities}/elJson.json"
path_eljson2 = f"{path_utilities}/elJson2.json"
path_client = "client.txt"


for i in (path_utilities, path_picture, path_sound, path_download, path_amino):
    Path(i).mkdir(exist_ok=True)


class Parameters:
    __slots__ = ("subClient", "chatId", "authorId", "author", "message", "messageId")

    def __init__(self, data, communaute: dict = None):
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
