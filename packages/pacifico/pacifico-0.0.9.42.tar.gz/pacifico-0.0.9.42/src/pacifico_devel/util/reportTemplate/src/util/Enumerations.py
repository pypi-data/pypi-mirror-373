from enum import Enum, auto
import pathlib as pth


class PlotKind(Enum):
    LINE_PLOT = auto()
    BAR_PLOT = auto()
    TABLE_PLOT = auto()
    MULTI_BAR_PLOT = auto()


class Backend(Enum):
    BOKEH = auto()
    ALTAIR = auto()


class BokehTheme(Enum):
    THEME_1 = auto()
    THEME_2 = auto()

    @property
    def path(self) -> pth.Path:
        if self is self.__class__.THEME_1:
            return pth.Path(__file__).parents[1] / "core" / "Style" / "bokeh_themes" / "pacifico_theme.yml"
        elif self is self.__class__.THEME_2:
            # INSERT PATH HERE
            pass


if __name__ == '__main__':
    bt = BokehTheme.THEME_1
    print(bt.path)
    print(bt.path.is_file())
