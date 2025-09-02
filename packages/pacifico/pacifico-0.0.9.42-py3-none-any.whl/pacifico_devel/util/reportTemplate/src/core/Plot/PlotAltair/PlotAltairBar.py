import typing as typ
import pandas as pd
import altair as alt

import pacifico_devel.util.reportTemplate.src.core.Plot.PlotAltair.PlotAltair as plta
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.lexikon.src.core.Translator as trl


class PlotAltairBar(plta.PlotAltair):
    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotAltairBar, self).__init__(df=df, shape=shape, languageInput=languageInput,
                                            languageOutput=languageOutput, basePlotResolution=basePlotResolution,
                                            style=style)
        self._title = title

    def _makeChart(self) -> alt.Chart:
        categoriesColumn = self.df.columns[0]
        valuesColumn = self.df.columns[1]

        self.df["barchart_color"] = self.df[valuesColumn].apply(self._colorMap)

        chart = alt.Chart(self.df).mark_bar().encode(x=valuesColumn,
                                                     y=alt.Y(categoriesColumn, sort="-x"),
                                                     color=alt.Color("barchart_color:N", scale=None))
        chart = chart.properties(title=self._title,
                                 width=self._shape[0],
                                 height=self._shape[1])
        return chart

    @staticmethod
    def _colorMap(x: float):
        if x > 0:
            return pc.PacificoPlotColors.BLUE.getCodeString()
        return pc.PacificoPlotColors.PINK.getCodeString()
