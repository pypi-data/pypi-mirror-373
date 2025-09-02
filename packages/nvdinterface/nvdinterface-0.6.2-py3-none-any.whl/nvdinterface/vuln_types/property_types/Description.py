from iso639 import Lang


class Description:

    def __init__(self, lang: str, value: str):
        self._lang = Lang(lang)
        self._value = value

    @property
    def content(self):
        return self._value

    @property
    def language(self):
        return self._lang.pt1
