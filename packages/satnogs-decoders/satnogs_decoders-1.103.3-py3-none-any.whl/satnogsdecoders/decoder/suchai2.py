# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Suchai2(KaitaiStruct):
    """:field prio: sch.csp_h.prio
    :field source: sch.csp_h.source
    :field dest: sch.csp_h.dest
    :field dest_port: sch.csp_h.dest_port
    :field source_port: sch.csp_h.source_port
    :field flags: sch.csp_h.flags
    :field nframe: sch.nframe
    :field type: sch.type
    :field node: sch.node
    :field ndata: sch.ndata
    :field index: sch.status.index
    :field timestamp: sch.status.timestamp
    :field dat_obc_opmode: sch.status.dat_obc_opmode
    :field dat_rtc_date_time: sch.status.dat_rtc_date_time
    :field dat_obc_last_reset: sch.status.dat_obc_last_reset
    :field dat_obc_hrs_alive: sch.status.dat_obc_hrs_alive
    :field dat_obc_hrs_wo_reset: sch.status.dat_obc_hrs_wo_reset
    :field dat_obc_reset_counter: sch.status.dat_obc_reset_counter
    :field dat_obc_executed_cmds: sch.status.dat_obc_executed_cmds
    :field dat_obc_failed_cmds: sch.status.dat_obc_failed_cmds
    :field dat_com_count_tm: sch.status.dat_com_count_tm
    :field dat_com_count_tc: sch.status.dat_com_count_tc
    :field dat_com_last_tc: sch.status.dat_com_last_tc
    :field dat_fpl_last: sch.status.dat_fpl_last
    :field dat_fpl_queue: sch.status.dat_fpl_queue
    :field dat_ads_tle_epoch: sch.status.dat_ads_tle_epoch
    :field dat_eps_vbatt: sch.status.dat_eps_vbatt
    :field dat_eps_cur_sun: sch.status.dat_eps_cur_sun
    :field dat_eps_cur_sys: sch.status.dat_eps_cur_sys
    :field dat_obc_temp_1: sch.status.dat_obc_temp_1
    :field dat_eps_temp_bat0: sch.status.dat_eps_temp_bat0
    :field dat_drp_mach_action: sch.status.dat_drp_mach_action
    :field dat_drp_mach_state: sch.status.dat_drp_mach_state
    :field dat_drp_mach_payloads: sch.status.dat_drp_mach_payloads
    :field dat_drp_mach_step: sch.status.dat_drp_mach_step
    :field sat_id: sch.sat_id
    """

    class SatName(Enum):
        suchai2 = 16
        suchai3 = 17
        plantsat = 18
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.sch = Suchai2.SuchaiFrame(self._io, self, self._root)

    class SuchaiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_h = Suchai2.CspHeader(self._io, self, self._root)
            self.nframe = self._io.read_u2be()
            self.type = self._io.read_u1()
            self.node = self._io.read_u1()
            self.ndata = self._io.read_u4be()
            self.status = Suchai2.Status(self._io, self, self._root)

        @property
        def sat_id(self):
            if hasattr(self, '_m_sat_id'):
                return self._m_sat_id

            self._m_sat_id = KaitaiStream.resolve_enum(Suchai2.SatName, self.csp_h.dest_port)
            return getattr(self, '_m_sat_id', None)


    class CspHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.prio = self._io.read_bits_int_be(2)
            self.source = self._io.read_bits_int_be(5)
            self.dest = self._io.read_bits_int_be(5)
            self.dest_port = self._io.read_bits_int_be(6)
            self.source_port = self._io.read_bits_int_be(6)
            self._io.align_to_byte()
            self.flags = self._io.read_u1()


    class Status(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.index = self._io.read_u4be()
            self.timestamp = self._io.read_u4be()
            self.dat_obc_opmode = self._io.read_u4be()
            self.dat_rtc_date_time = self._io.read_u4be()
            self.dat_obc_last_reset = self._io.read_u4be()
            self.dat_obc_hrs_alive = self._io.read_u4be()
            self.dat_obc_hrs_wo_reset = self._io.read_u4be()
            self.dat_obc_reset_counter = self._io.read_u4be()
            self.dat_obc_executed_cmds = self._io.read_u4be()
            self.dat_obc_failed_cmds = self._io.read_u4be()
            self.dat_com_count_tm = self._io.read_u4be()
            self.dat_com_count_tc = self._io.read_u4be()
            self.dat_com_last_tc = self._io.read_u4be()
            self.dat_fpl_last = self._io.read_u4be()
            self.dat_fpl_queue = self._io.read_u4be()
            self.dat_ads_tle_epoch = self._io.read_u4be()
            self.dat_eps_vbatt = self._io.read_u4be()
            self.dat_eps_cur_sun = self._io.read_u4be()
            self.dat_eps_cur_sys = self._io.read_u4be()
            self.dat_obc_temp_1 = self._io.read_u4be()
            self.dat_eps_temp_bat0 = self._io.read_u4be()
            self.dat_drp_mach_action = self._io.read_u4be()
            self.dat_drp_mach_state = self._io.read_u4be()
            self.dat_drp_mach_payloads = self._io.read_u4be()
            self.dat_drp_mach_step = self._io.read_u4be()



