import collections.abc
# internal
from .parser import (
    bind_callback,
    parse_args,
    validate_callback,
    validate_lite_callback
)

__all__ = ('CallbackInfo', 'CommandHandler',)


class CallbackInfo:
    def __init__(
        self,
        names,
        callback,
        condition
    ):
        self.names = set(name.lower() for name in names)
        self.callback = callback
        self.condition = condition

    def __hash__(self):
        return hash((*self.names, self.callback, self.condition))

    def __eq__(self, value: object) -> bool:
        if isinstance(value, CallbackInfo):
            return self.callback == value.callback
        return value in self

    def __contains__(self, key):
        return (key.lower() if isinstance(key, str) else key) in self.names


class CommandHandler:
    """Represents the chat message commands plugin (Base)"""

    def __init__(self):
        self.callbacks = {}

    def execute(self, name, data, category="command"):
        """Try to execute the specified command"""
        category = self.get_category(category)
        callback, condition = None, None
        for callback_info in category:
            if name not in callback_info:
                continue
            callback, condition = callback_info.callback, callback_info.condition
        if callback is None:
            return
        if condition and not condition(data):
            return
        arguments = parse_args(data.message, data.subClient.client.parser_feature)
        args, kwargs = bind_callback(callback, data, arguments)
        return callback(*args, **kwargs)

    def category_exist(self, category):
        """Check if the given callback-category exists"""
        return category in self.callbacks

    def get_category(self, category):
        """Get a callback-category"""
        self.add_category(category)
        return self.callbacks[category]

    def add_category(self, category):
        """Create the given callback-category"""
        if category not in self.callbacks:
            self.callbacks[category] = set()

    def commands_list(self):
        """Get command list names"""
        return list(self.get_category("command"))

    def answer_list(self):
        """Get answer list names"""
        return list(self.get_category("answer"))

    def get_command_info(self, name):
        for callback in filter(lambda command: name in command, self.commands_list()):
            return callback

    def get_answer_info(self, name):
        for callback in filter(lambda answer: name in answer, self.answer_list()):
            return callback

    def command(self, name=None, condition=None):
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
        names = set([name] if isinstance(name, str) else [] if name is None else list(name))
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_callback(callback)
            if not names:
                names.add(callback.__name__)
            self.get_category("command").add(CallbackInfo(names, callback, condition))
            return callback
        return inner

    def answer(self, name=None, condition=None):
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
        names = set([name] if isinstance(name, str) else [] if name is None else list(name))
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_callback(callback)
            if not names:
                names.add(callback.__name__)
            self.get_category("answer").add(CallbackInfo(names, callback, condition))
            return callback
        return inner

    def on_member_join_chat(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_member_join_chat").add(CallbackInfo(["on_member_join_chat"], callback, condition))
            return callback
        return inner

    def on_member_leave_chat(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_member_leave_chat").add(CallbackInfo(["on_member_leave_chat"], callback, condition))
            return callback
        return inner

    def on_message(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_message").add(CallbackInfo(["on_message"], callback, condition))
            return callback
        return inner

    def on_other(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_other").add(CallbackInfo(["on_other"], callback, condition))
            return callback
        return inner

    def on_delete(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_delete").add(CallbackInfo(["on_delete"], callback, condition))
            return callback
        return inner

    def on_remove(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_remove").add(CallbackInfo(["on_remove"], callback, condition))
            return callback
        return inner

    def on_all(self, condition=None):
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
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_all").add(CallbackInfo(["on_all"], callback, condition))
            return callback
        return inner

    def on_event(self, name, condition=None):
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
        names = set(name if not isinstance(name, str) else [name])
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
            validate_lite_callback(callback)
            self.get_category("on_event").add(CallbackInfo(names, callback, condition))
            return callback
        return inner
