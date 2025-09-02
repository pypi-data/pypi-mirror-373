# -*- coding: utf-8 -*-

import abc
import datetime as dt
from abc import ABCMeta, abstractmethod
import pandas as pd
import pathlib as pth
import typing as typ
import re
from docx2pdf import convert
import PyPDF2
import os
import chromedriver_autoinstaller
from openpyxl import load_workbook

from pacifico_devel import Message
from pacifico_devel.api.src.util import Enumerations, Variant

# from pacifico_devel.util.reportTemplate.src.core.Style.Style import Style
import pacifico_devel.util.reportTemplate.src.core.Style.Style as stl
# from pacifico_devel.util.reportTemplate.src.core.Plot.Plot import Plot
# import pacifico_devel.util.reportTemplate.src.io.PlotFactory as pltf
import pacifico_devel.util.reportTemplate.src.core.Plot.Plot as bplt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotAltair.PlotAltairLine as pal
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotAltair.PlotAltairBar as pab
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLinePercent as pblp
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLineXticks as pbxt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLinePercentXticks as pbpxt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLineAndPointed as pblap
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLine as pbl
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehLineTwoYAxis as pblt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehPieChart as pbpc
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehBar as pbb
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehMultiBar as pbmb
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBokeh.PlotBokehFigure.PlotBokehStackBar as pbsb
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTable as pt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableIndex as pti
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableNoIndexes as ptni
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTablePercent as ptpc
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTablePercentIndex as ptpci
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableCarryAndRoll as ptcr
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableColorMap as ptcm
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableOneColorMap as ptocm
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableColorIndex as ptci
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTablePositions as ptp
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableWithDivisions as ptd
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotTable.PlotTableWithDivisionsIndex as ptdi
# import pacifico_devel.util.reportTemplate.src.util.Enumerations as renm
import pacifico_devel.util.reportTemplate.src.util.Report.DateFormatterEn as dtf
import pacifico_devel.util.reportTemplate.src.util.CONFIG as CFG
from pacifico_devel.util.lexikon.src.util.Enumerations import Language
from pacifico_devel.util.lexikon.src.core.Translator import Translator

from pacifico_devel.util.aws import S3
from pacifico_devel.util.cfg import Configuration as cfg

multiDate = typ.Union[dt.date, dt.datetime]


