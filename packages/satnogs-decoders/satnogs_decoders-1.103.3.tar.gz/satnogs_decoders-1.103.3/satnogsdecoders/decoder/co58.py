# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Co58(KaitaiStruct):
    """:field beacon_type: beacon_types.type_check.beacon_type
    :field time_counter: beacon_types.type_check.time_counter
    :field uplink_counter: beacon_types.type_check.uplink_counter
    :field camera_counter: beacon_types.type_check.camera_counter
    :field sel_reset_counter: beacon_types.type_check.sel_reset_counter
    :field antenna_deployed: beacon_types.type_check.antenna_deployed
    :field cw_duty_ratio: beacon_types.type_check.cw_duty_ratio
    :field obc_reset: beacon_types.type_check.obc_reset
    :field state_of_charge: beacon_types.type_check.state_of_charge
    :field state_of_obc: beacon_types.type_check.state_of_obc
    :field state_of_tx_tnc: beacon_types.type_check.state_of_tx_tnc
    :field undefined: beacon_types.type_check.undefined
    :field rssi_max_between_xiv1_and_xiv2: beacon_types.type_check.rssi_max_between_xiv1_and_xiv2
    :field batt_v: beacon_types.type_check.batt_v
    :field sol_v: beacon_types.type_check.sol_v
    :field batt_t_from_ad_conversion: beacon_types.type_check.batt_t_from_ad_conversion
    :field plus_x_i: beacon_types.type_check.plus_x_i
    :field minus_x_i: beacon_types.type_check.minus_x_i
    :field plus_y_i: beacon_types.type_check.plus_y_i
    :field minus_y_i: beacon_types.type_check.minus_y_i
    :field plus_z_i: beacon_types.type_check.plus_z_i
    :field minus_z_i: beacon_types.type_check.minus_z_i
    :field plus_x_t: beacon_types.type_check.plus_x_t
    :field minus_x_t: beacon_types.type_check.minus_x_t
    :field plus_y_t: beacon_types.type_check.plus_y_t
    :field minus_y_t: beacon_types.type_check.minus_y_t
    :field plus_z_t: beacon_types.type_check.plus_z_t
    :field minus_z_t: beacon_types.type_check.minus_z_t
    :field fm_transmitter_t: beacon_types.type_check.fm_transmitter_t
    :field batt_v_from_obc: beacon_types.type_check.batt_v_from_obc
    :field sol_v_from_obc: beacon_types.type_check.sol_v_from_obc
    :field batt_t_from_obc: beacon_types.type_check.batt_t_from_obc
    :field rssi_max_between_xiv3_and_xiv6: beacon_types.type_check.rssi_max_between_xiv3_and_xiv6
    :field beacon: beacon_types.type_check.beacon
    :field discard: beacon_types.type_check.discard_discard
    
    .. seealso::
       Source - https://web.archive.org/web/20120516012116/http:/www.space.t.u-tokyo.ac.jp/gs/application.html
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.xiv = (self._io.read_bytes(3)).decode(u"ASCII")
        if not self.xiv == u"xiv":
            raise kaitaistruct.ValidationNotEqualError(u"xiv", self.xiv, self._io, u"/seq/0")
        self.beacon_types = Co58.BeaconTypesT(self._io, self, self._root)

    class Xiv3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.batt_v_raw = self._io.read_u1()
            self.sol_v_raw = self._io.read_u1()
            self.batt_t_from_ad_conversion_raw = self._io.read_u1()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = self.batt_v_raw
            return getattr(self, '_m_value1', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

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

            self._m_value3_hex = self.value3_hex_left_digit + self.value3_hex_right_digit
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

            self._m_beacon = u"xiv3 " + self.value1_hex + self.value2_hex + self.value3_hex
            return getattr(self, '_m_beacon', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 3
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = self.sol_v_raw
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def sol_v(self):
            if hasattr(self, '_m_sol_v'):
                return self._m_sol_v

            self._m_sol_v = (self.sol_v_raw * 0.0754)
            return getattr(self, '_m_sol_v', None)

        @property
        def batt_v(self):
            if hasattr(self, '_m_batt_v'):
                return self._m_batt_v

            self._m_batt_v = (self.batt_v_raw * 0.07526666)
            return getattr(self, '_m_batt_v', None)

        @property
        def value1_hex_right(self):
            if hasattr(self, '_m_value1_hex_right'):
                return self._m_value1_hex_right

            self._m_value1_hex_right = (self.value1 % 16)
            return getattr(self, '_m_value1_hex_right', None)

        @property
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = self.batt_t_from_ad_conversion_raw
            return getattr(self, '_m_value3', None)

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
        def value2_hex_left_digit(self):
            if hasattr(self, '_m_value2_hex_left_digit'):
                return self._m_value2_hex_left_digit

            self._m_value2_hex_left_digit = (u"a" if str(self.value2_hex_left) == u"10" else (u"b" if str(self.value2_hex_left) == u"11" else (u"c" if str(self.value2_hex_left) == u"12" else (u"d" if str(self.value2_hex_left) == u"13" else (u"e" if str(self.value2_hex_left) == u"14" else (u"f" if str(self.value2_hex_left) == u"15" else str(self.value2_hex_left)))))))
            return getattr(self, '_m_value2_hex_left_digit', None)

        @property
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

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
        def batt_t_from_ad_conversion(self):
            if hasattr(self, '_m_batt_t_from_ad_conversion'):
                return self._m_batt_t_from_ad_conversion

            self._m_batt_t_from_ad_conversion = ((self.batt_t_from_ad_conversion_raw * 0.5948) - 67.203)
            return getattr(self, '_m_batt_t_from_ad_conversion', None)

        @property
        def value1_hex_left_digit(self):
            if hasattr(self, '_m_value1_hex_left_digit'):
                return self._m_value1_hex_left_digit

            self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
            return getattr(self, '_m_value1_hex_left_digit', None)


    class Xiv2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.byte_1 = self._io.read_u1()
            self.byte_2 = self._io.read_u1()
            self.byte_3 = self._io.read_u1()
            self.rssi_max_between_xiv1_and_xiv2_raw = self._io.read_u1()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = self.byte_1
            return getattr(self, '_m_value1', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

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

            self._m_value3_hex = self.value3_hex_left_digit + self.value3_hex_right_digit
            return getattr(self, '_m_value3_hex', None)

        @property
        def value3_hex_right(self):
            if hasattr(self, '_m_value3_hex_right'):
                return self._m_value3_hex_right

            self._m_value3_hex_right = (self.value3 % 16)
            return getattr(self, '_m_value3_hex_right', None)

        @property
        def rssi_max_between_xiv1_and_xiv2(self):
            if hasattr(self, '_m_rssi_max_between_xiv1_and_xiv2'):
                return self._m_rssi_max_between_xiv1_and_xiv2

            self._m_rssi_max_between_xiv1_and_xiv2 = ((((self.rssi_max_between_xiv1_and_xiv2_raw * 4.77) * 4) / 255) - 107)
            return getattr(self, '_m_rssi_max_between_xiv1_and_xiv2', None)

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

            self._m_beacon = u"xiv2 " + self.value1_hex + self.value2_hex + self.value3_hex + self.value4_hex
            return getattr(self, '_m_beacon', None)

        @property
        def sel_reset_counter(self):
            if hasattr(self, '_m_sel_reset_counter'):
                return self._m_sel_reset_counter

            self._m_sel_reset_counter = (self.byte_2 & 7)
            return getattr(self, '_m_sel_reset_counter', None)

        @property
        def obc_reset(self):
            if hasattr(self, '_m_obc_reset'):
                return self._m_obc_reset

            self._m_obc_reset = ((self.byte_2 >> 6) & 1)
            return getattr(self, '_m_obc_reset', None)

        @property
        def value4(self):
            if hasattr(self, '_m_value4'):
                return self._m_value4

            self._m_value4 = self.rssi_max_between_xiv1_and_xiv2_raw
            return getattr(self, '_m_value4', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 2
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = self.byte_2
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def state_of_charge(self):
            if hasattr(self, '_m_state_of_charge'):
                return self._m_state_of_charge

            self._m_state_of_charge = (self.byte_2 >> 7)
            return getattr(self, '_m_state_of_charge', None)

        @property
        def antenna_deployed(self):
            if hasattr(self, '_m_antenna_deployed'):
                return self._m_antenna_deployed

            self._m_antenna_deployed = ((self.byte_2 >> 3) & 1)
            return getattr(self, '_m_antenna_deployed', None)

        @property
        def undefined(self):
            if hasattr(self, '_m_undefined'):
                return self._m_undefined

            self._m_undefined = (self.byte_3 >> 2)
            return getattr(self, '_m_undefined', None)

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
        def uplink_counter(self):
            if hasattr(self, '_m_uplink_counter'):
                return self._m_uplink_counter

            self._m_uplink_counter = (self.byte_1 & 31)
            return getattr(self, '_m_uplink_counter', None)

        @property
        def value4_hex_right(self):
            if hasattr(self, '_m_value4_hex_right'):
                return self._m_value4_hex_right

            self._m_value4_hex_right = (self.value4 % 16)
            return getattr(self, '_m_value4_hex_right', None)

        @property
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = self.byte_3
            return getattr(self, '_m_value3', None)

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
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

        @property
        def value4_hex(self):
            if hasattr(self, '_m_value4_hex'):
                return self._m_value4_hex

            self._m_value4_hex = self.value4_hex_left_digit + self.value4_hex_right_digit
            return getattr(self, '_m_value4_hex', None)

        @property
        def cw_duty_ratio(self):
            if hasattr(self, '_m_cw_duty_ratio'):
                return self._m_cw_duty_ratio

            self._m_cw_duty_ratio = ((self.byte_2 >> 4) & 3)
            return getattr(self, '_m_cw_duty_ratio', None)

        @property
        def value3_hex_left_digit(self):
            if hasattr(self, '_m_value3_hex_left_digit'):
                return self._m_value3_hex_left_digit

            self._m_value3_hex_left_digit = (u"a" if str(self.value3_hex_left) == u"10" else (u"b" if str(self.value3_hex_left) == u"11" else (u"c" if str(self.value3_hex_left) == u"12" else (u"d" if str(self.value3_hex_left) == u"13" else (u"e" if str(self.value3_hex_left) == u"14" else (u"f" if str(self.value3_hex_left) == u"15" else str(self.value3_hex_left)))))))
            return getattr(self, '_m_value3_hex_left_digit', None)

        @property
        def camera_counter(self):
            if hasattr(self, '_m_camera_counter'):
                return self._m_camera_counter

            self._m_camera_counter = (self.byte_1 >> 5)
            return getattr(self, '_m_camera_counter', None)

        @property
        def value2_hex_left(self):
            if hasattr(self, '_m_value2_hex_left'):
                return self._m_value2_hex_left

            self._m_value2_hex_left = self.value2 // 16
            return getattr(self, '_m_value2_hex_left', None)

        @property
        def state_of_tx_tnc(self):
            if hasattr(self, '_m_state_of_tx_tnc'):
                return self._m_state_of_tx_tnc

            self._m_state_of_tx_tnc = ((self.byte_3 >> 1) & 1)
            return getattr(self, '_m_state_of_tx_tnc', None)

        @property
        def value1_hex_left_digit(self):
            if hasattr(self, '_m_value1_hex_left_digit'):
                return self._m_value1_hex_left_digit

            self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
            return getattr(self, '_m_value1_hex_left_digit', None)

        @property
        def state_of_obc(self):
            if hasattr(self, '_m_state_of_obc'):
                return self._m_state_of_obc

            self._m_state_of_obc = (self.byte_3 & 1)
            return getattr(self, '_m_state_of_obc', None)


    class Xiv6(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fm_transmitter_t_raw = self._io.read_u1()
            self.batt_v_from_obc_raw = self._io.read_u1()
            self.sol_v_from_obc_raw = self._io.read_u1()
            self.batt_t_from_obc_raw = self._io.read_u1()
            self.rssi_max_between_xiv3_and_xiv6_raw = self._io.read_u1()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = self.fm_transmitter_t_raw
            return getattr(self, '_m_value1', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

        @property
        def value5_hex_right(self):
            if hasattr(self, '_m_value5_hex_right'):
                return self._m_value5_hex_right

            self._m_value5_hex_right = (self.value5 % 16)
            return getattr(self, '_m_value5_hex_right', None)

        @property
        def value1_hex_left(self):
            if hasattr(self, '_m_value1_hex_left'):
                return self._m_value1_hex_left

            self._m_value1_hex_left = self.value1 // 16
            return getattr(self, '_m_value1_hex_left', None)

        @property
        def value5_hex_left_digit(self):
            if hasattr(self, '_m_value5_hex_left_digit'):
                return self._m_value5_hex_left_digit

            self._m_value5_hex_left_digit = (u"a" if str(self.value5_hex_left) == u"10" else (u"b" if str(self.value5_hex_left) == u"11" else (u"c" if str(self.value5_hex_left) == u"12" else (u"d" if str(self.value5_hex_left) == u"13" else (u"e" if str(self.value5_hex_left) == u"14" else (u"f" if str(self.value5_hex_left) == u"15" else str(self.value5_hex_left)))))))
            return getattr(self, '_m_value5_hex_left_digit', None)

        @property
        def batt_v_from_obc(self):
            if hasattr(self, '_m_batt_v_from_obc'):
                return self._m_batt_v_from_obc

            self._m_batt_v_from_obc = ((self.batt_v_from_obc_raw * 4.5) / 255)
            return getattr(self, '_m_batt_v_from_obc', None)

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

            self._m_beacon = u"xiv6 " + self.value1_hex + self.value2_hex + self.value3_hex + self.value4_hex + self.value5_hex
            return getattr(self, '_m_beacon', None)

        @property
        def value5_hex(self):
            if hasattr(self, '_m_value5_hex'):
                return self._m_value5_hex

            self._m_value5_hex = self.value5_hex_left_digit + self.value5_hex_right_digit
            return getattr(self, '_m_value5_hex', None)

        @property
        def value4(self):
            if hasattr(self, '_m_value4'):
                return self._m_value4

            self._m_value4 = self.batt_t_from_obc_raw
            return getattr(self, '_m_value4', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 6
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = self.batt_v_from_obc_raw
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def value5_hex_left(self):
            if hasattr(self, '_m_value5_hex_left'):
                return self._m_value5_hex_left

            self._m_value5_hex_left = self.value5 // 16
            return getattr(self, '_m_value5_hex_left', None)

        @property
        def rssi_max_between_xiv3_and_xiv6(self):
            if hasattr(self, '_m_rssi_max_between_xiv3_and_xiv6'):
                return self._m_rssi_max_between_xiv3_and_xiv6

            self._m_rssi_max_between_xiv3_and_xiv6 = ((((self.rssi_max_between_xiv3_and_xiv6_raw * 4.77) * 4) / 255) - 107)
            return getattr(self, '_m_rssi_max_between_xiv3_and_xiv6', None)

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
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = self.sol_v_from_obc_raw
            return getattr(self, '_m_value3', None)

        @property
        def sol_v_from_obc(self):
            if hasattr(self, '_m_sol_v_from_obc'):
                return self._m_sol_v_from_obc

            self._m_sol_v_from_obc = ((((self.sol_v_from_obc_raw * 4.5) * 74.9) / 18.7) / 255)
            return getattr(self, '_m_sol_v_from_obc', None)

        @property
        def batt_t_from_obc(self):
            if hasattr(self, '_m_batt_t_from_obc'):
                return self._m_batt_t_from_obc

            self._m_batt_t_from_obc = ((self.batt_t_from_obc_raw * 0.5948) - 67.203)
            return getattr(self, '_m_batt_t_from_obc', None)

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
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

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
        def fm_transmitter_t(self):
            if hasattr(self, '_m_fm_transmitter_t'):
                return self._m_fm_transmitter_t

            self._m_fm_transmitter_t = ((self.fm_transmitter_t_raw * 0.5811) - 67.055)
            return getattr(self, '_m_fm_transmitter_t', None)

        @property
        def value2_hex_left(self):
            if hasattr(self, '_m_value2_hex_left'):
                return self._m_value2_hex_left

            self._m_value2_hex_left = self.value2 // 16
            return getattr(self, '_m_value2_hex_left', None)

        @property
        def value5(self):
            if hasattr(self, '_m_value5'):
                return self._m_value5

            self._m_value5 = self.rssi_max_between_xiv3_and_xiv6_raw
            return getattr(self, '_m_value5', None)

        @property
        def value5_hex_right_digit(self):
            if hasattr(self, '_m_value5_hex_right_digit'):
                return self._m_value5_hex_right_digit

            self._m_value5_hex_right_digit = (u"a" if str(self.value5_hex_right) == u"10" else (u"b" if str(self.value5_hex_right) == u"11" else (u"c" if str(self.value5_hex_right) == u"12" else (u"d" if str(self.value5_hex_right) == u"13" else (u"e" if str(self.value5_hex_right) == u"14" else (u"f" if str(self.value5_hex_right) == u"15" else str(self.value5_hex_right)))))))
            return getattr(self, '_m_value5_hex_right_digit', None)

        @property
        def value1_hex_left_digit(self):
            if hasattr(self, '_m_value1_hex_left_digit'):
                return self._m_value1_hex_left_digit

            self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
            return getattr(self, '_m_value1_hex_left_digit', None)


    class Xiv4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.plus_x_i_raw = self._io.read_u1()
            self.minus_x_i_raw = self._io.read_u1()
            self.plus_y_i_raw = self._io.read_u1()
            self.minus_y_i_raw = self._io.read_u1()
            self.plus_z_i_raw = self._io.read_u1()
            self.minus_z_i_raw = self._io.read_u1()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = self.plus_x_i_raw
            return getattr(self, '_m_value1', None)

        @property
        def value6_hex_left(self):
            if hasattr(self, '_m_value6_hex_left'):
                return self._m_value6_hex_left

            self._m_value6_hex_left = self.value6 // 16
            return getattr(self, '_m_value6_hex_left', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

        @property
        def value5_hex_right(self):
            if hasattr(self, '_m_value5_hex_right'):
                return self._m_value5_hex_right

            self._m_value5_hex_right = (self.value5 % 16)
            return getattr(self, '_m_value5_hex_right', None)

        @property
        def plus_z_i(self):
            if hasattr(self, '_m_plus_z_i'):
                return self._m_plus_z_i

            self._m_plus_z_i = ((self.plus_z_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_plus_z_i', None)

        @property
        def value1_hex_left(self):
            if hasattr(self, '_m_value1_hex_left'):
                return self._m_value1_hex_left

            self._m_value1_hex_left = self.value1 // 16
            return getattr(self, '_m_value1_hex_left', None)

        @property
        def value5_hex_left_digit(self):
            if hasattr(self, '_m_value5_hex_left_digit'):
                return self._m_value5_hex_left_digit

            self._m_value5_hex_left_digit = (u"a" if str(self.value5_hex_left) == u"10" else (u"b" if str(self.value5_hex_left) == u"11" else (u"c" if str(self.value5_hex_left) == u"12" else (u"d" if str(self.value5_hex_left) == u"13" else (u"e" if str(self.value5_hex_left) == u"14" else (u"f" if str(self.value5_hex_left) == u"15" else str(self.value5_hex_left)))))))
            return getattr(self, '_m_value5_hex_left_digit', None)

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

            self._m_beacon = u"xiv4 " + self.value1_hex + self.value2_hex + self.value3_hex + self.value4_hex + self.value5_hex + self.value6_hex
            return getattr(self, '_m_beacon', None)

        @property
        def value5_hex(self):
            if hasattr(self, '_m_value5_hex'):
                return self._m_value5_hex

            self._m_value5_hex = self.value5_hex_left_digit + self.value5_hex_right_digit
            return getattr(self, '_m_value5_hex', None)

        @property
        def value4(self):
            if hasattr(self, '_m_value4'):
                return self._m_value4

            self._m_value4 = self.minus_y_i_raw
            return getattr(self, '_m_value4', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 4
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = self.minus_x_i_raw
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def value5_hex_left(self):
            if hasattr(self, '_m_value5_hex_left'):
                return self._m_value5_hex_left

            self._m_value5_hex_left = self.value5 // 16
            return getattr(self, '_m_value5_hex_left', None)

        @property
        def value6(self):
            if hasattr(self, '_m_value6'):
                return self._m_value6

            self._m_value6 = self.minus_z_i_raw
            return getattr(self, '_m_value6', None)

        @property
        def minus_y_i(self):
            if hasattr(self, '_m_minus_y_i'):
                return self._m_minus_y_i

            self._m_minus_y_i = ((self.minus_y_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_minus_y_i', None)

        @property
        def value6_hex(self):
            if hasattr(self, '_m_value6_hex'):
                return self._m_value6_hex

            self._m_value6_hex = self.value6_hex_left_digit + self.value6_hex_right_digit
            return getattr(self, '_m_value6_hex', None)

        @property
        def plus_x_i(self):
            if hasattr(self, '_m_plus_x_i'):
                return self._m_plus_x_i

            self._m_plus_x_i = ((self.plus_x_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_plus_x_i', None)

        @property
        def plus_y_i(self):
            if hasattr(self, '_m_plus_y_i'):
                return self._m_plus_y_i

            self._m_plus_y_i = ((self.plus_y_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_plus_y_i', None)

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
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = self.plus_y_i_raw
            return getattr(self, '_m_value3', None)

        @property
        def minus_z_i(self):
            if hasattr(self, '_m_minus_z_i'):
                return self._m_minus_z_i

            self._m_minus_z_i = ((self.minus_z_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_minus_z_i', None)

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
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

        @property
        def value6_hex_right(self):
            if hasattr(self, '_m_value6_hex_right'):
                return self._m_value6_hex_right

            self._m_value6_hex_right = (self.value6 % 16)
            return getattr(self, '_m_value6_hex_right', None)

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
        def value6_hex_left_digit(self):
            if hasattr(self, '_m_value6_hex_left_digit'):
                return self._m_value6_hex_left_digit

            self._m_value6_hex_left_digit = (u"a" if str(self.value6_hex_left) == u"10" else (u"b" if str(self.value6_hex_left) == u"11" else (u"c" if str(self.value6_hex_left) == u"12" else (u"d" if str(self.value6_hex_left) == u"13" else (u"e" if str(self.value6_hex_left) == u"14" else (u"f" if str(self.value6_hex_left) == u"15" else str(self.value6_hex_left)))))))
            return getattr(self, '_m_value6_hex_left_digit', None)

        @property
        def value2_hex_left(self):
            if hasattr(self, '_m_value2_hex_left'):
                return self._m_value2_hex_left

            self._m_value2_hex_left = self.value2 // 16
            return getattr(self, '_m_value2_hex_left', None)

        @property
        def value6_hex_right_digit(self):
            if hasattr(self, '_m_value6_hex_right_digit'):
                return self._m_value6_hex_right_digit

            self._m_value6_hex_right_digit = (u"a" if str(self.value6_hex_right) == u"10" else (u"b" if str(self.value6_hex_right) == u"11" else (u"c" if str(self.value6_hex_right) == u"12" else (u"d" if str(self.value6_hex_right) == u"13" else (u"e" if str(self.value6_hex_right) == u"14" else (u"f" if str(self.value6_hex_right) == u"15" else str(self.value6_hex_right)))))))
            return getattr(self, '_m_value6_hex_right_digit', None)

        @property
        def minus_x_i(self):
            if hasattr(self, '_m_minus_x_i'):
                return self._m_minus_x_i

            self._m_minus_x_i = ((self.minus_x_i_raw * 2.4) - 2.4)
            return getattr(self, '_m_minus_x_i', None)

        @property
        def value5(self):
            if hasattr(self, '_m_value5'):
                return self._m_value5

            self._m_value5 = self.plus_z_i_raw
            return getattr(self, '_m_value5', None)

        @property
        def value5_hex_right_digit(self):
            if hasattr(self, '_m_value5_hex_right_digit'):
                return self._m_value5_hex_right_digit

            self._m_value5_hex_right_digit = (u"a" if str(self.value5_hex_right) == u"10" else (u"b" if str(self.value5_hex_right) == u"11" else (u"c" if str(self.value5_hex_right) == u"12" else (u"d" if str(self.value5_hex_right) == u"13" else (u"e" if str(self.value5_hex_right) == u"14" else (u"f" if str(self.value5_hex_right) == u"15" else str(self.value5_hex_right)))))))
            return getattr(self, '_m_value5_hex_right_digit', None)

        @property
        def value1_hex_left_digit(self):
            if hasattr(self, '_m_value1_hex_left_digit'):
                return self._m_value1_hex_left_digit

            self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
            return getattr(self, '_m_value1_hex_left_digit', None)


    class Discard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.discard = self._io.read_bits_int_be(1) != 0

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            self._m_discard_discard = int(self.discard) // 0
            return getattr(self, '_m_discard_discard', None)


    class Xiv5(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.plus_x_t_raw = self._io.read_u1()
            self.minus_x_t_raw = self._io.read_u1()
            self.plus_y_t_raw = self._io.read_u1()
            self.minus_y_t_raw = self._io.read_u1()
            self.plus_z_t_raw = self._io.read_u1()
            self.minus_z_t_raw = self._io.read_u1()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = self.plus_x_t_raw
            return getattr(self, '_m_value1', None)

        @property
        def value6_hex_left(self):
            if hasattr(self, '_m_value6_hex_left'):
                return self._m_value6_hex_left

            self._m_value6_hex_left = self.value6 // 16
            return getattr(self, '_m_value6_hex_left', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

        @property
        def value5_hex_right(self):
            if hasattr(self, '_m_value5_hex_right'):
                return self._m_value5_hex_right

            self._m_value5_hex_right = (self.value5 % 16)
            return getattr(self, '_m_value5_hex_right', None)

        @property
        def value1_hex_left(self):
            if hasattr(self, '_m_value1_hex_left'):
                return self._m_value1_hex_left

            self._m_value1_hex_left = self.value1 // 16
            return getattr(self, '_m_value1_hex_left', None)

        @property
        def value5_hex_left_digit(self):
            if hasattr(self, '_m_value5_hex_left_digit'):
                return self._m_value5_hex_left_digit

            self._m_value5_hex_left_digit = (u"a" if str(self.value5_hex_left) == u"10" else (u"b" if str(self.value5_hex_left) == u"11" else (u"c" if str(self.value5_hex_left) == u"12" else (u"d" if str(self.value5_hex_left) == u"13" else (u"e" if str(self.value5_hex_left) == u"14" else (u"f" if str(self.value5_hex_left) == u"15" else str(self.value5_hex_left)))))))
            return getattr(self, '_m_value5_hex_left_digit', None)

        @property
        def minus_z_t(self):
            if hasattr(self, '_m_minus_z_t'):
                return self._m_minus_z_t

            self._m_minus_z_t = ((self.minus_z_t_raw * 0.5932) - 66.483)
            return getattr(self, '_m_minus_z_t', None)

        @property
        def plus_z_t(self):
            if hasattr(self, '_m_plus_z_t'):
                return self._m_plus_z_t

            self._m_plus_z_t = ((self.plus_z_t_raw * 0.5880) - 64.903)
            return getattr(self, '_m_plus_z_t', None)

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

            self._m_beacon = u"xiv5 " + self.value1_hex + self.value2_hex + self.value3_hex + self.value4_hex + self.value5_hex + self.value6_hex
            return getattr(self, '_m_beacon', None)

        @property
        def value5_hex(self):
            if hasattr(self, '_m_value5_hex'):
                return self._m_value5_hex

            self._m_value5_hex = self.value5_hex_left_digit + self.value5_hex_right_digit
            return getattr(self, '_m_value5_hex', None)

        @property
        def value4(self):
            if hasattr(self, '_m_value4'):
                return self._m_value4

            self._m_value4 = self.minus_y_t_raw
            return getattr(self, '_m_value4', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 5
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = self.minus_x_t_raw
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def value5_hex_left(self):
            if hasattr(self, '_m_value5_hex_left'):
                return self._m_value5_hex_left

            self._m_value5_hex_left = self.value5 // 16
            return getattr(self, '_m_value5_hex_left', None)

        @property
        def value6(self):
            if hasattr(self, '_m_value6'):
                return self._m_value6

            self._m_value6 = self.minus_z_t_raw
            return getattr(self, '_m_value6', None)

        @property
        def value6_hex(self):
            if hasattr(self, '_m_value6_hex'):
                return self._m_value6_hex

            self._m_value6_hex = self.value6_hex_left_digit + self.value6_hex_right_digit
            return getattr(self, '_m_value6_hex', None)

        @property
        def plus_x_t(self):
            if hasattr(self, '_m_plus_x_t'):
                return self._m_plus_x_t

            self._m_plus_x_t = ((self.plus_x_t_raw * 0.5896) - 65.614)
            return getattr(self, '_m_plus_x_t', None)

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
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = self.plus_y_t_raw
            return getattr(self, '_m_value3', None)

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
        def minus_y_t(self):
            if hasattr(self, '_m_minus_y_t'):
                return self._m_minus_y_t

            self._m_minus_y_t = ((self.minus_y_t_raw * 0.5846) - 66.280)
            return getattr(self, '_m_minus_y_t', None)

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
        def minus_x_t(self):
            if hasattr(self, '_m_minus_x_t'):
                return self._m_minus_x_t

            self._m_minus_x_t = ((self.minus_x_t_raw * 0.5916) - 66.133)
            return getattr(self, '_m_minus_x_t', None)

        @property
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

        @property
        def value6_hex_right(self):
            if hasattr(self, '_m_value6_hex_right'):
                return self._m_value6_hex_right

            self._m_value6_hex_right = (self.value6 % 16)
            return getattr(self, '_m_value6_hex_right', None)

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
        def value6_hex_left_digit(self):
            if hasattr(self, '_m_value6_hex_left_digit'):
                return self._m_value6_hex_left_digit

            self._m_value6_hex_left_digit = (u"a" if str(self.value6_hex_left) == u"10" else (u"b" if str(self.value6_hex_left) == u"11" else (u"c" if str(self.value6_hex_left) == u"12" else (u"d" if str(self.value6_hex_left) == u"13" else (u"e" if str(self.value6_hex_left) == u"14" else (u"f" if str(self.value6_hex_left) == u"15" else str(self.value6_hex_left)))))))
            return getattr(self, '_m_value6_hex_left_digit', None)

        @property
        def plus_y_t(self):
            if hasattr(self, '_m_plus_y_t'):
                return self._m_plus_y_t

            self._m_plus_y_t = ((self.plus_y_t_raw * 0.5862) - 65.813)
            return getattr(self, '_m_plus_y_t', None)

        @property
        def value2_hex_left(self):
            if hasattr(self, '_m_value2_hex_left'):
                return self._m_value2_hex_left

            self._m_value2_hex_left = self.value2 // 16
            return getattr(self, '_m_value2_hex_left', None)

        @property
        def value6_hex_right_digit(self):
            if hasattr(self, '_m_value6_hex_right_digit'):
                return self._m_value6_hex_right_digit

            self._m_value6_hex_right_digit = (u"a" if str(self.value6_hex_right) == u"10" else (u"b" if str(self.value6_hex_right) == u"11" else (u"c" if str(self.value6_hex_right) == u"12" else (u"d" if str(self.value6_hex_right) == u"13" else (u"e" if str(self.value6_hex_right) == u"14" else (u"f" if str(self.value6_hex_right) == u"15" else str(self.value6_hex_right)))))))
            return getattr(self, '_m_value6_hex_right_digit', None)

        @property
        def value5(self):
            if hasattr(self, '_m_value5'):
                return self._m_value5

            self._m_value5 = self.plus_z_t_raw
            return getattr(self, '_m_value5', None)

        @property
        def value5_hex_right_digit(self):
            if hasattr(self, '_m_value5_hex_right_digit'):
                return self._m_value5_hex_right_digit

            self._m_value5_hex_right_digit = (u"a" if str(self.value5_hex_right) == u"10" else (u"b" if str(self.value5_hex_right) == u"11" else (u"c" if str(self.value5_hex_right) == u"12" else (u"d" if str(self.value5_hex_right) == u"13" else (u"e" if str(self.value5_hex_right) == u"14" else (u"f" if str(self.value5_hex_right) == u"15" else str(self.value5_hex_right)))))))
            return getattr(self, '_m_value5_hex_right_digit', None)

        @property
        def value1_hex_left_digit(self):
            if hasattr(self, '_m_value1_hex_left_digit'):
                return self._m_value1_hex_left_digit

            self._m_value1_hex_left_digit = (u"a" if str(self.value1_hex_left) == u"10" else (u"b" if str(self.value1_hex_left) == u"11" else (u"c" if str(self.value1_hex_left) == u"12" else (u"d" if str(self.value1_hex_left) == u"13" else (u"e" if str(self.value1_hex_left) == u"14" else (u"f" if str(self.value1_hex_left) == u"15" else str(self.value1_hex_left)))))))
            return getattr(self, '_m_value1_hex_left_digit', None)


    class BeaconTypesT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 13856:
                self.type_check = Co58.Xiv6(self._io, self, self._root)
            elif _on == 13600:
                self.type_check = Co58.Xiv5(self._io, self, self._root)
            elif _on == 12576:
                self.type_check = Co58.Xiv1(self._io, self, self._root)
            elif _on == 12832:
                self.type_check = Co58.Xiv2(self._io, self, self._root)
            elif _on == 13344:
                self.type_check = Co58.Xiv4(self._io, self, self._root)
            elif _on == 13088:
                self.type_check = Co58.Xiv3(self._io, self, self._root)
            else:
                self.type_check = Co58.Discard(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            self._m_check = self._io.read_u2be()
            return getattr(self, '_m_check', None)


    class Xiv1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_counter = self._io.read_bits_int_be(24)
            self._io.align_to_byte()
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def value1(self):
            if hasattr(self, '_m_value1'):
                return self._m_value1

            self._m_value1 = (self.time_counter >> 16)
            return getattr(self, '_m_value1', None)

        @property
        def value3_hex_right_digit(self):
            if hasattr(self, '_m_value3_hex_right_digit'):
                return self._m_value3_hex_right_digit

            self._m_value3_hex_right_digit = (u"a" if str(self.value3_hex_right) == u"10" else (u"b" if str(self.value3_hex_right) == u"11" else (u"c" if str(self.value3_hex_right) == u"12" else (u"d" if str(self.value3_hex_right) == u"13" else (u"e" if str(self.value3_hex_right) == u"14" else (u"f" if str(self.value3_hex_right) == u"15" else str(self.value3_hex_right)))))))
            return getattr(self, '_m_value3_hex_right_digit', None)

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

            self._m_value3_hex = self.value3_hex_left_digit + self.value3_hex_right_digit
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

            self._m_beacon = u"xiv1 " + self.value1_hex + self.value2_hex + self.value3_hex
            return getattr(self, '_m_beacon', None)

        @property
        def discard_discard(self):
            if hasattr(self, '_m_discard_discard'):
                return self._m_discard_discard

            if len(self.discard) != 0:
                self._m_discard_discard = int(self.discard) // 0

            return getattr(self, '_m_discard_discard', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 1
            return getattr(self, '_m_beacon_type', None)

        @property
        def value2(self):
            if hasattr(self, '_m_value2'):
                return self._m_value2

            self._m_value2 = ((self.time_counter >> 8) & 255)
            return getattr(self, '_m_value2', None)

        @property
        def value3_hex_left(self):
            if hasattr(self, '_m_value3_hex_left'):
                return self._m_value3_hex_left

            self._m_value3_hex_left = self.value3 // 16
            return getattr(self, '_m_value3_hex_left', None)

        @property
        def value1_hex_right(self):
            if hasattr(self, '_m_value1_hex_right'):
                return self._m_value1_hex_right

            self._m_value1_hex_right = (self.value1 % 16)
            return getattr(self, '_m_value1_hex_right', None)

        @property
        def value3(self):
            if hasattr(self, '_m_value3'):
                return self._m_value3

            self._m_value3 = (self.time_counter & 255)
            return getattr(self, '_m_value3', None)

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
        def value2_hex_left_digit(self):
            if hasattr(self, '_m_value2_hex_left_digit'):
                return self._m_value2_hex_left_digit

            self._m_value2_hex_left_digit = (u"a" if str(self.value2_hex_left) == u"10" else (u"b" if str(self.value2_hex_left) == u"11" else (u"c" if str(self.value2_hex_left) == u"12" else (u"d" if str(self.value2_hex_left) == u"13" else (u"e" if str(self.value2_hex_left) == u"14" else (u"f" if str(self.value2_hex_left) == u"15" else str(self.value2_hex_left)))))))
            return getattr(self, '_m_value2_hex_left_digit', None)

        @property
        def value2_hex(self):
            if hasattr(self, '_m_value2_hex'):
                return self._m_value2_hex

            self._m_value2_hex = self.value2_hex_left_digit + self.value2_hex_right_digit
            return getattr(self, '_m_value2_hex', None)

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



