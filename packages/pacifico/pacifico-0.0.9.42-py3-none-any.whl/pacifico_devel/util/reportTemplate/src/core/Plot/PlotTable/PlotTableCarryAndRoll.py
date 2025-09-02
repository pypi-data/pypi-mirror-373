import pandas as pd
import typing as typ
import pathlib as pth
import dataframe_image as dfi
import pandas.io.formats.style as pdst

import pacifico_devel.util.reportTemplate.src.core.Plot.Plot as bplt
# from pacifico_devel.util.reportTemplate.src.core.Plot.Table.Table import Table
# from pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors import PacificoPlotColors
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc
# import pacifico_devel.util.reportTemplate.src.util.Enumerations as renm
from pacifico_devel.util.reportTemplate.src.util.Patches import ScreenshotPatch

import pacifico_devel.util.reportTemplate.src.core.Plot.PlotAltair.PlotAltair as plta
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.lexikon.src.core.Translator as trl


# TO DO: Implement formatter

class PlotTableCarryAndRoll(bplt.Plot):
    def __init__(self,
                 df: pd.DataFrame,
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 shape: typ.Tuple[float, float],
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 formatter: typ.Optional[typ.Dict[str, str]] = None):
        super(PlotTableCarryAndRoll, self).__init__(df=df,
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
                   ("color", "#330099"),
                   ('text-align', 'center'),
                   ('font-size', '12pt')]

        index_col = {'selector': 'th.col_heading',
                     'props': [('background-color', "#330099"),
                               ('font-family', 'Klartext Mono'),
                               ('color', 'white'),
                               ('text-align', 'center'),
                               ('font-size', '12pt')]}
        index_col_level0 = {'selector': 'th.col_heading.level0',
                            'props': [('border-right', '3px solid #ffffff')]}

        index_col_level1 = {'selector': 'th.col_heading.level1',
                            'props': [('border-right', '3px solid #ffffff')]}

        index_col_level2 = {'selector': 'th.col_heading.level2',
                            'props': [('border-bottom', '3px solid #ffffff')]}

        indexName = {'selector': 'th.blank.level2',
                     'props': [('background-color', "#330099"),
                               ('border-bottom', '3px solid #ffffff')]}
        cols = []
        index = 1
        last = 1
        for col in range(len(self.df.columns)):
            if index <= len(self.df.columns):
                if col == 0:
                    cols.append({'selector': 'th.col_heading.level1.col0',
                                 'props': [('border-right', '0px solid #ffffff')]})
                else:
                    cols.append({'selector': '.col{}'.format(index),
                                 'props': [('border-right', '3px solid #ffffff')]})
                    if last == 1:
                        index += 3
                        last = 3
                    elif last == 3:
                        index += 1
                        last = 1

        dfst = self.df.style.set_table_styles([{"selector": "th", "props": thProps},
                                               {"selector": "td.data", "props": tdProps},
                                               indexName,
                                               index_col,
                                               index_col_level0,
                                               index_col_level1,
                                               index_col_level2] + cols).hide_index()
        if self._formatter is None:
            dfst = dfst.format(lambda x: "{:.2f}".format(x) if isinstance(x, float) else '{}'.format(x), na_rep='')
        else:
            dfst = dfst.format(self._formatter, na_rep='')
        return dfst

    def df_to_excel(self, writer, tag):
        """
        saves DataFrame to excel
        Returns:

        """

        self.df.to_excel(writer, sheet_name=tag)
