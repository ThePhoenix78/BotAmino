import collections.abc
# internal
from .parser import bind_callback, parse_args, validate_callback, validate_lite_callback

__all__ = ('Command',)


class Command:
    """Represents the chat message commands plugin (Base)"""

    def __init__(self):
        self.commands = {}
        self.conditions = {}

    def execute(self, name, data, category="command"):
        """Try to execute the specified command"""
        callback = self.commands[category][name]
        condition = self.conditions[category].get(name, None)
        if condition and not condition(data):
            return
        arguments = parse_args(data.message, data.subClient.client.parser_feature)
        args, kwargs = bind_callback(callback, data, arguments)
        return callback(*args, **kwargs)

    def categorie_exist(self, category):
        """Check if the given callback-category exists"""
        return category in self.commands

    def add_categorie(self, category):
        """Create the given callback-category"""
        if category not in self.commands:
            self.commands[category] = {}

    def add_condition(self, category):
        """Create condition for the given callback-category"""
        if category not in self.conditions:
            self.conditions[category] = {}

    def commands_list(self):
        """Get command list names"""
        return list(self.commands["command"])

    def answer_list(self):
        """Get answer list names"""
        return list(self.commands["answer"])

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
        self.add_categorie("command")
        self.add_condition("command")
        names = set([name] if isinstance(name, str) else list(name) if isinstance(name, collections.abc.Iterable) else [])
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
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
        self.add_categorie("answer")
        self.add_condition("answer")
        names = set([name] if isinstance(name, str) else list(name) if isinstance(name, collections.abc.Iterable) else [])
        if callable(condition):
            validate_lite_callback(condition)
        def inner(callback):
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
        self.add_categorie("on_member_join_chat")
        self.add_condition("on_member_join_chat")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_member_join_chat"]["on_member_join_chat"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_member_join_chat"]["on_member_join_chat"] = callback
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
        self.add_categorie("on_member_leave_chat")
        self.add_condition("on_member_leave_chat")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_member_leave_chat"]["on_member_leave_chat"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_member_leave_chat"]["on_member_leave_chat"] = callback
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
        self.add_categorie("on_message")
        self.add_condition("on_message")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_message"]["on_message"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_message"]["on_message"] = callback
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
        self.add_categorie("on_other")
        self.add_condition("on_other")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_other"]["on_other"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_other"]["on_other"] = callback
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
        self.add_categorie("on_delete")
        self.add_condition("on_delete")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_delete"]["on_delete"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_delete"]["on_delete"] = callback
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
        self.add_categorie("on_remove")
        self.add_condition("on_remove")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_remove"]["on_remove"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_remove"]["on_remove"] = callback
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
        self.add_categorie("on_all")
        self.add_condition("on_all")
        if callable(condition):
            validate_lite_callback(condition)
            self.conditions["on_all"]["on_all"] = condition
        def inner(callback):
            validate_lite_callback(callback)
            self.commands["on_all"]["on_all"] = callback
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
        self.add_categorie("on_event")
        self.add_condition("on_event")
        names = set(name if not isinstance(name, str) else [name])
        if callable(condition):
            validate_lite_callback(condition)
            for key in names:
                self.conditions["on_event"][key] = condition
        def inner(callback):
            validate_lite_callback(callback)
            for key in names:
                self.commands["on_event"][key] = callback
            return callback
        return inner
