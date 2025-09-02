import pacifico_devel.util.reportTemplate.src.core.Plot.PlotLine as pltl
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotBar as pltb
import pacifico_devel.util.reportTemplate.src.core.Plot.Table.TableDataframeImage as pltt
import pacifico_devel.util.reportTemplate.src.core.Plot.PlotMultiBar as plmb
import pacifico_devel.util.reportTemplate.src.util.Enumerations as renm

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm


class PlotFactory:
    @staticmethod
    def getPlot(plotKind: renm.PlotKind,
                languageInput: lenm.Language,
                languageOutput: lenm.Language):
        """
        Returns the pertinent plot object.

        Args:
            plotKind:
            languageInput:
            languageOutput:

        Returns:

        """
        kwargs = {"languageInput": languageInput,
                  "languageOutput": languageOutput}

        if plotKind is renm.PlotKind.LINE_PLOT:
            return pltl.PlotLine(**kwargs)
        elif plotKind is renm.PlotKind.BAR_PLOT:
            return pltb.PlotBar(**kwargs)
        elif plotKind is renm.PlotKind.TABLE_PLOT:
            return pltt.TableDataframeImage(**kwargs)
        elif plotKind is renm.PlotKind.MULTI_BAR_PLOT:
            return plmb.PlotMultiBar(**kwargs)

        raise ValueError(f"Invalid plot kind: {plotKind}")
