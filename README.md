# BotAmino
An API for bot amino based on Slimakoi's work

Discord server https://discord.gg/KZgKktQ6Rt

## How does this API works?

It works like the Amino.py's API but with added features like commands or answer
for example:

```python3
from BotAmino import BotAmino

print("wait...")
client = BotAmino()
client.prefix = "/"  # set the prefix to /
client.wait = 10  # wait 10 sec before doing a new command


@client.command("ping")
def ping(data):
    data.subClient.send_message(data.chatId, message="pong!")


@client.answer("hey")
def hello(data):
    data.subClient.send_message(data.chatId, message="Hey! Hey!")


client.launch()
print("ready")
```

## There is also built-in functions that might be useful:

• add_title(userId, title, color) : add a title to an user

• remove_title(userId, title) : remove the title given to the user

• follow_user(userId) : follow the user in parameters

• unfollow_user(userId) : unfollow the user in parameters

• leave_all_chats() : leave all the chats for a given community

• join_all_chat() : join all the publics chat of an Amino

• get_chats() : return a list of the publics chatrooms

• join_chatroom(chat_name_or_link) : join the chat for the given link/name

• pay(nb_of_coins, blogId, chatId, objectId, transactionId) : give coins in balance, transactionId not necessary (automatically generated if not put)

• get_wallet_amount() : return the number of coin of the bot

• get_member_title(userId) : return the titles of the member

• get_member_level(userId) : return the level of the member [1-20]

• leave_community() : leave the current community

• get_chat_id(chat) : return the id of the chat (link supported)

• ask_amino_staff(message) : send the message to all the curators/leader of the amino

• get_user_id(name_or_id) : return a tuple with the name and the userId (name, uid)

• get_staff(community) : return the staff of the given community (communityId or aminoId)

• accept_role(noticeId, chatId) : accept a promotion or a chat transfert
