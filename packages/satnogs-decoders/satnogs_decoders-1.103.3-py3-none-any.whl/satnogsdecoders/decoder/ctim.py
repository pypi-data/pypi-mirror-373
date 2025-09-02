# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Ctim(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign
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
    :field version: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.version
    :field type: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.type
    :field sec_hdr_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sec_hdr_flag
    :field pkt_apid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pkt_apid
    :field seq_flgs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.seq_flgs
    :field seq_ctr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.seq_ctr
    :field pkt_len: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pkt_len
    :field shcoarse: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.shcoarse
    :field shfine: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.shfine
    :field sw_major_version: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_major_version
    :field sw_minor_version: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_minor_version
    :field sw_patch_version: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_patch_version
    :field sw_image_id: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_image_id
    :field sw_cmd_recv_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_recv_count
    :field sw_cmd_fmt_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_fmt_count
    :field sw_cmd_rjct_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_rjct_count
    :field sw_cmd_succ_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_succ_count
    :field sw_cmd_succ_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_succ_op
    :field sw_cmd_rjct_op: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_rjct_op
    :field sw_cmd_fail_code: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_fail_code
    :field sw_cmd_xsum_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_xsum_state
    :field reusable_spare_1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_1
    :field reusable_spare_2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_2
    :field reusable_spare_3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_3
    :field reusable_spare_4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_4
    :field reusable_spare_5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_5
    :field sw_cmd_arm_state_uhf: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_arm_state_uhf
    :field sw_cmd_arm_state_seq: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_arm_state_seq
    :field sw_cmd_arm_state_ext: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_cmd_arm_state_ext
    :field reusable_spare_6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_6
    :field sw_eps_pwr_state_deploy_pwr: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_deploy_pwr
    :field sw_eps_pwr_state_deploy: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_deploy
    :field sw_eps_pwr_state_iic: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_iic
    :field sw_eps_pwr_state_inst: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_inst
    :field sw_eps_pwr_state_sband: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_sband
    :field sw_eps_pwr_state_uhf: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_uhf
    :field sw_eps_pwr_state_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_eps_pwr_state_adcs
    :field reusable_spare_7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_7
    :field reusable_spare_8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_8
    :field reusable_spare_9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_9
    :field reusable_spare_10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_10
    :field reusable_spare_11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_11
    :field reusable_spare_12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.reusable_spare_12
    :field sw_bat_alive_state_battery1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_bat_alive_state_battery1
    :field sw_bat_alive_state_battery0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_bat_alive_state_battery0
    :field sw_mode_clt_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_mode_clt_count
    :field sw_mode_system_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_mode_system_mode
    :field sw_sband_sync_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_sband_sync_state
    :field sw_time_since_rx: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_time_since_rx
    :field sw_sband_timeout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_sband_timeout
    :field spare_2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.spare_2
    :field sw_payload_pwr_cycle_req: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_payload_pwr_cycle_req
    :field sw_payload_pwr_off_req: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_payload_pwr_off_req
    :field sw_payload_stat_msg_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_payload_stat_msg_state
    :field sw_payload_time_msg_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_payload_time_msg_state
    :field sw_payload_alive_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_payload_alive_state
    :field sw_uhf_alive: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_uhf_alive
    :field sw_uhf_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_uhf_temp
    :field sw_adcs_alive: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_alive
    :field sw_inst_cmd_succ_count_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_inst_cmd_succ_count_ctim
    :field sw_inst_cmd_rjct_count_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_inst_cmd_rjct_count_ctim
    :field sw_esr_obs_id_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_esr_obs_id_ctim
    :field sw_thrm_a1_a_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_thrm_a1_a_ctim
    :field sw_thrm_a1_b_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_thrm_a1_b_ctim
    :field sw_fss_q1_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_fss_q1_ctim
    :field sw_fss_q2_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_fss_q2_ctim
    :field sw_fss_q3_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_fss_q3_ctim
    :field sw_fss_q4_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_fss_q4_ctim
    :field sw_volt_p12v_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_volt_p12v_ctim
    :field sw_thrm_pwm_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_thrm_pwm_ctim
    :field sw_inst_fp_resp_count_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_inst_fp_resp_count_ctim
    :field sw_shutter_state_b4_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_b4_ctim
    :field sw_shutter_state_b3_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_b3_ctim
    :field sw_shutter_state_b2_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_b2_ctim
    :field sw_shutter_state_b1_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_b1_ctim
    :field sw_shutter_state_a4_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_a4_ctim
    :field sw_shutter_state_a3_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_a3_ctim
    :field sw_shutter_state_a2_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_a2_ctim
    :field sw_shutter_state_a1_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_shutter_state_a1_ctim
    :field sw_inst_cmd_fail_code_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_inst_cmd_fail_code_ctim
    :field sw_esr_filtered_a12_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_esr_filtered_a12_ctim
    :field sw_esr_filtered_b12_ctim: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_esr_filtered_b12_ctim
    :field sw_seq_state_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_state_auto
    :field sw_seq_state_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_state_op1
    :field sw_seq_state_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_state_op2
    :field sw_seq_state_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_state_op3
    :field sw_seq_stop_code_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_stop_code_auto
    :field sw_seq_stop_code_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_stop_code_op1
    :field sw_seq_stop_code_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_stop_code_op2
    :field sw_seq_stop_code_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_stop_code_op3
    :field sw_seq_exec_buf_auto: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_exec_buf_auto
    :field sw_seq_exec_buf_op1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_exec_buf_op1
    :field sw_seq_exec_buf_op2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_exec_buf_op2
    :field sw_seq_exec_buf_op3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_seq_exec_buf_op3
    :field sw_store_partition_write_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_write_misc
    :field sw_store_partition_read_misc: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_read_misc
    :field sw_store_partition_write_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_write_adcs
    :field sw_store_partition_read_adcs: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_read_adcs
    :field sw_store_partition_write_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_write_beacon
    :field sw_store_partition_read_beacon: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_read_beacon
    :field sw_store_partition_write_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_write_log
    :field sw_store_partition_read_log: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_read_log
    :field sw_store_partition_write_payload: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_write_payload
    :field sw_store_partition_read_payload: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_store_partition_read_payload
    :field sw_fp_resp_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_fp_resp_count
    :field sw_ana_bus_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_bus_v
    :field sw_ana_3p3_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_3p3_v
    :field sw_ana_3p3_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_3p3_i
    :field sw_ana_1p8_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_1p8_i
    :field sw_ana_1p0_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_1p0_i
    :field sw_ana_cdh_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_cdh_temp
    :field sw_ana_sa1_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_sa1_v
    :field sw_ana_sa1_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_sa1_i
    :field sw_ana_sa2_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_sa2_v
    :field sw_ana_sa2_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_sa2_i
    :field sw_ana_bat1_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_bat1_v
    :field sw_ana_bat2_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_bat2_v
    :field sw_ana_eps_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_eps_temp
    :field sw_ana_eps_3p3_ref: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_eps_3p3_ref
    :field sw_ana_eps_bus_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_eps_bus_i
    :field sw_ana_xact_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_xact_i
    :field sw_ana_uhf_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_uhf_i
    :field sw_ana_sband_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_sband_i
    :field sw_ana_inst_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_inst_i
    :field sw_ana_hk_3p3_ref: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_hk_3p3_ref
    :field sw_ana_ifb_i: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_ifb_i
    :field sw_ana_ifb_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_ana_ifb_temp
    :field sw_adcs_eclipse: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_eclipse
    :field sw_adcs_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_att_valid
    :field sw_adcs_ref_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_ref_valid
    :field sw_adcs_time_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_time_valid
    :field sw_adcs_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_mode
    :field sw_adcs_recommend_sun_point: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_recommend_sun_point
    :field sw_adcs_sun_point_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_sun_point_state
    :field sw_adcs_analogs_voltage_2p5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_voltage_2p5
    :field sw_adcs_analogs_voltage_1p8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_voltage_1p8
    :field sw_adcs_analogs_voltage_1p0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_voltage_1p0
    :field sw_adcs_analogs_det_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_det_temp
    :field sw_adcs_analogs_motor1_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_motor1_temp
    :field sw_adcs_analogs_motor2_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_motor2_temp
    :field sw_adcs_analogs_motor3_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_motor3_temp
    :field spare_16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.spare_16
    :field sw_adcs_analogs_digital_bus_v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_analogs_digital_bus_v
    :field sw_adcs_cmd_acpt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_cmd_acpt
    :field sw_adcs_cmd_fail: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_cmd_fail
    :field sw_adcs_time: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_time
    :field sw_adcs_sun_vec1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_sun_vec1
    :field sw_adcs_sun_vec2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_sun_vec2
    :field sw_adcs_sun_vec3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_sun_vec3
    :field sw_adcs_wheel_sp1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_wheel_sp1
    :field sw_adcs_wheel_sp2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_wheel_sp2
    :field sw_adcs_wheel_sp3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_wheel_sp3
    :field sw_adcs_body_rt1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_rt1
    :field sw_adcs_body_rt2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_rt2
    :field sw_adcs_body_rt3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_rt3
    :field sw_adcs_body_quat1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_quat1
    :field sw_adcs_body_quat2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_quat2
    :field sw_adcs_body_quat3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_quat3
    :field sw_adcs_body_quat4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_adcs_body_quat4
    :field sw_spare_0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_spare_0
    :field sw_spare_1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_spare_1
    :field sw_spare_2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_spare_2
    :field sw_spare_3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.sw_spare_3
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Ctim.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Ctim.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Ctim.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Ctim.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Ctim.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Ctim.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Ctim.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Ctim.IFrame(self._io, self, self._root)


    class CtimSwStatT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sw_major_version = self._io.read_u1()
            self.sw_minor_version = self._io.read_u1()
            self.sw_patch_version = self._io.read_u1()
            self.sw_image_id = self._io.read_u1()
            self.sw_cmd_recv_count = self._io.read_u2be()
            self.sw_cmd_fmt_count = self._io.read_u2be()
            self.sw_cmd_rjct_count = self._io.read_u2be()
            self.sw_cmd_succ_count = self._io.read_u2be()
            self.sw_cmd_succ_op = self._io.read_u2be()
            self.sw_cmd_rjct_op = self._io.read_u2be()
            self.sw_cmd_fail_code = self._io.read_u1()
            self.sw_cmd_xsum_state = self._io.read_u1()
            self.reusable_spare_1 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_2 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_3 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_4 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_5 = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_uhf = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_seq = self._io.read_bits_int_be(1) != 0
            self.sw_cmd_arm_state_ext = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_6 = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_deploy_pwr = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_deploy = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_iic = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_inst = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_sband = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_uhf = self._io.read_bits_int_be(1) != 0
            self.sw_eps_pwr_state_adcs = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_7 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_8 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_9 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_10 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_11 = self._io.read_bits_int_be(1) != 0
            self.reusable_spare_12 = self._io.read_bits_int_be(1) != 0
            self.sw_bat_alive_state_battery1 = self._io.read_bits_int_be(1) != 0
            self.sw_bat_alive_state_battery0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sw_mode_clt_count = self._io.read_u1()
            self.sw_mode_system_mode = self._io.read_u1()
            self.sw_sband_sync_state = self._io.read_u1()
            self.sw_time_since_rx = self._io.read_u2be()
            self.sw_sband_timeout = self._io.read_u2be()
            self.spare_2 = self._io.read_bits_int_be(2)
            self.sw_payload_pwr_cycle_req = self._io.read_bits_int_be(1) != 0
            self.sw_payload_pwr_off_req = self._io.read_bits_int_be(1) != 0
            self.sw_payload_stat_msg_state = self._io.read_bits_int_be(1) != 0
            self.sw_payload_time_msg_state = self._io.read_bits_int_be(1) != 0
            self.sw_payload_alive_state = self._io.read_bits_int_be(2)
            self._io.align_to_byte()
            self.sw_uhf_alive = self._io.read_u1()
            self.sw_uhf_temp = self._io.read_s1()
            self.sw_adcs_alive = self._io.read_u1()
            self.sw_inst_cmd_succ_count_ctim = self._io.read_u2be()
            self.sw_inst_cmd_rjct_count_ctim = self._io.read_u1()
            self.sw_esr_obs_id_ctim = self._io.read_u1()
            self.sw_thrm_a1_a_ctim = self._io.read_u2be()
            self.sw_thrm_a1_b_ctim = self._io.read_u2be()
            self.sw_fss_q1_ctim = self._io.read_u2be()
            self.sw_fss_q2_ctim = self._io.read_u2be()
            self.sw_fss_q3_ctim = self._io.read_u2be()
            self.sw_fss_q4_ctim = self._io.read_u2be()
            self.sw_volt_p12v_ctim = self._io.read_u2be()
            self.sw_thrm_pwm_ctim = self._io.read_u2be()
            self.sw_inst_fp_resp_count_ctim = self._io.read_u2be()
            self.sw_shutter_state_b4_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_b3_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_b2_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_b1_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_a4_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_a3_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_a2_ctim = self._io.read_bits_int_be(1) != 0
            self.sw_shutter_state_a1_ctim = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.sw_inst_cmd_fail_code_ctim = self._io.read_u1()
            self.sw_esr_filtered_a12_ctim = self._io.read_f4be()
            self.sw_esr_filtered_b12_ctim = self._io.read_f4be()
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
            self.sw_store_partition_write_payload = self._io.read_u4be()
            self.sw_store_partition_read_payload = self._io.read_u4be()
            self.sw_fp_resp_count = self._io.read_u2be()
            self.sw_ana_bus_v = self._io.read_u2be()
            self.sw_ana_3p3_v = self._io.read_u2be()
            self.sw_ana_3p3_i = self._io.read_u2be()
            self.sw_ana_1p8_i = self._io.read_u2be()
            self.sw_ana_1p0_i = self._io.read_u2be()
            self.sw_ana_cdh_temp = self._io.read_u2be()
            self.sw_ana_sa1_v = self._io.read_u2be()
            self.sw_ana_sa1_i = self._io.read_u2be()
            self.sw_ana_sa2_v = self._io.read_u2be()
            self.sw_ana_sa2_i = self._io.read_u2be()
            self.sw_ana_bat1_v = self._io.read_u2be()
            self.sw_ana_bat2_v = self._io.read_u2be()
            self.sw_ana_eps_temp = self._io.read_u2be()
            self.sw_ana_eps_3p3_ref = self._io.read_u2be()
            self.sw_ana_eps_bus_i = self._io.read_u2be()
            self.sw_ana_xact_i = self._io.read_u2be()
            self.sw_ana_uhf_i = self._io.read_u2be()
            self.sw_ana_sband_i = self._io.read_u2be()
            self.sw_ana_inst_i = self._io.read_u2be()
            self.sw_ana_hk_3p3_ref = self._io.read_u2be()
            self.sw_ana_ifb_i = self._io.read_u2be()
            self.sw_ana_ifb_temp = self._io.read_u2be()
            self.sw_adcs_eclipse = self._io.read_u1()
            self.sw_adcs_att_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_ref_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_time_valid = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_mode = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_recommend_sun_point = self._io.read_bits_int_be(1) != 0
            self.sw_adcs_sun_point_state = self._io.read_bits_int_be(3)
            self._io.align_to_byte()
            self.sw_adcs_analogs_voltage_2p5 = self._io.read_u1()
            self.sw_adcs_analogs_voltage_1p8 = self._io.read_u1()
            self.sw_adcs_analogs_voltage_1p0 = self._io.read_u1()
            self.sw_adcs_analogs_det_temp = self._io.read_s1()
            self.sw_adcs_analogs_motor1_temp = self._io.read_s2be()
            self.sw_adcs_analogs_motor2_temp = self._io.read_s2be()
            self.sw_adcs_analogs_motor3_temp = self._io.read_s2be()
            self.spare_16 = self._io.read_s2be()
            self.sw_adcs_analogs_digital_bus_v = self._io.read_s2be()
            self.sw_adcs_cmd_acpt = self._io.read_u1()
            self.sw_adcs_cmd_fail = self._io.read_u1()
            self.sw_adcs_time = self._io.read_s4be()
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
            self.sw_spare_0 = self._io.read_u4be()
            self.sw_spare_1 = self._io.read_u4be()
            self.sw_spare_2 = self._io.read_u4be()
            self.sw_spare_3 = self._io.read_u4be()


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Ctim.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Ctim.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Ctim.Callsign(self._io, self, self._root)
            self.src_ssid_raw = Ctim.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Ctim.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CTIM\000\000") or (self.callsign == u"LASP\000\000")) :
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
            self.ax25_info = Ctim.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
            if self._parent.packet_primary_header.sec_hdr_flag:
                self._raw_secondary_header = self._io.read_bytes(6)
                _io__raw_secondary_header = KaitaiStream(BytesIO(self._raw_secondary_header))
                self.secondary_header = Ctim.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)

            _on = self._parent.packet_primary_header.pkt_apid
            if _on == 1:
                self.user_data_field = Ctim.CtimSwStatT(self._io, self, self._root)


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
            self.shcoarse = self._io.read_u4be()
            self.shfine = self._io.read_u2be()


    class PacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int_be(3)
            self.type = self._io.read_bits_int_be(1) != 0
            self.sec_hdr_flag = self._io.read_bits_int_be(1) != 0
            self.pkt_apid = self._io.read_bits_int_be(11)
            self.seq_flgs = self._io.read_bits_int_be(2)
            self.seq_ctr = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.pkt_len = self._io.read_u2be()


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
            self.callsign_ror = Ctim.Callsign(_io__raw_callsign_ror, self, self._root)


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Ctim.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Ctim.DataSectionT(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Ctim.CcsdsSpacePacketT(self._io, self, self._root)



