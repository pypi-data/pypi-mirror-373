import abc
import pathlib as pth
import pandas as pd
import altair as alt

import pacifico_devel.util.reportTemplate.src.core.Plot.Plot as bplt


class PlotAltair(bplt.Plot, metaclass=abc.ABCMeta):
    """
    Abstract class for all necessary plots made with Altair Backend.
    """

    def saveImage(self) -> None:
        """


        Args:
            dfTranslated:

        Returns:

        """
        chart = self._makeChart()
        chart.save(fp=self.pathImage)

    @abc.abstractmethod
    def _makeChart(self) -> alt.Chart:
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