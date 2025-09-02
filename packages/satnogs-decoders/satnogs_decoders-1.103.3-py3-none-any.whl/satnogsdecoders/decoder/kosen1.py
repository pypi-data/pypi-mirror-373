# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Kosen1(KaitaiStruct):
    """:field callsign: callsign
    :field s: s
    :field rssi: rssi
    :field battery_temperature: bat_t
    :field battery_voltage: bat_v
    :field battery_current: bat_i
    :field load_current: load_i
    :field solar_cell_output_current_minus_z: sc_z
    :field solar_cell_output_current_minus_y: sc_y
    :field solar_cell_output_current_minus_x: sc_x
    :field necessary_for_lengthcheck: necessary_for_lengthcheck
    :field beacon: beacon
    
    .. seealso::
       Source - https://space.kochi-ct.jp/kosen-1/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.callsign = (self._io.read_bytes(8)).decode(u"ASCII")
        if not self.callsign == u"kosen-1 ":
            raise kaitaistruct.ValidationNotEqualError(u"kosen-1 ", self.callsign, self._io, u"/seq/0")
        self.s = (self._io.read_bytes(2)).decode(u"ASCII")
        if not  ((self.s == u"s1") or (self.s == u"s2") or (self.s == u"S1") or (self.s == u"S2")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.s, self._io, u"/seq/1")
        self.value1 = self._io.read_u1()
        self.value2 = self._io.read_u1()
        self.value3 = self._io.read_u1()
        self.value4 = self._io.read_u1()
        self.lengthcheck = (self._io.read_bytes_full()).decode(u"utf-8")

    @property
    def bat_v(self):
        if hasattr(self, '_m_bat_v'):
            return self._m_bat_v

        if  ((self.value3 != 255) and (self.s == u"s1")) :
            self._m_bat_v = (0.0253 * self.value3)

        return getattr(self, '_m_bat_v', None)

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
    def value2_hex_right(self):
        if hasattr(self, '_m_value2_hex_right'):
            return self._m_value2_hex_right

        self._m_value2_hex_right = (self.value2 % 16)
        return getattr(self, '_m_value2_hex_right', None)

    @property
    def value3_hex(self):
        if hasattr(self, '_m_value3_hex'):
            return self._m_value3_hex

        self._m_value3_hex = (u".." if self.value3_hex_left_digit + self.value3_hex_right_digit == u"ff" else self.value3_hex_left_digit + self.value3_hex_right_digit)
        return getattr(self, '_m_value3_hex', None)

    @property
    def rssi(self):
        if hasattr(self, '_m_rssi'):
            return self._m_rssi

        if  ((self.value1 != 255) and (self.s == u"s1")) :
            self._m_rssi = ((0.409 * self.value1) - 127.4)

        return getattr(self, '_m_rssi', None)

    @property
    def value3_hex_right(self):
        if hasattr(self, '_m_value3_hex_right'):
            return self._m_value3_hex_right

        self._m_value3_hex_right = (self.value3 % 16)
        return getattr(self, '_m_value3_hex_right', None)

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

        self._m_beacon = self.s + u" " + self.value1_hex + u" " + self.value2_hex + u" " + self.value3_hex + u" " + self.value4_hex
        return getattr(self, '_m_beacon', None)

    @property
    def sc_x(self):
        if hasattr(self, '_m_sc_x'):
            return self._m_sc_x

        if  ((self.value4 != 255) and (self.s == u"s2")) :
            self._m_sc_x = (self.value4 / 0.256)

        return getattr(self, '_m_sc_x', None)

    @property
    def value3_hex_left(self):
        if hasattr(self, '_m_value3_hex_left'):
            return self._m_value3_hex_left

        self._m_value3_hex_left = self.value3 // 16
        return getattr(self, '_m_value3_hex_left', None)

    @property
    def load_i(self):
        if hasattr(self, '_m_load_i'):
            return self._m_load_i

        if  ((self.value1 != 255) and (self.s == u"s2")) :
            self._m_load_i = (self.value1 / 0.1024)

        return getattr(self, '_m_load_i', None)

    @property
    def bat_i(self):
        if hasattr(self, '_m_bat_i'):
            return self._m_bat_i

        if  ((self.value4 != 255) and (self.s == u"s1")) :
            self._m_bat_i = ((self.value4 - 128) / 0.0512)

        return getattr(self, '_m_bat_i', None)

    @property
    def sc_z(self):
        if hasattr(self, '_m_sc_z'):
            return self._m_sc_z

        if  ((self.value2 != 255) and (self.s == u"s2")) :
            self._m_sc_z = (self.value2 / 0.256)

        return getattr(self, '_m_sc_z', None)

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

        self._m_value1_hex = (u".." if self.value1_hex_left_digit + self.value1_hex_right_digit == u"ff" else self.value1_hex_left_digit + self.value1_hex_right_digit)
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
    def value2_hex(self):
        if hasattr(self, '_m_value2_hex'):
            return self._m_value2_hex

        self._m_value2_hex = (u".." if self.value2_hex_left_digit + self.value2_hex_right_digit == u"ff" else self.value2_hex_left_digit + self.value2_hex_right_digit)
        return getattr(self, '_m_value2_hex', None)

    @property
    def value4_hex(self):
        if hasattr(self, '_m_value4_hex'):
            return self._m_value4_hex

        self._m_value4_hex = (u".." if self.value4_hex_left_digit + self.value4_hex_right_digit == u"ff" else self.value4_hex_left_digit + self.value4_hex_right_digit)
        return getattr(self, '_m_value4_hex', None)

    @property
    def bat_t(self):
        if hasattr(self, '_m_bat_t'):
            return self._m_bat_t

        if  ((self.value2 != 255) and (self.s == u"s1")) :
            self._m_bat_t = ((((((0.00003 * self.value2) * self.value2) * self.value2) - ((0.011 * self.value2) * self.value2)) + (1.49 * self.value2)) - 28.1)

        return getattr(self, '_m_bat_t', None)

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
    def value1_hex_left_digit(self):
        if hasattr(self, '_m_value1_hex_left_digit'):
            return self._m_value1_hex_left_digit

        self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
        return getattr(self, '_m_value1_hex_left_digit', None)

    @property
    def sc_y(self):
        if hasattr(self, '_m_sc_y'):
            return self._m_sc_y

        if  ((self.value3 != 255) and (self.s == u"s2")) :
            self._m_sc_y = (self.value3 / 0.256)

        return getattr(self, '_m_sc_y', None)


