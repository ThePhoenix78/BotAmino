from BotAmino import *
from gtts import gTTS, lang
import os
from random import choice


print("wait...")
client = BotAmino()
client.prefix = "/"

# parameters inside the data : subClient : the "amino",
#                              chatId : the chat where the command has be done,
#                              authorId : the id of the author
#                              author : the username of the user who did the command
#                              message : the content of the message (withoud the !command)
#                              messageId : the message id of the command


@client.command("say")
def say_something(data):
    audio_file = "ttp.mp3"
    langue = list(lang.tts_langs().keys())
    gTTS(text=data.message, lang=choice(langue), slow=False).save(audio_file)
    with open(audio_file, 'rb') as fp:
        data.subClient.send_message(data.chatId, file=fp, fileType="audio")
    os.remove(audio_file)


@client.command("hello")
def random_action(data):
    data.subClient.send_message(data.chatId, "Hello!^^")


# --->
# first, we name our command, here, I will call it title


@client.command("title_example")
def give_a_title(data):
    # we give the function the name we want (here give_a_title for example)
    # /!\ The function MUST HAVE a parameter (call it data for an easy use)
    data.subClient.add_title(data.authorId, data.message)
    # My API have some code allready done to make the life easier, and the add_title is one of them
    # To use it, just do : data.subClient (= the community where the command have to be done)
    # data.authorId is for giving the title to the user that made the command
    # data.message is the name of the title (if the command was !title DOLPHIN, then message will be DOLPHIN)

    data.subClient.send_message(chatId=data.chatId, message="Done!")
    # Here is an cfunction taken from the Amino.py's API (https://aminopy.readthedocs.io/en/latest/amino.html#amino.client.Client.send_message)
    # it take at least 2 parameters, the chatId (the chat where the message have to be send)
    # and the message (here Done!), you can add as well other parameters like replyTo=data.authorId


@client.command("title")
def title(args):
    if client.check(args, 'staff', id_=client.botId):
        try:
            title, color = args.message.split("color=")
            color = color if color.startswith("#") else f'#{color}'
        except Exception:
            title = args.message
            color = None

        if args.subClient.add_title(args.authorId, title, color):
            args.subClient.send_message(args.chatId, f"The titles of {args.author} has changed")


@client.command("8ball")
def height_ball(data):
    test = choice(["não", "sim", "talvez", "claro", "nunca", "acho que sim"])
    data.subClient.send_message(data.chatId, test)


client.launch()


@client.callbacks.event("on_voice_message")
def on_audio(data):
    print("audio_file")


print("ready")
