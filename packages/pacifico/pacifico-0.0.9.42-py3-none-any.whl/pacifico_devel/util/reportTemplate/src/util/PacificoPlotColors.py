from enum import Enum, auto
from typing import Tuple, Optional
import seaborn as sns


class PacificoPlotColors(Enum):
    """
    Class for geting colors of pacifico plots
    """
    PINK = auto()
    BLUE = auto()
    TURQUOISE = auto()
    METALIC_BLUE = auto()
    DARKER_GREY = auto()
    DARK_GREY = auto()
    YELLOW = auto()
    ORANGE = auto()
    GREEN = auto()
    LIGHT_GREY = auto()
    LIGHTER_GREY = auto()
    PURPLE = auto()

    def getCodeString(self) -> str or list:
        """
        Get CodeString for a given color.

        Returns:

        """
        if self is PacificoPlotColors.BLUE:
            return "#330099"
        if self is PacificoPlotColors.PINK:
            return "#FF2E66"
        if self == PacificoPlotColors.METALIC_BLUE:
            return "#27576e"
        if self is PacificoPlotColors.TURQUOISE:
            return "#00D3B1"
        if self == PacificoPlotColors.DARKER_GREY:
            return "#505050"
        if self is PacificoPlotColors.DARK_GREY:
            return "#636363"
        if self is PacificoPlotColors.YELLOW:
            return "#FFD700"
        if self is PacificoPlotColors.ORANGE:
            return "#FF663D"
        if self is PacificoPlotColors.GREEN:
            return "#2BC655"
        if self is PacificoPlotColors.LIGHT_GREY:
            return "#D2D2D2"
        if self == PacificoPlotColors.LIGHTER_GREY:
            return "#dcdcdc"
        if self == PacificoPlotColors.PURPLE:
            return "#505050"

    def getRgbTuple(self, normalize=False) -> Tuple[int]:
        """
        get RGB float tuple.

        Args:
            normalize:

        Returns:

        """
        if self is PacificoPlotColors.PINK:
            out = 255, 46, 102
        elif self is PacificoPlotColors.BLUE:
            out = 39, 19, 129
        elif self is PacificoPlotColors.TURQUOISE:
            out = 0, 21, 177
        elif self is PacificoPlotColors.DARK_GREY:
            out = 99, 99, 99
        elif self is PacificoPlotColors.YELLOW:
            out = 255, 215, 0
        elif self is PacificoPlotColors.ORANGE:
            out = 43, 298, 85
        elif self is PacificoPlotColors.GREEN:
            out = 43, 298, 85
        elif self is PacificoPlotColors.LIGHT_GREY:
            out = 210, 210, 210
        else:
            raise ValueError(f"Invalid PacificoPlotColors: {self}")

        if normalize:
            out = (score / 255 for score in out)
        return out

    @classmethod
    def setPallete(cls,
                   lenPallete: Optional[int] = None,
                   nColors: int = 3,
                   returnPallete=False) -> None:
        """
        Set pallete for seaborn plot.

        Args:
            lenPallete:
            nColors:
            returnPallete:

        Returns:

        """
        if lenPallete is None:
            lenPallete = nColors
        colorStrings = [color.getCodeString() for color in cls]
        pallete = sns.blend_palette(colorStrings[:nColors],
                                    n_colors=lenPallete)
        sns.set_palette(pallete)
        if returnPallete:
            return pallete


if __name__ == '__main__':
    print(PacificoPlotColors.DARK_GREY.getCodeString())