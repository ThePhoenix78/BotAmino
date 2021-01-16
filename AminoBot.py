import sys
import os
import txt2pdf
from gtts import gTTS, lang

from json import dumps, load
from random import choice, randint
from pathlib import Path
from contextlib import suppress

from pdf2image import convert_from_path
from youtube_dl import YoutubeDL
from BotAmino import *

# Big optimisation thanks to SempreLEGIT#1378 ♥


version = "1.7.3"
print(f"version : {version}")

path_eljson1 = f"{path_utilities}/elJson.json"
path_eljson2 = f"{path_utilities}/elJson2.json"

communaute = BotAmino()


def print_exception(exc):
    print(repr(exc))


def join_community(comId: str = None, inv: str = None):
    if inv:
        try:
            communaute.client.request_join_community(comId=comId, message='Cookie for everyone!!')
            return True
        except Exception as e:
            print_exception(e)
    else:
        try:
            communaute.client.join_community(comId=comId, invitationId=inv)
            return True
        except Exception as e:
            print_exception(e)


@communaute.command("joinamino")
def join_amino(args):
    invit = None
    if communaute.taille_commu >= 20 and not communaute.check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "The bot has joined too many communities!")
        return

    staff = args.subClient.get_staff(args.message)

    if args.authorId not in staff and not communaute.communaute.check(args, 'me'):
        args.subClient.send_message(args.chatId, "You need to be in the community's staff!")
        return

    if not staff:
        args.subClient.send_message(args.chatId, "Wrong amino ID!")
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
        if size < 100 and not communaute.communaute.check(args, 'me'):
            args.subClient.send_message(args.chatId, "Your community must have at least 100 members")
            return

        join_community(comId, invit)
        val = communaute.client.get_from_code(f"http://aminoapps.com/c/{amino_c}")
        isJoined = val.json["extensions"]["isCurrentUserJoined"]
        if isJoined:
            communaute.add_community(args.message)
            communaute[comId].run()
            auth = communaute.get_community(comId).subclient.get_user_info(args.message).nickname
            communaute[comId].ask_amino_staff(f"Hello! I am a bot and i can do a lot of stuff!\nI've been invited here by {auth}.\nIf you need help, you can do !help.\nEnjoy^^")
            args.subClient.send_message(args.chatId, "Joined!")
            return
        args.subClient.send_message(args.chatId, "Waiting for join!")
        return
    else:
        args.subClient.send_message(args.chatId, "Allready joined!")
        return

    args.subClient.send_message(args.chatId, "Something went wrong!")


@communaute.command("title")
def title(args):
    if communaute.communaute.check(args, 'staff', id_=communaute.botId):
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


@communaute.command("cookie")
def cookie(args):
    args.subClient.send_message(args.chatId, f"Here is a cookie for {args.author} 🍪")


@communaute.command("ramen")
def ramen(args):
    args.subClient.send_message(args.chatId, f"Here are some ramen for {args.author} 🍜")


@communaute.command("dice")
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


@communaute.command("join")
def join(args):
    val = args.subClient.join_chat(args.message, args.chatId)
    if val or val == "":
        args.subClient.send_message(args.chatId, f"Chat {val} joined".strip())
    else:
        args.subClient.send_message(args.chatId, "No chat joined")


@communaute.command("joinall")
def join_all(args):
    if communaute.communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.join_all_chat()
        args.subClient.send_message(args.chatId, "All chat joined")


@communaute.command("leaveall")
def leave_all(args):
    if communaute.communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Leaving all chat...")
        args.subClient.leave_all_chats()


@communaute.command("leave")
def leave(args):
    if args.message and (communaute.communaute.check(args, 'me', 'admin')):
        chat_ide = args.subClient.get_chat_id(args.message)
        if chat_ide:
            args.chatId = chat_ide
    args.subClient.leave_chat(args.chatId)


@communaute.command("clear")
def clear(args):
    if communaute.communaute.check(args, 'staff', 'me', 'admin'):
        if communaute.communaute.check(args, 'staff', id_=communaute.botId):
            value = True
        else:
            value = False
        size = 1
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)

        if size > 50 and not communaute.communaute.check(args, 'me'):
            size = 50

        messages = args.subClient.subclient.get_chat_messages(chatId=args.chatId, size=size).messageId

        for message in messages:
            with suppress(Exception):
                args.subClient.delete_message(args.chatId, message, asStaff=value)


