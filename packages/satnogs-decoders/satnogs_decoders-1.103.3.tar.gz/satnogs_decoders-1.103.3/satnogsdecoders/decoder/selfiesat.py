# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Selfiesat(KaitaiStruct):
    """:field crc: csp_header.crc
    :field rdp: csp_header.rdp
    :field xtea: csp_header.xtea
    :field hmac: csp_header.hmac
    :field reserved: csp_header.reserved
    :field src_port: csp_header.src_port
    :field dst_port: csp_header.dst_port
    :field destination: csp_header.destination
    :field source: csp_header.source
    :field priority: csp_header.priority
    :field packet_length: csp_data.packet_length
    :field alarm_mask: csp_data.csp_payload.alarm_mask
    :field eps_counter_boot: csp_data.csp_payload.eps_counter_boot
    :field eps_vbatt: csp_data.csp_payload.eps_vbatt
    :field eps_outputmask: csp_data.csp_payload.eps_outputmask
    :field id: csp_data.csp_payload.id
    :field fsm_states: csp_data.csp_payload.fsm_states
    :field callsign: csp_data.csp_payload.callsign
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.csp_header = Selfiesat.CspHeaderT(self._io, self, self._root)
        self.csp_data = Selfiesat.CspDataT(self._io, self, self._root)

    class CspHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_flags = []
            for i in range(4):
                self.csp_flags.append(self._io.read_u1())


        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source

            self._m_source = ((self.csp_flags[3] >> 1) & 31)
            return getattr(self, '_m_source', None)

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp

            self._m_rdp = ((self.csp_flags[0] >> 1) & 1)
            return getattr(self, '_m_rdp', None)

        @property
        def src_port(self):
            if hasattr(self, '_m_src_port'):
                return self._m_src_port

            self._m_src_port = (self.csp_flags[1] & 63)
            return getattr(self, '_m_src_port', None)

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination

            self._m_destination = (((self.csp_flags[2] | (self.csp_flags[3] << 8)) >> 4) & 31)
            return getattr(self, '_m_destination', None)

        @property
        def dst_port(self):
            if hasattr(self, '_m_dst_port'):
                return self._m_dst_port

            self._m_dst_port = (((self.csp_flags[1] | (self.csp_flags[2] << 8)) >> 6) & 63)
            return getattr(self, '_m_dst_port', None)

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority

            self._m_priority = (self.csp_flags[3] >> 6)
            return getattr(self, '_m_priority', None)

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved

            self._m_reserved = (self.csp_flags[0] >> 4)
            return getattr(self, '_m_reserved', None)

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea

            self._m_xtea = ((self.csp_flags[0] >> 2) & 1)
            return getattr(self, '_m_xtea', None)

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac

            self._m_hmac = ((self.csp_flags[0] >> 3) & 1)
            return getattr(self, '_m_hmac', None)

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc

            self._m_crc = (self.csp_flags[0] & 1)
            return getattr(self, '_m_crc', None)


    class CspDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_length = self._io.read_u2be()
            if not  ((self.packet_length == 224)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.packet_length, self._io, u"/types/csp_data_t/seq/0")
            self.pad_0 = self._io.read_bytes(8)
            self._raw_csp_payload = self._io.read_bytes_full()
            _io__raw_csp_payload = KaitaiStream(BytesIO(self._raw_csp_payload))
            self.csp_payload = Selfiesat.SelfiesatTelemetryT(_io__raw_csp_payload, self, self._root)


    class SelfiesatTelemetryT(KaitaiStruct):
        """struct bcn_normal {
          unsigned int alarm_mask;            // Alarms from housekeeping
          unsigned short eps_counter_boot;    // EPS boot count
          unsigned short eps_vbatt;           // Voltage of EPS battery
          unsigned char eps_outputmask;       // Whether channels are on or off
          unsigned char id;                   // Identifier for beacons
          unsigned char fsm_states;           // obc_main's internal fsm states
        };
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.alarm_mask = self._io.read_u4be()
            self.eps_counter_boot = self._io.read_u2be()
            self.eps_vbatt = self._io.read_u2be()
            self.eps_outputmask = self._io.read_u1()
            self.id = self._io.read_u1()
            self.fsm_states = self._io.read_u1()
            self.pad_1 = self._io.read_bytes(1)
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(9), 0, False)).decode(u"ASCII")
            if not  ((self.callsign == u"SelfieSat")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/selfiesat_telemetry_t/seq/7")



