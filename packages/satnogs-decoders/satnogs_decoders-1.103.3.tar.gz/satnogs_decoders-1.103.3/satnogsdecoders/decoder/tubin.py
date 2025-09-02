# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Tubin(KaitaiStruct):
    """:field msgtype: mf.msgtype
    :field block_length: mf.block_length
    :field target_address: mf.target_address
    :field target_sub_address: mf.target_sub_address
    :field ack_flag: mf.ack_flag
    :field baudrate_flag: mf.baudrate_flag
    :field callsign: mf.callsign
    :field callsign_crc: mf.callsign_crc
    :field scid: mf.tf.scid
    :field version: mf.tf.version
    :field counter: mf.tf.counter
    
    :field spcrc: mf.tf.sp.spcrc
    :field gs_quality_byte: mf.gs_quality_byte
    :field gs_error_marker: mf.gs_error_marker
    :field gs_tnc_temperature: mf.gs_tnc_temperature
    
    .. seealso::
       'https://www.tu.berlin/en/raumfahrttechnik/institute/amateur-radio'
       'https://www.static.tu.berlin/fileadmin/www/10002275/Amateur_Radio/TechnoSat_Telemetry_Format.ods'
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.mf = Tubin.MasterFrame(self._io, self, self._root)

    class SourcePacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length_msb = self._io.read_u1()
            if self.length_msb != 255:
                self.length_lsb = self._io.read_u1()

            if self.length_msb == 255:
                self.padding = self._io.read_bytes_full()

            if self.length_msb != 255:
                self.vcid = self._io.read_bits_int_be(4)

            if self.length_msb != 255:
                self.rtfrac = self._io.read_bits_int_be(4)

            self._io.align_to_byte()
            if self.length_msb != 255:
                self.rtsec = self._io.read_u4be()

            if self.length_msb != 255:
                self.nodid = self._io.read_u1()

            if self.length_msb != 255:
                self.spid = self._io.read_u1()

            if self.length_msb != 255:
                _on = self.spid
                if _on == 131:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpTmAocsStateEstimationA(_io__raw_user_data, self, self._root)
                elif _on == 60:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpStdTmAocs(_io__raw_user_data, self, self._root)
                elif _on == 249:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpType249(_io__raw_user_data, self, self._root)
                elif _on == 21:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpType21(_io__raw_user_data, self, self._root)
                elif _on == 41:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpType41(_io__raw_user_data, self, self._root)
                elif _on == 16:
                    self._raw_user_data = self._io.read_bytes(self.splen)
                    _io__raw_user_data = KaitaiStream(BytesIO(self._raw_user_data))
                    self.user_data = Tubin.SpType16(_io__raw_user_data, self, self._root)
                else:
                    self.user_data = self._io.read_bytes(self.splen)

            if self.length_msb != 255:
                self.spcrc = self._io.read_u2be()


        @property
        def splen(self):
            if hasattr(self, '_m_splen'):
                return self._m_splen

            if self.length_msb != 255:
                self._m_splen = ((self.length_msb << 8) | (self.length_lsb if self.length_msb != 255 else 0))

            return getattr(self, '_m_splen', None)


    class SpType249(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(3)


    class SpType16(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(16)


    class SpType21(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(28)


    class SpStdTmAocs(KaitaiStruct):
        """Type 60
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.nodeno = self._io.read_bits_int_be(1) != 0
            self.rst_en = self._io.read_bits_int_be(1) != 0
            self.botslt = self._io.read_bits_int_be(3)
            self.synpps = self._io.read_bits_int_be(1) != 0
            self.disutc = self._io.read_bits_int_be(1) != 0
            self.dulbsy = self._io.read_bits_int_be(1) != 0
            self.acs_mode = self._io.read_bits_int_be(5)
            self.mfs_received = self._io.read_bits_int_be(1) != 0
            self.sss_received = self._io.read_bits_int_be(1) != 0
            self.gyr_received = self._io.read_bits_int_be(1) != 0
            self.for_received = self._io.read_bits_int_be(1) != 0
            self.str_received = self._io.read_bits_int_be(1) != 0
            self.res_1_bit = self._io.read_bits_int_be(1) != 0
            self.mts_received = self._io.read_bits_int_be(1) != 0
            self.rw0_received = self._io.read_bits_int_be(1) != 0
            self.rw1_received = self._io.read_bits_int_be(1) != 0
            self.rw2_received = self._io.read_bits_int_be(1) != 0
            self.rw3_received = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.std_q_s = self._io.read_s2be()
            self.std_q_x = self._io.read_s2be()
            self.std_q_y = self._io.read_s2be()
            self.std_q_z = self._io.read_s2be()
            self.std_rate_x = self._io.read_s1()
            self.std_rate_y = self._io.read_s1()
            self.std_rate_z = self._io.read_s1()
            self.std_r_x = self._io.read_s1()
            self.std_r_y = self._io.read_s1()
            self.std_r_z = self._io.read_s1()


    class SpTmAocsStateEstimationA(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.esta_q_s = self._io.read_s4be()
            self.esta_q_x = self._io.read_s4be()
            self.esta_q_y = self._io.read_s4be()
            self.esta_q_z = self._io.read_s4be()
            self.esta_rate_x = self._io.read_s2be()
            self.esta_rate_y = self._io.read_s2be()
            self.esta_rate_z = self._io.read_s2be()
            self.esta_acc_x = self._io.read_s2be()
            self.esta_acc_y = self._io.read_s2be()
            self.esta_acc_z = self._io.read_s2be()
            self.esta_b_sat_x = self._io.read_s2be()
            self.esta_b_sat_y = self._io.read_s2be()
            self.esta_b_sat_z = self._io.read_s2be()
            self.esta_s_sat_x = self._io.read_s2be()
            self.esta_s_sat_y = self._io.read_s2be()
            self.esta_s_sat_z = self._io.read_s2be()
            self.esta_b_tod_x = self._io.read_s2be()
            self.esta_b_tod_y = self._io.read_s2be()
            self.esta_b_tod_z = self._io.read_s2be()
            self.esta_s_tod_x = self._io.read_s2be()
            self.esta_s_tod_y = self._io.read_s2be()
            self.esta_s_tod_z = self._io.read_s2be()
            self.esta_r_x = self._io.read_s2be()
            self.esta_r_y = self._io.read_s2be()
            self.esta_r_z = self._io.read_s2be()
            self.esta_v_x = self._io.read_s2be()
            self.esta_v_y = self._io.read_s2be()
            self.esta_v_z = self._io.read_s2be()
            self.esta_occultatio = self._io.read_u1()


    class MasterFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.msgtype = self._io.read_bits_int_be(3)
            self.block_length = self._io.read_bits_int_be(5)
            self.target_address = self._io.read_bits_int_be(4)
            self.target_sub_address = self._io.read_bits_int_be(2)
            self.ack_flag = self._io.read_bits_int_be(1) != 0
            self.baudrate_flag = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(6), 0, False)).decode(u"ascii")
            if not self.callsign == u"DP0TBN":
                raise kaitaistruct.ValidationNotEqualError(u"DP0TBN", self.callsign, self._io, u"/types/master_frame/seq/6")
            self.callsign_crc = self._io.read_u2be()
            self._raw_tf = self._io.read_bytes(((self.block_length + 1) * 18))
            _io__raw_tf = KaitaiStream(BytesIO(self._raw_tf))
            self.tf = Tubin.TransferFrame(_io__raw_tf, self, self._root)
            self.gs_quality_byte = self._io.read_u1()
            self.gs_error_marker = self._io.read_u4be()
            self.gs_tnc_temperature = self._io.read_u1()


    class TransferFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.scid = self._io.read_bits_int_be(12)
            self.version = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.counter = self._io.read_u2be()
            self.sp = []
            i = 0
            while True:
                _ = Tubin.SourcePacket(self._io, self, self._root)
                self.sp.append(_)
                if  ((self._io.pos() >= self._io.size()) or (_.length_msb == 255)) :
                    break
                i += 1
            self.tfpad = self._io.read_bytes_full()


    class SpType41(KaitaiStruct):
        """Standard AOCS data
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(7)



