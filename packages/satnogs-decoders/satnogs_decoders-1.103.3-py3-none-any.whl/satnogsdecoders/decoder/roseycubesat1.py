# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Roseycubesat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field payload_size: ax25_frame.payload.ax25_info.payload_size
    :field payload_to: ax25_frame.payload.ax25_info.payload_to
    :field packet_id: ax25_frame.payload.ax25_info.packet_id
    :field text: ax25_frame.payload.ax25_info.payload.text
    :field timeStamp: ax25_frame.payload.ax25_info.payload.time
    :field bat_v: ax25_frame.payload.ax25_info.payload.bat_v
    :field bat_c: ax25_frame.payload.ax25_info.payload.bat_c
    :field temperature: ax25_frame.payload.ax25_info.payload.temperature
    :field mode: ax25_frame.payload.ax25_info.payload.mode
    :field eps_boot_counter: ax25_frame.payload.ax25_info.payload.eps_boot_counter
    :field command_counter: ax25_frame.payload.ax25_info.payload.command_counter
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Roseycubesat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Roseycubesat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Roseycubesat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Roseycubesat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Roseycubesat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Roseycubesat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Roseycubesat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Roseycubesat1.IFrame(self._io, self, self._root)


    class PeriodicMsg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.text = (KaitaiStream.bytes_terminate(self._io.read_bytes(30), 0, False)).decode(u"UTF-8")
            self.time = self._io.read_u4le()
            self.bat_v = self._io.read_u2le()
            self.bat_c = self._io.read_s2le()
            self.temperature = self._io.read_s2le()
            self.mode = self._io.read_u1()
            self.eps_boot_counter = self._io.read_u2le()
            self.command_counter = self._io.read_u2le()


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Roseycubesat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Roseycubesat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Roseycubesat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Roseycubesat1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self.pid
            if _on == 240:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Roseycubesat1.Frame(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


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
            self.ax25_info = self._io.read_bytes_full()


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.payload_size = self._io.read_u1()
            self.payload_to = self._io.read_u1()
            self.packet_id = self._io.read_u2le()
            _on = self.packet_id
            if _on == 65535:
                self.payload = Roseycubesat1.PeriodicMsg(self._io, self, self._root)


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
            self.callsign_ror = Roseycubesat1.Callsign(_io__raw_callsign_ror, self, self._root)



