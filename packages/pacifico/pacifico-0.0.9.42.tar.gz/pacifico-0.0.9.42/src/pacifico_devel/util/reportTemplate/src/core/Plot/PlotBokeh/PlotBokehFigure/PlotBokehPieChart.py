from pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokeh import PlotBokeh
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc
import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl

import bokeh.plotting as bpl
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.models import LabelSet

import pandas as pd
import numpy as np
import typing as typ
from bokeh.plotting import output_file, show
from bokeh.io import export_png


class PlotBokehPieChart(PlotBokeh):
    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotBokehPieChart, self).__init__(df=df, shape=shape, languageInput=languageInput,
                                                languageOutput=languageOutput, basePlotResolution=basePlotResolution,
                                                style=style)
        self._title = title

    def _makeChart(self) -> bpl.Figure:
        assets = list(self.df['component'])
        self.df['angle'] = self.df['weight'] / self.df['weight'].sum() * 2 * np.pi
        self.df['color'] = [color.getCodeString() for i, color in zip(range(len(assets)), pc.PacificoPlotColors)]
        chart = figure(width=self._shape[0],
                       height=self._shape[1],
                       toolbar_location=None)
        chart.title = self._title
        chart.wedge(x=0, y=1,
                    radius=0.75,
                    start_angle=cumsum('angle', include_zero=True),
                    end_angle=cumsum('angle'),
                    line_color="white",
                    fill_color='color',
                    legend_field='component',
                    source=self.df)
        self.df["weight"] = round(self.df['weight'], 1).astype(str) + ' %'
        self.df["weight"] = self.df["weight"].str.pad(20, side="left")
        source = ColumnDataSource(self.df)
        labels = LabelSet(x=0, y=1, text='weight', angle=cumsum('angle', include_zero=True),
                          source=source, render_mode='canvas', text_color='#FFFFFF', text_font_size="15px")
        chart.add_layout(labels)
        self.style(chart)
        self.legendStyle(chart, 'vertical', 'right')
        return chart

    def legendStyle(self, plot, orientation: str = 'vertical', layout: str = 'right'):
        new_legend = plot.legend[0]
        plot.add_layout(new_legend, layout)  # 'below'
        plot.legend.orientation = orientation  # 'horizontal'
        plot.legend.location = "center"
        plot.legend.border_line_alpha = 0
        plot.legend.background_fill_color = None
        plot.xgrid.grid_line_color = None
        plot.legend.click_policy = "hide"
        plot.legend.label_text_font = "klartext mono"
        plot.legend.label_text_color = pc.PacificoPlotColors.DARK_GREY.getCodeString()
        return plot

    def style(self, plot):
        plot.title.text_color = pc.PacificoPlotColors.BLUE.getCodeString()
        plot.title.text_font_size = "20px"
        plot.axis.axis_label = None
        plot.axis.visible = False
        plot.grid.grid_line_color = None
        plot.outline_line_color = None
        plot.legend.border_line_alpha = 0
        plot.legend.label_text_font = "klartext mono"
        return plot


if __name__ == '__main__':
    from datetime import datetime
    from Applications.ApplicationReportChileUnemployment.src.core.Data import Data
    from pacifico_devel.util.lexikon.src.util.Enumerations import Language
    import chromedriver_autoinstaller

    chromedriver_autoinstaller.install()
    data = Data(datetime.now())
    data.load('KmK9FqgJ5h1pSNjh1vhha6ul30vXBOBiMVlmplXf', ['60703000-6', 'F049.CES.TAS.UCH3.65.T'])
    data.computeUnemployment()
    data = data.getData()
    months = {'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 'jul': 7,
              'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12}
    dataDict = {}
    years = list(set(data['Año']))
    years.sort()
    for year in years[-5:]:
        dataDict[str(year)] = data[data['Año'] == year]['Desempleo (Total)'].tolist()
    dataPlot = {**{'xAxisCategory': list(months.keys())}, **dataDict}

    dataPlot = pd.DataFrame(dataPlot)

    PlotBokehMultiBar(df=dataPlot,
                      shape=(900, 500),
                      languageInput=Language.fromDeeplString("ES"),
                      languageOutput=Language.fromDeeplString("ES"),
                      basePlotResolution=1000,
                      style=None,
                      title='')._makeChart()  # debugMakeChart(dataPlot, (900, 500))
