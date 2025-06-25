from __future__ import annotations

import collections.abc
import typing
import typing_extensions

# internal
from .deprecated import DEPRECATED_EVENTS
from .parser import bind_callback, parse_args, validate_callback, validate_lite_callback
from .parameters import Parameters
from .types import MediaType, MessageType
from .typing import CallbackCategory, Callback, Condition, Events, LiteCallbackT

__all__ = ("Command",)

P = typing_extensions.ParamSpec("P")


class Command:
    """Represents the chat message commands plugin (Base)"""

    def __init__(self) -> None:
        self.commands: dict[
            CallbackCategory,
            dict[typing.Any, collections.abc.Callable[..., typing.Any]],
        ] = {}
        self.conditions: dict[CallbackCategory, dict[typing.Any, Condition]] = {}

    def execute(
        self, key: typing.Any, data: Parameters, category: CallbackCategory = "command"
    ) -> typing.Any:
        """Try to execute the specified command"""
        callback = self.commands[category][key]
        condition = self.conditions[category].get(key, None)
        if condition and not condition(data):
            return
        arguments = parse_args(data.message, data.subClient.client.parser_feature)
        args, kwargs = bind_callback(callback, data, arguments)
        return callback(*args, **kwargs)

    def categorie_exist(self, category: CallbackCategory) -> bool:
        """Check if the given callback-category exists"""
        return category in self.commands

    def add_category(self, category: CallbackCategory) -> None:
        """Create the given callback-category"""
        if category not in self.commands:
            self.commands[category] = {}

    def add_condition(self, category: CallbackCategory) -> None:
        """Create condition for the given callback-category"""
        if category not in self.conditions:
            self.conditions[category] = {}

    def commands_list(self) -> list[str]:
        """Get command list names"""
        return list(self.commands["command"])

    def answer_list(self) -> list[str]:
        """Get answer list names"""
        return list(self.commands["answer"])

    def command(
        self,
        name: str | typing.Iterable[str] | None = None,
        condition: Condition | None = None,
    ) -> collections.abc.Callable[[Callback[P]], Callback[P]]:
        """Decorator to create a command

        Parameters
        ----------
        name : str, Iterable[str], optional
            The name or names of the command. If not provided, the name will be set to the name of the decorated function.
        condition : Callable[[Parameters], bool], optional
            The command condition. Default is None.

        Examples
        --------
        ```
        @botamino.command('test')
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message="Bot is ready!")
        ```

        """
        self.add_category("command")
        self.add_condition("command")
        names = set(
            [name]
            if isinstance(name, str)
            else list(name) if isinstance(name, collections.abc.Iterable) else []
        )
        if callable(condition):
            validate_lite_callback(condition)

        def inner(callback: Callback[P]) -> Callback[P]:
            validate_callback(callback)
            if not names:
                names.add(callback.__name__)
            if callable(condition):
                for command in names:
                    self.conditions["command"][command] = condition
            for command in names:
                self.commands["command"][command.lower()] = callback
            return callback

        return inner

    def answer(
        self,
        name: str | typing.Iterable[str] | None = None,
        condition: Condition | None = None,
    ) -> collections.abc.Callable[[Callback[P]], Callback[P]]:
        """Decorator to create an answer

        Parameters
        ----------
        name : str, Iterable[str], optional
            The name or names of the answer. If not provided, the name will be set to the name of the decorated function.
        condition : Callable[[Parameters], bool], optional
            The answer condition. Default is None.

        Examples
        --------
        ```
        @botamino.answer('hi')
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message=f"Hi @{data.author}!", mentionUserIds=[data.authorId])
        ```

        """
        self.add_category("answer")
        self.add_condition("answer")
        names = set(
            [name]
            if isinstance(name, str)
            else list(name) if isinstance(name, collections.abc.Iterable) else []
        )
        if callable(condition):
            validate_lite_callback(condition)

        def inner(callback: Callback[P]) -> Callback[P]:
            validate_callback(callback)
            if not names:
                names.add(callback.__name__)
            if callable(condition):
                for command in names:
                    self.conditions["answer"][command] = condition
            for command in names:
                self.commands["answer"][command.lower()] = callback
            return callback

        return inner

    def on_member_join_chat(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_member_join_chat event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_member_join_chat()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message=f"Welcome @{data.author}!", mentionUserIds=[data.authorId])
        ```

        """
        self.add_category("on_member_join_chat")
        self.add_condition("on_member_join_chat")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_member_join_chat"]["on_member_join_chat"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_member_join_chat"]["on_member_join_chat"] = callback
            return callback

        return inner

    def on_member_leave_chat(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_member_leave_chat event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_member_leave_chat()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message=f"Bye @{data.author}!", mentionUserIds=[data.authorId])
        ```

        """
        self.add_category("on_member_leave_chat")
        self.add_condition("on_member_leave_chat")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_member_leave_chat"]["on_member_leave_chat"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_member_leave_chat"]["on_member_leave_chat"] = callback
            return callback

        return inner

    def on_message(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_message event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_message(condition=lambda data: bool(data.replyId))
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message=f"mmm ...")
        ```

        """
        self.add_category("on_message")
        self.add_condition("on_message")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_message"]["on_message"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_message"]["on_message"] = callback
            return callback

        return inner

    def on_other(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_other event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_other()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message="live chat!")
        ```

        """
        self.add_category("on_other")
        self.add_condition("on_other")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_other"]["on_other"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_other"]["on_other"] = callback
            return callback

        return inner

    def on_delete(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_delete event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_delete()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message="deleted message!")
        ```

        """
        self.add_category("on_delete")
        self.add_condition("on_delete")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_delete"]["on_delete"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_delete"]["on_delete"] = callback
            return callback

        return inner

    def on_remove(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_remove event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_remove()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message="force removed message!")
        ```

        """
        self.add_category("on_remove")
        self.add_condition("on_remove")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_remove"]["on_remove"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_remove"]["on_remove"] = callback
            return callback

        return inner

    def on_all(
        self, condition: Condition | None = None
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_all event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_all()
        def test(data: Parameters) -> None:
            data.subClient.send_message(data.chatId, message="Hi there!")
        ```

        """
        self.add_category("on_all")
        self.add_condition("on_all")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_all"]["on_all"] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            self.commands["on_all"]["on_all"] = callback
            return callback

        return inner

    def on_event(
        self,
        name: (
            Events
            | MessageType
            | MediaType
            | collections.abc.Iterable[Events | MessageType | MediaType]
        ),
        condition: Condition | None = None,
    ) -> collections.abc.Callable[[LiteCallbackT], LiteCallbackT]:
        """Decorator to create the on_event event

        Parameters
        ----------
        condition : Callable[[Parameters], bool], optional
            The event condition. Default is None.

        Examples
        --------
        ```
        @botamino.on_event("on_youtube_message")
        def test(data: Parameters) -> None:
            print(data.message)
        ```

        """
        self.add_category("on_event")
        self.add_condition("on_event")
        events: list[MediaType | MessageType] = []
        for event_name in set(
            [name] if isinstance(name, (str, MessageType, MediaType)) else name
        ):
            if isinstance(event_name, str):
                try:
                    event = DEPRECATED_EVENTS[event_name]
                except KeyError:
                    raise ValueError("Invalid %r event name" % event_name) from None
            elif isinstance(event_name, (MediaType, MessageType)):  # type: ignore
                event = event_name
            else:
                raise ValueError(
                    "Expected a MessageType, MediaType or event name, not %s"
                    % event_name
                )
            events.append(event)
        if callable(condition):
            validate_lite_callback(condition)
            for key in events:
                self.conditions["on_event"][key] = condition

        def inner(callback: LiteCallbackT) -> LiteCallbackT:
            validate_lite_callback(callback)
            for key in events:
                self.commands["on_event"][key] = callback
            return callback

        return inner
