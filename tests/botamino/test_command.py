from BotAmino import Parameters, parser


def sum(data: Parameters, a: int, b: int) -> None:
    result = str(a + b)
    data.subClient.send_message(data.chatId, message=result)


parser.validate_callback(sum)
