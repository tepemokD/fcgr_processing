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
