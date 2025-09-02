# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Snet(KaitaiStruct):
    """:field fsync: pdu_header.fsync
    :field crc: pdu_header.crc
    :field fcid_major: pdu_header.fcid_major
    :field fcid_sub: pdu_header.fcid_sub
    :field urgent: pdu_header.control_1.urgent
    :field extended: pdu_header.control_1.extended
    :field crc_check: pdu_header.control_1.crc_check
    :field multi_frame: pdu_header.control_1.multi_frame
    :field time_tag_setting: pdu_header.control_1.time_tag_setting
    :field time_tagged: pdu_header.control_1.time_tagged
    :field data_length: pdu_header.data_length
    :field time_tag: pdu_header.time_tag
    :field versno: pdu_header_extension.extension.versno
    :field dfcid: pdu_header_extension.extension.dfcid
    :field rfu: pdu_header_extension.extension.rfu
    :field channel_info: pdu_header_extension.channel_info
    :field qos: pdu_header_extension.control_2.qos
    :field pdu_type_id: pdu_header_extension.control_2.pdu_type_id
    :field arq: pdu_header_extension.control_2.arq
    :field control_2_rfu: pdu_header_extension.control_2.rfu
    :field time_tag_sub: pdu_header_extension.time_tag_sub
    :field scid: pdu_header_extension.scid
    :field seqno: pdu_header_extension.seqno
    :field adcs_pget_imodechklistthisstepactive: payload.adcs_pget_imodechklistthisstepactive
    :field adcs_pget_iattdetfinalstate: payload.adcs_pget_iattdetfinalstate
    :field adcs_pget_isensorarrayavailstatusga: payload.adcs_pget_isensorarrayavailstatusga
    :field adcs_pget_isensorarrayavailstatusmfsa: payload.adcs_pget_isensorarrayavailstatusmfsa
    :field adcs_pget_isensorarrayavailstatussusea: payload.adcs_pget_isensorarrayavailstatussusea
    :field adcs_pget_iactarrayavailstatusrwa: payload.adcs_pget_iactarrayavailstatusrwa
    :field adcs_pget_iactarrayavailstatusmata: payload.adcs_pget_iactarrayavailstatusmata
    :field adcs_pget_attdetmfsdistcorrmode: payload.adcs_pget_attdetmfsdistcorrmode
    :field adcs_pget_attdetsusedistcorrmode: payload.adcs_pget_attdetsusedistcorrmode
    :field adcs_pget_attdettrackigrfdeltab: payload.adcs_pget_attdettrackigrfdeltab
    :field adcs_pget_attdetsusealbedotracking: payload.adcs_pget_attdetsusealbedotracking
    :field adcs_pget_suse1albedoflag: payload.adcs_pget_suse1albedoflag
    :field adcs_pget_suse2albedoflag: payload.adcs_pget_suse2albedoflag
    :field adcs_pget_suse3albedoflag: payload.adcs_pget_suse3albedoflag
    :field adcs_pget_suse4albedoflag: payload.adcs_pget_suse4albedoflag
    :field adcs_pget_suse5albedoflag: payload.adcs_pget_suse5albedoflag
    :field adcs_pget_suse6albedoflag: payload.adcs_pget_suse6albedoflag
    :field adcs_pget_attdetautovirtualizemfsa: payload.adcs_pget_attdetautovirtualizemfsa
    :field adcs_pget_attdetautovirtualizesusea: payload.adcs_pget_attdetautovirtualizesusea
    :field adcs_pget_attdetnarrowvectors: payload.adcs_pget_attdetnarrowvectors
    :field adcs_pget_attdetmismatchingvectors: payload.adcs_pget_attdetmismatchingvectors
    :field raw: payload.adcs_pget_omegaxoptimal_sat.raw
    :field value: payload.adcs_pget_omegaxoptimal_sat.value
    :field adcs_pget_omegayoptimal_sat_raw: payload.adcs_pget_omegayoptimal_sat.raw
    :field adcs_pget_omegayoptimal_sat_value: payload.adcs_pget_omegayoptimal_sat.value
    :field adcs_pget_omegazoptimal_sat_raw: payload.adcs_pget_omegazoptimal_sat.raw
    :field adcs_pget_omegazoptimal_sat_value: payload.adcs_pget_omegazoptimal_sat.value
    :field adcs_pget_magxoptimal_sat_raw: payload.adcs_pget_magxoptimal_sat.raw
    :field adcs_pget_magxoptimal_sat_value: payload.adcs_pget_magxoptimal_sat.value
    :field adcs_pget_magyoptimal_sat_raw: payload.adcs_pget_magyoptimal_sat.raw
    :field adcs_pget_magyoptimal_sat_value: payload.adcs_pget_magyoptimal_sat.value
    :field adcs_pget_magzoptimal_sat_raw: payload.adcs_pget_magzoptimal_sat.raw
    :field adcs_pget_magzoptimal_sat_value: payload.adcs_pget_magzoptimal_sat.value
    :field adcs_pget_sunxoptimal_sat_raw: payload.adcs_pget_sunxoptimal_sat.raw
    :field adcs_pget_sunxoptimal_sat_value: payload.adcs_pget_sunxoptimal_sat.value
    :field adcs_pget_sunyoptimal_sat_raw: payload.adcs_pget_sunyoptimal_sat.raw
    :field adcs_pget_sunyoptimal_sat_value: payload.adcs_pget_sunyoptimal_sat.value
    :field adcs_pget_sunzoptimal_sat_raw: payload.adcs_pget_sunzoptimal_sat.raw
    :field adcs_pget_sunzoptimal_sat_value: payload.adcs_pget_sunzoptimal_sat.value
    :field adcs_pget_dctrltorquerwax_sat_lr_raw: payload.adcs_pget_dctrltorquerwax_sat_lr.raw
    :field adcs_pget_dctrltorquerwax_sat_lr_value: payload.adcs_pget_dctrltorquerwax_sat_lr.value
    :field adcs_pget_dctrltorquerway_sat_lr_raw: payload.adcs_pget_dctrltorquerway_sat_lr.raw
    :field adcs_pget_dctrltorquerway_sat_lr_value: payload.adcs_pget_dctrltorquerway_sat_lr.value
    :field adcs_pget_dctrltorquerwaz_sat_lr_raw: payload.adcs_pget_dctrltorquerwaz_sat_lr.raw
    :field adcs_pget_dctrltorquerwaz_sat_lr_value: payload.adcs_pget_dctrltorquerwaz_sat_lr.value
    :field adcs_pget_dctrlmagmomentmatax_sat_lr_raw: payload.adcs_pget_dctrlmagmomentmatax_sat_lr.raw
    :field adcs_pget_dctrlmagmomentmatax_sat_lr_value: payload.adcs_pget_dctrlmagmomentmatax_sat_lr.value
    :field adcs_pget_dctrlmagmomentmatay_sat_lr_raw: payload.adcs_pget_dctrlmagmomentmatay_sat_lr.raw
    :field adcs_pget_dctrlmagmomentmatay_sat_lr_value: payload.adcs_pget_dctrlmagmomentmatay_sat_lr.value
    :field adcs_pget_dctrlmagmomentmataz_sat_lr_raw: payload.adcs_pget_dctrlmagmomentmataz_sat_lr.raw
    :field adcs_pget_dctrlmagmomentmataz_sat_lr_value: payload.adcs_pget_dctrlmagmomentmataz_sat_lr.value
    :field adcs_pget_ireadtorquerwx_mfr_raw: payload.adcs_pget_ireadtorquerwx_mfr.raw
    :field adcs_pget_ireadtorquerwx_mfr_value: payload.adcs_pget_ireadtorquerwx_mfr.value
    :field adcs_pget_ireadtorquerwy_mfr_raw: payload.adcs_pget_ireadtorquerwy_mfr.raw
    :field adcs_pget_ireadtorquerwy_mfr_value: payload.adcs_pget_ireadtorquerwy_mfr.value
    :field adcs_pget_ireadtorquerwz_mfr_raw: payload.adcs_pget_ireadtorquerwz_mfr.raw
    :field adcs_pget_ireadtorquerwz_mfr_value: payload.adcs_pget_ireadtorquerwz_mfr.value
    :field adcs_pget_ireadrotspeedrwx_mfr: payload.adcs_pget_ireadrotspeedrwx_mfr
    :field adcs_pget_ireadrotspeedrwy_mfr: payload.adcs_pget_ireadrotspeedrwy_mfr
    :field adcs_pget_ireadrotspeedrwz_mfr: payload.adcs_pget_ireadrotspeedrwz_mfr
    :field adcs_pget_sgp4latxpef_raw: payload.adcs_pget_sgp4latxpef.raw
    :field adcs_pget_sgp4latxpef_value: payload.adcs_pget_sgp4latxpef.value
    :field adcs_pget_sgp4longypef_raw: payload.adcs_pget_sgp4longypef.raw
    :field adcs_pget_sgp4longypef_value: payload.adcs_pget_sgp4longypef.value
    :field adcs_pget_sgp4altpef_raw: payload.adcs_pget_sgp4altpef.raw
    :field adcs_pget_sgp4altpef_value: payload.adcs_pget_sgp4altpef.value
    :field adcs_pget_attitudeerrorangle_raw: payload.adcs_pget_attitudeerrorangle.raw
    :field adcs_pget_attitudeerrorangle_value: payload.adcs_pget_attitudeerrorangle.value
    :field adcs_pget_targetdata_distance: payload.adcs_pget_targetdata_distance
    :field adcs_pget_targetdata_controlisactive: payload.adcs_pget_targetdata_controlisactive
    :field eps_pget_s00_cur_solx_pos_raw: payload.eps_pget_s00_cur_solx_pos.raw
    :field eps_pget_s00_cur_solx_pos_value: payload.eps_pget_s00_cur_solx_pos.value
    :field eps_pget_s01_cur_solx_neg_raw: payload.eps_pget_s01_cur_solx_neg.raw
    :field eps_pget_s01_cur_solx_neg_value: payload.eps_pget_s01_cur_solx_neg.value
    :field eps_pget_s02_cur_soly_pos_raw: payload.eps_pget_s02_cur_soly_pos.raw
    :field eps_pget_s02_cur_soly_pos_value: payload.eps_pget_s02_cur_soly_pos.value
    :field eps_pget_s03_cur_soly_neg_raw: payload.eps_pget_s03_cur_soly_neg.raw
    :field eps_pget_s03_cur_soly_neg_value: payload.eps_pget_s03_cur_soly_neg.value
    :field eps_pget_s04_cur_solz_pos_raw: payload.eps_pget_s04_cur_solz_pos.raw
    :field eps_pget_s04_cur_solz_pos_value: payload.eps_pget_s04_cur_solz_pos.value
    :field eps_pget_s05_cur_solz_neg_raw: payload.eps_pget_s05_cur_solz_neg.raw
    :field eps_pget_s05_cur_solz_neg_value: payload.eps_pget_s05_cur_solz_neg.value
    :field eps_pget_s06_v_sol: payload.eps_pget_s06_v_sol
    :field eps_pget_s24_v_bat0_raw: payload.eps_pget_s24_v_bat0.raw
    :field eps_pget_s24_v_bat0_value: payload.eps_pget_s24_v_bat0.value
    :field eps_pget_s26_a_in_charger0_raw: payload.eps_pget_s26_a_in_charger0.raw
    :field eps_pget_s26_a_in_charger0_value: payload.eps_pget_s26_a_in_charger0.value
    :field eps_pget_s25_a_out_charger0_raw: payload.eps_pget_s25_a_out_charger0.raw
    :field eps_pget_s25_a_out_charger0_value: payload.eps_pget_s25_a_out_charger0.value
    :field eps_pget_s13_v_bat1_raw: payload.eps_pget_s13_v_bat1.raw
    :field eps_pget_s13_v_bat1_value: payload.eps_pget_s13_v_bat1.value
    :field eps_pget_s23_a_in_charger1_raw: payload.eps_pget_s23_a_in_charger1.raw
    :field eps_pget_s23_a_in_charger1_value: payload.eps_pget_s23_a_in_charger1.value
    :field eps_pget_s14_a_out_charger1_raw: payload.eps_pget_s14_a_out_charger1.raw
    :field eps_pget_s14_a_out_charger1_value: payload.eps_pget_s14_a_out_charger1.value
    :field eps_pget_s22_v_sum_raw: payload.eps_pget_s22_v_sum.raw
    :field eps_pget_s22_v_sum_value: payload.eps_pget_s22_v_sum.value
    :field eps_pget_s44_v_3v3_raw: payload.eps_pget_s44_v_3v3.raw
    :field eps_pget_s44_v_3v3_value: payload.eps_pget_s44_v_3v3.value
    :field eps_pget_s45_v_5v_raw: payload.eps_pget_s45_v_5v.raw
    :field eps_pget_s45_v_5v_value: payload.eps_pget_s45_v_5v.value
    :field thm_pget_s31_th_bat0_raw: payload.thm_pget_s31_th_bat0.raw
    :field thm_pget_s31_th_bat0_value: payload.thm_pget_s31_th_bat0.value
    :field thm_pget_s15_th_bat1_raw: payload.thm_pget_s15_th_bat1.raw
    :field thm_pget_s15_th_bat1_value: payload.thm_pget_s15_th_bat1.value
    :field thm_pget_th_obc: payload.thm_pget_th_obc
    :field eps_pget_a_obc: payload.eps_pget_a_obc
    :field eps_pget_v_obc: payload.eps_pget_v_obc
    :field eps_pget_s30_a_in_bat0_raw: payload.eps_pget_s30_a_in_bat0.raw
    :field eps_pget_s30_a_in_bat0_value: payload.eps_pget_s30_a_in_bat0.value
    :field eps_pget_s29_a_out_bat0_raw: payload.eps_pget_s29_a_out_bat0.raw
    :field eps_pget_s29_a_out_bat0_value: payload.eps_pget_s29_a_out_bat0.value
    :field eps_pget_s12_a_in_bat1_raw: payload.eps_pget_s12_a_in_bat1.raw
    :field eps_pget_s12_a_in_bat1_value: payload.eps_pget_s12_a_in_bat1.value
    :field eps_pget_s20_a_out_bat1_raw: payload.eps_pget_s20_a_out_bat1.raw
    :field eps_pget_s20_a_out_bat1_value: payload.eps_pget_s20_a_out_bat1.value
    :field com0_pget_systime: payload.contents.com0_pget_systime
    :field com0_pget_memdatatype: payload.contents.com0_pget_memdatatype
    :field com0_pget_memdata32: payload.contents.com0_pget_memdata32
    :field com1_pget_systime: payload.contents.com1_pget_systime
    :field com1_pget_memdatatype: payload.contents.com1_pget_memdatatype
    :field com1_pget_memdata32: payload.contents.com1_pget_memdata32
    """

    class Versno(Enum):
        salsat = 0

    class Scid(Enum):
        snet_a = 0
        snet_b = 1
        snet_c = 2
        snet_d = 3
        salsat = 4
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.pdu_header = Snet.PduHeader(self._io, self, self._root)
        if self.pdu_header.control_1.extended:
            self.pdu_header_extension = Snet.PduHeaderExtension(self._io, self, self._root)

        _on = self.pdu_header.fcid_major
        if _on == 0:
            self.payload = Snet.AdcsStandardTelemetry(self._io, self, self._root)
        elif _on == 9:
            self.payload = Snet.EpsStandardTelemetry(self._io, self, self._root)
        elif _on == 54:
            self.payload = Snet.Fcid54(self._io, self, self._root)

    class EpsStandardTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_pget_s00_cur_solx_pos = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s01_cur_solx_neg = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s02_cur_soly_pos = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s03_cur_soly_neg = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s04_cur_solz_pos = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s05_cur_solz_neg = Snet.Solarcurrent(self._io, self, self._root)
            self.eps_pget_s06_v_sol = self._io.read_s2le()
            self.eps_pget_s24_v_bat0 = Snet.Batvoltage(self._io, self, self._root)
            self.eps_pget_s26_a_in_charger0 = Snet.Chargecurr(self._io, self, self._root)
            self.eps_pget_s25_a_out_charger0 = Snet.Outcurr(self._io, self, self._root)
            self.eps_pget_s13_v_bat1 = Snet.Batvoltage(self._io, self, self._root)
            self.eps_pget_s23_a_in_charger1 = Snet.Chargecurr(self._io, self, self._root)
            self.eps_pget_s14_a_out_charger1 = Snet.Outcurr(self._io, self, self._root)
            self.eps_pget_s22_v_sum = Snet.Batvoltage(self._io, self, self._root)
            self.eps_pget_s44_v_3v3 = Snet.V3voltage(self._io, self, self._root)
            self.eps_pget_s45_v_5v = Snet.V5voltage(self._io, self, self._root)
            self.thm_pget_s31_th_bat0 = Snet.Battemp(self._io, self, self._root)
            self.thm_pget_s15_th_bat1 = Snet.Battemp(self._io, self, self._root)
            self.thm_pget_th_obc = self._io.read_s2le()
            self.eps_pget_a_obc = self._io.read_u2le()
            self.eps_pget_v_obc = self._io.read_u2le()
            self.eps_pget_s30_a_in_bat0 = Snet.Chargecurr(self._io, self, self._root)
            self.eps_pget_s29_a_out_bat0 = Snet.Chargecurr(self._io, self, self._root)
            self.eps_pget_s12_a_in_bat1 = Snet.Chargecurr(self._io, self, self._root)
            self.eps_pget_s20_a_out_bat1 = Snet.Chargecurr(self._io, self, self._root)


    class Torquemag(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s1()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 127)
            return getattr(self, '_m_value', None)


    class Mailbox0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.com0_pget_systime = self._io.read_u4le()
            self.com0_pget_memdatatype = self._io.read_u1()
            self.com0_pget_memdata32 = self._io.read_bytes(32)


    class Battemp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 256)
            return getattr(self, '_m_value', None)


    class Torquerw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s1()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((1000000 * self.raw) / 38484)
            return getattr(self, '_m_value', None)


    class Fcid54(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.pdu_header.fcid_major
            if _on == 17:
                self.contents = Snet.Mailbox0(self._io, self, self._root)
            elif _on == 117:
                self.contents = Snet.Mailbox1(self._io, self, self._root)


    class Control1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.urgent = self._io.read_bits_int_be(1) != 0
            self.extended = self._io.read_bits_int_be(1) != 0
            self.crc_check = self._io.read_bits_int_be(1) != 0
            self.multi_frame = self._io.read_bits_int_be(1) != 0
            self.time_tag_setting = self._io.read_bits_int_be(1) != 0
            self.time_tagged = self._io.read_bits_int_be(1) != 0


    class PduHeaderExtension(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.extension = Snet.Extension(self._io, self, self._root)
            self.channel_info = self._io.read_bits_int_be(8)
            self._io.align_to_byte()
            self.control_2 = Snet.Control2(self._io, self, self._root)
            self.time_tag_sub = self._io.read_bits_int_be(16)
            self.scid = KaitaiStream.resolve_enum(Snet.Scid, self._io.read_bits_int_be(10))
            self.seqno = self._io.read_bits_int_be(14)


    class Sunvect(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 32000)
            return getattr(self, '_m_value', None)


    class V3voltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 8)
            return getattr(self, '_m_value', None)


    class Chargecurr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 12)
            return getattr(self, '_m_value', None)


    class Angularrate(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 260)
            return getattr(self, '_m_value', None)


    class Batvoltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 2)
            return getattr(self, '_m_value', None)


    class Control2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.qos = self._io.read_bits_int_be(1) != 0
            self.pdu_type_id = self._io.read_bits_int_be(1) != 0
            self.arq = self._io.read_bits_int_be(1) != 0
            self.rfu = self._io.read_bits_int_be(5)


    class Attitude(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 177)
            return getattr(self, '_m_value', None)


    class PduHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fsync = self._io.read_bits_int_be(18)
            if not self.fsync == 249152:
                raise kaitaistruct.ValidationNotEqualError(249152, self.fsync, self._io, u"/types/pdu_header/seq/0")
            self.crc = self._io.read_bits_int_be(14)
            self.fcid_major = self._io.read_bits_int_be(6)
            self.fcid_sub = self._io.read_bits_int_be(10)
            self._io.align_to_byte()
            self.control_1 = Snet.Control1(self._io, self, self._root)
            self.data_length = self._io.read_bits_int_be(10)
            self._io.align_to_byte()
            if self.control_1.time_tagged == True:
                self.time_tag = self._io.read_u4le()



    class Solarcurrent(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 50)
            return getattr(self, '_m_value', None)


    class Alt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u1()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 0.25)
            return getattr(self, '_m_value', None)


    class V5voltage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 5)
            return getattr(self, '_m_value', None)


    class Outcurr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 6)
            return getattr(self, '_m_value', None)


    class Measuredtorque(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((1000000 * self.raw) / 9696969)
            return getattr(self, '_m_value', None)


    class Lon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 177)
            return getattr(self, '_m_value', None)


    class Mailbox1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.com1_pget_systime = self._io.read_u4le()
            self.com1_pget_memdatatype = self._io.read_u1()
            self.com1_pget_memdata32 = self._io.read_bytes(32)


    class Magfield(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 0.1)
            return getattr(self, '_m_value', None)


    class Lat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2le()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (self.raw / 355)
            return getattr(self, '_m_value', None)


    class Extension(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.versno = KaitaiStream.resolve_enum(Snet.Versno, self._io.read_bits_int_be(2))
            self.dfcid = self._io.read_bits_int_be(2)
            self.rfu = self._io.read_bits_int_be(4)


    class AdcsStandardTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_pget_imodechklistthisstepactive = self._io.read_s1()
            self.adcs_pget_iattdetfinalstate = self._io.read_u1()
            self.adcs_pget_isensorarrayavailstatusga = self._io.read_u1()
            self.adcs_pget_isensorarrayavailstatusmfsa = self._io.read_u1()
            self.adcs_pget_isensorarrayavailstatussusea = self._io.read_u1()
            self.adcs_pget_iactarrayavailstatusrwa = self._io.read_u1()
            self.adcs_pget_iactarrayavailstatusmata = self._io.read_u1()
            self.adcs_pget_attdetmfsdistcorrmode = self._io.read_u1()
            self.adcs_pget_attdetsusedistcorrmode = self._io.read_u1()
            self.adcs_pget_attdettrackigrfdeltab = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_attdetsusealbedotracking = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse1albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse2albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse3albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse4albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse5albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_suse6albedoflag = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_attdetautovirtualizemfsa = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_attdetautovirtualizesusea = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_attdetnarrowvectors = self._io.read_bits_int_be(1) != 0
            self.adcs_pget_attdetmismatchingvectors = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.adcs_pget_omegaxoptimal_sat = Snet.Angularrate(self._io, self, self._root)
            self.adcs_pget_omegayoptimal_sat = Snet.Angularrate(self._io, self, self._root)
            self.adcs_pget_omegazoptimal_sat = Snet.Angularrate(self._io, self, self._root)
            self.adcs_pget_magxoptimal_sat = Snet.Magfield(self._io, self, self._root)
            self.adcs_pget_magyoptimal_sat = Snet.Magfield(self._io, self, self._root)
            self.adcs_pget_magzoptimal_sat = Snet.Magfield(self._io, self, self._root)
            self.adcs_pget_sunxoptimal_sat = Snet.Sunvect(self._io, self, self._root)
            self.adcs_pget_sunyoptimal_sat = Snet.Sunvect(self._io, self, self._root)
            self.adcs_pget_sunzoptimal_sat = Snet.Sunvect(self._io, self, self._root)
            self.adcs_pget_dctrltorquerwax_sat_lr = Snet.Torquerw(self._io, self, self._root)
            self.adcs_pget_dctrltorquerway_sat_lr = Snet.Torquerw(self._io, self, self._root)
            self.adcs_pget_dctrltorquerwaz_sat_lr = Snet.Torquerw(self._io, self, self._root)
            self.adcs_pget_dctrlmagmomentmatax_sat_lr = Snet.Torquemag(self._io, self, self._root)
            self.adcs_pget_dctrlmagmomentmatay_sat_lr = Snet.Torquemag(self._io, self, self._root)
            self.adcs_pget_dctrlmagmomentmataz_sat_lr = Snet.Torquemag(self._io, self, self._root)
            self.adcs_pget_ireadtorquerwx_mfr = Snet.Measuredtorque(self._io, self, self._root)
            self.adcs_pget_ireadtorquerwy_mfr = Snet.Measuredtorque(self._io, self, self._root)
            self.adcs_pget_ireadtorquerwz_mfr = Snet.Measuredtorque(self._io, self, self._root)
            self.adcs_pget_ireadrotspeedrwx_mfr = self._io.read_s2le()
            self.adcs_pget_ireadrotspeedrwy_mfr = self._io.read_s2le()
            self.adcs_pget_ireadrotspeedrwz_mfr = self._io.read_s2le()
            self.adcs_pget_sgp4latxpef = Snet.Lat(self._io, self, self._root)
            self.adcs_pget_sgp4longypef = Snet.Lon(self._io, self, self._root)
            self.adcs_pget_sgp4altpef = Snet.Alt(self._io, self, self._root)
            self.adcs_pget_attitudeerrorangle = Snet.Attitude(self._io, self, self._root)
            self.adcs_pget_targetdata_distance = self._io.read_u2le()
            self.adcs_pget_targetdata_controlisactive = self._io.read_bits_int_be(1) != 0



