import unicodedata
import string
import contextlib

__all__ = ('BannedWords',)


class BannedWords:
    def filtre_message(self, message, encoding):
        """filter characters of the specified encoding from the message"""
        return unicodedata.normalize('NFD', message).encode(encoding, 'ignore').decode("utf8").strip().lower().translate(str.maketrans("", "", string.punctuation))

    def check_banned_words(self, data, staff=False):
        """Delete the message if it contains a banned word"""
        banned_words = set()
        for encoding in ("ascii", "utf8"):
            words = set(filter(lambda w: w in data.subClient.banned_words, self.filtre_message(data.message, encoding).split()))
            if words:
                banned_words.update(words)
        if banned_words:
            with contextlib.suppress(Exception):
                data.subClient.delete_message(
                    data.chatId,
                    data.messageId,
                    reason=f"Banned word : %s" % ', '.join(banned_words),
                    asStaff=staff
                )
