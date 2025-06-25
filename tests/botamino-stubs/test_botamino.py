from typing import reveal_type
from BotAmino import BotAmino

email, password = input('email: '), input('password: ')

bot = BotAmino(email.strip(), password.strip())


reveal_type(bot)
reveal_type(bot.userId)
reveal_type(bot.bio)
reveal_type(bot.commands)
