from iteramethod import Specimen

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap

from .verificationmessages import Message
from .units_change import UnitsChange

from .setup_plot import *


class WindowSIFRange(QWidget,
                     Message):
    def __init__(self,
                 unit: UnitsChange):
        super().__init__()

        self.unit = unit

        self.ui = uic.loadUi(FILE_WINDOW_SIF_UI, self)

        self.unit_w.setText(f"{self.unit.length}")
        self.unit_b.setText(f"{self.unit.length}")
        self.unit_a0.setText(f"{self.unit.length}")
        self.label_force.setText(f"{self.unit.force}")
        self.label_length.setText(f"{self.unit.length}")
        self.unit_sif.setText(f"{self.unit.sif}")

        self.specimen: Specimen = None

        self.specimen_list = {TYPE_SPECIMEN_NAME_PROGRAM[0]: IMAGE_CT_SPECIMEN,
                              TYPE_SPECIMEN_NAME_PROGRAM[1]: IMAGE_SENB_SPECIMEN}

        specimen_image = QPixmap(self.specimen_list[TYPE_SPECIMEN_NAME_PROGRAM[0]])

        self.specimen_image.setPixmap(specimen_image)

        self.Box_specimen_type_SIF.currentIndexChanged.connect(self.check_box_specimen_type_sif)
        self.Button_calculated_sif_range.clicked.connect(self.calculated)

        self.radioButton_length.toggled.connect(self.changing_label)

    def changing_label(self) -> None:
        """
        Changing label value, calculated and dimension
        :return: None
        """
        lab_val = self.label_value.text()
        lab_calc = self.label_calcuclated.text()
        self.label_value.setText(lab_calc)
        self.label_calcuclated.setText(lab_val)

        dim_val = self.label_length.text()
        dim_calc = self.unit_sif.text()
        self.label_length.setText(dim_calc)
        self.unit_sif.setText(dim_val)

        self._clear_numeric()

    def check_box_specimen_type_sif(self) -> None:
        """
        Changing the specimen image
        :return: None
        """
        specimen_image = QPixmap(self.specimen_list[self.Box_specimen_type_SIF.currentText()])
        self.specimen_image.setPixmap(specimen_image)

    def calculated(self) -> None:
        """
        Calculated result
        :return: None
        """
        self.specimen = Specimen.create_simple_specimen(
            type_specimen=TYPE_SPECIMEN_NAME[self.Box_specimen_type_SIF.currentText()],
            w=self.Edit_w_specimen.value(),
            b=self.Edit_B_specimen.value(),
            a0=self.Edit_a0_specimen.value(),
            p_max=self.Edit_Pmax_load.value(),
            r=self.Edit_R_load.value(),
            si=True if self.unit.unit == "SI" else False)

        if self.checking_numbers() and self.checking_value():
            func = self.specimen.value
            if self.radioButton_length.isChecked():
                func = self.specimen.calc_length

            result = func(self.doubleSpinBox_number.value())
            self.label_result.setText(f"{result:.2f}")
        else:
            self._clear_numeric()

    def _clear_numeric(self) -> None:
        self.doubleSpinBox_number.setValue(0.0)
        self.label_result.setText(f"-")


if __name__ == "__main__":
    pass
