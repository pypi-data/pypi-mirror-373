# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Azaadisat2(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field call_sign: ax25_frame.payload.ax25_info.header.call_sign
    :field frame_number: ax25_frame.payload.ax25_info.header.frame_number
    :field message_type: ax25_frame.payload.ax25_info.header.message_type
    :field transmitted_on: ax25_frame.payload.ax25_info.header.transmitted_on
    :field boot_counter: ax25_frame.payload.ax25_info.data.boot_counter
    :field deployment_status: ax25_frame.payload.ax25_info.data.deployment_status
    :field arm_deployment_percentage: ax25_frame.payload.ax25_info.data.arm_deployment_percentage
    :field expansion_deployment_percentage: ax25_frame.payload.ax25_info.data.expansion_deployment_percentage
    :field obc_temperature: ax25_frame.payload.ax25_info.data.obc_temperature
    :field bus_voltage: ax25_frame.payload.ax25_info.data.bus_voltage
    :field bus_current: ax25_frame.payload.ax25_info.data.bus_current
    :field battery_temperature: ax25_frame.payload.ax25_info.data.battery_temperature
    :field radiation: ax25_frame.payload.ax25_info.data.radiation
    :field checksum: ax25_frame.payload.ax25_info.data.checksum
    :field message_slot: ax25_frame.payload.ax25_info.data.message_slot
    :field size: ax25_frame.payload.ax25_info.data.size
    :field message: ax25_frame.payload.ax25_info.data.message
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Azaadisat2.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Azaadisat2.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Azaadisat2.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Azaadisat2.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Azaadisat2.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Azaadisat2.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Azaadisat2.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Azaadisat2.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Azaadisat2.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Azaadisat2.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Azaadisat2.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Azaadisat2.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Azaadisat2.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class SfMessageT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message_slot = self._io.read_u1()
            self.size = self._io.read_u1()
            self.message = (self._io.read_bytes(self.size)).decode(u"ASCII")
            self.checksum = self._io.read_u1()


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
            self.ax25_info = Azaadisat2.PayloadT(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"SKITRC") or (self.callsign == u"AZDSAT")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class SatelliteInfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.boot_counter = self._io.read_u2le()
            self.deployment_status = self._io.read_u1()
            self.arm_deployment_percentage = self._io.read_u1()
            self.expansion_deployment_percentage = self._io.read_u1()
            self.obc_temperature = self._io.read_f4le()
            self.bus_voltage = self._io.read_f4le()
            self.bus_current = self._io.read_f4le()
            self.battery_temperature = self._io.read_f4le()
            self.radiation = self._io.read_f4le()
            self.checksum = self._io.read_u1()


    class HeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call_sign = (self._io.read_bytes(6)).decode(u"ASCII")
            self.frame_number = self._io.read_u1()
            self.message_type = self._io.read_u1()
            self.transmitted_on = self._io.read_u1()


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
            self.ax25_info = Azaadisat2.PayloadT(_io__raw_ax25_info, self, self._root)


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


    class PayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Azaadisat2.HeaderT(self._io, self, self._root)
            _on = self.header.message_type
            if _on == 1:
                self.data = Azaadisat2.SatelliteInfoT(self._io, self, self._root)
            elif _on == 2:
                self.data = Azaadisat2.SfMessageT(self._io, self, self._root)


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Azaadisat2.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Azaadisat2.SsidMask(self._io, self, self._root)


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
                _ = Azaadisat2.Repeaters(self._io, self, self._root)
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
            self.callsign_ror = Azaadisat2.Callsign(_io__raw_callsign_ror, self, self._root)



