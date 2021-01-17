from BotAmino import *

print("Wait...")

client = BotAmino()
client.prefix = "/"

# parameters inside the args : subClient : the "amino",
#                              chatId : the chat where the command has be done,
#                              authorId : the id of the author
#                              author : the username of the user who did the command
#                              message : the content of the message (withoud the !command)
#                              messageId : the message id of the command


@client.command("hello")
def and_random_action(args):
    args.subClient.send_message(args.chatId, "Hello!^^")


print(client.commands_list())

client.launch()
print("ready")
