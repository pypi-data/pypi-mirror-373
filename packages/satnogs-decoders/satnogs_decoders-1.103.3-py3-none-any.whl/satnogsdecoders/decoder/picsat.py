# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Picsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field ccsds_version: ax25_frame.ax25_payload.ax25_info.ccsds_header.ccsds_version
    :field packet_type: ax25_frame.ax25_payload.ax25_info.ccsds_header.packet_type
    :field secondary_header_flag: ax25_frame.ax25_payload.ax25_info.ccsds_header.secondary_header_flag
    :field process_id: ax25_frame.ax25_payload.ax25_info.ccsds_header.process_id
    :field level_flag: ax25_frame.ax25_payload.ax25_info.ccsds_header.level_flag
    :field payload_flag: ax25_frame.ax25_payload.ax25_info.ccsds_header.payload_flag
    :field packet_category: ax25_frame.ax25_payload.ax25_info.ccsds_header.packet_category
    :field sequence_flag: ax25_frame.ax25_payload.ax25_info.ccsds_header.sequence_flag
    :field packet_id: ax25_frame.ax25_payload.ax25_info.ccsds_header.packet_id
    :field data_length: ax25_frame.ax25_payload.ax25_info.ccsds_header.data_length
    :field days_since_ref: ax25_frame.ax25_payload.ax25_info.ccsds_secondary_header.days_since_ref
    :field ms_since_today: ax25_frame.ax25_payload.ax25_info.ccsds_secondary_header.ms_since_today
    :field solar_panel5_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel5_error_flag
    :field solar_panel4_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel4_error_flag
    :field solar_panel3_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel3_error_flag
    :field solar_panel2_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel2_error_flag
    :field solar_panel1_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel1_error_flag
    :field i_adcs_get_attitude_error: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.i_adcs_get_attitude_error
    :field i_adcs_get_status_register_error: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.i_adcs_get_status_register_error
    :field fram_enable_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.fram_enable_error_flag
    :field ants_b_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ants_b_error_flag
    :field ants_a_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ants_a_error_flag
    :field trxvu_tx_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.trxvu_tx_error_flag
    :field trxvu_rx_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.trxvu_rx_error_flag
    :field obc_supervisor_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.obc_supervisor_error_flag
    :field gom_eps_error_flag: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.gom_eps_error_flag
    :field ant1_undeployed_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_undeployed_ants_b_status
    :field ant1_timeout_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_timeout_ants_b_status
    :field ant1_deploying_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_deploying_ants_b_status
    :field ant2_undeployed_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_undeployed_ants_b_status
    :field ant2_timeout_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_timeout_ants_b_status
    :field ant2_deploying_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_deploying_ants_b_status
    :field ignore_flag_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ignore_flag_ants_b_status
    :field ant3_undeployed_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_undeployed_ants_b_status
    :field ant3_timeout_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_timeout_ants_b_status
    :field ant3_deploying_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_deploying_ants_b_status
    :field ant4_undeployed_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_undeployed_ants_b_status
    :field ant4_timeout_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_timeout_ants_b_status
    :field ant4_deploying_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_deploying_ants_b_status
    :field armed_ants_b_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.armed_ants_b_status
    :field ant1_undeployed_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_undeployed_ants_a_status
    :field ant1_timeout_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_timeout_ants_a_status
    :field ant1_deploying_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant1_deploying_ants_a_status
    :field ant2_undeployed_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_undeployed_ants_a_status
    :field ant2_timeout_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_timeout_ants_a_status
    :field ant2_deploying_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant2_deploying_ants_a_status
    :field ignore_flag_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ignore_flag_ants_a_status
    :field ant3_undeployed_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_undeployed_ants_a_status
    :field ant3_timeout_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_timeout_ants_a_status
    :field ant3_deploying_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant3_deploying_ants_a_status
    :field ant4_undeployed_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_undeployed_ants_a_status
    :field ant4_timeout_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_timeout_ants_a_status
    :field ant4_deploying_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ant4_deploying_ants_a_status
    :field armed_ants_a_status: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.armed_ants_a_status
    :field solar_panel_temp5_zp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel_temp5_zp
    :field solar_panel_temp4_ym: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel_temp4_ym
    :field solar_panel_temp3_yp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel_temp3_yp
    :field solar_panel_temp2_xm: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel_temp2_xm
    :field solar_panel_temp1_xp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.solar_panel_temp1_xp
    :field ants_temperature_side_b: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ants_temperature_side_b
    :field ants_temperature_side_a: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.ants_temperature_side_a
    :field tx_trxvu_hk_current: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.tx_trxvu_hk_current
    :field tx_trxvu_hk_forwardpower: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.tx_trxvu_hk_forwardpower
    :field tx_trxvu_hk_tx_reflectedpower: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.tx_trxvu_hk_tx_reflectedpower
    :field tx_trxvu_hk_pa_temp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.tx_trxvu_hk_pa_temp
    :field rx_trxvu_hk_pa_temp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.rx_trxvu_hk_pa_temp
    :field rx_trxvu_hk_board_temp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.rx_trxvu_hk_board_temp
    :field eps_hk_temp_batt1: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.eps_hk_temp_batt1
    :field eps_hk_temp_batt0: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.eps_hk_temp_batt0
    :field eps_hk_batt_mode: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.eps_hk_batt_mode
    :field eps_h_kv_batt: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.eps_h_kv_batt
    :field eps_hk_boot_cause: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.eps_hk_boot_cause
    :field n_reboots_eps: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.n_reboots_eps
    :field n_reboots_obc: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.n_reboots_obc
    :field quaternion1: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.quaternion1
    :field quaternion2: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.quaternion2
    :field quaternion3: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.quaternion3
    :field quaternion4: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.quaternion4
    :field angular_rate_x: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.angular_rate_x
    :field angular_rate_y: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.angular_rate_y
    :field angular_rate_z: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.angular_rate_z
    :field adcs_stat_flag_hl_op_tgt_cap: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_tgt_cap
    :field adcs_stat_flag_hl_op_tgt_track_fix_wgs84: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_tgt_track_fix_wgs84
    :field adcs_stat_flag_hl_op_tgt_track_nadir: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_tgt_track_nadir
    :field adcs_stat_flag_hl_op_tgt_track: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_tgt_track
    :field adcs_stat_flag_hl_op_tgt_track_const_v: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_tgt_track_const_v
    :field adcs_stat_flag_hl_op_spin: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_spin
    :field adcs_stat_flag_hl_op_sunp: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_sunp
    :field adcs_stat_flag_hl_op_detumbling: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_detumbling
    :field adcs_stat_flag_hl_op_measure: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_measure
    :field adcs_stat_flag_datetime_valid: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_datetime_valid
    :field adcs_stat_flag_hl_op_safe: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_safe
    :field adcs_stat_flag_hl_op_idle: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.adcs_stat_flag_hl_op_idle
    :field up_time: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.up_time
    :field last_fram_log_fun_err_code: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.last_fram_log_fun_err_code
    :field last_fram_log_line_code: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.last_fram_log_line_code
    :field last_fram_log_file_crc_code: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.last_fram_log_file_crc_code
    :field last_fram_log_counter: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.last_fram_log_counter
    :field average_photon_count: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.average_photon_count
    :field sat_mode: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.sat_mode
    :field tc_sequence_count: ax25_frame.ax25_payload.ax25_info.ccsds_data_section.obc_packet.tc_sequence_count
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Picsat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Picsat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.ax25_payload = Picsat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.ax25_payload = Picsat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.ax25_payload = Picsat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.ax25_payload = Picsat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.ax25_payload = Picsat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.ax25_payload = Picsat.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Picsat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Picsat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Picsat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Picsat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Picsat.Repeater(self._io, self, self._root)

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
            self.ax25_info = Picsat.PicsatCcsdsFrameT(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"PICSAT")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class CcsdsHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.process_id = self._io.read_bits_int_be(4)
            self.level_flag = self._io.read_bits_int_be(1) != 0
            self.payload_flag = self._io.read_bits_int_be(1) != 0
            self.packet_category = self._io.read_bits_int_be(5)
            self.sequence_flag = self._io.read_bits_int_be(2)
            self.packet_id = self._io.read_bits_int_be(14)
            self.data_length = self._io.read_bits_int_be(16)


    class PicsatCcsdsFrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_header = Picsat.CcsdsHeaderT(self._io, self, self._root)
            if True == self.ccsds_header.secondary_header_flag:
                self.ccsds_secondary_header = Picsat.CcsdsSecondaryHeaderT(self._io, self, self._root)

            if False == self.ccsds_header.payload_flag:
                self.ccsds_data_section = Picsat.ObcPacketT(self._io, self, self._root)



    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


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


    class ObcPacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.ccsds_header.packet_category
            if _on == 1:
                self.obc_packet = Picsat.ObcBeaconT(self._io, self, self._root)
            else:
                self.obc_packet = Picsat.DumpT(self._io, self, self._root)


    class DumpT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.payload = self._io.read_bytes_full()


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Picsat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Picsat.SsidMask(self._io, self, self._root)


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
                _ = Picsat.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


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
            self.callsign_ror = Picsat.Callsign(_io__raw_callsign_ror, self, self._root)


    class CcsdsSecondaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.days_since_ref = self._io.read_u2be()
            self.ms_since_today = self._io.read_u4be()


    class ObcBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.solar_panel5_error_flag = self._io.read_bits_int_be(1) != 0
            self.solar_panel4_error_flag = self._io.read_bits_int_be(1) != 0
            self.solar_panel3_error_flag = self._io.read_bits_int_be(1) != 0
            self.solar_panel2_error_flag = self._io.read_bits_int_be(1) != 0
            self.solar_panel1_error_flag = self._io.read_bits_int_be(1) != 0
            self.i_adcs_get_attitude_error = self._io.read_bits_int_be(1) != 0
            self.i_adcs_get_status_register_error = self._io.read_bits_int_be(1) != 0
            self.fram_enable_error_flag = self._io.read_bits_int_be(1) != 0
            self.ants_b_error_flag = self._io.read_bits_int_be(1) != 0
            self.ants_a_error_flag = self._io.read_bits_int_be(1) != 0
            self.trxvu_tx_error_flag = self._io.read_bits_int_be(1) != 0
            self.trxvu_rx_error_flag = self._io.read_bits_int_be(1) != 0
            self.obc_supervisor_error_flag = self._io.read_bits_int_be(1) != 0
            self.gom_eps_error_flag = self._io.read_bits_int_be(1) != 0
            self.ant1_undeployed_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant1_timeout_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant1_deploying_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant2_undeployed_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant2_timeout_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant2_deploying_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ignore_flag_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant3_undeployed_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant3_timeout_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant3_deploying_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant4_undeployed_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant4_timeout_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant4_deploying_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.armed_ants_b_status = self._io.read_bits_int_be(1) != 0
            self.ant1_undeployed_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant1_timeout_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant1_deploying_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant2_undeployed_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant2_timeout_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant2_deploying_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ignore_flag_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant3_undeployed_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant3_timeout_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant3_deploying_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant4_undeployed_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant4_timeout_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.ant4_deploying_ants_a_status = self._io.read_bits_int_be(1) != 0
            self.armed_ants_a_status = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.solar_panel_temp5_zp = self._io.read_u2be()
            self.solar_panel_temp4_ym = self._io.read_u2be()
            self.solar_panel_temp3_yp = self._io.read_u2be()
            self.solar_panel_temp2_xm = self._io.read_u2be()
            self.solar_panel_temp1_xp = self._io.read_u2be()
            self.ants_temperature_side_b = self._io.read_u2be()
            self.ants_temperature_side_a = self._io.read_u2be()
            self.tx_trxvu_hk_current = self._io.read_u2be()
            self.tx_trxvu_hk_forwardpower = self._io.read_u2be()
            self.tx_trxvu_hk_tx_reflectedpower = self._io.read_u2be()
            self.tx_trxvu_hk_pa_temp = self._io.read_u2be()
            self.rx_trxvu_hk_pa_temp = self._io.read_u2be()
            self.rx_trxvu_hk_board_temp = self._io.read_u2be()
            self.eps_hk_temp_batt1 = self._io.read_s2be()
            self.eps_hk_temp_batt0 = self._io.read_s2be()
            self.eps_hk_batt_mode = self._io.read_u1()
            self.eps_h_kv_batt = self._io.read_u2be()
            self.eps_hk_boot_cause = self._io.read_u4be()
            self.n_reboots_eps = self._io.read_u4be()
            self.n_reboots_obc = self._io.read_u4be()
            self.quaternion1 = self._io.read_f4be()
            self.quaternion2 = self._io.read_f4be()
            self.quaternion3 = self._io.read_f4be()
            self.quaternion4 = self._io.read_f4be()
            self.angular_rate_x = self._io.read_f4be()
            self.angular_rate_y = self._io.read_f4be()
            self.angular_rate_z = self._io.read_f4be()
            self.gap_0 = self._io.read_bits_int_be(12)
            self.adcs_stat_flag_hl_op_tgt_cap = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_tgt_track_fix_wgs84 = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_tgt_track_nadir = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_tgt_track = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_tgt_track_const_v = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_spin = self._io.read_bits_int_be(1) != 0
            self.gap_1 = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_sunp = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_detumbling = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_measure = self._io.read_bits_int_be(1) != 0
            self.gap_2 = self._io.read_bits_int_be(5)
            self.adcs_stat_flag_datetime_valid = self._io.read_bits_int_be(1) != 0
            self.gap_3 = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_safe = self._io.read_bits_int_be(1) != 0
            self.adcs_stat_flag_hl_op_idle = self._io.read_bits_int_be(1) != 0
            self.gap_4 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.up_time = self._io.read_u4be()
            self.last_fram_log_fun_err_code = self._io.read_s2be()
            self.last_fram_log_line_code = self._io.read_u2be()
            self.last_fram_log_file_crc_code = self._io.read_u4be()
            self.last_fram_log_counter = self._io.read_u2be()
            self.average_photon_count = self._io.read_u2be()
            self.sat_mode = self._io.read_u1()
            self.tc_sequence_count = self._io.read_u2be()



