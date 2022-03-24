from inspect import getfullargspec


class Command:
    def __init__(self):
        self.commands = {}
        self.conditions = {}

    def execute(self, commande, data, type: str = "command"):
        com = self.commands[type][commande]
        arg = getfullargspec(com).args
        arg.pop(0)
        s = len(arg)
        dico = {}
        if s:
            dico = {key: value for key, value in zip(arg, data.message.split()[0:s])}

        if self.conditions[type].get(commande, None):
            if self.conditions[type][commande](data):
                return self.commands[type][commande](data, **dico)
            return
        return self.commands[type][commande](data, **dico)

    def categorie_exist(self, type: str):
        return type in self.commands.keys()

    def add_categorie(self, type):
        if type not in self.commands.keys():
            self.commands[type] = {}

    def add_condition(self, type):
        if type not in self.conditions.keys():
            self.conditions[type] = {}

    def commands_list(self):
        return [command for command in self.commands["command"].keys()]

    def answer_list(self):
        return [command for command in self.commands["answser"].keys()]

    def command(self, name=None, condition=None):
        type = "command"
        self.add_categorie(type)
        self.add_condition(type)
        if isinstance(name, str):
            name = [name]
        elif not name:
            name = []

        def add_command(command_funct):
            name.append(command_funct.__name__)
            if callable(condition):
                for command in name:
                    self.conditions[type][command] = condition
            for command in name:
                self.commands[type][command.lower()] = command_funct
            return command_funct

        return add_command

    def answer(self, name, condition=None):
        type = "answer"
        self.add_categorie(type)
        self.add_condition(type)

        if isinstance(name, str):
            name = [name]
        elif not name:
            name = []

        def add_command(command_funct):
            # name.append(command_funct.__name__)
            if callable(condition):
                for command in name:
                    self.conditions[type][command] = condition

            for command in name:
                self.commands[type][command.lower()] = command_funct
            return command_funct

        return add_command

    def on_member_join_chat(self, condition=None):
        type = "on_member_join_chat"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_member_leave_chat(self, condition=None):
        type = "on_member_leave_chat"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_message(self, condition=None):
        type = "on_message"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_other(self, condition=None):
        type = "on_other"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_delete(self, condition=None):
        type = "on_delete"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_remove(self, condition=None):
        type = "on_remove"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_all(self, condition=None):
        type = "on_all"
        self.add_categorie(type)
        self.add_condition(type)
        if callable(condition):
            self.conditions[type][type] = condition

        def add_command(command_funct):
            self.commands[type][type] = command_funct
            return command_funct
        return add_command

    def on_event(self, name, condition=None):
        type = "on_event"
        self.add_categorie(type)
        self.add_condition(type)

        if isinstance(name, str):
            name = [name]
        elif not name:
            name = []

        def add_command(command_funct):
            # name.append(command_funct.__name__)
            if callable(condition):
                for command in name:
                    self.conditions[type][command] = condition

            for command in name:
                self.commands[type][command] = command_funct
            return command_funct

        return add_command
