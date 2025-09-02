import datetime as dt
import pathlib as pth
import typing as typ

from pacifico_devel.util.lexikon.src.util.Enumerations import Language


class Style:  # make abstract
    """
    Analogue to CSS?
    """
    _CSS_DEFAULT_PATH: pth.Path = pth.Path(__file__).parent.parent / "css" / "pacifico.css"

    def __init__(self,
                 cssPath: typ.Union[pth.Path, str] = _CSS_DEFAULT_PATH):
        self._cssPath = cssPath

    @staticmethod
    def _processIntegerPart(value: float,
                            language: Language) -> str:
        """
        Does formatting of integer part of float.

        Args:
            value:
            language:

        Returns:

        """
        absVal = abs(value)
        integer = str(int(absVal))

        reversedIntegerString = ""

        for i, char in enumerate(integer[::-1]):
            if i % 3 == 0 and i != 0:
                reversedIntegerString += language.thousandsSeparator()
            reversedIntegerString += char
        return reversedIntegerString[::-1]

    @staticmethod
    def _processDecimalPart(value: float,
                            numberDecimals: int) -> str:
        """
        Does processing of decimal part of float.

        Args:
            value:
            numberDecimals:

        Returns:

        """
        if numberDecimals < 0:
            raise ValueError(f"Number of decimals must be a positive integer, but is {numberDecimals}.")

        absVal = abs(value)
        if "." in str(absVal):
            decimalString: str = str(absVal).split(".")[-1]
        else:
            decimalString: str = ""

        if numberDecimals > len(decimalString):
            decimalString += "0" * (numberDecimals - len(decimalString))

        return decimalString[:numberDecimals]

    @classmethod
    def convertFloatToString(cls,
                             value: float,
                             numberDecimals: int,
                             language: Language) -> str:
        """
        Takes double and returns typical format of language. Ex: 1234.5678, EN -> 1,234.5678, [...]
        Use package that does this.

        Args:
            value:
            numberDecimals:
            language:

        Returns:

        """
        sign = "-" if value < 0 else ""

        integerPart = cls._processIntegerPart(value,
                                              language)

        if numberDecimals == 0:
            return sign + integerPart
        decimalPart = cls._processDecimalPart(value,
                                              numberDecimals)
        return sign + integerPart + language.decimalSeparator() + decimalPart

    @classmethod
    def convertIntToString(cls,
                           value: int,
                           language: Language) -> str:
        """
        Trivial. [excercise left to the reader]

        Args:
            value:
            language:

        Returns:

        """
        return cls.convertFloatToString(value=value,
                                        numberDecimals=0,
                                        language=language)

    @classmethod
    def convertDateTimeToString(cls,
                                value: dt.datetime,
                                language: Language) -> str:
        """
        Same same, but different (with dates). EN -> MM/DD/YYYY [...], LOCALE for hour.

        Args:
            value:
            language:

        Returns:

        """
        timeFormat = language.dateFormatString() + " %H:%M:%S"

        return value.strftime(timeFormat)

    @classmethod
    def convertDateToString(cls,
                            value: dt.date,
                            language: Language) -> str:
        """
        Same as previous.

        Args:
            value:
            language:

        Returns:

        """
        # return value.strftime(fmt="%d/%m/%Y")
        return value.strftime(language.dateFormatString())

    @classmethod
    def convertDateMonthToString(cls,
                                 value: dt.date,
                                 language: Language) -> str:
        """
        Either MM/YYYY or 'jun 2018'. For the moment, only first convention.

        Args:
            value:
            language:

        Returns:

        """
        formatString = language.dateSeparator().join(["%m", "%Y"])
        return value.strftime(formatString)

    @classmethod
    def convertDateQuarterToString(cls,
                                   value: dt.date,
                                   language: Language) -> str:
        """
        EN -> Q2/2018/.

        Args:
            value:
            language:

        Returns:

        """
        quarter = value.month // 3 + 1
        return "Q" + str(quarter) + language.dateSeparator() + str(value.year)

    @classmethod
    def convertDateYearToString(cls,
                                value: dt.date) -> str:
        return str(value.year)

    def getCss(self):
        """

        Returns: CSS corresponding to this style.

        """
        pass


if __name__ == '__main__':
    sty = Style()
    s = sty.convertFloatToString(value=1234567891.23,
                                 numberDecimals=1,
                                 language=Language.English_US)
    print(s)

    date = dt.date(year=2019, month=5, day=27)
    # ds = sty.convertDateMonthToString(date, language=Language.English_US)
    # ds = sty.convertDateQuarterToString(date, language=Language.English_US)
    ds = sty.convertDateToString(date, language=Language.German)

    for lang in Language:
        print(f"{lang.name}: {sty.convertDateToString(date, language=lang)}")

    # print(sty.convertDateToString(date, language=Language.German))
    # print(sty.convertDateToString(date, language=Language.English_US))
