from .setup import FORMAL_V23
from .calculate import derivativeinterpolatecubicspline, interpolatecubicspline

import numpy as np


class FCGR:
    def __init__(self,
                 methodfcg: str = 'Polynomial',
                 **kwargs):
        super().__init__(**kwargs)

        assert methodfcg in ('Polynomial', 'Secant', 'Cybic_Spline_Derivative'), "The type differentiation is incorrect"
        self.method_fcg = methodfcg

        self.formal_23_specimen: dict = None
        self.fcgr_sample: list = None

    def _fgcrsecant(self) -> None:
        """
        Creating a sequence with the rate of fatigue crack growth. The secant method. ASTM E647 X1.1
        :return: None
        """
        temp_length_fcg = []
        for index in range(self.num_point - 2):
            temp_length_fcg.append(((self.length_crack[index] + self.length_crack[index + 1]) / 2,
                                    (self.length_crack[index + 1] - self.length_crack[index]) /
                                    (self.cycle_crack[index + 1] - self.cycle_crack[index])))

        temp_length_fcg.sort(key=lambda x: x[0])

        fcg_interp = interpolatecubicspline(*list(zip(*temp_length_fcg)))
        self.fcgr_sample = fcg_interp(self.length_crack)

    def _fcgrpolynomial(self) -> None:
        """
        Creating a sequence with the rate of fatigue crack growth. The method of differentiation of a polynomial of
        degree 7. ASTM E647 X1.2 and IS 1 92127-90 7.3.4
        num_point_break - the number of points at the beginning and at the end processed by the cubic spline
        :return: None
        """
        num_point_break = 4
        length_crack_fcg = []
        fcg_crack = []
        for i in range(num_point_break, self.num_point - num_point_break):
            c1 = (self.cycle_crack[i - 3] + self.cycle_crack[i + 3]) / 2
            c2 = (self.cycle_crack[i + 3] - self.cycle_crack[i - 3]) / 2
            p11 = 7.0
            bb1 = sum(self.length_crack[i - 3:i + 4])
            p22 = 0.0
            p33 = 0.0
            p12 = 0.0
            p13 = 0.0
            p23 = 0.0
            bb2 = 0.0
            bb3 = 0.0
            for m in range(-3, 4):
                p22 += ((self.cycle_crack[m + i] - c1) / c2) ** 2
                p33 += ((self.cycle_crack[m + i] - c1) / c2) ** 4
                p12 += ((self.cycle_crack[m + i] - c1) / c2)
                p13 += ((self.cycle_crack[m + i] - c1) / c2) ** 2
                p23 += ((self.cycle_crack[m + i] - c1) / c2) ** 3
                bb2 += self.length_crack[m + i] * (self.cycle_crack[m + i] - c1) / c2
                bb3 += self.length_crack[m + i] * (((self.cycle_crack[m + i] - c1) / c2) ** 2)
            b0 = (p12 * p23 * bb3 - p12 * bb2 * p33 + p23 * bb2 * p13 - p13 * bb3 * p22 - bb1 * (
                    p23 ** 2) + bb1 * p22 * p33) / (
                         -p33 * (p12 ** 2) - p11 * (p23 ** 2) + 2 * p23 * p13 * p12 + p11 * p22 * p33 - p22 * (
                         p13 ** 2))
            b1 = (-p11 * p23 * bb3 + bb2 * p11 * p33 + p13 * p12 * bb3 - p12 * p33 * bb1 + p23 * p13 * bb1 - bb2 * (
                    p13 ** 2)) / (
                         -p33 * (p12 ** 2) - p11 * (p23 ** 2) + 2 * p23 * p13 * p12 + p11 * p22 * p33 - p22 * (
                         p13 ** 2))
            b2 = (p12 * p13 * bb2 + p23 * p12 * bb1 - p11 * p23 * bb2 - bb1 * p13 * p22 - bb3 * (
                    p12 ** 2) + bb3 * p11 * p22) / (
                         -p33 * (p12 ** 2) - p11 * (p23 ** 2) + 2 * p23 * p13 * p12 + p11 * p22 * p33 - p22 * (
                         p13 ** 2))

            length_crack_fcg.append(
                b0 + b1 * (self.cycle_crack[i] - c1) / c2 + b2 * (((self.cycle_crack[i] - c1) / c2) ** 2))
            fcg_crack.append(b1 / c2 + 2 * b2 * (self.cycle_crack[i] - c1) / (c2 ** 2))

        # Cubic spline
        der_fcg = derivativeinterpolatecubicspline(self.cycle_crack, self.length_crack)
        fcgr_sample_themp_temp = der_fcg(self.cycle_crack)

        i = 0
        temp_length_fcg = []
        while self.length_crack[i] < length_crack_fcg[0]:
            temp_length_fcg.append((self.length_crack[i], fcgr_sample_themp_temp[i]))
            i += 1
        temp_length_fcg.sort(key=lambda x: x[0])

        length_crack_fcg = [el[0] for el in temp_length_fcg] + length_crack_fcg
        fcg_crack = [el[1] for el in temp_length_fcg] + fcg_crack

        i = self.num_point - 1
        temp_length_fcg = []
        while self.length_crack[i] > length_crack_fcg[-1]:
            temp_length_fcg.append((self.length_crack[i], fcgr_sample_themp_temp[i]))
            i -= 1
        length_crack_fcg = length_crack_fcg + [el[0] for el in temp_length_fcg][::-1]
        fcg_crack = fcg_crack + [el[1] for el in temp_length_fcg][::-1]

        # fcg_interp = interpolatecubicspline(length_crack_fcg, fcg_crack)
        # self.fcgr_sample = fcg_interp(self.length_crack)

        self.fcgr_sample = np.interp(self.length_crack, length_crack_fcg, fcg_crack)

    def _fcgcsd(self) -> None:
        """
        Creating a sequence with the rate of fatigue crack growth. The method of differentiation of a cubic spline.
        :return: None
        """
        der_fcg = derivativeinterpolatecubicspline(self.cycle_crack, self.length_crack)
        self.fcgr_sample = der_fcg(self.cycle_crack)

    def createfcg(self) -> None:
        """
        Creating a sequence with the rate of fatigue crack growth.
        :return: None
        """
        if self.method_fcg == 'Polynomial':
            self._fcgrpolynomial()
        elif self.method_fcg == 'Secant':
            self._fgcrsecant()
        elif self.method_fcg == 'Cybic_Spline_Derivative':
            self._fcgcsd()

    def searchformalv23(self) -> bool:
        """
        Parameters of the experimental point before the formal upper bound
        :return: True - formal_23_specimen calculated, False - not
        """
        i = self.num_point - 1

        while i >= 0 and (self.fcgr_sample[i] > FORMAL_V23 or np.isnan(self.fcgr_sample[i]) or self.fcgr_sample[i] < 0):
            i -= 1

        if i >= 0:
            self.formal_23_specimen = {'length': self.length_crack[i],
                                       'cycle': self.cycle_crack[i],
                                       'range_SIF': self.value(self.length_crack[i]),
                                       'gr': self.fcgr_sample[i],
                                       'numeric_point': i + 1}
            return True
        else:
            return False


