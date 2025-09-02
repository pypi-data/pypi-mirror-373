# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aisat(KaitaiStruct):
    """:field callsign: callsign
    :field beacon_type: beacon_types.check
    :field volts: beacon_types.type_check.volts
    :field dbm: beacon_types.type_check.dbm
    :field pa: beacon_types.type_check.pa
    :field pcb: beacon_types.type_check.pcb
    :field beacon: beacon_types.type_check.beacon
    
    .. seealso::
       
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
        if not self.callsign == u"dp0ais":
            raise kaitaistruct.ValidationNotEqualError(u"dp0ais", self.callsign, self._io, u"/seq/0")
        self.beacon_types = Aisat.BeaconTypesT(self._io, self, self._root)

    class Pa(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pa = self._io.read_s1()

        @property
        def beacon(self):
            if hasattr(self, '_m_beacon'):
                return self._m_beacon

            self._m_beacon = u"PA " + str(self.pa) + u" C"
            return getattr(self, '_m_beacon', None)


    class Dbm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dbm = self._io.read_u1()

        @property
        def beacon(self):
            if hasattr(self, '_m_beacon'):
                return self._m_beacon

            self._m_beacon = str((-1 * self.dbm)) + u" dBm"
            return getattr(self, '_m_beacon', None)


    class BeaconTypesT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 1:
                self.type_check = Aisat.Volts(self._io, self, self._root)
            elif _on == 2:
                self.type_check = Aisat.Dbm(self._io, self, self._root)
            elif _on == 3:
                self.type_check = Aisat.Pa(self._io, self, self._root)
            elif _on == 4:
                self.type_check = Aisat.Pcb(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            self._m_check = self._io.read_u1()
            return getattr(self, '_m_check', None)


    class Pcb(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pcb = self._io.read_s1()

        @property
        def beacon(self):
            if hasattr(self, '_m_beacon'):
                return self._m_beacon

            self._m_beacon = u"PCB " + str(self.pcb) + u" C"
            return getattr(self, '_m_beacon', None)


    class Volts(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.volts = self._io.read_u2be()

        @property
        def beacon(self):
            if hasattr(self, '_m_beacon'):
                return self._m_beacon

            self._m_beacon = (str(self.volts))[0:1] + u"." + (str(self.volts))[1:3] + u" V"
            return getattr(self, '_m_beacon', None)



