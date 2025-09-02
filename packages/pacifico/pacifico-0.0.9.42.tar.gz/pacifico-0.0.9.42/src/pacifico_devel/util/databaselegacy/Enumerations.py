import enum
import typing as typ


class DataBase(enum.Enum):
    External_Data = enum.auto()
    External_Data_Raw = enum.auto()
    Inflacion = enum.auto()
    Tasas = enum.auto()
    mx = enum.auto()
    mx2 = enum.auto()
    postgres = enum.auto()
    webmonitor = enum.auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    def options(cls) -> typ.List[str]:
        return [db.name for db in cls]


if __name__ == '__main__':
    print(DataBase.options())

    # print(DataBase.External_Data)
