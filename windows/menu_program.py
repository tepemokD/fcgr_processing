import os

from .setup_plot import TEXT_ABOUT
from .units_change import UnitsChange
from .conversion_units import ConversionUnits

from PyQt6.QtWidgets import QMessageBox


class MenuProgram:
    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)

    def _window_about(self) -> None:
        """
        Window about
        :return: None
        """
        QMessageBox.about(self,
                          "Сведения о программе",
                          TEXT_ABOUT)

    @staticmethod
    def _open_manual() -> None:
        """
        Opening the instruction file
        :return: None
        """
        try:
            os.startfile(r'instruction\User_manual.pdf')
        except FileNotFoundError:
            pass

    @staticmethod
    def _open_theory() -> None:
        """
        Opening the instruction file
        :return: None
        """
        try:
            os.startfile(r'instruction\Theory.pdf')
        except FileNotFoundError:
            pass

    @staticmethod
    def window_conversion_units() -> None:
        ConversionUnits().show()

    def window_units_show(self) -> None:
        QMessageBox.about(self,
                          "Сведения об единицах измерения",
                          f"<pre>СИ:<br>"
                          f'    Длина - {UnitsChange.units_si["length"]}<br>'
                          f"    КИН - {UnitsChange.units_si['sif']}<br>"
                          f"    Скорость роста трещины - {UnitsChange.units_si['cgr']}<br>"
                          f"    Коэффициент С - {UnitsChange.units_si['coef_c']}<br>"
                          f"Метрическая:<br>"
                          f"    Длина - {UnitsChange.units_metric['length']}<br>"
                          f"    КИН - {UnitsChange.units_metric['sif']}<br>"
                          f"    Скорость роста трещины - {UnitsChange.units_metric['cgr']}<br>"
                          f"    Коэффициент С - {UnitsChange.units_metric['coef_c']}</pre>")


if __name__ == "__main__":
    pass
