from .setup import *
from .calculatecriteria import Criteria
from .crackgrowthrate import CrackGrowthUniAxial
from .imspecimens import Specimen

from math import log10


class IterativeMethod(Criteria):
    def __init__(self,
                 type_calculation: str = 'automatic',
                 **kwargs):
        assert type_calculation in ('automatic',
                                    'manual_search_low_border',
                                    'manual_search_bottom_border',
                                    'border'), "The calculation method is incorrect"
        self.type_calculation = type_calculation

        self.result: dict = dict()
        self.cycle_crack = None
        self.fn12: int = 0
        self.fn23: int = None
        self.coefficient_c: float = None
        self.exponent_n: float = None
        self.cgua: CrackGrowthUniAxial = None
        self.rangesif: list = None
        self.fcg: list = None
        self.done: bool = False

        self.parameters12: list = []
        self.parameters23: list = []

        self.check: bool = None

        super().__init__(**kwargs)

    def __repr__(self):
        if not self.coefficient_c and not self.cgua:
            return "There is no result"

        text = f"Type of calculation: {self.type_calculation}\n"
        text += f"Selected criteria: {', '.join(self.type_criteria)}\n"

        text += f"\n"
        if self.type_calculation == 'automatic' or self.type_calculation == 'border':
            text += f"Coefficient C\tExponent n\n"
            text += f"{self.coefficient_c:.4e}\t{self.exponent_n}\n"
            text += f"\n"

            text += f"length_min\tcycle_min\trange SIF_min\tV_min\tstart point\n"
            text += (f"{self.cgua.specimen.length_crack[self.fn12]:.4f}\t"
                     f"{self.cgua.specimen.cycle_crack[self.fn12]:.0f}\t"
                     f"{self.cgua.specimen.value(self.cgua.specimen.length_crack[self.fn12]):.2f}\t"
                     f"{self.cgua.specimen.fcgr_sample[self.fn12]:.4e}\t"
                     f"{self.fn12 + 1}\n")
            text += f"\n"

            text += f"length_max\tcycle_min\trange SIF_max\tV_max\tend point\n"
            text += (f"{self.cgua.specimen.length_crack[self.fn23]:.4f}\t"
                     f"{self.cgua.specimen.cycle_crack[self.fn23]:.0f}\t"
                     f"{self.cgua.specimen.value(self.cgua.specimen.length_crack[self.fn23]):.2f}\t"
                     f"{self.cgua.specimen.fcgr_sample[self.fn23]:.4e}\t"
                     f"{self.fn23 + 1}\n")
            text += f"\n"

            text += f"Values of criteria:\n"
            for key in self.result.keys():
                text += f"{key} = {self.result[key]:.6f}\n"

        elif self.type_calculation == 'manual_search_low_border':
            text += f"Search for the lower bound.\n"
            text += (f"Start point\tEnd point\tCoefficient C\tExponent n\t"
                     f"Criteria: Cycle end\tCriteria: R square\tCriteria: Cycle all\tCriteria: comparison\n")
            for index in range(len(self.parameters12)):
                text += (f"{self.parameters12[index]['point_numbers'][0] + 1}\t"
                         f"{self.parameters12[index]['point_numbers'][1] + 1}\t"
                         f"{self.parameters12[index]['coefficient_c']:.4e}\t"
                         f"{self.parameters12[index]['exponent_n']}\t"
                         f"{self.parameters12[index]['criteria']['cycle_end']:.6f}\t"
                         f"{self.parameters12[index]['criteria']['R_square']:.6f}\t"
                         f"{self.parameters12[index]['criteria']['cycle_all']:.6f}\t"
                         f"{self.parameters12[index]['criteria']['comparison']:.6f}\n")

        elif self.type_calculation == 'manual_search_bottom_border':
            text += f"Search for an upper bound.\n"
            text += (f"Start point\tEnd point\tCoefficient C\tExponent n\t"
                     f"Criteria: Cycle end\tCriteria: R square\tCriteria: Cycle all\tCriteria: comparison\n")
            for index in range(len(self.parameters23)):
                text += (f"{self.parameters23[index]['point_numbers'][0] + 1}\t"
                         f"{self.parameters23[index]['point_numbers'][1] + 1}\t"
                         f"{self.parameters23[index]['coefficient_c']:.4e}\t"
                         f"{self.parameters23[index]['exponent_n']}\t"
                         f"{self.parameters23[index]['criteria']['cycle_end']:.6f}\t"
                         f"{self.parameters23[index]['criteria']['R_square']:.6f}\t"
                         f"{self.parameters23[index]['criteria']['cycle_all']:.6f}\t"
                         f"{self.parameters23[index]['criteria']['comparison']:.6f}\n")

        text += "\n" + "-" * 70 + "\n"
        text += f"{self.cgua.specimen}\n"

        return text

    def _propertisparis(self) -> None:
        """
        Calculating the coefficient C and the exponent n of the Paris equation
        :return: None
        """
        exponent_n_left = START_EXPONENT_N
        exponent_n_right = END_EXPONENT_N

        constanta = (sum(self.cgua.specimen.length_crack[self.fn12:self.fn23 + 1]) -
                     self.cgua.specimen.length_crack[self.fn12] * (self.fn23 - self.fn12 + 1))

        # A special case
        if self._function_exponent(exponent_n_left, constanta)[0] * \
                self._function_exponent(exponent_n_right, constanta)[0] > 0:
            exponent_n_left = START_EXPONENT_N / 10
            exponent_n_right = END_EXPONENT_N * 10

        if self._function_exponent(exponent_n_left, constanta)[0] * \
                self._function_exponent(exponent_n_right, constanta)[0] > 0:
            assert False, "The exponent is not acceptable"

        index_error = 0
        exponent_n_mid = None
        while exponent_n_right - exponent_n_left > COEF_CONV_INCREMENT:
            exponent_n_mid = (exponent_n_left + exponent_n_right) / 2
            function_n_mid = self._function_exponent(exponent_n_mid, constanta)[0]

            if function_n_mid > 0:
                exponent_n_right = exponent_n_mid
            else:
                exponent_n_left = exponent_n_mid
            index_error += 1
            assert index_error < 10e5, "Exceeding the number of cycles. The exponent is not acceptable"

        coefficient_c = constanta / self._function_exponent(exponent_n_mid, constanta)[1]

        self.exponent_n = round(exponent_n_mid, int(log10(1 / COEF_CONV_INCREMENT)))
        self.coefficient_c = coefficient_c

    def _function_exponent(self,
                           exponent_n: float,
                           constanta: float) -> tuple[float, float]:
        """
        Calculating the exponent n function
        :param exponent_n: the exponent n of the Paris equation
        :param constanta: the constant C of the Paris equation
        :return: the exponent n function of n and the integral the sif range
        """
        range_sif_exp = map(lambda x: pow(x, exponent_n), self.rangesif[self.fn12:self.fn23 + 1])
        range_sif_exp = list(range_sif_exp)
        integral_sif = [0]
        for i in range(1, self.fn23 - self.fn12 + 1):
            integral_sif.append(integral_sif[-1] +
                                (self.cgua.specimen.cycle_crack[self.fn12 + i] -
                                 self.cgua.specimen.cycle_crack[self.fn12 + i - 1]) *
                                (range_sif_exp[i - 1] + range_sif_exp[i]) / 2)

        function_2 = sum(integral_sif)
        function_1 = 0
        for index in range(self.fn23 - self.fn12 + 1):
            function_1 += self.cgua.specimen.length_crack[self.fn12 + index] * integral_sif[index]
        function_3 = sum(map(lambda x: pow(x, 2), integral_sif))

        return (self.cgua.specimen.length_crack[self.fn12] * pow(function_2, 2) -
                function_1 * function_2 + constanta * function_3,
                function_2)

    def _calculate_length_cycle(self) -> None:
        """
        Calculate the length and number of cycles using the coefficient C and the exponent n
        :return: None
        """
        self.length_calculate, self.cycle_calculate = (
            self.cgua.crackgrowtharray({'coefficient_c': self.coefficient_c, 'exponent_n': self.exponent_n},
                                       self.cgua.specimen.length_crack[self.fn12:self.fn23 + 1],
                                       cycle_start=self.cgua.specimen.cycle_crack[self.fn12]))

    def setspecimen(self,
                    specimen: Specimen) -> None:
        """
        Setting instance "Specimen" class
        :param specimen: instance "Specimen" class
        :return: None
        """
        self.cgua = CrackGrowthUniAxial(specimen)
        self.rangesif = self.cgua.specimen.array(self.cgua.specimen.length_crack)
        self.cgua.specimen.createfcg()
        self.fcg = self.cgua.specimen.fcgr_sample
        self.cgua.specimen.searchformalv23()
        self.fn23 = self.cgua.specimen.formal_23_specimen['numeric_point'] - 1

    def search12(self) -> None:
        """
        Search for the lower bound. Result in parameters12
        :return: None
        """
        self.parameters12 = []

        if self.type_criteria:
            self.check = self.isright
        else:
            self.check = lambda: False

        while self.fn23 - self.fn12 + 1 > MIN_POINT and (not self.parameters12 or not self.check()):
            self._propertisparis()
            self._calculate_length_cycle()
            self.calculatecriteria()
            self.parameters12.append({'point_numbers': (self.fn12, self.fn23),
                                      'coefficient_c': self.coefficient_c,
                                      'exponent_n': self.exponent_n,
                                      'criteria': self.result.copy()})
            self.fn12 += 1
        self.fn12 -= 1

    def search23(self) -> None:
        """
        Search for the upper bound. Result in parameters23
        :return: None
        """
        self.parameters23 = []

        if self.type_criteria:
            self.check = self.isright
        else:
            self.check = lambda: True

        num_check = self.fn23
        num_start = self.fn23
        while self.fn23 < self.cgua.specimen.num_point:
            self._propertisparis()
            self._calculate_length_cycle()
            self.calculatecriteria()
            self.parameters23.append({'point_numbers': (self.fn12, self.fn23),
                                      'coefficient_c': self.coefficient_c,
                                      'exponent_n': self.exponent_n,
                                      'criteria': self.result.copy()})
            if not self.parameters23 or self.check():
                num_check = self.fn23
            self.fn23 += 1

        self.fn23 -= 1

        if num_check != self.fn23:
            self.coefficient_c = self.parameters23[num_check - num_start]['coefficient_c']
            self.exponent_n = self.parameters23[num_check - num_start]['exponent_n']
            self.result = self.parameters23[num_check - num_start]['criteria'].copy()
            self.parameters23 = self.parameters23[:num_check - num_start + 1]
            self.fn23 = num_check

    def auto(self) -> dict[str: tuple[float], str: float, str: float]:
        """
        Automatic mode bottom and low edge calculate
        :return: dict with a calculate result
        """
        self.search12()
        done = self.done
        self.search23()
        return {'point_numbers': (self.fn12, self.fn23),
                'coefficient_c': self.coefficient_c,
                'exponent_n': self.exponent_n,
                'criteria': done}

    def edge(self,
             start: int,
             end: int) -> dict[str: tuple[float], str: float, str: float]:
        """
        Calculation based on specified edge
        :param start: start number point
        :param end: end number point
        :return: dict with a calculate result
        """
        assert 0 <= start < self.cgua.specimen.num_point and 0 <= end < self.cgua.specimen.num_point and (
                end - start + 1 > MIN_POINT), "Value start and end is incorrect"

        self.fn12 = start
        self.fn23 = end

        self._propertisparis()
        self._calculate_length_cycle()
        self.calculatecriteria()

        return {'point_numbers': (start, end),
                'coefficient_c': self.coefficient_c,
                'exponent_n': self.exponent_n}
