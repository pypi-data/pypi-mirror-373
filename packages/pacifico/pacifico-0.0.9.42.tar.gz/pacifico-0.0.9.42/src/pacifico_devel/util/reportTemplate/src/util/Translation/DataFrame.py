import pandas as pd
import pandas.api.types as pdt

import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.lexikon.src.core.Translator as trl


def translateDataFrame(df: pd.DataFrame,
                       languageInput: lenm.Language,
                       languageOutput: lenm.Language) -> pd.DataFrame:
    """
    Translates all strings in dataframe.

    Args:
        df:
        languageInput:
        languageOutput:

    Returns:

    """
    dfAux = df.copy()
    ##
    if pdt.is_string_dtype(dfAux.index):
        dfAux.index = trl.Translator.translate(text=dfAux.index,
                                               languageInput=languageInput,
                                               languageOutput=languageOutput)
    ##
    if dfAux.index.name is None:
        dfAux.index.name = trl.Translator.translate(text="index",
                                                    languageInput=lenm.Language.English_US,
                                                    languageOutput=languageOutput)
    else:
        dfAux.index.name = trl.Translator.translate(text=dfAux.index.name,
                                                    languageInput=languageInput,
                                                    languageOutput=languageOutput)
    ##
    if pdt.is_string_dtype(dfAux.columns):
        dfAux.columns = trl.Translator.translate(text=dfAux.columns,
                                                 languageInput=languageInput,
                                                 languageOutput=languageOutput)
    for col in dfAux.columns:
        if pdt.is_string_dtype(dfAux[col]):
            dfAux[col] = trl.Translator.translate(text=dfAux[col],
                                                  languageInput=languageInput,
                                                  languageOutput=languageOutput)
    return dfAux
