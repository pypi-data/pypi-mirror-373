# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sputnixusp(KaitaiStruct):
    """:field callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid_raw_ssid_mask: ax25_frame.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.ax25_header.pid
    :field packet_type: ax25_frame.payload.packet_type
    :field skip1: ax25_frame.payload.tlm.skip1
    :field skip2: ax25_frame.payload.tlm.skip2
    :field skip3: ax25_frame.payload.tlm.skip3
    :field usb1: ax25_frame.payload.tlm.usb1
    :field usb2: ax25_frame.payload.tlm.usb2
    :field usb3: ax25_frame.payload.tlm.usb3
    :field isb1: ax25_frame.payload.tlm.isb1
    :field isb2: ax25_frame.payload.tlm.isb2
    :field isb3: ax25_frame.payload.tlm.isb3
    :field iab: ax25_frame.payload.tlm.iab
    :field ich1: ax25_frame.payload.tlm.ich1
    :field ich2: ax25_frame.payload.tlm.ich2
    :field ich3: ax25_frame.payload.tlm.ich3
    :field ich4: ax25_frame.payload.tlm.ich4
    :field t1_pw: ax25_frame.payload.tlm.t1_pw
    :field t2_pw: ax25_frame.payload.tlm.t2_pw
    :field t3_pw: ax25_frame.payload.tlm.t3_pw
    :field t4_pw: ax25_frame.payload.tlm.t4_pw
    :field flags1: ax25_frame.payload.tlm.flags1
    :field flags2: ax25_frame.payload.tlm.flags2
    :field flags3: ax25_frame.payload.tlm.flags3
    :field reserved1: ax25_frame.payload.tlm.reserved1
    :field uab: ax25_frame.payload.tlm.uab
    :field reg_tel_id: ax25_frame.payload.tlm.reg_tel_id
    :field time: ax25_frame.payload.tlm.time
    :field nres_ps: ax25_frame.payload.tlm.nres_ps
    :field fl_ps: ax25_frame.payload.tlm.fl_ps
    :field t_amp: ax25_frame.payload.tlm.t_amp
    :field t_uhf: ax25_frame.payload.tlm.t_uhf
    :field rssi_rx: ax25_frame.payload.tlm.rssi_rx
    :field pf: ax25_frame.payload.tlm.pf
    :field pb: ax25_frame.payload.tlm.pb
    :field nres_uhf: ax25_frame.payload.tlm.nres_uhf
    :field fl_uhf: ax25_frame.payload.tlm.fl_uhf
    :field time_uhf: ax25_frame.payload.tlm.time_uhf
    :field uptime_uhf: ax25_frame.payload.tlm.uptime_uhf
    :field current_uhf: ax25_frame.payload.tlm.current_uhf
    :field uuhf: ax25_frame.payload.tlm.uuhf
    :field t_mb: ax25_frame.payload.tlm.t_mb
    :field mx: ax25_frame.payload.tlm.mx
    :field my: ax25_frame.payload.tlm.my
    :field mz: ax25_frame.payload.tlm.mz
    :field vx: ax25_frame.payload.tlm.vx
    :field vy: ax25_frame.payload.tlm.vy
    :field vz: ax25_frame.payload.tlm.vz
    :field nres_ext: ax25_frame.payload.tlm.nres_ext
    :field rcon: ax25_frame.payload.tlm.rcon
    :field fl_ext: ax25_frame.payload.tlm.fl_ext
    :field time_ext: ax25_frame.payload.tlm.time_ext
    :field fl_payload: ax25_frame.payload.tlm.fl_payload
    :field time_send: ax25_frame.payload.tlm.time_send
    :field t_plate: ax25_frame.payload.tlm.t_plate
    :field t_cpu: ax25_frame.payload.tlm.t_cpu
    :field cursens1: ax25_frame.payload.tlm.cursens1
    :field cursens2: ax25_frame.payload.tlm.cursens2
    :field nrst: ax25_frame.payload.tlm.nrst
    :field time_rst: ax25_frame.payload.tlm.time_rst
    :field ch1rate: ax25_frame.payload.tlm.ch1rate
    :field ch2rate: ax25_frame.payload.tlm.ch2rate
    :field ch3rate: ax25_frame.payload.tlm.ch3rate
    :field ch4rate: ax25_frame.payload.tlm.ch4rate
    :field ch5rate: ax25_frame.payload.tlm.ch5rate
    :field ch6rate: ax25_frame.payload.tlm.ch6rate
    :field ptrend1: ax25_frame.payload.tlm.ptrend1
    :field ptrctl1: ax25_frame.payload.tlm.ptrctl1
    :field ptrend2: ax25_frame.payload.tlm.ptrend2
    :field ptrctl2: ax25_frame.payload.tlm.ptrctl2
    :field ptrend3: ax25_frame.payload.tlm.ptrend3
    :field ptrctl3: ax25_frame.payload.tlm.ptrctl3
    :field lastevent_ch1_1: ax25_frame.payload.tlm.lastevent_ch1_1
    :field lastevent_ch1_2: ax25_frame.payload.tlm.lastevent_ch1_2
    :field lastevent_ch1_3: ax25_frame.payload.tlm.lastevent_ch1_3
    :field lastevent_ch2_1: ax25_frame.payload.tlm.lastevent_ch2_1
    :field lastevent_ch2_2: ax25_frame.payload.tlm.lastevent_ch2_2
    :field lastevent_ch2_3: ax25_frame.payload.tlm.lastevent_ch2_3
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Sputnixusp.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Sputnixusp.Ax25Header(self._io, self, self._root)
            self.payload = Sputnixusp.BeaconTlm(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Sputnixusp.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Sputnixusp.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Sputnixusp.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Sputnixusp.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class ExtendedTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.t_mb = self._io.read_u2le()
            self.mx = self._io.read_u4le()
            self.my = self._io.read_u4le()
            self.mz = self._io.read_u4le()
            self.vx = self._io.read_u4le()
            self.vy = self._io.read_u4le()
            self.vz = self._io.read_u4le()
            self.nres_ext = self._io.read_u1()
            self.rcon = self._io.read_u1()
            self.fl_ext = self._io.read_u1()
            self.time_ext = self._io.read_u4le()
            self.fl_payload = self._io.read_u1()
            self.time_send = self._io.read_u4le()
            self.t_plate = self._io.read_u2le()
            self.t_cpu = self._io.read_u2le()
            self.cursens1 = self._io.read_u2le()
            self.cursens2 = self._io.read_u2le()
            self.nrst = self._io.read_u1()
            self.time_rst = self._io.read_u4le()
            self.ch1rate = self._io.read_u2le()
            self.ch2rate = self._io.read_u2le()
            self.ch3rate = self._io.read_u2le()
            self.ch4rate = self._io.read_u2le()
            self.ch5rate = self._io.read_u2le()
            self.ch6rate = self._io.read_u2le()
            self.ptrend1 = self._io.read_u2le()
            self.ptrctl1 = self._io.read_u2le()
            self.ptrend2 = self._io.read_u2le()
            self.ptrctl2 = self._io.read_u2le()
            self.ptrend3 = self._io.read_u2le()
            self.ptrctl3 = self._io.read_u2le()
            self.lastevent_ch1_1 = self._io.read_u1()
            self.lastevent_ch1_2 = self._io.read_u1()
            self.lastevent_ch1_3 = self._io.read_u1()
            self.lastevent_ch2_1 = self._io.read_u1()
            self.lastevent_ch2_2 = self._io.read_u1()
            self.lastevent_ch2_3 = self._io.read_u1()


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


    class BeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_type = self._io.read_u2le()
            _on = self.packet_type
            if _on == 16918:
                self.tlm = Sputnixusp.GeneralTlm(self._io, self, self._root)
            elif _on == 16919:
                self.tlm = Sputnixusp.ExtendedTlm(self._io, self, self._root)


    class GeneralTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.skip1 = self._io.read_u2le()
            self.skip2 = self._io.read_u2le()
            self.skip3 = self._io.read_u2le()
            self.usb1 = self._io.read_u2le()
            self.usb2 = self._io.read_u2le()
            self.usb3 = self._io.read_u2le()
            self.isb1 = self._io.read_u2le()
            self.isb2 = self._io.read_u2le()
            self.isb3 = self._io.read_u2le()
            self.iab = self._io.read_u2le()
            self.ich1 = self._io.read_u2le()
            self.ich2 = self._io.read_u2le()
            self.ich3 = self._io.read_u2le()
            self.ich4 = self._io.read_u2le()
            self.t1_pw = self._io.read_u2le()
            self.t2_pw = self._io.read_u2le()
            self.t3_pw = self._io.read_u2le()
            self.t4_pw = self._io.read_u2le()
            self.flags1 = self._io.read_u1()
            self.flags2 = self._io.read_u1()
            self.flags3 = self._io.read_u1()
            self.reserved1 = self._io.read_u1()
            self.uab = self._io.read_u2le()
            self.reg_tel_id = self._io.read_u4le()
            self.time = self._io.read_u4le()
            self.nres_ps = self._io.read_u1()
            self.fl_ps = self._io.read_u1()
            self.t_amp = self._io.read_u1()
            self.t_uhf = self._io.read_u1()
            self.rssi_rx = self._io.read_s2be()
            self.pf = self._io.read_u1()
            self.pb = self._io.read_u1()
            self.nres_uhf = self._io.read_u1()
            self.fl_uhf = self._io.read_u1()
            self.time_uhf = self._io.read_u4le()
            self.uptime_uhf = self._io.read_u4le()
            self.current_uhf = self._io.read_u2le()
            self.uuhf = self._io.read_u2le()


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
            self.callsign_ror = Sputnixusp.Callsign(_io__raw_callsign_ror, self, self._root)



