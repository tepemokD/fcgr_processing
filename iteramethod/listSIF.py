from .setup import *

from .rwfile import readtwoarray, readciamfile
from .calculate import interpolatecubicspline, interlinear

from math import pow, sqrt, pi
from typing import Union


class RangeSIF:
    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)

        if self.type_sp == 'compact_tension':
            self.value = self._sif_ct
        elif self.type_sp == 'single_edge_notch_beam':
            self.value = self._sif_senb

        self.calc_length = self._length_specimen

        self.load_max: float = None
        self.asymmetry: float = None
        self.length_load: list = None
        self.load_range: list = None
        self.length_sif: list = None
        self.sif_range: list = None

        self.coef_units = 1

    def _sif_ct(self,
                length_crack: float) -> float:
        """
        Get sif of crack CT specimen. Murakamy, volume 1, article 1.7, page 57
        :param length_crack: crack length
        :return: sif of crack CT specimen
        """
        alfa = (self.a0 + length_crack) / self.w
        function = ((2 + alfa) *
                    (0.886 + 4.64 * alfa - 13.32 * pow(alfa, 2) + 14.72 * pow(alfa, 3) - 5.6 * pow(alfa, 4)) /
                    pow(1 - alfa, 3 / 2))
        sif_ct = function * self._range_load(self.a0 + length_crack) / (self.b * sqrt(self.w))

        return sif_ct * self.coef_units

    def _sif_senb(self,
                  length_crack: float) -> float:
        """
        Get sif of crack SENB specimen S = 4W. Murakamy, volume 1, article 1.5, page 54
        :param length_crack: length crack
        :return: sif of crack SENB specimen
        """
        alfa = (self.a0 + length_crack) / self.w
        function = ((1.99 - alfa * (1 - alfa) * (2.15 - 3.93 * alfa + 2.7 * pow(alfa, 2))) /
                    ((1 + 2 * alfa) * pow(1 - alfa, 3 / 2)))
        sif_senb = (3 * (4 * self.w) * self._range_load(self.a0 + length_crack) *
                    sqrt(pi * (self.a0 + length_crack)) * function / (2 * self.b * pow(self.w, 2)))

        return sif_senb * self.coef_units

    def _load_const_load_max(self,
                             *args) -> float:
        """
        Get the load range
        :return: load range
        """
        return self.load_max * (1 - self.asymmetry)

    def _length_specimen(self,
                         range_sif: float) -> float:
        """
        Get length of crack specimen.
        :param range_sif: SIF range of crack
        :return: length of crack CT specimen
        """
        if self.type_load == 'user_load':
            length_start = self.length_sif[0]
            length_end = self.length_sif[-1]
        else:
            length_start = 0
            length_end = self.w - self.a0
        while length_end - length_start > COEF_CONV_LENGTH:
            mean_length = (length_start + length_end) / 2
            if self.value(mean_length) > range_sif:
                length_end = mean_length
            else:
                length_start = mean_length

        return mean_length

    def setloads(self,
                 param: Union[dict, str],
                 delta_length: float = 0,
                 delta_load: float = 0,
                 type_file: str = 'txt') -> None:
        """
        Setting the loading parameters of the specimen
        :param param: Dictionary with loading parameters or name file with table length and load
        :param delta_length: reducing the size of the crack length
        :param delta_load: reducing the size of load
        :param type_file: txt - only dP(L), ciam - file machine
        :return: None
        """
        assert self.type_load != 'user_SIF', "Not use the module 'setloads' for load type 'user_SIF'"

        if self.type_load == 'cyclic_const_load_max':
            self.load_max = param['Pmax']
            self.asymmetry = param['R']
            self._range_load = self._load_const_load_max
        elif self.type_load == 'user_load':
            if type_file == 'txt':
                self.length_load, self.load_range = readtwoarray(param,
                                                                 delta_load,
                                                                 delta_length)
                self._range_load = interpolatecubicspline(self.length_load,
                                                          self.load_range)
            elif type_file == 'ciam':
                self.length_load, self.load_range = readciamfile(param,
                                                                 delta_load,
                                                                 delta_length,
                                                                 name_col='dPL')
                self._range_load = interlinear(self.length_load,
                                               self.load_range)

    def setsif(self,
               name_file: str,
               delta_length: float = 0,
               delta_sif: float = 0) -> None:
        """
        Setting experimental data: crack length, range SIF
        :param name_file: Name file with crack length and range SIF
        :param delta_length: reducing the size of the crack length
        :param delta_sif:reducing the sif range
        :return:
        """
        assert self.type_load == 'user_SIF', "Only for type load 'user_SIF'"
        self.length_sif, self.sif_range = readtwoarray(name_file, delta_length, delta_sif)
        self.value = interpolatecubicspline(self.length_sif, self.sif_range)

    def use_si(self) -> None:
        """
        Change self.coef_units for si: force - kN, length - mm, sif - MPa*mm^1/2
        :return: None
        """
        self.coef_units = pow(10, 3 / 2)

    def array(self,
              lengths: list[float]) -> list[float]:
        """
        The array of SIF range is calculated from the array of crack lengths
        :param lengths: array crack lengths
        :return: array SIF range
        """
        if self.type_load == 'user_SIF':
            return self.value(lengths)
        else:
            return [self.value(length) for length in lengths]
