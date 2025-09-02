import pathlib as pth

_ROOT_SRC = pth.Path(__file__).parents[1]

PATH_LOGO: pth.Path = pth.Path(__file__).parent / "images" / "Logo_Pacifico.jpg"
PATH_BOKEH_THEME: pth.Path = _ROOT_SRC / "core" / "Style" / "bokeh_themes" / "pacifico_theme.yml"
ROOT_TEMP_IMG_PLOTS: pth.Path = _ROOT_SRC / "core" / "Plot" / "tmp"
PATH_TEMPLATE_EXCEL: pth.Path = _ROOT_SRC / "core" / "Plot" / "tmp" / "output.xlsx"

# if __name__ == '__main__':
#     print(f"{PATH_BOKEH_THEME = }")
#     print(f"{pth.Path(__file__).parents[1] = }")
#
#     print(f"\n {'#' * 20} \n")
#
#     print(f"{PATH_LOGO.is_file() = }")
#     print(f"{PATH_BOKEH_THEME.is_file() = }")
#     print(f"{ROOT_TEMP_IMG_PLOTS.is_dir() = }")
