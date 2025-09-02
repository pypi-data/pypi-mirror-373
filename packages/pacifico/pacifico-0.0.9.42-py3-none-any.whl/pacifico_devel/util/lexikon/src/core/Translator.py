import typing as typ
import deepl
import pandas as pd
import pandas.api.types as pdt
import re
import numpy as np
from datetime import datetime
import pacifico_devel.util.lexikon.src.util.Enumerations as lenm
import pacifico_devel.util.cfg.Configuration as cfg


class Translator:
    """
    Class that implements language translator (probably with deep learning).
    """
    _KEY_NAME = "deepl_translator_key"

    @classmethod
    def translate_dataframe(cls,
                            df: pd.DataFrame,
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
        dfAux = dfAux.applymap(lambda x: x.date() if isinstance(x, datetime) else x)
        ##
        if pdt.is_string_dtype(dfAux.index):
            indexes = cls.translate(text=dfAux.index,
                                    languageInput=languageInput,
                                    languageOutput=languageOutput)
            if isinstance(dfAux.index, pd.MultiIndex):
                dfAux.index = pd.MultiIndex.from_tuples(indexes)
            else:
                dfAux.index = indexes
        ##
        if dfAux.index.name is not None:
            #     dfAux.index.name = cls.translate(text="index",
            #                                      languageInput=lenm.Language.English_US,
            #                                      languageOutput=languageOutput)
            # else:
            dfAux.index.name = cls.translate(text=dfAux.index.name,
                                             languageInput=languageInput,
                                             languageOutput=languageOutput)
        ##
        if pdt.is_string_dtype(dfAux.columns):
            cols = cls.translate(text=dfAux.columns,
                                 languageInput=languageInput,
                                 languageOutput=languageOutput)
            if isinstance(dfAux.columns, pd.MultiIndex):
                dfAux.columns = pd.MultiIndex.from_tuples(cols)
            else:
                dfAux.columns = cols
        for col in dfAux.columns:
            if pdt.is_string_dtype(dfAux[col]):
                dfAux[col] = cls.translate(text=dfAux[col],
                                           languageInput=languageInput,
                                           languageOutput=languageOutput)
        if languageInput is not languageOutput:
            dfAux = dfAux.applymap(lambda x: float(x) if bool(re.match('^[-+]?[0-9]*\.?[0-9]+$', str(x))) else (
                np.nan if x == 'nan' else (
                    datetime.strptime(x, '%Y-%m-%d') if bool(re.search(r'(\d+-\d+-\d+)', str(x))) else x)))

        return dfAux

    @classmethod
    def translate(cls,
                  text: typ.Union[str, typ.Iterable[str]],
                  languageInput: lenm.Language,
                  languageOutput: lenm.Language) -> typ.Union[str, typ.List[str], typ.List[tuple]]:
        """

        Args:
            text:
            languageInput:
            languageOutput:

        Returns: translated text

        """

        translator = deepl.Translator(cls._getKey())
        print(f"SOURCE LANG: {languageInput.deeplStringOutput}")
        print(f"TARGET LANG: {languageOutput.deeplStringOutput}")
        if isinstance(text, str):
            if languageInput is languageOutput:
                return text
            result = translator.translate_text(text=text,
                                               source_lang=languageInput.deeplStringInput,
                                               target_lang=languageOutput.deeplStringOutput)
            return result.text
        elif hasattr(text, "__iter__"):
            if languageInput is languageOutput:
                return list(text)
            result = translator.translate_text(text=text,
                                               source_lang=languageInput.deeplStringInput,
                                               target_lang=languageOutput.deeplStringOutput)

            if isinstance(text, pd.MultiIndex):
                text = [item for t in text for item in t]
                result = [res.text if res.text != '' else t for res, t in zip(result, text)]
                return [*zip(result[::2], result[1::2])]
            result = [res.text if res.text != '' else t for res, t in zip(result, text)]
            return result

        raise ValueError(f"Invalid input: {text} of type {type(text)}. Must be of type str or an iterable of str.")

    @classmethod
    def _getKey(cls):
        """ Returns key from key-keeper"""
        return cfg.get(cls._KEY_NAME)


if __name__ == '__main__':
    text = """Aumentamos nuestra proyección de IPC de marzo desde 0.94 % hasta 1.08 % sin consecuencias relevantes para el acumulado del año. El seguimiento
    a productos como cigarrillos y gas por red nos llevó a adelantar la variación mensual que esperábamos ocurriera en el segundo trimestre. Para el caso
del precio del gas licuado empiezan a materializarse los riesgos al alza: desde la proyección inicial del mes preveíamos aumentos significativos, pero
el seguimiento de precios nos llevó a proyectar un incremento aún mayor. Todo lo anterior se vio parcialmente compensado por una mayor caída
proyectada para el pasaje en bus interurbano."""
    print(bool(re.match('^[-+]?[0-9]*\.?[0-9]+$', '2022-1-3')))
    # translation = Translator.translate(text=text,
    #                                    languageInput=lenm.Language.English_US,
    #                                    languageOutput=lenm.Language.Spanish)
    #
    # print(f"ORIGINAL TEXT: {text}")
    # print(f"TRANSLATED TEXT: {translation}")

