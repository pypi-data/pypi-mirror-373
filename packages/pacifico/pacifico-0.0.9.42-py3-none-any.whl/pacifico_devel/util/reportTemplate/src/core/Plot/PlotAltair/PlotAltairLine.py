import typing as typ
import pandas as pd
import altair as alt

import pacifico_devel.util.reportTemplate.src.core.Plot.PlotAltair.PlotAltair as plta
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.lexikon.src.core.Translator as trl


## IDEA: collapse languageInput and languageOutput into one.


class PlotAltairLine(plta.PlotAltair):
    def __init__(self,
                 df: pd.DataFrame,
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 shape: typ.Tuple[float, float],
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotAltairLine, self).__init__(df=df,
                                             shape=shape,
                                             languageInput=languageInput,
                                             languageOutput=languageOutput,
                                             basePlotResolution=basePlotResolution,
                                             style=style)
        self._title = title

    def _makeChart(self) -> alt.Chart:
        indexName = self.df.index.name
        data = self.df[[colName
                        for colName in self.df.columns
                        if pd.api.types.is_numeric_dtype(self.df[colName])]]
        data = data.reset_index()

        varName = trl.Translator.translate(text="series",
                                           languageInput=self._languageInput,
                                           languageOutput=self._languageOutput)
        valueName = trl.Translator.translate(text="value",
                                             languageInput=self._languageInput,
                                             languageOutput=self._languageOutput)

        data = data.melt(id_vars=data.columns[0],
                         var_name=varName,
                         value_name=valueName)
        colorScale = alt.Scale(domain=data[varName].unique(),
                               range=[c.getCodeString()
                                      for c in pc.PacificoPlotColors]
                               )
        chart = alt.Chart(data).mark_line().encode(x=indexName,
                                                   y=valueName,
                                                   color=alt.Color(varName, scale=colorScale))
        chart = chart.properties(title=self._title,
                                 width=self._shape[0],
                                 height=self._shape[1])
        return chart
