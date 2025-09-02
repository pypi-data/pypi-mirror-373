# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Casaasat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field frame_id: ax25_frame.ax25_info.frame_id
    :field checksum: ax25_frame.ax25_info.checksum
    :field tm_code: ax25_frame.ax25_info.tm_code
    :field count: ax25_frame.ax25_info.count
    :field values___date: ax25_frame.ax25_info.values.___.type_check.date
    :field values___dosim_x1: ax25_frame.ax25_info.values.___.type_check.dosim_x1
    :field values___dosim_x2: ax25_frame.ax25_info.values.___.type_check.dosim_x2
    :field values___dosim_z1: ax25_frame.ax25_info.values.___.type_check.dosim_z1
    :field values___dosim_z2: ax25_frame.ax25_info.values.___.type_check.dosim_z2
    :field values___dosim_y1: ax25_frame.ax25_info.values.___.type_check.dosim_y1
    :field values___dosim_y2: ax25_frame.ax25_info.values.___.type_check.dosim_y2
    :field values___field_plus_y: ax25_frame.ax25_info.values.___.type_check.field_plus_y
    :field values___field_plus_x: ax25_frame.ax25_info.values.___.type_check.field_plus_x
    :field values___field_minus_z: ax25_frame.ax25_info.values.___.type_check.field_minus_z
    :field values___raw_minus_y: ax25_frame.ax25_info.values.___.type_check.raw_minus_y
    :field values___raw_minus_x: ax25_frame.ax25_info.values.___.type_check.raw_minus_x
    :field values___raw_minus_z: ax25_frame.ax25_info.values.___.type_check.raw_minus_z
    :field values___gain: ax25_frame.ax25_info.values.___.type_check.gain
    
    .. seealso::
       Source - https://site.amsat-f.org/download/120557/?tmstv=1735221517
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Casaasat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Casaasat.Ax25Header(self._io, self, self._root)
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Casaasat.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Casaasat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Casaasat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Casaasat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Casaasat.SsidMask(self._io, self, self._root)
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

            self._m_ssid = ((self.ssid_mask & 31) >> 1)
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
            self.callsign_ror = Casaasat.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.frame_id = self._io.read_u2be()
            self.checksum = self._io.read_u4be()
            self.tm_code = self._io.read_u1()
            if not  ((self.tm_code == 138) or (self.tm_code == 139)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.tm_code, self._io, u"/types/ax25_info_data/seq/2")
            self.count = self._io.read_u1()
            self.values = []
            for i in range(self.count):
                self.values.append(Casaasat.Ax25InfoData.ValuesT(self._io, self, self._root))


        class ValuesT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                _on = self.tm_code_switch
                if _on == 138:
                    self.type_check = Casaasat.Ax25InfoData.Dosimeter(self._io, self, self._root)
                elif _on == 139:
                    self.type_check = Casaasat.Ax25InfoData.MagneticField(self._io, self, self._root)

            @property
            def tm_code_switch(self):
                if hasattr(self, '_m_tm_code_switch'):
                    return self._m_tm_code_switch

                _pos = self._io.pos()
                self._io.seek(6)
                self._m_tm_code_switch = self._io.read_u1()
                self._io.seek(_pos)
                return getattr(self, '_m_tm_code_switch', None)


        class Dosimeter(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.date = self._io.read_u4be()
                self.dosim_x1 = self._io.read_u2be()
                self.dosim_x2 = self._io.read_u2be()
                self.dosim_z1 = self._io.read_u2be()
                self.dosim_z2 = self._io.read_u2be()
                self.dosim_y1 = self._io.read_u2be()
                self.dosim_y2 = self._io.read_u2be()


        class MagneticField(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.date = self._io.read_u4be()
                self.field_plus_y = self._io.read_u4be()
                self.field_plus_x = self._io.read_u4be()
                self.field_minus_z = self._io.read_u4be()
                self.raw_minus_y = self._io.read_u2be()
                self.raw_minus_x = self._io.read_u2be()
                self.raw_minus_z = self._io.read_u2be()
                self.gain = self._io.read_u1()




