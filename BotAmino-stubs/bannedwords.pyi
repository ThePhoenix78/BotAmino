from .parameters import Parameters

__all__ = ('BannedWords',)


class BannedWords:
    def filtre_message(self, message: str, encoding: str) -> str: ...
    def check_banned_words(self, data: Parameters, staff: bool = False) -> None: ...
