# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class No44(KaitaiStruct):
    """:field counter: no44.type_check.counter
    :field current_plus_x: no44.type_check.current_plus_x
    :field current_plus_z: no44.type_check.current_plus_z
    :field current_plus_y: no44.type_check.current_plus_y
    :field current_minus_x: no44.type_check.current_minus_x
    :field temp_plus_y: no44.type_check.temp_plus_y
    :field temp_batt_a: no44.type_check.temp_batt_a
    :field temp_xmit_a: no44.type_check.temp_xmit_a
    :field temp_plus_z: no44.type_check.temp_plus_z
    :field temp_plus_x: no44.type_check.temp_plus_x
    :field temp_stack_a: no44.type_check.temp_stack_a
    :field current_minus_y: no44.type_check.current_minus_y
    :field current_batt_a: no44.type_check.current_batt_a
    :field a_batt_a_volt: no44.type_check.a_batt_a_volt
    :field a_batt_b_volt: no44.type_check.a_batt_b_volt
    :field power_out_a: no44.type_check.power_out_a
    :field eight_v_reg_a: no44.type_check.eight_v_reg_a
    :field current_minus_x: no44.type_check.current_minus_x
    :field current_minus_z: no44.type_check.current_minus_z
    :field current_minus_y: no44.type_check.current_minus_y
    :field current_plus_x: no44.type_check.current_plus_x
    :field temp_minus_y: no44.type_check.temp_minus_y
    :field temp_batt_b: no44.type_check.temp_batt_b
    :field temp_xmit_b: no44.type_check.temp_xmit_b
    :field temp_minus_z: no44.type_check.temp_minus_z
    :field temp_minus_x: no44.type_check.temp_minus_x
    :field temp_stack_b: no44.type_check.temp_stack_b
    :field current_plus_y: no44.type_check.current_plus_y
    :field current_batt_b: no44.type_check.current_batt_b
    :field b_batt_a_volt: no44.type_check.b_batt_a_volt
    :field b_batt_b_volt: no44.type_check.b_batt_b_volt
    :field power_out_b: no44.type_check.power_out_b
    :field eight_v_reg_b: no44.type_check.eight_v_reg_b
    :field monitor: no44.type_check.monitor
    :field dest_callsign: no44.type_check.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: no44.type_check.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: no44.type_check.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: no44.type_check.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: no44.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: no44.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: no44.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field ctl: no44.type_check.ax25_frame.ax25_header.ctl
    :field pid: no44.type_check.ax25_frame.payload.pid
    :field monitor: no44.type_check.ax25_frame.payload.ax25_info.data_monitor
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.no44 = No44.No44T(self._io, self, self._root)

    class No44T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 2925953672:
                self.type_check = No44.SideA(self._io, self, self._root)
            elif _on == 2693179010:
                self.type_check = No44.SideB(self._io, self, self._root)
            else:
                self.type_check = No44.Aprs(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(7)
            self._m_check = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class SideA(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_0 = self._io.read_u8be()
            if not  ((self.header_0 == 9550589474490835118)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_0, self._io, u"/types/side_a/seq/0")
            self.header_1 = self._io.read_u8be()
            if not  ((self.header_1 == 7386616552107452046)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_1, self._io, u"/types/side_a/seq/1")
            self.header_2 = self._io.read_u8be()
            if not  ((self.header_2 == 9414927030128210004)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_2, self._io, u"/types/side_a/seq/2")
            self.header_3 = self._io.read_u1()
            if not  ((self.header_3 == 35)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_3, self._io, u"/types/side_a/seq/3")
            self.counter = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_1 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_2 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_3 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_4 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.five_v_reference = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.ones = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.cycle_count = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.last_number = (self._io.read_bytes_term(13, False, True, True)).decode(u"ASCII")

        @property
        def current_minus_x(self):
            if hasattr(self, '_m_current_minus_x'):
                return self._m_current_minus_x

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_minus_x = (((0.0024 * (int(self.value_4) * int(self.value_4))) + (0.414 * int(self.value_4))) - 25.3)

            return getattr(self, '_m_current_minus_x', None)

        @property
        def a_batt_a_volt(self):
            if hasattr(self, '_m_a_batt_a_volt'):
                return self._m_a_batt_a_volt

            if (self.cycle_count)[2:4] == u"11":
                self._m_a_batt_a_volt = (0.0984 * int(self.value_1))

            return getattr(self, '_m_a_batt_a_volt', None)

        @property
        def current_plus_y(self):
            if hasattr(self, '_m_current_plus_y'):
                return self._m_current_plus_y

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_plus_y = (((0.0031 * (int(self.value_3) * int(self.value_3))) + (0.241 * int(self.value_3))) - 25.3)

            return getattr(self, '_m_current_plus_y', None)

        @property
        def current_plus_z(self):
            if hasattr(self, '_m_current_plus_z'):
                return self._m_current_plus_z

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_plus_z = (((0.0048 * (int(self.value_2) * int(self.value_2))) + (0.75 * int(self.value_2))) - 54.6)

            return getattr(self, '_m_current_plus_z', None)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor

            self._m_monitor = u"T#" + self.counter + u"," + self.value_1 + u"," + self.value_2 + u"," + self.value_3 + u"," + self.value_4 + u"," + self.five_v_reference + u"," + self.ones + u"," + self.cycle_count + u"," + self.last_number
            return getattr(self, '_m_monitor', None)

        @property
        def power_out_a(self):
            if hasattr(self, '_m_power_out_a'):
                return self._m_power_out_a

            if (self.cycle_count)[2:4] == u"11":
                self._m_power_out_a = (0.0311 * int(self.value_3))

            return getattr(self, '_m_power_out_a', None)

        @property
        def temp_plus_z(self):
            if hasattr(self, '_m_temp_plus_z'):
                return self._m_temp_plus_z

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_plus_z = ((0.3414 * int(self.value_4)) - 19.71)

            return getattr(self, '_m_temp_plus_z', None)

        @property
        def temp_xmit_a(self):
            if hasattr(self, '_m_temp_xmit_a'):
                return self._m_temp_xmit_a

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_xmit_a = ((0.3414 * int(self.value_3)) - 19.71)

            return getattr(self, '_m_temp_xmit_a', None)

        @property
        def temp_stack_a(self):
            if hasattr(self, '_m_temp_stack_a'):
                return self._m_temp_stack_a

            if (self.cycle_count)[2:4] == u"10":
                self._m_temp_stack_a = ((0.3414 * int(self.value_2)) - 19.71)

            return getattr(self, '_m_temp_stack_a', None)

        @property
        def temp_plus_y(self):
            if hasattr(self, '_m_temp_plus_y'):
                return self._m_temp_plus_y

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_plus_y = ((0.3414 * int(self.value_1)) - 19.71)

            return getattr(self, '_m_temp_plus_y', None)

        @property
        def current_batt_a(self):
            if hasattr(self, '_m_current_batt_a'):
                return self._m_current_batt_a

            if (self.cycle_count)[2:4] == u"10":
                self._m_current_batt_a = ((((-0.00004 * ((int(self.value_4) * int(self.value_4)) * int(self.value_4))) + (0.0114 * (int(self.value_4) * int(self.value_4)))) - (2.56 * int(self.value_4))) + 252)

            return getattr(self, '_m_current_batt_a', None)

        @property
        def eight_v_reg_a(self):
            if hasattr(self, '_m_eight_v_reg_a'):
                return self._m_eight_v_reg_a

            if (self.cycle_count)[2:4] == u"11":
                self._m_eight_v_reg_a = (0.0356 * int(self.value_4))

            return getattr(self, '_m_eight_v_reg_a', None)

        @property
        def current_minus_y(self):
            if hasattr(self, '_m_current_minus_y'):
                return self._m_current_minus_y

            if (self.cycle_count)[2:4] == u"10":
                self._m_current_minus_y = (((0.0037 * (int(self.value_3) * int(self.value_3))) + (0.0264 * int(self.value_3))) - 18.5)

            return getattr(self, '_m_current_minus_y', None)

        @property
        def a_batt_b_volt(self):
            if hasattr(self, '_m_a_batt_b_volt'):
                return self._m_a_batt_b_volt

            if (self.cycle_count)[2:4] == u"11":
                self._m_a_batt_b_volt = (0.09826 * int(self.value_2))

            return getattr(self, '_m_a_batt_b_volt', None)

        @property
        def temp_batt_a(self):
            if hasattr(self, '_m_temp_batt_a'):
                return self._m_temp_batt_a

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_batt_a = ((0.3414 * int(self.value_2)) - 19.71)

            return getattr(self, '_m_temp_batt_a', None)

        @property
        def temp_plus_x(self):
            if hasattr(self, '_m_temp_plus_x'):
                return self._m_temp_plus_x

            if (self.cycle_count)[2:4] == u"10":
                self._m_temp_plus_x = ((0.3414 * int(self.value_1)) - 19.71)

            return getattr(self, '_m_temp_plus_x', None)

        @property
        def current_plus_x(self):
            if hasattr(self, '_m_current_plus_x'):
                return self._m_current_plus_x

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_plus_x = (((0.0012 * (int(self.value_1) * int(self.value_1))) + (0.646 * int(self.value_1))) - 25.96)

            return getattr(self, '_m_current_plus_x', None)


    class SideB(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header_0 = self._io.read_u8be()
            if not  ((self.header_0 == 9550589474490835104)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_0, self._io, u"/types/side_b/seq/0")
            self.header_1 = self._io.read_u8be()
            if not  ((self.header_1 == 9702586106363946638)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_1, self._io, u"/types/side_b/seq/1")
            self.header_2 = self._io.read_u8be()
            if not  ((self.header_2 == 9414927030128210004)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_2, self._io, u"/types/side_b/seq/2")
            self.header_3 = self._io.read_u1()
            if not  ((self.header_3 == 35)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header_3, self._io, u"/types/side_b/seq/3")
            self.counter = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_1 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_2 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_3 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.value_4 = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.five_v_reference = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.ones = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.cycle_count = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.last_number = (self._io.read_bytes_term(13, False, True, True)).decode(u"ASCII")

        @property
        def current_minus_x(self):
            if hasattr(self, '_m_current_minus_x'):
                return self._m_current_minus_x

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_minus_x = (((0.0034 * (int(self.value_1) * int(self.value_1))) + (0.2284 * int(self.value_1))) - 26.6)

            return getattr(self, '_m_current_minus_x', None)

        @property
        def b_batt_a_volt(self):
            if hasattr(self, '_m_b_batt_a_volt'):
                return self._m_b_batt_a_volt

            if (self.cycle_count)[2:4] == u"11":
                self._m_b_batt_a_volt = (0.09774 * int(self.value_1))

            return getattr(self, '_m_b_batt_a_volt', None)

        @property
        def current_plus_y(self):
            if hasattr(self, '_m_current_plus_y'):
                return self._m_current_plus_y

            if (self.cycle_count)[2:4] == u"10":
                self._m_current_plus_y = (((0.0038 * (int(self.value_3) * int(self.value_3))) + (0.0084 * int(self.value_3))) - 19.8)

            return getattr(self, '_m_current_plus_y', None)

        @property
        def temp_stack_b(self):
            if hasattr(self, '_m_temp_stack_b'):
                return self._m_temp_stack_b

            if (self.cycle_count)[2:4] == u"10":
                self._m_temp_stack_b = ((0.3414 * int(self.value_2)) - 19.71)

            return getattr(self, '_m_temp_stack_b', None)

        @property
        def current_minus_z(self):
            if hasattr(self, '_m_current_minus_z'):
                return self._m_current_minus_z

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_minus_z = (((0.0096 * (int(self.value_2) * int(self.value_2))) + (0.864 * int(self.value_2))) - 53.8)

            return getattr(self, '_m_current_minus_z', None)

        @property
        def temp_minus_x(self):
            if hasattr(self, '_m_temp_minus_x'):
                return self._m_temp_minus_x

            if (self.cycle_count)[2:4] == u"10":
                self._m_temp_minus_x = ((0.3414 * int(self.value_1)) - 19.71)

            return getattr(self, '_m_temp_minus_x', None)

        @property
        def b_batt_b_volt(self):
            if hasattr(self, '_m_b_batt_b_volt'):
                return self._m_b_batt_b_volt

            if (self.cycle_count)[2:4] == u"11":
                self._m_b_batt_b_volt = (0.09457 * int(self.value_2))

            return getattr(self, '_m_b_batt_b_volt', None)

        @property
        def power_out_b(self):
            if hasattr(self, '_m_power_out_b'):
                return self._m_power_out_b

            if (self.cycle_count)[2:4] == u"11":
                self._m_power_out_b = (0.0223 * int(self.value_3))

            return getattr(self, '_m_power_out_b', None)

        @property
        def temp_batt_b(self):
            if hasattr(self, '_m_temp_batt_b'):
                return self._m_temp_batt_b

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_batt_b = ((0.3414 * int(self.value_2)) - 19.71)

            return getattr(self, '_m_temp_batt_b', None)

        @property
        def temp_minus_z(self):
            if hasattr(self, '_m_temp_minus_z'):
                return self._m_temp_minus_z

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_minus_z = ((0.3414 * int(self.value_4)) - 19.71)

            return getattr(self, '_m_temp_minus_z', None)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor

            self._m_monitor = u"T#" + self.counter + u"," + self.value_1 + u"," + self.value_2 + u"," + self.value_3 + u"," + self.value_4 + u"," + self.five_v_reference + u"," + self.ones + u"," + self.cycle_count + u"," + self.last_number
            return getattr(self, '_m_monitor', None)

        @property
        def temp_xmit_b(self):
            if hasattr(self, '_m_temp_xmit_b'):
                return self._m_temp_xmit_b

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_xmit_b = ((0.3414 * int(self.value_3)) - 19.71)

            return getattr(self, '_m_temp_xmit_b', None)

        @property
        def current_minus_y(self):
            if hasattr(self, '_m_current_minus_y'):
                return self._m_current_minus_y

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_minus_y = (((0.0023 * (int(self.value_3) * int(self.value_3))) + (0.473 * int(self.value_3))) - 23.2)

            return getattr(self, '_m_current_minus_y', None)

        @property
        def eight_v_reg_b(self):
            if hasattr(self, '_m_eight_v_reg_b'):
                return self._m_eight_v_reg_b

            if (self.cycle_count)[2:4] == u"11":
                self._m_eight_v_reg_b = (0.0351 * int(self.value_4))

            return getattr(self, '_m_eight_v_reg_b', None)

        @property
        def current_plus_x(self):
            if hasattr(self, '_m_current_plus_x'):
                return self._m_current_plus_x

            if (self.cycle_count)[2:4] == u"00":
                self._m_current_plus_x = (((0.003 * (int(self.value_4) * int(self.value_4))) + (0.4 * int(self.value_4))) - 26.6)

            return getattr(self, '_m_current_plus_x', None)

        @property
        def current_batt_b(self):
            if hasattr(self, '_m_current_batt_b'):
                return self._m_current_batt_b

            if (self.cycle_count)[2:4] == u"10":
                self._m_current_batt_b = ((((-0.00004 * ((int(self.value_4) * int(self.value_4)) * int(self.value_4))) + (0.0158 * (int(self.value_4) * int(self.value_4)))) - (3.32 * int(self.value_4))) + 259)

            return getattr(self, '_m_current_batt_b', None)

        @property
        def temp_minus_y(self):
            if hasattr(self, '_m_temp_minus_y'):
                return self._m_temp_minus_y

            if (self.cycle_count)[2:4] == u"01":
                self._m_temp_minus_y = ((0.3414 * int(self.value_1)) - 19.71)

            return getattr(self, '_m_temp_minus_y', None)


    class Aprs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = No44.Aprs.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = No44.Aprs.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = No44.Aprs.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = No44.Aprs.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = No44.Aprs.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = No44.Aprs.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = No44.Aprs.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = No44.Aprs.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = No44.Aprs.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = No44.Aprs.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = No44.Aprs.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = No44.Aprs.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = No44.Aprs.Repeater(self._io, self, self._root)

                self.ctl = self._io.read_u1()


        class UiFrame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.pid = self._io.read_u1()
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = No44.Aprs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


        class Callsign(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


        class IFrame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.pid = self._io.read_u1()
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = No44.Aprs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


        class SsidMask(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ssid_mask = self._io.read_u1()

            @property
            def ssid(self):
                if hasattr(self, '_m_ssid'):
                    return self._m_ssid

                self._m_ssid = ((self.ssid_mask & 31) >> 1)
                return getattr(self, '_m_ssid', None)

            @property
            def hbit(self):
                if hasattr(self, '_m_hbit'):
                    return self._m_hbit

                self._m_hbit = ((self.ssid_mask & 128) >> 7)
                return getattr(self, '_m_hbit', None)


        class Repeaters(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rpt_callsign_raw = No44.Aprs.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = No44.Aprs.SsidMask(self._io, self, self._root)


        class Repeater(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rpt_instance = []
                i = 0
                while True:
                    _ = No44.Aprs.Repeaters(self._io, self, self._root)
                    self.rpt_instance.append(_)
                    if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                        break
                    i += 1


        class CallsignRaw(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self._raw__raw_callsign_ror = self._io.read_bytes(6)
                self._raw_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_callsign_ror, 8 - (1), 1)
                _io__raw_callsign_ror = KaitaiStream(BytesIO(self._raw_callsign_ror))
                self.callsign_ror = No44.Aprs.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_monitor = (self._io.read_bytes_full()).decode(u"utf-8")




