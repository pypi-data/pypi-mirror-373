# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Connectat11(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.ax25_header.pid
    :field beacon_id: ax25_frame.beacon.beacon_header.beacon_id
    :field rx_packet_cnt: ax25_frame.beacon.beacon_data.rx_packet_cnt
    :field tmtc_temperature1: ax25_frame.beacon.beacon_data.tmtc_temperature1
    :field tmtc_temperature2: ax25_frame.beacon.beacon_data.tmtc_temperature2
    :field mppt_converter_voltage_1: ax25_frame.beacon.beacon_data.mppt_converter_voltage_1
    :field mppt_converter_voltage_2: ax25_frame.beacon.beacon_data.mppt_converter_voltage_2
    :field mppt_converter_voltage_3: ax25_frame.beacon.beacon_data.mppt_converter_voltage_3
    :field mppt_converter_voltage_4: ax25_frame.beacon.beacon_data.mppt_converter_voltage_4
    :field panel1_current: ax25_frame.beacon.beacon_data.panel1_current
    :field panel3_current: ax25_frame.beacon.beacon_data.panel3_current
    :field panel2_current: ax25_frame.beacon.beacon_data.panel2_current
    :field panel5_current: ax25_frame.beacon.beacon_data.panel5_current
    :field panel6_current: ax25_frame.beacon.beacon_data.panel6_current
    :field panel4_current: ax25_frame.beacon.beacon_data.panel4_current
    :field vbat: ax25_frame.beacon.beacon_data.vbat
    :field eps_temperature1: ax25_frame.beacon.beacon_header.eps_temperature1
    :field eps_temperature2: ax25_frame.beacon.beacon_header.eps_temperature2
    :field eps_temperature3: ax25_frame.beacon.beacon_header.eps_temperature3
    :field eps_temperature4: ax25_frame.beacon.beacon_header.eps_temperature4
    :field obc_unix_time: ax25_frame.beacon.beacon_header.obc_unix_time
    :field obc_boot_time: ax25_frame.beacon.beacon_header.obc_boot_time
    :field obc_boot_count: ax25_frame.beacon.beacon_header.obc_boot_count
    :field panel1_temperature: ax25_frame.beacon.beacon_header.panel1_temperature
    :field panel2_temperature: ax25_frame.beacon.beacon_header.panel2_temperature
    :field panel3_temperature: ax25_frame.beacon.beacon_header.panel3_temperature
    :field panel4_temperature: ax25_frame.beacon.beacon_header.panel4_temperature
    :field panel5_temperature: ax25_frame.beacon.beacon_header.panel5_temperature
    :field panel6_temperature: ax25_frame.beacon.beacon_header.panel6_temperature
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Connectat11.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Connectat11.Ax25Header(self._io, self, self._root)
            self.beacon = Connectat11.BeaconT(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Connectat11.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Connectat11.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Connectat11.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Connectat11.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"utf-8")
            if not  ((self.callsign == u"CONT11") or (self.callsign == u"PLANS1")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class BeaconHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_preamble = self._io.read_u4le()
            self.beacon_preamble1 = self._io.read_u1()
            self.beacon_id = self._io.read_u1()
            self.beacon_padding = self._io.read_u8le()
            self.beacon_padding1 = self._io.read_u2le()


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_header = Connectat11.BeaconHeaderT(self._io, self, self._root)
            if self.beacon_header.beacon_id == 3:
                self.beacon_data = Connectat11.BeaconDataT(self._io, self, self._root)



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


    class BeaconDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rx_packet_cnt = self._io.read_u2le()
            self.data0001 = self._io.read_u2le()
            self.tmtc_temperature1 = self._io.read_s1()
            self.tmtc_temperature2 = self._io.read_s1()
            self.data0002 = self._io.read_u8le()
            self.data0003 = self._io.read_u4le()
            self.data0004 = self._io.read_u4le()
            self.data0005 = self._io.read_u4le()
            self.data0006 = self._io.read_u4le()
            self.data0007 = self._io.read_u4le()
            self.mppt_converter_voltage_1 = self._io.read_u2le()
            self.mppt_converter_voltage_2 = self._io.read_u2le()
            self.mppt_converter_voltage_3 = self._io.read_u2le()
            self.mppt_converter_voltage_4 = self._io.read_u2le()
            self.panel1_current = self._io.read_u2le()
            self.panel3_current = self._io.read_u2le()
            self.panel2_current = self._io.read_u2le()
            self.panel5_current = self._io.read_u2le()
            self.panel6_current = self._io.read_u2le()
            self.panel4_current = self._io.read_u2le()
            self.vbat = self._io.read_u2le()
            self.data0008 = self._io.read_u8le()
            self.data0008a = self._io.read_u8le()
            self.data0008b = self._io.read_u8le()
            self.data0008c = self._io.read_u8le()
            self.data0008d = self._io.read_u8le()
            self.eps_temperature1 = self._io.read_s1()
            self.eps_temperature2 = self._io.read_s1()
            self.eps_temperature3 = self._io.read_s1()
            self.eps_temperature4 = self._io.read_s1()
            self.data0009 = self._io.read_u1()
            self.obc_unix_time = self._io.read_u4le()
            self.obc_boot_time = self._io.read_u4le()
            self.obc_boot_count = self._io.read_u4le()
            self.data0010 = self._io.read_u8le()
            self.data0010a = self._io.read_u8le()
            self.data0010b = self._io.read_u1()
            self.panel1_temperature = self._io.read_s1()
            self.panel2_temperature = self._io.read_s1()
            self.panel3_temperature = self._io.read_s1()
            self.panel4_temperature = self._io.read_s1()
            self.panel5_temperature = self._io.read_s1()
            self.panel6_temperature = self._io.read_s1()
            self.data_0011 = self._io.read_u8le()
            self.data_0011a = self._io.read_u8le()
            self.data_0011b = self._io.read_u8le()
            self.data_0011c = self._io.read_u8le()
            self.data_0011d = self._io.read_u8le()
            self.data_0011e = self._io.read_u8le()
            self.data_0011f = self._io.read_u8le()
            self.data_0011g = self._io.read_u8le()
            self.data_0011h = self._io.read_u8le()
            self.data_0011i = self._io.read_u8le()
            self.data_0011j = self._io.read_u8le()
            self.data_0011k = self._io.read_u4le()


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
            self.callsign_ror = Connectat11.Callsign(_io__raw_callsign_ror, self, self._root)



