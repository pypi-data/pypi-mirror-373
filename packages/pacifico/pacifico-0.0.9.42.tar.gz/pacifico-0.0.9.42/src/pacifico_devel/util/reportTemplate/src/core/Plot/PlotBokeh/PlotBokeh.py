import abc
import pathlib as pth
import bokeh.io as bio
import pandas as pd
import typing as typ
import bokeh.plotting as bpl
import bokeh.models as bm
from bokeh.plotting import output_file, show

import pacifico_devel.util.reportTemplate.src.util.CONFIG as CFG

import pacifico_devel.util.reportTemplate.src.core.Plot.Plot as bplt


class PlotBokeh(bplt.Plot, metaclass=abc.ABCMeta):
    """
    Abstract class for all necessary plots made with Bokeh Backend.
    """
    _BOKEH_THEME_PATH = CFG.PATH_BOKEH_THEME

    # @property
    # def _theme_path(self):
    #     return self._BOKEH_THEME_PATH

    def saveImage(self) -> None:
        """


        Args:
            dfTranslated:

        Returns:

        """
        output_file("Plot.html")  # Was Necessary.
        chart = self._makeChart()
        print(self.pathImage)
        bio.export_png(chart,
                       filename=self.pathImage)
        print(self.pathImage)

    @abc.abstractmethod
    def _makeChart(self) -> typ.Union[bpl.Figure, bm.DataTable]:
        """
        Makes chart.

        Args:
            dfTranslated:

        Returns:

        """
        pass

    def df_to_excel(self, writer, tag):
        """
        saves DataFrame to excel
        Returns:

        """
        self.df.to_excel(writer, sheet_name=tag)
