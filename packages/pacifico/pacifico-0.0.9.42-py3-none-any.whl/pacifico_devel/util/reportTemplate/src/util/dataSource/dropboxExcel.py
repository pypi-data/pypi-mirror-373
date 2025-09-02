import pathlib as pth
import typing as typ
import pandas as pd
import datetime as dt

from pacifico_devel.util.dropbox import Dropbox as dbx
import pacifico_devel.util.reportTemplate.executables.CONFIG as CFG

multiPath = typ.Union[str, pth.Path]


def _isDateLike(path: pth.Path) -> bool:
    return all(s.isnumeric() for s in path.stem.split("-"))


def _isExcelLike(path: pth.Path) -> bool:
    return path.suffix == ".xlsx"


def _getDate(stem: str):
    return dt.datetime.strptime(stem, CFG.DATETIME_FORMAT)


def _readExcelDbx(path: multiPath,
                  sheetName: str,
                  indexCol: typ.Union[int, str]) -> pd.DataFrame:
    dbx.downloadFile(dropboxPath=path)
    df = pd.read_excel(path.name,
                       sheet_name=sheetName,
                       index_col=indexCol)
    pth.Path(path.name).unlink()
    return df


####################

def getDataProyecciones(sheetName: str = "Mayores_Incidencias",
                        indexCol: typ.Optional[int] = None) -> pd.DataFrame:
    """

    Args:
        sheetName:
        indexCol:

    Returns: most recent excel in 'proyecciones' folder.

    """
    items = dbx.listPath(CFG.ROOT_DROPBOX_PROYECCIONES)
    filePaths = [pth.Path(item.path_display)
                 for item in items]
    filePaths: typ.List[pth.Path] = [filePath
                                     for filePath in filePaths
                                     if _isExcelLike(filePath) and _isDateLike(filePath)]
    maxPath: pth.Path = max(filePaths,
                            key=lambda p: _getDate(p.stem))
    return _readExcelDbx(path=maxPath, sheetName=sheetName, indexCol=indexCol)


if __name__ == '__main__':
    # items = dbx.listPath("Pacifico/Chile/IPC/Proyecciones")
    # print(items)
    print(getDataProyecciones())