class CrackGrowthUniAxial:
    def __init__(self,
                 specimen):
        self.specimen = specimen

    def crackgrowthvolume_paris(self,
                                propertis: dict[str: dict],
                                start_length: float,
                                end_length: float) -> float:
        """
        Calculation of the number of cycle of fatigue crack growth
        :param propertis: crack grwoth rate properties (Paris)
        :param start_length: the length of the initial crack
        :param end_length: the length of the final crack
        :return: number of crack growth cycle
        """
        length_calculate = start_length
        cycle_calculate = 0
        while length_calculate < end_length:
            length_calculate += propertis['coefficient_c'] * pow(self.specimen.value(length_calculate),
                                                                 propertis['exponent_n'])
            cycle_calculate += 1
        return cycle_calculate

    def crackgrowtharray(self,
                         properties: dict[str: dict],
                         interval: list,
                         cycle_start: int = 0) -> tuple[list[float], list[float]]:
        """
        Calculation of the number of cycle of fatigue crack growth
        :param properties: crack growth rate properties (Paris)
        :param interval:
        :param cycle_start: first number cycle
        :return: number of crack growth length, number of crack growth cycle
        """
        length_calculate = interval[0]
        end_length = interval[-1]
        cycle_calculate = 0 + cycle_start
        cycle_array = [cycle_calculate]
        length_array = [length_calculate]
        index_interval = 1
        while length_calculate < end_length:
            length_calculate += properties['coefficient_c'] * pow(self.specimen.value(length_calculate),
                                                                  properties['exponent_n'])
            cycle_calculate += 1

            if length_calculate >= interval[index_interval]:
                length_array.append(length_calculate)
                cycle_array.append(cycle_calculate)
                index_interval += 1
        return length_array, cycle_array
