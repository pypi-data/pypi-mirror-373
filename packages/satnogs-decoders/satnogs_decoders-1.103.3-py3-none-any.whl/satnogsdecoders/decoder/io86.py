# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Io86(KaitaiStruct):
    """:field telemetry_beacon: io86.type_check.ax25_frame.payload.ax25_info.telemetry_beacon
    :field counter: io86.type_check.ax25_frame.payload.ax25_info.counter
    :field analog1: io86.type_check.ax25_frame.payload.ax25_info.analog1
    :field analog2: io86.type_check.ax25_frame.payload.ax25_info.analog2
    :field analog3: io86.type_check.ax25_frame.payload.ax25_info.analog3
    :field analog4: io86.type_check.ax25_frame.payload.ax25_info.analog4
    :field analog5: io86.type_check.ax25_frame.payload.ax25_info.analog5
    :field digital1: io86.type_check.ax25_frame.payload.ax25_info.digital1
    :field digital2: io86.type_check.ax25_frame.payload.ax25_info.digital2
    :field digital3: io86.type_check.ax25_frame.payload.ax25_info.digital3
    :field digital4: io86.type_check.ax25_frame.payload.ax25_info.digital4
    :field digital5: io86.type_check.ax25_frame.payload.ax25_info.digital5
    :field digital6: io86.type_check.ax25_frame.payload.ax25_info.digital6
    :field digital7: io86.type_check.ax25_frame.payload.ax25_info.digital7
    :field digital8: io86.type_check.ax25_frame.payload.ax25_info.digital8
    :field dest_callsign: io86.type_check.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: io86.type_check.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: io86.type_check.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: io86.type_check.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: io86.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: io86.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: io86.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field ctl: io86.type_check.ax25_frame.ax25_header.ctl
    :field pid: io86.type_check.ax25_frame.payload.pid
    :field monitor: io86.type_check.ax25_frame.payload.ax25_info.data_monitor
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.io86 = Io86.Io86T(self._io, self, self._root)

    class Io86T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 21539:
                self.type_check = Io86.Telemetry(self._io, self, self._root)
            else:
                self.type_check = Io86.Digi(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(23)
            self._m_check = self._io.read_u2be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class Telemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Io86.Telemetry.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Io86.Telemetry.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = Io86.Telemetry.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Io86.Telemetry.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = Io86.Telemetry.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = Io86.Telemetry.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = Io86.Telemetry.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = Io86.Telemetry.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Io86.Telemetry.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Io86.Telemetry.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Io86.Telemetry.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Io86.Telemetry.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Io86.Telemetry.Repeater(self._io, self, self._root)

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
                self.ax25_info = Io86.Telemetry.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.ax25_info = Io86.Telemetry.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.rpt_callsign_raw = Io86.Telemetry.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Io86.Telemetry.SsidMask(self._io, self, self._root)


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
                    _ = Io86.Telemetry.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Io86.Telemetry.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.telemetry = (self._io.read_bytes(2)).decode(u"ASCII")
                if not self.telemetry == u"T#":
                    raise kaitaistruct.ValidationNotEqualError(u"T#", self.telemetry, self._io, u"/types/telemetry/types/ax25_info_data/seq/0")
                self.counter_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.analog1_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.analog2_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.analog3_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.analog4_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.analog5_ascii = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
                self.digital1_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital2_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital3_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital4_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital5_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital6_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital7_ascii = (self._io.read_bytes(1)).decode(u"ASCII")
                self.digital8_ascii = (self._io.read_bytes(1)).decode(u"ASCII")

            @property
            def digital4(self):
                if hasattr(self, '_m_digital4'):
                    return self._m_digital4

                self._m_digital4 = int(self.digital4_ascii)
                return getattr(self, '_m_digital4', None)

            @property
            def counter(self):
                if hasattr(self, '_m_counter'):
                    return self._m_counter

                self._m_counter = int(self.counter_ascii)
                return getattr(self, '_m_counter', None)

            @property
            def analog4(self):
                if hasattr(self, '_m_analog4'):
                    return self._m_analog4

                self._m_analog4 = int(self.analog4_ascii)
                return getattr(self, '_m_analog4', None)

            @property
            def analog1(self):
                if hasattr(self, '_m_analog1'):
                    return self._m_analog1

                self._m_analog1 = int(self.analog1_ascii)
                return getattr(self, '_m_analog1', None)

            @property
            def digital5(self):
                if hasattr(self, '_m_digital5'):
                    return self._m_digital5

                self._m_digital5 = int(self.digital5_ascii)
                return getattr(self, '_m_digital5', None)

            @property
            def digital3(self):
                if hasattr(self, '_m_digital3'):
                    return self._m_digital3

                self._m_digital3 = int(self.digital3_ascii)
                return getattr(self, '_m_digital3', None)

            @property
            def digital6(self):
                if hasattr(self, '_m_digital6'):
                    return self._m_digital6

                self._m_digital6 = int(self.digital6_ascii)
                return getattr(self, '_m_digital6', None)

            @property
            def telemetry_beacon(self):
                if hasattr(self, '_m_telemetry_beacon'):
                    return self._m_telemetry_beacon

                self._m_telemetry_beacon = self.telemetry + self.counter_ascii + u"," + self.analog1_ascii + u"," + self.analog2_ascii + u"," + self.analog3_ascii + u"," + self.analog4_ascii + u"," + self.analog5_ascii + u"," + self.digital1_ascii + self.digital1_ascii + self.digital3_ascii + self.digital4_ascii + self.digital5_ascii + self.digital6_ascii + self.digital7_ascii + self.digital8_ascii
                return getattr(self, '_m_telemetry_beacon', None)

            @property
            def digital2(self):
                if hasattr(self, '_m_digital2'):
                    return self._m_digital2

                self._m_digital2 = int(self.digital2_ascii)
                return getattr(self, '_m_digital2', None)

            @property
            def digital1(self):
                if hasattr(self, '_m_digital1'):
                    return self._m_digital1

                self._m_digital1 = int(self.digital1_ascii)
                return getattr(self, '_m_digital1', None)

            @property
            def analog3(self):
                if hasattr(self, '_m_analog3'):
                    return self._m_analog3

                self._m_analog3 = int(self.analog3_ascii)
                return getattr(self, '_m_analog3', None)

            @property
            def digital8(self):
                if hasattr(self, '_m_digital8'):
                    return self._m_digital8

                self._m_digital8 = int(self.digital8_ascii)
                return getattr(self, '_m_digital8', None)

            @property
            def analog5(self):
                if hasattr(self, '_m_analog5'):
                    return self._m_analog5

                self._m_analog5 = int(self.analog5_ascii)
                return getattr(self, '_m_analog5', None)

            @property
            def digital7(self):
                if hasattr(self, '_m_digital7'):
                    return self._m_digital7

                self._m_digital7 = int(self.digital7_ascii)
                return getattr(self, '_m_digital7', None)

            @property
            def analog2(self):
                if hasattr(self, '_m_analog2'):
                    return self._m_analog2

                self._m_analog2 = int(self.analog2_ascii)
                return getattr(self, '_m_analog2', None)



    class Digi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Io86.Digi.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Io86.Digi.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = Io86.Digi.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Io86.Digi.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = Io86.Digi.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = Io86.Digi.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = Io86.Digi.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = Io86.Digi.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Io86.Digi.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Io86.Digi.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Io86.Digi.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Io86.Digi.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Io86.Digi.Repeater(self._io, self, self._root)

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
                self.ax25_info = Io86.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.ax25_info = Io86.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.rpt_callsign_raw = Io86.Digi.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Io86.Digi.SsidMask(self._io, self, self._root)


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
                    _ = Io86.Digi.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Io86.Digi.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_monitor = (self._io.read_bytes_full()).decode(u"utf-8")