@communaute.command("spam")
def spam(args):
    try:
        size = int(args.message.strip().split().pop())
        msg = " ".join(args.message.strip().split()[:-1])
    except ValueError:
        size = 1
        msg = args.message

    if size > 10 and not (communaute.communaute.check(args, 'me', 'admin')):
        size = 10

    for _ in range(size):
        with suppress(Exception):
            args.subClient.send_message(args.chatId, msg)


@communaute.command("mention")
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

    if size > 5 and not (communaute.communaute.check(args, 'me', 'admin')):
        size = 5

    if val:
        for _ in range(size):
            with suppress(Exception):
                args.subClient.send_message(chatId=args.chatId, message=f"‎‏‎‏@{val[0]}‬‭", mentionUserIds=[val[1]])


@communaute.command("all")
def mentionall(args):
    if communaute.communaute.check(args, 'staff', 'me', 'admin'):
        if args.message and communaute.communaute.check(args, 'me'):
            chat_ide = args.subClient.get_chat_id(args.message)
            if chat_ide:
                args.chatId = chat_ide
            args.message = " ".join(args.message.strip().split()[:-1])

        mention = [userId for userId in args.subClient.subclient.get_chat_users(chatId=args.chatId).userId]
        test = "".join(["‎‏‎‏‬‭" for user in args.subClient.subclient.get_chat_users(chatId=args.chatId).userId])

        with suppress(Exception):
            args.subClient.send_message(chatId=args.chatId, message=f"@everyone{test}", mentionUserIds=mention)


@communaute.command("msg")
def msg(args):
    value = 0
    size = 1
    ment = None
    with suppress(Exception):
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=False)

    if "chat=" in args.message and communaute.communaute.check(args, 'me'):
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

    if size > 10 and not (communaute.check(args, 'me', 'admin')):
        size = 10

    for _ in range(size):
        with suppress(Exception):
            args.subClient.send_message(chatId=args.chatId, message=f"{args.message}", messageType=value, mentionUserIds=ment)


