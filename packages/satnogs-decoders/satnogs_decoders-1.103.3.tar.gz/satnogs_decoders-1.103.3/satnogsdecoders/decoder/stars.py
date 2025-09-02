# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Stars(KaitaiStruct):
    """:field rm: rm
    :field beacon_no: beacon_no
    :field satellite_time: satellite_time
    :field condition: condition
    :field rssi: rssi
    :field temperature_1: temperature_1
    :field temperature_2: temperature_2
    :field temperature_3: temperature_3
    :field mode: mode
    :field reset_times_of_com_system: reset_times_of_com_system
    :field receive_times_of_cdh: receive_times_of_cdh
    :field solarcell_current: solarcell_current
    :field solarcell_voltage: solarcell_voltage
    :field total_system_current: total_system_current
    :field total_voltage: total_voltage
    :field solarcell_voltage_cdh: solarcell_voltage_cdh
    :field total_voltage_cdh: total_voltage_cdh
    :field necessary_for_lengthcheck: necessary_for_lengthcheck
    :field beacon: beacon
    
    .. seealso::
       Source - http://stars.eng.shizuoka.ac.jp/english/CW_Telemetry_format.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.rm = (self._io.read_bytes(1)).decode(u"ASCII")
        if not  ((self.rm == u"r") or (self.rm == u"m")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.rm, self._io, u"/seq/0")
        self.beacon_no = (self._io.read_bytes(1)).decode(u"ASCII")
        if not  ((self.beacon_no == u"2") or (self.beacon_no == u"3") or (self.beacon_no == u"4") or (self.beacon_no == u"5") or (self.beacon_no == u"6")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.beacon_no, self._io, u"/seq/1")
        self.value1 = self._io.read_u1()
        self.value2 = self._io.read_u1()
        self.value3 = self._io.read_u1()
        self.value4 = self._io.read_u1()
        self.lengthcheck = (self._io.read_bytes_full()).decode(u"utf-8")

    @property
    def temperature_3(self):
        if hasattr(self, '_m_temperature_3'):
            return self._m_temperature_3

        if self.beacon_no == u"3":
            self._m_temperature_3 = self.value4

        return getattr(self, '_m_temperature_3', None)

    @property
    def total_voltage(self):
        if hasattr(self, '_m_total_voltage'):
            return self._m_total_voltage

        if self.beacon_no == u"5":
            self._m_total_voltage = (self.value4 * 0.05888)

        return getattr(self, '_m_total_voltage', None)

    @property
    def total_voltage_cdh(self):
        if hasattr(self, '_m_total_voltage_cdh'):
            return self._m_total_voltage_cdh

        if self.beacon_no == u"6":
            self._m_total_voltage_cdh = (((self.value3 << 8) | self.value4) * 0.05888)

        return getattr(self, '_m_total_voltage_cdh', None)

    @property
    def reset_times_of_com_system(self):
        if hasattr(self, '_m_reset_times_of_com_system'):
            return self._m_reset_times_of_com_system

        if self.beacon_no == u"4":
            self._m_reset_times_of_com_system = self.value2

        return getattr(self, '_m_reset_times_of_com_system', None)

    @property
    def value3_hex_right_digit(self):
        if hasattr(self, '_m_value3_hex_right_digit'):
            return self._m_value3_hex_right_digit

        self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
        return getattr(self, '_m_value3_hex_right_digit', None)

    @property
    def necessary_for_lengthcheck(self):
        if hasattr(self, '_m_necessary_for_lengthcheck'):
            return self._m_necessary_for_lengthcheck

        if len(self.lengthcheck) != 0:
            self._m_necessary_for_lengthcheck = int(self.lengthcheck) // 0

        return getattr(self, '_m_necessary_for_lengthcheck', None)

    @property
    def value1_hex_left(self):
        if hasattr(self, '_m_value1_hex_left'):
            return self._m_value1_hex_left

        self._m_value1_hex_left = self.value1 // 16
        return getattr(self, '_m_value1_hex_left', None)

    @property
    def satellite_time(self):
        if hasattr(self, '_m_satellite_time'):
            return self._m_satellite_time

        if self.beacon_no == u"2":
            self._m_satellite_time = (((self.value1 << 16) | (self.value2 << 8)) | self.value3)

        return getattr(self, '_m_satellite_time', None)

    @property
    def condition(self):
        if hasattr(self, '_m_condition'):
            return self._m_condition

        if self.beacon_no == u"2":
            self._m_condition = self.value4

        return getattr(self, '_m_condition', None)

    @property
    def value2_hex_right(self):
        if hasattr(self, '_m_value2_hex_right'):
            return self._m_value2_hex_right

        self._m_value2_hex_right = (self.value2 % 16)
        return getattr(self, '_m_value2_hex_right', None)

    @property
    def value3_hex(self):
        if hasattr(self, '_m_value3_hex'):
            return self._m_value3_hex

        self._m_value3_hex = self.value3_hex_left_digit + self.value3_hex_right_digit
        return getattr(self, '_m_value3_hex', None)

    @property
    def total_system_current(self):
        if hasattr(self, '_m_total_system_current'):
            return self._m_total_system_current

        if self.beacon_no == u"5":
            self._m_total_system_current = (self.value3 * 0.025138)

        return getattr(self, '_m_total_system_current', None)

    @property
    def rssi(self):
        if hasattr(self, '_m_rssi'):
            return self._m_rssi

        if self.beacon_no == u"3":
            self._m_rssi = self.value1 // 2

        return getattr(self, '_m_rssi', None)

    @property
    def value3_hex_right(self):
        if hasattr(self, '_m_value3_hex_right'):
            return self._m_value3_hex_right

        self._m_value3_hex_right = (self.value3 % 16)
        return getattr(self, '_m_value3_hex_right', None)

    @property
    def temperature_2(self):
        if hasattr(self, '_m_temperature_2'):
            return self._m_temperature_2

        if self.beacon_no == u"3":
            self._m_temperature_2 = self.value3

        return getattr(self, '_m_temperature_2', None)

    @property
    def value1_hex_right_digit(self):
        if hasattr(self, '_m_value1_hex_right_digit'):
            return self._m_value1_hex_right_digit

        self._m_value1_hex_right_digit = (u"a" if str(self.value1_hex_right) == u"10" else (u"b" if str(self.value1_hex_right) == u"11" else (u"c" if str(self.value1_hex_right) == u"12" else (u"d" if str(self.value1_hex_right) == u"13" else (u"e" if str(self.value1_hex_right) == u"14" else (u"f" if str(self.value1_hex_right) == u"15" else str(self.value1_hex_right)))))))
        return getattr(self, '_m_value1_hex_right_digit', None)

    @property
    def beacon(self):
        if hasattr(self, '_m_beacon'):
            return self._m_beacon

        self._m_beacon = self.rm + self.beacon_no + u" " + self.value1_hex + u" " + self.value2_hex + u" " + self.value3_hex + u" " + self.value4_hex
        return getattr(self, '_m_beacon', None)

    @property
    def solarcell_voltage_cdh(self):
        if hasattr(self, '_m_solarcell_voltage_cdh'):
            return self._m_solarcell_voltage_cdh

        if self.beacon_no == u"6":
            self._m_solarcell_voltage_cdh = (((self.value1 << 8) | self.value2) * 0.05888)

        return getattr(self, '_m_solarcell_voltage_cdh', None)

    @property
    def value3_hex_left(self):
        if hasattr(self, '_m_value3_hex_left'):
            return self._m_value3_hex_left

        self._m_value3_hex_left = self.value3 // 16
        return getattr(self, '_m_value3_hex_left', None)

    @property
    def receive_times_of_cdh(self):
        if hasattr(self, '_m_receive_times_of_cdh'):
            return self._m_receive_times_of_cdh

        if self.beacon_no == u"4":
            self._m_receive_times_of_cdh = self.value4

        return getattr(self, '_m_receive_times_of_cdh', None)

    @property
    def solarcell_voltage(self):
        if hasattr(self, '_m_solarcell_voltage'):
            return self._m_solarcell_voltage

        if self.beacon_no == u"5":
            self._m_solarcell_voltage = (self.value2 * 0.05888)

        return getattr(self, '_m_solarcell_voltage', None)

    @property
    def value4_hex_left_digit(self):
        if hasattr(self, '_m_value4_hex_left_digit'):
            return self._m_value4_hex_left_digit

        self._m_value4_hex_left_digit = (u"a" if str(self.value4_hex_left) == u"10" else (u"b" if str(self.value4_hex_left) == u"11" else (u"c" if str(self.value4_hex_left) == u"12" else (u"d" if str(self.value4_hex_left) == u"13" else (u"e" if str(self.value4_hex_left) == u"14" else (u"f" if str(self.value4_hex_left) == u"15" else str(self.value4_hex_left)))))))
        return getattr(self, '_m_value4_hex_left_digit', None)

    @property
    def value1_hex_right(self):
        if hasattr(self, '_m_value1_hex_right'):
            return self._m_value1_hex_right

        self._m_value1_hex_right = (self.value1 % 16)
        return getattr(self, '_m_value1_hex_right', None)

    @property
    def value4_hex_right(self):
        if hasattr(self, '_m_value4_hex_right'):
            return self._m_value4_hex_right

        self._m_value4_hex_right = (self.value4 % 16)
        return getattr(self, '_m_value4_hex_right', None)

    @property
    def value4_hex_right_digit(self):
        if hasattr(self, '_m_value4_hex_right_digit'):
            return self._m_value4_hex_right_digit

        self._m_value4_hex_right_digit = (u"a" if str(self.value4_hex_right) == u"10" else (u"b" if str(self.value4_hex_right) == u"11" else (u"c" if str(self.value4_hex_right) == u"12" else (u"d" if str(self.value4_hex_right) == u"13" else (u"e" if str(self.value4_hex_right) == u"14" else (u"f" if str(self.value4_hex_right) == u"15" else str(self.value4_hex_right)))))))
        return getattr(self, '_m_value4_hex_right_digit', None)

    @property
    def value1_hex(self):
        if hasattr(self, '_m_value1_hex'):
            return self._m_value1_hex

        self._m_value1_hex = self.value1_hex_left_digit + self.value1_hex_right_digit
        return getattr(self, '_m_value1_hex', None)

    @property
    def value2_hex_right_digit(self):
        if hasattr(self, '_m_value2_hex_right_digit'):
            return self._m_value2_hex_right_digit

        self._m_value2_hex_right_digit = (u"a" if str(self.value2_hex_right) == u"10" else (u"b" if str(self.value2_hex_right) == u"11" else (u"c" if str(self.value2_hex_right) == u"12" else (u"d" if str(self.value2_hex_right) == u"13" else (u"e" if str(self.value2_hex_right) == u"14" else (u"f" if str(self.value2_hex_right) == u"15" else str(self.value2_hex_right)))))))
        return getattr(self, '_m_value2_hex_right_digit', None)

    @property
    def value4_hex_left(self):
        if hasattr(self, '_m_value4_hex_left'):
            return self._m_value4_hex_left

        self._m_value4_hex_left = self.value4 // 16
        return getattr(self, '_m_value4_hex_left', None)

    @property
    def value2_hex_left_digit(self):
        if hasattr(self, '_m_value2_hex_left_digit'):
            return self._m_value2_hex_left_digit

        self._m_value2_hex_left_digit = (u"a" if str(self.value2_hex_left) == u"10" else (u"b" if str(self.value2_hex_left) == u"11" else (u"c" if str(self.value2_hex_left) == u"12" else (u"d" if str(self.value2_hex_left) == u"13" else (u"e" if str(self.value2_hex_left) == u"14" else (u"f" if str(self.value2_hex_left) == u"15" else str(self.value2_hex_left)))))))
        return getattr(self, '_m_value2_hex_left_digit', None)

    @property
    def temperature_1(self):
        if hasattr(self, '_m_temperature_1'):
            return self._m_temperature_1

        if self.beacon_no == u"3":
            self._m_temperature_1 = self.value2

        return getattr(self, '_m_temperature_1', None)

    @property
    def value2_hex(self):
        if hasattr(self, '_m_value2_hex'):
            return self._m_value2_hex

        self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
        return getattr(self, '_m_value2_hex', None)

    @property
    def mode(self):
        if hasattr(self, '_m_mode'):
            return self._m_mode

        if self.beacon_no == u"4":
            self._m_mode = self.value1

        return getattr(self, '_m_mode', None)

    @property
    def value4_hex(self):
        if hasattr(self, '_m_value4_hex'):
            return self._m_value4_hex

        self._m_value4_hex = self.value4_hex_left_digit + self.value4_hex_right_digit
        return getattr(self, '_m_value4_hex', None)

    @property
    def value3_hex_left_digit(self):
        if hasattr(self, '_m_value3_hex_left_digit'):
            return self._m_value3_hex_left_digit

        self._m_value3_hex_left_digit = (u"a" if str(self.value3_hex_left) == u"10" else (u"b" if str(self.value3_hex_left) == u"11" else (u"c" if str(self.value3_hex_left) == u"12" else (u"d" if str(self.value3_hex_left) == u"13" else (u"e" if str(self.value3_hex_left) == u"14" else (u"f" if str(self.value3_hex_left) == u"15" else str(self.value3_hex_left)))))))
        return getattr(self, '_m_value3_hex_left_digit', None)

    @property
    def value2_hex_left(self):
        if hasattr(self, '_m_value2_hex_left'):
            return self._m_value2_hex_left

        self._m_value2_hex_left = self.value2 // 16
        return getattr(self, '_m_value2_hex_left', None)

    @property
    def solarcell_current(self):
        if hasattr(self, '_m_solarcell_current'):
            return self._m_solarcell_current

        if self.beacon_no == u"5":
            self._m_solarcell_current = (self.value1 * 0.007906)

        return getattr(self, '_m_solarcell_current', None)

    @property
    def value1_hex_left_digit(self):
        if hasattr(self, '_m_value1_hex_left_digit'):
            return self._m_value1_hex_left_digit

        self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
        return getattr(self, '_m_value1_hex_left_digit', None)


