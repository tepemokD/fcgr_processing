from .setup import COEF_CONV_METHOD

from numpy import isnan
from math import log


class Criteria:
    def __init__(self,
                 type_criteria: list[str],
                 **kwargs):
        assert all(type_cr in ('all',
                               'cycle_end',
                               'R_square',
                               'cycle_all',
                               'comparison') for type_cr in type_criteria), "The criteria type is incorrect"
        self.type_criteria = type_criteria

        self.result = dict()

    def _cycleend(self,
                  cycle_experimental: float,
                  cycle_calculated: float) -> float:
        """
        The relative error at the last point
        Rationing to one
        :param cycle_experimental: The experimental number of cycles
        :param cycle_calculated: The calculated number of cycle
        :return: relative error cycle
        """
        return 1 - abs(cycle_experimental - cycle_calculated) / cycle_experimental

    def _rsquare(self,
                 cycle_experimental: list[float],
                 cycle_calculated: list[float]) -> float:
        """
        R-square coefficient
        :param cycle_experimental: sequence of experimental cycle values
        :param cycle_calculated: sequence of calculated cycle values
        :return: value R-square coefficient
        """
        cycle_experimental_mean = sum(cycle_experimental) / len(cycle_experimental)

        sum_square_experimental = 0
        for cycle in cycle_experimental:
            sum_square_experimental += pow(cycle - cycle_experimental_mean, 2)

        sum_square_error = 0
        for index in range(len(cycle_experimental)):
            sum_square_error += pow(cycle_experimental[index] - cycle_calculated[index], 2)

        return 1 - sum_square_error / sum_square_experimental

    def _cycleall(self,
                  cycle_experimental: list[float],
                  cycle_calculated: list[float]) -> float:
        """
        Maximum relative error at the all point
        Rationing to one
        :param cycle_experimental: sequence of experimental cycle value
        :param cycle_calculated: sequence if calculated cycle value
        :return: maximum relative error of cycles
        """
        max_error_cycle = 0

        for index in range(1, len(cycle_experimental)):
            max_error_cycle = max(max_error_cycle,
                                  abs(cycle_experimental[index] - cycle_calculated[index]) / cycle_experimental[index])
        return 1 - max_error_cycle

    def _comparison(self,
                    range_sif_experimental: list[float],
                    cgr_experimental: list[float],
                    coefficient_c: float,
                    exponents_n: float) -> dict[str: float]:
        """
        Comparison of the experimental values of the crack growth rate with the calculated coefficients
        of the Paris equation
        Paper "Влияние частоты нагружения на закономерности и механизмы роста усталостных трещин в титановых сплавах.
        Сообщение 1. Матохнюк Л.Е., Ордынский В.С. Проблемы прочности - 1988 №1 стр. 17-21"
        Paper "Влияние частоты нагружения на закономерности и механизмы роста усталостных трещин в титановых сплавах.
        Сообщение 2. Матохнюк Л.Е., Яковлева Т.Ю. Проблемы прочности - 1988 №1 стр. 21-31"
        :param range_sif_experimental: experimental SIF range
        :param cgr_experimental: experimental crack growth rate
        :param coefficient_c: coefficient c Paris equation
        :param exponents_n: exponents n Paris equation
        :return: error coefficients
        """
        cgr_experimental, range_sif_experimental = tuple(zip(*[el for el in
                                                               zip(cgr_experimental, range_sif_experimental)
                                                               if ((not isnan(el[0])) and el[0] > 0)]))

        experimental_n = list(map(lambda x, y: log(y / coefficient_c, x),
                                  range_sif_experimental,
                                  cgr_experimental))

        max_error = 0
        for exp in experimental_n:
            max_error = max(max_error, abs(exp - exponents_n) / exp)

        return 1 - max_error

    def calculatecriteria(self) -> None:
        """
        Calculation of criteria values
        :return: None
        """
        self.result['cycle_end'] = self._cycleend(self.cgua.specimen.cycle_crack[self.fn23],
                                                  self.cycle_calculate[-1])
        self.result['R_square'] = self._rsquare(self.cgua.specimen.cycle_crack[self.fn12:self.fn23 + 1],
                                                self.cycle_calculate)
        self.result['cycle_all'] = self._cycleall(self.cgua.specimen.cycle_crack[self.fn12:self.fn23 + 1],
                                                  self.cycle_calculate)

        self.result['comparison'] = self._comparison(self.rangesif[self.fn12:self.fn23 + 1],
                                                     self.fcg[self.fn12:self.fn23 + 1],
                                                     self.coefficient_c,
                                                     self.exponent_n)

    def isright(self) -> bool:
        """
        The accuracy of the calculated values of the criteria
        :return: True - the accuracy is acceptable
        """
        assert self.result, "Need use calculatecriteria() method"

        if 'all' in self.type_criteria:
            for key in self.result.keys():
                if self.result[key] < COEF_CONV_METHOD:
                    return False
        else:
            for key in self.type_criteria:
                if self.result[key] < COEF_CONV_METHOD:
                    return False

        self.done = True

        return True
