from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from decimal import Decimal

from .units_change import UnitsChange
from .setup_plot import FILE_WINDOW_UNITS_UI


class ConversionUnits(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi(FILE_WINDOW_UNITS_UI, self)

        self.unit = "Metric_to_SI"

        self.push_change_unit.clicked.connect(self.change_unit)
        self.push_sif.clicked.connect(self.change_sif)
        self.push_force.clicked.connect(self.change_force)
        self.push_coef.clicked.connect(self.change_coef)

    def change_unit(self) -> None:
        """
        Changing the measurement system
        :return: None
        """
        if self.unit == "Metric_to_SI":
            self.unit = "SI_to_Metric"
            self.push_change_unit.setText("<-")
            self.force_metric.clear()
            self.sif_metric.clear()
            self.coefficient_metric.clear()
            self.exp_coef_metric.clear()
            self.force_metric.setReadOnly(True)
            self.sif_metric.setReadOnly(True)
            self.coefficient_metric.setReadOnly(True)
            self.exp_coef_metric.setReadOnly(True)
            self.force_si.setReadOnly(False)
            self.sif_si.setReadOnly(False)
            self.coefficient_si.setReadOnly(False)
            self.exp_coef_si.setReadOnly(False)
        else:
            self.unit = "Metric_to_SI"
            self.push_change_unit.setText("->")
            self.force_si.clear()
            self.sif_si.clear()
            self.coefficient_si.clear()
            self.exp_coef_si.clear()
            self.force_si.setReadOnly(True)
            self.sif_si.setReadOnly(True)
            self.coefficient_si.setReadOnly(True)
            self.exp_coef_si.setReadOnly(True)
            self.force_metric.setReadOnly(False)
            self.sif_metric.setReadOnly(False)
            self.coefficient_metric.setReadOnly(False)
            self.exp_coef_metric.setReadOnly(False)

    def change_sif(self) -> None:
        """
        Conversion of the SIF value.
        :return: None
        """
        if self.unit == "Metric_to_SI":
            self._sif_metric_to_si()
        else:
            self._sif_si_to_metric()

    def change_force(self) -> None:
        """
        Conversion of the forse value.
        :return: None
        """
        if self.unit == "Metric_to_SI":
            self._force_metric_to_si()
        else:
            self._force_si_to_metric()

    def change_coef(self) -> None:
        """
        Conversion of the coefficient C value.
        :return: None
        """
        if self.unit == "Metric_to_SI":
            self._coef_metric_to_si()
        else:
            self._coef_si_to_metric()

    def _sif_metric_to_si(self) -> None:
        """
        Conversion of the SIF value from the metric system to the SI system.
        :return: None
        """
        self.sif_si.setValue(self.sif_metric.value() * UnitsChange.units_metric['coef_sif_metric_to_si'])

    def _sif_si_to_metric(self) -> None:
        """
        Conversion of the SIF value from the SI system to the metric system.
        :return: None
        """
        self.sif_metric.setValue(self.sif_si.value() * UnitsChange.units_si['coef_sif_si_to_metric'])

    def _force_metric_to_si(self) -> None:
        """
        Conversion of the force value from the metric system to the SI system.
        :return: None
        """
        self.force_si.setValue(self.force_metric.value() * UnitsChange.units_metric['coef_force_metric_to_si'])

    def _force_si_to_metric(self) -> None:
        """
        Conversion of the force value from the SI system to the metric system.
        :return: None
        """
        self.force_metric.setValue(self.force_si.value() * UnitsChange.units_si['coef_force_si_to_metric'])

    def _coef_metric_to_si(self) -> None:
        """
        Conversion of the coefficient C value from the metric system to the SI system.
        :return: None
        """
        coefficient_c_si = (self.coefficient_metric.value() * pow(10, -self.exp_coef_metric.value()) *
                            pow(UnitsChange.units_metric['coef_sif_metric_to_si'], -self.exponent.value()))

        _, digits, exponent = Decimal(coefficient_c_si).as_tuple()

        self.coefficient_si.setValue(Decimal(coefficient_c_si).scaleb(-len(digits) - exponent + 1).normalize())
        self.exp_coef_si.setValue(abs(int(len(digits) + exponent - 1)))

    def _coef_si_to_metric(self) -> None:
        """
        Conversion of the coefficient value from the SI system to the metric system.
        :return: None
        """
        coefficient_c_metric = (self.coefficient_si.value() * pow(10, -self.exp_coef_si.value()) *
                                pow(UnitsChange.units_si['coef_sif_si_to_metric'], -self.exponent.value()))

        _, digits, exponent = Decimal(coefficient_c_metric).as_tuple()

        self.coefficient_metric.setValue(Decimal(coefficient_c_metric).scaleb(-len(digits) - exponent + 1).normalize())
        self.exp_coef_metric.setValue(abs(int(len(digits) + exponent - 1)))
