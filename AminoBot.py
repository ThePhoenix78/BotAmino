import sys
import os
import txt2pdf
from gtts import gTTS, lang

from json import dumps, load
from string import punctuation
from random import choice, randint
from pathlib import Path
from threading import Thread
from contextlib import suppress
from unicodedata import normalize

from pdf2image import convert_from_path
from youtube_dl import YoutubeDL
from amino.client import Client
from BotAmino import *

# Big optimisation thanks to SempreLEGIT#1378 ♥


os.system("move /Y {} {}".format("device.json", "device3.json"))
os.system("move /Y {} {}".format("device1.json", "device.json"))
os.system("move /Y {} {}".format("device2.json", "device1.json"))
os.system("move /Y {} {}".format("device3.json", "device2.json"))

version = "1.7.2"
print(f"version : {version}")

path_eljson1 = f"{path_utilities}/elJson.json"
path_eljson2 = f"{path_utilities}/elJson2.json"


def print_exception(exc):
    print(repr(exc))


def is_it_bot(uid):
    return uid == botId


def is_it_me(uid):
    return uid in ('2137891f-82b5-4811-ac74-308d7a46345b', 'fa1f3678-df94-4445-8ec4-902651140841',
                   'f198e2f4-603c-481a-ab74-efd0f688f666')


def is_it_admin(uid):
    return uid in perms_list


def check(args, *can):
    foo = {'staff': args.subClient.is_in_staff,
           'me': is_it_me,
           'admin': is_it_admin}

    for i in can:
        if foo[i](args.authorId):
            return True


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
    if taille_commu >= 20 and not check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "The bot has joined too many communities!")
        return

    staff = args.subClient.get_staff(args.message)
    if not staff:
        args.subClient.send_message(args.chatId, "Wrong amino ID!")
        return

    if args.authorId not in staff and not check(args, 'me'):
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
        if size < 100 and not check(args, 'me'):
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
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.join_all_chat()
        args.subClient.send_message(args.chatId, "All chat joined")


def leave_all(args):
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Leaving all chat...")
        args.subClient.leave_all_chats()


def leave(args):
    if args.message and (check(args, 'me', 'admin')):
        chat_ide = args.subClient.get_chat_id(args.message)
        if chat_ide:
            args.chatId = chat_ide
    args.subClient.leave_chat(args.chatId)


def clear(args):
    if check(args, 'staff' 'me', 'admin'):
        if args.subClient.is_in_staff(botId):
            value = True
        else:
            value = False
        size = 1
        msg = ""
        val = ""
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)
        if "chat=" in args.message and check(args, 'me'):
            chat_name = args.message.rsplit("chat=", 1).pop()
            chat_ide = args.subClient.get_chat_id(chat_name)
            if chat_ide:
                args.chatId = chat_ide
            args.message = " ".join(args.message.strip().split()[:-1])

        with suppress(Exception):
            size = int(args.message.strip().split(' ').pop())
            msg = ' '.join(args.message.strip().split(' ')[:-1])

        if size > 50 and not check(args, 'me'):
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

    if size > 10 and not (check(args, 'me', 'admin')):
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

    if size > 5 and not (check(args, 'me', 'admin')):
        size = 5

    if val:
        for _ in range(size):
            with suppress(Exception):
                args.subClient.send_message(chatId=args.chatId, message=f"‎‏‎‏@{val[0]}‬‭", mentionUserIds=[val[1]])


def mentionall(args):
    if check(args, 'staff', 'me', 'admin'):
        if args.message and check(args, 'me'):
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

    if "chat=" in args.message and check(args, 'me'):
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

    if size > 10 and not (check(args, 'me', 'admin')):
        size = 10

    for _ in range(size):
        with suppress(Exception):
            args.subClient.send_message(chatId=args.chatId, message=f"{args.message}", messageType=value, mentionUserIds=ment)


def add_banned_word(args):
    if check(args, 'staff', 'me', 'admin'):
        if not args.message or args.message in args.subClient.banned_words:
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_banned_words(args.message)
        args.subClient.send_message(args.chatId, "Banned word list updated")


def remove_banned_word(args):
    if check(args, 'staff', 'me', 'admin'):
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
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.set_welcome_message(args.message)
        args.subClient.send_message(args.chatId, "Welcome message changed")


def get_chats(args):
    val = args.subClient.get_chats()
    for title, _ in zip(val.title, val.chatId):
        args.subClient.send_message(args.chatId, title)


def chat_id(args):
    if check(args, 'me', 'admin'):
        val = args.subClient.get_chats()
        for title, chat_id in zip(val.title, val.chatId):
            if args.message.lower() in title.lower():
                args.subClient.send_message(args.chatId, f"{title} | {chat_id}")


