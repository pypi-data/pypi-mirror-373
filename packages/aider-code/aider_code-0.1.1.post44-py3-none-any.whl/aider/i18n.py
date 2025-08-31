import json
import importlib


class I18n:
    def __init__(self, lang="ko"):
        lang = lang.lower()
        lang = "ko" if any(x in lang for x in ["ko", "kr", "korea"]) else "en"
        with (
            importlib.resources.files("aider.locales")
            .joinpath(f"{lang}.json")
            .open("r", encoding="utf-8") as f
        ):
            self.translations = json.load(f)

    def t(self, key, **kwargs):
        tran_str = self.translations.get(key)
        if not tran_str:
            return key
        return tran_str.format(**kwargs)
