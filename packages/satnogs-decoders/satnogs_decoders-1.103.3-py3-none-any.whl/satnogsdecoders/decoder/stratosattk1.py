# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Stratosattk1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.ax25_header.pid
    :field obc_timestamp: ax25_frame.payload.obc_timestamp
    :field eps_cell_current: ax25_frame.payload.eps_cell_current
    :field eps_system_current: ax25_frame.payload.eps_system_current
    :field eps_cell_voltage_half: ax25_frame.payload.eps_cell_voltage_half
    :field eps_cell_voltage_full: ax25_frame.payload.eps_cell_voltage_full
    :field eps_integral_cell_current: ax25_frame.payload.eps_integral_cell_current
    :field eps_integral_system_current: ax25_frame.payload.eps_integral_system_current
    :field adc_temperature_pos_x: ax25_frame.payload.adc_temperature_pos_x
    :field adc_temperature_neg_x: ax25_frame.payload.adc_temperature_neg_x
    :field adc_temperature_pos_y: ax25_frame.payload.adc_temperature_pos_y
    :field adc_temperature_neg_y: ax25_frame.payload.adc_temperature_neg_y
    :field adc_temperature_pos_z: ax25_frame.payload.adc_temperature_pos_z
    :field adc_temperature_neg_z: ax25_frame.payload.adc_temperature_neg_z
    :field adc_temperature_cell1: ax25_frame.payload.adc_temperature_cell1
    :field adc_temperature_cell2: ax25_frame.payload.adc_temperature_cell2
    :field attitude_control: ax25_frame.payload.attitude_control
    :field obc_cpu_load: ax25_frame.payload.obc_cpu_load
    :field obc_boot_count: ax25_frame.payload.obc_boot_count
    :field comm_boot_count: ax25_frame.payload.comm_boot_count
    :field comm_rssi: ax25_frame.payload.comm_rssi
    :field comm_received_packets: ax25_frame.payload.comm_received_packets
    :field comm_sent_packets: ax25_frame.payload.comm_sent_packets
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Stratosattk1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Stratosattk1.Ax25Header(self._io, self, self._root)
            self.payload = Stratosattk1.StratosatBeaconTlm(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Stratosattk1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Stratosattk1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Stratosattk1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Stratosattk1.SsidMask(self._io, self, self._root)
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
            if not  ((self.callsign == u"BEACON") or (self.callsign == u"RS52S ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class StratosatBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc_timestamp = self._io.read_u4le()
            self.eps_cell_current = self._io.read_u2le()
            self.eps_system_current = self._io.read_u2le()
            self.eps_cell_voltage_half = self._io.read_u2le()
            self.eps_cell_voltage_full = self._io.read_u2le()
            self.eps_integral_cell_current = self._io.read_u4le()
            self.eps_integral_system_current = self._io.read_u4le()
            self.adc_temperature_pos_x = self._io.read_s1()
            self.adc_temperature_neg_x = self._io.read_s1()
            self.adc_temperature_pos_y = self._io.read_s1()
            self.adc_temperature_neg_y = self._io.read_s1()
            self.adc_temperature_pos_z = self._io.read_s1()
            self.adc_temperature_neg_z = self._io.read_s1()
            self.adc_temperature_cell1 = self._io.read_s1()
            self.adc_temperature_cell2 = self._io.read_s1()
            self.attitude_control = self._io.read_u1()
            self.obc_cpu_load = self._io.read_u1()
            self.obc_boot_count = self._io.read_u2le()
            self.comm_boot_count = self._io.read_u2le()
            self.comm_rssi = self._io.read_s1()
            self.comm_received_packets = self._io.read_u2le()
            self.comm_sent_packets = self._io.read_u2le()


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
            self.callsign_ror = Stratosattk1.Callsign(_io__raw_callsign_ror, self, self._root)



