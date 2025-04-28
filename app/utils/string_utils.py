import unicodedata
import re


class StringUtils:
    @staticmethod
    def sanitize_filename(text: str) -> str:
        """
        Replace smart quotes and non-ASCII characters with ASCII
        :param text:
        :return: str
        """
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
        ascii_text = re.sub(r"[^a-zA-Z0-9_.-]", "_", ascii_text)
        return ascii_text


