# -*- coding: utf-8 -*-

import docxtpl as dtp
import docx.shared as ds
import datetime as dt
import typing as typ
import pathlib as pth

from pacifico_devel.util.reportTemplate.src.core.Report.Report import Report
from pacifico_devel.util.lexikon.src.util.Enumerations import Language
import pacifico_devel.util.reportTemplate.src.util.CONFIG as CFG


class ReportDocx(Report):
    _OUTPUT_FORMAT = ".docx"
    _FILENAME_TEMPLATE_DEFAULT: str = "demo.docx"
    _PAGE_DIMENSIONS_DEFAULT: typ.Tuple[float, float] = (27.94, 21.59)  # CARTA, HORIZONTAL, cm, (width, height)
    _PAGE_MARGINS_DEFAULT: typ.Tuple[float, float] = (1.27, 1.27)  # ESTRECHO, cm, (width, height)

    def __init__(self,
                 pathTemplate: typ.Union[str, pth.Path] = _FILENAME_TEMPLATE_DEFAULT,
                 languageOutput: typ.Union[Language, str] = Language.Spanish,
                 languageInput: typ.Union[Language, str] = Language.Spanish,
                 date: dt.datetime = dt.datetime.now(),
                 pageDimensions: typ.Tuple[float, float] = _PAGE_DIMENSIONS_DEFAULT,
                 pageMargins: typ.Tuple[float, float] = _PAGE_MARGINS_DEFAULT):
        super().__init__(pathTemplate=pathTemplate,
                         languageOutput=languageOutput,
                         languageInput=languageInput,
                         date=date,
                         outputFormat=self._OUTPUT_FORMAT)

        self._doc: dtp.DocxTemplate = dtp.DocxTemplate(self._pathTemplate)
        self._contents: typ.Dict[str, typ.Union[str, dtp.InlineImage]] = {}

        self._widthUnit: float = pageDimensions[0] - 2 * pageMargins[0]  # cm
        self._heightUnit: float = pageDimensions[1] - 2 * pageMargins[1]  # cm

    def _setString(self,
                   tag: str,
                   value: str):
        """
        Adds string to document.

        Args:
            tag:
            value:

        Returns:

        """
        self._contents[tag] = value

    def render(self,
               pathOutput: typ.Union[str, pth.Path]) -> None:
        """
        Generates document and saves it to _PATH_OUTPUT class attribute.

        Returns:
            param pathOutput:

        """
        print("#" * 20 + "\n")
        print(f"DOCUMENT CONTENTS: {self._contents}")
        if isinstance(pathOutput, str):
            pathOutput = pth.Path(pathOutput)
        self._doc.render(self._contents)
        self._doc.save(str(pathOutput))
        print(f"SAVED TO {pathOutput}")
        self._deleteAllTempPlots()



    def setImage(self,
                 tag: str,
                 path: typ.Union[str, pth.Path],
                 width: typ.Optional[float] = None,
                 height: typ.Optional[float] = None) -> None:
        """
        Sets an image. Width is taken into account first; height is taken into account only if width is None.

        Returns:

        """
        print(f"Setting Image at {tag}...")
        if width is None:
            if height is None:
                self._contents[tag] = dtp.InlineImage(tpl=self._doc,
                                                      image_descriptor=str(path)
                                                      )
            else:
                self._contents[tag] = dtp.InlineImage(tpl=self._doc,
                                                      image_descriptor=str(path),
                                                      height=ds.Cm(height * self._heightUnit * (1 - self._EPSILON))
                                                      )
        else:
            self._contents[tag] = dtp.InlineImage(tpl=self._doc,
                                                  image_descriptor=str(path),
                                                  width=ds.Cm(width * self._widthUnit * (1 - self._EPSILON)),
                                                  )
        print(f"Setting Image at {tag}... DONE!")

    def setLogo(self,
                tag: str,
                width: typ.Optional[int] = None,
                height: typ.Optional[int] = None) -> None:
        self.setImage(tag=tag,
                      path=CFG.PATH_LOGO,
                      height=height,
                      width=width)
    #
    # def setPageBreak(self):
    #     self._contents['page_break'] = '\f'
    #
    # def getDox(self):
    #     return self._doc.get_docx()


if __name__ == '__main__':
    from pacifico_devel.util.reportTemplate.src.util.testing import makeRandomCategoricalDf
    from pacifico_devel.util.reportTemplate.src.core.Plot.PlotBar import PlotBar
    from pacifico_devel.util.reportTemplate.src.core.Plot.PlotLine import PlotLine
    from pacifico_devel.util.reportTemplate.src.core.Plot.Table.TableDefault import TableDefault

    df = makeRandomCategoricalDf(shape=(15, 3))

    bp = PlotBar()
    bp.makePlot(df=df,
                title="bar plot",
                shape=(1 / 2, 1),
                valuesColumn="value_0")

    lp = PlotLine()
    lp.makePlot(df=df,
                title="line plot")

    tab = TableDefault()
    tab.makePlot(df=df,
                 title="table")

    text = "Este es un texto en espanol."

    rdoc = ReportDocx(languageOutput=Language.English_US)
    rdoc.setPlot(tag="bar_plot_image",
                 df=df,
                 plotKind="bar_plot",
                 title="",
                 shape=(1 / 2, 1))
    rdoc.setPlot(tag="line_plot_image",
                 df=df,
                 plotKind="line_plot",
                 title="",
                 shape=(1 / 2, 1))
    rdoc.setPlot(tag="table_image",
                 df=df,
                 plotKind="tabple_plot",
                 title="",
                 shape=(1 / 2, 1))

    rdoc.setText(tag="text",
                 value=text)

    rdoc.setText(tag="title",
                 value="Report Demo")

    rdoc.render(None)
