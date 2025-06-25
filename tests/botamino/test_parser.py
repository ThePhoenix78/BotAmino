import os
import typing
import BotAmino.parser


def command(
    data: BotAmino.Parameters,
    a: str,
    b: int,
    c: typing.Literal[1, 2, 3],
    d: typing.Literal[4, 5, 6] = 4
) -> None:
    print(f"{data=} {a=} {b=} {c=} {d=}")

BotAmino.parser.validate_callback(command)

inputs = [
    "hello 452.23 3 7",
    "world 23 4 5"
]

for message in inputs:
    data = typing.cast(BotAmino.Parameters, None)
    arguments = BotAmino.parser.parse_args(message)
    args, kwargs = BotAmino.parser.bind_callback(command, data, arguments)
    command(*args, **kwargs)

os._exit(0)
