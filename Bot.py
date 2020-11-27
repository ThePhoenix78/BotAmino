import amino
import json
import os
import sys
import unicodedata
import time
import string
import threading


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

try:
    os.mkdir("utilities")
except FileExistsError:
    pass

try:
    os.mkdir("pictures")
except FileExistsError:
    pass

try:
    os.mkdir("download")
except FileExistsError:
    pass

try:
    os.mkdir("sound")
except FileExistsError:
    pass

try:
    os.mkdir(f"utilities{slash}welcomeMessage")
except FileExistsError:
    pass

try:
    os.mkdir(f"utilities{slash}bannedWords")
except FileExistsError:
    pass


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
        fic = open(f"{pathWelcome}{self.communityAminoId}.txt", "w", encoding="utf8")
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
            users = self.subclient.get_all_users(type="recent", start=st, size=100)
            for user in users.json['userProfileList']:
                if user["level"] <= lvl:
                    userLvlList.append(user['uid'])
            self.subclient.start_chat(userId=userLvlList, message=message)
            size -= 100
            st += 100

        userLvlList = []
        users = self.subclient.get_all_users(type="recent", start=0, size=size)

        for user in users.json['userProfileList']:
            if user["level"] <= lvl:
                userLvlList.append(user['uid'])

        self.subclient.start_chat(userId=userLvlList, message=message)

    def askAminoStaff(self, message):
        users = self.communityStaff
        self.subclient.start_chat(userId=users, message=message)

    def getChatId(self, chat: str = None):
        try:
            chati = self.subclient.get_from_code(chat).objectId
            return chati
        except:
            pass
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
            message = fic.read()
        return message

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
            try:
                self.subclient.leave_chat(elem)
            except:
                pass


    def checkNewMember(self):
        newList = self.subclient.get_all_users(start=0, size=25, type="recent")
        newMember = [elem["uid"] for elem in newList.json["userProfileList"]]
        for elem in newMember:
            try:
                val = self.subclient.get_wall_comments(userId=elem, sorting="newest").commentId
            except:
                val = True
            if elem not in self.allNewUsersCommunityId or not val:
                try:
                    self.subclient.comment(message=self.messageBvn, userId=elem)
                except:
                    pass
                self.allUsers += 1
                self.allNewUsersCommunityId.append(elem)

    def getMemberLevel(self, UID):
        return self.subclient.get_user_info(userId=UID).level

    def isLevelGood(self, UID):
        return self.subclient.get_user_info(userId=UID).level > self.lvlmin

    def getMemberTitles(self, UID):
        try:
            val = self.subclient.get_user_info(userId=UID).customTitles
        except:
            val = False
        return val

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
            try:
                self.subclient.join_chat(chatId)
                return ""
            except:
                pass
        try:
            chati = self.subclient.get_from_code(chat).objectId
            self.subclient.join_chat(chati)
            return chat
        except:
            pass
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
            try:
                self.subclient.join_chat(elem)
            except:
                pass

    def leaveChat(self, chat: str):
        self.subclient.leave_chat(chat)

    def leaveAllChat(self):
        val = self.subclient.get_public_chat_threads().chatId
        for elem in val:
            try:
                self.subclient.leave_chat(elem)
            except:
                pass

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
        try:
            self.subclient.edit_titles(UID, tlist, clist)
        except:
            pass
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
        while self.marche:
            if i >= 60:
                if self.messageBvn:
                    self.checkNewMember()
                try:
                    self.subclient.activity_status("on")
                except:
                    pass
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

try:
    with open("admin.json", "r") as fic:
        permsList = json.load(fic)
except FileNotFoundError:
    fic = open("admin.json", "w")
    fic.write('["YOUR AMINOID HERE"]')
    fic.close()
    print("You should put your Amino Id in the file admin.json")
    permsList = []

try:
    with open("client.txt", "r") as fic:
        login = fic.readlines()
except FileNotFoundError:
    fic = open("client.txt", "w")
    fic.write("email\npassword")
    fic.close()
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
        try:
            val = client.get_from_code("https://aminoapps.com/u/"+elem).objectId
            sublist.append(val)
            continue
        except:
            pass
        try:
            val = client.get_user_info(elem).userId
            sublist.append(val)
            continue
        except:
            pass
    return sublist


permsList = tradlist(permsList)


def threadLaunch(commu):
    try:
        commi = BotAmino(client=client, community=commu)
        communaute[commi.communityId] = commi
        communaute[commi.communityId].run()
    except:
        client.leave_community(commu)


for commu in aminoList.comId:
    th = threading.Thread(target=threadLaunch, args=[commu])
    th.start()
    tailleCommu += 1

th.join()

commandDico = {}

@client.callbacks.event("on_text_message")
def on_text_message(data):
    try:
        commuId = data.json["ndcId"]
        subClient = communaute[commuId]
    except:
        return

    message = data.message.content
    chatId = data.message.chatId
    authorId = data.message.author.userId
    messageId = data.message.messageId

    if not is_it_bot(authorId) and not subClient.is_in_staff(authorId):
        try:
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
        except:
            pass

    if message.startswith(subClient.prefixeId) and not is_it_bot(authorId):
        author = data.message.author.nickname
        commande = ""
        message = str(message).strip().split(communaute[commuId].prefixeId, 1).pop()
        commande = str(message).strip().split(" ", 1)[0].lower()
        try:
            message = str(message).strip().split(" ", 1)[1]
        except:
            message = ""
    else:
        return

    [threading.Thread(target=values, args=[subClient, chatId, authorId, author, message, messageId]).start() for key, values in commandDico.items() if commande == key.lower()]


print("Ready")