@communaute.command("abw")
def add_banned_word(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        if not args.message or args.message in args.subClient.banned_words:
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_banned_words(args.message)
        args.subClient.send_message(args.chatId, "Banned word list updated")


@communaute.command("rbw")
def remove_banned_word(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        if not args.message:
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.remove_banned_words(args.message)
        args.subClient.send_message(args.chatId, "Banned word list updated")


@communaute.command("bwl")
def banned_word_list(args):
    val = ""
    if args.subClient.banned_words:
        for elem in args.subClient.banned_words:
            val += elem + "\n"
    else:
        val = "No words in the list"
    args.subClient.send_message(args.chatId, val)


@communaute.command("sw")
def sw(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.set_welcome_message(args.message)
        args.subClient.send_message(args.chatId, "Welcome message changed")


@communaute.command("chatlist")
def get_chats(args):
    val = args.subClient.get_chats()
    for title, _ in zip(val.title, val.chatId):
        args.subClient.send_message(args.chatId, title)


@communaute.command("chatid")
def chat_id(args):
    if communaute.check(args, 'me', 'admin'):
        val = args.subClient.get_chats()
        for title, chat_id in zip(val.title, val.chatId):
            if args.message.lower() in title.lower():
                args.subClient.send_message(args.chatId, f"{title} | {chat_id}")


@communaute.command("leaveamino")
def leave_amino(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Leaving the amino!")
        args.subClient.leave_community()
    del communaute[args.subClient.community_id]


@communaute.command("prank")
def prank(args):
    with suppress(Exception):
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)

    transactionId = "5b3964da-a83d-c4d0-daf3-6e259d10fbc3"
    if args.message and communaute.check(args, 'me'):
        chat_ide = args.subClient.get_chat_id(args.message)
        if chat_ide:
            args.chatId = chat_ide
    for _ in range(10):
        args.subClient.pay(coins=500, chatId=args.chatId, transactionId=transactionId)


@communaute.command("image")
def image(args):
    val = os.listdir("pictures")
    if val:
        file = choice(val)
        with suppress(Exception):
            with open(path_picture+file, 'rb') as fp:
                args.subClient.send_message(args.chatId, file=fp, fileType="image")
    else:
        args.subClient.send_message(args.chatId, "Error! No file")


@communaute.command("audio")
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


@communaute.command("convert")
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


@communaute.command("help")
def helper(args):
    if not args.message:
        args.subClient.send_message(args.chatId, helpMsg)
    elif args.message == "msg":
        args.subClient.send_message(args.chatId, help_message)
    elif args.message == "ask":
        args.subClient.send_message(args.chatId, helpAsk)
    else:
        args.subClient.send_message(args.chatId, "No help is available for this command")


@communaute.command("reboot")
def reboot(args):
    if communaute.check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Restarting Bot")
        os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])


def stop(args):
    if communaute.check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Stopping Bot")
        os.execv(sys.executable, ["None", "None"])


@communaute.command("uinfo")
def uinfo(args):
    if communaute.check(args, 'me', 'admin'):
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
            with open(path_eljson1, "w") as file:
                file.write(dumps(val.json, sort_keys=True, indent=4))

        with suppress(Exception):
            with open(path_eljson2, "w") as file:
                file.write(dumps(val2.json, sort_keys=True, indent=4))

        for i in (path_eljson1, path_eljson2):
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

        if not os.path.getsize(path_eljson1) and not os.path.getsize(path_eljson1):
            args.subClient.send_message(args.chatId, "Error!")


@communaute.command("cinfo")
def cinfo(args):
    if communaute.check(args, 'me', 'admin'):
        val = ""
        with suppress(Exception):
            val = args.subClient.client.get_from_code(f"http://aminoapps.com/c/{args.message}")

        with suppress(Exception):
            with open(path_eljson1, "w") as file:
                file.write(dumps(val.json, sort_keys=True, indent=4))

        if os.path.getsize(path_eljson1):
            txt2pdf.callPDF(path_eljson1, "result.pdf")
            pages = convert_from_path('result.pdf', 150)
            for page in pages:
                file = 'result.jpg'
                page.save(file,  'JPEG')
                with open(file, 'rb') as fp:
                    args.subClient.send_message(args.chatId, file=fp, fileType="image")
                os.remove(file)
            os.remove("result.pdf")

        if not os.path.getsize(path_eljson1):
            args.subClient.send_message(args.chatId, "Error!")


@communaute.command("sendinfo")
def sendinfo(args):
    if (communaute.check(args, 'me', 'admin')) and args.message != "":
        arguments = args.message.strip().split()
        for eljson in (path_eljson1, path_eljson2):
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


@communaute.command("global")
def get_global(args):
    val = args.subClient.get_user_id(args.message)[1]
    if val:
        ide = args.subClient.client.get_user_info(val).aminoId
        args.subClient.send_message(args.chatId, f"http://aminoapps.com/u/{ide}")
    else:
        args.subClient.send_message(args.chatId, "Error!")


@communaute.command("follow")
def follow(args):
    args.subClient.follow_user(args.authorId)
    args.subClient.send_message(args.chatId, "Now following you!")


@communaute.command("unfollow")
def unfollow(args):
    args.subClient.unfollow_user(args.authorId)
    args.subClient.send_message(args.chatId, "Unfollow!")


@communaute.command("stopamino")
def stop_amino(args):
    if communaute.check(args, 'me', 'admin'):
        args.subClient.stop_instance()
        del communaute[args.subClient.community_id]


@communaute.command("block")
def block(args):
    if communaute.check(args, 'me', 'admin'):
        val = args.subClient.get_user_id(args.message)
        if val:
            args.subClient.client.block(val[1])
            args.subClient.send_message(args.chatId, f"User {val[0]} blocked!")


@communaute.command("unblock")
def unblock(args):
    if communaute.check(args, 'me', 'admin'):
        val = args.subClient.client.get_blocked_users()
        for aminoId, userId in zip(val.aminoId, val.userId):
            if args.message in aminoId:
                args.subClient.client.unblock(userId)
                args.subClient.send_message(args.chatId, f"User {aminoId} unblocked!")


@communaute.command("accept")
def accept(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
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


@communaute.command("say")
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


@communaute.command("ask")
def ask_thing(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
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


@communaute.command("askstaff")
def ask_staff(args):
    if communaute.check(args, 'me', 'admin'):
        amino_list = communaute.client.sub_clients()
        for commu in amino_list.comId:
            communaute[commu].ask_amino_staff(message=args.message)
        args.subClient.send_message(args.chatId, "Asking...")


@communaute.command("prefix")
def prefix(args):
    if args.message:
        args.subClient.set_prefix(args.message)
        args.subClient.send_message(args.chatId, f"prefix set as {args.message}")


@communaute.command("lock")
def lock_command(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        if not args.message or args.message in args.subClient.locked_command or args.message not in communaute.get_commands_names() or args.message in ("lock", "unlock"):
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_locked_command(args.message)
        args.subClient.send_message(args.chatId, "Locked command list updated")


@communaute.command("unlock")
def unlock_command(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        if args.message:
            try:
                args.message = args.message.lower().strip().split()
            except Exception:
                args.message = [args.message.lower().strip()]
            args.subClient.remove_locked_command(args.message)
            args.subClient.send_message(args.chatId, "Locked command list updated")


@communaute.command("llock")
def locked_command_list(args):
    val = ""
    if args.subClient.locked_command:
        for elem in args.subClient.locked_command:
            val += elem+"\n"
    else:
        val = "No locked command"
    args.subClient.send_message(args.chatId, val)


@communaute.command("alock")
def admin_lock_command(args):
    if communaute.check(args, 'me', 'admin'):
        if not args.message or args.message not in communaute.get_commands_names() or args.message == "alock":
            return

        command = args.subClient.admin_locked_command
        args.message = [args.message]

        if args.message[0] in command:
            args.subClient.remove_admin_locked_command(args.message)
        else:
            args.subClient.add_admin_locked_command(args.message)

        args.subClient.send_message(args.chatId, "Locked command list updated")


@communaute.command("allock")
def locked_admin_command_list(args):
    if communaute.check(args, 'me', 'admin'):
        val = ""
        if args.subClient.admin_locked_command:
            for elem in args.subClient.admin_locked_command:
                val += elem+"\n"
        else:
            val = "No locked command"
        args.subClient.send_message(args.chatId, val)


@communaute.command("view")
def read_only(args):
    if args.subClient.is_in_staff(communaute.botId) and communaute.check(args, 'staff', 'me', 'admin'):
        chats = args.subClient.only_view
        if args.chatId not in chats:
            args.subClient.add_only_view(args.chatId)
            args.subClient.send_message(args.chatId, "This chat is now in only-view mode")
        else:
            args.subClient.remove_only_view(args.chatId)
            args.subClient.send_message(args.chatId, "This chat is no longer in only-view mode")
        return
    elif not communaute.check(args, 'staff', id_=communaute.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


@communaute.command("keepu")
def keep_favorite_users(args):
    if args.subClient.is_in_staff(communaute.botId) and communaute.check(args, 'staff', 'me', 'admin'):
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
    elif not communaute.check(args, 'staff', id_=communaute.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")
    else:
        args.subClient.send_message(args.chatId, "Error!")


@communaute.command("unkeepu")
def unkeep_favorite_users(args):
    if args.subClient.is_in_staff(communaute.botId) and communaute.check(args, 'staff', 'me', 'admin'):
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
    elif not communaute.check(args, 'staff', id_=communaute.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")
    else:
        args.subClient.send_message(args.chatId, "Error!")


@communaute.command("keepc")
def keep_favorite_chats(args):
    if args.subClient.is_in_staff(communaute.botId) and communaute.check(args, 'staff', 'me', 'admin'):
        chats = args.subClient.favorite_chats
        with suppress(Exception):
            chat = args.subClient.subclient.get_from_code(f"{args.message}")
            if chat.objectId not in chats:
                args.subClient.add_favorite_chats(chat.objectId)
                args.subClient.send_message(args.chatId, "Added to favorite chats")
            return

        val = args.subClient.get_chats()

        for title, chatId in zip(val.title, val.chatId):
            if args.message == title and chatId not in chats:
                args.subClient.add_favorite_chats(chatId)
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
    elif not communaute.check(args, 'staff', id_=communaute.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")
    else:
        args.subClient.send_message(args.chatId, "Error!")


@communaute.command("unkeepc")
def unkeep_favorite_chats(args):
    if args.subClient.is_in_staff(communaute.botId) and communaute.check(args, 'staff', 'me', 'admin'):
        chats = args.subClient.favorite_chats

        with suppress(Exception):
            chat = args.subClient.subclient.get_from_code(f"{args.message}")
            if chat.objectId in chats:
                args.subClient.remove_favorite_chats(chat.objectId)
                args.subClient.send_message(args.chatId, "Removed to favorite chats")
            return

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

    elif not communaute.check(args, 'staff', id_=communaute.botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")
    else:
        args.subClient.send_message(args.chatId, "Error!")


@communaute.command("welcome")
def welcome_channel(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.set_welcome_chat(args.chatId)
        args.subClient.send_message(args.chatId, "Welcome channel set!")


@communaute.command("unwelcome")
def unwelcome_channel(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
        args.subClient.unset_welcome_chat()
        args.subClient.send_message(args.chatId, "Welcome channel unset!")


@communaute.command("level")
def level(args):
    if communaute.check(args, 'staff', 'me', 'admin'):
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


@communaute.command("taxe")
def taxe(args):
    if communaute.check(args, 'me', 'admin'):
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

communaute.launch()
print("Ready")
