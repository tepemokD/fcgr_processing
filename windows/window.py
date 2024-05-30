import sys

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt6.QtCore import Qt

from iteramethod import Specimen, IterativeMethod

from .verificationmessages import Message
from .setup_plot import *
from .menu_program import MenuProgram
from .units_change import UnitsChange
from .window_sif_range import WindowSIFRange
from .window_paris_mean import WindowMeanParis

import pyqtgraph as pg
import numpy as np

pg.setConfigOptions(background='w',
                    foreground='k')


class WindowFcgr(QMainWindow,
                 Message,
                 MenuProgram):
    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)

        self.ui = uic.loadUi(FILE_WINDOW_UI, self)

        self.units_name: UnitsChange = UnitsChange("Metric")

        self.specimen: Specimen = None
        self.calculate: IterativeMethod = None

        self.calculate_12: IterativeMethod = None
        self.calculate_23: IterativeMethod = None

        self.Box_specimen_type.currentIndexChanged.connect(self.check_box_specimen_type)
        self.Box_load_type.currentIndexChanged.connect(self.check_box_load_type)

        self.Button_auto_type.toggled.connect(self.check_button_auto_type)
        self.Button_manual_type.toggled.connect(self.check_button_manual_type)
        self.Button_borders_type.toggled.connect(self.check_button_borders_type)

        self.Button_file_experiment.clicked.connect(self.open_file_experiment)
        self.Button_file_load.clicked.connect(self.open_file_load_or_sif)
        self.Button_create_specimen.clicked.connect(self.create_specimen)
        self.Button_calculate.clicked.connect(self.calculate_specimen)

        self.num_point.valueChanged.connect(self._info_num_point)

        self.about.triggered.connect(self._window_about)
        self.manual.triggered.connect(self._open_manual)
        self.theory.triggered.connect(self._open_theory)
        self.calculate_SIF_range.triggered.connect(self.window_program_sif_range)
        self.calculate_mean.triggered.connect(self.window_program_paris_mean)
        self.save_file.triggered.connect(self.save_result_to_file)

        self.units_metric.triggered.connect(self._change_unit_si)
        self.units_si.triggered.connect(self._change_unit_metric)
        self.units_show.triggered.connect(self.window_units_show)
        self.conversion_units.triggered.connect(self.window_conversion_units)

    def check_box_specimen_type(self) -> None:
        """
        Changes in the selection of the specimen type
        :return: None
        """
        if self.Box_specimen_type.currentIndex() == 2:
            self.Edit_w_specimen.clear()
            self.Edit_a0_specimen.clear()
            self.Edit_B_specimen.clear()
            self.Edit_Pmax_load.clear()
            self.Edit_R_load.clear()

            self.Edit_w_specimen.setEnabled(False)
            self.Edit_a0_specimen.setEnabled(False)
            self.Edit_B_specimen.setEnabled(False)
            self.Edit_Pmax_load.setEnabled(False)
            self.Edit_R_load.setEnabled(False)

            self.Box_load_type.setEnabled(False)

            self.Edit_file_load.setEnabled(True)
            self.Button_file_load.setEnabled(True)
        else:
            self.Edit_w_specimen.setEnabled(True)
            self.Edit_a0_specimen.setEnabled(True)
            self.Edit_B_specimen.setEnabled(True)
            self.Edit_Pmax_load.setEnabled(True)
            self.Edit_R_load.setEnabled(True)

            self.Box_load_type.setEnabled(True)
            self.check_box_load_type()

    def check_box_load_type(self) -> None:
        """
        Changes in the selection of the load type
        :return: None
        """
        if self.Box_load_type.currentIndex() == 1:
            self.Edit_Pmax_load.clear()
            self.Edit_R_load.clear()

            self.Edit_Pmax_load.setEnabled(False)
            self.Edit_R_load.setEnabled(False)

            self.Edit_file_load.setEnabled(True)
            self.Button_file_load.setEnabled(True)

        else:
            self.Edit_file_load.clear()

            self.Edit_Pmax_load.setEnabled(True)
            self.Edit_R_load.setEnabled(True)

            self.Edit_file_load.setEnabled(False)
            self.Button_file_load.setEnabled(False)

    def check_button_auto_type(self) -> None:
        """
        Changed in selection of the auto type
        :return: None
        """
        if self.Button_auto_type.isChecked():
            self.Box_R_square_criteria.setChecked(True)
            self.Box_cycle_end_criteria.setChecked(True)

            self.Button_search_n12.setChecked(0)
            self.Button_search_n23.setChecked(0)
            self.Button_plot.setChecked(0)
            self.Button_search_n12.setEnabled(False)
            self.Button_search_n23.setEnabled(False)
            self.Button_plot.setEnabled(False)

            self.Edit_num_point_start.clear()
            self.Edit_num_point_end.clear()
            self.Edit_num_point_start.setEnabled(False)
            self.Edit_num_point_end.setEnabled(False)

    def check_button_manual_type(self) -> None:
        """
        Changed in selection in the manual type
        :return: None
        """
        if self.Button_manual_type.isChecked():
            self.Button_search_n12.setEnabled(True)
            self.Button_search_n23.setEnabled(True)
            self.Button_plot.setEnabled(True)
            self.Button_search_n12.setChecked(1)
            self.Button_search_n23.setChecked(0)
            self.Button_plot.setChecked(0)

            self.Edit_num_point_start.clear()
            self.Edit_num_point_end.clear()
            self.Edit_num_point_start.setEnabled(True)
            self.Edit_num_point_end.setEnabled(True)

    def check_button_borders_type(self) -> None:
        """
        Changed in selection in the borders type
        :return: None
        """
        if self.Button_borders_type.isChecked():
            self.Box_R_square_criteria.setChecked(False)
            self.Box_comparison_criteria.setChecked(False)
            self.Box_cycle_all_criteria.setChecked(False)
            self.Box_cycle_end_criteria.setChecked(False)

            self.Box_R_square_criteria.setEnabled(False)
            self.Box_comparison_criteria.setEnabled(False)
            self.Box_cycle_all_criteria.setEnabled(False)
            self.Box_cycle_end_criteria.setEnabled(False)

            self.Edit_num_point_start.clear()
            self.Edit_num_point_end.clear()
            self.Edit_num_point_start.setEnabled(True)
            self.Edit_num_point_end.setEnabled(True)

            self.Button_search_n12.setEnabled(False)
            self.Button_search_n23.setEnabled(False)
            self.Button_plot.setEnabled(False)
        else:
            self.Box_R_square_criteria.setEnabled(True)
            self.Box_comparison_criteria.setEnabled(True)
            self.Box_cycle_all_criteria.setEnabled(True)
            self.Box_cycle_end_criteria.setEnabled(True)

    def _change_unit_si(self) -> None:
        """
        Changing the measurement system to metric
        :return: None
        """
        if self.units_metric.isChecked():
            self.units_si.toggle()
            self._change_label_unit("Metric")
        else:
            self.units_metric.setChecked(True)

    def _change_unit_metric(self) -> None:
        """
        Changing the measurement system to si
        :return: None
        """
        if self.units_si.isChecked():
            self.units_metric.toggle()
            self._change_label_unit("SI")

        else:
            self.units_si.setChecked(True)

    def _change_label_unit(self,
                           unit: str) -> None:
        """
        Changing the label text and clearing the sample and calculations
        :param unit: unit name
        :return: None
        """
        self.units_name.set_units(unit)
        # Text
        self.unit_p_max.setText(f"{self.units_name.force}")
        self.unit_w.setText(f"{self.units_name.length}")
        self.unit_b.setText(f"{self.units_name.length}")
        self.unit_a0.setText(f"{self.units_name.length}")
        self.length_np_unit.setText(f"{self.units_name.length}")
        self.sif_np_unit.setText(f"{self.units_name.sif}")

        if self.specimen:
            self.label_length_specimen.setText(f"от {min(self.specimen.length_crack):.4f} {self.units_name.length} "
                                               f"до {max(self.specimen.length_crack):.4f} {self.units_name.length}")
            self.label_SIF_specimen.setText(f"от {self.specimen.value(min(self.specimen.length_crack)):.2f} "
                                            f"{self.units_name.sif} "
                                            f"до {self.specimen.value(max(self.specimen.length_crack)):.2f} "
                                            f"{self.units_name.sif}")
            self.label_cgr_specimen.setText(f"от {self.specimen.fcgr_sample[0]:.4e} {self.units_name.cgr} "
                                            f"до {self.specimen.fcgr_sample[-1]:.4e} {self.units_name.cgr}")
        else:
            self.label_length_specimen.setText(f"от - {self.units_name.length} "
                                               f"до - {self.units_name.length}")
            self.label_SIF_specimen.setText(f"от - {self.units_name.sif} "
                                            f"до - {self.units_name.sif}")
            self.label_cgr_specimen.setText(f"от - {self.units_name.cgr} "
                                            f"до - {self.units_name.cgr}")
        self.label_length_calculate.setText(f"от - {self.units_name.length} "
                                            f"до - {self.units_name.length}")
        self.label_sif_calculate.setText(f"от - {self.units_name.sif} "
                                         f"до - {self.units_name.sif}")
        self.label_grc_calculate.setText(f"от - {self.units_name.cgr} "
                                         f"до - {self.units_name.cgr}")

        self._clear_calculate()
        self._clear_specimen()

    def plot_length_specimen(self) -> None:
        """
        Plotting scatter experiment data of a specimen
        :return: None
        """
        x_coord = self.specimen.cycle_crack
        y_coord = self.specimen.length_crack

        scatter = pg.ScatterPlotItem(size=SIZE_SCATTER_DATA,
                                     pen=EDGE_SCATTER_DATA,
                                     brush=BODY_SCATTER_DATA)
        scatter.addPoints(x_coord, y_coord)

        self.len_cycle.setTitle('Длина трещины от количества циклов')
        self.len_cycle.setLabel('left',
                                text='длина трещины',
                                units=self.units_name.length)
        self.len_cycle.setLabel('bottom',
                                text=f"{self.units_name.cycle}<br>")
        self.len_cycle.showGrid(x=True,
                                y=True)
        self.len_cycle.addItem(scatter)

    def plot_sif(self) -> None:
        """
        Plotting scatter SIF range of a specimen
        :return: None
        """
        x_coord = self.specimen.length_crack
        y_coord = self.specimen.array(x_coord)

        scatter = pg.ScatterPlotItem(size=SIZE_SCATTER_DATA,
                                     pen=EDGE_SCATTER_DATA,
                                     brush=BODY_SCATTER_DATA)
        scatter.addPoints(x_coord, y_coord)
        self.sif_specimen.setTitle('Размах КИН от длины трещины')
        self.sif_specimen.setLabel('left',
                                   text='размах КИН',
                                   units=self.units_name.sif)
        self.sif_specimen.setLabel('bottom',
                                   text=f"длина трещины ({self.units_name.length})<br>")
        self.sif_specimen.showGrid(x=True,
                                   y=True)
        self.sif_specimen.addItem(scatter)

    def plot_fcgr(self) -> None:
        """
        Plotting scatter fatigue crack growth rate of a specimen
        :return: None
        """
        x_coord = self.specimen.array(self.specimen.length_crack)
        y_coord = self.specimen.fcgr_sample

        y_coord, x_coord = tuple(zip(*[el for el in
                                       zip(y_coord, x_coord)
                                       if ((not np.isnan(el[0])) and el[0] > 0)]))
        x_coord = np.log10(x_coord)
        y_coord = np.log10(y_coord)

        scatter = pg.ScatterPlotItem(size=SIZE_SCATTER_DATA,
                                     pen=EDGE_SCATTER_DATA,
                                     brush=BODY_SCATTER_DATA)
        scatter.addPoints(x_coord, y_coord)
        self.fcgr_specimen.setTitle('СРТУ от размаха КИН')
        self.fcgr_specimen.setLabel('left',
                                    text='СРТУ',
                                    units=self.units_name.cgr)
        self.fcgr_specimen.setLabel('bottom',
                                    text=f"Размах КИН ({self.units_name.sif})<br>")
        self.fcgr_specimen.showGrid(x=True,
                                    y=True)
        self.fcgr_specimen.addItem(scatter)

    def open_file_experiment(self) -> None:
        """
        Selecting a file with experimental data
        :return: None
        """
        file_window = QFileDialog.getOpenFileName(self,
                                                  caption='Файл с экспериментальными данными',
                                                  filter="Text (*.txt);;Table (*.csv)")
        self.Edit_file_experiment.setText(file_window[0])

    def open_file_load_or_sif(self) -> None:
        """
        Selecting a file with load or SIF range
        :return: None
        """
        text_caption = 'Файл с изменением размаха нагрузки от количества циклов нагружения'
        if self.Box_specimen_type.currentIndex() == 2:
            text_caption = 'Файл с зависимостью размаха КИН от длины трещины'

        file_window = QFileDialog.getOpenFileName(self,
                                                  caption=text_caption,
                                                  filter="Text (*.txt);;Table (*.csv)")
        self.Edit_file_load.setText(file_window[0])

    def create_specimen(self) -> None:
        """
        Checking the input data for the correctness of the input and the requirements of regulatory documents.
        Creating an instance of the EE class
        :return: None
        """
        self._clear_specimen()

        if self.Box_specimen_type.currentIndex() == 2:  # Load file SIF range
            if (self.checking_file(self.Edit_file_experiment.text(),
                                   title="Ошибка в файле с экспериментальными данными",
                                   column1_check=('increasing',),
                                   column2_check=('positive',),
                                   min_point=True) and
                    self.checking_file(self.Edit_file_load.text(),
                                       title="Ошибка в файле с зависимостью размаха КИН от длины трещины",
                                       column2_check=('positive',)) and
                    self.checking_col(self.Edit_file_experiment.text(),
                                      self.Edit_file_load.text(),
                                      "Ошибка в файле с зависимостью размаха КИН от длины трещины")):
                self.specimen = Specimen.create_specimen_set_sif(self.Edit_file_experiment.text(),
                                                                 self.Edit_file_load.text(),
                                                                 self.lineEdit_temperature.text(),
                                                                 self.lineEdit_material.text(),
                                                                 self.lineEdit_number_sp.text(),
                                                                 self.textEdit_total_sp.toPlainText())

        elif self.Box_specimen_type.currentIndex() != 2 and self.Box_load_type.currentIndex() == 1:  # Load file dP(L)
            if (self.checking_file(self.Edit_file_experiment.text(),
                                   title="Ошибка в файле с экспериментальными данными",
                                   column1_check=('increasing',),
                                   column2_check=('positive',),
                                   min_point=True) and
                    self.checking_file(self.Edit_file_load.text(),
                                       title="Ошибка в файле с зависимостью размаха напряжений от длины трещины",
                                       column2_check=('positive',)) and
                    self.checking_col(self.Edit_file_experiment.text(),
                                      self.Edit_file_load.text(),
                                      "Ошибка в файле с зависимостью размаха напряжений от длины трещины") and
                    self.checking_numbers(self.Edit_file_experiment.text())):
                self.specimen = Specimen.create_specimen_set_load(self.Edit_file_experiment.text(),
                                                                  ['compact_tension',
                                                                   'single_edge_notch_beam'][
                                                                      self.Box_specimen_type.currentIndex()],
                                                                  self.Edit_file_load.text(),
                                                                  self.Edit_w_specimen.value(),
                                                                  self.Edit_B_specimen.value(),
                                                                  self.Edit_a0_specimen.value(),
                                                                  self.lineEdit_temperature.text(),
                                                                  self.lineEdit_material.text(),
                                                                  self.lineEdit_number_sp.text(),
                                                                  self.textEdit_total_sp.toPlainText(),
                                                                  si=True if self.units_name.unit == "SI" else False)

        elif self.Box_specimen_type.currentIndex() != 2 and self.Box_load_type.currentIndex() == 0:  # dP=const
            if (self.checking_file(self.Edit_file_experiment.text(),
                                   title="Ошибка в файле с экспериментальными данными",
                                   column1_check=('increasing',),
                                   column2_check=('positive',),
                                   min_point=True) and
                    self.checking_numbers(self.Edit_file_experiment.text())):
                self.specimen = Specimen.create_specimen(self.Edit_file_experiment.text(),
                                                         ['compact_tension',
                                                          'single_edge_notch_beam'][
                                                             self.Box_specimen_type.currentIndex()],
                                                         self.Edit_w_specimen.value(),
                                                         self.Edit_B_specimen.value(),
                                                         self.Edit_a0_specimen.value(),
                                                         self.Edit_Pmax_load.value(),
                                                         self.Edit_R_load.value(),
                                                         self.lineEdit_temperature.text(),
                                                         self.lineEdit_material.text(),
                                                         self.lineEdit_number_sp.text(),
                                                         self.textEdit_total_sp.toPlainText(),
                                                         si=True if self.units_name.unit == "SI" else False)

        elif self.Box_specimen_type.currentIndex() != 2 and self.Box_load_type.currentIndex() == 2:  # Load file L(N)
            if (self.checking_file(self.Edit_file_experiment.text(),
                                   title="Ошибка в файле с экспериментальными данными",
                                   column1_check=('increasing',),
                                   column2_check=('positive',),
                                   min_point=True,
                                   type_file='ciam') and
                    self.checking_numbers(self.Edit_file_experiment.text(),
                                          type_file='ciam')):
                self.specimen = Specimen.create_specimen(self.Edit_file_experiment.text(),
                                                         ['compact_tension',
                                                          'single_edge_notch_beam'][
                                                             self.Box_specimen_type.currentIndex()],
                                                         self.Edit_w_specimen.value(),
                                                         self.Edit_B_specimen.value(),
                                                         self.Edit_a0_specimen.value(),
                                                         self.Edit_Pmax_load.value(),
                                                         self.Edit_R_load.value(),
                                                         self.lineEdit_temperature.text(),
                                                         self.lineEdit_material.text(),
                                                         self.lineEdit_number_sp.text(),
                                                         self.textEdit_total_sp.toPlainText(),
                                                         si=True if self.units_name.unit == "SI" else False,
                                                         type_file='ciam')

        self.Button_auto_type.setEnabled(True)
        self.Button_auto_type.setChecked(True)

        if self.specimen:
            self.label_num_point_specimen.setText(f"{self.specimen.num_point}")
            self.label_length_specimen.setText(
                f"от {min(self.specimen.length_crack):.4f} {self.units_name.length} "
                f"до {max(self.specimen.length_crack):.4f} {self.units_name.length}")
            self.label_num_cycle_specimen.setText(
                f"от {self.specimen.cycle_crack[0]:.0f} "
                f"до {self.specimen.cycle_crack[-1]:.0f}")
            self.label_SIF_specimen.setText(
                f"от {self.specimen.value(min(self.specimen.length_crack)):.2f} {self.units_name.sif} "
                f"до {self.specimen.value(max(self.specimen.length_crack)):.2f} {self.units_name.sif}")
            self.label_cgr_specimen.setText(
                f"от {self.specimen.fcgr_sample[0]:.4e} {self.units_name.cgr} "
                f"до {self.specimen.fcgr_sample[-1]:.4e} {self.units_name.cgr}")
            self.num_point.setEnabled(True)
            # Обновление границ номеров точек
            self.num_point.setMaximum(self.specimen.num_point)

            self.plot_fcgr()
            self.plot_length_specimen()
            self.plot_sif()

            if self.checking_pre_calculate():
                self.Button_auto_type.setEnabled(False)
                self.Button_manual_type.setChecked(True)
            else:
                # Информаци о формальной верхней границе
                self.label_f23_info.setText(f"номер точки: {self.specimen.formal_23_specimen['numeric_point']:.0f},<br>"
                                            f"длина трещины: {self.specimen.formal_23_specimen['length']:.4f} "
                                            f"{self.units_name.length},<br>"
                                            f"количество циклов: {self.specimen.formal_23_specimen['cycle']:.0f},<br>"
                                            f"размах КИН: {self.specimen.formal_23_specimen['range_SIF']:.2f} "
                                            f"{self.units_name.sif},<br>"
                                            f"СРТУ: {self.specimen.formal_23_specimen['gr']:.4e} "
                                            f"{self.units_name.cgr}")

    def calculate_specimen(self) -> None:
        """
        Checking the existence of a sample
        :return: None
        """
        if self.specimen:
            self.calculate_specimen_go()
            self.save_file.setEnabled(True)

        else:
            self.no_data()

    def calculate_specimen_go(self) -> None:
        """
        Starting the calculation depending on the specified source data
        :return: None
        """
        dict_criteria = {'cycle_end': self.Box_cycle_end_criteria.checkState() == Qt.CheckState.Checked,
                         'R_square': self.Box_R_square_criteria.checkState() == Qt.CheckState.Checked,
                         'cycle_all': self.Box_cycle_all_criteria.checkState() == Qt.CheckState.Checked,
                         'comparison': self.Box_comparison_criteria.checkState() == Qt.CheckState.Checked}
        type_criteria = [key for key in dict_criteria if dict_criteria[key] == 1]

        if self.Button_auto_type.isChecked():
            self._clear_calculate()

            self.calculate = IterativeMethod(type_criteria=type_criteria,
                                             type_calculation='automatic')
            self.calculate.setspecimen(self.specimen)
            dict_result = self.calculate.auto()

            self._plot_result_12(result=self.calculate)
            self._plot_result_23(result=self.calculate)

            self._plot_result(coef_c=dict_result['coefficient_c'],
                              exp_n=dict_result['exponent_n'],
                              length_start=self.specimen.length_crack[dict_result['point_numbers'][0]],
                              length_end=self.specimen.length_crack[dict_result['point_numbers'][1]],
                              cycle_start=self.specimen.cycle_crack[dict_result['point_numbers'][0]],
                              cycle_end=self.specimen.cycle_crack[dict_result['point_numbers'][1]],
                              sif_start=self.specimen.value(
                                  self.specimen.length_crack[dict_result['point_numbers'][0]]),
                              sif_end=self.specimen.value(self.specimen.length_crack[dict_result['point_numbers'][1]]),
                              grc_start=self.specimen.fcgr_sample[dict_result['point_numbers'][0]],
                              grc_end=self.specimen.fcgr_sample[dict_result['point_numbers'][1]])

            self._plot_graph_result(dict_result)

            self.check_result_done(dict_result['criteria'])

        elif self.Button_manual_type.isChecked():

            if self.Button_search_n12.isChecked():
                self._clear_calculate_12()

                if self.check_min_numeric_points():
                    self.calculate_12 = IterativeMethod(type_criteria=type_criteria,
                                                        type_calculation='manual_search_low_border')
                    self.calculate_12.setspecimen(self.specimen)

                    self.calculate_12.fn12 = self.Edit_num_point_start.value() - 1
                    self.calculate_12.fn23 = self.Edit_num_point_end.value() - 1

                    self.calculate_12.search12()

                    self._plot_result_12(result=self.calculate_12)

                    self.check_result_done(True)

            elif self.Button_search_n23.isChecked():
                self._clear_calculate_23()

                if self.check_min_numeric_points():
                    self.calculate_23 = IterativeMethod(type_criteria=type_criteria,
                                                        type_calculation='manual_search_bottom_border')
                    self.calculate_23.setspecimen(self.specimen)

                    self.calculate_23.fn12 = self.Edit_num_point_start.value() - 1
                    self.calculate_23.fn23 = self.Edit_num_point_end.value() - 1

                    self.calculate_23.search23()

                    self._plot_result_23(result=self.calculate_23)

                    self.check_result_done(True)

            elif self.Button_plot.isChecked():
                self._clear_calculate_result()

                if self.check_min_numeric_points() and self.check_range_numeric_points():

                    if self.calculate_12 and self.Edit_num_point_end.value() - 1 == \
                            self.calculate_12.parameters12[0]['point_numbers'][1]:

                        for index in range(len(self.calculate_12.parameters12)):
                            if self.Edit_num_point_start.value() - 1 == \
                                    self.calculate_12.parameters12[index]['point_numbers'][0]:
                                break

                        dict_result = {'point_numbers': self.calculate_12.parameters12[index]['point_numbers'],
                                       'coefficient_c': self.calculate_12.parameters12[index]['coefficient_c'],
                                       'exponent_n': self.calculate_12.parameters12[index]['exponent_n']}
                    else:

                        for index in range(len(self.calculate_23.parameters23)):
                            if self.Edit_num_point_end.value() - 1 == \
                                    self.calculate_23.parameters23[index]['point_numbers'][1]:
                                break

                        dict_result = {'point_numbers': self.calculate_23.parameters23[index]['point_numbers'],
                                       'coefficient_c': self.calculate_23.parameters23[index]['coefficient_c'],
                                       'exponent_n': self.calculate_23.parameters23[index]['exponent_n']}

                    self._plot_result(coef_c=dict_result['coefficient_c'],
                                      exp_n=dict_result['exponent_n'],
                                      length_start=self.specimen.length_crack[dict_result['point_numbers'][0]],
                                      length_end=self.specimen.length_crack[dict_result['point_numbers'][1]],
                                      cycle_start=self.specimen.cycle_crack[dict_result['point_numbers'][0]],
                                      cycle_end=self.specimen.cycle_crack[dict_result['point_numbers'][1]],
                                      sif_start=self.specimen.value(
                                          self.specimen.length_crack[dict_result['point_numbers'][0]]),
                                      sif_end=self.specimen.value(
                                          self.specimen.length_crack[dict_result['point_numbers'][1]]),
                                      grc_start=self.specimen.fcgr_sample[dict_result['point_numbers'][0]],
                                      grc_end=self.specimen.fcgr_sample[dict_result['point_numbers'][1]])
                    self._plot_graph_result(dict_result)

                    self.check_result_done(True)

        elif self.Button_borders_type.isChecked():
            self._clear_calculate()

            if self.check_min_numeric_points():
                self.calculate = IterativeMethod(type_criteria=type_criteria,
                                                 type_calculation='border')
                self.calculate.setspecimen(self.specimen)

                dict_result = self.calculate.edge(start=self.Edit_num_point_start.value() - 1,
                                                  end=self.Edit_num_point_end.value() - 1)

                self._plot_result(coef_c=dict_result['coefficient_c'],
                                  exp_n=dict_result['exponent_n'],
                                  length_start=self.specimen.length_crack[dict_result['point_numbers'][0]],
                                  length_end=self.specimen.length_crack[dict_result['point_numbers'][1]],
                                  cycle_start=self.specimen.cycle_crack[dict_result['point_numbers'][0]],
                                  cycle_end=self.specimen.cycle_crack[dict_result['point_numbers'][1]],
                                  sif_start=self.specimen.value(
                                      self.specimen.length_crack[dict_result['point_numbers'][0]]),
                                  sif_end=self.specimen.value(
                                      self.specimen.length_crack[dict_result['point_numbers'][1]]),
                                  grc_start=self.specimen.fcgr_sample[dict_result['point_numbers'][0]],
                                  grc_end=self.specimen.fcgr_sample[dict_result['point_numbers'][1]])
                self._plot_graph_result(dict_result)

                self.check_result_done(True)

    def _plot_result_12(self,
                        result: IterativeMethod) -> None:
        """
        Plotting for the bottom edge
        :param result - result data
        :return: None
        """
        x_coord = []
        coef_c = []
        exp_n = []
        len(result.type_criteria)
        criteria_12 = {'R_square': [],
                       'cycle_end': [],
                       'comparison': [],
                       'cycle_all': []}

        for element in result.parameters12:
            x_coord.append(element['point_numbers'][0])
            coef_c.append(np.log10(element['coefficient_c']))
            exp_n.append(element['exponent_n'])
            for key in element['criteria'].keys():
                criteria_12[key].append(element['criteria'][key])

        self.plot_criteria_12.addLegend(offset=POSITION_LEGEND_MAIN,
                                        horSpacing=HORIZONTAL_SPACING_LEGEND,
                                        verSpacing=VERTICAL_SPACING_LEGEND,
                                        brush=COLOR_LEGEND)

        scatter_coef_12 = pg.ScatterPlotItem(size=SIZE_SCATTER_RESULT,
                                             pen=EDGE_SCATTER_RESULT,
                                             brush=BODY_SCATTER_RESULT)
        scatter_exp_12 = pg.ScatterPlotItem(size=SIZE_SCATTER_RESULT,
                                            pen=EDGE_SCATTER_RESULT,
                                            brush=BODY_SCATTER_RESULT)
        scatter_criteria_12 = dict()
        for key in criteria_12.keys():
            scatter_criteria_12[key] = pg.PlotCurveItem()

        scatter_coef_12.addPoints(x_coord, coef_c)
        scatter_exp_12.addPoints(x_coord, exp_n)
        for key in scatter_criteria_12.keys():
            scatter_criteria_12[key].setData(x=x_coord,
                                             y=criteria_12[key],
                                             name=LEGEND_CRITERIA[key][0],
                                             pen=LEGEND_CRITERIA[key][1])

        self.plot_coef_c_12.setTitle(f'Коэффициент C от<br>количества отброшенных точек')
        self.plot_coef_c_12.setLabel('left',
                                     text='коэффициент С')
        self.plot_coef_c_12.setLabel('bottom',
                                     text='количество отброшенных точек<br>')
        self.plot_coef_c_12.showGrid(x=True,
                                     y=True)
        self.plot_coef_c_12.addItem(scatter_coef_12)

        self.plot_exp_n_12.setTitle(f'Показатель степени n от<br>количества отброшенных точек')
        self.plot_exp_n_12.setLabel('left',
                                    text='показатель степени n')
        self.plot_exp_n_12.setLabel('bottom',
                                    text='количество отброшенных точек<br>')
        self.plot_exp_n_12.showGrid(x=True,
                                    y=True)
        self.plot_exp_n_12.addItem(scatter_exp_12)

        self.plot_criteria_12.setTitle(f'Критерии от<br>количества отброшенных точек')
        self.plot_criteria_12.setLabel('left',
                                       text='критерии')
        self.plot_criteria_12.setLabel('bottom',
                                       text='количество отброшенных точек<br>')
        self.plot_criteria_12.showGrid(x=True,
                                       y=True)
        self.plot_criteria_12.setYRange(min=0.99,
                                        max=1)
        for key in scatter_criteria_12.keys():
            self.plot_criteria_12.addItem(scatter_criteria_12[key])

    def _plot_result_23(self,
                        result: IterativeMethod) -> None:
        """
        Plotting for the low edge
        :param result calculate data
        :return: None
        """
        x_coord = []
        coef_c = []
        exp_n = []
        len(result.type_criteria)
        criteria_23 = {'R_square': [],
                       'cycle_end': [],
                       'comparison': [],
                       'cycle_all': []
                       }

        for element in result.parameters23:
            x_coord.append(element['point_numbers'][1])
            coef_c.append(np.log10(element['coefficient_c']))
            exp_n.append(element['exponent_n'])
            for key in element['criteria'].keys():
                criteria_23[key].append(element['criteria'][key])

        x_coord = [x - x_coord[0] for x in x_coord]
        self.plot_criteria_23.addLegend(offset=POSITION_LEGEND_MAIN,
                                        horSpacing=HORIZONTAL_SPACING_LEGEND,
                                        verSpacing=VERTICAL_SPACING_LEGEND,
                                        brush=COLOR_LEGEND)

        scatter_coef_23 = pg.ScatterPlotItem(size=SIZE_SCATTER_RESULT,
                                             pen=EDGE_SCATTER_RESULT,
                                             brush=BODY_SCATTER_RESULT)
        scatter_exp_23 = pg.ScatterPlotItem(size=SIZE_SCATTER_RESULT,
                                            pen=EDGE_SCATTER_RESULT,
                                            brush=BODY_SCATTER_RESULT)
        scatter_criteria_23 = dict()
        for key in criteria_23.keys():
            scatter_criteria_23[key] = pg.PlotCurveItem()

        scatter_coef_23.addPoints(x_coord, coef_c)
        scatter_exp_23.addPoints(x_coord, exp_n)
        for key in scatter_criteria_23.keys():
            scatter_criteria_23[key].setData(x=x_coord,
                                             y=criteria_23[key],
                                             name=LEGEND_CRITERIA[key][0],
                                             pen=LEGEND_CRITERIA[key][1])

        self.plot_coef_c_23.setTitle(f'Коэффициент C от<br>количества добавленных точек')
        self.plot_coef_c_23.setLabel('left',
                                     text='коэффициент С')
        self.plot_coef_c_23.setLabel('bottom',
                                     text='количество добавленных точек<br>')
        self.plot_coef_c_23.showGrid(x=True,
                                     y=True)
        self.plot_coef_c_23.addItem(scatter_coef_23)

        self.plot_exp_n_23.setTitle(f'Показатель степени n от<br>количества добавленных точек')
        self.plot_exp_n_23.setLabel('left',
                                    text='показатель степени n')
        self.plot_exp_n_23.setLabel('bottom',
                                    text='количество добавленных точек<br>')
        self.plot_exp_n_23.showGrid(x=True,
                                    y=True)
        self.plot_exp_n_23.addItem(scatter_exp_23)

        self.plot_criteria_23.setTitle(f'Критерии от<br>количества добавленных точек')
        self.plot_criteria_23.setLabel('left',
                                       text='критерии')
        self.plot_criteria_23.setLabel('bottom',
                                       text='количество добавленных точек<br>')
        self.plot_criteria_23.showGrid(x=True,
                                       y=True)
        self.plot_criteria_23.setYRange(min=0.99,
                                        max=1)
        for key in scatter_criteria_23.keys():
            self.plot_criteria_23.addItem(scatter_criteria_23[key])

    def _plot_graph_result(self,
                           dict_result: dict) -> None:
        """
        Plotting graph result: L(N), FCGR(SIF range)
        :return: None
        """
        self.len_cycle.clear()
        self.fcgr_specimen.clear()

        self.plot_length_specimen()
        self.plot_fcgr()

        line_length_result = pg.PlotCurveItem()
        line_fcgr_result = pg.PlotCurveItem()

        if self.calculate:
            model = self.calculate
        elif self.calculate_12:
            model = self.calculate_12
        else:
            model = self.calculate_23

        length_result, cycle_result = model.cgua.crackgrowtharray(
            properties={'coefficient_c': dict_result['coefficient_c'], 'exponent_n': dict_result['exponent_n']},
            interval=np.linspace(start=self.specimen.length_crack[dict_result['point_numbers'][0]],
                                 stop=self.specimen.length_crack[dict_result['point_numbers'][1]],
                                 num=NUMERIC_SCATTER),
            cycle_start=self.specimen.cycle_crack[dict_result['point_numbers'][0]])

        x_fcgr = [self.specimen.value(self.specimen.length_crack[dict_result['point_numbers'][0]]),
                  self.specimen.value(self.specimen.length_crack[dict_result['point_numbers'][1]])]
        y_fcgr = [dict_result['coefficient_c'] * x ** dict_result['exponent_n'] for x in x_fcgr]
        x_fcgr = np.log10(x_fcgr)
        y_fcgr = np.log10(y_fcgr)

        line_length_result.setData(x=cycle_result,
                                   y=length_result,
                                   pen=RESULT_LINE)
        line_fcgr_result.setData(x=x_fcgr,
                                 y=y_fcgr,
                                 pen=RESULT_LINE)

        self.len_cycle.addItem(line_length_result)
        self.fcgr_specimen.addItem(line_fcgr_result)

    def _plot_result(self,
                     coef_c: float,
                     exp_n: float,
                     length_start: float,
                     length_end: float,
                     cycle_start: float,
                     cycle_end: float,
                     sif_start: float,
                     sif_end: float,
                     grc_start: float,
                     grc_end: float) -> None:
        """
        Displaying calculation results
        :param coef_c: coefficient C Paris equation
        :param exp_n: exponent n Paris equation
        :param length_start: the value of the length of the lower edge
        :param length_end: the value of the length of the upper edge
        :param cycle_start: the numeric of the cycle of the lower edge
        :param cycle_end: the numeric of the cycle of the upper edge
        :param sif_start: the value of the SIF range of the lower edge
        :param sif_end: the value of the SIF range of the upper edge
        :param grc_start: the value of the crack growth rate of the lower edge
        :param grc_end: the vakue of the crack growth rate of the upper edge
        :return: None
        """
        self.label_coefficient_c.setText(f"{coef_c:.4e}")
        self.label_exponent_n.setText(f"{exp_n:.4f}")
        self.label_length_calculate.setText(f"от {length_start:.4f} {self.units_name.length} "
                                            f"до {length_end:.4f} {self.units_name.length}")
        self.label_num_cycle_calculate.setText(f"от {cycle_start:.0f} до {cycle_end:.0f}")
        self.label_sif_calculate.setText(
            f"от {sif_start:.2f} {self.units_name.sif} "
            f"до {sif_end:.2f} {self.units_name.sif}")
        self.label_grc_calculate.setText(f"от {grc_start:.4e} {self.units_name.cgr}"
                                         f" до {grc_end:.4e} {self.units_name.cgr}")

    def _clear_specimen(self) -> None:
        """
        Clearing specimen data.
        :return: None
        """
        self.specimen = None

        self.save_file.setEnabled(False)

        self.label_num_point_specimen.setText(f"-")
        self.label_length_specimen.setText(f"от - {self.units_name.length} "
                                           f"до - {self.units_name.length}")
        self.label_num_cycle_specimen.setText(f"от - "
                                              f"до -")
        self.label_SIF_specimen.setText(f"от - {self.units_name.sif} "
                                        f"до - {self.units_name.sif}")
        self.label_cgr_specimen.setText(f"от - {self.units_name.cgr} "
                                        f"до - {self.units_name.cgr}")
        self.length_np.setText(f"-")
        self.cycle_np.setText(f"-")
        self.sif_np.setText(f"-")
        self.fcgr_np.setText(f"-")
        self.label_f23_info.setText(f"-")

        self.len_cycle.clear()
        self.sif_specimen.clear()
        self.fcgr_specimen.clear()
        self.num_point.clear()

        self._clear_calculate()

    def _clear_calculate(self) -> None:
        """
        Clearing calculate data.
        :return: None
        """
        self.calculate = None
        self.calculate_12 = None
        self.calculate_23 = None

        self._clear_calculate_12()
        self._clear_calculate_23()

        self._clear_calculate_result()

    def _clear_calculate_12(self) -> None:
        """
        Clearing calculate data bottom edge.
        :return: None
        """
        self.plot_coef_c_12.clear()
        self.plot_exp_n_12.clear()
        self.plot_criteria_12.clear()

    def _clear_calculate_23(self) -> None:
        """
        Clearing calculate data low edge.
        :return: None
        """
        self.plot_coef_c_23.clear()
        self.plot_exp_n_23.clear()
        self.plot_criteria_23.clear()

    def _clear_calculate_result(self) -> None:
        """
        Clearing calculate data result.
        :return: None
        """
        self.Edit_num_point_start.clear()
        self.Edit_num_point_end.clear()

        self.label_coefficient_c.setText(f"-")
        self.label_exponent_n.setText(f"-")
        self.label_length_calculate.setText(f"от - {self.units_name.length} "
                                            f"до - {self.units_name.length}")
        self.label_num_cycle_calculate.setText(f"от - "
                                               f"до -")
        self.label_sif_calculate.setText(f"от - {self.units_name.sif} "
                                         f"до - {self.units_name.sif}")
        self.label_grc_calculate.setText(f"от - {self.units_name.cgr} "
                                         f"до - {self.units_name.cgr}")

    def _info_num_point(self) -> None:
        """
        Information about the point by number.
        :return: None
        """
        num_point = self.num_point.value() - 1
        self.length_np.setText(f"{self.specimen.length_crack[num_point]:.4f}")
        self.cycle_np.setText(f"{self.specimen.cycle_crack[num_point]:.0f}")
        self.sif_np.setText(f"{self.specimen.value(self.specimen.length_crack[num_point]):.2f}")
        self.fcgr_np.setText(f"{self.specimen.fcgr_sample[num_point]:.4e}")

    def save_result_to_file(self) -> None:
        """
        Saving the results to a file
        :return: None
        """
        if self.calculate or self.calculate_12 or self.calculate_23:
            file_name, _ = QFileDialog.getSaveFileName(self,
                                                       caption="Сохранение свойств трещиностойкости",
                                                       filter="Text (*.txt)",
                                                       )
            with open(file_name, 'w') as file:
                result = f"{self.units_name}\n"
                result += "\n" + "-" * 70 + "\n"
                if self.calculate:
                    result += f"{self.calculate}"
                if self.calculate_12:
                    result += f"{self.calculate_12}"
                if self.calculate_23:
                    result += f"{self.calculate_23}"
                file.write(result)

    def window_program_sif_range(self) -> None:
        """
        Opening a window with SIF range calculation
        :return: None
        """
        WindowSIFRange(self.units_name).show()

    def window_program_paris_mean(self) -> None:
        """
        Opening a window with mean properties (Paris) calculation
        :return: None
        """
        WindowMeanParis(self.units_name).show()


def windows_program():
    app = QApplication(sys.argv)
    program = WindowFcgr()
    program.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    pass
