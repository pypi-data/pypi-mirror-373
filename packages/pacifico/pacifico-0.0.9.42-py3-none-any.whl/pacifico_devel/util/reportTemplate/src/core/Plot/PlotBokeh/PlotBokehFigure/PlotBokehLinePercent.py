import typing as typ
import pandas as pd
import altair as alt
import bokeh.plotting as bpl
import bokeh.themes as bt
import bokeh.models as bm
from bokeh.models import NumeralTickFormatter, FixedTicker
from bokeh.plotting import output_file, show

import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokeh as pltb
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm

import pacifico_devel.util.lexikon.src.core.Translator as trl


## IDEA: collapse languageInput and languageOutput into one.


class PlotBokehLinePercent(pltb.PlotBokeh):
    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotBokehLinePercent, self).__init__(df=df, shape=shape, languageInput=languageInput,
                                                   languageOutput=languageOutput, basePlotResolution=basePlotResolution,
                                                   style=style)
        self._title = title

    def _makeChart(self) -> bpl.Figure:
        # output_file("line.html")
        chart = bpl.figure(width=self._shape[0],
                           height=self._shape[1],
                           toolbar_location=None)
        bpl.curdoc().theme = bt.Theme(filename=self._BOKEH_THEME_PATH)
        chart.title = self._title
        if pd.api.types.is_datetime64_any_dtype(self.df.index):
            if '-' in self._DATE_TIME_FORMAT:
                self._DATE_TIME_FORMAT = self._DATE_TIME_FORMAT.replace("-%d-", '-')
            if '/' in self._DATE_TIME_FORMAT:
                self._DATE_TIME_FORMAT = self._DATE_TIME_FORMAT.replace("%d/", '')
            chart.xaxis[0].formatter = bm.DatetimeTickFormatter(years=self._DATE_TIME_FORMAT,
                                                                months=self._DATE_TIME_FORMAT)
            # days=self._DATE_TIME_FORMAT)
        for colName, color in zip(self.df.columns,
                                  pc.PacificoPlotColors):
            if pd.api.types.is_numeric_dtype(self.df[colName].astype('float')):
                data = self.df[colName].astype('float')
                chart.line(x=data.index,
                           y=data,
                           legend_label=colName,
                           color=color.getCodeString(),
                           # source=data,
                           line_width=2)

        self.style(chart)
        self.legendStyle(chart, 'horizontal', 'below')
        # show(chart)
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
        # TITLE
        plot.title.text_color = pc.PacificoPlotColors.BLUE.getCodeString()
        plot.title.text_font_size = "20px"
        plot.title.text_font = "klartext mono"
        # plot.title.text_font_style = "italic"
        # LABELS
        plot.axis.axis_label_text_font = "klartext mono"
        plot.axis.axis_label_text_font_size = "15px"
        plot.axis.axis_label_text_font_style = 'normal'
        plot.axis.axis_label_text_color = pc.PacificoPlotColors.DARK_GREY.getCodeString()
        plot.axis.major_label_text_color = pc.PacificoPlotColors.DARK_GREY.getCodeString()
        # AXIS
        plot.xaxis.axis_line_color = pc.PacificoPlotColors.LIGHT_GREY.getCodeString()
        plot.axis.major_tick_line_color = pc.PacificoPlotColors.LIGHT_GREY.getCodeString()
        plot.xaxis.major_tick_line_width = 1
        plot.axis.minor_tick_line_color = pc.PacificoPlotColors.LIGHT_GREY.getCodeString()
        plot.yaxis.minor_tick_line_color = None
        plot.yaxis.axis_line_color = None
        # TICKS
        # plot.xaxis.major_label_orientation = np.pi / 2
        plot.xaxis.major_label_orientation = "vertical"
        plot.yaxis[0].formatter = NumeralTickFormatter(format="y{0%} ")
        # BACKGROUND
        plot.xgrid.grid_line_color = None
        plot.outline_line_color = None
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
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #    print(data[''])
    years = list(set(data['Año']))
    years.sort()
    series = []
    seriesNames = ['Fuerza de trabajo (Total)', 'Población ocupada (Total)']
    periods = 12

    serie = Data.percentChange(data[seriesNames], periods)  # data[criteria].dropna().pct_change(periods=12) * 100
    date = datetime(years[-4], max(serie.index).month, 1)
    series.append(serie[serie.index >= date])
    dataPlot = pd.concat(series, axis=1)

    p = PlotBokehLinePercent(df=dataPlot,
                             shape=(1, 1 / 4),
                             languageInput=Language.fromDeeplString("ES"),
                             languageOutput=Language.fromDeeplString("ES"),
                             basePlotResolution=1000,
                             style=None,
                             title='')._makeChart()
    show(p)
