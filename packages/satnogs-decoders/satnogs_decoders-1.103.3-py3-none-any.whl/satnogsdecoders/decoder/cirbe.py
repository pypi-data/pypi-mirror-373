# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cirbe(KaitaiStruct):
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
    :field soh_l0_wdt_2sec_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_2sec_cnt
    :field soh_l0_reset_armed: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.reset_armed
    :field soh_l0_wdt_stat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_stat
    :field soh_l0_wdt_en: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.wdt_en
    :field soh_l0_table_select: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.table_select
    :field soh_l0_boot_relay: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.boot_relay
    :field soh_l0_l0_acpt_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.l0_acpt_cnt
    :field soh_l0_l0_rjct_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.l0_rjct_cnt
    :field soh_l0_hw_sec_cnt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.hw_sec_cnt
    :field soh_l0_time_tag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.time_tag
    :field soh_l0_spare_end: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_l0.spare_end
    :field soh_command_tlm_cmd_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.cmd_status
    :field soh_command_tlm_realtime_cmd_accept_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.realtime_cmd_accept_count
    :field soh_command_tlm_realtime_cmd_reject_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.realtime_cmd_reject_count
    :field soh_command_tlm_stored_cmd_accept_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.stored_cmd_accept_count
    :field soh_command_tlm_stored_cmd_reject_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_command_tlm.stored_cmd_reject_count
    :field soh_general_scrub_status_overall: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.scrub_status_overall
    :field soh_general_image_booted: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.image_booted
    :field soh_general_image_auto_failover: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.image_auto_failover
    :field soh_general_inertia_index: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_general.inertia_index
    :field soh_time_tai_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.tai_seconds
    :field soh_time_time_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.time_valid
    :field soh_time_health1_pack_spare2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.health1_pack_spare2
    :field soh_time_rtc_osc_rst_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.rtc_osc_rst_count
    :field soh_time_rtc_init_time_at_boot: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.rtc_init_time_at_boot
    :field soh_time_rtc_sync_stat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.rtc_sync_stat
    :field soh_time_rtc_alive: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.rtc_alive
    :field soh_time_rtc_power: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_time.rtc_power
    :field soh_refs_position_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci1
    :field soh_refs_position_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci2
    :field soh_refs_position_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.position_wrt_eci3
    :field soh_refs_velocity_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci1
    :field soh_refs_velocity_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci2
    :field soh_refs_velocity_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.velocity_wrt_eci3
    :field soh_refs_modeled_sun_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.modeled_sun_vector_body1
    :field soh_refs_modeled_sun_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.modeled_sun_vector_body2
    :field soh_refs_modeled_sun_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.modeled_sun_vector_body3
    :field soh_refs_mag_model_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.mag_model_vector_body1
    :field soh_refs_mag_model_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.mag_model_vector_body2
    :field soh_refs_mag_model_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.mag_model_vector_body3
    :field soh_refs_refs_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.refs_valid
    :field soh_refs_run_low_rate_task: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_refs.run_low_rate_task
    :field soh_att_det_q_body_wrt_eci1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci1
    :field soh_att_det_q_body_wrt_eci2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci2
    :field soh_att_det_q_body_wrt_eci3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci3
    :field soh_att_det_q_body_wrt_eci4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.q_body_wrt_eci4
    :field soh_att_det_tracker_sol_mixed: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.tracker_sol_mixed
    :field soh_att_det_tracker2_data_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.tracker2_data_valid
    :field soh_att_det_tracker1_data_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.tracker1_data_valid
    :field soh_att_det_imu_data_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.imu_data_valid
    :field soh_att_det_meas_rate_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.meas_rate_valid
    :field soh_att_det_meas_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.meas_att_valid
    :field soh_att_det_attitude_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_det.attitude_valid
    :field soh_att_cmd_hr_cycle_safe_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.hr_cycle_safe_mode
    :field soh_att_cmd_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.health1_pack_spare1
    :field soh_att_cmd_sun_point_reason: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.sun_point_reason
    :field soh_att_cmd_recommend_sun_point: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.recommend_sun_point
    :field soh_att_cmd_adcs_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_cmd.adcs_mode
    :field soh_rw_drive_filtered_speed_rpm1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm1
    :field soh_rw_drive_filtered_speed_rpm2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm2
    :field soh_rw_drive_filtered_speed_rpm3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_rw_drive.filtered_speed_rpm3
    :field soh_tracker_operating_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.operating_mode
    :field soh_tracker_star_id_step: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.star_id_step
    :field soh_tracker_att_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.att_status
    :field soh_tracker_num_attitude_stars: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker.num_attitude_stars
    :field soh_att_ctrl_eigen_error: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.eigen_error
    :field soh_att_ctrl_sun_point_angle_error: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.sun_point_angle_error
    :field soh_att_ctrl_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.health1_pack_spare1
    :field soh_att_ctrl_sun_source_failover: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.sun_source_failover
    :field soh_att_ctrl_sun_avoid_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.sun_avoid_flag
    :field soh_att_ctrl_on_sun_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.on_sun_flag
    :field soh_att_ctrl_momentum_too_high: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.momentum_too_high
    :field soh_att_ctrl_att_ctrl_active: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_att_ctrl.att_ctrl_active
    :field soh_momentum_total_momentum_mag: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.total_momentum_mag
    :field soh_momentum_duty_cycle1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle1
    :field soh_momentum_duty_cycle2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle2
    :field soh_momentum_duty_cycle3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.duty_cycle3
    :field soh_momentum_torque_rod_mode1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode1
    :field soh_momentum_torque_rod_mode2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode2
    :field soh_momentum_torque_rod_mode3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_mode3
    :field soh_momentum_torque_rod_firing_pack_spare: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_firing_pack_spare
    :field soh_momentum_torque_rod_direction3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_direction3
    :field soh_momentum_torque_rod_direction2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_direction2
    :field soh_momentum_torque_rod_direction1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_direction1
    :field soh_momentum_torque_rod_enable3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_enable3
    :field soh_momentum_torque_rod_enable2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_enable2
    :field soh_momentum_torque_rod_enable1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.torque_rod_enable1
    :field soh_momentum_health1_pack_spare2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.health1_pack_spare2
    :field soh_momentum_mag_source_failover: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.mag_source_failover
    :field soh_momentum_tr_fault: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.tr_fault
    :field soh_momentum_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.health1_pack_spare1
    :field soh_momentum_momentum_vector_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_enabled
    :field soh_momentum_momentum_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.momentum_vector_valid
    :field soh_momentum_tr_drive_power_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_momentum.tr_drive_power_state
    :field soh_css_sun_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body1
    :field soh_css_sun_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body2
    :field soh_css_sun_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_body3
    :field soh_css_sun_vector_status: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_status
    :field soh_css_css_invalid_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.css_invalid_count
    :field soh_css_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.health1_pack_spare1
    :field soh_css_sun_sensor_used: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_sensor_used
    :field soh_css_css_test_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.css_test_mode
    :field soh_css_sun_vector_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.sun_vector_enabled
    :field soh_css_meas_sun_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.meas_sun_valid
    :field soh_css_css_power_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_css.css_power_state
    :field soh_mag_mag_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body1
    :field soh_mag_mag_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body2
    :field soh_mag_mag_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_body3
    :field soh_mag_mag_invalid_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_invalid_count
    :field soh_mag_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.health1_pack_spare1
    :field soh_mag_mag_sensor_used: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_sensor_used
    :field soh_mag_mag_test_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_test_mode
    :field soh_mag_mag_vector_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_enabled
    :field soh_mag_mag_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_vector_valid
    :field soh_mag_mag_power_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_mag.mag_power_state
    :field soh_imu_imu_avg_vector_body1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body1
    :field soh_imu_imu_avg_vector_body1_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body1_dps
    :field soh_imu_imu_avg_vector_body1_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body1_rpm
    :field soh_imu_imu_avg_vector_body2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body2
    :field soh_imu_imu_avg_vector_body2_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body2_dps
    :field soh_imu_imu_avg_vector_body2_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body2_rpm
    :field soh_imu_imu_avg_vector_body3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body3
    :field soh_imu_imu_avg_vector_body3_dps: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body3_dps
    :field soh_imu_imu_avg_vector_body3_rpm: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_avg_vector_body3_rpm
    :field soh_imu_imu_invalid_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_invalid_count
    :field soh_imu_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.health1_pack_spare1
    :field soh_imu_imu_valid_packets: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_valid_packets
    :field soh_imu_imu_test_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_test_mode
    :field soh_imu_imu_vector_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_vector_enabled
    :field soh_imu_imu_vector_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_vector_valid
    :field soh_imu_imu_power_state: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_imu.imu_power_state
    :field soh_clock_sync_hr_run_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_run_count
    :field soh_clock_sync_hr_exec_time_ms1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms1
    :field soh_clock_sync_hr_exec_time_ms2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms2
    :field soh_clock_sync_hr_exec_time_ms3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms3
    :field soh_clock_sync_hr_exec_time_ms4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms4
    :field soh_clock_sync_hr_exec_time_ms5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_clock_sync.hr_exec_time_ms5
    :field soh_analogs_battery_voltage: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_analogs.battery_voltage
    :field soh_gps_gps_cycles_since_crc_data: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_cycles_since_crc_data
    :field soh_gps_gps_lock_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_lock_count
    :field soh_gps_msg_used_satellites: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.msg_used_satellites
    :field soh_gps_gps_pos_lock: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_pos_lock
    :field soh_gps_gps_time_lock: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_time_lock
    :field soh_gps_msg_data_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.msg_data_valid
    :field soh_gps_gps_new_data_received: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_new_data_received
    :field soh_gps_gps_enable: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_enable
    :field soh_gps_gps_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.gps_valid
    :field soh_gps_health1_pack_spare1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_gps.health1_pack_spare1
    :field soh_event_check_latched_resp_fire_pack_bit8: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit8
    :field soh_event_check_latched_resp_fire_pack_bit7: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit7
    :field soh_event_check_latched_resp_fire_pack_bit6: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit6
    :field soh_event_check_latched_resp_fire_pack_bit5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit5
    :field soh_event_check_latched_resp_fire_pack_bit4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit4
    :field soh_event_check_latched_resp_fire_pack_bit3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit3
    :field soh_event_check_latched_resp_fire_pack_bit2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit2
    :field soh_event_check_latched_resp_fire_pack_bit1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit1
    :field soh_event_check_latched_resp_fire_pack_bit16: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit16
    :field soh_event_check_latched_resp_fire_pack_bit15: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit15
    :field soh_event_check_latched_resp_fire_pack_bit14: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit14
    :field soh_event_check_latched_resp_fire_pack_bit13: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit13
    :field soh_event_check_latched_resp_fire_pack_bit12: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit12
    :field soh_event_check_latched_resp_fire_pack_bit11: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit11
    :field soh_event_check_latched_resp_fire_pack_bit10: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit10
    :field soh_event_check_latched_resp_fire_pack_bit9: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_event_check.latched_resp_fire_pack_bit9
    :field soh_radio_sd_minute_cur: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_minute_cur
    :field soh_radio_sd_percent_used_total: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_percent_used_total
    :field soh_radio_sd_ok: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_ok
    :field soh_radio_sd_fault_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sd_fault_count
    :field soh_radio_sq_channel: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_channel
    :field soh_radio_sq_trap_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_trap_count
    :field soh_radio_sq_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sq_temp
    :field soh_radio_sdr_tx_tx_frames: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_tx_frames
    :field soh_radio_sdr_tx_tx_power: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_tx_power
    :field soh_radio_sdr_tx_temp: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_temp
    :field soh_radio_sdr_tx_comm_error: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_radio.sdr_tx_comm_error
    :field soh_tracker_ctrl_tracker_att_valid: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.soh_tracker_ctrl.tracker_att_valid
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Cirbe.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Cirbe.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Cirbe.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Cirbe.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Cirbe.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Cirbe.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Cirbe.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Cirbe.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Cirbe.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Cirbe.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Cirbe.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Cirbe.SsidMask(self._io, self, self._root)
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
            self.ax25_info = Cirbe.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CIRBE ") or (self.callsign == u"BCT   ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class SohClockSyncT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hr_run_count = self._io.read_u4be()
            self.hr_exec_time_ms1 = self._io.read_u1()
            self.hr_exec_time_ms2 = self._io.read_u1()
            self.hr_exec_time_ms3 = self._io.read_u1()
            self.hr_exec_time_ms4 = self._io.read_u1()
            self.hr_exec_time_ms5 = self._io.read_u1()


    class SohAttCmdT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hr_cycle_safe_mode = self._io.read_u4be()
            self.health1_pack_spare1 = self._io.read_bits_int_be(1) != 0
            self.sun_point_reason = self._io.read_bits_int_be(3)
            self.recommend_sun_point = self._io.read_bits_int_be(1) != 0
            self.padding_0 = self._io.read_bits_int_be(2)
            self.adcs_mode = self._io.read_bits_int_be(1) != 0


    class SohTrackerCtrlT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tracker_att_valid = self._io.read_u1()


    class SohTimeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tai_seconds = self._io.read_f8be()
            self.time_valid = self._io.read_u1()
            self.health1_pack_spare2 = self._io.read_bits_int_be(1) != 0
            self.rtc_osc_rst_count = self._io.read_bits_int_be(3)
            self.rtc_init_time_at_boot = self._io.read_bits_int_be(1) != 0
            self.rtc_sync_stat = self._io.read_bits_int_be(1) != 0
            self.rtc_alive = self._io.read_bits_int_be(1) != 0
            self.rtc_power = self._io.read_bits_int_be(1) != 0


    class SohGpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gps_cycles_since_crc_data = self._io.read_u4be()
            self.gps_lock_count = self._io.read_u2be()
            self.msg_used_satellites = self._io.read_u1()
            self.gps_pos_lock = self._io.read_bits_int_be(1) != 0
            self.gps_time_lock = self._io.read_bits_int_be(1) != 0
            self.msg_data_valid = self._io.read_bits_int_be(1) != 0
            self.gps_new_data_received = self._io.read_bits_int_be(1) != 0
            self.padding_0 = self._io.read_bits_int_be(1) != 0
            self.gps_enable = self._io.read_bits_int_be(1) != 0
            self.gps_valid = self._io.read_bits_int_be(1) != 0
            self.health1_pack_spare1 = self._io.read_bits_int_be(1) != 0


    class SohRwDriveT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.filtered_speed_rpm1 = self._io.read_s2be()
            self.filtered_speed_rpm2 = self._io.read_s2be()
            self.filtered_speed_rpm3 = self._io.read_s2be()


    class SohAnalogsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_voltage = self._io.read_u2be()


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
            self.ax25_info = Cirbe.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class CirbeBctSohT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.soh_l0 = Cirbe.SohL0T(self._io, self, self._root)
            self.soh_command_tlm = Cirbe.SohCommandTlmT(self._io, self, self._root)
            self.soh_general = Cirbe.SohGeneralT(self._io, self, self._root)
            self.soh_time = Cirbe.SohTimeT(self._io, self, self._root)
            self.soh_refs = Cirbe.SohRefsT(self._io, self, self._root)
            self.soh_att_det = Cirbe.SohAttDetT(self._io, self, self._root)
            self.soh_att_cmd = Cirbe.SohAttCmdT(self._io, self, self._root)
            self.soh_rw_drive = Cirbe.SohRwDriveT(self._io, self, self._root)
            self.soh_tracker = Cirbe.SohTrackerT(self._io, self, self._root)
            self.soh_att_ctrl = Cirbe.SohAttCtrlT(self._io, self, self._root)
            self.soh_momentum = Cirbe.SohMomentumT(self._io, self, self._root)
            self.soh_css = Cirbe.SohCssT(self._io, self, self._root)
            self.soh_mag = Cirbe.SohMagT(self._io, self, self._root)
            self.soh_imu = Cirbe.SohImuT(self._io, self, self._root)
            self.soh_clock_sync = Cirbe.SohClockSyncT(self._io, self, self._root)
            self.soh_analogs = Cirbe.SohAnalogsT(self._io, self, self._root)
            self.soh_gps = Cirbe.SohGpsT(self._io, self, self._root)
            self.soh_event_check = Cirbe.SohEventCheckT(self._io, self, self._root)
            self.soh_radio = Cirbe.SohRadioT(self._io, self, self._root)
            self.soh_tracker_ctrl = Cirbe.SohTrackerCtrlT(self._io, self, self._root)


    class SohRadioT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sd_minute_cur = self._io.read_u4be()
            self.sd_percent_used_total = self._io.read_u1()
            self.sd_ok = self._io.read_u1()
            self.sd_fault_count = self._io.read_u1()
            self.sq_channel = self._io.read_s1()
            self.sq_trap_count = self._io.read_u1()
            self.sq_temp = self._io.read_s1()
            self.sdr_tx_tx_frames = self._io.read_u4be()
            self.sdr_tx_tx_power = self._io.read_s1()
            self.sdr_tx_temp = self._io.read_s1()
            self.sdr_tx_comm_error = self._io.read_u1()


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


    class SohTrackerT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.operating_mode = self._io.read_u1()
            self.star_id_step = self._io.read_u1()
            self.att_status = self._io.read_u1()
            self.num_attitude_stars = self._io.read_u1()


    class SohImuT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.imu_avg_vector_body1 = self._io.read_s2be()
            self.imu_avg_vector_body2 = self._io.read_s2be()
            self.imu_avg_vector_body3 = self._io.read_s2be()
            self.imu_invalid_count = self._io.read_u2be()
            self.health1_pack_spare1 = self._io.read_bits_int_be(3)
            self.imu_valid_packets = self._io.read_bits_int_be(1) != 0
            self.imu_test_mode = self._io.read_bits_int_be(1) != 0
            self.imu_vector_enabled = self._io.read_bits_int_be(1) != 0
            self.imu_vector_valid = self._io.read_bits_int_be(1) != 0
            self.imu_power_state = self._io.read_bits_int_be(1) != 0


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
                self.secondary_header = Cirbe.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)

            _on = self._parent.packet_primary_header.application_process_id
            if _on == 80:
                self.user_data_field = Cirbe.CirbeBctSohT(self._io, self, self._root)


    class SohMomentumT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.total_momentum_mag = self._io.read_u2be()
            self.duty_cycle1 = self._io.read_s1()
            self.duty_cycle2 = self._io.read_s1()
            self.duty_cycle3 = self._io.read_s1()
            self.torque_rod_mode1 = self._io.read_u1()
            self.torque_rod_mode2 = self._io.read_u1()
            self.torque_rod_mode3 = self._io.read_u1()
            self.torque_rod_firing_pack_spare = self._io.read_bits_int_be(1) != 0
            self.torque_rod_direction3 = self._io.read_bits_int_be(1) != 0
            self.torque_rod_direction2 = self._io.read_bits_int_be(1) != 0
            self.torque_rod_direction1 = self._io.read_bits_int_be(1) != 0
            self.padding_0 = self._io.read_bits_int_be(1) != 0
            self.torque_rod_enable3 = self._io.read_bits_int_be(1) != 0
            self.torque_rod_enable2 = self._io.read_bits_int_be(1) != 0
            self.torque_rod_enable1 = self._io.read_bits_int_be(1) != 0
            self.health1_pack_spare2 = self._io.read_bits_int_be(2)
            self.mag_source_failover = self._io.read_bits_int_be(1) != 0
            self.tr_fault = self._io.read_bits_int_be(1) != 0
            self.health1_pack_spare1 = self._io.read_bits_int_be(1) != 0
            self.momentum_vector_enabled = self._io.read_bits_int_be(1) != 0
            self.momentum_vector_valid = self._io.read_bits_int_be(1) != 0
            self.tr_drive_power_state = self._io.read_bits_int_be(1) != 0


    class SohCssT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sun_vector_body1 = self._io.read_s2be()
            self.sun_vector_body2 = self._io.read_s2be()
            self.sun_vector_body3 = self._io.read_s2be()
            self.sun_vector_status = self._io.read_u1()
            self.css_invalid_count = self._io.read_u2be()
            self.health1_pack_spare1 = self._io.read_bits_int_be(1) != 0
            self.sun_sensor_used = self._io.read_bits_int_be(3)
            self.css_test_mode = self._io.read_bits_int_be(1) != 0
            self.sun_vector_enabled = self._io.read_bits_int_be(1) != 0
            self.meas_sun_valid = self._io.read_bits_int_be(1) != 0
            self.css_power_state = self._io.read_bits_int_be(1) != 0


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
            self.sub_seconds = self._io.read_u1()
            self.padding = self._io.read_u1()


    class SohEventCheckT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.latched_resp_fire_pack_bit8 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit7 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit6 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit5 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit4 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit3 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit2 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit1 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit16 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit15 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit14 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit13 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit12 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit11 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit10 = self._io.read_bits_int_be(1) != 0
            self.latched_resp_fire_pack_bit9 = self._io.read_bits_int_be(1) != 0


    class SohMagT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mag_vector_body1 = self._io.read_s2be()
            self.mag_vector_body2 = self._io.read_s2be()
            self.mag_vector_body3 = self._io.read_s2be()
            self.mag_invalid_count = self._io.read_u2be()
            self.health1_pack_spare1 = self._io.read_bits_int_be(1) != 0
            self.mag_sensor_used = self._io.read_bits_int_be(3)
            self.mag_test_mode = self._io.read_bits_int_be(1) != 0
            self.mag_vector_enabled = self._io.read_bits_int_be(1) != 0
            self.mag_vector_valid = self._io.read_bits_int_be(1) != 0
            self.mag_power_state = self._io.read_bits_int_be(1) != 0


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
            self.callsign_ror = Cirbe.Callsign(_io__raw_callsign_ror, self, self._root)


    class SohGeneralT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.scrub_status_overall = self._io.read_s1()
            self.image_booted = self._io.read_u1()
            self.image_auto_failover = self._io.read_u1()
            self.inertia_index = self._io.read_u1()


    class SohAttCtrlT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eigen_error = self._io.read_u4be()
            self.sun_point_angle_error = self._io.read_u2be()
            self.health1_pack_spare1 = self._io.read_bits_int_be(2)
            self.sun_source_failover = self._io.read_bits_int_be(1) != 0
            self.sun_avoid_flag = self._io.read_bits_int_be(1) != 0
            self.padding_0 = self._io.read_bits_int_be(1) != 0
            self.on_sun_flag = self._io.read_bits_int_be(1) != 0
            self.momentum_too_high = self._io.read_bits_int_be(1) != 0
            self.att_ctrl_active = self._io.read_bits_int_be(1) != 0


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Cirbe.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Cirbe.DataSectionT(self._io, self, self._root)


    class SohL0T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.wdt_2sec_cnt = self._io.read_bits_int_be(3)
            self.reset_armed = self._io.read_bits_int_be(1) != 0
            self.wdt_stat = self._io.read_bits_int_be(1) != 0
            self.wdt_en = self._io.read_bits_int_be(1) != 0
            self.table_select = self._io.read_bits_int_be(1) != 0
            self.boot_relay = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.l0_acpt_cnt = self._io.read_u1()
            self.l0_rjct_cnt = self._io.read_u1()
            self.hw_sec_cnt = self._io.read_u1()
            self.padding_0 = self._io.read_u8be()
            self.time_tag = self._io.read_u4be()
            self.padding_1a = self._io.read_u8be()
            self.padding_1b = self._io.read_u2be()
            self.spare_end = self._io.read_u4be()
            self.spare_end_b = self._io.read_u2be()


    class SohRefsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.position_wrt_eci1 = self._io.read_s4be()
            self.position_wrt_eci2 = self._io.read_s4be()
            self.position_wrt_eci3 = self._io.read_s4be()
            self.velocity_wrt_eci1 = self._io.read_s4be()
            self.velocity_wrt_eci2 = self._io.read_s4be()
            self.velocity_wrt_eci3 = self._io.read_s4be()
            self.modeled_sun_vector_body1 = self._io.read_s2be()
            self.modeled_sun_vector_body2 = self._io.read_s2be()
            self.modeled_sun_vector_body3 = self._io.read_s2be()
            self.mag_model_vector_body1 = self._io.read_s2be()
            self.mag_model_vector_body2 = self._io.read_s2be()
            self.mag_model_vector_body3 = self._io.read_s2be()
            self.refs_valid = self._io.read_u1()
            self.run_low_rate_task = self._io.read_u1()


    class SohAttDetT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.q_body_wrt_eci1 = self._io.read_s4be()
            self.q_body_wrt_eci2 = self._io.read_s4be()
            self.q_body_wrt_eci3 = self._io.read_s4be()
            self.q_body_wrt_eci4 = self._io.read_s4be()
            self.tracker_sol_mixed = self._io.read_bits_int_be(1) != 0
            self.padding_0 = self._io.read_bits_int_be(1) != 0
            self.tracker2_data_valid = self._io.read_bits_int_be(1) != 0
            self.tracker1_data_valid = self._io.read_bits_int_be(1) != 0
            self.imu_data_valid = self._io.read_bits_int_be(1) != 0
            self.meas_rate_valid = self._io.read_bits_int_be(1) != 0
            self.meas_att_valid = self._io.read_bits_int_be(1) != 0
            self.attitude_valid = self._io.read_bits_int_be(1) != 0


    class SohCommandTlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd_status = self._io.read_u1()
            self.realtime_cmd_accept_count = self._io.read_u1()
            self.realtime_cmd_reject_count = self._io.read_u1()
            self.stored_cmd_accept_count = self._io.read_u1()
            self.stored_cmd_reject_count = self._io.read_u1()


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Cirbe.CcsdsSpacePacketT(self._io, self, self._root)



