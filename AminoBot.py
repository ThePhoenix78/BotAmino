#  coding: utf-8
import amino
import json
import random
import os
import sys
import unicodedata
import time
import string
import threading
import youtube_dl
from pdf2image import convert_from_path
from pathlib import Path
from contextlib import suppress

# Big optimisation thanks to SempreLEGIT#1378 ♥

programmer = os.path.basename(sys.argv[0])

platform = sys.platform
slash = "\\"

if platform == "win32":
    slash = "\\"
else:
    slash = "/"

pathWelcome = f"utilities{slash}welcomeMessage{slash}"
pathBannedWords = f"utilities{slash}bannedWords{slash}"
pict = f"pictures{slash}"
sounder = f"sound{slash}"
downloader = f"download{slash}"


depart = os.getcwd()
marche = True

for i in ('utilities', 'pictures', 'download', 'sound', 'utilities/welcomeMessage', 'utilities/bannedWords'):
    Path(i).mkdir(exist_ok=True)


class BotAmino:
    def __init__(self, client, community, inv: str = None):
        self.client = client
        self.prefixeId = "!"
        self.lvlmin = 0
        self.marche = True

        if type(community) == type(2):
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
        except:
            self.communityLeaderAgentId = "-"

        try:
            self.communityStaffList = self.community.json["communityHeadList"]
        except:
            self.communityStaffList = ""

        if self.communityStaffList:
            self.communityLeaders = [elem["uid"] for elem in self.communityStaffList if elem["role"] in (100, 102)]
            self.communityCurators = [elem["uid"] for elem in self.communityStaffList if elem["role"] == 101]
            self.communityStaff = [elem["uid"] for elem in self.communityStaffList]

        try:
            fic = open(f"{pathWelcome}{self.communityAminoId}.txt", "r", encoding="utf8")
            fic.close()
        except FileNotFoundError:
            self.createFiles()

        self.subclient = amino.SubClient(comId=self.communityId, profile=client.profile)
        self.bannedWords = self.bannedWordsList()
        self.messageBvn = self.welcomeMessage()
        self.subclient.activity_status("on")
        userList = self.subclient.get_all_users(start=0, size=25, type="recent")
        self.allUsers = userList.json['userProfileCount']
        self.allNewUsersCommunityId = [elem["uid"] for elem in userList.json["userProfileList"]]

    def createFiles(self):
        os.chdir(depart)
        fic = open(f"{pathWelcome}{self.communityAminoId}.txt", "w", encoding="utf8")
        fic.close()
        fic = open(f"{pathBannedWords}{self.communityAminoId}.json", "w", encoding="utf8")
        fic.write("[]")
        fic.close()

    def is_in_staff(self, UID):
        return UID in self.communityStaff

    def is_leader(self, UID):
        return UID in self.communityLeaders

    def is_curator(self, UID):
        return UID in self.communityCurators

    def is_agent(self, UID):
        return UID == self.communityLeaderAgentId

    def acceptRole(self, RID: str):
        try:
            self.subclient.promotion(noticeId=RID)
            return True
        except:
            return False

    def getStaff(self, community):
        if type(community) == type(10):
            try:
                community = self.client.get_community_info(comId=community)
            except:
                pass
        else:
            try:
                informations = self.client.get_from_code("https://aminoapps.com/c/"+community)
            except:
                return False
            communityId = informations.json["extensions"]["community"]["ndcId"]
            community = self.client.get_community_info(comId=communityId)

        try:
            communityStaffList = community.json["communityHeadList"]
        except:
            communityStaffList = ""

        if communityStaffList:
            communityStaff = [elem["uid"] for elem in communityStaffList]

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

    def askAllMembers(self, message, lvl: int):
        size = self.allUsers
        st = 0
        users = self.subclient.get_all_users(type="recent", start=st, size=100)

        while size > 100:
            userLvlList = []
            userLvlList = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
            self.subclient.start_chat(userId=userLvlList, message=message)
            size -= 100
            st += 100

        userLvlList = []
        users = self.subclient.get_all_users(type="recent", start=0, size=size)
        userLvlList = [user['uid'] for user in users.json['userProfileList'] if user['level'] <= lvl]
        self.subclient.start_chat(userId=userLvlList, message=message)

    def askAminoStaff(self, message):
        self.subclient.start_chat(userId=self.communityStaff, message=message)

    def getChatId(self, chat: str = None):
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

    def prefixe(self, prefixe: str):
        self.prefixeId = prefixe

    def stopInstance(self):
        self.marche = False

    def setWelcomeMessage(self, message: str):
        with open(f"{pathWelcome}{self.communityAminoId}.txt", "w", encoding="utf8") as fic:
            fic.write(message)
        self.messageBvn = message

    def welcomeMessage(self):
        with open(f"{pathWelcome}{self.communityAminoId}.txt", "r", encoding="utf8") as fic:
            return fic.read()

    def bannedWordsList(self):
        with open(f"{pathBannedWords}{self.communityAminoId}.json", "r", encoding="utf8") as fic:
            message = json.load(fic)
        message = [elem.lower() for elem in message]
        return message

    def addBannedWords(self, liste: list):
        self.bannedWords.extend(liste)
        with open(f"{pathBannedWords}{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(json.dumps(self.bannedWords, sort_keys=False, indent=4))

    def removeBannedWord(self, liste: list):
        os.chdir(depart)
        for elem in liste:
            if elem in self.bannedWords:
                self.bannedWords.remove(elem)
        with open(f"{pathBannedWords}{self.communityAminoId}.json", "w", encoding="utf8") as fic:
            fic.write(json.dumps(self.bannedWords, sort_keys=False, indent=4))

    def leaveCommunity(self):
        self.client.leave_community(comId=self.communityId)
        self.marche = False
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def checkNewMember(self):
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

    def getMemberLevel(self, UID):
        return self.subclient.get_user_info(userId=UID).level

    def isLevelGood(self, UID):
        return self.subclient.get_user_info(userId=UID).level > self.lvlmin

    def getMemberTitles(self, UID):
        try:
            return self.subclient.get_user_info(userId=UID).customTitles
        except Exception:
            return False

    def getMember(self, UID):
        return self.subclient.get_user_info(userId=UID)

    def setMessageLevel(self, level: int):
        return f"You need the level {level} to do this command"

    def deleteMessage(self, chatId: str, messageId: str, reason: str = "Clear", asStaff: bool = False):
        self.subclient.delete_message(chatId, messageId, asStaff, reason)

    def sendMessage(self, chatId: str = None, message: str = "None", messageType: str = None, file: str = None, fileType: str = None, replyTo: str = None, mentionUserIds: str = None):
        self.subclient.send_message(chatId=chatId, message=message, file=file, fileType=fileType, replyTo=replyTo, messageType=messageType, mentionUserIds=mentionUserIds)

    def joinChat(self, chat: str, chatId: str = None):
        chat = chat.replace("http:aminoapps.com/p/", "")
        if not chat:
            with suppress(Exception):
                self.subclient.join_chat(chatId)
                return ""

            with suppress(Exception):
                chati = self.subclient.get_from_code(chat).objectId
                self.subclient.join_chat(chati)
                return chat

        val = self.subclient.get_public_chat_threads()
        for elem, t in zip(val.title, val.chatId):
            if chat == elem:
                self.subclient.join_chat(t)
                return elem

        val = self.subclient.get_public_chat_threads()
        for elem, t in zip(val.title, val.chatId):
            if chat.lower() in elem.lower() or chat == t:
                self.subclient.join_chat(t)
                return elem

        return False

    def chatList(self):
        return self.subclient.get_public_chat_threads()

    def joinAllChat(self):
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.join_chat(elem)

    def leaveChat(self, chat: str):
        self.subclient.leave_chat(chat)

    def leaveAllChat(self):
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            with suppress(Exception):
                self.subclient.leave_chat(elem)

    def followUser(self, UID):
        self.subclient.follow(userId=[UID])

    def unFollowUser(self, UID):
        self.subclient.unfollow(userId=UID)

    def addTitle(self, UID, title: str, color: str = "#999999"):
        member = self.getMemberTitles(UID)
        tlist = []
        clist = []
        try:
            tlist = [elem["title"] for elem in member]
            clist = [elem["color"] for elem in member]
        except:
            pass

        tlist.append(title)
        clist.append(color)

        with suppress(Exception):
            self.subclient.edit_titles(UID, tlist, clist)

        return True

    def removeTitle(self, UID, title: str):
        member = self.getMemberTitles(UID)
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
        while marche and self.marche:
            if i >= 60:
                if self.messageBvn:
                    self.checkNewMember()
                with suppress(Exception):
                    self.subclient.activity_status('on')
                self.subclient.edit_profile(content=activities[o])
                i = 0
                o += 1
                if o > len(activities)-1:
                    o = 0
            i += 1
            time.sleep(1)

    def run(self):
        th2 = threading.Thread(target=self.passive)
        th2.start()


def is_it_bot(UID):
    return UID == botId


def is_it_me(UID):
    return UID in ["userId"]


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
        subClient.sendMessage(chatId, "The bot has joined too many communities!")
        return

    staff = subClient.getStaff(message)

    if not staff:
        subClient.sendMessage(chatId, "Wrong amino ID!")
        return

    if authorId not in staff and not is_it_me(authorId):
        subClient.sendMessage(chatId, "You need to be in the community's staff!")
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
                subClient.sendMessage(chatId, "Joined!")
                return
        else:
            subClient.sendMessage(chatId, "Allready joined!")
            return
    subClient.sendMessage(chatId, "Waiting for join!")


def title(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(botId):
        color = None
        try:
            elem = message.strip().split("color=")
            message, color = elem[0], elem[1].strip()
            if not color.startswith("#"):
                color = "#"+color
            val = subClient.addTitle(authorId, message, color)
        except Exception:
            val = subClient.addTitle(authorId, message)

        if val:
            subClient.sendMessage(chatId, f"The titles of {author} has changed")
        else:
            subClient.sendMessage(chatId, subClient.setMessageLevel(subClient.lvlmin))


def cookie(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.sendMessage(chatId, f"Here is a cookie for {author} 🍪")


def ramen(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.sendMessage(chatId, f"Here are some ramen for {author} 🍜")


def dice(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if not message:
        cpt = random.randint(1, 20)
        subClient.sendMessage(chatId, f"🎲 -{cpt},(1-20)- 🎲")
    with suppress(Exception):
        pt = message.split('d')
        val = ''
        cpt = 0
        for _ in range(int(pt[0])):
            cpt += pt
            val += str(random.randint(1, int(pt[1]))) + ' '

        subClient.sendMessage(chatId, f'🎲 -{cpt},[ {val}](1-{pt[1]})- 🎲')


def join(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.joinChat(message, chatId)
    if val or val == "":
        subClient.sendMessage(chatId, f"Chat {val} joined".strip())
    else:
        subClient.sendMessage(chatId, "No chat joined")


def joinall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId):
        if subClient.joinAllChat():
            subClient.sendMessage(chatId, "All chat joined")


def leaveall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.sendMessage(chatId, "Leaving all chat...")
        subClient.leaveAllChat()


def leave(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if message and (is_it_me(authorId) or is_it_admin(authorId)):
        chatIde = subClient.getChatId(message)
        if chatIde:
            chatId = chatIde
    subClient.leaveChat(chatId)


def clear(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if (subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId)) and subClient.is_in_staff(botId):
        size = 1
        msg = ""
        val = ""
        subClient.deleteMessage(chatId, messageId, asStaff=True)
        if "chat=" in message and is_it_me(authorId):
            chatName = message.rsplit("chat=", 1).pop()
            chatIde = subClient.getChatId(chatName)
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
                subClient.deleteMessage(chatId, message, asStaff=True)
                continue
            elif authorId == val[1]:
                subClient.deleteMessage(chatId, message, asStaff=True)


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
            subClient.sendMessage(chatId, msg)


def mention(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if "chat=" in message and is_it_me(authorId):
        chatName = message.rsplit("chat=", 1).pop()
        chatIde = subClient.getChatId(chatName)
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
        subClient.sendMessage(chatId=chatId, message="Username not found")
        return

    if size > 5 and not (is_it_me(authorId) or is_it_admin(authorId)):
        size = 5

    if val:
        for i in range(size):
            with suppress(Exception):
                subClient.sendMessage(chatId=chatId, message=f"‎‏‎‏@{val[0]}‬‭", mentionUserIds=[val[1]])


def mentionall(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if message and is_it_me(authorId):
            chatIde = subClient.getChatId(message)
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
                subClient.sendMessage(chatId=chatId, message=f"@everyone{test}", mentionUserIds=mention)


def msg(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    value = 0
    size = 1
    ment = None
    with suppress(Exception):
        subClient.deleteMessage(chatId, messageId, asStaff=True)

    if "chat=" in message and is_it_me(authorId):
        chatName = message.rsplit("chat=", 1).pop()
        chatIde = subClient.getChatId(chatName)
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
            subClient.sendMessage(chatId=chatId, message=f"{message}", messageType=value, mentionUserIds=ment)


def abw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message or message in subClient.bannedWords:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.addBannedWords(message)
        subClient.sendMessage(chatId, "Banned word list updated")


def rbw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        if not message:
            return
        try:
            message = message.lower().strip().split()
        except Exception:
            message = [message.lower().strip()]
        subClient.removeBannedWord(message)
        subClient.sendMessage(chatId, "Banned word list updated")


def bwl(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = ""
    if subClient.bannedWords:
        for elem in subClient.bannedWords:
            val += elem+"\n"
    else:
        val = "No words in the list"
    subClient.sendMessage(chatId, val)


def sw(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.setWelcomeMessage(message)
        subClient.sendMessage(chatId, "Welcome message changed")


def chatList(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.chatList()
    for elem, t in zip(val.title, val.chatId):
        subClient.sendMessage(chatId, elem)


def chatid(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.chatList()
        for elem, t in zip(val.title, val.chatId):
            if message.lower() in elem.lower():
                subClient.sendMessage(chatId, f"{elem} | {t}")


def leaveAmino(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        subClient.sendMessage(chatId, "Leaving the amino!")
        subClient.leaveCommunity()
    del communaute[subClient.communityId]


def prank(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        with suppress(Exception):
            subClient.deleteMessage(chatId, messageId, asStaff=True)

        transactionId = "5b3964da-a83d-c4d0-daf3-6e259d10fbc3"
        oldChat = None
        if message and is_it_me(authorId):
            chatIde = subClient.getChatId(message)
            if chatIde:
                oldChat = chatId
                chatId = chatIde
        for _ in range(10):
            subClient.subclient.send_coins(coins=500, chatId=chatId, transactionId=transactionId)

        if oldChat:
            chatId = oldChat
        subClient.sendMessage(chatId, "Done")


def image(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    os.chdir(depart)
    val = os.listdir("pictures")
    if val:
        file = random.choice(val)
        with suppress(Exception):
            with open(pict+file,  'rb') as fp:
                subClient.sendMessage(chatId, file=fp, fileType="image")
        return
    subClient.sendMessage(chatId, "Error! No file")


def audio(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    os.chdir(depart)
    val = os.listdir("sound")
    if val:
        file = random.choice(val)
        with suppress(Exception):
            with open(sounder+file,  'rb') as fp:
                subClient.sendMessage(chatId, file=fp, fileType="audio")
        return
    subClient.sendMessage(chatId, "Error! No file")


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

        if music in os.listdir(sounder):
            return music

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            'extract-audio': True,
            'outtmpl': downloader+music+".webm",
            }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
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
        music = downloader+music
        val = decoupe(music, size)

        if not val:
            try:
                with open(music,  'rb') as fp:
                    subClient.sendMessage(chatId, file=fp, fileType="audio")
            except Exception:
                subClient.sendMessage(chatId, "Error! File too heavy (9 min max)")
            os.remove(music)
            return
        os.remove(music)
        for elem in val:
            with suppress(Exception):
                with open(elem,  'rb') as fp:
                    subClient.sendMessage(chatId, file=fp, fileType="audio")
            os.remove(elem)
        return
    subClient.sendMessage(chatId, "Error! Wrong link")


def helper(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if not message:
        subClient.sendMessage(chatId, helpMsg)
    elif message == "msg":
        subClient.sendMessage(chatId, helpMessage)
    elif message == "ask":
        subClient.sendMessage(chatId, helpAsk)
    else:
        subClient.sendMessage(chatId, "No help is available for this command")

def reboot(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    global marche
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.sendMessage(chatId, "Restarting Bot")
        os.execv(sys.executable, ["None", programmer])
        marche = False
        quit()


def stop(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    global marche
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.sendMessage(chatId, "Stopping Bot")
        os.execv(sys.executable, ["None", "None"])
        marche = False
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
                fic.write(json.dumps(val.json, sort_keys=False, indent=4))

        with suppress(Exception):
            with open("elJson2.json", "w") as fic:
                fic.write(json.dumps(val2.json, sort_keys=False, indent=4))

        if os.path.getsize("elJson.json"):
            os.system("txt2pdf elJson.json --output result.pdf")
            pages = convert_from_path('result.pdf', 150)
            i = 1
            for page in pages:
                file = 'result'+str(i)+'.jpg'
                page.save(file,  'JPEG')
                with open(file,  'rb') as fp:
                    subClient.sendMessage(chatId, file=fp, fileType="image")
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
                    subClient.sendMessage(chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize("elJson.json") and not os.path.getsize("elJson.json"):
            subClient.sendMessage(chatId, "Error!")


def cinfo(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = ""

        with suppress(Exception):
            val = subClient.client.get_from_code("https://aminoapps.com/c/"+message)

        with suppress(Exception):
            with open("elJson.json", "w") as fic:
                fic.write(json.dumps(val.json, sort_keys=False, indent=4))

        if os.path.getsize("elJson.json"):
            os.system("txt2pdf elJson.json --output result.pdf")
            pages = convert_from_path('result.pdf', 150)
            i = 1
            for page in pages:
                file = 'result'+str(i)+'.jpg'
                page.save(file,  'JPEG')
                with open(file,  'rb') as fp:
                    subClient.sendMessage(chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize("elJson.json"):
            subClient.sendMessage(chatId, "Error!")
            return


def sendinfo(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if (is_it_admin(authorId) or is_it_me(authorId)) and message != "":
        arg = message.strip().split(" ")

        if not os.path.getsize("elJson.json") and not os.path.getsize("elJson2.json"):
            subClient.sendMessage(chatId, "Error!")
            return

        if os.path.getsize("elJson.json"):
            cont = True

            with open("elJson.json", 'r') as file:
                val = json.load(file)

            try:
                mem = arg.pop(0)
                memoire = val[mem]
            except:
                subClient.sendMessage(chatId, "Wrong key!")
                return

            if arg:
                for elem in arg:
                    try:
                        memoire = memoire[elem]
                    except:
                        subClient.sendMessage(chatId, "Wrong key 1!")
                        cont = False
            if cont:
                subClient.sendMessage(chatId, f"{memoire}")

        if os.path.getsize("elJson2.json"):
            cont = True

            with open("elJson2.json", 'r') as file:
                val = json.load(file)

            memoire = val[mem]

            if arg:
                for elem in arg:
                    try:
                        memoire = memoire[elem]
                    except:
                        subClient.sendMessage(chatId, "Wrong key 2!")
                        cont = False
            if cont:
                subClient.sendMessage(chatId, f"{memoire}")


def getglobal(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    val = subClient.get_user_id(message)[1]
    if val:
        ide = subClient.client.get_user_info(val).aminoId
        subClient.sendMessage(chatId, "http://aminoapps.com/u/"+ide)
        return
    subClient.sendMessage(chatId, "Error!")


def follow(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.followUser(authorId)
    subClient.sendMessage(chatId, "Now following you!")


def unfollow(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    subClient.unFollowUser(authorId)
    subClient.sendMessage(chatId, "Unfollow!")


def stopamino(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        subClient.stopInstance()
        del communaute[subClient.communityId]


def block(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.get_user_id(message)
        if val:
            subClient.client.block(val[1])
            subClient.sendMessage(chatId, f"User {val[0]} blocked!")


def unblock(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.client.get_blocked_users()
        for elem, t in zip(val.aminoId, val.userId):
            if message in elem:
                subClient.client.unblock(t)
                subClient.sendMessage(chatId, f"User {elem} unblocked!")


def accept(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if subClient.is_in_staff(authorId) or is_it_me(authorId) or is_it_admin(authorId):
        val = subClient.subclient.get_notices(start=0, size=25)
        ans = None
        res = None
        with suppress(Exception):
            subClient.subclient.accept_host(chatId)
            subClient.sendMessage(chatId, "Accepted!")
            return

        for elem in val:
            if 'become' in elem['title'] or "host" in elem['title']:
                res = elem['noticeId']
        if res:
            ans = subClient.acceptRole(res)
        if ans:
            subClient.sendMessage(chatId, "Accepted!")
        else:
            subClient.sendMessage(chatId, "Error!")


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

        subClient.askAllMembers(message, lvl)
        subClient.sendMessage(chatId, "Asking...")


def askstaff(subClient=None, chatId=None, authorId=None, author=None, message=None, messageId=None):
    if is_it_me(authorId) or is_it_admin(authorId):
        aminoList = client.sub_clients()
        for commu in aminoList.comId:
            communaute[commu].askAminoStaff(message=message)
        subClient.sendMessage(chatId, "Asking...")


commandDico = {"help": helper, "title": title, "dice": dice, "join": join, "ramen": ramen,
                "cookie": cookie, "leave": leave, "abw": abw, "rbw": rbw, "bwl": bwl,
                "clear": clear, "joinall": joinall, "leaveall": leaveall, "reboot": reboot,
                "stop": stop, "spam": spam, "mention": mention, "msg": msg,
                "uinfo": uinfo, "cinfo": cinfo, "joinamino": joinamino, "chatlist": chatList, "sw": sw,
                "accept": accept, "chatid": chatid, "prank": prank,
                "leaveamino": leaveAmino, "sendinfo": sendinfo, "image": image, "all": mentionall,
                "block": block, "unblock": unblock, "follow": follow, "unfollow": unfollow,
                "stopamino": stopamino, "block": block, "unblock": unblock,
                "ask": askthing, "askstaff": askstaff,
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
- chatlist\t: the list of public chats
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

[C]--- SPECIAL ---
- joinamino (amino id): join the amino (you need to be in the amino's staff)**
- uinfo (user): will give informations about the user²
- cinfo (aminoId): will give informations about the community²
- sendinfo (args): send the info from uinfo or cinfo

*(only work if bot is in staff)
**(In developpement)
²(only for devlopper or bot owner)

-- all commands are available for the owner of the bot --
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
        permsList = json.load(fic)
except FileNotFoundError:
    with open('admin.json', 'w') as fic:
        fic.write("['YOUR AMINOID HERE']")
    print("You should put your Amino Id in the file admin.json")
    permsList = []

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

client = amino.Client()
client.login(email=identifiant, password=mdp)
botId = client.userId
aminoList = client.sub_clients()

communaute = {}
tailleCommu = 0


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
        client.leave_community(commu)


for commu in aminoList.comId:
    th = threading.Thread(target=threadLaunch, args=[commu])
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

    if not is_it_bot(authorId) and not subClient.is_in_staff(authorId):
        with suppress(Exception):
            para = unicodedata.normalize('NFD', message).encode('ascii', 'ignore').decode("utf8").strip().lower()
            para = para.translate(str.maketrans("", "", string.punctuation))
            para = para.split(" ")
            if para == [""]:
                pass
            else:
                for elem in para:
                    if elem in subClient.bannedWords:
                        subClient.deleteMessage(chatId, data.message.messageId, "Banned word", asStaff=True)
                        return

    if message.startswith(subClient.prefixeId) and not is_it_bot(authorId):
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

    [threading.Thread(target=values, args=[subClient, chatId, authorId, author, message, messageId]).start() for key, values in commandDico.items() if commande == key.lower()]


print("Ready")
