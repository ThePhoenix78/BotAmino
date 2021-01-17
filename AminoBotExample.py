from BotAmino import *

client = BotAmino()
client.prefix = "/"

@client.command("hello")
def and_random_action(args):
    args.subClient.send_message(args.chatId, "Hello!^^")

client.launch()
print("ready")
