from typing import Any, Callable, Dict, Iterable, List, Optional, Union
from .parameters import Parameters
from .typing import (
    CallbackCategory,
    Callback,
    CallbackT,
    Condition,
    Events,
    LiteCallback,
    LiteCallbackT
)

__all__ = ('Command',)


class Command:
    def __init__(self) -> None:
        self.commands: Dict[CallbackCategory, Dict[str, Union[Callback, LiteCallback]]]
        self.conditions: Dict[CallbackCategory, Dict[str, Condition]]
    def execute(self, name: str, data: Parameters, category: CallbackCategory = "command") -> Any: ...
    def categorie_exist(self, category: CallbackCategory) -> bool: ...
    def add_categorie(self, category: CallbackCategory) -> None: ...
    def add_condition(self, category: CallbackCategory) -> None: ...
    def commands_list(self) -> List[str]: ...
    def answer_list(self) -> List[str]: ...
    def command(self, name: Optional[Union[str, Iterable[str]]] = None, condition: Optional[Condition] = None) -> Callable[[CallbackT], CallbackT]: ...
    def answer(self, name: Optional[Union[str, Iterable[str]]] = None, condition: Optional[Condition] = None) -> Callable[[CallbackT], CallbackT]: ...
    def on_member_join_chat(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_member_leave_chat(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_message(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_other(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_delete(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_remove(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_all(self, condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
    def on_event(self, name: Union[Iterable[Events], Events], condition: Optional[Condition] = None) -> Callable[[LiteCallbackT], LiteCallbackT]: ...
