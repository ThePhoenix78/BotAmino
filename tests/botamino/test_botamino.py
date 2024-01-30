import BotAmino

email, password = input('email: '), input('password: ')

bot = BotAmino.BotAmino(email.strip(), password.strip())

@bot.command(['test', 'hi'])
def _(data: BotAmino.Parameters) -> None:
    print(data.author, data.message, data.authorIcon)

bot.launch(False)
