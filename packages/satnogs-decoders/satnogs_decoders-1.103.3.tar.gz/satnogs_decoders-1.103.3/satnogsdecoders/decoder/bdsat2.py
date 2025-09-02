# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Bdsat2(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field monitor: ax25_frame.payload.ax25_info.monitor
    :field packet_type_q: ax25_frame.payload.ax25_info.packet_type_q
    :field message: ax25_frame.payload.ax25_info.body.message
    
    :field obc_reset_cnt: ax25_frame.payload.ax25_info.body.obc_reset_cnt
    :field obc_uptime: ax25_frame.payload.ax25_info.body.obc_uptime
    :field obc_uptime_tot: ax25_frame.payload.ax25_info.body.obc_uptime_tot
    :field obc_bat: ax25_frame.payload.ax25_info.body.obc_bat
    :field obc_temp_mcu: ax25_frame.payload.ax25_info.body.obc_temp_mcu
    :field obc_temp_brd: ax25_frame.payload.ax25_info.body.obc_temp_brd
    :field obc_temp_zn: ax25_frame.payload.ax25_info.body.obc_temp_zn
    :field obc_temp_xp: ax25_frame.payload.ax25_info.body.obc_temp_xp
    :field obc_temp_yp: ax25_frame.payload.ax25_info.body.obc_temp_yp
    :field obc_temp_yn: ax25_frame.payload.ax25_info.body.obc_temp_yn
    :field obc_temp_xn: ax25_frame.payload.ax25_info.body.obc_temp_xn
    :field obc_freemem: ax25_frame.payload.ax25_info.body.obc_freemem
    
    :field psu_reset_cnt: ax25_frame.payload.ax25_info.body.psu_reset_cnt
    :field psu_uptime: ax25_frame.payload.ax25_info.body.psu_uptime
    :field psu_uptime_tot: ax25_frame.payload.ax25_info.body.psu_uptime_tot
    :field psu_battery: ax25_frame.payload.ax25_info.body.psu_battery
    :field psu_temp_sys: ax25_frame.payload.ax25_info.body.psu_temp_sys
    :field psu_temp_bat: ax25_frame.payload.ax25_info.body.psu_temp_bat
    :field psu_cur_in: ax25_frame.payload.ax25_info.body.psu_cur_in
    :field psu_cur_out: ax25_frame.payload.ax25_info.body.psu_cur_out
    :field psu_ch_state_num: ax25_frame.payload.ax25_info.body.psu_ch_state_num
    :field psu_ch0_state: ax25_frame.payload.ax25_info.body.psu_ch0_state
    :field psu_ch1_state: ax25_frame.payload.ax25_info.body.psu_ch1_state
    :field psu_ch2_state: ax25_frame.payload.ax25_info.body.psu_ch2_state
    :field psu_ch3_state: ax25_frame.payload.ax25_info.body.psu_ch3_state
    :field psu_ch4_state: ax25_frame.payload.ax25_info.body.psu_ch4_state
    :field psu_ch5_state: ax25_frame.payload.ax25_info.body.psu_ch5_state
    :field psu_ch6_state: ax25_frame.payload.ax25_info.body.psu_ch6_state
    :field psu_sys_state: ax25_frame.payload.ax25_info.body.psu_sys_state
    :field psu_gnd_wdt: ax25_frame.payload.ax25_info.body.psu_gnd_wdt
    
    :field uhf_uptime: ax25_frame.payload.ax25_info.body.uhf_uptime
    :field uhf_uptime_tot: ax25_frame.payload.ax25_info.body.uhf_uptime_tot
    :field uhf_reset_cnt: ax25_frame.payload.ax25_info.body.uhf_reset_cnt
    :field uhf_rf_reset_cnt: ax25_frame.payload.ax25_info.body.uhf_rf_reset_cnt
    :field uhf_trx_temp: ax25_frame.payload.ax25_info.body.uhf_trx_temp
    :field uhf_rf_temp: ax25_frame.payload.ax25_info.body.uhf_rf_temp
    :field uhf_pa_temp: ax25_frame.payload.ax25_info.body.uhf_pa_temp
    :field uhf_digipeater_cnt: ax25_frame.payload.ax25_info.body.uhf_digipeater_cnt
    :field uhf_last_digipeater: ax25_frame.payload.ax25_info.body.uhf_last_digipeater
    :field uhf_rx_cnt: ax25_frame.payload.ax25_info.body.uhf_rx_cnt
    :field uhf_tx_cnt: ax25_frame.payload.ax25_info.body.uhf_tx_cnt
    :field uhf_act_rssi_raw: ax25_frame.payload.ax25_info.body.uhf_act_rssi_raw
    :field uhf_dcd_rssi_raw: ax25_frame.payload.ax25_info.body.uhf_dcd_rssi_raw
    :field vhf_uptime: ax25_frame.payload.ax25_info.body.vhf_uptime
    :field vhf_uptime_tot: ax25_frame.payload.ax25_info.body.vhf_uptime_tot
    :field vhf_reset_cnt: ax25_frame.payload.ax25_info.body.vhf_reset_cnt
    :field vhf_rf_reset_cnt: ax25_frame.payload.ax25_info.body.vhf_rf_reset_cnt
    :field vhf_trx_temp: ax25_frame.payload.ax25_info.body.vhf_trx_temp
    :field vhf_rf_temp: ax25_frame.payload.ax25_info.body.vhf_rf_temp
    :field vhf_pa_temp: ax25_frame.payload.ax25_info.body.vhf_pa_temp
    :field vhf_digipeater_cnt: ax25_frame.payload.ax25_info.body.vhf_digipeater_cnt
    :field vhf_last_digipeater: ax25_frame.payload.ax25_info.body.vhf_last_digipeater
    :field vhf_rx_cnt: ax25_frame.payload.ax25_info.body.vhf_rx_cnt
    :field vhf_tx_cnt: ax25_frame.payload.ax25_info.body.vhf_tx_cnt
    :field vhf_act_rssi_raw: ax25_frame.payload.ax25_info.body.vhf_act_rssi_raw
    :field vhf_dcd_rssi_raw: ax25_frame.payload.ax25_info.body.vhf_dcd_rssi_raw
    
    :field bds_state: ax25_frame.payload.ax25_info.body.bds_state
    :field bds_prog_id: ax25_frame.payload.ax25_info.body.bds_prog_id
    :field bds_hwstate_int: ax25_frame.payload.ax25_info.body.bds_hwstate
    :field bds_cron: ax25_frame.payload.ax25_info.body.bds_cron
    :field bds_tmp_c0: ax25_frame.payload.ax25_info.body.bds_tmp_c0
    :field bds_tmp_c1: ax25_frame.payload.ax25_info.body.bds_tmp_c1
    :field bds_tmp_e1_0: ax25_frame.payload.ax25_info.body.bds_tmp_e1_0
    :field bds_tmp_e1_1: ax25_frame.payload.ax25_info.body.bds_tmp_e1_1
    :field bds_tmp_e1_2: ax25_frame.payload.ax25_info.body.bds_tmp_e1_2
    :field bds_tmp_e1_3: ax25_frame.payload.ax25_info.body.bds_tmp_e1_3
    :field bds_tmp_e2_0: ax25_frame.payload.ax25_info.body.bds_tmp_e2_0
    :field bds_tmp_e2_1: ax25_frame.payload.ax25_info.body.bds_tmp_e2_1
    :field bds_tmp_e2_2: ax25_frame.payload.ax25_info.body.bds_tmp_e2_2
    :field bds_tmp_e2_3: ax25_frame.payload.ax25_info.body.bds_tmp_e2_3
    :field bds_tmp_ei_0: ax25_frame.payload.ax25_info.body.bds_tmp_ei_0_float
    :field bds_tmp_ei_1: ax25_frame.payload.ax25_info.body.bds_tmp_ei_1_float
    :field bds_pres_ei_0: ax25_frame.payload.ax25_info.body.bds_pres_ei_0_float
    :field bds_pres_ei_1: ax25_frame.payload.ax25_info.body.bds_pres_ei_1_float
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Bdsat2.Ax25Frame(self._io, self, self._root)

    class Psu(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.psu_pass_packet_type = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_rst_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_temp_sys_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_temp_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_cur_in_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_cur_out_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_ch_state_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_sys_state_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.psu_gnd_wdt_str = (self._io.read_bytes_full()).decode(u"utf8")

        @property
        def psu_ch3_state(self):
            if hasattr(self, '_m_psu_ch3_state'):
                return self._m_psu_ch3_state

            self._m_psu_ch3_state = ((self.psu_ch_state_num >> 3) & 1)
            return getattr(self, '_m_psu_ch3_state', None)

        @property
        def psu_reset_cnt(self):
            if hasattr(self, '_m_psu_reset_cnt'):
                return self._m_psu_reset_cnt

            self._m_psu_reset_cnt = int(self.psu_rst_cnt_str)
            return getattr(self, '_m_psu_reset_cnt', None)

        @property
        def psu_uptime_tot(self):
            if hasattr(self, '_m_psu_uptime_tot'):
                return self._m_psu_uptime_tot

            self._m_psu_uptime_tot = int(self.psu_uptime_tot_str)
            return getattr(self, '_m_psu_uptime_tot', None)

        @property
        def psu_temp_bat(self):
            if hasattr(self, '_m_psu_temp_bat'):
                return self._m_psu_temp_bat

            self._m_psu_temp_bat = int(self.psu_temp_bat_str)
            return getattr(self, '_m_psu_temp_bat', None)

        @property
        def psu_ch5_state(self):
            if hasattr(self, '_m_psu_ch5_state'):
                return self._m_psu_ch5_state

            self._m_psu_ch5_state = ((self.psu_ch_state_num >> 5) & 1)
            return getattr(self, '_m_psu_ch5_state', None)

        @property
        def psu_ch0_state(self):
            if hasattr(self, '_m_psu_ch0_state'):
                return self._m_psu_ch0_state

            self._m_psu_ch0_state = ((self.psu_ch_state_num >> 0) & 1)
            return getattr(self, '_m_psu_ch0_state', None)

        @property
        def psu_gnd_wdt(self):
            if hasattr(self, '_m_psu_gnd_wdt'):
                return self._m_psu_gnd_wdt

            self._m_psu_gnd_wdt = int(self.psu_gnd_wdt_str)
            return getattr(self, '_m_psu_gnd_wdt', None)

        @property
        def psu_uptime(self):
            if hasattr(self, '_m_psu_uptime'):
                return self._m_psu_uptime

            self._m_psu_uptime = int(self.psu_uptime_str)
            return getattr(self, '_m_psu_uptime', None)

        @property
        def psu_sys_state(self):
            if hasattr(self, '_m_psu_sys_state'):
                return self._m_psu_sys_state

            self._m_psu_sys_state = int(self.psu_sys_state_str)
            return getattr(self, '_m_psu_sys_state', None)

        @property
        def psu_ch_state_num(self):
            if hasattr(self, '_m_psu_ch_state_num'):
                return self._m_psu_ch_state_num

            self._m_psu_ch_state_num = int(self.psu_ch_state_str, 16)
            return getattr(self, '_m_psu_ch_state_num', None)

        @property
        def psu_ch6_state(self):
            if hasattr(self, '_m_psu_ch6_state'):
                return self._m_psu_ch6_state

            self._m_psu_ch6_state = ((self.psu_ch_state_num >> 6) & 1)
            return getattr(self, '_m_psu_ch6_state', None)

        @property
        def psu_cur_out(self):
            if hasattr(self, '_m_psu_cur_out'):
                return self._m_psu_cur_out

            self._m_psu_cur_out = int(self.psu_cur_out_str)
            return getattr(self, '_m_psu_cur_out', None)

        @property
        def psu_ch2_state(self):
            if hasattr(self, '_m_psu_ch2_state'):
                return self._m_psu_ch2_state

            self._m_psu_ch2_state = ((self.psu_ch_state_num >> 2) & 1)
            return getattr(self, '_m_psu_ch2_state', None)

        @property
        def psu_temp_sys(self):
            if hasattr(self, '_m_psu_temp_sys'):
                return self._m_psu_temp_sys

            self._m_psu_temp_sys = int(self.psu_temp_sys_str)
            return getattr(self, '_m_psu_temp_sys', None)

        @property
        def psu_cur_in(self):
            if hasattr(self, '_m_psu_cur_in'):
                return self._m_psu_cur_in

            self._m_psu_cur_in = int(self.psu_cur_in_str)
            return getattr(self, '_m_psu_cur_in', None)

        @property
        def psu_ch1_state(self):
            if hasattr(self, '_m_psu_ch1_state'):
                return self._m_psu_ch1_state

            self._m_psu_ch1_state = ((self.psu_ch_state_num >> 1) & 1)
            return getattr(self, '_m_psu_ch1_state', None)

        @property
        def psu_ch4_state(self):
            if hasattr(self, '_m_psu_ch4_state'):
                return self._m_psu_ch4_state

            self._m_psu_ch4_state = ((self.psu_ch_state_num >> 4) & 1)
            return getattr(self, '_m_psu_ch4_state', None)

        @property
        def psu_battery(self):
            if hasattr(self, '_m_psu_battery'):
                return self._m_psu_battery

            self._m_psu_battery = int(self.psu_bat_str)
            return getattr(self, '_m_psu_battery', None)


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Bdsat2.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Bdsat2.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Bdsat2.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Bdsat2.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Bdsat2.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Bdsat2.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Bdsat2.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Bdsat2.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Bdsat2.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Bdsat2.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Bdsat2.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Bdsat2.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Bdsat2.Tlm(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Bds(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bds_pass_packet_type = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_state = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_prog_id = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_hwstate = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_cron = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_c0_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_c1_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e1_0_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e1_1_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e1_2_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e1_3_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e2_0_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e2_1_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e2_2_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_e2_3_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_ei_0_w_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
            self.bds_tmp_ei_0_d_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_tmp_ei_1_w_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
            self.bds_tmp_ei_1_d_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_pres_ei_0_w_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
            self.bds_pres_ei_0_d_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.bds_pres_ei_1_w_str = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
            self.bds_pres_ei_1_d_str = (self._io.read_bytes_full()).decode(u"utf8")

        @property
        def bds_tmp_e2_1(self):
            if hasattr(self, '_m_bds_tmp_e2_1'):
                return self._m_bds_tmp_e2_1

            self._m_bds_tmp_e2_1 = int(self.bds_tmp_e2_1_str)
            return getattr(self, '_m_bds_tmp_e2_1', None)

        @property
        def bds_tmp_c1(self):
            if hasattr(self, '_m_bds_tmp_c1'):
                return self._m_bds_tmp_c1

            self._m_bds_tmp_c1 = int(self.bds_tmp_c1_str)
            return getattr(self, '_m_bds_tmp_c1', None)

        @property
        def bds_tmp_e1_3(self):
            if hasattr(self, '_m_bds_tmp_e1_3'):
                return self._m_bds_tmp_e1_3

            self._m_bds_tmp_e1_3 = int(self.bds_tmp_e1_3_str)
            return getattr(self, '_m_bds_tmp_e1_3', None)

        @property
        def bds_tmp_e2_0(self):
            if hasattr(self, '_m_bds_tmp_e2_0'):
                return self._m_bds_tmp_e2_0

            self._m_bds_tmp_e2_0 = int(self.bds_tmp_e2_0_str)
            return getattr(self, '_m_bds_tmp_e2_0', None)

        @property
        def bds_tmp_c0(self):
            if hasattr(self, '_m_bds_tmp_c0'):
                return self._m_bds_tmp_c0

            self._m_bds_tmp_c0 = int(self.bds_tmp_c0_str)
            return getattr(self, '_m_bds_tmp_c0', None)

        @property
        def bds_tmp_e1_0(self):
            if hasattr(self, '_m_bds_tmp_e1_0'):
                return self._m_bds_tmp_e1_0

            self._m_bds_tmp_e1_0 = int(self.bds_tmp_e1_0_str)
            return getattr(self, '_m_bds_tmp_e1_0', None)

        @property
        def bds_tmp_e1_2(self):
            if hasattr(self, '_m_bds_tmp_e1_2'):
                return self._m_bds_tmp_e1_2

            self._m_bds_tmp_e1_2 = int(self.bds_tmp_e1_2_str)
            return getattr(self, '_m_bds_tmp_e1_2', None)

        @property
        def bds_tmp_ei_0_float(self):
            if hasattr(self, '_m_bds_tmp_ei_0_float'):
                return self._m_bds_tmp_ei_0_float

            self._m_bds_tmp_ei_0_float = (int(self.bds_tmp_ei_0_w_str) + (int(self.bds_tmp_ei_0_d_str) * 0.01))
            return getattr(self, '_m_bds_tmp_ei_0_float', None)

        @property
        def bds_tmp_ei_1_float(self):
            if hasattr(self, '_m_bds_tmp_ei_1_float'):
                return self._m_bds_tmp_ei_1_float

            self._m_bds_tmp_ei_1_float = (int(self.bds_tmp_ei_1_w_str) + (int(self.bds_tmp_ei_1_d_str) * 0.01))
            return getattr(self, '_m_bds_tmp_ei_1_float', None)

        @property
        def bds_hwstate_int(self):
            if hasattr(self, '_m_bds_hwstate_int'):
                return self._m_bds_hwstate_int

            self._m_bds_hwstate_int = int(self.bds_hwstate)
            return getattr(self, '_m_bds_hwstate_int', None)

        @property
        def bds_pres_ei_1_float(self):
            if hasattr(self, '_m_bds_pres_ei_1_float'):
                return self._m_bds_pres_ei_1_float

            self._m_bds_pres_ei_1_float = (int(self.bds_pres_ei_1_w_str) + (int(self.bds_pres_ei_1_d_str) * 0.001))
            return getattr(self, '_m_bds_pres_ei_1_float', None)

        @property
        def bds_tmp_e2_3(self):
            if hasattr(self, '_m_bds_tmp_e2_3'):
                return self._m_bds_tmp_e2_3

            self._m_bds_tmp_e2_3 = int(self.bds_tmp_e2_3_str)
            return getattr(self, '_m_bds_tmp_e2_3', None)

        @property
        def bds_tmp_e2_2(self):
            if hasattr(self, '_m_bds_tmp_e2_2'):
                return self._m_bds_tmp_e2_2

            self._m_bds_tmp_e2_2 = int(self.bds_tmp_e2_2_str)
            return getattr(self, '_m_bds_tmp_e2_2', None)

        @property
        def bds_pres_ei_0_float(self):
            if hasattr(self, '_m_bds_pres_ei_0_float'):
                return self._m_bds_pres_ei_0_float

            self._m_bds_pres_ei_0_float = (int(self.bds_pres_ei_0_w_str) + (int(self.bds_pres_ei_0_d_str) * 0.001))
            return getattr(self, '_m_bds_pres_ei_0_float', None)

        @property
        def bds_tmp_e1_1(self):
            if hasattr(self, '_m_bds_tmp_e1_1'):
                return self._m_bds_tmp_e1_1

            self._m_bds_tmp_e1_1 = int(self.bds_tmp_e1_1_str)
            return getattr(self, '_m_bds_tmp_e1_1', None)


    class Uhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.uhf_packet_id_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_rf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_trx_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_rf_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_pa_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_digipeater_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_last_digipeater_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_rx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_tx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_act_rssi_raw_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uhf_dcd_rssi_raw_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def uhf_rf_reset_cnt(self):
            if hasattr(self, '_m_uhf_rf_reset_cnt'):
                return self._m_uhf_rf_reset_cnt

            self._m_uhf_rf_reset_cnt = int(self.uhf_rf_reset_cnt_str)
            return getattr(self, '_m_uhf_rf_reset_cnt', None)

        @property
        def uhf_act_rssi_raw(self):
            if hasattr(self, '_m_uhf_act_rssi_raw'):
                return self._m_uhf_act_rssi_raw

            self._m_uhf_act_rssi_raw = int(self.uhf_act_rssi_raw_str)
            return getattr(self, '_m_uhf_act_rssi_raw', None)

        @property
        def uhf_last_digipeater(self):
            if hasattr(self, '_m_uhf_last_digipeater'):
                return self._m_uhf_last_digipeater

            self._m_uhf_last_digipeater = self.uhf_last_digipeater_str
            return getattr(self, '_m_uhf_last_digipeater', None)

        @property
        def uhf_pa_temp(self):
            if hasattr(self, '_m_uhf_pa_temp'):
                return self._m_uhf_pa_temp

            self._m_uhf_pa_temp = int(self.uhf_pa_temp_str)
            return getattr(self, '_m_uhf_pa_temp', None)

        @property
        def uhf_uptime_tot(self):
            if hasattr(self, '_m_uhf_uptime_tot'):
                return self._m_uhf_uptime_tot

            self._m_uhf_uptime_tot = int(self.uhf_uptime_tot_str)
            return getattr(self, '_m_uhf_uptime_tot', None)

        @property
        def uhf_tx_cnt(self):
            if hasattr(self, '_m_uhf_tx_cnt'):
                return self._m_uhf_tx_cnt

            self._m_uhf_tx_cnt = int(self.uhf_tx_cnt_str)
            return getattr(self, '_m_uhf_tx_cnt', None)

        @property
        def uhf_rf_temp(self):
            if hasattr(self, '_m_uhf_rf_temp'):
                return self._m_uhf_rf_temp

            self._m_uhf_rf_temp = int(self.uhf_rf_temp_str)
            return getattr(self, '_m_uhf_rf_temp', None)

        @property
        def uhf_dcd_rssi_raw(self):
            if hasattr(self, '_m_uhf_dcd_rssi_raw'):
                return self._m_uhf_dcd_rssi_raw

            self._m_uhf_dcd_rssi_raw = int(self.uhf_dcd_rssi_raw_str)
            return getattr(self, '_m_uhf_dcd_rssi_raw', None)

        @property
        def uhf_uptime(self):
            if hasattr(self, '_m_uhf_uptime'):
                return self._m_uhf_uptime

            self._m_uhf_uptime = int(self.uhf_uptime_str)
            return getattr(self, '_m_uhf_uptime', None)

        @property
        def uhf_rx_cnt(self):
            if hasattr(self, '_m_uhf_rx_cnt'):
                return self._m_uhf_rx_cnt

            self._m_uhf_rx_cnt = int(self.uhf_rx_cnt_str)
            return getattr(self, '_m_uhf_rx_cnt', None)

        @property
        def uhf_reset_cnt(self):
            if hasattr(self, '_m_uhf_reset_cnt'):
                return self._m_uhf_reset_cnt

            self._m_uhf_reset_cnt = int(self.uhf_reset_cnt_str)
            return getattr(self, '_m_uhf_reset_cnt', None)

        @property
        def uhf_digipeater_cnt(self):
            if hasattr(self, '_m_uhf_digipeater_cnt'):
                return self._m_uhf_digipeater_cnt

            self._m_uhf_digipeater_cnt = int(self.uhf_digipeater_cnt_str)
            return getattr(self, '_m_uhf_digipeater_cnt', None)

        @property
        def uhf_trx_temp(self):
            if hasattr(self, '_m_uhf_trx_temp'):
                return self._m_uhf_trx_temp

            self._m_uhf_trx_temp = int(self.uhf_trx_temp_str)
            return getattr(self, '_m_uhf_trx_temp', None)


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Bdsat2.Tlm(_io__raw_ax25_info, self, self._root)


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


    class Vhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vhf_packet_id_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_rf_reset_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_trx_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_rf_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_pa_temp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_digipeater_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_last_digipeater_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_rx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_tx_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_act_rssi_raw_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.vhf_dcd_rssi_raw_str = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

        @property
        def vhf_digipeater_cnt(self):
            if hasattr(self, '_m_vhf_digipeater_cnt'):
                return self._m_vhf_digipeater_cnt

            self._m_vhf_digipeater_cnt = int(self.vhf_digipeater_cnt_str)
            return getattr(self, '_m_vhf_digipeater_cnt', None)

        @property
        def vhf_tx_cnt(self):
            if hasattr(self, '_m_vhf_tx_cnt'):
                return self._m_vhf_tx_cnt

            self._m_vhf_tx_cnt = int(self.vhf_tx_cnt_str)
            return getattr(self, '_m_vhf_tx_cnt', None)

        @property
        def vhf_rx_cnt(self):
            if hasattr(self, '_m_vhf_rx_cnt'):
                return self._m_vhf_rx_cnt

            self._m_vhf_rx_cnt = int(self.vhf_rx_cnt_str)
            return getattr(self, '_m_vhf_rx_cnt', None)

        @property
        def vhf_last_digipeater(self):
            if hasattr(self, '_m_vhf_last_digipeater'):
                return self._m_vhf_last_digipeater

            self._m_vhf_last_digipeater = self.vhf_last_digipeater_str
            return getattr(self, '_m_vhf_last_digipeater', None)

        @property
        def vhf_pa_temp(self):
            if hasattr(self, '_m_vhf_pa_temp'):
                return self._m_vhf_pa_temp

            self._m_vhf_pa_temp = int(self.vhf_pa_temp_str)
            return getattr(self, '_m_vhf_pa_temp', None)

        @property
        def vhf_uptime(self):
            if hasattr(self, '_m_vhf_uptime'):
                return self._m_vhf_uptime

            self._m_vhf_uptime = int(self.vhf_uptime_str)
            return getattr(self, '_m_vhf_uptime', None)

        @property
        def vhf_rf_temp(self):
            if hasattr(self, '_m_vhf_rf_temp'):
                return self._m_vhf_rf_temp

            self._m_vhf_rf_temp = int(self.vhf_rf_temp_str)
            return getattr(self, '_m_vhf_rf_temp', None)

        @property
        def vhf_uptime_tot(self):
            if hasattr(self, '_m_vhf_uptime_tot'):
                return self._m_vhf_uptime_tot

            self._m_vhf_uptime_tot = int(self.vhf_uptime_tot_str)
            return getattr(self, '_m_vhf_uptime_tot', None)

        @property
        def vhf_trx_temp(self):
            if hasattr(self, '_m_vhf_trx_temp'):
                return self._m_vhf_trx_temp

            self._m_vhf_trx_temp = int(self.vhf_trx_temp_str)
            return getattr(self, '_m_vhf_trx_temp', None)

        @property
        def vhf_rf_reset_cnt(self):
            if hasattr(self, '_m_vhf_rf_reset_cnt'):
                return self._m_vhf_rf_reset_cnt

            self._m_vhf_rf_reset_cnt = int(self.vhf_rf_reset_cnt_str)
            return getattr(self, '_m_vhf_rf_reset_cnt', None)

        @property
        def vhf_dcd_rssi_raw(self):
            if hasattr(self, '_m_vhf_dcd_rssi_raw'):
                return self._m_vhf_dcd_rssi_raw

            self._m_vhf_dcd_rssi_raw = int(self.vhf_dcd_rssi_raw_str)
            return getattr(self, '_m_vhf_dcd_rssi_raw', None)

        @property
        def vhf_reset_cnt(self):
            if hasattr(self, '_m_vhf_reset_cnt'):
                return self._m_vhf_reset_cnt

            self._m_vhf_reset_cnt = int(self.vhf_reset_cnt_str)
            return getattr(self, '_m_vhf_reset_cnt', None)

        @property
        def vhf_act_rssi_raw(self):
            if hasattr(self, '_m_vhf_act_rssi_raw'):
                return self._m_vhf_act_rssi_raw

            self._m_vhf_act_rssi_raw = int(self.vhf_act_rssi_raw_str)
            return getattr(self, '_m_vhf_act_rssi_raw', None)


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Bdsat2.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Bdsat2.SsidMask(self._io, self, self._root)


    class Repeater(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_instance = []
            i = 0
            while True:
                _ = Bdsat2.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class Msg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = (self._io.read_bytes_full()).decode(u"utf8")


    class Obc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc_pass_packet_type = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_rst_cnt_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_uptime_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_uptime_tot_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_bat_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_mcu_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_brd_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_zn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yp_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_yn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_temp_xn_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.obc_freemem_str = (self._io.read_bytes_full()).decode(u"utf8")

        @property
        def obc_uptime(self):
            if hasattr(self, '_m_obc_uptime'):
                return self._m_obc_uptime

            self._m_obc_uptime = int(self.obc_uptime_str)
            return getattr(self, '_m_obc_uptime', None)

        @property
        def obc_temp_xp(self):
            if hasattr(self, '_m_obc_temp_xp'):
                return self._m_obc_temp_xp

            self._m_obc_temp_xp = int(self.obc_temp_xp_str)
            return getattr(self, '_m_obc_temp_xp', None)

        @property
        def obc_temp_yp(self):
            if hasattr(self, '_m_obc_temp_yp'):
                return self._m_obc_temp_yp

            self._m_obc_temp_yp = int(self.obc_temp_yp_str)
            return getattr(self, '_m_obc_temp_yp', None)

        @property
        def obc_freemem(self):
            if hasattr(self, '_m_obc_freemem'):
                return self._m_obc_freemem

            self._m_obc_freemem = int(self.obc_freemem_str)
            return getattr(self, '_m_obc_freemem', None)

        @property
        def obc_temp_zn(self):
            if hasattr(self, '_m_obc_temp_zn'):
                return self._m_obc_temp_zn

            self._m_obc_temp_zn = int(self.obc_temp_zn_str)
            return getattr(self, '_m_obc_temp_zn', None)

        @property
        def obc_temp_brd(self):
            if hasattr(self, '_m_obc_temp_brd'):
                return self._m_obc_temp_brd

            self._m_obc_temp_brd = int(self.obc_temp_brd_str)
            return getattr(self, '_m_obc_temp_brd', None)

        @property
        def obc_bat(self):
            if hasattr(self, '_m_obc_bat'):
                return self._m_obc_bat

            self._m_obc_bat = int(self.obc_bat_str)
            return getattr(self, '_m_obc_bat', None)

        @property
        def obc_uptime_tot(self):
            if hasattr(self, '_m_obc_uptime_tot'):
                return self._m_obc_uptime_tot

            self._m_obc_uptime_tot = int(self.obc_uptime_tot_str)
            return getattr(self, '_m_obc_uptime_tot', None)

        @property
        def obc_reset_cnt(self):
            if hasattr(self, '_m_obc_reset_cnt'):
                return self._m_obc_reset_cnt

            self._m_obc_reset_cnt = int(self.obc_rst_cnt_str)
            return getattr(self, '_m_obc_reset_cnt', None)

        @property
        def obc_temp_yn(self):
            if hasattr(self, '_m_obc_temp_yn'):
                return self._m_obc_temp_yn

            self._m_obc_temp_yn = int(self.obc_temp_yn_str)
            return getattr(self, '_m_obc_temp_yn', None)

        @property
        def obc_temp_xn(self):
            if hasattr(self, '_m_obc_temp_xn'):
                return self._m_obc_temp_xn

            self._m_obc_temp_xn = int(self.obc_temp_xn_str)
            return getattr(self, '_m_obc_temp_xn', None)

        @property
        def obc_temp_mcu(self):
            if hasattr(self, '_m_obc_temp_mcu'):
                return self._m_obc_temp_mcu

            self._m_obc_temp_mcu = int(self.obc_temp_mcu_str)
            return getattr(self, '_m_obc_temp_mcu', None)


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
            self.callsign_ror = Bdsat2.Callsign(_io__raw_callsign_ror, self, self._root)


    class Tlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.packet_type_q
            if _on == 66:
                self.body = Bdsat2.Bds(self._io, self, self._root)
            elif _on == 85:
                self.body = Bdsat2.Uhf(self._io, self, self._root)
            elif _on == 86:
                self.body = Bdsat2.Vhf(self._io, self, self._root)
            elif _on == 79:
                self.body = Bdsat2.Obc(self._io, self, self._root)
            elif _on == 80:
                self.body = Bdsat2.Psu(self._io, self, self._root)
            else:
                self.body = Bdsat2.Msg(self._io, self, self._root)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_monitor = (self._io.read_bytes_full()).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_monitor', None)

        @property
        def packet_type_q(self):
            if hasattr(self, '_m_packet_type_q'):
                return self._m_packet_type_q

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_packet_type_q = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_packet_type_q', None)



