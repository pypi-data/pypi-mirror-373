# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Aepex(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field ccsds_version: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.ccsds_version
    :field packet_type: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_type
    :field secondary_header_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.secondary_header_flag
    :field is_stored_data: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.is_stored_data
    :field application_process_id: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.application_process_id
    :field grouping_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.grouping_flag
    :field sequence_count: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.sequence_count
    :field packet_length: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.packet_length
    :field time_stamp_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.time_stamp_seconds
    :field sub_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.sub_seconds
    :field padding: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.padding
    :field sw_cmd_recv_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_recv_count
    :field sw_cmd_fmt_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_fmt_count
    :field sw_cmd_rjct_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_rjct_count
    :field sw_cmd_succ_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_succ_count
    :field padding1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.padding1
    :field padding2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.padding2
    :field sw_cmd_fail_code: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_fail_code
    :field sw_cmd_xsum_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_xsum_state
    :field reusable_spare_1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_1
    :field reusable_spare_2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_2
    :field reusable_spare_3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_3
    :field reusable_spare_4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_4
    :field reusable_spare_5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_5
    :field sw_cmd_arm_state_uhf: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_arm_state_uhf
    :field sw_cmd_arm_state_seq: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_arm_state_seq
    :field sw_cmd_arm_state_dbg: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_cmd_arm_state_dbg
    :field reusable_spare_6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_6
    :field sw_eps_pwr_state_inst4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_inst4
    :field sw_eps_pwr_state_inst3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_inst3
    :field sw_eps_pwr_state_inst2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_inst2
    :field sw_eps_pwr_state_inst1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_inst1
    :field sw_eps_pwr_state_sband: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_sband
    :field sw_eps_pwr_state_uhf: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_uhf
    :field sw_eps_pwr_state_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_eps_pwr_state_adcs
    :field sw_time_since_rx: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_time_since_rx
    :field reusable_spare_7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_7
    :field reusable_spare_8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_8
    :field reusable_spare_9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_9
    :field reusable_spare_10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_10
    :field reusable_spare_11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_11
    :field reusable_spare_12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_12
    :field reusable_spare_13: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_13
    :field sw_bat_alive_state_battery0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_bat_alive_state_battery0
    :field sw_mode_clt_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_mode_clt_count
    :field sw_mode_system_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_mode_system_mode
    :field reusable_spare_14: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_14
    :field sw_sband_pa_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_sband_pa_temp
    :field sw_sband_pa_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_sband_pa_curr
    :field reusable_spare_15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_15
    :field sw_uhf_alive: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_uhf_alive
    :field sw_uhf_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_uhf_temp
    :field reusable_spare_16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_16
    :field sw_seq_state_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_state_auto
    :field sw_seq_state_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_state_op1
    :field sw_seq_state_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_state_op2
    :field sw_seq_state_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_state_op3
    :field sw_seq_stop_code_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_stop_code_auto
    :field sw_seq_stop_code_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_stop_code_op1
    :field sw_seq_stop_code_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_stop_code_op2
    :field sw_seq_stop_code_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_stop_code_op3
    :field sw_seq_exec_buf_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_exec_buf_auto
    :field sw_seq_exec_buf_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_exec_buf_op1
    :field sw_seq_exec_buf_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_exec_buf_op2
    :field sw_seq_exec_buf_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_seq_exec_buf_op3
    :field sw_store_partition_write_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_write_misc
    :field sw_store_partition_read_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_read_misc
    :field sw_store_partition_write_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_write_adcs
    :field sw_store_partition_read_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_read_adcs
    :field sw_store_partition_write_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_write_beacon
    :field sw_store_partition_read_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_read_beacon
    :field sw_store_partition_write_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_write_log
    :field sw_store_partition_read_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_read_log
    :field sw_store_partition_write_sci: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_write_sci
    :field sw_store_partition_read_sci: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_store_partition_read_sci
    :field sw_fp_resp_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_fp_resp_count
    :field sw_ana_bus_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_bus_v
    :field sw_ana_3p3_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_3p3_v
    :field sw_ana_2p5_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_2p5_v
    :field sw_ana_1p8_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_1p8_v
    :field sw_ana_1p0_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_1p0_v
    :field sw_ana_3p3_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_3p3_i
    :field sw_ana_1p8_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_1p8_i
    :field sw_ana_1p0_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_1p0_i
    :field sw_ana_cdh_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_cdh_temp
    :field sw_ana_cdh_3p3_ref: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_cdh_3p3_ref
    :field sw_ana_sa1_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sa1_v
    :field sw_ana_sa1_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sa1_i
    :field sw_ana_sa2_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sa2_v
    :field sw_ana_sa2_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sa2_i
    :field sw_ana_bat1_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_bat1_v
    :field sw_ana_eps_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_eps_temp
    :field sw_ana_eps_3p3_ref: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_eps_3p3_ref
    :field sw_ana_eps_bus_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_eps_bus_v
    :field sw_ana_eps_bus_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_eps_bus_i
    :field sw_ana_xact_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_xact_v
    :field sw_ana_xact_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_xact_i
    :field sw_ana_uhf_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_uhf_v
    :field sw_ana_uhf_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_uhf_i
    :field sw_ana_sband_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sband_v
    :field sw_ana_sband_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_sband_i
    :field sw_ana_axis1_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis1_volt
    :field sw_ana_axis1_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis1_curr
    :field sw_ana_axis2_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis2_volt
    :field sw_ana_axis2_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis2_curr
    :field sw_ana_axis3_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis3_volt
    :field sw_ana_axis3_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_axis3_curr
    :field sw_ana_afire_volt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_afire_volt
    :field sw_ana_afire_curr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_afire_curr
    :field sw_ana_ifb_therm1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_ana_ifb_therm1
    :field sw_adcs_alive: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_alive
    :field sw_adcs_eclipse: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_eclipse
    :field sw_adcs_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_att_valid
    :field sw_adcs_ref_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_ref_valid
    :field sw_adcs_time_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_time_valid
    :field sw_adcs_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_mode
    :field sw_adcs_recommend_sun_point: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_recommend_sun_point
    :field sw_adcs_sun_point_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_sun_point_state
    :field reusable_spare_17: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_17
    :field sw_adcs_analogs_voltage_2p5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_voltage_2p5
    :field sw_adcs_analogs_voltage_1p8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_voltage_1p8
    :field sw_adcs_analogs_voltage_1p0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_voltage_1p0
    :field sw_adcs_analogs_det_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_det_temp
    :field sw_adcs_analogs_motor1_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_motor1_temp
    :field sw_adcs_analogs_motor2_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_motor2_temp
    :field sw_adcs_analogs_motor3_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_motor3_temp
    :field sw_adcs_analogs_digital_bus_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_analogs_digital_bus_v
    :field sw_adcs_cmd_acpt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_cmd_acpt
    :field sw_adcs_cmd_fail: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_cmd_fail
    :field sw_adcs_sun_vec1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_sun_vec1
    :field sw_adcs_sun_vec2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_sun_vec2
    :field sw_adcs_sun_vec3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_sun_vec3
    :field sw_adcs_wheel_sp1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_wheel_sp1
    :field sw_adcs_wheel_sp2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_wheel_sp2
    :field sw_adcs_wheel_sp3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_wheel_sp3
    :field sw_adcs_body_rt1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_rt1
    :field sw_adcs_body_rt2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_rt2
    :field sw_adcs_body_rt3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_rt3
    :field sw_adcs_body_quat1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_quat1
    :field sw_adcs_body_quat2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_quat2
    :field sw_adcs_body_quat3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_quat3
    :field sw_adcs_body_quat4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_adcs_body_quat4
    :field des_met_time_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..des_met_time_seconds
    :field sw_im_id: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..sw_im_id
    :field payload_alive_axis1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..payload_alive_axis1
    :field payload_alive_axis2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..payload_alive_axis2
    :field payload_alive_axis3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..payload_alive_axis3
    :field payload_alive_afire: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..payload_alive_afire
    :field reusable_spare_18: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_18
    :field reusable_spare_18: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_19
    :field reusable_spare_18: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..reusable_spare_20
    :field reusable_spare_18: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field..checksum
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Aepex.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Aepex.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Aepex.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Aepex.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Aepex.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Aepex.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Aepex.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Aepex.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Aepex.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Aepex.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Aepex.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Aepex.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Aepex.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"APX   ") or (self.callsign == u"LASP  ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


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
            self.ax25_info = Aepex.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class DataSectionT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self._parent.packet_primary_header.secondary_header_flag:
                self._raw_secondary_header = self._io.read_bytes(6)
                _io__raw_secondary_header = KaitaiStream(BytesIO(self._raw_secondary_header))
                self.secondary_header = Aepex.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)

            _on = self._parent.packet_primary_header.application_process_id
            if _on == 1:
                self.user_data_field = Aepex.AepexSwStat(self._io, self, self._root)


    class SwStatT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sw_cmd_recv_count = self._io.read_u2be()
            self.sw_cmd_fmt_count = self._io.read_u2be()
            self.sw_cmd_rjct_count = self._io.read_u2be()
            self.sw_cmd_succ_count = self._io.read_u2be()
            self.padding1 = self._io.read_u2be()
            self.padding2 = self._io.read_u2be()
            self.sw_cmd_fail_code = self._io.read_u1()
            self.sw_cmd_xsum_state = self._io.read_u1()
            self.reusable_spare_1 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_2 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_3 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_4 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_5 = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_uhf = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_seq = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_dbg = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_6 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_inst4 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_inst3 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_inst2 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_inst1 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_sband = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_uhf = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_adcs = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sw_time_since_rx = self._io.read_u4be()
            self.reusable_spare_7 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_8 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_9 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_10 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_11 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_12 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_13 = self._io.read_bits_int_be(1) != 0
            self.sw_bat_alive_state_battery0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sw_mode_clt_count = self._io.read_u1()
            self.sw_mode_system_mode = self._io.read_u1()
            self.reusable_spare_14 = self._io.read_u1()
            self.sw_sband_pa_temp = self._io.read_u2be()
            self.sw_sband_pa_curr = self._io.read_u2be()
            self.reusable_spare_15 = self._io.read_u1()
            self.sw_uhf_alive = self._io.read_u1()
            self.sw_uhf_temp = self._io.read_s1()
            self.reusable_spare_16 = self._io.read_u1()
            self.sw_seq_state_auto = self._io.read_u1()
            self.sw_seq_state_op1 = self._io.read_u1()
            self.sw_seq_state_op2 = self._io.read_u1()
            self.sw_seq_state_op3 = self._io.read_u1()
            self.sw_seq_stop_code_auto = self._io.read_u1()
            self.sw_seq_stop_code_op1 = self._io.read_u1()
            self.sw_seq_stop_code_op2 = self._io.read_u1()
            self.sw_seq_stop_code_op3 = self._io.read_u1()
            self.sw_seq_exec_buf_auto = self._io.read_u2be()
            self.sw_seq_exec_buf_op1 = self._io.read_u2be()
            self.sw_seq_exec_buf_op2 = self._io.read_u2be()
            self.sw_seq_exec_buf_op3 = self._io.read_u2be()
            self.sw_store_partition_write_misc = self._io.read_u4be()
            self.sw_store_partition_read_misc = self._io.read_u4be()
            self.sw_store_partition_write_adcs = self._io.read_u4be()
            self.sw_store_partition_read_adcs = self._io.read_u4be()
            self.sw_store_partition_write_beacon = self._io.read_u4be()
            self.sw_store_partition_read_beacon = self._io.read_u4be()
            self.sw_store_partition_write_log = self._io.read_u4be()
            self.sw_store_partition_read_log = self._io.read_u4be()
            self.sw_store_partition_write_sci = self._io.read_u4be()
            self.sw_store_partition_read_sci = self._io.read_u4be()
            self.sw_fp_resp_count = self._io.read_u2be()
            self.sw_ana_bus_v = self._io.read_u2be()
            self.sw_ana_3p3_v = self._io.read_u2be()
            self.sw_ana_2p5_v = self._io.read_u2be()
            self.sw_ana_1p8_v = self._io.read_u2be()
            self.sw_ana_1p0_v = self._io.read_u2be()
            self.sw_ana_3p3_i = self._io.read_u2be()
            self.sw_ana_1p8_i = self._io.read_u2be()
            self.sw_ana_1p0_i = self._io.read_u2be()
            self.sw_ana_cdh_temp = self._io.read_u2be()
            self.sw_ana_cdh_3p3_ref = self._io.read_u2be()
            self.sw_ana_sa1_v = self._io.read_u2be()
            self.sw_ana_sa1_i = self._io.read_u2be()
            self.sw_ana_sa2_v = self._io.read_u2be()
            self.sw_ana_sa2_i = self._io.read_u2be()
            self.sw_ana_bat1_v = self._io.read_u2be()
            self.sw_ana_eps_temp = self._io.read_u2be()
            self.sw_ana_eps_3p3_ref = self._io.read_u2be()
            self.sw_ana_eps_bus_v = self._io.read_u2be()
            self.sw_ana_eps_bus_i = self._io.read_u2be()
            self.sw_ana_xact_v = self._io.read_u2be()
            self.sw_ana_xact_i = self._io.read_u2be()
            self.sw_ana_uhf_v = self._io.read_u2be()
            self.sw_ana_uhf_i = self._io.read_u2be()
            self.sw_ana_sband_v = self._io.read_u2be()
            self.sw_ana_sband_i = self._io.read_u2be()
            self.sw_ana_axis1_volt = self._io.read_u2be()
            self.sw_ana_axis1_curr = self._io.read_u2be()
            self.sw_ana_axis2_volt = self._io.read_u2be()
            self.sw_ana_axis2_curr = self._io.read_u2be()
            self.sw_ana_axis3_volt = self._io.read_u2be()
            self.sw_ana_axis3_curr = self._io.read_u2be()
            self.sw_ana_afire_volt = self._io.read_u2be()
            self.sw_ana_afire_curr = self._io.read_u2be()
            self.sw_ana_ifb_therm1 = self._io.read_u2be()
            self.sw_adcs_alive = self._io.read_u1()
            self.sw_adcs_eclipse = self._io.read_u1()
            self.sw_adcs_att_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_ref_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_time_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_mode = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_recommend_sun_point = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_sun_point_state = self._io.read_bits_int_be(3)
            self._io.align_to_byte()
            self.reusable_spare_17 = self._io.read_u1()
            self.sw_adcs_analogs_voltage_2p5 = self._io.read_u1()
            self.sw_adcs_analogs_voltage_1p8 = self._io.read_u1()
            self.sw_adcs_analogs_voltage_1p0 = self._io.read_u1()
            self.sw_adcs_analogs_det_temp = self._io.read_s1()
            self.sw_adcs_analogs_motor1_temp = self._io.read_s2be()
            self.sw_adcs_analogs_motor2_temp = self._io.read_s2be()
            self.sw_adcs_analogs_motor3_temp = self._io.read_s2be()
            self.sw_adcs_analogs_digital_bus_v = self._io.read_s2be()
            self.sw_adcs_cmd_acpt = self._io.read_u1()
            self.sw_adcs_cmd_fail = self._io.read_u1()
            self.sw_adcs_sun_vec1 = self._io.read_s2be()
            self.sw_adcs_sun_vec2 = self._io.read_s2be()
            self.sw_adcs_sun_vec3 = self._io.read_s2be()
            self.sw_adcs_wheel_sp1 = self._io.read_s2be()
            self.sw_adcs_wheel_sp2 = self._io.read_s2be()
            self.sw_adcs_wheel_sp3 = self._io.read_s2be()
            self.sw_adcs_body_rt1 = self._io.read_s4be()
            self.sw_adcs_body_rt2 = self._io.read_s4be()
            self.sw_adcs_body_rt3 = self._io.read_s4be()
            self.sw_adcs_body_quat1 = self._io.read_s4be()
            self.sw_adcs_body_quat2 = self._io.read_s4be()
            self.sw_adcs_body_quat3 = self._io.read_s4be()
            self.sw_adcs_body_quat4 = self._io.read_s4be()
            self.des_met_time_seconds = self._io.read_u4be()
            self.sw_im_id = self._io.read_u1()
            self.payload_alive_axis1 = self._io.read_u1()
            self.payload_alive_axis2 = self._io.read_u1()
            self.payload_alive_axis3 = self._io.read_u1()
            self.payload_alive_afire = self._io.read_u1()
            self.reusable_spare_18 = self._io.read_u1()
            self.reusable_spare_19 = self._io.read_u1()
            self.reusable_spare_20 = self._io.read_u1()
            self.checksum = self._io.read_u4be()


    class SecondaryHeaderT(KaitaiStruct):
        """The Secondary Header is a feature of the Space Packet which allows
        additional types of information that may be useful to the user
        application (e.g., a time code) to be included.
        See: 4.1.3.2 in CCSDS 133.0-B-1
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_stamp_seconds = self._io.read_u4be()
            self.sub_seconds = self._io.read_u2be()


    class PacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.is_stored_data = self._io.read_bits_int_be(1) != 0
            self.application_process_id = self._io.read_bits_int_be(10)
            self.grouping_flag = self._io.read_bits_int_be(2)
            self.sequence_count = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_length = self._io.read_u2be()


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
            self.callsign_ror = Aepex.Callsign(_io__raw_callsign_ror, self, self._root)


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Aepex.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Aepex.DataSectionT(self._io, self, self._root)


    class AepexSwStat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sw_stat_t = Aepex.SwStatT(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Aepex.CcsdsSpacePacketT(self._io, self, self._root)



