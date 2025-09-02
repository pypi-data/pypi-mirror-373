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

class PlotTablePositions(bplt.Plot):
    def __init__(self,
                 df: pd.DataFrame,
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 shape: typ.Tuple[float, float],
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 formatter: typ.Optional[typ.Dict[str, str]] = None):
        super(PlotTablePositions, self).__init__(df=df,
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
                   ('font-size', '14pt')]

        index_col = {'selector': 'th.col_heading',
                     'props': [('background-color', "#330099"),
                               ('font-family', 'Klartext Mono'),
                               ('color', 'white'),
                               ('text-align', 'center'),
                               ('font-size', '16pt')]}

        dfst = self.df.style.set_table_styles([{"selector": "th.blank", "props": thProps},
                                               {"selector": "td", "props": tdProps},
                                               index_col])
        dfst = dfst.set_properties(**{'width': '300px'}
                                   ).set_properties(subset=['Posición',
                                                            'Comentario'],
                                                    **{'text-align': 'justify'}
                                                    ).set_properties(subset=['Fecha de inicio',
                                                                             'Fecha de cierre',
                                                                             'Nivel de inicio',
                                                                             'Nivel de cierre',
                                                                             'Retorno a hoy',
                                                                             'Horizonte'
                                                                             ], **{'text-align': 'center'})
        dfst = dfst.hide_index()
        if self._formatter is None:
            dfst = dfst.format("{}")
        else:
            dfst = dfst.format(self._formatter)
        return dfst

    def df_to_excel(self, writer, tag):
        """
        saves DataFrame to excel
        Returns:

        """

        self.df.to_excel(writer, sheet_name=tag)