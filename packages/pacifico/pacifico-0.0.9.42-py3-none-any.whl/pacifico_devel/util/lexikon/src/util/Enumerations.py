from enum import Enum, auto
from typing import List


class Language(Enum):
    Spanish = auto()
    English_US = auto()
    French = auto()
    German = auto()
    Japanese = auto()

    @classmethod
    def fromDeeplString(cls,
                        stringRepr: str):
        for lang in cls:
            if stringRepr in {lang.deeplStringInput, lang.deeplStringOutput}:
                return lang
        msg1 = f"Invalid string representation: {stringRepr}. "
        msg2 = f"It must be one of {[lang.deeplString for lang in cls]}."
        raise ValueError(msg1 + "\n" + msg2)

    @property
    def deeplStringInput(self) -> str:
        if self == Language.English_US:
            return "EN"
        return self.deeplStringOutput

    @property
    def deeplStringOutput(self) -> str:
        if self == Language.Spanish:
            return "ES"
        elif self == Language.English_US:
            return "EN-US"  # "EN-US"
        elif self == Language.French:
            return "FR"
        elif self == Language.German:
            return "DE"
        elif self == Language.Japanese:
            return "JA"

    def thousandsSeparator(self) -> str:
        """
        SOURCE: https://en.wikipedia.org/wiki/Decimal_separator

        Returns:

        """
        spaceSeparated = {Language.French,
                          Language.English_US,
                          Language.Spanish}
        dotSeparated = {Language.German}
        commaSeparated = {Language.Japanese}
        if self in spaceSeparated:
            return " "
        elif self in dotSeparated:
            return "."
        elif self in commaSeparated:
            return ","
        raise ValueError()

    def decimalSeparator(self) -> str:
        dotSeparated = {Language.Japanese, Language.English_US}
        commaSeparated = {Language.German, Language.Spanish, Language.French}
        if self in dotSeparated:
            return "."
        elif self in commaSeparated:
            return ","
        raise ValueError()

    def dateSeparator(self) -> str:
        slashSeparated: set = {Language.Spanish,
                               Language.French}
        dashSeparated: set = {Language.English_US,
                              Language.German,
                              Language.Japanese}
        if self in slashSeparated:
            return "/"
        elif self in dashSeparated:
            return "-"

        raise ValueError()

    def dateOrder(self) -> List[str]:
        descending = {Language.English_US,
                      Language.German,
                      Language.Japanese}

        ascending = {Language.Spanish,
                     Language.French}

        if self in ascending:
            return ["%d", "%m", "%Y"]
        elif self in descending:
            return ["%Y", "%d", "%m"]

        raise NotImplementedError(f"Language not Implemented. Please implement at {__file__}.")

    def dateFormatString(self) -> str:
        return self.dateSeparator().join(self.dateOrder())

    # def longDateFormat(self) -> str:
    #     locale.setlocale(locale.LC_TIME, (self.deeplString, "UTF-8"))
    #     return "%A %#d, %B %Y"


if __name__ == '__main__':
    # import datetime as dt
    #
    # lang = Language.Spanish
    #
    # dateString = dt.date.today().strftime(lang.longDateFormat())
    # print(dateString)
    # print(Language["English_US"])
    # locale.setlocale(locale.LC_TIME, (self.deeplString, "UTF-8"))
    print(Language(Language.Spanish))
