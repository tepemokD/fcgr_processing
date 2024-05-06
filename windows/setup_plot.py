NUMERIC_SCATTER = 100

POSITION_LEGEND_MAIN = (-30, -30)
POSITION_LEGEND_MEIN = (0, -100)

COLOR_LEGEND = 'w'
VERTICAL_SPACING_LEGEND = 0
HORIZONTAL_SPACING_LEGEND = 20
WIDTH_LINE_CRITERIA = 2
LEGEND_CRITERIA = {'cycle_end': (f'last &Delta;N', dict(color=(230, 40, 5),
                                                        width=WIDTH_LINE_CRITERIA)),
                   'R_square': (f'R<sup>2</sup>', dict(color=(0, 0, 128),
                                                       width=WIDTH_LINE_CRITERIA)),
                   'cycle_all': (f'max(&Delta;N)', dict(color=(11, 102, 35),
                                                        width=WIDTH_LINE_CRITERIA)),
                   'comparison': (f'Paris', dict(color=(153, 0, 204),
                                                 width=WIDTH_LINE_CRITERIA))}

RESULT_LINE = dict(color=(230, 40, 5),
                   width=2)
SIZE_SCATTER_RESULT = 10
EDGE_SCATTER_RESULT = dict(color=(0, 0, 0),
                           width=1)
BODY_SCATTER_RESULT = (178, 178, 178)

SIZE_SCATTER_EXPERIMENT = 5
EDGE_SCATTER_EXPERIMENT = dict(color=(0, 0, 0),
                               width=1)
BODY_SCATTER_EXPERIMENT = (255, 255, 255)

SIZE_SCATTER_DATA = 6
EDGE_SCATTER_DATA = dict(color=(0, 0, 0),
                         width=1)
BODY_SCATTER_DATA = (178, 178, 178)
TEXT_ABOUT = (f"Программа обработки СРТУ - это программа, в которой реализован итерационный метод обработки результатов"
              f" испытний образца на скорость роста трещины усталости.\n\n"
              f"Март 2024. Версия 1.0")

RAZMERNOST = {'length': {'si': 'мм', 'si2': 'мм'},
              'force': {'si': 'кгс', 'si2': 'kN'},
              'SIF': {'si': 'кгс/мм^3/2', 'si2': 'МПа мм'},
              'coefficient_C': {'si': '--', 'si2': '---'}}

TYPE_SPECIMEN_NAME_PROGRAM = ('C(T) specimen', 'SENB specimen')
TYPE_SPECIMEN_NAME_IMSPECIMEN = ('compact_tension', 'single_edge_notch_beam')

TYPE_SPECIMEN_NAME = dict(zip(TYPE_SPECIMEN_NAME_PROGRAM, TYPE_SPECIMEN_NAME_IMSPECIMEN))

FILE_WINDOW_UI = r'windows_ui\main_window_programme.ui'
FILE_WINDOW_MEAN_UI = r'windows_ui\window_paris_mean.ui'
FILE_WINDOW_SIF_UI = r'windows_ui\window_SIF_range.ui'
FILE_WINDOW_UNITS_UI = r'windows_ui\conversion_units.ui'

IMAGE_CT_SPECIMEN = r'images\specimen_C(T).png'
IMAGE_SENB_SPECIMEN = r'images\specimen_SENB.png'
