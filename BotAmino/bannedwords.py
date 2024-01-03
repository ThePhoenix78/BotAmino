# python future feature compatibility (v3.10)
from __future__ import annotations
# native packages
from typing import TYPE_CHECKING
from unicodedata import normalize
from string import punctuation
from contextlib import suppress
# only type-checkers
if TYPE_CHECKING:
    from .parameters import Parameters

__all__ = ('BannedWords',)


class BannedWords:
    def filtre_message(self, message: str, encoding: str) -> str:
        """filter characters of the specified encoding from the message"""
        return normalize('NFD', message).encode(encoding, 'ignore').decode("utf8").strip().lower().translate(str.maketrans("", "", punctuation))

    def check_banned_words(self, data: Parameters, staff: bool = False) -> None:
        """Delete the message if it contains a banned word"""
        banned_words = set()
        for encoding in ("ascii", "utf8"):
            words = set(filter(lambda w: w in data.subClient.banned_words, self.filtre_message(data.message, encoding).split()))
            if words:
                banned_words.update(words)
        if banned_words:
            with suppress(Exception):
                data.subClient.delete_message(
                    data.chatId,
                    data.messageId,
                    reason=f"Banned word : %s" % ', '.join(banned_words),
                    asStaff=staff
                )
