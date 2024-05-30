import numpy as np
from typing import Tuple


def readtwoarray(name_file: str,
                 delta_y: float,
                 delta_x: float) -> Tuple[list, list]:
    """
    Reading two vectors from a file
    :param name_file: name file
    :param delta_x: reducing x
    :param delta_y: reducing y
    :return: a tuple of two arrays
    """
    with open(name_file, 'r', encoding="utf8") as file:
        list_line = file.read().replace(',', '.').splitlines()
    x_array, y_array = np.genfromtxt(list_line, skip_header=1, unpack=True)

    return x_array - delta_x, y_array - delta_y

def readciamfile(name_file: str,
                 delta_y: float,
                 delta_x: float,
                 name_col: str = 'LN') -> Tuple[list, list] or Tuple[float, float]:
    """

    :param name_file: name file
    :param delta_y: reducing y
    :param delta_x: reducing x
    :param name_col:
    :return: a tuple of two arrays
    """
    with open(name_file, 'r', encoding="utf8") as file:
        list_line = file.read().replace(',', '.').splitlines()

    # list_line убрать пустые строки, убрать три строки, убрать 0-1, 4-12 столбцы
    i = 0
    while not list_line[i].strip():
        i += 1
    list_line = list_line[i + 3:]
    n = len(list_line)
    x_array = np.array([0.0] * n)
    y_array = np.array([0.0] * n)
    str_to_float = lambda num: float(num.strip().rstrip(';'))
    for i in range(n):
        if name_col == 'LN':
            _, _, y_array_i, x_array_i, _, _, _, _, _, _, _, _, _ = list_line[i].split()
        elif name_col == 'Pconst':
            _, _, _, _, x_array_i, _, _, _, y_array_i, _, _, _, _ = list_line[i].split()
        elif name_col == 'dPL':
            _, _, x_array_i, _, y_max, y_min, _, _, _, _, _, _, _ = list_line[i].split()
            y_array_i = str(str_to_float(y_max) - str_to_float(y_min))
        x_array[i] = str_to_float(x_array_i)
        y_array[i] = str_to_float(y_array_i)

    if name_col == 'Pconst':
        return np.mean(x_array), np.mean(y_array)

    return x_array - delta_x, y_array - delta_y


def readfivearray(name_file: str) -> Tuple[list, list, list, list, list]:
    """
    Reading five vectors from a file
    :rtype: object
    :param name_file:
    :return: a tuple of five arrays
    """
    with open(name_file, 'r', encoding="utf8") as file:
        list_line = file.read().replace(',', '.').splitlines()
    array1, array2, array3, array4, array5 = np.genfromtxt(list_line, skip_header=1, unpack=True)

    return array1, array2, array3, array4, array5


if __name__ == "__main__":
    pass
