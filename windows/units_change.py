class UnitsChange:
    units_si = {"length": "мм",
                "sif": f"МПа&sdot;м<sup>1/2</sup>",
                "force": f"кН",
                "cgr": f"мм/цикл",
                "coef_c": f"мм&sdot;(МПа&sdot;м<sup>1/2</sup>)<sup>-n</sup>",
                "coef_sif_si_to_metric": pow(10, 3 / 2) / 9.80665,
                "coef_force_si_to_metric": 1000 / 9.80665}
    units_metric = {"length": "мм",
                    "sif": f"кгс/мм<sup>3/2</sup>",
                    "force": f"кгс",
                    "cgr": f"мм/цикл",
                    "coef_c": f"мм&sdot;(кгс/мм<sup>3/2</sup>)<sup>-n</sup>",
                    "coef_sif_metric_to_si": 9.80665 / pow(10, 3 / 2),
                    "coef_force_metric_to_si": 9.80665 / 1000}
    units = {"SI": units_si,
             "Metric": units_metric}

    def __init__(self,
                 unit: str) -> None:
        self.unit: str = unit
        self.sif: str = None
        self.force: str = None
        self.length: str = None
        self.cgr: str = None
        self.coef_sif: int = None

        self.set_units(self.unit)

    def set_units(self,
                  unit: str) -> None:
        self.unit = unit
        self.sif = self.units[self.unit]["sif"]
        self.force = self.units[self.unit]["force"]
        self.length = self.units[self.unit]["length"]
        self.cgr = self.units[self.unit]["cgr"]


if __name__ == "__main__":
    pass