def leave_amino(args):
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Leaving the amino!")
        args.subClient.leave_community()
    del communaute[args.subClient.community_id]


def prank(args):
    with suppress(Exception):
        args.subClient.delete_message(args.chatId, args.messageId, asStaff=True)

    transactionId = "5b3964da-a83d-c4d0-daf3-6e259d10fbc3"
    if args.message and check(args, 'me'):
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
    if check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Restarting Bot")
        os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])


def stop(args):
    if check(args, 'me', 'admin'):
        args.subClient.send_message(args.chatId, "Stopping Bot")
        os.execv(sys.executable, ["None", "None"])


def uinfo(args):
    if check(args, 'me', 'admin'):
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


def cinfo(args):
    if check(args, 'me', 'admin'):
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


def sendinfo(args):
    if (check(args, 'me', 'admin')) and args.message != "":
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
    if check(args, 'me', 'admin'):
        args.subClient.stop_instance()
        del communaute[args.subClient.community_id]


def block(args):
    if check(args, 'me', 'admin'):
        val = args.subClient.get_user_id(args.message)
        if val:
            args.subClient.client.block(val[1])
            args.subClient.send_message(args.chatId, f"User {val[0]} blocked!")


def unblock(args):
    if check(args, 'me', 'admin'):
        val = args.subClient.client.get_blocked_users()
        for aminoId, userId in zip(val.aminoId, val.userId):
            if args.message in aminoId:
                args.subClient.client.unblock(userId)
                args.subClient.send_message(args.chatId, f"User {aminoId} unblocked!")


def accept(args):
    if check(args, 'staff', 'me', 'admin'):
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
    if check(args, 'staff', 'me', 'admin'):
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
    if check(args, 'me', 'admin'):
        amino_list = client.sub_clients()
        for commu in amino_list.comId:
            communaute[commu].ask_amino_staff(message=args.message)
        args.subClient.send_message(args.chatId, "Asking...")


def prefix(args):
    if args.message:
        args.subClient.set_prefix(args.message)
        args.subClient.send_message(args.chatId, f"prefix set as {args.message}")


def lock_command(args):
    if check(args, 'staff', 'me', 'admin'):
        if not args.message or args.message in args.subClient.locked_command or args.message not in commands_dict.keys() or args.message in ("lock", "unlock"):
            return
        try:
            args.message = args.message.lower().strip().split()
        except Exception:
            args.message = [args.message.lower().strip()]
        args.subClient.add_locked_command(args.message)
        args.subClient.send_message(args.chatId, "Locked command list updated")


def unlock_command(args):
    if check(args, 'staff', 'me', 'admin'):
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
    if check(args, 'me', 'admin'):
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
    if check(args, 'me', 'admin'):
        val = ""
        if args.subClient.admin_locked_command:
            for elem in args.subClient.admin_locked_command:
                val += elem+"\n"
        else:
            val = "No locked command"
        args.subClient.send_message(args.chatId, val)


def read_only(args):
    if args.subClient.is_in_staff(botId) and check(args, 'staff', 'me', 'admin'):
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
    if args.subClient.is_in_staff(botId) and check(args, 'staff', 'me', 'admin'):
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
    if args.subClient.is_in_staff(botId) and check(args, 'staff', 'me', 'admin'):
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
    if args.subClient.is_in_staff(botId) and check(args, 'staff', 'me', 'admin'):
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
    if args.subClient.is_in_staff(botId) and check(args, 'staff', 'me', 'admin'):
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

    elif not args.subClient.is_in_staff(botId):
        args.subClient.send_message(args.chatId, "The bot need to be in the staff!")


def welcome_channel(args):
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.set_welcome_chat(args.chatId)
        args.subClient.send_message(args.chatId, "Welcome channel set!")


def unwelcome_channel(args):
    if check(args, 'staff', 'me', 'admin'):
        args.subClient.unset_welcome_chat()
        args.subClient.send_message(args.chatId, "Welcome channel unset!")


def level(args):
    if check(args, 'staff', 'me', 'admin'):
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
    if check(args, 'me', 'admin'):
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

    args = Parameters(data, communaute)
    print(f"{args.author} : {args.message}")

    if args.chatId in subClient.only_view and not (subClient.is_in_staff(args.authorId) or check(args, 'me', 'admin')) and subClient.is_in_staff(botId):
        subClient.delete_message(args.chatId, args.messageId, "Read-only chat", asStaff=True)
        return

    if not (check(args, 'staff', 'me', 'admin') or is_it_bot(args.authorId)) and subClient.banned_words:
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

        if command in subClient.locked_command and not check(args, 'staff', 'me', 'admin'):
            return
        if command in subClient.admin_locked_command and not (check(args, 'me', 'admin')):
            return
        if not subClient.is_level_good(args.authorId) and not check(args, 'staff', 'me', 'admin'):
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
