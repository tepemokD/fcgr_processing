from __future__ import annotations

from .listSIF import RangeSIF
from .rwfile import readtwoarray
from .crackgrowthrate import FCGR


class Specimen(RangeSIF, FCGR):
    def __init__(self,
                 type_sp: str = 'compact_tension',
                 type_load: str = 'cyclic_const_load_max',
                 temperature: str = '',
                 material: str = '',
                 number: str = '',
                 total: str = '',
                 **kwargs):

        assert type_sp in ('compact_tension',
                           'single_edge_notch_beam',
                           'other'), "The specimen type geometry is incorrect"
        self.type_sp = type_sp

        assert type_load in ('cyclic_const_load_max',
                             'user_load',
                             'user_SIF'), "The specimen type load is incorrect"
        self.type_load = type_load

        if self.type_load == 'user_SIF':
            self.type_sp = 'other'

        self.cycle_crack: list = None
        self.length_crack: list = None
        self.num_point: int = None
        self.w: float = None
        self.b: float = None
        self.a0: float = None
        self.temperature: str = temperature
        self.material: str = material
        self.number: str = number
        self.total: str = total

        super().__init__(**kwargs)

    def __repr__(self) -> str:
        text = f"The type of specimen: {self.type_sp}\n"
        if self.w:
            text += f"The dimensions of the specimen: W = {self.w}, B = {self.b}, a0 = {self.a0}\n"

        text += (f"Material: {self.material}\n"
                 f"Temperature: {self.temperature}\n"
                 f"Number specimen: {self.number}\n"
                 f"Total: {self.total}\n")

        text += f"\n"
        if self.type_load == 'cyclic_const_load_max':
            amplitude = self.load_max * (1 - self.asymmetry) / 2
            mean = self.load_max * (1 - self.asymmetry) / 2
            text += f"Cycling testing: force amplitude = {amplitude:.2f}, force mean = {mean:.2f}\n"

        text += f"\n"
        if any(self.cycle_crack):
            text += f"Experimental data:\n"
            text += f"Point\tLength\tCycle\tRange SIF\tFCGR\n"
            for index in range(self.num_point):
                text += (f"{index + 1}\t"
                         f"{self.length_crack[index]:.4f}\t"
                         f"{self.cycle_crack[index]:.0f}\t"
                         f"{self.value(self.length_crack[index]):.2f}\t")
                if self.fcgr_sample[index] > 0:
                    text += f"{self.fcgr_sample[index]:.4e}\n"
                else:
                    text += f"-\n"

        return text

    @classmethod
    def create_specimen_set_sif(cls,
                                file_experiment: str,
                                file_sif: str,
                                temperature_specimen: str,
                                material_specimen: str,
                                number_specimen: str,
                                total_specimen: str) -> Specimen:
        specimen = cls(type_load='user_SIF',
                       type_sp='other',
                       temperature=temperature_specimen,
                       material=material_specimen,
                       number=number_specimen,
                       total=total_specimen)
        specimen.setcrackgrowth(file_experiment)
        specimen.setsif(file_sif)
        specimen.createfcg()
        return specimen

    @classmethod
    def create_specimen_set_load(cls,
                                 file_experiment: str,
                                 type_specimen: str,
                                 file_load: str,
                                 w: float,
                                 b: float,
                                 a0: float,
                                 temperature_specimen: str,
                                 material_specimen: str,
                                 number_specimen: str,
                                 total_specimen: str,
                                 si: bool = False) -> Specimen:
        specimen = cls(type_sp=type_specimen,
                       type_load='user_load',
                       temperature=temperature_specimen,
                       material=material_specimen,
                       number=number_specimen,
                       total=total_specimen)
        specimen.setgeometry({'W': w,
                              'B': b,
                              'a0': a0})
        specimen.setcrackgrowth(file_experiment,
                                delta_length=a0)
        specimen.setloads(file_load)
        specimen.createfcg()

        if si:
            specimen.use_si()
        return specimen

    @classmethod
    def create_specimen(cls,
                        file_experiment: str,
                        type_specimen: str,
                        w: float,
                        b: float,
                        a0: float,
                        p_max: float,
                        r: float,
                        temperature_specimen: str,
                        material_specimen: str,
                        number_specimen: str,
                        total_specimen: str,
                        si: bool = False) -> Specimen:
        specimen = cls(type_sp=type_specimen,
                       temperature=temperature_specimen,
                       material=material_specimen,
                       number=number_specimen,
                       total=total_specimen)
        specimen.setgeometry({'W': w,
                              'B': b,
                              'a0': a0})
        specimen.setloads({'Pmax': p_max,
                           'R': r})
        specimen.setcrackgrowth(file_experiment,
                                delta_length=a0)
        specimen.createfcg()
        if si:
            specimen.use_si()
        return specimen

    @classmethod
    def create_simple_specimen(cls,
                               type_specimen: str,
                               w: float,
                               b: float,
                               a0: float,
                               p_max: float,
                               r: float,
                               si: bool = False) -> Specimen:
        specimen = cls(type_sp=type_specimen)
        specimen.setgeometry({'W': w,
                              'B': b,
                              'a0': a0})
        specimen.setloads({'Pmax': p_max,
                           'R': r})
        if si:
            specimen.use_si()
        return specimen

    def setgeometry(self,
                    geometry: dict) -> None:
        """
        Setting the standard geometric sizes of the specimen
        :param geometry: Dictionary with specimen sizes
        :return: None
        """
        assert self.type_sp != 'other' and self.type_load != 'user_SIF', \
            "Not use the module 'setgeometry' for the specimen type 'other' or for the load type 'user_SIF'"

        if self.type_sp in ('compact_tension', 'single_edge_notch_beam'):
            self.w = geometry['W']
            self.b = geometry['B']
            self.a0 = geometry['a0']

    def setcrackgrowth(self,
                       name_file: str,
                       delta_length: float = 0,
                       delta_cycle: float = 0) -> None:
        """
        Setting experimental data: crack length, number of loading cycles
        :param name_file: Name file with crack length and number of loading cycles
        :param delta_length: reducing the size of the crack length
        :param delta_cycle: reducing the size of the number of loading cycles
        :return: None
        """
        self.cycle_crack, self.length_crack = readtwoarray(name_file, delta_length, delta_cycle)
        self.num_point = len(self.cycle_crack)

    def setcrackgrowth_array(self,
                             cycle: list,
                             length: list) -> None:
        """
        Setting experimental data: crack length, number of loading cycles
        :param cycle: an array of cycle changes with crack growth
        :param length:an array of length changes with crack growth
        :return: None
        """
        self.cycle_crack, self.length_crack = cycle, length
        self.num_point = len(self.cycle_crack)

    def check_delta_length_ct(self) -> bool:
        """
        Verification of the requirement 6.4.3 OST 1 92127-90 for c(t) specimen
        :return: True - the requirement is not satisfied, False - the requirement is satisfied
        """
        assert self.type_sp == 'compact_tension', \
            "Use the module 'check_delta_length_ct' only for the specimen type 'compact_tension'"

        delta_length = []
        for index in range(1, self.num_point):
            delta_length.append(abs(self.length_crack[index] - self.length_crack[index - 1]))

        for index, delta in enumerate(delta_length):
            if ((0.25 <= (self.length_crack[index] + self.a0) / self.w < 0.4 and delta > self.w / 25) or
                    (0.4 <= (self.length_crack[index] + self.a0) / self.w <= 0.6 and delta > self.w / 50) or
                    ((self.length_crack[index] + self.a0) / self.w > 0.6 and delta > self.w / 100)):
                return True
        return False

    def check_delta_length(self) -> bool:
        """
        Verification of the requirement 6.4.4 OST 1 92127-90 for c(t) specimen
        :return: True - the requirement is not satisfied, False - the requirement is satisfied
        """
        assert self.type_sp == 'single_edge_notch_beam', \
            "Use the module 'check_delta_length' only for the specimen type 'single_edge_notch_beam'"

        delta_length = []
        for index in range(1, self.num_point):
            delta_length.append(abs(self.length_crack[index] - self.length_crack[index - 1]))

        for index, delta in enumerate(delta_length):
            if delta > self.w / 50:
                return True
        return False
