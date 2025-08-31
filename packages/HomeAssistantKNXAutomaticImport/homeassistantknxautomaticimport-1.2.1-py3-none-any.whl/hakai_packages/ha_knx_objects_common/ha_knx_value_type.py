from ruamel.yaml import YAML

from hakai_packages.knx_project_objects import KNXDPTType
from hakai_packages.knx_utils import Serializable, serializable_to_yaml

# pylint: disable=R0801

yaml = YAML()

class HAKNXValueType(Serializable):

    _value_types: dict[str, KNXDPTType] = {
        'binary':           KNXDPTType.constructor_from_ints(1, None),
        'switch':           KNXDPTType.constructor_from_ints(1, 1),
        'bool':             KNXDPTType.constructor_from_ints(1, 2),
        'enable':           KNXDPTType.constructor_from_ints(1, 3),
        'ramp':             KNXDPTType.constructor_from_ints(1, 4),
        'alarm':            KNXDPTType.constructor_from_ints(1, 5),
        'binary value':     KNXDPTType.constructor_from_ints(1, 6),
        'step':             KNXDPTType.constructor_from_ints(1, 7),
        'up down':          KNXDPTType.constructor_from_ints(1, 8),
        'open close':       KNXDPTType.constructor_from_ints(1, 9),
        'start':            KNXDPTType.constructor_from_ints(1, 10),
        'state':            KNXDPTType.constructor_from_ints(1, 11),
        'invert':           KNXDPTType.constructor_from_ints(1, 12),
        'dim send style':   KNXDPTType.constructor_from_ints(1, 13),
        'input source':     KNXDPTType.constructor_from_ints(1, 14),
        'reset':            KNXDPTType.constructor_from_ints(1, 15),
        'ack':              KNXDPTType.constructor_from_ints(1, 16),
        'trigger':          KNXDPTType.constructor_from_ints(1, 17),
        'occupancy':        KNXDPTType.constructor_from_ints(1, 18),
        'window door':      KNXDPTType.constructor_from_ints(1, 19),
        'logical function': KNXDPTType.constructor_from_ints(1, 21),
        'scene ab':         KNXDPTType.constructor_from_ints(1, 22),
        'shutter blinds mode':  KNXDPTType.constructor_from_ints(1, 23),
        'day night':        KNXDPTType.constructor_from_ints(1, 24),
        'heat cool':        KNXDPTType.constructor_from_ints(1, 100),
        'consumer producer':KNXDPTType.constructor_from_ints(1, 1200),
        'energy direction': KNXDPTType.constructor_from_ints(1, 1201),
        '1byte_unsigned':   KNXDPTType.constructor_from_ints(5, None),
        'percent':          KNXDPTType.constructor_from_ints(5, 1),
        'angle':            KNXDPTType.constructor_from_ints(5, 3),
        'percentU8':        KNXDPTType.constructor_from_ints(5, 4),
        'decimal_factor':   KNXDPTType.constructor_from_ints(5, 5),
        'tariff':           KNXDPTType.constructor_from_ints(5, 6),
        'pulse':            KNXDPTType.constructor_from_ints(5, 10),
        '1byte_signed':     KNXDPTType.constructor_from_ints(6, None),
        'percentV8':        KNXDPTType.constructor_from_ints(6, 1),
        'counter_pulses':   KNXDPTType.constructor_from_ints(6, 10),
        '2byte_unsigned':   KNXDPTType.constructor_from_ints(7, None),
        'pulse_2byte':      KNXDPTType.constructor_from_ints(7, 1),
        'time_period_msec': KNXDPTType.constructor_from_ints(7, 2),
        'time_period_10msec': KNXDPTType.constructor_from_ints(7, 3),
        'time_period_100msec': KNXDPTType.constructor_from_ints(7, 4),
        'time_period_sec':  KNXDPTType.constructor_from_ints(7, 5),
        'time_period_min':  KNXDPTType.constructor_from_ints(7, 6),
        'time_period_hrs':  KNXDPTType.constructor_from_ints(7, 7),
        'length_mm':        KNXDPTType.constructor_from_ints(7, 11),
        'current':          KNXDPTType.constructor_from_ints(7, 12),
        'brightness':       KNXDPTType.constructor_from_ints(7, 13),
        'color_temperature': KNXDPTType.constructor_from_ints(7, 600),
        '2byte_signed':     KNXDPTType.constructor_from_ints(8, None),
        'pulse_2byte_signed': KNXDPTType.constructor_from_ints(8, 1),
        'delta_time_ms':    KNXDPTType.constructor_from_ints(8, 2),
        'delta_time_10ms':  KNXDPTType.constructor_from_ints(8, 3),
        'delta_time_100ms': KNXDPTType.constructor_from_ints(8, 4),
        'delta_time_sec':   KNXDPTType.constructor_from_ints(8, 5),
        'delta_time_min':   KNXDPTType.constructor_from_ints(8, 6),
        'delta_time_hrs':   KNXDPTType.constructor_from_ints(8, 7),
        'percentV16':       KNXDPTType.constructor_from_ints(8, 10),
        'rotation_angle':   KNXDPTType.constructor_from_ints(8, 11),
        'length_m':         KNXDPTType.constructor_from_ints(8, 12),
        '2byte_float':      KNXDPTType.constructor_from_ints(9, None),
        'temperature':      KNXDPTType.constructor_from_ints(9, 1),
        'temperature_difference_2byte': KNXDPTType.constructor_from_ints(9, 2),
        'temperature_a':    KNXDPTType.constructor_from_ints(9, 3),
        'illuminance':      KNXDPTType.constructor_from_ints(9, 4),
        'wind_speed_ms':    KNXDPTType.constructor_from_ints(9, 5),
        'pressure_2byte':   KNXDPTType.constructor_from_ints(9, 6),
        'humidity':         KNXDPTType.constructor_from_ints(9, 7),
        'ppm':              KNXDPTType.constructor_from_ints(9, 8),
        'air_flow':         KNXDPTType.constructor_from_ints(9, 9),
        'time_1':           KNXDPTType.constructor_from_ints(9, 10),
        'time_2':           KNXDPTType.constructor_from_ints(9, 11),
        'voltage':          KNXDPTType.constructor_from_ints(9, 20),
        'curr':             KNXDPTType.constructor_from_ints(9, 21),
        'power_density':    KNXDPTType.constructor_from_ints(9, 22),
        'kelvin_per_percent': KNXDPTType.constructor_from_ints(9, 23),
        'power_2byte':      KNXDPTType.constructor_from_ints(9, 24),
        'volume_flow':      KNXDPTType.constructor_from_ints(9, 25),
        'rain_amount':      KNXDPTType.constructor_from_ints(9, 26),
        'temperature_f':    KNXDPTType.constructor_from_ints(9, 27),
        'wind_speed_kmh':   KNXDPTType.constructor_from_ints(9, 28),
        'absolute_humidity': KNXDPTType.constructor_from_ints(9, 29),
        'concentration_ugm3': KNXDPTType.constructor_from_ints(9, 30),
        'time':             KNXDPTType.constructor_from_ints(10, 1),
        'date':             KNXDPTType.constructor_from_ints(11, 1),
        '4byte_unsigned':   KNXDPTType.constructor_from_ints(12, None),
        'pulse_4_ucount':   KNXDPTType.constructor_from_ints(12, 1),
        'long_time_period_sec': KNXDPTType.constructor_from_ints(12, 100),
        'long_time_period_min': KNXDPTType.constructor_from_ints(12, 101),
        'long_time_period_hrs': KNXDPTType.constructor_from_ints(12, 102),
        'volume_liquid_litre': KNXDPTType.constructor_from_ints(12, 1200),
        'volume_m3':        KNXDPTType.constructor_from_ints(12, 1201),
        '4byte_signed':     KNXDPTType.constructor_from_ints(13, None),
        'pulse_4byte':      KNXDPTType.constructor_from_ints(13, 1),
        'flow_rate_m3h':    KNXDPTType.constructor_from_ints(13, 2),
        'active_energy':    KNXDPTType.constructor_from_ints(13, 10),
        'apparant_energy':  KNXDPTType.constructor_from_ints(13, 11),
        'reactive_energy':  KNXDPTType.constructor_from_ints(13, 12),
        'active_energy_kwh': KNXDPTType.constructor_from_ints(13, 13),
        'apparant_energy_kvah': KNXDPTType.constructor_from_ints(13, 14),
        'reactive_energy_kvarh': KNXDPTType.constructor_from_ints(13, 15),
        'active_energy_mwh': KNXDPTType.constructor_from_ints(13, 16),
        'long_delta_timesec': KNXDPTType.constructor_from_ints(13, 100),
        '4byte_float':      KNXDPTType.constructor_from_ints(14, None),
        'acceleration':     KNXDPTType.constructor_from_ints(14, 0),
        'acceleration_angular': KNXDPTType.constructor_from_ints(14, 1),
        'activation_energy': KNXDPTType.constructor_from_ints(14, 2),
        'activity':         KNXDPTType.constructor_from_ints(14, 3),
        'mol':              KNXDPTType.constructor_from_ints(14, 4),
        'amplitude':        KNXDPTType.constructor_from_ints(14, 5),
        'angle_rad':        KNXDPTType.constructor_from_ints(14, 6),
        'angle_deg':        KNXDPTType.constructor_from_ints(14, 7),
        'angular_momentum': KNXDPTType.constructor_from_ints(14, 8),
        'angular_velocity': KNXDPTType.constructor_from_ints(14, 9),
        'area':             KNXDPTType.constructor_from_ints(14, 10),
        'capacitance':      KNXDPTType.constructor_from_ints(14, 11),
        'charge_density_surface': KNXDPTType.constructor_from_ints(14, 12),
        'charge_density_volume': KNXDPTType.constructor_from_ints(14, 13),
        'compressibility':  KNXDPTType.constructor_from_ints(14, 14),
        'conductance':      KNXDPTType.constructor_from_ints(14, 15),
        'electrical_conductivity': KNXDPTType.constructor_from_ints(14, 16),
        'density':          KNXDPTType.constructor_from_ints(14, 17),
        'electric_charge':  KNXDPTType.constructor_from_ints(14, 18),
        'electric_current': KNXDPTType.constructor_from_ints(14, 19),
        'electric_current_density': KNXDPTType.constructor_from_ints(14, 20),
        'electric_dipole_moment': KNXDPTType.constructor_from_ints(14, 21),
        'electric_displacement': KNXDPTType.constructor_from_ints(14, 22),
        'electric_field_strength': KNXDPTType.constructor_from_ints(14, 23),
        'electric_flux':    KNXDPTType.constructor_from_ints(14, 24),
        'electric_flux_density': KNXDPTType.constructor_from_ints(14, 25),
        'electric_polarization': KNXDPTType.constructor_from_ints(14, 26),
        'electric_potential': KNXDPTType.constructor_from_ints(14, 27),
        'electric_potential_difference': KNXDPTType.constructor_from_ints(14, 28),
        'electromagnetic_moment': KNXDPTType.constructor_from_ints(14, 29),
        'electromotive_force': KNXDPTType.constructor_from_ints(14, 30),
        'energy':           KNXDPTType.constructor_from_ints(14, 31),
        'force':            KNXDPTType.constructor_from_ints(14, 32),
        'frequency':        KNXDPTType.constructor_from_ints(14, 33),
        'angular_frequency': KNXDPTType.constructor_from_ints(14, 34),
        'heatcapacity':     KNXDPTType.constructor_from_ints(14, 35),
        'heatflowrate':     KNXDPTType.constructor_from_ints(14, 36),
        'heat_quantity':    KNXDPTType.constructor_from_ints(14, 37),
        'impedance':        KNXDPTType.constructor_from_ints(14, 38),
        'length':           KNXDPTType.constructor_from_ints(14, 39),
        'light_quantity':   KNXDPTType.constructor_from_ints(14, 40),
        'luminance':        KNXDPTType.constructor_from_ints(14, 41),
        'luminous_flux':    KNXDPTType.constructor_from_ints(14, 42),
        'luminous_intensity': KNXDPTType.constructor_from_ints(14, 43),
        'magnetic_field_strength': KNXDPTType.constructor_from_ints(14, 44),
        'magnetic_flux':    KNXDPTType.constructor_from_ints(14, 45),
        'magnetic_flux_density': KNXDPTType.constructor_from_ints(14, 46),
        'magnetic_moment':  KNXDPTType.constructor_from_ints(14, 47),
        'magnetic_polarization': KNXDPTType.constructor_from_ints(14, 48),
        'magnetization':    KNXDPTType.constructor_from_ints(14, 49),
        'magnetomotive_force': KNXDPTType.constructor_from_ints(14, 50),
        'mass':             KNXDPTType.constructor_from_ints(14, 51),
        'mass_flux':        KNXDPTType.constructor_from_ints(14, 52),
        'momentum':         KNXDPTType.constructor_from_ints(14, 53),
        'phaseanglerad':    KNXDPTType.constructor_from_ints(14, 54),
        'phaseangledeg':    KNXDPTType.constructor_from_ints(14, 55),
        'power':            KNXDPTType.constructor_from_ints(14, 56),
        'powerfactor':      KNXDPTType.constructor_from_ints(14, 57),
        'pressure':         KNXDPTType.constructor_from_ints(14, 58),
        'reactance':        KNXDPTType.constructor_from_ints(14, 59),
        'resistance':       KNXDPTType.constructor_from_ints(14, 60),
        'resistivity':      KNXDPTType.constructor_from_ints(14, 61),
        'self_inductance':  KNXDPTType.constructor_from_ints(14, 62),
        'solid_angle':      KNXDPTType.constructor_from_ints(14, 63),
        'sound_intensity':  KNXDPTType.constructor_from_ints(14, 64),
        'speed':            KNXDPTType.constructor_from_ints(14, 65),
        'stress':           KNXDPTType.constructor_from_ints(14, 66),
        'surface_tension':  KNXDPTType.constructor_from_ints(14, 67),
        'common_temperature': KNXDPTType.constructor_from_ints(14, 68),
        'absolute_temperature': KNXDPTType.constructor_from_ints(14, 69),
        'temperature_difference': KNXDPTType.constructor_from_ints(14, 70),
        'thermal_capacity': KNXDPTType.constructor_from_ints(14, 71),
        'thermal_conductivity': KNXDPTType.constructor_from_ints(14, 72),
        'thermoelectric_power': KNXDPTType.constructor_from_ints(14, 73),
        'time_seconds':     KNXDPTType.constructor_from_ints(14, 74),
        'torque':           KNXDPTType.constructor_from_ints(14, 75),
        'volume':           KNXDPTType.constructor_from_ints(14, 76),
        'volume_flux':      KNXDPTType.constructor_from_ints(14, 77),
        'weight':           KNXDPTType.constructor_from_ints(14, 78),
        'work':             KNXDPTType.constructor_from_ints(14, 79),
        'apparent_power':   KNXDPTType.constructor_from_ints(14, 80),
        'string':           KNXDPTType.constructor_from_ints(16, 0),
        'latin_1':          KNXDPTType.constructor_from_ints(16, 1),
        'scene_number':     KNXDPTType.constructor_from_ints(17, 1),
        'datetime':         KNXDPTType.constructor_from_ints(19, 1),
        '8byte_signed':     KNXDPTType.constructor_from_ints(29, None),
        'active_energy_8byte': KNXDPTType.constructor_from_ints(29, 10),
        'apparant_energy_8byte': KNXDPTType.constructor_from_ints(29, 11),
        'reactive_energy_8byte': KNXDPTType.constructor_from_ints(29, 12),
    }

    def __init__(self):
        super().__init__()
        self._type = None

    @property
    def dpt(self) -> KNXDPTType | None:
        if self._type is None:
            return None
        return self._value_types[self._type]

    @dpt.setter
    def dpt(self, dpt: KNXDPTType | None):
        if dpt is None:
            self._type = None
            return
        dpt_found = False
        for key, value in self._value_types.items():
            if (value.main == dpt.main) and (value.sub == dpt.sub):
                self._type = key
                dpt_found = True
        if not dpt_found:
            for key, value in self._value_types.items():
                if (value.main == dpt.main) and (value.sub is None):
                    self._type = key
                    dpt_found = True
        if not dpt_found:
            self._type = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value_type: str | None):
        if value_type is None:
            self._type = None
            return
        if value_type in self._value_types:
            self._type = value_type
        else:
            self._type = None

    def __str__(self):
        return self._type

    def __repr__(self):
        return self._type

    def __eq__(self, other):
        if not isinstance(other, HAKNXValueType):
            return False
        return self.type == other.type

    def to_dict(self):
        return self._type

    def from_dict(self, dict_obj: dict):
        if isinstance(dict_obj, str):
            raise ValueError(f"Unexpected type '{type(dict_obj)}', expecting a string")
        self.type = dict_obj

    def to_yaml(self, representer):
        output_node = representer.represent_str(self._type)
        return output_node

yaml.register_class(HAKNXValueType)
yaml.representer.add_representer(HAKNXValueType, serializable_to_yaml)
