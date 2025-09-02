# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Kashiwa(KaitaiStruct):
    """:field batt_v: kashiwa.type_check.batt_v
    :field batt_i: kashiwa.type_check.batt_i
    :field batt_t: kashiwa.type_check.batt_t
    :field bpb_t: kashiwa.type_check.bpb_t
    :field raw_i: kashiwa.type_check.raw_i
    :field lcl_5v0: kashiwa.type_check.lcl_5v0
    :field lcl_depand: kashiwa.type_check.lcl_depand
    :field lcl_compic: kashiwa.type_check.lcl_compic
    :field sap_minus_x: kashiwa.type_check.sap_minus_x
    :field sap_plus_y: kashiwa.type_check.sap_plus_y
    :field sap_minus_y: kashiwa.type_check.sap_minus_y
    :field sap_plus_z: kashiwa.type_check.sap_plus_z
    :field sap_minus_z: kashiwa.type_check.sap_minus_z
    :field sap_minus_z: kashiwa.type_check.sap_minus_z
    :field reserve: kashiwa.type_check.reserve
    :field reserve_cmd_counter: kashiwa.type_check.reserve_cmd_counter
    :field gmsk_cmd_counter: kashiwa.type_check.gmsk_cmd_counter
    :field kill_counter: kashiwa.type_check.kill_counter
    :field kill_sw: kashiwa.type_check.kill_sw
    :field boss_on_off: kashiwa.type_check.boss_on_off
    :field ack_mis_end: kashiwa.type_check.ack_mis_end
    :field ack_mis_error: kashiwa.type_check.ack_mis_error
    :field ack_mis_mog: kashiwa.type_check.ack_mis_mog
    :field mis_iss: kashiwa.type_check.mis_iss
    :field beacon_field: kashiwa.type_check.beacon_field
    :field dest_callsign: kashiwa.type_check.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: kashiwa.type_check.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: kashiwa.type_check.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: kashiwa.type_check.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: kashiwa.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: kashiwa.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: kashiwa.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field ctl: kashiwa.type_check.ax25_frame.ax25_header.ctl
    :field pid: kashiwa.type_check.ax25_frame.payload.pid
    :field monitor: kashiwa.type_check.ax25_frame.payload.ax25_info.data_monitor
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.kashiwa = Kashiwa.KashiwaT(self._io, self, self._root)

    class KashiwaT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 5355678641493134145:
                self.type_check = Kashiwa.Cw(self._io, self, self._root)
            elif _on == 7670528987939498849:
                self.type_check = Kashiwa.Cw(self._io, self, self._root)
            elif _on == 5352306439146123338:
                self.type_check = Kashiwa.SpecialBeacon(self._io, self, self._root)
            else:
                self.type_check = Kashiwa.Aprs(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_check = self._io.read_u8be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class Cw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_and_satellite_name = (self._io.read_bytes(13)).decode(u"ASCII")
            if not  ((self.callsign_and_satellite_name == u"JS1YMXKASHIWA") or (self.callsign_and_satellite_name == u"js1ymxkashiwa")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign_and_satellite_name, self._io, u"/types/cw/seq/0")
            self.batt_v = self._io.read_u1()
            self.batt_i = self._io.read_u1()
            self.batt_t = self._io.read_u1()
            self.bpb_t = self._io.read_u1()
            self.raw_i = self._io.read_u1()
            self.lcl_5v0 = self._io.read_bits_int_be(1) != 0
            self.lcl_depand = self._io.read_bits_int_be(1) != 0
            self.lcl_compic = self._io.read_bits_int_be(1) != 0
            self.sap_minus_x = self._io.read_bits_int_be(1) != 0
            self.sap_plus_y = self._io.read_bits_int_be(1) != 0
            self.sap_minus_y = self._io.read_bits_int_be(1) != 0
            self.sap_plus_z = self._io.read_bits_int_be(1) != 0
            self.sap_minus_z = self._io.read_bits_int_be(1) != 0
            self.reserve = self._io.read_bits_int_be(1) != 0
            self.reserve_cmd_counter = self._io.read_bits_int_be(4)
            self.gmsk_cmd_counter = self._io.read_bits_int_be(3)
            self.kill_counter = self._io.read_bits_int_be(2)
            self.kill_sw = self._io.read_bits_int_be(1) != 0
            self.boss_on_off = self._io.read_bits_int_be(1) != 0
            self.ack_mis_end = self._io.read_bits_int_be(1) != 0
            self.ack_mis_error = self._io.read_bits_int_be(1) != 0
            self.ack_mis_mog = self._io.read_bits_int_be(1) != 0
            self.mis_iss = self._io.read_bits_int_be(1) != 0


    class SpecialBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_source_callsign = (self._io.read_bytes(14)).decode(u"ASCII")
            if not  ((self.dest_source_callsign == u"JG6YBW0JG6YMX0")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.dest_source_callsign, self._io, u"/types/special_beacon/seq/0")
            self.ctl_pid = self._io.read_u2be()
            self.beacon_field = (self._io.read_bytes_full()).decode(u"UTF-16BE")


    class Aprs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Kashiwa.Aprs.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Kashiwa.Aprs.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = Kashiwa.Aprs.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Kashiwa.Aprs.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = Kashiwa.Aprs.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = Kashiwa.Aprs.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = Kashiwa.Aprs.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = Kashiwa.Aprs.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Kashiwa.Aprs.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Kashiwa.Aprs.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Kashiwa.Aprs.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Kashiwa.Aprs.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Kashiwa.Aprs.Repeater(self._io, self, self._root)

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
                self.ax25_info = Kashiwa.Aprs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.ax25_info = Kashiwa.Aprs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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

                self._m_ssid = ((self.ssid_mask & 15) >> 1)
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
                self.rpt_callsign_raw = Kashiwa.Aprs.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Kashiwa.Aprs.SsidMask(self._io, self, self._root)


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
                    _ = Kashiwa.Aprs.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Kashiwa.Aprs.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_monitor = (self._io.read_bytes_full()).decode(u"utf-8")