class Report(metaclass=ABCMeta):
    """
    Puts it all together? (format and style, analogue to HTML and CSS.)
    """

    _BASE_PLOT_RESOLUTION: int = 1000
    _EPSILON: float = 2 / 100
    _WRITER = pd.ExcelWriter(CFG.PATH_TEMPLATE_EXCEL, engine='xlsxwriter')

    def __init__(self,
                 pathTemplate: typ.Union[pth.Path, str],
                 languageOutput: typ.Union[Language, str] = Language.Spanish,
                 languageInput: typ.Union[Language, str] = Language.Spanish,
                 date: dt.datetime = dt.datetime.now(),
                 outputFormat: typ.Optional[str] = None):

        chromedriver_autoinstaller.install()

        self._pathTemplate: pth.Path = pth.Path(pathTemplate)
        self._checkPathTemplate()

        if outputFormat is None:
            self._outputFormat: str = pathTemplate.suffix
        else:
            self._outputFormat: str = outputFormat

        if isinstance(languageOutput, str):
            self._languageOutput = Language.fromDeeplString(languageOutput)
        else:
            self._languageOutput = languageOutput

        if isinstance(languageInput, str):
            self._languageInput = Language.fromDeeplString(languageInput)
        else:
            self._languageInput = languageInput

        if not self._pathTemplate.suffix == self._outputFormat:
            raise ValueError(f"File {self._pathTemplate} must be a {self._outputFormat} document.")

        self._date = date
        self._tempPlots: typ.Dict[str, bplt.Plot] = {}

    @property
    def languageOutput(self) -> Language:
        return self._languageOutput

    @property
    def languageInput(self) -> Language:
        return self._languageInput

    @abc.abstractmethod
    def render(self,
               pathOutput: typ.Union[str, pth.Path]) -> None:
        """
        Generates document and saves it locally.

        Args:
            pathOutput:

        Returns:

        """
        pass

    def export(self,
               applicationName: str) -> typ.List[Message.Report]:
        """
        Make a file from abstract reportTemplate and save it to a S3 stated in the filename.

        Args:
           applicationName:

        Returns (str): URL of document.

        """
        self.render(pathOutput=self._tempOutputPath)
        url = self._uploadAndGetUrl(filepathLocal=self._tempOutputPath)
        dateEffective = dt.datetime.now()
        message = self._getMessage(url=url,
                                   applicationName=applicationName,
                                   dateEffective=dateEffective)
        return [message]

    def export2excel(self, applicationName: str, clean: bool = True):
        self._WRITER.close()
        pathExcel = CFG.PATH_TEMPLATE_EXCEL
        url = self._uploadAndGetUrl(filepathLocal=pathExcel)
        dateEffective = dt.datetime.now()
        message = self._getMessage(url=url,
                                   applicationName=applicationName,
                                   dateEffective=dateEffective)
        return [message]

    def exportPDF(self, applicationName: str, clean: bool = True):
        self.render(pathOutput=self._tempOutputPath)
        convert(self._tempOutputPath)
        pathPDF = pth.Path(self._tempOutputPath.parent) / (self._tempOutputPath.stem + ".pdf")
        if clean:
            self.cleanPDF(pathPDF)
        url = self._uploadAndGetUrl(filepathLocal=pathPDF)
        dateEffective = dt.datetime.now()
        message = self._getMessage(url=url,
                                   applicationName=applicationName,
                                   dateEffective=dateEffective)
        return [message]

    def cleanPDF(self, filePathReader: typ.Union[str, pth.Path]):
        fileName: str = self._pathTemplate.stem + "_temp1.pdf"
        filePathWriter = self._pathTemplate.parent / fileName
        writer = PyPDF2.PdfFileWriter()
        file = open(filePathReader, 'rb')
        reader = PyPDF2.PdfFileReader(file)
        for index, page in enumerate(reader.pages):
            texts = [text for text in page.extractText().split('\n') if not re.search("^\s*$", text)]
            if len(texts) > 2 or index == 0:
                writer.addPage(page)
        outputFile = open(filePathWriter, "wb")
        writer.write(outputFile)
        file.close()
        os.remove(filePathReader)
        outputFile.close()
        os.rename(filePathWriter, filePathReader)

    def _deleteAllTempPlots(self) -> None:
        """
        deletes all temporary plot images

        Returns:

        """
        [plot.deleteImage()
         for plot in self._tempPlots.values()]

    def _getMessage(self,
                    url: str,
                    applicationName: str,
                    dateEffective: dt.datetime) -> Message.Report:
        """
        Returns information in API format (Message.Report).

        Args:
            url:
            applicationName:
            dateEffective:

        Returns:

        """
        # document, chapter, section, subsection, paragraph = self.splitApplicationName(applicationName=applicationName)
        keys: typ.List[str] = ["document", "chapter", "section", "subsection", "paragraph"]
        values: typ.List[str] = self._splitApplicationName(applicationName=applicationName)

        if not 1 <= len(values) <= 4:
            msg1 = "Expecting name to be split into list of between 1 and 4 elements, "
            msg2 = f"but returned: {values}"
            raise ValueError(msg1 + msg2)

        values.append(self._outputFormat)  # put format last
        argDict: typ.Dict[str, typ.Union[str, dt.datetime, Variant.Variant]] = {k: v
                                                                                for k, v in zip(keys, values)}
        argDict["item"] = "report"
        argDict["dateEffective"] = dateEffective
        variant: Variant.Variant = Variant.Variant(value=url,
                                                   valueType=Enumerations.ValueType.ValueType_Url)
        print(f"URL: {url}.")
        argDict["variant"] = variant

        message: Message.Report = Message.Report(**argDict)
        return message

    @abstractmethod
    def _setString(self,
                   tag,
                   value: str) -> None:
        """
        Adds string to document.

        Args:
            tag:
            value:

        Returns:

        """
        pass

    @abstractmethod
    def setImage(self,
                 tag: str,
                 path: typ.Union[str, pth.Path],
                 width: typ.Optional[float] = None,
                 height: typ.Optional[float] = None) -> None:
        """
        Sets an image.

        Returns:

        """

        pass

    def setString(self,
                  tag: str,
                  value: str,
                  translate: bool = False) -> None:  # could be enumeration or beautifulSoup:
        """
        For bond mnemo (for example).

        Args:
            value:
            tag:
            translate:

        Returns:

        """
        valueString = value
        if translate:
            print("\n" + "#" * 20)
            print("TRANSLATING...")
            msg1 = f"TEXT TO TRANSLATE FROM {self._languageInput.deeplStringInput} to {self._languageOutput.deeplStringOutput}:"
            msg2 = f"\n\t{valueString}"
            print(msg1 + msg2)
            valueString = Translator.translate(text=valueString,
                                               languageInput=self.languageInput,
                                               languageOutput=self.languageOutput)
            print(f"TRANSLATION : \n\t{valueString}")
            print("TRANSLATING... DONE!")
            print("#" * 20 + "\n")
        self._setString(value=valueString,
                        tag=tag)

    def setText(self,
                tag: str,
                value: str):
        """
        For Commentary (for example)

        Args:
            value:
            tag:

        Returns:

        """
        return self.setString(value=value,
                              tag=tag,
                              translate=True)

    def setInteger(self,
                   tag: str,
                   value: int) -> None:
        self.setString(value=stl.Style.convertIntToString(value,
                                                          self.languageOutput),
                       tag=tag)

    def setFloat(self,
                 tag: str,
                 value: float,
                 numberDecimals: int,
                 isPercentage: bool = False) -> None:
        """
        Same as above.

        Args:
            value:
            numberDecimals:
            tag:
            isPercentage:

        Returns:

        """
        valueString = stl.Style.convertFloatToString(value=value,
                                                     numberDecimals=numberDecimals,
                                                     language=self.languageOutput)

        self.setString(value=valueString,
                       tag=tag)

    def setLongDate(self,
                    tag: str,
                    value: typ.Optional[multiDate] = None,
                    ) -> None:

        if value is None:
            longDateStringEn = dtf.DateFormatterEn.getLongDateStringEn(self._date)
        else:
            longDateStringEn = dtf.DateFormatterEn.getLongDateStringEn(value)

        longDateString = Translator.translate(text=longDateStringEn,
                                              languageInput=Language.English_US,
                                              languageOutput=self.languageOutput)
        self.setString(value=longDateString,
                       tag=tag,
                       translate=False)

    def setDateTime(self,
                    value: dt.datetime,
                    tag: str) -> None:
        valueString = stl.Style.convertDateTimeToString(value=value,
                                                        language=self.languageOutput)
        self.setString(value=valueString,
                       tag=tag)

    def setDate(self,
                value: dt.date,
                tag: str) -> None:
        """


        Args:
            value:
            tag:

        Returns:

        """
        valueString = stl.Style.convertDateToString(value,
                                                    language=self.languageOutput)

        self.setString(value=valueString,
                       tag=tag)

    def setDateMonth(self,
                     value: dt.date,
                     tag: str) -> None:
        """
        YYYY/MM

        Args:
            value:
            tag:

        Returns:

        """
        valueString = stl.Style.convertDateMonthToString(value,
                                                         language=self.languageOutput)

        self.setString(value=valueString,
                       tag=tag)

    def setDateQuarter(self,
                       value: dt.date,
                       tag: str) -> None:
        """
        YYYY

        Args:
            value:
            tag:

        Returns:

        """
        valueString = stl.Style.convertDateQuarterToString(value,
                                                           language=self.languageOutput)

        self.setString(value=valueString,
                       tag=tag)

    def setDateYear(self,
                    value: dt.date,
                    tag: str) -> None:
        """
        YYYY

        Args:
            value:
            tag:

        Returns:

        """
        valueString = stl.Style.convertDateYearToString(value)

        self.setString(value=valueString,
                       tag=tag)

    # def setPlot(self,
    #             tag: str,
    #             df: pd.DataFrame,
    #             plotKind: typ.Union[renm.PlotKind, str],
    #             title: str,
    #             shape: typ.Tuple[float, float],
    #             backend: typ.Union[renm.Backend, str, None] = None):  # width, height
    #
    #     if backend is None:
    #         backend = self._plotBackend
    #
    #     if isinstance(plotKind, str):
    #         plotKind = renm.PlotKind[plotKind.upper()]
    #
    #     p = pltf.PlotFactory.getPlot(plotKind=plotKind,
    #                                  languageInput=self._languageInput,
    #                                  languageOutput=self._languageOutput)
    #
    #     if title:
    #         titleTranslated = Translator.translate(title,
    #                                                languageInput=self._languageInput,
    #                                                languageOutput=self._languageOutput)
    #     else:
    #         titleTranslated = title
    #
    #     p.makePlot(df=df,
    #                title=titleTranslated,
    #                shape=tuple(int(dim * self._BASE_PLOT_RESOLUTION)
    #                            for dim in shape
    #                            ),
    #                backend=backend)
    #     self.setImage(tag=tag,
    #                   path=p.pathImage,
    #                   width=shape[0],
    #                   height=shape[1])
    #     self._tempPlots[tag] = p

    # SET PLOTS

    def _set_plot(self,
                  plot: bplt.Plot,
                  tag: str,
                  shape: typ.Tuple[float, float]) -> None:
        """
        Creates image from plot object, then sets the image into report and finally inserts plot into
        an internal dictionary for later access and erasure.

        Args:
            plot:
            tag:
            shape:

        Returns:

        """
        plot.saveImage()
        plot.df_to_excel(self._WRITER, tag)

        self.setImage(tag=tag,
                      path=plot.pathImage,
                      width=shape[0],
                      height=shape[1])
        self._tempPlots[tag] = plot

    def setPlotLine(self,
                    tag: str,
                    df: pd.DataFrame,
                    title: str,
                    shape: typ.Tuple[float, float]) -> None:

        p = pal.PlotAltairLine(df=df,
                               shape=shape,
                               languageInput=self.languageInput,
                               languageOutput=self.languageOutput,
                               basePlotResolution=self._BASE_PLOT_RESOLUTION,
                               title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotLinePercent(self,
                           tag: str,
                           df: pd.DataFrame,
                           title: str,
                           shape: typ.Tuple[float, float]) -> None:

        p = pblp.PlotBokehLinePercent(df=df,
                                      shape=shape,
                                      languageInput=self.languageInput,
                                      languageOutput=self.languageOutput,
                                      basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                      title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotLineXticks(self,
                          tag: str,
                          df: pd.DataFrame,
                          title: str,
                          shape: typ.Tuple[float, float],
                          xTicks: list = None) -> None:

        p = pbxt.PlotBokehLineXticks(df=df,
                                     shape=shape,
                                     languageInput=self.languageInput,
                                     languageOutput=self.languageOutput,
                                     basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                     title=title,
                                     xTicks=xTicks)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotLinePercentXticks(self,
                                 tag: str,
                                 df: pd.DataFrame,
                                 title: str,
                                 shape: typ.Tuple[float, float],
                                 xTicks: list = None) -> None:

        p = pbpxt.PlotBokehLinePercentXticks(df=df,
                                             shape=shape,
                                             languageInput=self.languageInput,
                                             languageOutput=self.languageOutput,
                                             basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                             title=title,
                                             xTicks=xTicks)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotBokehLine(self,
                         tag: str,
                         df: pd.DataFrame,
                         title: str,
                         shape: typ.Tuple[float, float]) -> None:

        p = pbl.PlotBokehLine(df=df,
                              shape=shape,
                              languageInput=self.languageInput,
                              languageOutput=self.languageOutput,
                              basePlotResolution=self._BASE_PLOT_RESOLUTION,
                              title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotBokehLineAndPointed(self,
                                   tag: str,
                                   df: pd.DataFrame,
                                   title: str,
                                   shape: typ.Tuple[float, float]) -> None:

        p = pblap.PlotBokehLineAndPointed(df=df,
                                          shape=shape,
                                          languageInput=self.languageInput,
                                          languageOutput=self.languageOutput,
                                          basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                          title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotLineTwoAxis(self,
                           tag: str,
                           df: pd.DataFrame,
                           title: str,
                           shape: typ.Tuple[float, float]) -> None:

        p = pblt.PlotBokehLineTwoYAxis(df=df,
                                       shape=shape,
                                       languageInput=self.languageInput,
                                       languageOutput=self.languageOutput,
                                       basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                       title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotPieChart(self,
                        tag: str,
                        df: pd.DataFrame,
                        title: str,
                        shape: typ.Tuple[float, float]) -> None:

        p = pbpc.PlotBokehPieChart(df=df,
                                   shape=shape,
                                   languageInput=self.languageInput,
                                   languageOutput=self.languageOutput,
                                   basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                   title=title)

        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotBar(self,
                   tag: str,
                   df: pd.DataFrame,
                   title: str,
                   shape: typ.Tuple[float, float]) -> None:

        p = pab.PlotAltairBar(df=df,
                              shape=shape,
                              languageInput=self.languageInput,
                              languageOutput=self.languageOutput,
                              basePlotResolution=self._BASE_PLOT_RESOLUTION,
                              title=title)

        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotStackBar(self,
                        tag: str,
                        df: pd.DataFrame,
                        title: str,
                        shape: typ.Tuple[float, float]) -> None:

        p = pbsb.PlotBokehStackBar(df=df,
                                   shape=shape,
                                   languageInput=self.languageInput,
                                   languageOutput=self.languageOutput,
                                   basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                   title=title)

        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotBar2(self,
                    tag: str,
                    df: pd.DataFrame,
                    title: str,
                    shape: typ.Tuple[float, float]) -> None:

        p = pbb.PlotBokehBar(df=df,
                             shape=shape,
                             languageInput=self.languageInput,
                             languageOutput=self.languageOutput,
                             basePlotResolution=self._BASE_PLOT_RESOLUTION,
                             title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setPlotMultiBar2(self,
                         tag: str,
                         df: pd.DataFrame,
                         title: str,
                         shape: typ.Tuple[float, float]) -> None:
        p = pbmb.PlotBokehMultiBar(df=df,
                                   shape=shape,
                                   languageInput=self.languageInput,
                                   languageOutput=self.languageOutput,
                                   basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                   title=title)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTable(self,
                 tag: str,
                 df: pd.DataFrame,
                 shape: typ.Tuple[float, float],
                 formatter=None) -> None:

        p = pt.PlotTable(df=df,
                         shape=shape,
                         languageInput=self.languageInput,
                         languageOutput=self.languageOutput,
                         basePlotResolution=self._BASE_PLOT_RESOLUTION,
                         formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableNoIndexes(self,
                          tag: str,
                          df: pd.DataFrame,
                          shape: typ.Tuple[float, float],
                          formatter=None) -> None:

        p = ptni.PlotTableNoIndexes(df=df,
                                    shape=shape,
                                    languageInput=self.languageInput,
                                    languageOutput=self.languageOutput,
                                    basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                    formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTablePercent(self,
                        tag: str,
                        df: pd.DataFrame,
                        shape: typ.Tuple[float, float]) -> None:

        p = ptpc.PlotTablePercent(df=df,
                                  shape=shape,
                                  languageInput=self.languageInput,
                                  languageOutput=self.languageOutput,
                                  basePlotResolution=self._BASE_PLOT_RESOLUTION)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTablePercentIndex(self,
                             tag: str,
                             df: pd.DataFrame,
                             shape: typ.Tuple[float, float]) -> None:

        p = ptpci.PlotTablePercentIndex(df=df,
                                        shape=shape,
                                        languageInput=self.languageInput,
                                        languageOutput=self.languageOutput,
                                        basePlotResolution=self._BASE_PLOT_RESOLUTION)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableCarryAndRoll(self,
                             tag: str,
                             df: pd.DataFrame,
                             shape: typ.Tuple[float, float],
                             formatter=None) -> None:

        p = ptcr.PlotTableCarryAndRoll(df=df,
                                       shape=shape,
                                       languageInput=self.languageInput,
                                       languageOutput=self.languageOutput,
                                       basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                       formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableColorIndex(self,
                           tag: str,
                           df: pd.DataFrame,
                           shape: typ.Tuple[float, float],
                           formatter=None) -> None:

        p = ptci.PlotTableColorIndex(df=df,
                                     shape=shape,
                                     languageInput=self.languageInput,
                                     languageOutput=self.languageOutput,
                                     basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                     formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableIndex(self,
                      tag: str,
                      df: pd.DataFrame,
                      shape: typ.Tuple[float, float],
                      formatter=None) -> None:

        p = pti.PlotTableIndex(df=df,
                               shape=shape,
                               languageInput=self.languageInput,
                               languageOutput=self.languageOutput,
                               basePlotResolution=self._BASE_PLOT_RESOLUTION,
                               formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableColorMap(self,
                         tag: str,
                         df: pd.DataFrame,
                         shape: typ.Tuple[float, float],
                         formatter=None) -> None:

        p = ptcm.PlotTableColorMap(df=df,
                                   shape=shape,
                                   languageInput=self.languageInput,
                                   languageOutput=self.languageOutput,
                                   basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                   formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableOneColorMap(self,
                            tag: str,
                            df: pd.DataFrame,
                            shape: typ.Tuple[float, float],
                            formatter=None) -> None:

        p = ptocm.PlotTableOneColorMap(df=df,
                                       shape=shape,
                                       languageInput=self.languageInput,
                                       languageOutput=self.languageOutput,
                                       basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                       formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTablePositions(self,
                          tag: str,
                          df: pd.DataFrame,
                          shape: typ.Tuple[float, float],
                          formatter=None) -> None:

        p = ptp.PlotTablePositions(df=df,
                                   shape=shape,
                                   languageInput=self.languageInput,
                                   languageOutput=self.languageOutput,
                                   basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                   formatter=formatter)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableWithDivisions(self,
                              tag: str,
                              df: pd.DataFrame,
                              shape: typ.Tuple[float, float],
                              formatter=None,
                              columnsSubset: list = []) -> None:

        p = ptd.PlotTableWithDivisions(df=df,
                                       shape=shape,
                                       languageInput=self.languageInput,
                                       languageOutput=self.languageOutput,
                                       basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                       formatter=formatter,
                                       columnsSubset=columnsSubset)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    def setTableWithDivisionsIndex(self,
                                   tag: str,
                                   df: pd.DataFrame,
                                   shape: typ.Tuple[float, float],
                                   formatter=None,
                                   columnsSubset: list = []) -> None:

        p = ptdi.PlotTableWithDivisionsIndex(df=df,
                                             shape=shape,
                                             languageInput=self.languageInput,
                                             languageOutput=self.languageOutput,
                                             basePlotResolution=self._BASE_PLOT_RESOLUTION,
                                             formatter=formatter,
                                             columnsSubset=columnsSubset)
        self._set_plot(plot=p,
                       tag=tag,
                       shape=shape)

    #
    # def setTable(self,
    #              df: pd.DataFrame,
    #              tag: str,
    #              shape: typ.Tuple[int, int] = (10, 10),
    #              formatter: dict = None):
    #     """
    #     PLAN: df (Done through Style) -> HTML -> IMAGE -> Paste in reportTemplate.
    #
    #     Args:
    #         df:
    #         tag:
    #         shape:
    #
    #     Returns:
    #
    #     """
    #     p = pltf.PlotFactory.getPlot(plotKind=renm.PlotKind.TABLE_PLOT,
    #                                  languageInput=self._languageInput,
    #                                  languageOutput=self._languageOutput)
    #
    #     p.makePlot(df=df,
    #                shape=tuple(int(dim * self._BASE_PLOT_RESOLUTION)
    #                            for dim in shape),
    #                backend=self._plotBackend,
    #                formatter=formatter)
    #     self.setImage(tag=tag,
    #                   path=p.pathImage,
    #                   width=shape[0],
    #                   height=shape[1])
    #     self._tempPlots[tag] = p

    @property
    def _tempOutputPath(self) -> pth.Path:
        fileName: str = self._pathTemplate.stem + "_temp" + self._outputFormat
        return self._pathTemplate.parent / fileName

    def _checkPathTemplate(self) -> None:
        """
        Assures the input template's path exists.

        """
        if not self._pathTemplate.is_file():
            msg = f"No such template path: {self._pathTemplate}. Please initialize with a valid template path."
            raise FileNotFoundError(msg)

    def _checkOuputFormat(self) -> None:
        """
        Assures input template's format is the output's file format.

        """
        if not self._pathTemplate.suffix == self._outputFormat:
            raise ValueError(f"File {self._pathTemplate} must be a {self._outputFormat} document.")

    def _uploadAndGetUrl(self, filepathLocal: typ.Union[str, pth.Path]) -> str:

        """
        Uploads file to S3 and returns URL.

        Args:
            filepathLocal:

        Returns:

        """

        if isinstance(filepathLocal, str):
            filepathLocal = pth.Path(filepathLocal)
        filepathBucket: pth.Path = self._getFilePathUpload(filePathLocal=filepathLocal)
        bucketName = "media-pacifico"
        awsAccessKey = cfg.get("AWS_ACCESS_KEY_PACIFICO")
        awsSecretKey = cfg.get("AWS_SECRET_KEY_PACIFICO")
        S3.writeFileToBucket(filepathLocal.as_posix(),
                             bucketName,
                             awsAccessKey,
                             awsSecretKey,
                             filepathBucket.as_posix())  # also erases file
        url = S3.getUrl(filepathBucket.as_posix(),
                        bucketName,
                        awsAccessKey=awsAccessKey,
                        awsSecretKey=awsSecretKey)
        return url

    @staticmethod
    def _splitApplicationName(applicationName: str) -> typ.List[str]:
        splitName: typ.List[str] = re.findall("[A-Z][a-z]+",
                                              applicationName)  # NEEDS TO INCLUDE CAPITAL LETTERS FOLLOWING
        splitName = [s for s in splitName if s != "Application"]
        if len(splitName) == 0:
            splitName = ["Report"]
        if len(splitName) >= 5:
            sFinal = " ".join(splitName[4:])
            splitName = splitName[:4]
            splitName[4] = sFinal
        return splitName

    @staticmethod
    def _getFilePathUpload(filePathLocal: pth.Path) -> pth.Path:
        stringTime: str = dt.datetime.now().strftime("%Y.%m.%d_%H.%M.%S.%f")
        fileNameUpload = filePathLocal.stem + "_" + stringTime + filePathLocal.suffix
        return pth.Path(fileNameUpload)


if __name__ == '__main__':
    # print(__file__)
    # print(pth.Path(pth.Path(__file__)))
    # test = "ApplicationStuffABTesting"
    # print(Report.splitApplicationName(test))
    filepathBucket = "template_temp_2022.04.22_17.17.36.906014.docx"
    filepathLocal = "template_temp_2022.04.22_17.17.36.906014.docx"
    bucketName = "media-pacifico"
    awsAccessKey = cfg.get("AWS_ACCESS_KEY_PACIFICO")
    awsSecretKey = cfg.get("AWS_SECRET_KEY_PACIFICO")
    # S3.writeFileToBucket(filepathLocal.as_posix(),
    #                      bucketName,
    #                      awsAccessKey,
    #                      awsSecretKey,
    #                      filepathBucket.as_posix())  # also erases file
    url = S3.getUrl(filepathBucket,
                    bucketName,
                    awsAccessKey=awsAccessKey,
                    awsSecretKey=awsSecretKey)
    print(url)
