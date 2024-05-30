import numpy as np
from PyQt6.QtWidgets import QMessageBox
from os.path import isfile

from numpy import isnan

from iteramethod.rwfile import readtwoarray, readfivearray, readciamfile
from iteramethod.setup import MIN_POINT, MAX_SIF_RANGE_CALCULATED, MIN_SPECIMEN_MEAN_ONE_TEMPERATURE


class Message:
    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)

    def checking_file_mean(self,
                           file: str,
                           column_all_check: tuple[str] = ('positive',)) -> None:
        """
        Checking the file for values
        :param file: file name
        :param column_all_check: checking for positive values
        :return: None
        """

        try:
            col_all = readfivearray(file)

        except Exception as error:
            QMessageBox.critical(self,
                                 "Ошибка при зачитывании данных файла",
                                 f'<span style="color:red;">{str(error)}</span>')

            return False

        if (any(isnan(col_all[0])) or any(isnan(col_all[1])) or any(isnan(col_all[2])) or
                any(isnan(col_all[3])) or any(isnan(col_all[4]))):
            QMessageBox.critical(self,
                                 "Ошибка при зачитывании данных из файла",
                                 "В файле приведены данные, которые не возможно идентифицировать как числа")

            return False

        for index in range(5):
            if self._column_check(col_all[index],
                                  column_all_check,
                                  "Ошибка в исходных данных"):
                print('check3')

                return False

        values, counts = np.unique(col_all[4], return_counts=True)
        temperatures = []
        for index in range(len(counts)):
            if counts[index] < MIN_SPECIMEN_MEAN_ONE_TEMPERATURE:
                temperatures.append(values[index])

        if temperatures:
            QMessageBox.warning(self,
                                "Предупреждение",
                                f"Для температур {', '.join(map(str, temperatures))} C недостаточное количество "
                                f"образцов (меньше {MIN_SPECIMEN_MEAN_ONE_TEMPERATURE}).<br>"
                                f"Результаты могут быть не корректны")

        return True

    def checking_file(self,
                      file: str,
                      title: str,
                      column1_check: tuple[str] = ('positive', 'increasing'),
                      column2_check: tuple[str] = ('positive', 'increasing'),
                      min_point: bool = False,
                      type_file: str = 'txt') -> bool:
        """
        Checking the file with numeric columns for errors.
        :param file: the path to the file
        :param title: the title of the error message
        :param column1_check: list of criteria for the column1
        :param column2_check: list of criteria for the column1
        :param min_point: checking minimum numer point
        :param type_file: checking type file: txt - only L and N, ciam - read file machine
        :return: bool: True - not error; False - error.
        """
        if not isfile(file):
            QMessageBox.critical(self,
                                 title,
                                 "Файла в указанной директории не существует.")

            return False

        try:
            if type_file == 'txt':
                col1, col2 = readtwoarray(file,
                                          delta_x=0,
                                          delta_y=0)
            elif type_file == 'ciam':
                col1, col2 = readciamfile(file,
                                          delta_x=0,
                                          delta_y=0,
                                          name_col='LN')
            elif type_file == 'ciam_dPL':
                col1, col2 = readciamfile(file,
                                          delta_x=0,
                                          delta_y=0,
                                          name_col='dPL')

        except Exception as error:
            QMessageBox.critical(self,
                                 title,
                                 f'<span style="color:red;">{str(error)}</span>')

            return False

        if any(isnan(col1)) or any(isnan(col2)):
            QMessageBox.critical(self,
                                 title,
                                 "В файле приведены данные, которые не возможно идентифицировать как числа")

            return False

        if min_point and len(col1) <= MIN_POINT:
            QMessageBox.critical(self,
                                 title,
                                 "Приведено мало данных")

            return False

        if self._column_check(col1,
                              column1_check,
                              title):
            return False

        if self._column_check(col2,
                              column2_check,
                              title):
            return False

        return True

    def checking_numbers(self,
                         file: str = None,
                         type_file: str = 'txt') -> bool:
        """
        Checking the numbers entered in the gui
        :return: bool: True - not error, False - error.
        """
        text = ""

        if self.Edit_a0_specimen.value() >= self.Edit_w_specimen.value():
            text += f"<span><br>- значение a<sub>0</sub> должно быть меньше значения W</span>"

        if file:
            if type_file == 'txt':
                _, col2 = readtwoarray(file,
                                       delta_x=0,
                                       delta_y=0)
            elif type_file == 'ciam':
                _, col2 = readciamfile(file,
                                       delta_x=0,
                                       delta_y=0,
                                       name_col='LN')

            if max(col2) >= self.Edit_w_specimen.value():
                text += f"<span><br>- значение W должно быть больше максимальной замеренной длины трещины</span>"

        if text:
            QMessageBox.critical(self,
                                 "Ошибка в задании размеров образца",
                                 text)
            return False
        return True

    def checking_col(self,
                     file1: str,
                     file2: str,
                     title: str,
                     type_file2: str = 'txt') -> bool:
        """

        :param file1: a file with two arrays
        :param file2: a file with two arrays
        :param title: name error
        :param type_file2: type file2: txt - file1 != file2, ciam - file1 == file2
        :return: bool: True - not error, False - error.
        """
        if type_file2 == 'ciam':
            return True

        _, col2 = readtwoarray(file1,
                               delta_x=0,
                               delta_y=0)
        col1, _ = readtwoarray(file2,
                               delta_x=0,
                               delta_y=0)
        if min(col1) > min(col2) or max(col1) < max(col2):
            QMessageBox.critical(self,
                                 title,
                                 "Заданная зависимость не перекрывает экспериментальные данные")
            return False
        return True

    @staticmethod
    def _column_increasing(column: np.array) -> bool:
        """
        Checking the column for ascending.
        :param column: a list with integers or floating number
        :return: bool: True - column not increasing: False - column increasing.
        """
        for index in range(1, len(column)):
            if column[index] <= column[index - 1]:
                return True
        return False

    @staticmethod
    def _column_positive(column: np.array) -> bool:
        """
        Checking the column for positive.
        :param column: a list with integers or floating number
        :return: bool: True - column not positive: False - column positive.
        """
        if len(column[column <= 0]):
            return True
        return False

    def _column_check(self,
                      column: np.array,
                      check_list: list,
                      title: str) -> bool:
        """
        Checking the fulfillment of criteria for a sequence of numbers.
        :param column: a list with integers or floating number
        :param check_list: list of criteria
        :param title: the title of the error message
        :return: bool: True - the criteria are not fulfilled; False - the criteria are fulfilled.
        """
        check_dict = {'positive': (self._column_positive, f"Отрицательные значения не допустимы."),
                      'increasing': (self._column_increasing, f"Задана не возрастающая последовательность.")}

        for check in check_list:
            if check_dict[check][0](column):
                QMessageBox.critical(self,
                                     title,
                                     check_dict[check][1])

                return True
        return False

    def checking_pre_calculate(self) -> bool:
        """
        Checking the requirements of regulatory documents
        :return: True - dont use automatic mode, False - use automatic mode
        """
        text = ""
        flag = False

        if self.Box_specimen_type.currentIndex() == 0:
            if self.specimen.b < self.specimen.w / 20 or self.specimen.b > self.specimen.w / 2:
                text += (f"Размеры образца противоречат треботванию п.4.3.2 ОСТ 1 92127-90 и"
                         f"требованию A 1.2.2.1 ASTM E647\n")
            if min(self.specimen.length_crack + self.specimen.a0) < self.specimen.w / 5:
                text += (f"Размеры образца и минимальная экспериментальная длина "
                         f"трещины противоречат треботванию п.4.5.3 ОСТ 1 92127-90 и"
                         f"требованиям A 1.2.1 и A 1.5.1 ASTM E647\n")
            if self.specimen.check_delta_length_ct():
                text += (f"Размеры образца и экспериментальные данные "
                         f"противоречат треботванию п.6.4.3 ОСТ 1 92127-90 и"
                         f"требованию A 1.4.1 ASTM E647\n")
        elif self.Box_specimen_type.currentIndex() == 1:
            if self.specimen.check_delta_length():
                text += (f"Размеры образца и экспериментальные данные "
                         f"противоречат треботванию п.6.4.4 ОСТ 1 92127-90\n")
        elif self.Box_specimen_type.currentIndex() == 2:
            pass

        if self.Box_load_type.currentIndex() == 0:
            if self.Edit_R_load.value() > 0.6:
                text += f"Величина коэффициента асимметрии противоречит требованию п.6.8 ОСТ 1 92127-90\n"

        if self.specimen.searchformalv23():
            if self.specimen.formal_23_specimen['numeric_point'] + 1 < MIN_POINT:
                text += (f"Автоматический режим расчета недоступен:\n"
                         f"экспериментальных данных со скоростью ниже формальной верхней границе\n"
                         f"меньше необходимого минимума для расчета\n"
                         f"(количество экспериментальных точек должно быть не менее {MIN_POINT})")
                flag = True

        else:
            text += (f"Автоматический режим расчета недоступен:\n"
                     f"cреди экспериментальных данных нет точек со скоростью ниже формальной верхней границе")
            flag = True

        if text:
            QMessageBox.warning(self,
                                "Предупреждение",
                                text)
        return flag

    def no_data(self) -> None:
        """
        A message about the absence of a data
        :return: None
        """
        QMessageBox.critical(self,
                             "Расчет не выполнен",
                             "Данные не загружены")

    def check_min_numeric_points(self) -> bool:
        """
        Checking for the required minimum number of points for calculation
        :return: bool True - correct, False - dont correct
        """
        if (self.Edit_num_point_end.value() - self.Edit_num_point_start.value() + 1 > MIN_POINT and
                self.Edit_num_point_end.value() <= self.specimen.num_point):
            return True

        QMessageBox.critical(self,
                             "Расчет не выполнен",
                             f"Границы для расчета должны содержать более {MIN_POINT} точек<br>"
                             f"и не превышать общее количество точек для образца: {self.specimen.num_point}")

        return False

    def check_range_numeric_points(self) -> bool:
        """
        Checking the existence of the calculation result
        :return: bool  True - correct, False - dont correct
        """
        start = self.Edit_num_point_start.value() - 1
        end = self.Edit_num_point_end.value() - 1

        if self.calculate_12:
            edge_12 = self.calculate_12.parameters12
            if end == edge_12[0]['point_numbers'][1] and edge_12[0]['point_numbers'][0] <= start <= \
                    edge_12[-1]['point_numbers'][0]:
                return True
        if self.calculate_23:
            edge_23 = self.calculate_23.parameters23

            if start == edge_23[0]['point_numbers'][0] and edge_23[0]['point_numbers'][1] <= end <= \
                    edge_23[-1]['point_numbers'][1]:
                return True

        QMessageBox.critical(self,
                             "Расчет не выполнен",
                             f"Для указанных границ расчет не проводился")

        return False

    def check_result_done(self,
                          flag: bool) -> None:
        """
        Launching a warning window
        :param flag: True - None, False - warning
        :return: None
        """
        if not flag:
            QMessageBox.warning(self,
                                "Предупреждение",
                                f"При поиске нижней границы устойчивого участка развития трещины не обнаружена "
                                f"экспериментальная точка, удовлетворяющая заданным критериям")
        else:
            QMessageBox.information(self,
                                    "Прогресс",
                                    f"Расчет завершен.")

    def checking_value(self) -> bool:
        """
        Checking for a range hit for a specimen
        :return: True - correct, False - not correct
        """
        text = ""
        if self.radioButton_length.isChecked():
            if (self.specimen.value(0) <= self.doubleSpinBox_number.value() <
                    self.specimen.value((self.specimen.w - self.specimen.a0) * MAX_SIF_RANGE_CALCULATED)):
                return True

            text += (f"Размах КИН должен быть "
                     f"в пределах [{self.specimen.value(0):.2f}, "
                     f"{self.specimen.value((self.specimen.w - self.specimen.a0) * MAX_SIF_RANGE_CALCULATED):.2f})")

        elif self.radioButton_SIF_range.isChecked():
            if self.doubleSpinBox_number.value() < self.specimen.w - self.specimen.a0:
                return True

            text += (f"Длина трещины должна быть не больше<br>"
                     f"W - a<sub>0</sub> = {self.specimen.w - self.specimen.a0:.2f}")

        QMessageBox.critical(self,
                             "Расчет не выполнен",
                             text)
        return False

    def window_error(self,
                     text: str) -> None:
        """
        An unknown error message
        :param text: error text
        :return: None
        """
        QMessageBox.critical(self,
                             "Неизвестная ошибка",
                             text)

    def window_warning(self,
                       title: str,
                       text: str) -> None:
        """
        Warning message
        :param title: warning title
        :param text: warning text
        :return: None
        """
        QMessageBox.warning(self,
                            title,
                            text)


if __name__ == "__main__":
    pass
