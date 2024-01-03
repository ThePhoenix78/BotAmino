# python future feature compatibility (v3.10)
from __future__ import annotations
# native packages
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    TypeVar,
    Union,
    TYPE_CHECKING
)
from inspect import signature
# internal
from .utils import CallbackCategory, Events
# only type-checkers
if TYPE_CHECKING:
    from .parameters import Parameters

__all__ = ('Command',)

CommandFuncT = TypeVar('CommandFuncT', bound=Callable)


class Command:
    """Represents the chat message commands plugin (Base)"""

    def __init__(self) -> None:
        self.commands: Dict[CallbackCategory, Dict[str, Union[Callable[[Parameters], Any], Callable[..., Any]]]] = {}
        self.conditions: Dict[CallbackCategory, Dict[str, Callable[[Parameters], bool]]] = {}

    def execute(self, name: str, data: Parameters, category: CallbackCategory = "command"):
        """Try to execute the specified command"""
        callback = self.commands[category][name]
        condition = self.conditions[category].get(name, None)
        if condition and not condition(data):
            return
        sign = signature(callback)
        arguments = data.message.split()[0: len(sign.parameters)-1]
        extra = sign.bind_partial(data, *arguments)
        extra.apply_defaults()
        return callback(data, **extra.arguments)

    def categorie_exist(self, category: CallbackCategory) -> bool:
        """Check if the given callback-category exists"""
        return category in self.commands

    def add_categorie(self, category: CallbackCategory) -> None:
        """Create the given callback-category"""
        if category not in self.commands:
            self.commands[category] = {}

    def add_condition(self, category: CallbackCategory) -> None:
        """Create condition for the given callback-category"""
        if category not in self.conditions:
            self.conditions[category] = {}

    def commands_list(self) -> List[str]:
        """Get command list names"""
        return list(self.commands["command"])

    def answer_list(self) -> List[str]:
        """Get answer list names"""
        return list(self.commands["answer"])

    def command(self, name: Optional[Union[str, Iterable[str]]] = None, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "command"
        self.add_categorie(category)
        self.add_condition(category)
        names = set([name] if isinstance(name, str) else list(name) if isinstance(name, Iterable) else [])
        def add_command(callback: CommandFuncT) -> CommandFuncT:
            if not names:
                names.add(callback.__name__)
            if callable(condition):
                for command in names:
                    self.conditions[category][command] = condition
            for command in names:
                self.commands[category][command.lower()] = callback
            return callback
        return add_command

    def answer(self, name: Optional[Union[str, Iterable[str]]] = None, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "answer"
        self.add_categorie(category)
        self.add_condition(category)
        names = set([name] if isinstance(name, str) else list(name) if isinstance(name, Iterable) else [])
        def add_answer(callback: CommandFuncT) -> CommandFuncT:
            if not names:
                names.add(callback.__name__)
            if callable(condition):
                for command in names:
                    self.conditions[category][command] = condition
            for command in names:
                self.commands[category][command.lower()] = callback
            return callback
        return add_answer

    def on_member_join_chat(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_member_join_chat"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_member_leave_chat(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_member_leave_chat"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_message(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_message"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_other(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_other"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_delete(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_delete"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_remove(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_remove"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_all(self, condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_all"
        self.add_categorie(category)
        self.add_condition(category)
        if callable(condition):
            self.conditions[category][category] = condition
        def add_command(func: CommandFuncT) -> CommandFuncT:
            self.commands[category][category] = func
            return func
        return add_command

    def on_event(self, name: Union[Events, Iterable[Events]], condition: Optional[Callable[[Parameters], bool]] = None) -> Callable[[CommandFuncT], CommandFuncT]:
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
        category = "on_event"
        self.add_categorie(category)
        self.add_condition(category)        
        names = set([name] if isinstance(name, str) else list(name) if isinstance(name, Iterable) else [])
        def add_command(func: CommandFuncT) -> CommandFuncT:
            if callable(condition):
                for command in names:
                    self.conditions[category][command] = condition
            for command in name:
                self.commands[category][command] = func
            return func
        return add_command
