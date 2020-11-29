import sys
import os
from json import dumps, load
from time import sleep
from string import punctuation
from random import choice, randint
from pathlib import Path
from threading import Thread
from contextlib import suppress
from unicodedata import normalize
from pdf2image import convert_from_path

from amino.client import Client
from amino.sub_client import SubClient
from youtube_dl import YoutubeDL

# Big optimisation thanks to SempreLEGIT#1378 ♥

path_lock = 'utilities/locked_commands'
path_welcome = 'utilities/welcome_message'
path_banned_words = 'utilities/banned_words'
path_picture = 'pictures'
path_sound = 'sound'
path_download = 'download'

depart = os.getcwd()

for i in ("utilities", path_welcome, path_banned_words, path_picture, path_sound, path_download, path_lock):
    Path(i).mkdir(exist_ok=True)


class BotAmino:
    def __init__(self, client, community, inv: str = None):
        self.client = client
        self.prefixeId = "!"
        self.lvlmin = 0
        self.marche = True

        if isinstance(community, int):
            self.communityId = community
            self.community = self.client.get_community_info(comId=self.communityId)
            self.communityAminoId = self.community.aminoId
        else:
            self.communityAminoId = community
            self.informations = self.client.get_from_code("https://aminoapps.com/c/"+community)
            self.communityId = self.informations.json["extensions"]["community"]["ndcId"]
            self.community = self.client.get_community_info(comId=self.communityId)

        self.communityName = self.community.name
        try:
            self.communityLeaderAgentId = self.community.json["agent"]["uid"]
        except Exception:
            self.communityLeaderAgentId = "-"

        try:
            self.communityStaffList = self.community.json["communityHeadList"]
        except Exception:
            self.communityStaffList = ""

        if self.communityStaffList:
            self.communityLeaders = [elem["uid"] for elem in self.communityStaffList if elem["role"] in (100, 102)]
            self.communityCurators = [elem["uid"] for elem in self.communityStaffList if elem["role"] == 101]
            self.communityStaff = [elem["uid"] for elem in self.communityStaffList]

        if not Path(f'{path_welcome}/{self.communityAminoId}.txt').exists():
            self.create_files()

        self.subclient = SubClient(comId=self.communityId, profile=client.profile)
        self.bannedWords = self.banned_words()
        self.messageBvn = self.get_welcome_message()
        self.lockedCommand = self.get_locked_command()
        self.subclient.activity_status("on")
        userList = self.subclient.get_all_users(start=0, size=25, type="recent")
        self.allUsers = userList.json['userProfileCount']
        self.allNewUsersCommunityId = [elem["uid"] for elem in userList.json["userProfileList"]]

    def create_files(self):
        with open(f'{path_welcome}/{self.communityAminoId}.txt', 'w', encoding='utf8') as file_:
            pass
        with open(f'{path_banned_words}/{self.communityAminoId}.json', 'w', encoding='utf8') as file_:
            file_.write('[]')
        with open(f'{path_lock}/{self.communityAminoId}.json', 'w', encoding='utf8') as file_:
            file_.write('[]')

    def is_in_staff(self, UID):
        return UID in self.communityStaff

    def is_leader(self, UID):
        return UID in self.communityLeaders

    def is_curator(self, UID):
        return UID in self.communityCurators

    def is_agent(self, UID):
        return UID == self.communityLeaderAgentId

    def accept_role(self, RID: str):
        try:
            self.subclient.promotion(noticeId=RID)
            return True
        except Exception:
            return False

    def get_staff(self, community):
        if isinstance(community, int):
            with suppress(Exception):
                community = self.client.get_community_info(com_id=community)
        else:
            try:
                informations = self.client.get_from_code("https://aminoapps.com/c/"+community)
            except Exception:
                return False

            communityId = informations.json["extensions"]["community"]["ndcId"]
            community = self.client.get_community_info(comId=communityId)

        try:
            communityStaffList = community.json["communityHeadList"]
            communityStaff = [elem["uid"] for elem in communityStaffList]
        except Exception:
            communityStaffList = ""

        return communityStaff

    def get_user_id(self, Uname):
        size = self.allUsers
        st = 0
        while size > 100:
            users = self.subclient.get_all_users(type="recent", start=st, size=100)
            for user in users.json['userProfileList']:
                if Uname == user['nickname'] or Uname == user['uid']:
                    return (user["nickname"], user['uid'])

            for user in users.json['userProfileList']:
                if Uname.lower() in user['nickname'].lower():
                    return (user["nickname"], user['uid'])
            size -= 100
            st += 100

        users = self.subclient.get_all_users(type="recent", start=0, size=size)

        for user in users.json['userProfileList']:
            if Uname.lower() == user['nickname'].lower() or Uname == user['uid']:
                return (user["nickname"], user['uid'])

        for user in users.json['userProfileList']:
            if Uname.lower() in user['nickname'].lower():
                return (user["nickname"], user['uid'])
        return False

    def ask_all_members(self, message, lvl: int):
        size = self.allUsers
        st = 0

        while size > 100:
            users = self.subclient.get_all_users(type="recent", start=st, size=100)
            userLvlList = []
            userLvlList = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
            self.subclient.start_chat(userId=userLvlList, message=message)
            size -= 100
            st += 100

        userLvlList = []
        users = self.subclient.get_all_users(type="recent", start=0, size=size)
        userLvlList = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
        self.subclient.start_chat(userId=userLvlList, message=message)

    def ask_amino_staff(self, message):
        self.subclient.start_chat(userId=self.communityStaff, message=message)

    def get_chat_id(self, chat: str = None):
        with suppress(Exception):
            return self.subclient.get_from_code(chat).objectId

        val = self.subclient.get_public_chat_threads()
        for elem, t in zip(val.title, val.chatId):
            if chat == elem:
                return t
        for elem, t in zip(val.title, val.chatId):
            if chat.lower() in elem.lower() or chat == t:
                return t
        return False

    def set_prefixe(self, prefixe: str):
        self.prefixeId = prefixe

    def stop_instance(self):
        self.marche = False

    def set_welcome_message(self, message: str):
        with open(f"{path_welcome}/{self.communityAminoId}.txt", "w", encoding="utf8") as fic:
            fic.write(message)
        self.messageBvn = message

    def get_welcome_message(self):
        with open(f"{path_welcome}/{self.communityAminoId}.txt", "r", encoding="utf8") as fic:
            return fic.read()

    def add_locked_command(self, liste: list):
        self.lockedCommand.extend(liste)
        with open(f"{path_lock}/{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(dumps(self.lockedCommand, sort_keys=False, indent=4))

    def remove_locked_command(self, liste: list):
        for elem in liste:
            if elem in self.lockedCommand:
                self.lockedCommand.remove(elem)
        with open(f"{path_lock}/{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(dumps(self.lockedCommand, sort_keys=False, indent=4))

    def get_locked_command(self):
        with open(f"{path_lock}/{self.communityAminoId}.json", "r", encoding="utf8") as fic:
            return load(fic)

    def banned_words(self):
        with open(f"{path_banned_words}/{self.communityAminoId}.json", "r", encoding="utf8") as fic:
            message = load(fic)
        message = [elem.lower() for elem in message]
        return message

    def add_banned_words(self, liste: list):
        self.bannedWords.extend(liste)
        with open(f"{path_banned_words}/{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(dumps(self.bannedWords, sort_keys=False, indent=4))

    def remove_banned_words(self, liste: list):
        for elem in liste:
            if elem in self.bannedWords:
                self.bannedWords.remove(elem)
        with open(f"{path_banned_words}/{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(dumps(self.bannedWords, sort_keys=False, indent=4))

    def leave_community(self):
        self.client.leave_community(comId=self.communityId)
        self.marche = False
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def check_new_member(self):
        newList = self.subclient.get_all_users()
        newMember = [elem["uid"] for elem in newList.json["userProfileList"]]
        for elem in newMember:
            try:
                val = self.subclient.get_wall_comments(userId=elem, sorting='newest').commentId
            except Exception:
                val = True

            if not val and elem not in self.allNewUsersCommunityId:
                with suppress(Exception):
                    self.subclient.comment(message=self.messageBvn, userId=elem)

                self.allUsers += 1
                self.allNewUsersCommunityId.append(elem)

    def get_member_level(self, UID):
        return self.subclient.get_user_info(userId=UID).level

    def is_level_good(self, UID):
        return self.subclient.get_user_info(userId=UID).level > self.lvlmin

    def get_member_titles(self, UID):
        try:
            return self.subclient.get_user_info(userId=UID).customTitles
        except Exception:
            return False

    def get_member_info(self, UID):
        return self.subclient.get_user_info(userId=UID)

    def get_message_level(self, level: int):
        return f"You need the level {level} to do this command"

    def delete_message(self, chatId: str, messageId: str, reason: str = "Clear", asStaff: bool = False):
        self.subclient.delete_message(chatId, messageId, asStaff, reason)

    def send_message(self, chatId: str = None, message: str = "None", messageType: str = None, file: str = None, fileType: str = None, replyTo: str = None, mentionUserIds: str = None):
        self.subclient.send_message(chatId=chatId, message=message, file=file, fileType=fileType, replyTo=replyTo, messageType=messageType, mentionUserIds=mentionUserIds)

    def join_chat(self, chat: str, chatId: str = None):
        chat = chat.replace("http:aminoapps.com/p/", "")
        if not chat:
            with suppress(Exception):
                self.subclient.join_chat(chatId)
                return ""

            with suppress(Exception):
                chati = self.subclient.get_from_code(chat).objectId
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
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.join_chat(elem)

    def leave_chat(self, chat: str):
        self.subclient.leave_chat(chat)

    def leave_all_chats(self):
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def follow_user(self, UID):
        self.subclient.follow(userId=[UID])

    def unfollow_user(self, UID):
        self.subclient.unfollow(userId=UID)

    def add_title(self, UID, title: str, color: str = "#999999"):
        member = self.get_member_titles(UID)
        tlist = []
        clist = []
        with suppress(Exception):
            tlist = [elem['title'] for elem in member]
            clist = [elem['color'] for elem in member]

        tlist.append(title)
        clist.append(color)

        with suppress(Exception):
            self.subclient.edit_titles(UID, tlist, clist)

        return True

    def remove_title(self, UID, title: str):
        member = self.get_member_titles(UID)
        tlist = []
        clist = []
        for elem in member:
            tlist.append(elem["title"])
            clist.append(elem["color"])

        if title in tlist:
            nb = tlist.index(title)
            tlist.pop(nb)
            clist.pop(nb)
            self.subclient.edit_titles(UID, tlist, clist)
        return True

    def passive(self):
        i = 59
        o = 0
        activities = ["!cookie for cookies", "Hello everyone!", "!help for help"]
        while self.marche:
            if i >= 60:
                if self.messageBvn:
                    self.check_new_member()
                with suppress(Exception):
                    self.subclient.activity_status('on')
                self.subclient.edit_profile(content=activities[o])
                i = 0
                o += 1
                if o > len(activities)-1:
                    o = 0
            i += 1
            sleep(1)

    def run(self):
        th2 = Thread(target=self.passive)
        th2.start()


def is_it_bot(UID):
    return UID == bot_id


def is_it_me(UID):
    return UID in ('2137891f-82b5-4811-ac74-308d7a46345b', 'fa1f3678-df94-4445-8ec4-902651140841',
                   'f198e2f4-603c-481a-ab74-efd0f688f666')


def is_it_admin(UID):
    return UID in permsList


def joinCommunity(comId: str = None, inv: str = None):
    with suppress(Exception):
        client.join_community(comId=comId, invitationId=inv)
        return 1

    if inv:
        with suppress(Exception):
            client.request_join_community(comId=comId, message='Cookie for everyone!!')
            return 2


def joinamino(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    invit = None

    if tailleCommu >= 20 and not (is_it_me(authorId) or is_it_admin(authorId)):
        subClient.send_message(chatId, "The bot has joined too many communities!")
        return

    staff = subClient.get_staff(message)

    if not staff:
        subClient.send_message(chatId, "Wrong amino ID!")
        return

    if authorId not in staff and not is_it_me(authorId):
        subClient.send_message(chatId, "You need to be in the community's staff!")
        return

    try:
        test = message.strip().split(" ")
        aminoC = test[0]
        invit = test[1]
        invit = invit.replace("http://aminoapps.com/invite/", "")
    except Exception:
        aminoC = message
        invit = None

    try:
        val = subClient.client.get_from_code("https://aminoapps.com/c/"+aminoC)
        comId = val.json["extensions"]["community"]["ndcId"]
    except Exception:
        val = ""

    if val:
        isJoined = val.json["extensions"]["isCurrentUserJoined"]
        if not isJoined:
            joinCommunity(comId, invit)
            val = client.get_from_code("http://aminoapps.com/c/"+aminoC)
            isJoined = val.json["extensions"]["isCurrentUserJoined"]
            if isJoined:
                communaute[comId] = BotAmino(client=client, community=message)
                communaute[comId].run()
                subClient.send_message(chatId, "Joined!")
                return
        else:
            subClient.send_message(chatId, "Allready joined!")
            return
    subClient.send_message(chatId, "Waiting for join!")


def title(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(bot_id):
        color = None
        try:
            elem = message.strip().split("color=")
            message, color = elem[0], elem[1].strip()
            if not color.startswith("#"):
                color = "#"+color
            val = subClient.add_title(authorId, message, color)
        except Exception:
            val = subClient.add_title(authorId, message)

        if val:
            subClient.send_message(chatId, f"The titles of {author} has changed")
        else:
            subClient.send_message(chatId, subClient.get_message_level(subClient.lvlmin))


def cookie(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.send_message(chatId, f"Here is a cookie for {author} 🍪")


def ramen(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.send_message(chatId, f"Here are some ramen for {author} 🍜")


def dice(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if not message:
        cpt = randint(1, 20)
        subClient.send_message(chatId, f"🎲 -{cpt},(1-20)- 🎲")
        return

    with suppress(Exception):
        pt = message.split('d')
        val = ''
        cpt = 0
        for _ in range(int(pt[0])):
            ppt = randint(1, int(pt[1]))
            cpt += ppt
            val += str(ppt)+" "
        print(f'🎲 -{cpt},[ {val}](1-{pt[1]})- 🎲')
        subClient.send_message(chatId, f'🎲 -{cpt},[ {val}](1-{pt[1]})- 🎲')


def join(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.join_chat(message, chatId)
    if val or val == "":
        subClient.send_message(chatId, f"Chat {val} joined".strip())
    else:
        subClient.send_message(chatId, "No chat joined")


def joinall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId):
        if subClient.join_all_chat():
            subClient.send_message(chatId, "All chat joined")


def leaveall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.send_message(chatId, "Leaving all chat...")
        subClient.leave_all_chats()


def leave(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if message and (is_it_me(authorId) or is_it_admin(authorId)):
        chatIde = subClient.get_chat_id(message)
        if chatIde:
            chatId = chatIde
    subClient.leave_chat(chatId)


def clear(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if (subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId)) and subClient.is_in_staff(bot_id):
        size = 1
        msg = ""
        val = ""
        subClient.delete_message(chatId, messageId, asStaff=True)
        if "chat=" in message and is_it_me(authorId):
            chatName = message.rsplit("chat=", 1).pop()
            chatIde = subClient.get_chat_id(chatName)
            if chatIde:
                chatId = chatIde
            message = " ".join(message.strip().split(" ")[:-1])

        with suppress(Exception):
            size = int(message.strip().split(' ').pop())
            msg = ' '.join(message.strip().split(' ')[:-1])

        if size > 50 and not is_it_me(authorId):
            size = 50

        if msg:
            try:
                val = subClient.get_user_id(msg)
            except Exception:
                val = ""

        messages = subClient.subclient.get_chat_messages(chatId=chatId, size=size)

        for message, authorId in zip(messages.messageId, messages.author.userId):
            if not val:
                subClient.delete_message(chatId, message, asStaff=True)
                continue
            elif authorId == val[1]:
                subClient.delete_message(chatId, message, asStaff=True)


def spam(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    try:
        size = int(message.strip().split(" ").pop())
        msg = " ".join(message.strip().split(" ")[:-1])
    except ValueError:
        size = 1
        msg = message

    if size > 10 and not (is_it_me(authorId) or is_it_admin(authorId)):
        size = 10

    for i in range(size):
        with suppress(Exception):
            subClient.send_message(chatId, msg)


def mention(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if "chat=" in message and is_it_me(authorId):
        chatName = message.rsplit("chat=", 1).pop()
        chatIde = subClient.get_chat_id(chatName)
        if chatIde:
            chatId = chatIde
        message = " ".join(message.strip().split(" ")[:-1])
    try:
        size = int(message.strip().split(" ").pop())
        message = " ".join(message.strip().split(" ")[:-1])
    except ValueError:
        size = 1

    val = subClient.get_user_id(message)

    if not val:
        subClient.send_message(chatId=chatId, message="Username not found")
        return

    if size > 5 and not (is_it_me(authorId) or is_it_admin(authorId)):
        size = 5

    if val:
        for i in range(size):
            with suppress(Exception):
                subClient.send_message(chatId=chatId, message=f"‎‏‎‏@{val[0]}‬‭", mentionUserIds=[val[1]])


def mentionall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if message and is_it_me(authorId):
            chatIde = subClient.get_chat_id(message)
            if chatIde:
                chatId = chatIde
            message = " ".join(message.strip().split(" ")[:-1])

        try:
            size = int(message.strip().split(" ").pop())
            message = " ".join(message.strip().split(" ")[:-1])
        except ValueError:
            size = 1

        if size > 5 and not (is_it_me(authorId) or is_it_admin(authorId)):
            size = 5

        mention = [userId for userId in subClient.subclient.get_chat_users(chatId=chatId).userId]
        test = "".join(["‎‏‎‏‬‭" for user in subClient.subclient.get_chat_users(chatId=chatId).userId])

        for i in range(size):
            with suppress(Exception):
                subClient.send_message(chatId=chatId, message=f"@everyone{test}", mentionUserIds=mention)


def msg(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    value = 0
    size = 1
    ment = None
    with suppress(Exception):
        subClient.delete_message(chatId, messageId, asStaff=True)

    if "chat=" in message and is_it_me(authorId):
        chatName = message.rsplit("chat=", 1).pop()
        chatIde = subClient.get_chat_id(chatName)
        if chatIde:
            chatId = chatIde
        message = " ".join(message.strip().split(" ")[:-1])

    try:
        size = int(message.split(" ").pop())
        message = " ".join(message.strip().split(" ")[:-1])
    except ValueError:
        size = 0

    try:
        value = int(message.split(" ").pop())
        message = " ".join(message.strip().split(" ")[:-1])
    except ValueError:
        value = size
        size = 1

    if not message and value == 1:
        message = f"‎‏‎‏@{author}‬‭"
        ment = authorId

    if size > 10 and not (is_it_me(authorId) or is_it_admin(authorId)):
        size = 10

    for i in range(size):
        with suppress(Exception):
            subClient.send_message(chatId=chatId, message=f"{message}", messageType=value, mentionUserIds=ment)


def abw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message or message in subClient.bannedWords:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.add_banned_words(message)
        subClient.send_message(chatId, "Banned word list updated")


def rbw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.remove_banned_words(message)
        subClient.send_message(chatId, "Banned word list updated")


def bwl(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = ""
    if subClient.bannedWords:
        for elem in subClient.bannedWords:
            val += elem+"\n"
    else:
        val = "No words in the list"
    subClient.send_message(chatId, val)


def sw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.set_welcome_message(message)
        subClient.send_message(chatId, "Welcome message changed")


def get_chats(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.get_chats()
    for elem, t in zip(val.title, val.chatId):
        subClient.send_message(chatId, elem)


def chatid(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.get_chats()
        for elem, t in zip(val.title, val.chatId):
            if message.lower() in elem.lower():
                subClient.send_message(chatId, f"{elem} | {t}")


def leaveAmino(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.send_message(chatId, "Leaving the amino!")
        subClient.leave_community()
    del communaute[subClient.communityId]


def prank(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        with suppress(Exception):
            subClient.delete_message(chatId, messageId, asStaff=True)

        transactionId = "5b3964da-a83d-c4d0-daf3-6e259d10fbc3"
        oldChat = None
        if message and is_it_me(authorId):
            chatIde = subClient.get_chat_id(message)
            if chatIde:
                oldChat = chatId
                chatId = chatIde
        for _ in range(10):
            subClient.subclient.send_coins(coins=500, chatId=chatId, transactionId=transactionId)

        if oldChat:
            chatId = oldChat
        subClient.send_message(chatId, "Done")


def image(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    os.chdir(depart)
    val = os.listdir("pictures")
    if val:
        file = choice(val)
        with suppress(Exception):
            with open(path_picture+file,  'rb') as fp:
                subClient.send_message(chatId, file=fp, fileType="image")
        return
    subClient.send_message(chatId, "Error! No file")


def audio(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    os.chdir(depart)
    val = os.listdir("sound")
    if val:
        file = choice(val)
        with suppress(Exception):
            with open(path_sound+file,  'rb') as fp:
                subClient.send_message(chatId, file=fp, fileType="audio")
        return
    subClient.send_message(chatId, "Error! No file")


def telecharger(url):
    if ("=" in url and "/" in url and " " not in url) or ("/" in url and " " not in url):

        if "=" in url and "/" in url:
            ide = url.rsplit("=", 1)
            ide = ide[-1]
            music = ide
        elif "/" in url:
            ide = url.rsplit("/")
            ide = ide[-1]
            music = ide

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
            'outtmpl': path_download+music+".webm",
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
        nombreLigne = len(fichier.readlines())

    if temps < 180:
        return False

    elif temps > 540:
        return False

    decoupage = int((size*nombreLigne)/temps)

    t = 0
    fileList = []
    for a in range(0, nombreLigne, decoupage):
        b = a + decoupage
        if b >= nombreLigne:
            b = nombreLigne

        with open(musical, "rb") as fichier:
            lignes = fichier.readlines()[a:b]

        with open(musical.replace(".mp3", "PART"+str(t)+".mp3"),  "wb") as mus:
            for ligne in lignes:
                mus.write(ligne)

        fileList.append(musical.replace(".mp3", "PART"+str(t)+".mp3"))
        t += 1
    return fileList


def convert(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    os.chdir(depart)
    music, size = telecharger(message)
    if music:
        music = path_download+music
        val = decoupe(music, size)

        if not val:
            try:
                with open(music,  'rb') as fp:
                    subClient.send_message(chatId, file=fp, fileType="audio")
            except Exception:
                subClient.send_message(chatId, "Error! File too heavy (9 min max)")
            os.remove(music)
            return
        os.remove(music)
        for elem in val:
            with suppress(Exception):
                with open(elem,  'rb') as fp:
                    subClient.send_message(chatId, file=fp, fileType="audio")
            os.remove(elem)
        return
    subClient.send_message(chatId, "Error! Wrong link")


def helper(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if not message:
        subClient.send_message(chatId, helpMsg)
    elif message == "msg":
        subClient.send_message(chatId, helpMessage)
    elif message == "ask":
        subClient.send_message(chatId, helpAsk)
    else:
        subClient.send_message(chatId, "No help is available for this command")


def reboot(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.send_message(chatId, "Restarting Bot")
        os.execv(sys.executable, ["None", __file__])
        quit()


def stop(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.send_message(chatId, "Stopping Bot")
        os.execv(sys.executable, ["None", "None"])
        sys.exit(1)


def uinfo(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = ""
        val2 = ""
        UID = ""
        with suppress(Exception):
            val = subClient.client.get_user_info(message)

        with suppress(Exception):
            val2 = subClient.subclient.get_user_info(message)

        if not val:
            UID = subClient.get_user_id(message)
            if UID:
                val = subClient.client.get_user_info(UID[1])
                val2 = subClient.subclient.get_user_info(UID[1])
            print(val, val2)

        if not val:
            with suppress(Exception):
                lin = subClient.client.get_from_code("http://aminoapps.com/u/"+message).json["extensions"]["linkInfo"]["objectId"]
                val = subClient.client.get_user_info(lin)

            with suppress(Exception):
                val2 = subClient.subclient.get_user_info(lin)

        with suppress(Exception):
            with open("elJson.json", "w") as fic:
                fic.write(dumps(val.json, sort_keys=False, indent=4))

        with suppress(Exception):
            with open("elJson2.json", "w") as fic:
                fic.write(dumps(val2.json, sort_keys=False, indent=4))

        if os.path.getsize("elJson.json"):
            os.system("txt2pdf elJson.json --output result.pdf")
            pages = convert_from_path('result.pdf', 150)
            i = 1
            for page in pages:
                file = 'result'+str(i)+'.jpg'
                page.save(file,  'JPEG')
                with open(file,  'rb') as fp:
                    subClient.send_message(chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if os.path.getsize("elJson2.json"):
            os.system("txt2pdf elJson2.json --output result.pdf")
            pages = convert_from_path('result.pdf', 150)
            i = 1
            for page in pages:
                file = 'result'+str(i)+'.jpg'
                page.save(file,  'JPEG')
                with open(file,  'rb') as fp:
                    subClient.send_message(chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize("elJson.json") and not os.path.getsize("elJson.json"):
            subClient.send_message(chatId, "Error!")


def cinfo(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = ""

        with suppress(Exception):
            val = subClient.client.get_from_code("https://aminoapps.com/c/"+message)

        with suppress(Exception):
            with open("elJson.json", "w") as fic:
                fic.write(dumps(val.json, sort_keys=False, indent=4))

        if os.path.getsize("elJson.json"):
            os.system("txt2pdf elJson.json --output result.pdf")
            pages = convert_from_path('result.pdf', 150)
            i = 1
            for page in pages:
                file = 'result'+str(i)+'.jpg'
                page.save(file,  'JPEG')
                with open(file,  'rb') as fp:
                    subClient.send_message(chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize("elJson.json"):
            subClient.send_message(chatId, "Error!")
            return


def sendinfo(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if (is_it_admin(authorId) or is_it_me(authorId)) and message != "":
        arg = message.strip().split()

        for file_ in ('elJson.json', 'elJson2.json'):
            if Path(file_).exists():
                with open(file_, 'r') as file_:
                    val = load(file_)
                try:
                    memoire = val[arg.pop(0)]
                except Exception:
                    subClient.send_message(chatId, 'Wrong key!')
                    return
                if arg:
                    for elem in arg:
                        try:
                            memoire = memoire[elem]
                        except Exception:
                            subClient.send_message(chatId, 'Wrong key 1!')
                        else:
                            subClient.send_message(chatId, memoire)


def getglobal(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.get_user_id(message)[1]
    if val:
        ide = subClient.client.get_user_info(val).aminoId
        subClient.send_message(chatId, "http://aminoapps.com/u/"+ide)
        return
    subClient.send_message(chatId, "Error!")


def follow(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.follow_user(authorId)
    subClient.send_message(chatId, "Now following you!")


def unfollow(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.unfollow_user(authorId)
    subClient.send_message(chatId, "Unfollow!")


def stopamino(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.stop_instance()
        del communaute[subClient.communityId]


def block(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.get_user_id(message)
        if val:
            subClient.client.block(val[1])
            subClient.send_message(chatId, f"User {val[0]} blocked!")


def unblock(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.client.get_blocked_users()
        for aminoId, userId in zip(val.aminoId, val.userId):
            if message in aminoId:
                subClient.client.unblock(userId)
                subClient.send_message(chatId, f"User {aminoId} unblocked!")


def accept(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.subclient.get_notices(start=0, size=25)
        ans = None
        res = None
        with suppress(Exception):
            subClient.subclient.accept_host(chatId)
            subClient.send_message(chatId, "Accepted!")
            return

        for elem in val:
            if 'become' in elem['title'] or "host" in elem['title']:
                res = elem['noticeId']
        if res:
            ans = subClient.accept_role(res)
        if ans:
            subClient.send_message(chatId, "Accepted!")
        else:
            subClient.send_message(chatId, "Error!")


def askthing(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        lvl = ""
        if "lvl=" in message:
            lvl = message.rsplit("lvl=", 1)[1].strip().split(" ", 1)[0]
            message = message.replace("lvl="+lvl, "").strip()
        try:
            lvl = int(lvl)
        except ValueError:
            lvl = 20

        subClient.ask_all_members(message, lvl)
        subClient.send_message(chatId, "Asking...")


def askstaff(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        aminoList = client.sub_clients()
        for commu in aminoList.comId:
            communaute[commu].ask_amino_staff(message=message)
        subClient.send_message(chatId, "Asking...")

def lock_command(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message or message in subClient.lockedCommand:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.add_locked_command(message)
        subClient.send_message(chatId, "Locked command list updated")

def remove_lock(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.remove_locked_command(message)
        subClient.send_message(chatId, "Locked command list updated")


commandDico = {"help": helper, "title": title, "dice": dice, "join": join, "ramen": ramen,
               "cookie": cookie, "leave": leave, "abw": abw, "rbw": rbw, "bwl": bwl,
               "clear": clear, "joinall": joinall, "leaveall": leaveall, "reboot": reboot,
               "stop": stop, "spam": spam, "mention": mention, "msg": msg,
               "uinfo": uinfo, "cinfo": cinfo, "joinamino": joinamino, "get_chats": get_chats, "sw": sw,
               "accept": accept, "chatid": chatid, "prank": prank,
               "leaveamino": leaveAmino, "sendinfo": sendinfo, "image": image, "all": mentionall,
               "block": block, "unblock": unblock, "follow": follow, "unfollow": unfollow,
               "stopamino": stopamino, "block": block, "unblock": unblock,
               "ask": askthing, "askstaff": askstaff, "lock": lock_command, "rlock": remove_lock,
               "global": getglobal, "audio": audio, "convert": convert}


helpMsg = """
[C]--- COMMON COMMAND ---
- help (command)\t:  show this or the help associated to the command
- title (title)\t:  edit titles*
- dice (xdy)\t:  return x dice y (1d20) per default
- join (chat)\t:  join the specified channel
- mention (user)\t: mention an user
- spam (amount)\t: spam an message (limited to 10)
- msg (type)\t: send a "special" message (limited to 10)
- bwl\t:  the list of banneds words*
- get_chats\t: the list of public chats
- global (user)\t: give the global profile of the user
- leave\t:  leave the current channel
- follow\t: follow you
- unfollow\t: unfollow you
- convert (url)\t: will convert and send the music from the url (9 min max)
- audio\t: will send audio
- image\t: will send an image
- ramen\t:  give ramens!
- cookie\t:  give a cookie!

[C]--- STAFF COMMAND ---
- accept\t: accept the staff role
- abw (word list)\t:  add a banned word to the list*
- rbw (word list)\t:  remove a banned word from the list*
- sw (message)\t:  set the welcome message for new members (will start as soon as the welcome message is set)
- ask (message)(lvl=)\t: ask to all level (lvl) and inferior something
- clear (amount)\t:  clear the specified amount of message from the chat (max 50)*
- joinall\t:  join all public channels
- leaveall\t:  leave all public channels
- leaveamino\t: leave the community
- all\t: mention all the users of a channel
- lock (command)\t: lock the command (nobody can use it)
- rlock (command)\t: remove the lock for the command

[C]--- SPECIAL ---
- joinamino (amino id): join the amino (you need to be in the amino's staff)**
- uinfo (user): will give informations about the user²
- cinfo (aminoId): will give informations about the community²
- sendinfo (args): send the info from uinfo or cinfo

*(only work if bot is in staff)
**(In developpement)
²(only for devlopper or bot owner)

-- all commands are available for the owner of the bot --
-- Bot made by The_Phoenix --
-- Thanks to Yu for supporting me^^ --
"""

helpMessage = """
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
    with open("admin.json", "r") as fic:
        permsList = load(fic)
except FileNotFoundError:
    with open('admin.json', 'w') as fic:
        fic.write('[\n\t"YOUR AMINOID HERE"\n]')
    print("You should put your Amino Id in the file admin.json")
    permsList = []

try:
    with open("lock.json", "r") as fic:
        commandLock = load(fic)
except FileNotFoundError:
    with open('lock.json', 'w') as fic:
        fic.write('[\n\t"COMMAND HERE"\n]')
    print("You should put the commands you don't want to use in the file lock.json")
    commandLock = []

try:
    with open("client.txt", "r") as fic:
        login = fic.readlines()
except FileNotFoundError:
    with open('client.txt', 'w') as fic:
        fic.write('email\npassword')
    print("Please enter your email and password in the file client.txt")
    print("-----end-----")
    sys.exit(1)

identifiant = login[0].strip()
mdp = login[1].strip()

client = Client()
client.login(email=identifiant, password=mdp)
bot_id = client.userId
aminoList = client.sub_clients()

communaute = {}
tailleCommu = 0

for command in commandLock:
    if command in commandDico.keys():
        del commandDico[command]


def tradlist(sub):
    sublist = []
    for elem in sub:
        with suppress(Exception):
            val = client.get_from_code("https://aminoapps.com/u/"+elem).objectId
            sublist.append(val)
            continue
        with suppress(Exception):
            val = client.get_user_info(elem).userId
            sublist.append(val)
            continue
    return sublist


permsList = tradlist(permsList)


def threadLaunch(commu):
    try:
        commi = BotAmino(client=client, community=commu)
        communaute[commi.communityId] = commi
        communaute[commi.communityId].run()
    except Exception:
        pass
        # client.leave_community(commu)


for commu in aminoList.comId:
    th = Thread(target=threadLaunch, args=[commu])
    th.start()
    tailleCommu += 1

th.join()


@client.callbacks.event("on_text_message")
def on_text_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except Exception:
        return

    message = data.message.content
    chatId = data.message.chatId
    authorId = data.message.author.userId
    messageId = data.message.messageId
    print(f"{data.message.author.nickname}:{message}")

    if not is_it_bot(authorId) and not subClient.is_in_staff(authorId):
        with suppress(Exception):
            para = normalize('NFD', message).encode('ascii', 'ignore').decode("utf8").strip().lower()
            para = para.translate(str.maketrans("", "", punctuation))
            para = para.split(" ")
            if para == [""]:
                pass
            else:
                for elem in para:
                    if elem in subClient.bannedWords:
                        subClient.delete_message(chatId, data.message.messageId, "Banned word", asStaff=True)
                        return

    if message.startswith(subClient.prefixeId) and not is_it_bot(authorId) and not [True for command in subClient.lockedCommand if command.lower() in commandDico.keys()]:
        author = data.message.author.nickname
        commande = ""
        message = str(message).strip().split(communaute[commuId].prefixeId, 1).pop()
        commande = str(message).strip().split(" ", 1)[0].lower()
        try:
            message = str(message).strip().split(" ", 1)[1]
        except Exception:
            message = ""
    else:
        return

    [Thread(target=values, args=[subClient, chatId, authorId, author, message, messageId]).start() for key, values in commandDico.items() if commande == key.lower()]


print("Ready")
