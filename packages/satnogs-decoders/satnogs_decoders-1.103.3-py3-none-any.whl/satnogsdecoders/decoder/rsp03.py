# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rsp03(KaitaiStruct):
    """## GMSK AX.25(w/G3RUH SatNOGS Default set)
    :field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.ax25_header.pid
    :field no001_header: ax25_frame.payload.no001_header
    #:field no001_header_1: ax25_frame.payload.no001_header_1
    :field no002_time: ax25_frame.payload.no002_time
    :field no003_time: ax25_frame.payload.no003_time
    :field packet_type: ax25_frame.payload.no004_packet_type.packet_type
    :field no005_telemetry_id: ax25_frame.payload.no004_packet_type.type_check.no005_telemetry_id
    :field no006_cobc_boot_count: ax25_frame.payload.no004_packet_type.type_check.no006_cobc_boot_count
    :field no007_cobc_elapsed_time: ax25_frame.payload.no004_packet_type.type_check.no007_cobc_elapsed_time
    :field no008_satellite_system_time: ax25_frame.payload.no004_packet_type.type_check.no008_satellite_system_time
    :field no009_cobc_temperature: ax25_frame.payload.no004_packet_type.type_check.no009_cobc_temperature
    :field no010_satellite_operation_mode: ax25_frame.payload.no004_packet_type.type_check.no010_satellite_operation_mode
    :field no011_antenna_deployment_status: ax25_frame.payload.no004_packet_type.type_check.no011_antenna_deployment_status
    :field no011_flag_0: ax25_frame.payload.no004_packet_type.type_check.no011_flag_0
    :field no011_flag_1: ax25_frame.payload.no004_packet_type.type_check.no011_flag_1
    :field no011_flag_2: ax25_frame.payload.no004_packet_type.type_check.no011_flag_2
    :field no011_flag_3: ax25_frame.payload.no004_packet_type.type_check.no011_flag_3
    :field no011_flag_4: ax25_frame.payload.no004_packet_type.type_check.no011_flag_4
    :field no011_flag_5: ax25_frame.payload.no004_packet_type.type_check.no011_flag_5
    :field no011_flag_6: ax25_frame.payload.no004_packet_type.type_check.no011_flag_6
    :field no011_flag_7: ax25_frame.payload.no004_packet_type.type_check.no011_flag_7
    
    :field no012_uplink_command_reception_count: ax25_frame.payload.no004_packet_type.type_check.no012_uplink_command_reception_count
    :field no013_cobc_temperature_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no013_cobc_temperature_upper_limit_exceed_count
    :field no014_cobc_temperature_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no014_cobc_temperature_lower_limit_exceed_count
    :field no015_cobc_voltage_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no015_cobc_voltage_upper_limit_exceed_count
    :field no016_cobc_voltage_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no016_cobc_voltage_lower_limit_exceed_count
    :field no017_cobc_current_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no017_cobc_current_upper_limit_exceed_count
    :field no018_cobc_current_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no018_cobc_current_lower_limit_exceed_count
    :field no019_main_radio_temperature_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no019_main_radio_temperature_upper_limit_exceed_count
    :field no020_main_radio_temperature_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no020_main_radio_temperature_lower_limit_exceed_count
    :field no021_main_radio_voltage_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no021_main_radio_voltage_upper_limit_exceed_count
    :field no022_main_radio_voltage_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no022_main_radio_voltage_lower_limit_exceed_count
    :field no023_main_radio_current_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no023_main_radio_current_upper_limit_exceed_count
    :field no024_main_radio_current_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no024_main_radio_current_lower_limit_exceed_count
    :field no025_sub_radio_temperature_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no025_sub_radio_temperature_upper_limit_exceed_count
    :field no026_sub_radio_temperature_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no026_sub_radio_temperature_lower_limit_exceed_count
    :field no027_sub_radio_voltage_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no027_sub_radio_voltage_upper_limit_exceed_count
    :field no028_sub_radio_voltage_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no028_sub_radio_voltage_lower_limit_exceed_count
    :field no029_sub_radio_current_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no029_sub_radio_current_upper_limit_exceed_count
    :field no030_sub_radio_current_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no030_sub_radio_current_lower_limit_exceed_count
    :field no031_aobc_temperature_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no031_aobc_temperature_upper_limit_exceed_count
    :field no032_aobc_temperature_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no032_aobc_temperature_lower_limit_exceed_count
    :field no033_aobc_voltage_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no033_aobc_voltage_upper_limit_exceed_count
    :field no034_aobc_voltage_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no034_aobc_voltage_lower_limit_exceed_count
    :field no035_aobc_current_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no035_aobc_current_upper_limit_exceed_count
    :field no036_aobc_current_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no036_aobc_current_lower_limit_exceed_count
    :field no037_mobc_temperature_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no037_mobc_temperature_upper_limit_exceed_count
    :field no038_mobc_temperature_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no038_mobc_temperature_lower_limit_exceed_count
    :field no039_mobc_voltage_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no039_mobc_voltage_upper_limit_exceed_count
    :field no040_mobc_voltage_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no040_mobc_voltage_lower_limit_exceed_count
    :field no041_mobc_current_upper_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no041_mobc_current_upper_limit_exceed_count
    :field no042_mobc_current_lower_limit_exceed_count: ax25_frame.payload.no004_packet_type.type_check.no042_mobc_current_lower_limit_exceed_count
    :field no043_magnetic_torque_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no043_magnetic_torque_consumption_current
    :field no044_reaction_wheel_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no044_reaction_wheel_consumption_current
    :field no045_antenna_deployment_heater_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no045_antenna_deployment_heater_consumption_current
    :field no046_main_radio_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no046_main_radio_consumption_current
    :field no047_sub_radio_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no047_sub_radio_consumption_current
    :field no048_mobc_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no048_mobc_consumption_current
    :field no049_cobc_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no049_cobc_consumption_current
    :field no050_aobc_consumption_current: ax25_frame.payload.no004_packet_type.type_check.no050_aobc_consumption_current
    :field no051_5v_bus_voltage: ax25_frame.payload.no004_packet_type.type_check.no051_5v_bus_voltage
    :field no052_33v_line_voltage: ax25_frame.payload.no004_packet_type.type_check.no052_33v_line_voltage
    :field no053_bus_current: ax25_frame.payload.no004_packet_type.type_check.no053_bus_current
    :field no054_sap_z_face_voltage: ax25_frame.payload.no004_packet_type.type_check.no054_sap_z_face_voltage
    :field no055_sap_z_face_temperature: ax25_frame.payload.no004_packet_type.type_check.no055_sap_z_face_temperature
    :field no056_sap__z_face_voltage: ax25_frame.payload.no004_packet_type.type_check.no056_sap__z_face_voltage
    :field no057_sap__z_face_temperature: ax25_frame.payload.no004_packet_type.type_check.no057_sap__z_face_temperature
    :field no058_sap_y_face_voltage: ax25_frame.payload.no004_packet_type.type_check.no058_sap_y_face_voltage
    :field no059_sap_y_face_temperature: ax25_frame.payload.no004_packet_type.type_check.no059_sap_y_face_temperature
    :field no060_sap__x_face_voltage: ax25_frame.payload.no004_packet_type.type_check.no060_sap__x_face_voltage
    :field no061_sap__x_face_temperature: ax25_frame.payload.no004_packet_type.type_check.no061_sap__x_face_temperature
    :field no062_sap__y_face_voltage: ax25_frame.payload.no004_packet_type.type_check.no062_sap__y_face_voltage
    :field no063_sap__y_face_temperature: ax25_frame.payload.no004_packet_type.type_check.no063_sap__y_face_temperature
    :field no064_sap_z_face_current: ax25_frame.payload.no004_packet_type.type_check.no064_sap_z_face_current
    :field no065_sap__z_face_current: ax25_frame.payload.no004_packet_type.type_check.no065_sap__z_face_current
    :field no066_sap_y_face_current: ax25_frame.payload.no004_packet_type.type_check.no066_sap_y_face_current
    :field no067_sap__x_face_current: ax25_frame.payload.no004_packet_type.type_check.no067_sap__x_face_current
    :field no068_sap__y_face_current: ax25_frame.payload.no004_packet_type.type_check.no068_sap__y_face_current
    :field no069_battery_1_output_voltage: ax25_frame.payload.no004_packet_type.type_check.no069_battery_1_output_voltage
    :field no070_battery_1_charging_current: ax25_frame.payload.no004_packet_type.type_check.no070_battery_1_charging_current
    :field no071_battery_1_discharging_current: ax25_frame.payload.no004_packet_type.type_check.no071_battery_1_discharging_current
    :field no072_battery_1_temperature: ax25_frame.payload.no004_packet_type.type_check.no072_battery_1_temperature
    :field no073_battery_1_cumulative_charge: ax25_frame.payload.no004_packet_type.type_check.no073_battery_1_cumulative_charge
    :field no074_battery_1_cumulative_discharge: ax25_frame.payload.no004_packet_type.type_check.no074_battery_1_cumulative_discharge
    :field no075_battery_2_output_voltage: ax25_frame.payload.no004_packet_type.type_check.no075_battery_2_output_voltage
    :field no076_battery_2_charging_current: ax25_frame.payload.no004_packet_type.type_check.no076_battery_2_charging_current
    :field no077_battery_2_discharging_current: ax25_frame.payload.no004_packet_type.type_check.no077_battery_2_discharging_current
    :field no078_battery_2_temperature: ax25_frame.payload.no004_packet_type.type_check.no078_battery_2_temperature
    :field no079_battery_2_cumulative_charge: ax25_frame.payload.no004_packet_type.type_check.no079_battery_2_cumulative_charge
    :field no080_battery_2_cumulative_discharge: ax25_frame.payload.no004_packet_type.type_check.no080_battery_2_cumulative_discharge
    :field no081_equipment_power_anomaly_status: ax25_frame.payload.no004_packet_type.type_check.no081_equipment_power_anomaly_status
    :field no081_flag_0: ax25_frame.payload.no004_packet_type.type_check.no081_flag_0
    :field no081_flag_1: ax25_frame.payload.no004_packet_type.type_check.no081_flag_1
    :field no081_flag_2: ax25_frame.payload.no004_packet_type.type_check.no081_flag_2
    :field no081_flag_3: ax25_frame.payload.no004_packet_type.type_check.no081_flag_3
    :field no081_flag_4: ax25_frame.payload.no004_packet_type.type_check.no081_flag_4
    :field no081_flag_5: ax25_frame.payload.no004_packet_type.type_check.no081_flag_5
    :field no081_flag_6: ax25_frame.payload.no004_packet_type.type_check.no081_flag_6
    :field no081_flag_7: ax25_frame.payload.no004_packet_type.type_check.no081_flag_7
    
    :field no082_equipment_power_status: ax25_frame.payload.no004_packet_type.type_check.no082_equipment_power_status
    :field no082_flag_0: ax25_frame.payload.no004_packet_type.type_check.no082_flag_0
    :field no082_flag_1: ax25_frame.payload.no004_packet_type.type_check.no082_flag_1
    :field no082_flag_2: ax25_frame.payload.no004_packet_type.type_check.no082_flag_2
    :field no082_flag_3: ax25_frame.payload.no004_packet_type.type_check.no082_flag_3
    :field no082_flag_4: ax25_frame.payload.no004_packet_type.type_check.no082_flag_4
    :field no082_flag_5: ax25_frame.payload.no004_packet_type.type_check.no082_flag_5
    :field no082_flag_6: ax25_frame.payload.no004_packet_type.type_check.no082_flag_6
    :field no082_flag_7: ax25_frame.payload.no004_packet_type.type_check.no082_flag_7
    
    :field no083_mppt_status: ax25_frame.payload.no004_packet_type.type_check.no083_mppt_status
    :field no083_flag_0: ax25_frame.payload.no004_packet_type.type_check.no083_flag_0
    :field no083_flag_1: ax25_frame.payload.no004_packet_type.type_check.no083_flag_1
    :field no083_flag_2: ax25_frame.payload.no004_packet_type.type_check.no083_flag_2
    :field no083_flag_3: ax25_frame.payload.no004_packet_type.type_check.no083_flag_3
    :field no083_flag_4: ax25_frame.payload.no004_packet_type.type_check.no083_flag_4
    :field no083_flag_5: ax25_frame.payload.no004_packet_type.type_check.no083_flag_5
    :field no083_flag_6: ax25_frame.payload.no004_packet_type.type_check.no083_flag_6
    :field no083_flag_7: ax25_frame.payload.no004_packet_type.type_check.no083_flag_7
    
    :field no084_battery_chargedischarge_controller_status: ax25_frame.payload.no004_packet_type.type_check.no084_battery_chargedischarge_controller_status
    :field no084_flag_0: ax25_frame.payload.no004_packet_type.type_check.no084_flag_0
    :field no084_flag_1: ax25_frame.payload.no004_packet_type.type_check.no084_flag_1
    :field no084_flag_2: ax25_frame.payload.no004_packet_type.type_check.no084_flag_2
    :field no084_flag_3: ax25_frame.payload.no004_packet_type.type_check.no084_flag_3
    :field no084_flag_4: ax25_frame.payload.no004_packet_type.type_check.no084_flag_4
    :field no084_flag_5: ax25_frame.payload.no004_packet_type.type_check.no084_flag_5
    :field no084_flag_6: ax25_frame.payload.no004_packet_type.type_check.no084_flag_6
    :field no084_flag_7: ax25_frame.payload.no004_packet_type.type_check.no084_flag_7
    
    :field no085_internal_equipment_communication_error_status: ax25_frame.payload.no004_packet_type.type_check.no085_internal_equipment_communication_error_status
    :field no085_flag_0: ax25_frame.payload.no004_packet_type.type_check.no085_flag_0
    :field no085_flag_1: ax25_frame.payload.no004_packet_type.type_check.no085_flag_1
    :field no085_flag_2: ax25_frame.payload.no004_packet_type.type_check.no085_flag_2
    :field no085_flag_3: ax25_frame.payload.no004_packet_type.type_check.no085_flag_3
    :field no085_flag_4: ax25_frame.payload.no004_packet_type.type_check.no085_flag_4
    :field no085_flag_5: ax25_frame.payload.no004_packet_type.type_check.no085_flag_5
    :field no085_flag_6: ax25_frame.payload.no004_packet_type.type_check.no085_flag_6
    :field no085_flag_7: ax25_frame.payload.no004_packet_type.type_check.no085_flag_7
    
    :field no086_main_radio_boot_count: ax25_frame.payload.no004_packet_type.type_check.no086_main_radio_boot_count
    :field no087_main_radio_elapsed_time: ax25_frame.payload.no004_packet_type.type_check.no087_main_radio_elapsed_time
    :field no088_main_radio_no_reception_time: ax25_frame.payload.no004_packet_type.type_check.no088_main_radio_no_reception_time
    :field no089_main_radio_rssi: ax25_frame.payload.no004_packet_type.type_check.no089_main_radio_rssi
    :field no090_main_radio_uplink_reception_counter: ax25_frame.payload.no004_packet_type.type_check.no090_main_radio_uplink_reception_counter
    :field no091_main_radio_uplink_modulation: ax25_frame.payload.no004_packet_type.type_check.no091_main_radio_uplink_modulation
    :field no092_main_radio_downlink_modulation: ax25_frame.payload.no004_packet_type.type_check.no092_main_radio_downlink_modulation
    :field no093_main_radio_downlink_protocol: ax25_frame.payload.no004_packet_type.type_check.no093_main_radio_downlink_protocol
    :field no094_main_radio_frequency_lock: ax25_frame.payload.no004_packet_type.type_check.no094_main_radio_frequency_lock
    :field no095_main_radio_pa_temperature: ax25_frame.payload.no004_packet_type.type_check.no095_main_radio_pa_temperature
    :field no096_main_radio_pa_current: ax25_frame.payload.no004_packet_type.type_check.no096_main_radio_pa_current
    :field no097_main_radio_mcu_temperature_: ax25_frame.payload.no004_packet_type.type_check.no097_main_radio_mcu_temperature_
    :field no098_sub_radio_boot_count: ax25_frame.payload.no004_packet_type.type_check.no098_sub_radio_boot_count
    :field no099_sub_radio_elapsed_time: ax25_frame.payload.no004_packet_type.type_check.no099_sub_radio_elapsed_time
    :field no100_sub_radio_no_reception_time: ax25_frame.payload.no004_packet_type.type_check.no100_sub_radio_no_reception_time
    :field no101_sub_radio_rssi: ax25_frame.payload.no004_packet_type.type_check.no101_sub_radio_rssi
    :field no102_sub_radio_uplink_reception_counter: ax25_frame.payload.no004_packet_type.type_check.no102_sub_radio_uplink_reception_counter
    :field no103_sub_radio_uplink_modulation: ax25_frame.payload.no004_packet_type.type_check.no103_sub_radio_uplink_modulation
    :field no104_sub_radio_downlink_modulation: ax25_frame.payload.no004_packet_type.type_check.no104_sub_radio_downlink_modulation
    :field no105_sub_radio_downlink_protocol: ax25_frame.payload.no004_packet_type.type_check.no105_sub_radio_downlink_protocol
    :field no106_sub_radio_frequency_lock: ax25_frame.payload.no004_packet_type.type_check.no106_sub_radio_frequency_lock
    :field no107_sub_radio_pa_temperature: ax25_frame.payload.no004_packet_type.type_check.no107_sub_radio_pa_temperature
    :field no108_sub_radio_pa_current: ax25_frame.payload.no004_packet_type.type_check.no108_sub_radio_pa_current
    :field no109_sub_radio_mcu_temperature: ax25_frame.payload.no004_packet_type.type_check.no109_sub_radio_mcu_temperature
    
    # :field no005_telemetry_id: ax25_frame.payload.no004_packet_type.type_check.no005_telemetry_id
    :field no006_cobc_uptime_: ax25_frame.payload.no004_packet_type.type_check.no006_cobc_uptime_
    :field no007_satellite_system_time: ax25_frame.payload.no004_packet_type.type_check.no007_satellite_system_time
    :field no008_mission_command_execution_result: ax25_frame.payload.no004_packet_type.type_check.no008_mission_command_execution_result
    :field no009_mission_command_execution_result_details: ax25_frame.payload.no004_packet_type.type_check.no009_mission_command_execution_result_details
    :field no010_os_time_at_telemetry_generation: ax25_frame.payload.no004_packet_type.type_check.no010_os_time_at_telemetry_generation
    :field no011_system_time_at_telemetry_generation: ax25_frame.payload.no004_packet_type.type_check.no011_system_time_at_telemetry_generation
    :field no012_mobc_temperature: ax25_frame.payload.no004_packet_type.type_check.no012_mobc_temperature
    :field no013_composition_system_status: ax25_frame.payload.no004_packet_type.type_check.no013_composition_system_status
    :field no014_stt_status: ax25_frame.payload.no004_packet_type.type_check.no014_stt_status
    :field no015_right_ascension_last_acquired_by_stt: ax25_frame.payload.no004_packet_type.type_check.no015_right_ascension_last_acquired_by_stt
    :field no016_declination_last_acquired_by_stt: ax25_frame.payload.no004_packet_type.type_check.no016_declination_last_acquired_by_stt
    :field no017_roll_angle_last_acquired_by_stt: ax25_frame.payload.no004_packet_type.type_check.no017_roll_angle_last_acquired_by_stt
    :field no018_validity_of_acquired_coordinates: ax25_frame.payload.no004_packet_type.type_check.no018_validity_of_acquired_coordinates
    :field no019_image_capture_time: ax25_frame.payload.no004_packet_type.type_check.no019_image_capture_time
    :field no020_most_recent_command_id_1: ax25_frame.payload.no004_packet_type.type_check.no020_most_recent_command_id_1
    :field no021_most_recent_command_result_1: ax25_frame.payload.no004_packet_type.type_check.no021_most_recent_command_result_1
    :field no022_most_recent_command_result_detail_1: ax25_frame.payload.no004_packet_type.type_check.no022_most_recent_command_result_detail_1
    :field no023_most_recent_command_id_2: ax25_frame.payload.no004_packet_type.type_check.no023_most_recent_command_id_2
    :field no024_most_recent_command_result_2: ax25_frame.payload.no004_packet_type.type_check.no024_most_recent_command_result_2
    :field no025_most_recent_command_result_detail_2: ax25_frame.payload.no004_packet_type.type_check.no025_most_recent_command_result_detail_2
    :field no026_most_recent_command_id_3: ax25_frame.payload.no004_packet_type.type_check.no026_most_recent_command_id_3
    :field no027_most_recent_command_result_3: ax25_frame.payload.no004_packet_type.type_check.no027_most_recent_command_result_3
    :field no028_most_recent_command_result_detail_3: ax25_frame.payload.no004_packet_type.type_check.no028_most_recent_command_result_detail_3
    # :field no005_telemetry_id: ax25_frame.payload.no004_packet_type.type_check.no005_telemetry_id
    :field no006_cobc_uptime: ax25_frame.payload.no004_packet_type.type_check.no006_cobc_uptime
    :field no007_satellite_system_time: ax25_frame.payload.no004_packet_type.type_check.no007_satellite_system_time
    :field no008_telemetry_type: ax25_frame.payload.no004_packet_type.type_check.no008_telemetry_type
    :field no009_attitude_control_mode: ax25_frame.payload.no004_packet_type.type_check.no009_attitude_control_mode
    :field no010_ground_packet_reception_count: ax25_frame.payload.no004_packet_type.type_check.no010_ground_packet_reception_count
    :field no011_x_axis_rw_mode: ax25_frame.payload.no004_packet_type.type_check.no011_x_axis_rw_mode
    :field no012_x_axis_rw_speed: ax25_frame.payload.no004_packet_type.type_check.no012_x_axis_rw_speed
    :field no013_x_axis_rw_status: ax25_frame.payload.no004_packet_type.type_check.no013_x_axis_rw_status
    :field no014_y_axis_rw_mode: ax25_frame.payload.no004_packet_type.type_check.no014_y_axis_rw_mode
    :field no015_y_axis_rw_speed: ax25_frame.payload.no004_packet_type.type_check.no015_y_axis_rw_speed
    :field no016_y_axis_rw_status: ax25_frame.payload.no004_packet_type.type_check.no016_y_axis_rw_status
    :field no017_z_axis_rw_mode: ax25_frame.payload.no004_packet_type.type_check.no017_z_axis_rw_mode
    :field no018_z_axis_rw_speed: ax25_frame.payload.no004_packet_type.type_check.no018_z_axis_rw_speed
    :field no019_z_axis_rw_status: ax25_frame.payload.no004_packet_type.type_check.no019_z_axis_rw_status
    :field no020_x_axis_mtq_mode: ax25_frame.payload.no004_packet_type.type_check.no020_x_axis_mtq_mode
    :field no021_x_axis_mtq_set_voltage: ax25_frame.payload.no004_packet_type.type_check.no021_x_axis_mtq_set_voltage
    :field no022_x_axis_mtq_status: ax25_frame.payload.no004_packet_type.type_check.no022_x_axis_mtq_status
    :field no023_y_axis_mtq_mode: ax25_frame.payload.no004_packet_type.type_check.no023_y_axis_mtq_mode
    :field no024_y_axis_mtq_set_voltage: ax25_frame.payload.no004_packet_type.type_check.no024_y_axis_mtq_set_voltage
    :field no025_y_axis_mtq_status: ax25_frame.payload.no004_packet_type.type_check.no025_y_axis_mtq_status
    :field no026_z_axis_mtq_mode: ax25_frame.payload.no004_packet_type.type_check.no026_z_axis_mtq_mode
    :field no027_z_axis_mtq_set_voltage: ax25_frame.payload.no004_packet_type.type_check.no027_z_axis_mtq_set_voltage
    :field no028_z_axis_mtq_status: ax25_frame.payload.no004_packet_type.type_check.no028_z_axis_mtq_status
    :field no029_imu1_x_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no029_imu1_x_axis_acceleration
    :field no030_imu1_y_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no030_imu1_y_axis_acceleration
    :field no031_imu1_z_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no031_imu1_z_axis_acceleration
    :field no032_imu1_x_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no032_imu1_x_axis_angular_velocity
    :field no033_imu1_y_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no033_imu1_y_axis_angular_velocity
    :field no034_imu1_z_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no034_imu1_z_axis_angular_velocity
    :field no035_imu1_x_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no035_imu1_x_axis_magnetic_field
    :field no036_imu1_y_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no036_imu1_y_axis_magnetic_field
    :field no037_imu1_z_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no037_imu1_z_axis_magnetic_field
    :field no038_imu1_temperature: ax25_frame.payload.no004_packet_type.type_check.no038_imu1_temperature
    :field no039_imu1_status: ax25_frame.payload.no004_packet_type.type_check.no039_imu1_status
    :field no040_imu2_x_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no040_imu2_x_axis_acceleration
    :field no041_imu2_y_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no041_imu2_y_axis_acceleration
    :field no042_imu2_z_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no042_imu2_z_axis_acceleration
    :field no043_imu2_x_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no043_imu2_x_axis_angular_velocity
    :field no044_imu2_y_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no044_imu2_y_axis_angular_velocity
    :field no045_imu2_z_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no045_imu2_z_axis_angular_velocity
    :field no046_imu2_x_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no046_imu2_x_axis_magnetic_field
    :field no047_imu2_y_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no047_imu2_y_axis_magnetic_field
    :field no048_imu2_z_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no048_imu2_z_axis_magnetic_field
    :field no049_imu2_temperature: ax25_frame.payload.no004_packet_type.type_check.no049_imu2_temperature
    :field no050_imu2_status: ax25_frame.payload.no004_packet_type.type_check.no050_imu2_status
    :field no051_imu3_x_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no051_imu3_x_axis_acceleration
    :field no052_imu3_y_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no052_imu3_y_axis_acceleration
    :field no053_imu3_z_axis_acceleration: ax25_frame.payload.no004_packet_type.type_check.no053_imu3_z_axis_acceleration
    :field no054_imu3_x_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no054_imu3_x_axis_angular_velocity
    :field no055_imu3_y_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no055_imu3_y_axis_angular_velocity
    :field no056_imu3_z_axis_angular_velocity: ax25_frame.payload.no004_packet_type.type_check.no056_imu3_z_axis_angular_velocity
    :field no057_imu3_x_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no057_imu3_x_axis_magnetic_field
    :field no058_imu3_y_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no058_imu3_y_axis_magnetic_field
    :field no059_imu3_z_axis_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no059_imu3_z_axis_magnetic_field
    :field no060_imu3_temperature: ax25_frame.payload.no004_packet_type.type_check.no060_imu3_temperature
    :field no061_imu3_status: ax25_frame.payload.no004_packet_type.type_check.no061_imu3_status
    :field no062_x_axis_rw_proportional_gain: ax25_frame.payload.no004_packet_type.type_check.no062_x_axis_rw_proportional_gain
    :field no063_x_axis_rw_derivative_gain: ax25_frame.payload.no004_packet_type.type_check.no063_x_axis_rw_derivative_gain
    :field no064_y_axis_rw_proportional_gain: ax25_frame.payload.no004_packet_type.type_check.no064_y_axis_rw_proportional_gain
    :field no065_y_axis_rw_derivative_gain: ax25_frame.payload.no004_packet_type.type_check.no065_y_axis_rw_derivative_gain
    :field no066_z_axis_rw_proportional_gain: ax25_frame.payload.no004_packet_type.type_check.no066_z_axis_rw_proportional_gain
    :field no067_z_axis_rw_derivative_gain: ax25_frame.payload.no004_packet_type.type_check.no067_z_axis_rw_derivative_gain
    :field no068_commissioning_runtime_: ax25_frame.payload.no004_packet_type.type_check.no068_commissioning_runtime_
    :field no069_imu_fault_detection_threshold: ax25_frame.payload.no004_packet_type.type_check.no069_imu_fault_detection_threshold
    :field no070_active_imu: ax25_frame.payload.no004_packet_type.type_check.no070_active_imu
    :field no071_bdot_control_voltage: ax25_frame.payload.no004_packet_type.type_check.no071_bdot_control_voltage
    :field no072_bdot_reference_magnetic_field: ax25_frame.payload.no004_packet_type.type_check.no072_bdot_reference_magnetic_field
    
    # CW-related fields for Grafana/InfluxDB export
    :field cw_beacon: ax25_frame.cw_beacon
    :field cw_type: ax25_frame.cw_type
    
    # ---------- CW 'G' (ASCII beacon) ----------
    :field cw_g_no001_Message_Identifier: ax25_frame.no001_message_identifier
    :field cw_g_no002_Telemetry_Type: ax25_frame.no002_telemetry_type_value
    :field cw_g_no003_COBC_Boot_Count: ax25_frame.no003_cobc_boot_count_value
    :field cw_g_no004_COBC_Uptime_seconds: ax25_frame.no004_cobc_uptime_seconds_value
    :field cw_g_no005_COBC_Temperature_c: ax25_frame.no005_cobc_temperature_degc_value
    :field cw_g_no006_Satellite_Operation_Mode: ax25_frame.no006_satellite_operation_mode_value
    :field cw_g_no007_Antenna_Deployment_Status: ax25_frame.no007_antenna_deployment_status_value
    :field cw_g_no007_AntDep_plusX: ax25_frame.no007_antdep_bit_pos_x
    :field cw_g_no007_AntDep_minusX: ax25_frame.no007_antdep_bit_neg_x
    :field cw_g_no007_AntDep_plusY: ax25_frame.no007_antdep_bit_pos_y
    :field cw_g_no007_AntDep_minusY: ax25_frame.no007_antdep_bit_neg_y
    :field cw_g_no008_Uplink_Reception_Count: ax25_frame.no008_uplink_reception_count_value
    :field cw_g_no009_Battery1_V_mV: ax25_frame.no009_battery_1_voltage_mv_value
    :field cw_g_no010_Battery1_Charging_Current_First_mA: ax25_frame.no010_battery_1_charging_current_first_half_ma_value
    
    # ---------- CW 'H' (ASCII beacon) ----------
    :field cw_h_no001_Message_Identifier: ax25_frame.no001_message_identifier
    :field cw_h_no002_Batt1_Charging_mA_second: ax25_frame.no002_battery_1_charging_current_second_half_ma_value
    :field cw_h_no003_Batt1_Discharging_mA: ax25_frame.no003_battery_1_discharging_current_ma_value
    :field cw_h_no004_Batt1_Temp_c: ax25_frame.no004_battery_1_temperature_degc_value
    :field cw_h_no005_Batt2_V_mV: ax25_frame.no005_battery_2_voltage_mv_value
    :field cw_h_no006_Batt2_Charging_mA: ax25_frame.no006_battery_2_charging_current_ma_value
    :field cw_h_no007_Batt2_Discharging_mA: ax25_frame.no007_battery_2_discharging_current_ma_value
    :field cw_h_no008_Batt2_Temp_c: ax25_frame.no008_battery_2_temperature_degc_value
    :field cw_h_no009_Subsys_PowerFault_bitmap: ax25_frame.no009_subsystem_power_fault_status_value
    :field cw_h_no009_NoFault_MOBC: ax25_frame.no009_fault_ok_mobc
    :field cw_h_no009_NoFault_TOBC_SUB: ax25_frame.no009_fault_ok_tobc_sub
    :field cw_h_no009_NoFault_RW: ax25_frame.no009_fault_ok_rw
    :field cw_h_no009_NoFault_ANTH: ax25_frame.no009_fault_ok_anth
    :field cw_h_no009_NoFault_TOBC_MAIN: ax25_frame.no009_fault_ok_tobc_main
    :field cw_h_no009_NoFault_MTQ: ax25_frame.no009_fault_ok_mtq
    :field cw_h_no009_NoFault_AOBC: ax25_frame.no009_fault_ok_aobc
    :field cw_h_no010_Subsys_OnOff_bitmap: ax25_frame.no010_subsystem_power_onoff_status_value
    :field cw_h_no010_On_MOBC: ax25_frame.no010_on_mobc
    :field cw_h_no010_On_AOBC: ax25_frame.no010_on_aobc
    :field cw_h_no010_On_TOBC_MAIN: ax25_frame.no010_on_tobc_main
    :field cw_h_no010_On_ANTDEP: ax25_frame.no010_on_antdep
    :field cw_h_no010_On_RW: ax25_frame.no010_on_rw
    :field cw_h_no010_On_TOBC_SUB: ax25_frame.no010_on_tobc_sub
    :field cw_h_no010_On_MTQ: ax25_frame.no010_on_mtq
    :field cw_h_no011_TOBC_Main_Boot_Count: ax25_frame.no011_tobc_main_boot_count_value
    
    # ---------- CW 'I' (ASCII beacon) ----------
    :field cw_i_no001_Message_Identifier: ax25_frame.no001_message_identifier
    :field cw_i_no002_Main_TOBC_Operating_h: ax25_frame.no002_main_tobc_operating_time_hour_value
    :field cw_i_no003_Main_TOBC_Reception_Count: ax25_frame.no003_main_tobc_reception_count_value
    :field cw_i_no004_Sub_TOBC_Boot_Count: ax25_frame.no004_sub_tobc_boot_count_value
    :field cw_i_no005_Sub_TOBC_Operating_h: ax25_frame.no005_sub_tobc_operating_time_hour_value
    :field cw_i_no006_Sub_TOBC_Reception_Count: ax25_frame.no006_sub_tobc_reception_count_value
    :field cw_i_no007_AOBC_Operation_Mode: ax25_frame.no007_aobc_operation_mode_value
    :field cw_i_no008_ACS_Power_bitmap: ax25_frame.no008_attctrl_power_status_value
    :field cw_i_no008_On_RW1: ax25_frame.no008_on_rw1
    :field cw_i_no008_On_RW2: ax25_frame.no008_on_rw2
    :field cw_i_no008_On_RW3: ax25_frame.no008_on_rw3
    :field cw_i_no008_On_MTQ1: ax25_frame.no008_on_mtq1
    :field cw_i_no008_On_MTQ2: ax25_frame.no008_on_mtq2
    :field cw_i_no008_On_MTQ3: ax25_frame.no008_on_mtq3
    :field cw_i_no009_X_gyro_mdeg_s: ax25_frame.no009_x_axis_angular_velocity_mdeg_s_s16
    :field cw_i_no010_Y_gyro_mdeg_s: ax25_frame.no010_y_axis_angular_velocity_mdeg_s_s16
    :field cw_i_no011_Z_gyro_mdeg_s: ax25_frame.no011_z_axis_angular_velocity_mdeg_s_s16
    :field cw_i_no012_MOBC_Composition: ax25_frame.no012_composition_status
    :field cw_i_no012_MOBC_STT: ax25_frame.no012_stt_status
    
    .. seealso::
       Source - https://rsp03.rymansat.com/assets/pdfs/RSP-03_HK_Beacon_Format(JP)_Rev1R0.pdf
    """

    class SttStatusCwI(Enum):
        stopped = 0
        standby = 1
        calculating = 2

    class ActiveImu(Enum):
        imu0 = 0
        imu1 = 1
        imu2 = 2

    class CompositionStatus(Enum):
        stopped = 0
        standby = 1
        composing = 2

    class EnableDisable(Enum):
        disabled = 0
        enabled = 1

    class MtqMode(Enum):
        false = 0
        active = 1

    class MissionCmdResult(Enum):
        success = 0
        crc_error = 241
        command_execution_error = 242
        command_not_executable = 255

    class AobcOperationMode(Enum):
        standby = 1
        stabilizing = 2
        pointing = 3
        unloading = 4
        commissioning = 5

    class MissionCmdDetail(Enum):
        async_command_received = 65280
        json_parse_error = 65281
        command_processing_result_error = 65282
        command_id_not_found = 65283
        mission_system_abnormal_termination = 65535

    class AttitudeCtrlMode(Enum):
        standby = 1
        stabilizing = 2
        pointing = 3
        unloading = 4
        commissioning = 5

    class SttStatus(Enum):
        stopped = 0
        standby = 1
        computing = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        _on = self.first_tag
        if _on == 71:
            self.ax25_frame = Rsp03.CwG(self._io, self, self._root)
        elif _on == 72:
            self.ax25_frame = Rsp03.CwH(self._io, self, self._root)
        elif _on == 73:
            self.ax25_frame = Rsp03.CwI(self._io, self, self._root)
        else:
            self.ax25_frame = Rsp03.Ax25FrameBody(self._io, self, self._root)

    class CwG(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no001_message_identifier = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.no001_message_identifier == u"G":
                raise kaitaistruct.ValidationNotEqualError(u"G", self.no001_message_identifier, self._io, u"/types/cw_g/seq/0")
            self.no002_telemetry_type_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no003_cobc_boot_count_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no004_cobc_uptime_seconds_hex = (self._io.read_bytes(8)).decode(u"ASCII")
            self.no005_cobc_temperature_degc_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no006_satellite_operation_mode_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no007_antenna_deployment_status_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no008_uplink_reception_count_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no009_battery_1_voltage_mv_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no010_battery_1_charging_current_first_half_ma_hex = (self._io.read_bytes(2)).decode(u"ASCII")

        @property
        def cw_type(self):
            if hasattr(self, '_m_cw_type'):
                return self._m_cw_type

            self._m_cw_type = self.no001_message_identifier
            return getattr(self, '_m_cw_type', None)

        @property
        def no007_antdep_bit_pos_y(self):
            if hasattr(self, '_m_no007_antdep_bit_pos_y'):
                return self._m_no007_antdep_bit_pos_y

            self._m_no007_antdep_bit_pos_y = (self.no007_antenna_deployment_status_value & 4) != 0
            return getattr(self, '_m_no007_antdep_bit_pos_y', None)

        @property
        def no009_battery_1_voltage_mv_value(self):
            if hasattr(self, '_m_no009_battery_1_voltage_mv_value'):
                return self._m_no009_battery_1_voltage_mv_value

            self._m_no009_battery_1_voltage_mv_value = int(self.no009_battery_1_voltage_mv_hex, 16)
            return getattr(self, '_m_no009_battery_1_voltage_mv_value', None)

        @property
        def no010_battery_1_charging_current_first_half_ma_value(self):
            if hasattr(self, '_m_no010_battery_1_charging_current_first_half_ma_value'):
                return self._m_no010_battery_1_charging_current_first_half_ma_value

            self._m_no010_battery_1_charging_current_first_half_ma_value = int(self.no010_battery_1_charging_current_first_half_ma_hex, 16)
            return getattr(self, '_m_no010_battery_1_charging_current_first_half_ma_value', None)

        @property
        def no007_antenna_deployment_status_value(self):
            if hasattr(self, '_m_no007_antenna_deployment_status_value'):
                return self._m_no007_antenna_deployment_status_value

            self._m_no007_antenna_deployment_status_value = int(self.no007_antenna_deployment_status_hex, 16)
            return getattr(self, '_m_no007_antenna_deployment_status_value', None)

        @property
        def no004_cobc_uptime_seconds_value(self):
            if hasattr(self, '_m_no004_cobc_uptime_seconds_value'):
                return self._m_no004_cobc_uptime_seconds_value

            self._m_no004_cobc_uptime_seconds_value = int(self.no004_cobc_uptime_seconds_hex, 16)
            return getattr(self, '_m_no004_cobc_uptime_seconds_value', None)

        @property
        def no007_antdep_bit_neg_x(self):
            if hasattr(self, '_m_no007_antdep_bit_neg_x'):
                return self._m_no007_antdep_bit_neg_x

            self._m_no007_antdep_bit_neg_x = (self.no007_antenna_deployment_status_value & 2) != 0
            return getattr(self, '_m_no007_antdep_bit_neg_x', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = self.no001_message_identifier + self.no002_telemetry_type_hex + self.no003_cobc_boot_count_hex + self.no004_cobc_uptime_seconds_hex + self.no005_cobc_temperature_degc_hex + self.no006_satellite_operation_mode_hex + self.no007_antenna_deployment_status_hex + self.no008_uplink_reception_count_hex + self.no009_battery_1_voltage_mv_hex + self.no010_battery_1_charging_current_first_half_ma_hex
            return getattr(self, '_m_cw_beacon', None)

        @property
        def no007_antdep_bit_neg_y(self):
            if hasattr(self, '_m_no007_antdep_bit_neg_y'):
                return self._m_no007_antdep_bit_neg_y

            self._m_no007_antdep_bit_neg_y = (self.no007_antenna_deployment_status_value & 8) != 0
            return getattr(self, '_m_no007_antdep_bit_neg_y', None)

        @property
        def no007_antdep_bit_pos_x(self):
            if hasattr(self, '_m_no007_antdep_bit_pos_x'):
                return self._m_no007_antdep_bit_pos_x

            self._m_no007_antdep_bit_pos_x = (self.no007_antenna_deployment_status_value & 1) != 0
            return getattr(self, '_m_no007_antdep_bit_pos_x', None)

        @property
        def no005_cobc_temperature_degc_value(self):
            if hasattr(self, '_m_no005_cobc_temperature_degc_value'):
                return self._m_no005_cobc_temperature_degc_value

            self._m_no005_cobc_temperature_degc_value = int(self.no005_cobc_temperature_degc_hex, 16)
            return getattr(self, '_m_no005_cobc_temperature_degc_value', None)

        @property
        def no006_satellite_operation_mode_value(self):
            if hasattr(self, '_m_no006_satellite_operation_mode_value'):
                return self._m_no006_satellite_operation_mode_value

            self._m_no006_satellite_operation_mode_value = int(self.no006_satellite_operation_mode_hex, 16)
            return getattr(self, '_m_no006_satellite_operation_mode_value', None)

        @property
        def no003_cobc_boot_count_value(self):
            if hasattr(self, '_m_no003_cobc_boot_count_value'):
                return self._m_no003_cobc_boot_count_value

            self._m_no003_cobc_boot_count_value = int(self.no003_cobc_boot_count_hex, 16)
            return getattr(self, '_m_no003_cobc_boot_count_value', None)

        @property
        def no002_telemetry_type_value(self):
            if hasattr(self, '_m_no002_telemetry_type_value'):
                return self._m_no002_telemetry_type_value

            self._m_no002_telemetry_type_value = int(self.no002_telemetry_type_hex, 16)
            return getattr(self, '_m_no002_telemetry_type_value', None)

        @property
        def no008_uplink_reception_count_value(self):
            if hasattr(self, '_m_no008_uplink_reception_count_value'):
                return self._m_no008_uplink_reception_count_value

            self._m_no008_uplink_reception_count_value = int(self.no008_uplink_reception_count_hex, 16)
            return getattr(self, '_m_no008_uplink_reception_count_value', None)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Rsp03.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Rsp03.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Rsp03.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Rsp03.SsidMask(self._io, self, self._root)
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
            if not  ((self.callsign == u"JS1YOY") or (self.callsign == u"JS1YPA")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class Packet1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no005_telemetry_id = self._io.read_u2le()
            self.no006_cobc_boot_count = self._io.read_u4le()
            self.no007_cobc_elapsed_time = self._io.read_u8le()
            self.no008_satellite_system_time = self._io.read_u8le()
            self.no009_cobc_temperature = self._io.read_s1()
            self.no010_satellite_operation_mode = self._io.read_u1()
            self.no011_antenna_deployment_status = self._io.read_u1()
            self.no012_uplink_command_reception_count = self._io.read_u2le()
            self.no013_cobc_temperature_upper_limit_exceed_count = self._io.read_u1()
            self.no014_cobc_temperature_lower_limit_exceed_count = self._io.read_u1()
            self.no015_cobc_voltage_upper_limit_exceed_count = self._io.read_u1()
            self.no016_cobc_voltage_lower_limit_exceed_count = self._io.read_u1()
            self.no017_cobc_current_upper_limit_exceed_count = self._io.read_u1()
            self.no018_cobc_current_lower_limit_exceed_count = self._io.read_u1()
            self.no019_main_radio_temperature_upper_limit_exceed_count = self._io.read_u1()
            self.no020_main_radio_temperature_lower_limit_exceed_count = self._io.read_u1()
            self.no021_main_radio_voltage_upper_limit_exceed_count = self._io.read_u1()
            self.no022_main_radio_voltage_lower_limit_exceed_count = self._io.read_u1()
            self.no023_main_radio_current_upper_limit_exceed_count = self._io.read_u1()
            self.no024_main_radio_current_lower_limit_exceed_count = self._io.read_u1()
            self.no025_sub_radio_temperature_upper_limit_exceed_count = self._io.read_u1()
            self.no026_sub_radio_temperature_lower_limit_exceed_count = self._io.read_u1()
            self.no027_sub_radio_voltage_upper_limit_exceed_count = self._io.read_u1()
            self.no028_sub_radio_voltage_lower_limit_exceed_count = self._io.read_u1()
            self.no029_sub_radio_current_upper_limit_exceed_count = self._io.read_u1()
            self.no030_sub_radio_current_lower_limit_exceed_count = self._io.read_u1()
            self.no031_aobc_temperature_upper_limit_exceed_count = self._io.read_u1()
            self.no032_aobc_temperature_lower_limit_exceed_count = self._io.read_u1()
            self.no033_aobc_voltage_upper_limit_exceed_count = self._io.read_u1()
            self.no034_aobc_voltage_lower_limit_exceed_count = self._io.read_u1()
            self.no035_aobc_current_upper_limit_exceed_count = self._io.read_u1()
            self.no036_aobc_current_lower_limit_exceed_count = self._io.read_u1()
            self.no037_mobc_temperature_upper_limit_exceed_count = self._io.read_u1()
            self.no038_mobc_temperature_lower_limit_exceed_count = self._io.read_u1()
            self.no039_mobc_voltage_upper_limit_exceed_count = self._io.read_u1()
            self.no040_mobc_voltage_lower_limit_exceed_count = self._io.read_u1()
            self.no041_mobc_current_upper_limit_exceed_count = self._io.read_u1()
            self.no042_mobc_current_lower_limit_exceed_count = self._io.read_u1()
            self.no043_magnetic_torque_consumption_current = self._io.read_s2le()
            self.no044_reaction_wheel_consumption_current = self._io.read_s2le()
            self.no045_antenna_deployment_heater_consumption_current = self._io.read_s2le()
            self.no046_main_radio_consumption_current = self._io.read_s2le()
            self.no047_sub_radio_consumption_current = self._io.read_s2le()
            self.no048_mobc_consumption_current = self._io.read_s2le()
            self.no049_cobc_consumption_current = self._io.read_s2le()
            self.no050_aobc_consumption_current = self._io.read_s2le()
            self.no051_5v_bus_voltage = self._io.read_s2le()
            self.no052_33v_line_voltage = self._io.read_s2le()
            self.no053_bus_current = self._io.read_s2le()
            self.no054_sap_z_face_voltage = self._io.read_s2le()
            self.no055_sap_z_face_temperature = self._io.read_s2le()
            self.no056_sap__z_face_voltage = self._io.read_s2le()
            self.no057_sap__z_face_temperature = self._io.read_s2le()
            self.no058_sap_y_face_voltage = self._io.read_s2le()
            self.no059_sap_y_face_temperature = self._io.read_s2le()
            self.no060_sap__x_face_voltage = self._io.read_s2le()
            self.no061_sap__x_face_temperature = self._io.read_s2le()
            self.no062_sap__y_face_voltage = self._io.read_s2le()
            self.no063_sap__y_face_temperature = self._io.read_s2le()
            self.no064_sap_z_face_current = self._io.read_s2le()
            self.no065_sap__z_face_current = self._io.read_s2le()
            self.no066_sap_y_face_current = self._io.read_s2le()
            self.no067_sap__x_face_current = self._io.read_s2le()
            self.no068_sap__y_face_current = self._io.read_s2le()
            self.no069_battery_1_output_voltage = self._io.read_s2le()
            self.no070_battery_1_charging_current = self._io.read_s2le()
            self.no071_battery_1_discharging_current = self._io.read_s2le()
            self.no072_battery_1_temperature = self._io.read_s2le()
            self.no073_battery_1_cumulative_charge = self._io.read_u4le()
            self.no074_battery_1_cumulative_discharge = self._io.read_u4le()
            self.no075_battery_2_output_voltage = self._io.read_s2le()
            self.no076_battery_2_charging_current = self._io.read_s2le()
            self.no077_battery_2_discharging_current = self._io.read_s2le()
            self.no078_battery_2_temperature = self._io.read_s2le()
            self.no079_battery_2_cumulative_charge = self._io.read_u4le()
            self.no080_battery_2_cumulative_discharge = self._io.read_u4le()
            self.no081_equipment_power_anomaly_status = self._io.read_u1()
            self.no082_equipment_power_status = self._io.read_u1()
            self.no083_mppt_status = self._io.read_u1()
            self.no084_battery_chargedischarge_controller_status = self._io.read_u1()
            self.no085_internal_equipment_communication_error_status = self._io.read_u1()
            self.no086_main_radio_boot_count = self._io.read_u1()
            self.no087_main_radio_elapsed_time = self._io.read_u1()
            self.no088_main_radio_no_reception_time = self._io.read_u1()
            self.no089_main_radio_rssi = self._io.read_s1()
            self.no090_main_radio_uplink_reception_counter = self._io.read_u1()
            self.no091_main_radio_uplink_modulation = self._io.read_u1()
            self.no092_main_radio_downlink_modulation = self._io.read_u1()
            self.no093_main_radio_downlink_protocol = self._io.read_u1()
            self.no094_main_radio_frequency_lock = self._io.read_u1()
            self.no095_main_radio_pa_temperature = self._io.read_s1()
            self.no096_main_radio_pa_current = self._io.read_s2le()
            self.no097_main_radio_mcu_temperature_ = self._io.read_s1()
            self.no098_sub_radio_boot_count = self._io.read_u1()
            self.no099_sub_radio_elapsed_time = self._io.read_u1()
            self.no100_sub_radio_no_reception_time = self._io.read_u1()
            self.no101_sub_radio_rssi = self._io.read_s1()
            self.no102_sub_radio_uplink_reception_counter = self._io.read_u1()
            self.no103_sub_radio_uplink_modulation = self._io.read_u1()
            self.no104_sub_radio_downlink_modulation = self._io.read_u1()
            self.no105_sub_radio_downlink_protocol = self._io.read_u1()
            self.no106_sub_radio_frequency_lock = self._io.read_u1()
            self.no107_sub_radio_pa_temperature = self._io.read_s1()
            self.no108_sub_radio_pa_current = self._io.read_s2le()
            self.no109_sub_radio_mcu_temperature = self._io.read_s1()

        @property
        def no084_flag_5(self):
            if hasattr(self, '_m_no084_flag_5'):
                return self._m_no084_flag_5

            self._m_no084_flag_5 = ((self.no084_battery_chargedischarge_controller_status >> 5) & 1) != 0
            return getattr(self, '_m_no084_flag_5', None)

        @property
        def no084_flag_3(self):
            if hasattr(self, '_m_no084_flag_3'):
                return self._m_no084_flag_3

            self._m_no084_flag_3 = ((self.no084_battery_chargedischarge_controller_status >> 3) & 1) != 0
            return getattr(self, '_m_no084_flag_3', None)

        @property
        def no011_flag_0(self):
            if hasattr(self, '_m_no011_flag_0'):
                return self._m_no011_flag_0

            self._m_no011_flag_0 = (self.no011_antenna_deployment_status & 1) != 0
            return getattr(self, '_m_no011_flag_0', None)

        @property
        def no084_flag_1(self):
            if hasattr(self, '_m_no084_flag_1'):
                return self._m_no084_flag_1

            self._m_no084_flag_1 = ((self.no084_battery_chargedischarge_controller_status >> 1) & 1) != 0
            return getattr(self, '_m_no084_flag_1', None)

        @property
        def no083_flag_5(self):
            if hasattr(self, '_m_no083_flag_5'):
                return self._m_no083_flag_5

            self._m_no083_flag_5 = ((self.no083_mppt_status >> 5) & 1) != 0
            return getattr(self, '_m_no083_flag_5', None)

        @property
        def no082_flag_5(self):
            if hasattr(self, '_m_no082_flag_5'):
                return self._m_no082_flag_5

            self._m_no082_flag_5 = ((self.no082_equipment_power_status >> 5) & 1) != 0
            return getattr(self, '_m_no082_flag_5', None)

        @property
        def no085_flag_3(self):
            if hasattr(self, '_m_no085_flag_3'):
                return self._m_no085_flag_3

            self._m_no085_flag_3 = ((self.no085_internal_equipment_communication_error_status >> 3) & 1) != 0
            return getattr(self, '_m_no085_flag_3', None)

        @property
        def no084_flag_0(self):
            if hasattr(self, '_m_no084_flag_0'):
                return self._m_no084_flag_0

            self._m_no084_flag_0 = (self.no084_battery_chargedischarge_controller_status & 1) != 0
            return getattr(self, '_m_no084_flag_0', None)

        @property
        def no081_flag_5(self):
            if hasattr(self, '_m_no081_flag_5'):
                return self._m_no081_flag_5

            self._m_no081_flag_5 = ((self.no081_equipment_power_anomaly_status >> 5) & 1) != 0
            return getattr(self, '_m_no081_flag_5', None)

        @property
        def no011_flag_7(self):
            if hasattr(self, '_m_no011_flag_7'):
                return self._m_no011_flag_7

            self._m_no011_flag_7 = ((self.no011_antenna_deployment_status >> 7) & 1) != 0
            return getattr(self, '_m_no011_flag_7', None)

        @property
        def no082_flag_0(self):
            if hasattr(self, '_m_no082_flag_0'):
                return self._m_no082_flag_0

            self._m_no082_flag_0 = (self.no082_equipment_power_status & 1) != 0
            return getattr(self, '_m_no082_flag_0', None)

        @property
        def no082_flag_4(self):
            if hasattr(self, '_m_no082_flag_4'):
                return self._m_no082_flag_4

            self._m_no082_flag_4 = ((self.no082_equipment_power_status >> 4) & 1) != 0
            return getattr(self, '_m_no082_flag_4', None)

        @property
        def no083_flag_4(self):
            if hasattr(self, '_m_no083_flag_4'):
                return self._m_no083_flag_4

            self._m_no083_flag_4 = ((self.no083_mppt_status >> 4) & 1) != 0
            return getattr(self, '_m_no083_flag_4', None)

        @property
        def no011_flag_1(self):
            if hasattr(self, '_m_no011_flag_1'):
                return self._m_no011_flag_1

            self._m_no011_flag_1 = ((self.no011_antenna_deployment_status >> 1) & 1) != 0
            return getattr(self, '_m_no011_flag_1', None)

        @property
        def no082_flag_6(self):
            if hasattr(self, '_m_no082_flag_6'):
                return self._m_no082_flag_6

            self._m_no082_flag_6 = ((self.no082_equipment_power_status >> 6) & 1) != 0
            return getattr(self, '_m_no082_flag_6', None)

        @property
        def no082_flag_3(self):
            if hasattr(self, '_m_no082_flag_3'):
                return self._m_no082_flag_3

            self._m_no082_flag_3 = ((self.no082_equipment_power_status >> 3) & 1) != 0
            return getattr(self, '_m_no082_flag_3', None)

        @property
        def no083_flag_1(self):
            if hasattr(self, '_m_no083_flag_1'):
                return self._m_no083_flag_1

            self._m_no083_flag_1 = ((self.no083_mppt_status >> 1) & 1) != 0
            return getattr(self, '_m_no083_flag_1', None)

        @property
        def no082_flag_7(self):
            if hasattr(self, '_m_no082_flag_7'):
                return self._m_no082_flag_7

            self._m_no082_flag_7 = ((self.no082_equipment_power_status >> 7) & 1) != 0
            return getattr(self, '_m_no082_flag_7', None)

        @property
        def no011_flag_4(self):
            if hasattr(self, '_m_no011_flag_4'):
                return self._m_no011_flag_4

            self._m_no011_flag_4 = ((self.no011_antenna_deployment_status >> 4) & 1) != 0
            return getattr(self, '_m_no011_flag_4', None)

        @property
        def no011_flag_3(self):
            if hasattr(self, '_m_no011_flag_3'):
                return self._m_no011_flag_3

            self._m_no011_flag_3 = ((self.no011_antenna_deployment_status >> 3) & 1) != 0
            return getattr(self, '_m_no011_flag_3', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = 1
            return getattr(self, '_m_beacon_type', None)

        @property
        def no082_flag_2(self):
            if hasattr(self, '_m_no082_flag_2'):
                return self._m_no082_flag_2

            self._m_no082_flag_2 = ((self.no082_equipment_power_status >> 2) & 1) != 0
            return getattr(self, '_m_no082_flag_2', None)

        @property
        def no081_flag_1(self):
            if hasattr(self, '_m_no081_flag_1'):
                return self._m_no081_flag_1

            self._m_no081_flag_1 = ((self.no081_equipment_power_anomaly_status >> 1) & 1) != 0
            return getattr(self, '_m_no081_flag_1', None)

        @property
        def no083_flag_7(self):
            if hasattr(self, '_m_no083_flag_7'):
                return self._m_no083_flag_7

            self._m_no083_flag_7 = ((self.no083_mppt_status >> 7) & 1) != 0
            return getattr(self, '_m_no083_flag_7', None)

        @property
        def no085_flag_0(self):
            if hasattr(self, '_m_no085_flag_0'):
                return self._m_no085_flag_0

            self._m_no085_flag_0 = (self.no085_internal_equipment_communication_error_status & 1) != 0
            return getattr(self, '_m_no085_flag_0', None)

        @property
        def no083_flag_2(self):
            if hasattr(self, '_m_no083_flag_2'):
                return self._m_no083_flag_2

            self._m_no083_flag_2 = ((self.no083_mppt_status >> 2) & 1) != 0
            return getattr(self, '_m_no083_flag_2', None)

        @property
        def no083_flag_6(self):
            if hasattr(self, '_m_no083_flag_6'):
                return self._m_no083_flag_6

            self._m_no083_flag_6 = ((self.no083_mppt_status >> 6) & 1) != 0
            return getattr(self, '_m_no083_flag_6', None)

        @property
        def no082_flag_1(self):
            if hasattr(self, '_m_no082_flag_1'):
                return self._m_no082_flag_1

            self._m_no082_flag_1 = ((self.no082_equipment_power_status >> 1) & 1) != 0
            return getattr(self, '_m_no082_flag_1', None)

        @property
        def no085_flag_6(self):
            if hasattr(self, '_m_no085_flag_6'):
                return self._m_no085_flag_6

            self._m_no085_flag_6 = ((self.no085_internal_equipment_communication_error_status >> 6) & 1) != 0
            return getattr(self, '_m_no085_flag_6', None)

        @property
        def no083_flag_3(self):
            if hasattr(self, '_m_no083_flag_3'):
                return self._m_no083_flag_3

            self._m_no083_flag_3 = ((self.no083_mppt_status >> 3) & 1) != 0
            return getattr(self, '_m_no083_flag_3', None)

        @property
        def no084_flag_7(self):
            if hasattr(self, '_m_no084_flag_7'):
                return self._m_no084_flag_7

            self._m_no084_flag_7 = ((self.no084_battery_chargedischarge_controller_status >> 7) & 1) != 0
            return getattr(self, '_m_no084_flag_7', None)

        @property
        def no083_flag_0(self):
            if hasattr(self, '_m_no083_flag_0'):
                return self._m_no083_flag_0

            self._m_no083_flag_0 = (self.no083_mppt_status & 1) != 0
            return getattr(self, '_m_no083_flag_0', None)

        @property
        def no084_flag_6(self):
            if hasattr(self, '_m_no084_flag_6'):
                return self._m_no084_flag_6

            self._m_no084_flag_6 = ((self.no084_battery_chargedischarge_controller_status >> 6) & 1) != 0
            return getattr(self, '_m_no084_flag_6', None)

        @property
        def no085_flag_5(self):
            if hasattr(self, '_m_no085_flag_5'):
                return self._m_no085_flag_5

            self._m_no085_flag_5 = ((self.no085_internal_equipment_communication_error_status >> 5) & 1) != 0
            return getattr(self, '_m_no085_flag_5', None)

        @property
        def no085_flag_2(self):
            if hasattr(self, '_m_no085_flag_2'):
                return self._m_no085_flag_2

            self._m_no085_flag_2 = ((self.no085_internal_equipment_communication_error_status >> 2) & 1) != 0
            return getattr(self, '_m_no085_flag_2', None)

        @property
        def no011_flag_5(self):
            if hasattr(self, '_m_no011_flag_5'):
                return self._m_no011_flag_5

            self._m_no011_flag_5 = ((self.no011_antenna_deployment_status >> 5) & 1) != 0
            return getattr(self, '_m_no011_flag_5', None)

        @property
        def no081_flag_0(self):
            if hasattr(self, '_m_no081_flag_0'):
                return self._m_no081_flag_0

            self._m_no081_flag_0 = (self.no081_equipment_power_anomaly_status & 1) != 0
            return getattr(self, '_m_no081_flag_0', None)

        @property
        def no011_flag_2(self):
            if hasattr(self, '_m_no011_flag_2'):
                return self._m_no011_flag_2

            self._m_no011_flag_2 = ((self.no011_antenna_deployment_status >> 2) & 1) != 0
            return getattr(self, '_m_no011_flag_2', None)

        @property
        def no085_flag_7(self):
            if hasattr(self, '_m_no085_flag_7'):
                return self._m_no085_flag_7

            self._m_no085_flag_7 = ((self.no085_internal_equipment_communication_error_status >> 7) & 1) != 0
            return getattr(self, '_m_no085_flag_7', None)

        @property
        def no084_flag_4(self):
            if hasattr(self, '_m_no084_flag_4'):
                return self._m_no084_flag_4

            self._m_no084_flag_4 = ((self.no084_battery_chargedischarge_controller_status >> 4) & 1) != 0
            return getattr(self, '_m_no084_flag_4', None)

        @property
        def no081_flag_3(self):
            if hasattr(self, '_m_no081_flag_3'):
                return self._m_no081_flag_3

            self._m_no081_flag_3 = ((self.no081_equipment_power_anomaly_status >> 3) & 1) != 0
            return getattr(self, '_m_no081_flag_3', None)

        @property
        def no081_flag_2(self):
            if hasattr(self, '_m_no081_flag_2'):
                return self._m_no081_flag_2

            self._m_no081_flag_2 = ((self.no081_equipment_power_anomaly_status >> 2) & 1) != 0
            return getattr(self, '_m_no081_flag_2', None)

        @property
        def no081_flag_4(self):
            if hasattr(self, '_m_no081_flag_4'):
                return self._m_no081_flag_4

            self._m_no081_flag_4 = ((self.no081_equipment_power_anomaly_status >> 4) & 1) != 0
            return getattr(self, '_m_no081_flag_4', None)

        @property
        def no084_flag_2(self):
            if hasattr(self, '_m_no084_flag_2'):
                return self._m_no084_flag_2

            self._m_no084_flag_2 = ((self.no084_battery_chargedischarge_controller_status >> 2) & 1) != 0
            return getattr(self, '_m_no084_flag_2', None)

        @property
        def no081_flag_7(self):
            if hasattr(self, '_m_no081_flag_7'):
                return self._m_no081_flag_7

            self._m_no081_flag_7 = ((self.no081_equipment_power_anomaly_status >> 7) & 1) != 0
            return getattr(self, '_m_no081_flag_7', None)

        @property
        def no081_flag_6(self):
            if hasattr(self, '_m_no081_flag_6'):
                return self._m_no081_flag_6

            self._m_no081_flag_6 = ((self.no081_equipment_power_anomaly_status >> 6) & 1) != 0
            return getattr(self, '_m_no081_flag_6', None)

        @property
        def no011_flag_6(self):
            if hasattr(self, '_m_no011_flag_6'):
                return self._m_no011_flag_6

            self._m_no011_flag_6 = ((self.no011_antenna_deployment_status >> 6) & 1) != 0
            return getattr(self, '_m_no011_flag_6', None)

        @property
        def no085_flag_4(self):
            if hasattr(self, '_m_no085_flag_4'):
                return self._m_no085_flag_4

            self._m_no085_flag_4 = ((self.no085_internal_equipment_communication_error_status >> 4) & 1) != 0
            return getattr(self, '_m_no085_flag_4', None)

        @property
        def no085_flag_1(self):
            if hasattr(self, '_m_no085_flag_1'):
                return self._m_no085_flag_1

            self._m_no085_flag_1 = ((self.no085_internal_equipment_communication_error_status >> 1) & 1) != 0
            return getattr(self, '_m_no085_flag_1', None)


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


    class Rsp03Payload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no001_header = self._io.read_u4le()
            self.no001_header_1 = self._io.read_u1()
            self.no002_time = self._io.read_u4le()
            self.no003_time = self._io.read_u2le()
            self.no004_packet_type = Rsp03.Rsp03Payload.No004PacketTypeT(self._io, self, self._root)

        class No004PacketTypeT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.packet_type = self._io.read_u1()
                _on = self.packet_type
                if _on == 1:
                    self.type_check = Rsp03.Packet1(self._io, self, self._root)
                elif _on == 2:
                    self.type_check = Rsp03.Packet2(self._io, self, self._root)
                elif _on == 3:
                    self.type_check = Rsp03.Packet3(self._io, self, self._root)


        @property
        def no001_header_u40(self):
            """5-byte header (u40) reconstructed as BE from u4le + u1."""
            if hasattr(self, '_m_no001_header_u40'):
                return self._m_no001_header_u40

            self._m_no001_header_u40 = ((((((self.no001_header & 255) << 32) + (((self.no001_header >> 8) & 255) << 24)) + (((self.no001_header >> 16) & 255) << 16)) + (((self.no001_header >> 24) & 255) << 8)) + self.no001_header_1)
            return getattr(self, '_m_no001_header_u40', None)

        @property
        def header_valid(self):
            """True if header matches known patterns."""
            if hasattr(self, '_m_header_valid'):
                return self._m_header_valid

            self._m_header_valid =  ((self.no001_header_u40 == 414023681) or (self.no001_header_u40 == 407535617) or (self.no001_header_u40 == 417300481)) 
            return getattr(self, '_m_header_valid', None)


    class CwH(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no001_message_identifier = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.no001_message_identifier == u"H":
                raise kaitaistruct.ValidationNotEqualError(u"H", self.no001_message_identifier, self._io, u"/types/cw_h/seq/0")
            self.no002_battery_1_charging_current_second_half_ma_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no003_battery_1_discharging_current_ma_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no004_battery_1_temperature_degc_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no005_battery_2_voltage_mv_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no006_battery_2_charging_current_ma_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no007_battery_2_discharging_current_ma_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no008_battery_2_temperature_degc_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no009_subsystem_power_fault_status_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no010_subsystem_power_onoff_status_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no011_tobc_main_boot_count_hex = (self._io.read_bytes(2)).decode(u"ASCII")

        @property
        def cw_type(self):
            if hasattr(self, '_m_cw_type'):
                return self._m_cw_type

            self._m_cw_type = self.no001_message_identifier
            return getattr(self, '_m_cw_type', None)

        @property
        def no009_fault_ok_aobc(self):
            if hasattr(self, '_m_no009_fault_ok_aobc'):
                return self._m_no009_fault_ok_aobc

            self._m_no009_fault_ok_aobc = (self.no009_subsystem_power_fault_status_value & 64) != 0
            return getattr(self, '_m_no009_fault_ok_aobc', None)

        @property
        def no011_tobc_main_boot_count_value(self):
            if hasattr(self, '_m_no011_tobc_main_boot_count_value'):
                return self._m_no011_tobc_main_boot_count_value

            self._m_no011_tobc_main_boot_count_value = int(self.no011_tobc_main_boot_count_hex, 16)
            return getattr(self, '_m_no011_tobc_main_boot_count_value', None)

        @property
        def no009_fault_ok_rw(self):
            if hasattr(self, '_m_no009_fault_ok_rw'):
                return self._m_no009_fault_ok_rw

            self._m_no009_fault_ok_rw = (self.no009_subsystem_power_fault_status_value & 4) != 0
            return getattr(self, '_m_no009_fault_ok_rw', None)

        @property
        def no010_on_tobc_sub(self):
            if hasattr(self, '_m_no010_on_tobc_sub'):
                return self._m_no010_on_tobc_sub

            self._m_no010_on_tobc_sub = (self.no010_subsystem_power_onoff_status_value & 2) != 0
            return getattr(self, '_m_no010_on_tobc_sub', None)

        @property
        def no010_on_aobc(self):
            if hasattr(self, '_m_no010_on_aobc'):
                return self._m_no010_on_aobc

            self._m_no010_on_aobc = (self.no010_subsystem_power_onoff_status_value & 32) != 0
            return getattr(self, '_m_no010_on_aobc', None)

        @property
        def no006_battery_2_charging_current_ma_value(self):
            if hasattr(self, '_m_no006_battery_2_charging_current_ma_value'):
                return self._m_no006_battery_2_charging_current_ma_value

            self._m_no006_battery_2_charging_current_ma_value = int(self.no006_battery_2_charging_current_ma_hex, 16)
            return getattr(self, '_m_no006_battery_2_charging_current_ma_value', None)

        @property
        def no004_battery_1_temperature_degc_value(self):
            if hasattr(self, '_m_no004_battery_1_temperature_degc_value'):
                return self._m_no004_battery_1_temperature_degc_value

            self._m_no004_battery_1_temperature_degc_value = int(self.no004_battery_1_temperature_degc_hex, 16)
            return getattr(self, '_m_no004_battery_1_temperature_degc_value', None)

        @property
        def no007_battery_2_discharging_current_ma_value(self):
            if hasattr(self, '_m_no007_battery_2_discharging_current_ma_value'):
                return self._m_no007_battery_2_discharging_current_ma_value

            self._m_no007_battery_2_discharging_current_ma_value = int(self.no007_battery_2_discharging_current_ma_hex, 16)
            return getattr(self, '_m_no007_battery_2_discharging_current_ma_value', None)

        @property
        def no009_fault_ok_mobc(self):
            if hasattr(self, '_m_no009_fault_ok_mobc'):
                return self._m_no009_fault_ok_mobc

            self._m_no009_fault_ok_mobc = (self.no009_subsystem_power_fault_status_value & 1) != 0
            return getattr(self, '_m_no009_fault_ok_mobc', None)

        @property
        def no009_fault_ok_tobc_sub(self):
            if hasattr(self, '_m_no009_fault_ok_tobc_sub'):
                return self._m_no009_fault_ok_tobc_sub

            self._m_no009_fault_ok_tobc_sub = (self.no009_subsystem_power_fault_status_value & 2) != 0
            return getattr(self, '_m_no009_fault_ok_tobc_sub', None)

        @property
        def no009_subsystem_power_fault_status_value(self):
            if hasattr(self, '_m_no009_subsystem_power_fault_status_value'):
                return self._m_no009_subsystem_power_fault_status_value

            self._m_no009_subsystem_power_fault_status_value = int(self.no009_subsystem_power_fault_status_hex, 16)
            return getattr(self, '_m_no009_subsystem_power_fault_status_value', None)

        @property
        def no008_battery_2_temperature_degc_value(self):
            if hasattr(self, '_m_no008_battery_2_temperature_degc_value'):
                return self._m_no008_battery_2_temperature_degc_value

            self._m_no008_battery_2_temperature_degc_value = int(self.no008_battery_2_temperature_degc_hex, 16)
            return getattr(self, '_m_no008_battery_2_temperature_degc_value', None)

        @property
        def no002_battery_1_charging_current_second_half_ma_value(self):
            if hasattr(self, '_m_no002_battery_1_charging_current_second_half_ma_value'):
                return self._m_no002_battery_1_charging_current_second_half_ma_value

            self._m_no002_battery_1_charging_current_second_half_ma_value = int(self.no002_battery_1_charging_current_second_half_ma_hex, 16)
            return getattr(self, '_m_no002_battery_1_charging_current_second_half_ma_value', None)

        @property
        def no010_on_tobc_main(self):
            if hasattr(self, '_m_no010_on_tobc_main'):
                return self._m_no010_on_tobc_main

            self._m_no010_on_tobc_main = (self.no010_subsystem_power_onoff_status_value & 16) != 0
            return getattr(self, '_m_no010_on_tobc_main', None)

        @property
        def no010_on_mtq(self):
            if hasattr(self, '_m_no010_on_mtq'):
                return self._m_no010_on_mtq

            self._m_no010_on_mtq = (self.no010_subsystem_power_onoff_status_value & 1) != 0
            return getattr(self, '_m_no010_on_mtq', None)

        @property
        def no009_fault_ok_anth(self):
            if hasattr(self, '_m_no009_fault_ok_anth'):
                return self._m_no009_fault_ok_anth

            self._m_no009_fault_ok_anth = (self.no009_subsystem_power_fault_status_value & 8) != 0
            return getattr(self, '_m_no009_fault_ok_anth', None)

        @property
        def no009_fault_ok_mtq(self):
            if hasattr(self, '_m_no009_fault_ok_mtq'):
                return self._m_no009_fault_ok_mtq

            self._m_no009_fault_ok_mtq = (self.no009_subsystem_power_fault_status_value & 32) != 0
            return getattr(self, '_m_no009_fault_ok_mtq', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = self.no001_message_identifier + self.no002_battery_1_charging_current_second_half_ma_hex + self.no003_battery_1_discharging_current_ma_hex + self.no004_battery_1_temperature_degc_hex + self.no005_battery_2_voltage_mv_hex + self.no006_battery_2_charging_current_ma_hex + self.no007_battery_2_discharging_current_ma_hex + self.no008_battery_2_temperature_degc_hex + self.no009_subsystem_power_fault_status_hex + self.no010_subsystem_power_onoff_status_hex + self.no011_tobc_main_boot_count_hex
            return getattr(self, '_m_cw_beacon', None)

        @property
        def no010_on_antdep(self):
            if hasattr(self, '_m_no010_on_antdep'):
                return self._m_no010_on_antdep

            self._m_no010_on_antdep = (self.no010_subsystem_power_onoff_status_value & 8) != 0
            return getattr(self, '_m_no010_on_antdep', None)

        @property
        def no010_on_rw(self):
            if hasattr(self, '_m_no010_on_rw'):
                return self._m_no010_on_rw

            self._m_no010_on_rw = (self.no010_subsystem_power_onoff_status_value & 4) != 0
            return getattr(self, '_m_no010_on_rw', None)

        @property
        def no009_fault_ok_tobc_main(self):
            if hasattr(self, '_m_no009_fault_ok_tobc_main'):
                return self._m_no009_fault_ok_tobc_main

            self._m_no009_fault_ok_tobc_main = (self.no009_subsystem_power_fault_status_value & 16) != 0
            return getattr(self, '_m_no009_fault_ok_tobc_main', None)

        @property
        def no005_battery_2_voltage_mv_value(self):
            if hasattr(self, '_m_no005_battery_2_voltage_mv_value'):
                return self._m_no005_battery_2_voltage_mv_value

            self._m_no005_battery_2_voltage_mv_value = int(self.no005_battery_2_voltage_mv_hex, 16)
            return getattr(self, '_m_no005_battery_2_voltage_mv_value', None)

        @property
        def no003_battery_1_discharging_current_ma_value(self):
            if hasattr(self, '_m_no003_battery_1_discharging_current_ma_value'):
                return self._m_no003_battery_1_discharging_current_ma_value

            self._m_no003_battery_1_discharging_current_ma_value = int(self.no003_battery_1_discharging_current_ma_hex, 16)
            return getattr(self, '_m_no003_battery_1_discharging_current_ma_value', None)

        @property
        def no010_subsystem_power_onoff_status_value(self):
            if hasattr(self, '_m_no010_subsystem_power_onoff_status_value'):
                return self._m_no010_subsystem_power_onoff_status_value

            self._m_no010_subsystem_power_onoff_status_value = int(self.no010_subsystem_power_onoff_status_hex, 16)
            return getattr(self, '_m_no010_subsystem_power_onoff_status_value', None)

        @property
        def no010_on_mobc(self):
            if hasattr(self, '_m_no010_on_mobc'):
                return self._m_no010_on_mobc

            self._m_no010_on_mobc = (self.no010_subsystem_power_onoff_status_value & 64) != 0
            return getattr(self, '_m_no010_on_mobc', None)


    class Ax25FrameBody(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Rsp03.Ax25Header(self._io, self, self._root)
            self.payload = Rsp03.Rsp03Payload(self._io, self, self._root)


    class Packet2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no005_telemetry_id = self._io.read_u2le()
            self.no006_cobc_uptime_ = self._io.read_u8le()
            self.no007_satellite_system_time = self._io.read_u8le()
            self.no008_mission_command_execution_result = self._io.read_u1()
            self.no009_mission_command_execution_result_details = self._io.read_u2le()
            self.no010_os_time_at_telemetry_generation = self._io.read_u8le()
            self.no011_system_time_at_telemetry_generation = self._io.read_u8le()
            self.no012_mobc_temperature = self._io.read_s1()
            self.no013_composition_system_status = KaitaiStream.resolve_enum(Rsp03.CompositionStatus, self._io.read_u1())
            self.no014_stt_status = KaitaiStream.resolve_enum(Rsp03.SttStatus, self._io.read_u1())
            self.no015_right_ascension_last_acquired_by_stt = self._io.read_f4le()
            self.no016_declination_last_acquired_by_stt = self._io.read_f4le()
            self.no017_roll_angle_last_acquired_by_stt = self._io.read_f4le()
            self.no018_validity_of_acquired_coordinates = self._io.read_u1()
            self.no019_image_capture_time = self._io.read_u8le()
            self.no020_most_recent_command_id_1 = self._io.read_u1()
            self.no021_most_recent_command_result_1 = KaitaiStream.resolve_enum(Rsp03.MissionCmdResult, self._io.read_u1())
            self.no022_most_recent_command_result_detail_1 = KaitaiStream.resolve_enum(Rsp03.MissionCmdDetail, self._io.read_u2le())
            self.no023_most_recent_command_id_2 = self._io.read_u1()
            self.no024_most_recent_command_result_2 = KaitaiStream.resolve_enum(Rsp03.MissionCmdResult, self._io.read_u1())
            self.no025_most_recent_command_result_detail_2 = KaitaiStream.resolve_enum(Rsp03.MissionCmdDetail, self._io.read_u2le())
            self.no026_most_recent_command_id_3 = self._io.read_u1()
            self.no027_most_recent_command_result_3 = KaitaiStream.resolve_enum(Rsp03.MissionCmdResult, self._io.read_u1())
            self.no028_most_recent_command_result_detail_3 = KaitaiStream.resolve_enum(Rsp03.MissionCmdDetail, self._io.read_u2le())


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
            self.callsign_ror = Rsp03.Callsign(_io__raw_callsign_ror, self, self._root)


    class CwI(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no001_message_identifier = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.no001_message_identifier == u"I":
                raise kaitaistruct.ValidationNotEqualError(u"I", self.no001_message_identifier, self._io, u"/types/cw_i/seq/0")
            self.no002_main_tobc_operating_time_hour_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no003_main_tobc_reception_count_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no004_sub_tobc_boot_count_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no005_sub_tobc_operating_time_hour_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no006_sub_tobc_reception_count_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no007_aobc_operation_mode_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no008_attctrl_power_status_hex = (self._io.read_bytes(2)).decode(u"ASCII")
            self.no009_x_axis_angular_velocity_mdeg_s_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no010_y_axis_angular_velocity_mdeg_s_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no011_z_axis_angular_velocity_mdeg_s_hex = (self._io.read_bytes(4)).decode(u"ASCII")
            self.no012_mobc_operation_mode_hex = (self._io.read_bytes(2)).decode(u"ASCII")

        @property
        def cw_type(self):
            if hasattr(self, '_m_cw_type'):
                return self._m_cw_type

            self._m_cw_type = self.no001_message_identifier
            return getattr(self, '_m_cw_type', None)

        @property
        def no006_sub_tobc_reception_count_value(self):
            if hasattr(self, '_m_no006_sub_tobc_reception_count_value'):
                return self._m_no006_sub_tobc_reception_count_value

            self._m_no006_sub_tobc_reception_count_value = int(self.no006_sub_tobc_reception_count_hex, 16)
            return getattr(self, '_m_no006_sub_tobc_reception_count_value', None)

        @property
        def no009_x_axis_angular_velocity_mdeg_s_u16(self):
            if hasattr(self, '_m_no009_x_axis_angular_velocity_mdeg_s_u16'):
                return self._m_no009_x_axis_angular_velocity_mdeg_s_u16

            self._m_no009_x_axis_angular_velocity_mdeg_s_u16 = int(self.no009_x_axis_angular_velocity_mdeg_s_hex, 16)
            return getattr(self, '_m_no009_x_axis_angular_velocity_mdeg_s_u16', None)

        @property
        def no008_on_mtq1(self):
            if hasattr(self, '_m_no008_on_mtq1'):
                return self._m_no008_on_mtq1

            self._m_no008_on_mtq1 = (self.no008_attctrl_power_status_value & 8) != 0
            return getattr(self, '_m_no008_on_mtq1', None)

        @property
        def no008_on_rw1(self):
            if hasattr(self, '_m_no008_on_rw1'):
                return self._m_no008_on_rw1

            self._m_no008_on_rw1 = (self.no008_attctrl_power_status_value & 1) != 0
            return getattr(self, '_m_no008_on_rw1', None)

        @property
        def no011_z_axis_angular_velocity_mdeg_s_s16(self):
            if hasattr(self, '_m_no011_z_axis_angular_velocity_mdeg_s_s16'):
                return self._m_no011_z_axis_angular_velocity_mdeg_s_s16

            self._m_no011_z_axis_angular_velocity_mdeg_s_s16 = (self.no011_z_axis_angular_velocity_mdeg_s_u16 - ((self.no011_z_axis_angular_velocity_mdeg_s_u16 & 32768) << 1))
            return getattr(self, '_m_no011_z_axis_angular_velocity_mdeg_s_s16', None)

        @property
        def no004_sub_tobc_boot_count_value(self):
            if hasattr(self, '_m_no004_sub_tobc_boot_count_value'):
                return self._m_no004_sub_tobc_boot_count_value

            self._m_no004_sub_tobc_boot_count_value = int(self.no004_sub_tobc_boot_count_hex, 16)
            return getattr(self, '_m_no004_sub_tobc_boot_count_value', None)

        @property
        def no012_mobc_stt_low_nibble(self):
            if hasattr(self, '_m_no012_mobc_stt_low_nibble'):
                return self._m_no012_mobc_stt_low_nibble

            self._m_no012_mobc_stt_low_nibble = (self.no012_mobc_operation_mode_value & 15)
            return getattr(self, '_m_no012_mobc_stt_low_nibble', None)

        @property
        def no005_sub_tobc_operating_time_hour_value(self):
            if hasattr(self, '_m_no005_sub_tobc_operating_time_hour_value'):
                return self._m_no005_sub_tobc_operating_time_hour_value

            self._m_no005_sub_tobc_operating_time_hour_value = int(self.no005_sub_tobc_operating_time_hour_hex, 16)
            return getattr(self, '_m_no005_sub_tobc_operating_time_hour_value', None)

        @property
        def no008_on_rw3(self):
            if hasattr(self, '_m_no008_on_rw3'):
                return self._m_no008_on_rw3

            self._m_no008_on_rw3 = (self.no008_attctrl_power_status_value & 4) != 0
            return getattr(self, '_m_no008_on_rw3', None)

        @property
        def no003_main_tobc_reception_count_value(self):
            if hasattr(self, '_m_no003_main_tobc_reception_count_value'):
                return self._m_no003_main_tobc_reception_count_value

            self._m_no003_main_tobc_reception_count_value = int(self.no003_main_tobc_reception_count_hex, 16)
            return getattr(self, '_m_no003_main_tobc_reception_count_value', None)

        @property
        def no012_mobc_composition_high_nibble(self):
            if hasattr(self, '_m_no012_mobc_composition_high_nibble'):
                return self._m_no012_mobc_composition_high_nibble

            self._m_no012_mobc_composition_high_nibble = ((self.no012_mobc_operation_mode_value >> 4) & 15)
            return getattr(self, '_m_no012_mobc_composition_high_nibble', None)

        @property
        def no012_composition_status(self):
            if hasattr(self, '_m_no012_composition_status'):
                return self._m_no012_composition_status

            self._m_no012_composition_status = KaitaiStream.resolve_enum(Rsp03.CompositionStatus, self.no012_mobc_composition_high_nibble)
            return getattr(self, '_m_no012_composition_status', None)

        @property
        def no010_y_axis_angular_velocity_mdeg_s_s16(self):
            if hasattr(self, '_m_no010_y_axis_angular_velocity_mdeg_s_s16'):
                return self._m_no010_y_axis_angular_velocity_mdeg_s_s16

            self._m_no010_y_axis_angular_velocity_mdeg_s_s16 = (self.no010_y_axis_angular_velocity_mdeg_s_u16 - ((self.no010_y_axis_angular_velocity_mdeg_s_u16 & 32768) << 1))
            return getattr(self, '_m_no010_y_axis_angular_velocity_mdeg_s_s16', None)

        @property
        def no012_mobc_operation_mode_value(self):
            if hasattr(self, '_m_no012_mobc_operation_mode_value'):
                return self._m_no012_mobc_operation_mode_value

            self._m_no012_mobc_operation_mode_value = int(self.no012_mobc_operation_mode_hex, 16)
            return getattr(self, '_m_no012_mobc_operation_mode_value', None)

        @property
        def no012_stt_status(self):
            if hasattr(self, '_m_no012_stt_status'):
                return self._m_no012_stt_status

            self._m_no012_stt_status = KaitaiStream.resolve_enum(Rsp03.SttStatusCwI, self.no012_mobc_stt_low_nibble)
            return getattr(self, '_m_no012_stt_status', None)

        @property
        def no008_attctrl_power_status_value(self):
            if hasattr(self, '_m_no008_attctrl_power_status_value'):
                return self._m_no008_attctrl_power_status_value

            self._m_no008_attctrl_power_status_value = int(self.no008_attctrl_power_status_hex, 16)
            return getattr(self, '_m_no008_attctrl_power_status_value', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = self.no001_message_identifier + self.no002_main_tobc_operating_time_hour_hex + self.no003_main_tobc_reception_count_hex + self.no004_sub_tobc_boot_count_hex + self.no005_sub_tobc_operating_time_hour_hex + self.no006_sub_tobc_reception_count_hex + self.no007_aobc_operation_mode_hex + self.no008_attctrl_power_status_hex + self.no009_x_axis_angular_velocity_mdeg_s_hex + self.no010_y_axis_angular_velocity_mdeg_s_hex + self.no011_z_axis_angular_velocity_mdeg_s_hex + self.no012_mobc_operation_mode_hex
            return getattr(self, '_m_cw_beacon', None)

        @property
        def no009_x_axis_angular_velocity_mdeg_s_s16(self):
            if hasattr(self, '_m_no009_x_axis_angular_velocity_mdeg_s_s16'):
                return self._m_no009_x_axis_angular_velocity_mdeg_s_s16

            self._m_no009_x_axis_angular_velocity_mdeg_s_s16 = (self.no009_x_axis_angular_velocity_mdeg_s_u16 - ((self.no009_x_axis_angular_velocity_mdeg_s_u16 & 32768) << 1))
            return getattr(self, '_m_no009_x_axis_angular_velocity_mdeg_s_s16', None)

        @property
        def no007_aobc_operation_mode_value(self):
            if hasattr(self, '_m_no007_aobc_operation_mode_value'):
                return self._m_no007_aobc_operation_mode_value

            self._m_no007_aobc_operation_mode_value = KaitaiStream.resolve_enum(Rsp03.AobcOperationMode, int(self.no007_aobc_operation_mode_hex, 16))
            return getattr(self, '_m_no007_aobc_operation_mode_value', None)

        @property
        def no010_y_axis_angular_velocity_mdeg_s_u16(self):
            if hasattr(self, '_m_no010_y_axis_angular_velocity_mdeg_s_u16'):
                return self._m_no010_y_axis_angular_velocity_mdeg_s_u16

            self._m_no010_y_axis_angular_velocity_mdeg_s_u16 = int(self.no010_y_axis_angular_velocity_mdeg_s_hex, 16)
            return getattr(self, '_m_no010_y_axis_angular_velocity_mdeg_s_u16', None)

        @property
        def no008_on_rw2(self):
            if hasattr(self, '_m_no008_on_rw2'):
                return self._m_no008_on_rw2

            self._m_no008_on_rw2 = (self.no008_attctrl_power_status_value & 2) != 0
            return getattr(self, '_m_no008_on_rw2', None)

        @property
        def no008_on_mtq2(self):
            if hasattr(self, '_m_no008_on_mtq2'):
                return self._m_no008_on_mtq2

            self._m_no008_on_mtq2 = (self.no008_attctrl_power_status_value & 16) != 0
            return getattr(self, '_m_no008_on_mtq2', None)

        @property
        def no002_main_tobc_operating_time_hour_value(self):
            if hasattr(self, '_m_no002_main_tobc_operating_time_hour_value'):
                return self._m_no002_main_tobc_operating_time_hour_value

            self._m_no002_main_tobc_operating_time_hour_value = int(self.no002_main_tobc_operating_time_hour_hex, 16)
            return getattr(self, '_m_no002_main_tobc_operating_time_hour_value', None)

        @property
        def no011_z_axis_angular_velocity_mdeg_s_u16(self):
            if hasattr(self, '_m_no011_z_axis_angular_velocity_mdeg_s_u16'):
                return self._m_no011_z_axis_angular_velocity_mdeg_s_u16

            self._m_no011_z_axis_angular_velocity_mdeg_s_u16 = int(self.no011_z_axis_angular_velocity_mdeg_s_hex, 16)
            return getattr(self, '_m_no011_z_axis_angular_velocity_mdeg_s_u16', None)

        @property
        def no008_on_mtq3(self):
            if hasattr(self, '_m_no008_on_mtq3'):
                return self._m_no008_on_mtq3

            self._m_no008_on_mtq3 = (self.no008_attctrl_power_status_value & 32) != 0
            return getattr(self, '_m_no008_on_mtq3', None)


    class Packet3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no005_telemetry_id = self._io.read_u2le()
            self.no006_cobc_uptime = self._io.read_u8le()
            self.no007_satellite_system_time = self._io.read_u8le()
            self.no008_telemetry_type = self._io.read_u1()
            self.no009_attitude_control_mode = KaitaiStream.resolve_enum(Rsp03.AttitudeCtrlMode, self._io.read_u1())
            self.no010_ground_packet_reception_count = self._io.read_u2le()
            self.no011_x_axis_rw_mode = KaitaiStream.resolve_enum(Rsp03.EnableDisable, self._io.read_u1())
            self.no012_x_axis_rw_speed = self._io.read_s4le()
            self.no013_x_axis_rw_status = self._io.read_u1()
            self.no014_y_axis_rw_mode = KaitaiStream.resolve_enum(Rsp03.EnableDisable, self._io.read_u1())
            self.no015_y_axis_rw_speed = self._io.read_s4le()
            self.no016_y_axis_rw_status = self._io.read_u1()
            self.no017_z_axis_rw_mode = KaitaiStream.resolve_enum(Rsp03.EnableDisable, self._io.read_u1())
            self.no018_z_axis_rw_speed = self._io.read_s4le()
            self.no019_z_axis_rw_status = self._io.read_u1()
            self.no020_x_axis_mtq_mode = KaitaiStream.resolve_enum(Rsp03.MtqMode, self._io.read_u1())
            self.no021_x_axis_mtq_set_voltage = self._io.read_s4le()
            self.no022_x_axis_mtq_status = self._io.read_u1()
            self.no023_y_axis_mtq_mode = KaitaiStream.resolve_enum(Rsp03.MtqMode, self._io.read_u1())
            self.no024_y_axis_mtq_set_voltage = self._io.read_s4le()
            self.no025_y_axis_mtq_status = self._io.read_u1()
            self.no026_z_axis_mtq_mode = KaitaiStream.resolve_enum(Rsp03.MtqMode, self._io.read_u1())
            self.no027_z_axis_mtq_set_voltage = self._io.read_s4le()
            self.no028_z_axis_mtq_status = self._io.read_u1()
            self.no029_imu1_x_axis_acceleration = self._io.read_f4le()
            self.no030_imu1_y_axis_acceleration = self._io.read_f4le()
            self.no031_imu1_z_axis_acceleration = self._io.read_f4le()
            self.no032_imu1_x_axis_angular_velocity = self._io.read_f4le()
            self.no033_imu1_y_axis_angular_velocity = self._io.read_f4le()
            self.no034_imu1_z_axis_angular_velocity = self._io.read_f4le()
            self.no035_imu1_x_axis_magnetic_field = self._io.read_f4le()
            self.no036_imu1_y_axis_magnetic_field = self._io.read_f4le()
            self.no037_imu1_z_axis_magnetic_field = self._io.read_f4le()
            self.no038_imu1_temperature = self._io.read_f4le()
            self.no039_imu1_status = self._io.read_u1()
            self.no040_imu2_x_axis_acceleration = self._io.read_f4le()
            self.no041_imu2_y_axis_acceleration = self._io.read_f4le()
            self.no042_imu2_z_axis_acceleration = self._io.read_f4le()
            self.no043_imu2_x_axis_angular_velocity = self._io.read_f4le()
            self.no044_imu2_y_axis_angular_velocity = self._io.read_f4le()
            self.no045_imu2_z_axis_angular_velocity = self._io.read_f4le()
            self.no046_imu2_x_axis_magnetic_field = self._io.read_f4le()
            self.no047_imu2_y_axis_magnetic_field = self._io.read_f4le()
            self.no048_imu2_z_axis_magnetic_field = self._io.read_f4le()
            self.no049_imu2_temperature = self._io.read_f4le()
            self.no050_imu2_status = self._io.read_u1()
            self.no051_imu3_x_axis_acceleration = self._io.read_f4le()
            self.no052_imu3_y_axis_acceleration = self._io.read_f4le()
            self.no053_imu3_z_axis_acceleration = self._io.read_f4le()
            self.no054_imu3_x_axis_angular_velocity = self._io.read_f4le()
            self.no055_imu3_y_axis_angular_velocity = self._io.read_f4le()
            self.no056_imu3_z_axis_angular_velocity = self._io.read_f4le()
            self.no057_imu3_x_axis_magnetic_field = self._io.read_f4le()
            self.no058_imu3_y_axis_magnetic_field = self._io.read_f4le()
            self.no059_imu3_z_axis_magnetic_field = self._io.read_f4le()
            self.no060_imu3_temperature = self._io.read_f4le()
            self.no061_imu3_status = self._io.read_u1()
            self.no062_x_axis_rw_proportional_gain = self._io.read_f4le()
            self.no063_x_axis_rw_derivative_gain = self._io.read_f4le()
            self.no064_y_axis_rw_proportional_gain = self._io.read_f4le()
            self.no065_y_axis_rw_derivative_gain = self._io.read_f4le()
            self.no066_z_axis_rw_proportional_gain = self._io.read_f4le()
            self.no067_z_axis_rw_derivative_gain = self._io.read_f4le()
            self.no068_commissioning_runtime_ = self._io.read_u4le()
            self.no069_imu_fault_detection_threshold = self._io.read_f4le()
            self.no070_active_imu = KaitaiStream.resolve_enum(Rsp03.ActiveImu, self._io.read_u1())
            self.no071_bdot_control_voltage = self._io.read_u4le()
            self.no072_bdot_reference_magnetic_field = self._io.read_f4le()


    @property
    def first_tag(self):
        if hasattr(self, '_m_first_tag'):
            return self._m_first_tag

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_first_tag = self._io.read_u1()
        self._io.seek(_pos)
        return getattr(self, '_m_first_tag', None)


