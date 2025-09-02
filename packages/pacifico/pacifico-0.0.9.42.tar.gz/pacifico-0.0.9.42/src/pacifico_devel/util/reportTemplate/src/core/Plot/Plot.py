# from abc import ABCMeta, abstractmethod
import abc
import dataclasses
import pathlib as pth
# import bokeh.io as bio
import pandas as pd
# import pandas.api.types as pdt
import typing as typ
import dataclasses as dtc
# import dataframe_image as dfi
# import altair as alt
import chromedriver_autoinstaller

# import bokeh.plotting as bpl
# import bokeh.models as bm
# import altair.vegalite.v4.api as altapi
# import pandas.io.formats.style as pdst

from pacifico_devel.util.reportTemplate.src.core.Style.Style import Style
import pacifico_devel.util.reportTemplate.src.util.Enumerations as renm

# import pacifico_devel.util.lexikon.src.core.Translator as trl
import pacifico_devel.util.reportTemplate.src.util.Translation.DataFrame as tldf
import pacifico_devel.util.lexikon.src.util.Enumerations as lenm

from pacifico_devel.util.reportTemplate.src.util.Patches import ScreenshotPatch
import pacifico_devel.util.reportTemplate.src.util.CONFIG as CFG

import pacifico_devel.util.lexikon.src.core.Translator as trl


# MultiDisplay = typ.Union[bpl.Figure, bm.DataTable, altapi.Chart, pdst.Styler]

@dtc.dataclass(frozen=True)
class ImagePathHandler:
    """
    Class for handling image paths.
    """

    temp_root: pth.Path

    def makePathImage(self) -> pth.Path:
        idxMax = self._getMaximumDigit()

        if idxMax is None:
            plotIdx = 0
        else:
            plotIdx = idxMax + 1

        fileName = f"plot_{plotIdx}.png"
        return self.temp_root / fileName

    def _getMaximumDigit(self) -> typ.Optional[int]:
        digits = [self._digitFromFileName(filePath.stem)
                  for filePath in self.temp_root.glob("*.png")]
        digits = [x
                  for x in digits
                  if x is not None]
        if len(digits) > 0:
            return max(digits)
        return None

    @staticmethod
    def _digitFromFileName(s: str) -> typ.Optional[int]:
        base = s.split("_")[-1]
        if base.isnumeric():
            return int(base)
        return None


class Plot(metaclass=abc.ABCMeta):
    """
    Abstract class for all necessary plots
    """
    _IMAGE_PATH_HANDLER: ImagePathHandler = ImagePathHandler(CFG.ROOT_TEMP_IMG_PLOTS)
    _DATE_TIME_FORMAT = lenm.Language.English_US.dateFormatString()

    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[Style] = None):
        self._df = trl.Translator.translate_dataframe(df=df,
                                                      languageInput=languageInput,
                                                      languageOutput=languageOutput)
        self._base_resolution = basePlotResolution

        self._shape = tuple(int(dim * self._base_resolution)
                            for dim in shape
                            )  # might be changed # TO DO: adapt to bokeh as well.
        self._languageInput = languageInput
        self._languageOutput = languageOutput
        self._style = style
        self._pathImage = self._IMAGE_PATH_HANDLER.makePathImage()  # self._makePathImage()

    @property
    def pathImage(self) -> pth.Path:
        return self._pathImage

    @property
    def df(self) -> pd.DataFrame:
        """

        Returns: dataframe of plot, translated.

        """
        return self._df

    def deleteImage(self) -> None:
        """
        Deletes plot image file.

        Returns:

        """
        self._pathImage.unlink()



    # def makeImage(self) -> pth.Path:
    #     """
    #     Translates dataframe and saves image of chart from dataframe. Finally, saves path to image
    #
    #     Returns:
    #
    #     """
    #     self._saveImage(self._pathImage)
    #     return self._pathImage

    @abc.abstractmethod
    def saveImage(self) -> None:
        """
        Saves image of chart from dataframe.

        Returns:

        """
        pass

    @abc.abstractmethod
    def df_to_excel(self, writer, tag):
        """
        saves DataFrame to excel
        Returns:

        """
        pass

    # def set_in_report(self,
    #                   report,
    #                   tag,
    #                   shape) -> None:
    #     self.saveImage()
    #     report.setImage(tag=tag,
    #                     path=self.pathImage,
    #                     width=shape[0],
    #                     height=shape[1])
    #     report.set_temp_plot(tag, self)


if __name__ == '__main__':
    print("/n")
    p = pth.Path(__file__).parent / "tmp"
    print(p)
    for x in p.glob("*.png"):
        print(x)

    # p = Plot(...)
    #
    # data = p.df
    #
    # new_data = get_new_data(...)
    # p.df = new_data
