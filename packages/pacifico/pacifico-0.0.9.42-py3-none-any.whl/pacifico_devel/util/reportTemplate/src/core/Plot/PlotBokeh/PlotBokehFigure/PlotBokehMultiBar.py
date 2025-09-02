from pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokeh import PlotBokeh
import pacifico_devel.util.reportTemplate.src.util.PacificoPlotColors as pc
import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl

import bokeh.plotting as bpl
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import dodge
from bokeh.io import curdoc
from bokeh.themes import Theme
from bokeh.models import NumeralTickFormatter
import pandas as pd
import typing as typ
from bokeh.plotting import output_file, show
from bokeh.io import export_png


class PlotBokehMultiBar(PlotBokeh):
    def __init__(self,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 languageInput: lenm.Language,
                 languageOutput: lenm.Language,
                 basePlotResolution: int,
                 style: typ.Optional[stl.Style] = None,
                 title: str = None):
        super(PlotBokehMultiBar, self).__init__(df=df, shape=shape, languageInput=languageInput,
                                                languageOutput=languageOutput, basePlotResolution=basePlotResolution,
                                                style=style)
        self._title = title

    def _makeChart(self) -> bpl.Figure:
        maxValue = self.df.iloc[:, 1:].max().max()
        data = self.df.to_dict(orient="list")
        positions, width = PlotBokehMultiBar.plotDistribution(len(list(data.keys())) - 1)
        source = ColumnDataSource(data=data)
        plot = figure(x_range=data['xAxisCategory'],
                      y_range=(0, maxValue * 1.1),
                      width=self._shape[0],
                      height=self._shape[1],
                      toolbar_location=None)
        plot.title = self._title
        categories = list(data.keys())
        categories.remove('xAxisCategory')
        for category, color, position in zip(categories, pc.PacificoPlotColors, positions):
            plot.vbar(x=dodge('xAxisCategory', position, range=plot.x_range), top=category, width=width,
                      source=source, color=color.getCodeString(), legend_label=category)
        if len(data['xAxisCategory']) > 12:
            plot.xaxis.major_label_orientation = "vertical"
        self.style(plot)
        self.legendStyle(plot, 'horizontal', 'below')
        # show(plot)
        # export_png(plot, filename="bokeh_plot.png")
        return plot

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
        # plot.xaxis.major_label_orientation = "vertical"
        # BACKGROUND
        plot.xgrid.grid_line_color = None
        plot.outline_line_color = None
        plot.yaxis[0].formatter = NumeralTickFormatter(format="y{0%} ")
        return plot

    @staticmethod
    def debugMakeChart(data, shape, title='') -> bpl.Figure:
        # output_file("PlotBokehMultiBar.html")
        maxValue = data.iloc[:, 1:].max().max()
        data = data.to_dict(orient="list")
        positions, width = PlotBokehMultiBar.plotDistribution(len(list(data.keys())) - 1)
        source = ColumnDataSource(data=data)
        plot = figure(x_range=data['xAxisCategory'],
                      y_range=(0, maxValue * 1.1),
                      width=shape[0],
                      height=shape[1],
                      toolbar_location=None)
        plot.title = title
        categories = list(data.keys())
        categories.remove('xAxisCategory')
        for category, color, position in zip(categories, pc.PacificoPlotColors, positions):
            plot.vbar(x=dodge('xAxisCategory', position, range=plot.x_range), top=category, width=width,
                      source=source, color=color.getCodeString(), legend_label=category)
        if len(data['xAxisCategory']) >= 12:
            plot.xaxis.major_label_orientation = "vertical"
        show(plot)
        export_png(plot, filename="bokeh_plot.png")
        return plot

    @staticmethod
    def plotDistribution(numberBarCategory):
        if numberBarCategory == 6:
            positions = [-0.45, -0.3, -0.15, 0, 0.15, 0.3, 0.45]
            width = 0.07
            return positions, width
        if numberBarCategory == 5:
            positions = [-0.3, -0.15, 0, 0.15, 0.3]
            width = 0.07
            return positions, width
        if numberBarCategory == 4:
            positions = [-0.15, -0.5, 0.5, 0.15]
            width = 0.08
            return positions, width
        if numberBarCategory == 3:
            positions = [-0.1, 0, 0.1]
            width = 0.085
            return positions, width
        if numberBarCategory == 2:
            positions = [-0.1, 0.1]
            width = 0.1
            return positions, width


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
