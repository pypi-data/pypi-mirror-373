class Library:
    def __init__(self, root_path: str):
        self.system = "ISO 639-1"
        self.version = "2007"

    def load(self) -> None:
        pass

    def code(self, decode: str) -> tuple[str | None, str | None]:
        return self._get_code(decode)

    def decode(self, code: str) -> tuple[str | None, str | None]:
        return self._get_decode(code)

    def code_or_decode(self, text: str) -> tuple[str | None, str | None]:
        code, name = self._get_decode(text)
        if not code:
            code, name = self._get_code(text)
        return code, name

    def _get_decode(self, code: str) -> tuple[str | None, str | None]:
        # Just support "en" for the moment
        return ("en", "English") if code == "en" else (None, None)

    def _get_code(self, decode: str) -> tuple[str | None, str | None]:
        # Just support "en" for the moment
        return ("en", "English") if decode.upper() == "ENGLISH" else (None, None)
