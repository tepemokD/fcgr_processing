from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFileDialog

from iteramethod import MeanProperties

from .setup_plot import *
from .verificationmessages import Message

import pyqtgraph as pg
import numpy as np
from .units_change import UnitsChange


class WindowMeanParis(QWidget,
                      Message):
    def __init__(self,
                 unit: UnitsChange):
        super().__init__()

        self.unit = unit

        self.ui = uic.loadUi(FILE_WINDOW_MEAN_UI, self)

        self.focal_sif.setText(f"размах КИН - {self.unit.sif}")
        self.focal_fcgr.setText(f"СРТУ - {self.unit.cgr}")
        self.border_sif.setText(f"Размах КИН от - {self.unit.sif} до - {self.unit.sif}")

        self.mean_properties: MeanProperties = None

        self.load_file.clicked.connect(self.open_file_properties_specimen)
        self.Button_calculate.clicked.connect(self.calculate)
        self.save_result.clicked.connect(self.save_file_result)

        self.ploting.currentIndexChanged.connect(self._plot_graph)
        self.get_temperature.currentIndexChanged.connect(self._write)

    def open_file_properties_specimen(self) -> None:
        """
        Checking and opening a file
        :return: None
        """
        file_window = QFileDialog.getOpenFileName(self,
                                                  caption="Файл со свойствами СРТУ образцов",
                                                  filter="Text (*.txt);;Table (*.csv)")

        if file_window[0] and self.checking_file_mean(file_window[0]):
            self.lineEdit_load_file.setText(file_window[0])
            self._clear_window()

    def calculate(self) -> None:
        """
        Clicking on the calculation start button
        :return: None
        """
        if self.lineEdit_load_file.text():
            self.calculate_go()
        else:
            self.no_data()

    def calculate_go(self) -> None:
        """
        Calculation of average properties
        :return: None
        """
        self._clear_window()

        if self.method_focal_point.isChecked():
            method = 'focal_point'
        else:  # self.method_mean.isChecked()
            method = 'mean_curve'

        if self.border_min.isChecked():
            mode_border = 'minimum'
        elif self.border_mean.isChecked():
            mode_border = 'mean'
        else:  # self.border_max.isChecked()
            mode_border = 'maximum'

        self.mean_properties = MeanProperties(mode=method,
                                              border_sif=mode_border,
                                              si=True if self.unit.unit == "SI" else False
                                              )
        self.mean_properties.set_file(self.lineEdit_load_file.text())

        try:
            self.mean_properties.calculate()
        except Exception as error:
            self.window_error(f'<span style="color:red;">{str(error)}</span>')

        if self.mean_properties.text_error:
            self.window_warning(title="Предупреждение о результатах расчета",
                                text=self.mean_properties.text_error)

        self._plot_result()

    def save_file_result(self) -> None:
        if self.mean_properties:
            file_name, _ = QFileDialog.getSaveFileName(self,
                                                       caption="Сохранение средних свойств трещиностойкости",
                                                       filter="Text (*.txt)",
                                                       )
            with open(file_name, 'w') as file:
                file.write(f'{self.mean_properties}')

    def _clear_window(self) -> None:
        """
        Deleting calculation results
        :return: None
        """
        self.mean_properties = None

        self.plot_scatter_curve.clear()

        self.ploting.clear()
        self.get_temperature.clear()

        self.coefficient_c.setText(f"Коэффициент С: -")
        self.exponent_n.setText(f"Показатель степени n: -")
        self.border_sif.setText(f"Размах КИН от - {self.unit.sif} до - {self.unit.sif}")
        self.focal_sif.setText(f"размах КИН - {self.unit.sif}<br>")
        self.focal_fcgr.setText(f"СРТУ - {self.unit.length}")

    def _plot_result(self) -> None:
        """
        Drawing the results
        :return: None
        """
        if self.mean_properties.mode == 'focal_point':
            self.focal_sif.setText(f"размах КИН {self.mean_properties.fp_sif_range:.2f} {self.unit.sif}<br>")
            self.focal_fcgr.setText(f"СРТУ {self.mean_properties.fp_fcgr:.4e} {self.unit.cgr}")

        self.ploting.addItem(f"lg(C) vs n")
        self.ploting.addItem(f"n vs T")
        self.ploting.addItem(f"delta K_min vs T")
        self.ploting.addItem(f"delta K_max vs T")

        self.get_temperature.addItems(map(str, self.mean_properties.num_temperature.keys()))

    def _plot_graph(self) -> None:
        """
        Drawing the results on graphs
        :return: None
        """
        if self.ploting.currentText():
            self.plot_scatter_curve.clear()
            self._axis(self.ploting.currentText())

    def _axis(self,
              axis: str) -> None:
        """
        Plotting the results
        :param axis: name plot
        :return: None
        """
        if axis == "lg(C) vs n":
            self.plot_scatter_curve.addLegend(offset=POSITION_LEGEND_MEIN,
                                              horSpacing=HORIZONTAL_SPACING_LEGEND,
                                              verSpacing=VERTICAL_SPACING_LEGEND,
                                              brush=COLOR_LEGEND)

            x_coord = [self.mean_properties.num_properties[key][0] for key in
                       self.mean_properties.num_properties.keys()]
            y_coord = np.log10([self.mean_properties.num_properties[key][1] for key in
                                self.mean_properties.num_properties.keys()])
            label_x = f"Показатель степени n<br>"
            label_y = f"Коэффициент lg(C)"
            title_text = f"Зависимость коэффициента lg(C)<br>от показателя степени n"
            self._plot_axis(x_coord,
                            y_coord,
                            type_draw='result',
                            name_scatter=f"Расчет")

            index = 0
            for temperature in self.mean_properties.num_temperature.keys():
                x_one_temp = self.mean_properties.exponent_n_array[
                    np.where(self.mean_properties.temperature_array == temperature)]
                y_one_temp = np.log10(self.mean_properties.coefficient_c_array[
                                          np.where(self.mean_properties.temperature_array == temperature)])
                self._plot_axis(x_one_temp,
                                y_one_temp,
                                type_draw='experimental_grad',
                                index_color=index,
                                name_scatter=f"{temperature}")
                index += 1

        elif axis == "n vs T":
            x_coord = list(self.mean_properties.num_properties.keys())
            y_coord = [self.mean_properties.num_properties[key][0] for key in
                       self.mean_properties.num_properties.keys()]
            label_x = f"Температура<br>"
            label_y = f"Показатель степени n"
            title_text = f"Зависимость показателя степени n от температуры"
            self._plot_axis(x_coord,
                            y_coord,
                            type_draw='result',
                            name_scatter=f"Расчет")

            x_coord_exp = self.mean_properties.temperature_array
            y_coord_exp = self.mean_properties.exponent_n_array
            self._plot_axis(x_coord_exp,
                            y_coord_exp,
                            type_draw='experiment',
                            name_scatter=f"Эксперимент")

        elif axis == "delta K_min vs T":
            x_coord = list(self.mean_properties.num_sif12.keys())
            y_coord = [self.mean_properties.num_sif12[key] for key in self.mean_properties.num_sif12.keys()]
            label_x = f"Температура<br>"
            label_y = f"Размах КИН &Delta;K<sub>мин</sub> ({self.unit.sif})"
            title_text = f"Зависимость размаха КИН<sub>мин</sub> от температуры"
            self._plot_axis(x_coord,
                            y_coord,
                            type_draw='result',
                            name_scatter=f"Расчет")

            x_coord_exp = self.mean_properties.temperature_array
            y_coord_exp = self.mean_properties.sif12_range_array
            self._plot_axis(x_coord_exp,
                            y_coord_exp,
                            type_draw='experiment',
                            name_scatter=f"Эксперимент")

        elif axis == "delta K_max vs T":
            x_coord = list(self.mean_properties.num_sif23.keys())
            y_coord = [self.mean_properties.num_sif23[key] for key in self.mean_properties.num_sif23.keys()]
            label_x = f"Температура<br>"
            label_y = f"Размах КИН &Delta;K<sub>макс</sub> ({self.unit.sif})"
            title_text = f"Зависимость размаха КИН<sub>макс</sub> от температуры"
            self._plot_axis(x_coord,
                            y_coord,
                            type_draw='result',
                            name_scatter=f"Расчет")

            x_coord_exp = self.mean_properties.temperature_array
            y_coord_exp = self.mean_properties.sif23_range_array
            self._plot_axis(x_coord_exp,
                            y_coord_exp,
                            type_draw='experiment',
                            name_scatter=f"Эксперимент")

        self.plot_scatter_curve.setTitle(title_text)
        self.plot_scatter_curve.setLabel('left',
                                         text=label_y)
        self.plot_scatter_curve.setLabel('bottom',
                                         text=label_x)
        self.plot_scatter_curve.showGrid(x=True,
                                         y=True)

    def _plot_axis(self,
                   x: list,
                   y: list,
                   type_draw: str,
                   index_color: int = None,
                   name_scatter: str = "") -> None:
        """
        Drawing points
        :param x: the x coordinate
        :param y: the y coordinate
        :param type_draw: scatter type
        :param index_color: scatter color
        :param name_scatter: legend name
        :return:
        """
        if type_draw == 'result':
            draw = (SIZE_SCATTER_RESULT, EDGE_SCATTER_RESULT, BODY_SCATTER_RESULT)
        elif type_draw == 'experiment':
            draw = (SIZE_SCATTER_EXPERIMENT, EDGE_SCATTER_EXPERIMENT, BODY_SCATTER_EXPERIMENT)
        elif type_draw == 'experimental_grad':
            draw = (SIZE_SCATTER_EXPERIMENT, EDGE_SCATTER_EXPERIMENT,
                    pg.intColor(index_color,
                                hues=len(self.mean_properties.num_temperature)))

        scatter = pg.ScatterPlotItem(size=draw[0],
                                     pen=draw[1],
                                     brush=draw[2])
        scatter.addPoints(x, y,
                          name=name_scatter)
        self.plot_scatter_curve.addItem(scatter)

    def _write(self) -> None:
        """
        Drawing the results in the text
        :return: None
        """
        if self.get_temperature.currentText():
            temperature = float(self.get_temperature.currentText())
            self.coefficient_c.setText(f"Коэффициент С: {self.mean_properties.num_properties[temperature][1]:.4e}")
            self.exponent_n.setText(f"Показатель степени n: {self.mean_properties.num_properties[temperature][0]}")
            self.border_sif.setText(
                f"Размах КИН от {self.mean_properties.num_sif12[temperature]:.2f} {self.unit.sif} "
                f"до {self.mean_properties.num_sif23[temperature]:.2f} {self.unit.sif}")
