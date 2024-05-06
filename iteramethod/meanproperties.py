from .setup import *

from .rwfile import readfivearray

from .crackgrowthrate import CrackGrowthUniAxial
from .imspecimens import Specimen
from .iterativemethod import IterativeMethod

import numpy as np
from statsmodels.stats.diagnostic import het_breuschpagan as tbp
from statsmodels.stats.diagnostic import het_goldfeldquandt as tgk

import statsmodels.api as sm


class MeanProperties:
    def __init__(self,
                 mode: str,
                 border_sif: str,
                 si: bool = False):
        super().__init__()

        assert mode in ('focal_point', 'mean_curve'), "Incorrect mode"
        self.mode = mode
        self.si = si

        if self.mode == 'focal_point':
            self.calculate = self._focal_point
            self.fp_sif_range: float
            self.fp_fcgr: float
        elif self.mode == 'mean_curve':
            self.calculate = self._mean_curve

        self.text_error: str = f""

        assert border_sif in ('minimum', 'mean', 'maximum'), "Incorrect border_sif"
        self.border_sif = border_sif

        if self.border_sif == 'minimum':
            self._method_sif12 = np.max
            self._method_sif23 = np.min
        elif self.border_sif == 'mean':
            self._method_sif12 = np.mean
            self._method_sif23 = np.mean
        elif self.border_sif == 'maximum':
            self._method_sif12 = np.min
            self._method_sif23 = np.max

        self.coefficient_c_array: list
        self.exponent_n_array: list
        self.sif12_range_array: list
        self.sif23_range_array: list
        self.temperature_array: list

        self.num_specimen: int = None
        self.num_temperature: dict = None
        self.num_sif12: dict = None
        self.num_sif23: dict = None

        self.num_properties: dict = None

    def __repr__(self):
        if not self.num_properties:
            return "There is no result"
        text = (f"Mode: {self.mode}\n"
                f"Border sif: {self.border_sif}\n")
        text += f"\n"

        text += f"The number of specimens: {self.num_specimen}\n"
        text += f"Temperature\tNumber specimens\n"
        for temperature in self.num_temperature.keys():
            text += f"{temperature}\t{self.num_temperature[temperature]}\n"

        text += f"\n"

        if self.mode == 'focal_point':
            text += "delta K_fp\tV_fp\n"
            text += f"{self.fp_sif_range:.2f}\t{self.fp_fcgr:.4e}\n"
            text += f"\n"

        text += "Coefficient C\tExponent n\tdelta K_min\tdelta K_max\tTemperature\n"
        for temperature in self.num_temperature.keys():
            text += (f"{self.num_properties[temperature][1]:.4e}\t"
                     f"{self.num_properties[temperature][0]}\t"
                     f"{self.num_sif12[temperature]:.2f}\t"
                     f"{self.num_sif23[temperature]:.2f}\t"
                     f"{temperature}\n")
        return text

    def set_file(self,
                 file_name: str) -> None:
        """
        Set data of specimens
        :param file_name: file name with data of specimens
        :return: None
        """
        (self.coefficient_c_array, self.exponent_n_array, self.sif12_range_array,
         self.sif23_range_array, self.temperature_array) = readfivearray(file_name)

        self.num_specimen = len(self.coefficient_c_array)

        value, count = np.unique(self.temperature_array, return_counts=True)
        self.num_temperature = dict(zip(value, count))

    def calculate_border_sif(self) -> None:
        """
        Calculating the boundaries of mean properties
        :return: None
        """
        self.num_sif12 = dict()
        self.num_sif23 = dict()
        for temperature in self.num_temperature.keys():
            sif12 = self._method_sif12(self.sif12_range_array[np.where(self.temperature_array == temperature)])
            sif23 = self._method_sif23(self.sif23_range_array[np.where(self.temperature_array == temperature)])

            self.num_sif12[temperature] = sif12
            self.num_sif23[temperature] = sif23

    def _focal_point(self) -> None:
        """
        Determination of average properties within the specified SIF boundaries using a focal point
        :return: None
        """
        self.calculate_border_sif()
        y = np.log10(self.coefficient_c_array)
        x = self.exponent_n_array

        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = np.dot(x, y)
        sum_square_x = np.dot(x, x)
        n = self.num_specimen

        # lgC = a + b * n
        b = (sum_x * sum_y - n * sum_xy) / (pow(sum_x, 2) - n * sum_square_x)
        a = (sum_y - b * sum_x) / n

        self._corr_fp(a, b)
        self.fp_sif_range = pow(10, -b)
        self.fp_fcgr = pow(10, a)

        self.num_properties = dict()
        for temperature in self.num_temperature.keys():
            mean_exponent_n = np.mean(self.exponent_n_array[np.where(self.temperature_array == temperature)])
            mean_exponent_n = round(mean_exponent_n, int(np.log10(1 / COEF_CONV_INCREMENT)))
            mean_coefficient_c = self._focal_point_c(mean_exponent_n)

            self.num_properties[temperature] = (mean_exponent_n, mean_coefficient_c)

    def _focal_point_c(self,
                       exp_n: float) -> float:
        """
        Calculation of the coefficient c using the coordinates of the focal point
        :param exp_n: exponent n
        :return: coefficient c
        """
        return pow(10, np.log10(self.fp_fcgr) - np.log10(self.fp_sif_range) * exp_n)

    def _corr_fp(self,
                 a: float,
                 b: float) -> None:
        """
        Determination of the correlation coefficient and checking for homoscedasticity.
        lgC = a + b * n
        :param a: Coefficient of the focal point equation
        :param b: Coefficient of the focal point equation
        :return: None
        """
        exp_n_mean = sum(self.exponent_n_array) / len(self.exponent_n_array)
        error_calc = 0
        error_exp = 0
        for index in range(len(self.exponent_n_array)):
            error_calc += pow(self.exponent_n_array[index] - ((np.log10(self.coefficient_c_array[index]) - a) / b), 2)
            error_exp += pow(self.exponent_n_array[index] - exp_n_mean, 2)

        r_square = 1 - error_calc / error_exp

        if r_square < COEF_CONV_METHOD_FP:
            self.text_error += (f"Коэффициент корреляции координат фокусной точки {r_square:.2f}, что меньше "
                                f"допустимого. Рекомендуется воспользоваться другим методом расчета.")

        x = sm.add_constant(np.log10(self.coefficient_c_array))
        y_error = [abs(self.exponent_n_array[index] - (np.log10(self.coefficient_c_array[index]) - a) / b)
                   for index in range(len(self.coefficient_c_array))]

        _, p_value1, _, _ = tbp(y_error, x)
        _, p_value2, _ = tgk(self.exponent_n_array, x)

        if p_value1 < COEF_HOMOSCEDASTICITY_FP or p_value2 < COEF_HOMOSCEDASTICITY_FP:
            self.text_error += (f"При определении координат фокусной точки не выполнено условие гомоскедастичности. "
                                f"Рекомендуется воспользоваться другим методом расчета.")

    def _mean_curve(self) -> None:
        """
        Determination of average properties within the specified KIN boundaries using curve averaging
        :return: None
        """
        self.calculate_border_sif()

        self.num_properties = dict()
        for temperature in self.num_temperature.keys():
            self.num_properties[temperature] = self._mean_curve_one_temp(
                sif12_range=self.num_sif12[temperature],
                sif23_range=self.num_sif23[temperature],
                n_array=self.exponent_n_array[np.where(self.temperature_array == temperature)],
                c_array=self.coefficient_c_array[np.where(self.temperature_array == temperature)])

    def _mean_curve_one_temp(self, sif12_range: float,
                             sif23_range: float,
                             n_array: list[float],
                             c_array: list[float]) -> tuple[float, float]:
        """
        Determination of average properties within the specified KIN boundaries by averaging curves
        for a single temperature
        :param sif12_range: bottom edge
        :param sif23_range: low edge
        :param n_array: exponents array
        :param c_array: coefficients array
        :return: (exponent n, coefficient c)
        """
        assert sif12_range < sif23_range, 'Incorrect: sif12_range > sif23_range'

        specimen = Specimen.create_simple_specimen(type_specimen='compact_tension',
                                                   w=FORMAL_SPECIMEN['W'],
                                                   b=FORMAL_SPECIMEN['B'],
                                                   a0=FORMAL_SPECIMEN['a0'],
                                                   p_max=FORMAL_SPECIMEN['P_MAX'] if not self.si
                                                   else FORMAL_SPECIMEN['P_MAX_SI'],
                                                   r=FORMAL_SPECIMEN['R'],
                                                   si=self.si
                                                   )

        length12_crack = specimen.calc_length(sif12_range)
        length23_crack = specimen.calc_length(sif23_range)

        length_array = np.linspace(length12_crack,
                                   length23_crack,
                                   num=FORMAL_SPECIMEN['NUM_POINT'])

        calculate = CrackGrowthUniAxial(specimen)

        n_specimen = len(n_array)
        cycle_array = [0] * FORMAL_SPECIMEN['NUM_POINT']

        for index_sp in range(n_specimen):
            _, cycle_crack = calculate.crackgrowtharray(properties={'coefficient_c': c_array[index_sp],
                                                                    'exponent_n': n_array[index_sp]},
                                                        interval=length_array)
            for index_cycle in range(FORMAL_SPECIMEN['NUM_POINT']):
                cycle_array[index_cycle] += cycle_crack[index_cycle]

        for index_cycle in range(FORMAL_SPECIMEN['NUM_POINT']):
            cycle_array[index_cycle] /= n_specimen

        specimen.setcrackgrowth_array(cycle_array,
                                      length_array)
        paris = IterativeMethod(type_criteria=[],
                                type_calcutaion='border')
        paris.setspecimen(specimen)
        result = paris.edge(start=0,
                            end=FORMAL_SPECIMEN['NUM_POINT'] - 1)

        exponent_n = result['exponent_n']
        coefficient_c = result['coefficient_c']

        return exponent_n, coefficient_c


if __name__ == "__main__":
    pass
