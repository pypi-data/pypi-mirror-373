# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Teikyosat4(KaitaiStruct):
    """:field s: s
    :field rssi_vhf: rssi_vhf
    :field rssi_shf: rssi_shf
    :field debug_connector: debug_connector
    :field gnd: gnd
    :field plus_x: plus_x
    :field plus_y: plus_y
    :field minus_x: minus_x
    :field minus_y: minus_y
    :field necessary_for_lengthcheck: necessary_for_lengthcheck
    :field beacon: beacon
    
    .. seealso::
       Source - https://drive.usercontent.google.com/download?id=1pdAPBraX38qtzIzjj6hehnZAioILPKhL&export=download
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.s = (self._io.read_bytes(2)).decode(u"ASCII")
        if not  ((self.s == u"s1") or (self.s == u"s2") or (self.s == u"S1") or (self.s == u"S2")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.s, self._io, u"/seq/0")
        self.value1 = self._io.read_u1()
        self.value2 = self._io.read_u1()
        self.value3 = self._io.read_u1()
        self.value4 = self._io.read_u1()
        self.lengthcheck = (self._io.read_bytes_full()).decode(u"utf-8")

    @property
    def debug_connector(self):
        if hasattr(self, '_m_debug_connector'):
            return self._m_debug_connector

        if  ((self.s == u"s1") or (self.s == u"S1")) :
            self._m_debug_connector = self.value3

        return getattr(self, '_m_debug_connector', None)

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
    def minus_x(self):
        if hasattr(self, '_m_minus_x'):
            return self._m_minus_x

        if  ((self.s == u"s2") or (self.s == u"S2")) :
            self._m_minus_x = ((self.value3 * 5.00) / 255)

        return getattr(self, '_m_minus_x', None)

    @property
    def plus_y(self):
        if hasattr(self, '_m_plus_y'):
            return self._m_plus_y

        if  ((self.s == u"s2") or (self.s == u"S2")) :
            self._m_plus_y = ((self.value2 * 5.00) / 255)

        return getattr(self, '_m_plus_y', None)

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
    def value3_hex_left(self):
        if hasattr(self, '_m_value3_hex_left'):
            return self._m_value3_hex_left

        self._m_value3_hex_left = self.value3 // 16
        return getattr(self, '_m_value3_hex_left', None)

    @property
    def rssi_shf(self):
        if hasattr(self, '_m_rssi_shf'):
            return self._m_rssi_shf

        if  ((self.s == u"s1") or (self.s == u"S1")) :
            self._m_rssi_shf = ((self.value2 * 5.00) / 255)

        return getattr(self, '_m_rssi_shf', None)

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
    def gnd(self):
        if hasattr(self, '_m_gnd'):
            return self._m_gnd

        if  ((self.s == u"s1") or (self.s == u"S1")) :
            self._m_gnd = self.value4

        return getattr(self, '_m_gnd', None)

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
    def plus_x(self):
        if hasattr(self, '_m_plus_x'):
            return self._m_plus_x

        if  ((self.s == u"s2") or (self.s == u"S2")) :
            self._m_plus_x = ((self.value1 * 5.00) / 255)

        return getattr(self, '_m_plus_x', None)

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
    def value3_hex_left_digit(self):
        if hasattr(self, '_m_value3_hex_left_digit'):
            return self._m_value3_hex_left_digit

        self._m_value3_hex_left_digit = (u"a" if str(self.value3_hex_left) == u"10" else (u"b" if str(self.value3_hex_left) == u"11" else (u"c" if str(self.value3_hex_left) == u"12" else (u"d" if str(self.value3_hex_left) == u"13" else (u"e" if str(self.value3_hex_left) == u"14" else (u"f" if str(self.value3_hex_left) == u"15" else str(self.value3_hex_left)))))))
        return getattr(self, '_m_value3_hex_left_digit', None)

    @property
    def minus_y(self):
        if hasattr(self, '_m_minus_y'):
            return self._m_minus_y

        if  ((self.s == u"s2") or (self.s == u"S2")) :
            self._m_minus_y = ((self.value4 * 5.00) / 255)

        return getattr(self, '_m_minus_y', None)

    @property
    def value2_hex_left(self):
        if hasattr(self, '_m_value2_hex_left'):
            return self._m_value2_hex_left

        self._m_value2_hex_left = self.value2 // 16
        return getattr(self, '_m_value2_hex_left', None)

    @property
    def rssi_vhf(self):
        if hasattr(self, '_m_rssi_vhf'):
            return self._m_rssi_vhf

        if  ((self.s == u"s1") or (self.s == u"S1")) :
            self._m_rssi_vhf = ((self.value1 * 5.00) / 255)

        return getattr(self, '_m_rssi_vhf', None)

    @property
    def value1_hex_left_digit(self):
        if hasattr(self, '_m_value1_hex_left_digit'):
            return self._m_value1_hex_left_digit

        self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
        return getattr(self, '_m_value1_hex_left_digit', None)


