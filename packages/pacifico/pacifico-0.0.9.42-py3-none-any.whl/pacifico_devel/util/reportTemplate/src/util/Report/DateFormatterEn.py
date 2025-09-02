import typing as typ
import datetime as dt

multiDate = typ.Union[dt.date, dt.datetime]


class DateFormatterEn:
    _INT_TO_WEEKDAY_EN: typ.List[str] = ["Monday", "Tuesday", "Wednesday",
                                         "Thursday", "Friday", "Saturday",
                                         "Sunday"]
    _INT_TO_MONTH_EN: typ.List[str] = ["January", "Febuary", "March",
                                       "April", "May", "June",
                                       "July", "August", "September",
                                       "October", "November", "December"]
    _SUFFIX_TO_INDEX: typ.Dict[str, typ.Set[int]] = {"st": {1},
                                                     "nd": {2},
                                                     "rd": {3},
                                                     "th": set(range(4, 10)) | {0}
                                                     }

    @classmethod
    def getLongDateStringEn(cls, date) -> str:
        """

        Args:
            date:

        Returns: input date in long written format.

        """
        weekdayString = cls._INT_TO_WEEKDAY_EN[date.weekday()]
        monthString = cls._INT_TO_MONTH_EN[date.month - 1]
        return f"{weekdayString}, {monthString} {date.day}{cls._getSuffixEn(date)}, {date.year}"

    @classmethod
    def _getSuffixEn(cls, date: multiDate):
        """

        Args:
            date:

        Returns: english language suffix for the day of the date. ex: 31-9-2022 -> "th"

        """
        lastDigit = int(str(date.day)[-1])
        for suffix, intSet in cls._SUFFIX_TO_INDEX.items():
            if lastDigit in intSet:
                return suffix
        raise ValueError(f"Invalid date argument: {date}")


if __name__ == '__main__':
    t = dt.date(2022, 3, 30)
    print(DateFormatterEn.getLongDateStringEn(t))
