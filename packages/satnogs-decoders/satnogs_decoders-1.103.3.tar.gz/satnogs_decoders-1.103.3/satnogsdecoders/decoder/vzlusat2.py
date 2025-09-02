# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Vzlusat2(KaitaiStruct):
    """:field csp_hdr_crc: csp_header.crc
    :field csp_hdr_rdp: csp_header.rdp
    :field csp_hdr_xtea: csp_header.xtea
    :field csp_hdr_hmac: csp_header.hmac
    :field csp_hdr_src_port: csp_header.source_port
    :field csp_hdr_dst_port: csp_header.destination_port
    :field csp_hdr_destination: csp_header.destination
    :field csp_hdr_source: csp_header.source
    :field csp_hdr_priority: csp_header.priority
    :field obc_timestamp: csp_data.payload.obc_timestamp
    :field obc_boot_count: csp_data.payload.obc_boot_count
    :field obc_reset_cause: csp_data.payload.obc_reset_cause
    :field eps_vbatt: csp_data.payload.eps_vbatt
    :field eps_cursun: csp_data.payload.eps_cursun
    :field eps_cursys: csp_data.payload.eps_cursys
    :field eps_temp_bat: csp_data.payload.eps_temp_bat
    :field radio_temp_pa: csp_data.payload.radio_temp_pa
    :field radio_tot_tx_count: csp_data.payload.radio_tot_tx_count
    :field radio_tot_rx_count: csp_data.payload.radio_tot_rx_count
    :field flag: csp_data.payload.flag
    :field chunk: csp_data.payload.chunk
    :field time: csp_data.payload.time
    :field data: csp_data.payload.data_raw.data.data_str
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.csp_header = Vzlusat2.CspHeaderT(self._io, self, self._root)
        self.csp_data = Vzlusat2.CspDataT(self._io, self, self._root)

    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header_raw = self._io.read_u4be()

        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source

            self._m_source = ((self.csp_header_raw >> 25) & 31)
            return getattr(self, '_m_source', None)

        @property
        def source_port(self):
            if hasattr(self, '_m_source_port'):
                return self._m_source_port

            self._m_source_port = ((self.csp_header_raw >> 8) & 63)
            return getattr(self, '_m_source_port', None)

        @property
        def destination_port(self):
            if hasattr(self, '_m_destination_port'):
                return self._m_destination_port

            self._m_destination_port = ((self.csp_header_raw >> 14) & 63)
            return getattr(self, '_m_destination_port', None)

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp

            self._m_rdp = ((self.csp_header_raw & 2) >> 1)
            return getattr(self, '_m_rdp', None)

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination

            self._m_destination = ((self.csp_header_raw >> 20) & 31)
            return getattr(self, '_m_destination', None)

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority

            self._m_priority = (self.csp_header_raw >> 30)
            return getattr(self, '_m_priority', None)

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved

            self._m_reserved = ((self.csp_header_raw >> 4) & 15)
            return getattr(self, '_m_reserved', None)

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea

            self._m_xtea = ((self.csp_header_raw & 4) >> 2)
            return getattr(self, '_m_xtea', None)

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac

            self._m_hmac = ((self.csp_header_raw & 8) >> 3)
            return getattr(self, '_m_hmac', None)

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc

            self._m_crc = (self.csp_header_raw & 1)
            return getattr(self, '_m_crc', None)


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd = self._io.read_u1()
            if  ((self._parent.csp_header.source == 1) and (self._parent.csp_header.destination == 26) and (self._parent.csp_header.source_port == 18) and (self._parent.csp_header.destination_port == 18)) :
                _on = self.cmd
                if _on == 86:
                    self.payload = Vzlusat2.Vzlusat2BeaconT(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Vzlusat2.Vzlusat2DropT(self._io, self, self._root)



    class Vzlusat2BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = self._io.read_bytes(8)
            if not self.callsign == b"\x5A\x4C\x55\x53\x41\x54\x2D\x32":
                raise kaitaistruct.ValidationNotEqualError(b"\x5A\x4C\x55\x53\x41\x54\x2D\x32", self.callsign, self._io, u"/types/vzlusat2_beacon_t/seq/0")
            self.obc_timestamp = self._io.read_u4be()
            self.obc_boot_count = self._io.read_u4be()
            self.obc_reset_cause = self._io.read_u4be()
            self.eps_vbatt = self._io.read_u2be()
            self.eps_cursun = self._io.read_u2be()
            self.eps_cursys = self._io.read_u2be()
            self.eps_temp_bat = self._io.read_s2be()
            self.radio_temp_pa_raw = self._io.read_s2be()
            self.radio_tot_tx_count = self._io.read_u4be()
            self.radio_tot_rx_count = self._io.read_u4be()

        @property
        def radio_temp_pa(self):
            if hasattr(self, '_m_radio_temp_pa'):
                return self._m_radio_temp_pa

            self._m_radio_temp_pa = (0.1 * self.radio_temp_pa_raw)
            return getattr(self, '_m_radio_temp_pa', None)


    class Vzlusat2DropT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flag = self._io.read_u1()
            self.chunk = self._io.read_u4be()
            self.time = self._io.read_u4be()
            self._raw_data_raw = self._io.read_bytes_full()
            _io__raw_data_raw = KaitaiStream(BytesIO(self._raw_data_raw))
            self.data_raw = Vzlusat2.Vzlusat2DropT.DataB64(_io__raw_data_raw, self, self._root)

        class DataB64(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self._raw__raw_data = self._io.read_bytes_full()
                _process = satnogsdecoders.process.B64encode()
                self._raw_data = _process.decode(self._raw__raw_data)
                _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
                self.data = Vzlusat2.Vzlusat2DropT.StrB64(_io__raw_data, self, self._root)


        class StrB64(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_str = (self._io.read_bytes_full()).decode(u"ASCII")




