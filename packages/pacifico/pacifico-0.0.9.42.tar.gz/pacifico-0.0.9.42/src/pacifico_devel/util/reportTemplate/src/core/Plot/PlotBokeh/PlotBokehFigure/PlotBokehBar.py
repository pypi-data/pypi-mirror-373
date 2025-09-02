import typing as typ
import pandas as pd
import bokeh.plotting as bpl
import bokeh.themes as bt
from bokeh.plotting import output_file

import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokeh as pltb
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm


class PlotBokehBar(pltb.PlotBokeh):
    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotBokehBar, self).__init__(df=df,
                                           shape=shape,
                                           languageInput=languageInput,
                                           languageOutput=languageOutput,
                                           basePlotResolution=basePlotResolution,
                                           style=style)
        self._title = title

    def _makeChart(self) -> bpl.Figure:
        categoriesColumn = self.df.columns[0]
        valuesColumn = self.df.columns[1]

        self.df["barchart_color"] = self.df[valuesColumn].apply(self._colorMap)
        #output_file("bar.html")
        chart = bpl.figure(width=self._shape[0],
                           height=self._shape[1],
                           y_range=self.df.sort_values(valuesColumn,
                                                       ascending=True)[categoriesColumn],
                           toolbar_location=None)
        bpl.curdoc().theme = bt.Theme(filename=self._BOKEH_THEME_PATH)
        chart.title = self._title

        chart.hbar(y=categoriesColumn,
                   left=0,
                   right=valuesColumn,
                   height=0.5,
                   color="barchart_color",
                   source=self.df)

        return chart

    @staticmethod
    def _colorMap(x: float):
        if x > 0:
            return pc.PacificoPlotColors.BLUE.getCodeString()
        return pc.PacificoPlotColors.PINK.getCodeString()
