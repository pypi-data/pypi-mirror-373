import pandas as pd
import typing as typ
import pathlib as pth
import dataframe_image as dfi
import pandas.io.formats.style as pdst
import numpy as np
import matplotlib as mpl
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import pacifico_devel.util.reportTemplate.src.core.Plot.Plot as bplt
from pacifico_devel.util.reportTemplate.src.util.Patches import ScreenshotPatch
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.lexikon.src.core.Translator as trl


# TO DO: Implement formatter

class PlotTableOneColorMap(bplt.Plot):
    def __init__(self,
                 df: pd.DataFrame,
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 shape: typ.Tuple[float, float],
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 formatter: typ.Optional[typ.Dict[str, str]] = None):
        super(PlotTableOneColorMap, self).__init__(df=df,
                                                   shape=shape,
                                                   languageInput=languageInput,
                                                   languageOutput=languageOutput,
                                                   basePlotResolution=basePlotResolution,
                                                   style=style)
        self._formatter = formatter

    def saveImage(self) -> None:
        """


        Args:
            dfTranslated:

        Returns:

        """
        chart = self._makeChart()
        ScreenshotPatch.patch()  # Monkey patch for chrome screenshots server
        print(f"SAVING TABLE TO: {self.pathImage} ...")
        dfi.export(obj=chart,
                   filename=str(self.pathImage))
        print(f"SAVING TABLE TO: {self.pathImage} ... DONE!")

    def _makeChart(self) -> pdst.Styler:
        # dfAux = self._translateDataFrame(df)
        thProps = [("background-color", pc.PacificoPlotColors.BLUE.getCodeString())]

        tdProps = [('font-family', 'Klartext Mono'),
                   ("color", pc.PacificoPlotColors.BLUE.getCodeString()),
                   ('text-align', 'center'),
                   ('font-size', '12pt')]

        index_col = {'selector': 'th.col_heading',
                     'props': [('background-color', pc.PacificoPlotColors.BLUE.getCodeString()),
                               ('font-family', 'Klartext Mono'),
                               ('color', 'white'),
                               #('border-bottom', '3px solid #ffffff'),
                               ('text-align', 'center'),
                               ('font-size', '12pt')]}

        indexName = {'selector': 'th.blank',
                     'props': [('background-color', pc.PacificoPlotColors.BLUE.getCodeString())]}
        #('border-bottom', '3px solid #ffffff')

        splitCol = {'selector': '.col0',
                    'props': [('border-right', '5px solid #ffffff')]}

        index = {'selector': 'th.row_heading',
                 'props': [('background-color', pc.PacificoPlotColors.BLUE.getCodeString()),
                           ('font-family', 'Klartext Mono'),
                           ('color', 'white'),
                           #('border-right', '3px solid #ffffff'),
                           ('font-weight', 'bold')]}

        dfst = self.df.style.set_table_styles([{"selector": "th", "props": thProps},
                                               {"selector": "td.data", "props": tdProps},
                                               index,
                                               indexName,
                                               index_col,
                                               splitCol
                                               ]).hide_index()

        cmap = PlotTableOneColorMap.__makeColormap()
        dfst = dfst.background_gradient(cmap=cmap,
                                        axis=None
                                        ).highlight_null('white')

        if self._formatter is None:
            dfst = dfst.format(lambda x: "{:.2f}".format(x) if isinstance(x, float) else '{}'.format(x), na_rep='')
        else:
            dfst = dfst.format(self._formatter, na_rep='')
        return dfst

    @staticmethod
    def __colorFader(c1, c2, mix: float = 0):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        c1 = np.array(mpl.colors.to_rgb(c1))
        c2 = np.array(mpl.colors.to_rgb(c2))
        return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)

    @staticmethod
    def __makeColormap():
        color1 = []
        for i in range(1, 100 + 1):
            color1.append(
                PlotTableOneColorMap.__colorFader(pc.PacificoPlotColors.PINK.getCodeString(), "#ffffff", i / 100))
        color1 = color1[0:90]
        return ListedColormap(color1)

    def df_to_excel(self, writer, tag):
        """
        saves DataFrame to excel
        Returns:

        """

        self.df.to_excel(writer, sheet_name=tag)
    # @staticmethod
    # def make_gradient(value, min_value: float, max_value: float, cmap1, cmap2):
    #     """
    #     Parameters
    #     ----------
    #
    #     v: tuple of (word, length)
    #     min_length: int
    #         minimum length of all words in the matrix
    #     max_length: int
    #         maximum length of all words in the matrix
    #     cmap: matplotlib color map, default value here is 'YlGn'
    #
    #     Returns
    #     -------
    #
    #     string:
    #         CSS setting a colour
    #
    #     For Matplotlib colormaps:
    #     See: https://matplotlib.org/stable/tutorials/colors/colormaps.html
    # """
    #     if isinstance(value, float):
    #         if value <= 0:
    #             max_value = 0
    #             value = (value - min_value) / (max_value - min_value)
    #             rgba = cmap1(value)
    #         else:
    #             min_value = 0
    #             value = (value - min_value) / (max_value - min_value)
    #             rgba = cmap2(value)
    #         return f'background-color: {mpl.colors.rgb2hex(rgba)};'


