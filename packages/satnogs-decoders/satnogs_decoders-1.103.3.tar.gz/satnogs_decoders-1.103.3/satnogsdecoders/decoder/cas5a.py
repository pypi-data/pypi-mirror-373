# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cas5a(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field function_code_main: ax25_frame.payload.function_code_main
    :field function_code_spare1: ax25_frame.payload.function_code_spare1
    :field function_code_sub: ax25_frame.payload.function_code_sub
    :field function_code_sub_spare1: ax25_frame.payload.function_code_sub_spare1
    :field sub_function_code_main: ax25_frame.payload.sub_function_code_main
    :field function_rev: ax25_frame.payload.function_rev
    :field sat_time_year: ax25_frame.payload.payload.sat_time_year
    :field sat_time_month: ax25_frame.payload.payload.sat_time_month
    :field sat_time_day: ax25_frame.payload.payload.sat_time_day
    :field sat_time_hour: ax25_frame.payload.payload.sat_time_hour
    :field sat_time_minute: ax25_frame.payload.payload.sat_time_minute
    :field sat_time_second: ax25_frame.payload.payload.sat_time_second
    :field ihu_total_reset_counter: ax25_frame.payload.payload.ihu_total_reset_counter
    :field battery_status: ax25_frame.payload.payload.battery_status
    :field remote_control_frame_reception_counter: ax25_frame.payload.payload.remote_control_frame_reception_counter
    :field remote_control_command_execution_counter: ax25_frame.payload.payload.remote_control_command_execution_counter
    :field telemetry_frame_transmission_counter: ax25_frame.payload.payload.telemetry_frame_transmission_counter
    :field ihu_status_1: ax25_frame.payload.payload.ihu_status_1
    :field reserved_00: ax25_frame.payload.payload.reserved_00
    :field i2c_bus_status: ax25_frame.payload.payload.i2c_bus_status
    :field reserved_01: ax25_frame.payload.payload.reserved_01
    :field reserved_02: ax25_frame.payload.payload.reserved_02
    :field reserved_03: ax25_frame.payload.payload.reserved_03
    :field ihu_status_2: ax25_frame.payload.payload.ihu_status_2
    :field ihu_status_3: ax25_frame.payload.payload.ihu_status_3
    :field px_cabin_inner_plate_temp: ax25_frame.payload.payload.px_cabin_inner_plate_temp
    :field nx_cabin_inner_plate_temp: ax25_frame.payload.payload.nx_cabin_inner_plate_temp
    :field pdcu_temp: ax25_frame.payload.payload.pdcu_temp
    :field dcdc_temp: ax25_frame.payload.payload.dcdc_temp
    :field pz_cabin_inner_plate_temp: ax25_frame.payload.payload.pz_cabin_inner_plate_temp
    :field nz_cabin_inner_plate_temp: ax25_frame.payload.payload.nz_cabin_inner_plate_temp
    :field px_solar_array_temp: ax25_frame.payload.payload.px_solar_array_temp
    :field nx_solar_array_temp: ax25_frame.payload.payload.nx_solar_array_temp
    :field py_solar_array_temp: ax25_frame.payload.payload.py_solar_array_temp
    :field ny_solar_array_temp: ax25_frame.payload.payload.ny_solar_array_temp
    :field pz_solar_array_temp: ax25_frame.payload.payload.pz_solar_array_temp
    :field nz_solar_array_temp: ax25_frame.payload.payload.nz_solar_array_temp
    :field bat_pack_1_temp_1: ax25_frame.payload.payload.bat_pack_1_temp_1
    :field bat_pack_1_temp_2: ax25_frame.payload.payload.bat_pack_1_temp_2
    :field bat_pack_2_temp_3: ax25_frame.payload.payload.bat_pack_2_temp_3
    :field bat_pack_2_temp_4: ax25_frame.payload.payload.bat_pack_2_temp_4
    :field ihu_temp: ax25_frame.payload.payload.ihu_temp
    :field uhf1_pa_temp: ax25_frame.payload.payload.uhf1_pa_temp
    :field cam3_temp: ax25_frame.payload.payload.cam3_temp
    :field cam1_temp: ax25_frame.payload.payload.cam1_temp
    :field cam2_temp: ax25_frame.payload.payload.cam2_temp
    :field uhf2_pa_temp: ax25_frame.payload.payload.uhf2_pa_temp
    :field battery_voltage_integer: ax25_frame.payload.payload.battery_voltage_integer
    :field battery_voltage_decimal: ax25_frame.payload.payload.battery_voltage_decimal
    :field primary_power_supply_integer: ax25_frame.payload.payload.primary_power_supply_integer
    :field primary_power_supply_decimal: ax25_frame.payload.payload.primary_power_supply_decimal
    :field bus_voltage_5v_integer: ax25_frame.payload.payload.bus_voltage_5v_integer
    :field bus_voltage_5v_decimal: ax25_frame.payload.payload.bus_voltage_5v_decimal
    :field bus_voltage_3v8_integer: ax25_frame.payload.payload.bus_voltage_3v8_integer
    :field bus_voltage_3v8_decimal: ax25_frame.payload.payload.bus_voltage_3v8_decimal
    :field ihu_voltage_3v3_integer: ax25_frame.payload.payload.ihu_voltage_3v3_integer
    :field ihu_voltage_3v3_decimal: ax25_frame.payload.payload.ihu_voltage_3v3_decimal
    :field total_solar_array_current: ax25_frame.payload.payload.total_solar_array_current
    :field primary_bus_current: ax25_frame.payload.payload.primary_bus_current
    :field total_load_current: ax25_frame.payload.payload.total_load_current
    :field ihu_current: ax25_frame.payload.payload.ihu_current
    :field reserved_04: ax25_frame.payload.payload.reserved_04
    :field hf_receiver_current: ax25_frame.payload.payload.hf_receiver_current
    :field reserved_05: ax25_frame.payload.payload.reserved_05
    :field uhf_transmitter_2_current: ax25_frame.payload.payload.uhf_transmitter_2_current
    :field ht_agc_voltage_integer: ax25_frame.payload.payload.ht_agc_voltage_integer
    :field ht_agc_voltage_decimal: ax25_frame.payload.payload.ht_agc_voltage_decimal
    :field uhf_transmitter_1_current: ax25_frame.payload.payload.uhf_transmitter_1_current
    :field uhf1_rf_power: ax25_frame.payload.payload.uhf1_rf_power
    :field uhf2_rf_power: ax25_frame.payload.payload.uhf2_rf_power
    :field vhf_receiver_current: ax25_frame.payload.payload.vhf_receiver_current
    :field vhf_agc_voltage_integer: ax25_frame.payload.payload.vhf_agc_voltage_integer
    :field vhf_agc_voltage_decimal: ax25_frame.payload.payload.vhf_agc_voltage_decimal
    :field delayed_telemetry_start_time_year: ax25_frame.payload.payload.delayed_telemetry_start_time_year
    :field delayed_telemetry_start_time_month: ax25_frame.payload.payload.delayed_telemetry_start_time_month
    :field delayed_telemetry_start_time_day: ax25_frame.payload.payload.delayed_telemetry_start_time_day
    :field delayed_telemetry_start_time_hour: ax25_frame.payload.payload.delayed_telemetry_start_time_hour
    :field delayed_telemetry_start_time_minute: ax25_frame.payload.payload.delayed_telemetry_start_time_minute
    :field delayed_telemetry_start_time_second: ax25_frame.payload.payload.delayed_telemetry_start_time_second
    :field delayed_telemetry_interval_time_hour: ax25_frame.payload.payload.delayed_telemetry_interval_time_hour
    :field delayed_telemetry_interval_time_minute: ax25_frame.payload.payload.delayed_telemetry_interval_time_minute
    :field delayed_telemetry_interval_time_second: ax25_frame.payload.payload.delayed_telemetry_interval_time_second
    :field delayed_telemetry_frequency_h: ax25_frame.payload.payload.delayed_telemetry_frequency_h
    :field delayed_telemetry_frequency_m: ax25_frame.payload.payload.delayed_telemetry_frequency_m
    :field delayed_telemetry_frequency_l: ax25_frame.payload.payload.delayed_telemetry_frequency_l
    :field cam_controller_operating_current: ax25_frame.payload.payload.cam_controller_operating_current
    :field cam_controller_operating_voltage_integer: ax25_frame.payload.payload.cam_controller_operating_voltage_integer
    :field cam_controller_operating_voltage_decimal: ax25_frame.payload.payload.cam_controller_operating_voltage_decimal
    :field total_cam_current: ax25_frame.payload.payload.total_cam_current
    :field cam_working_status: ax25_frame.payload.payload.cam_working_status
    :field cam1_photo_counter: ax25_frame.payload.payload.cam1_photo_counter
    :field cam2_photo_counter: ax25_frame.payload.payload.cam2_photo_counter
    :field cam3_photo_counter: ax25_frame.payload.payload.cam3_photo_counter
    :field cam1_delayed_photography_start_time_year: ax25_frame.payload.payload.cam1_delayed_photography_start_time_year
    :field cam1_delayed_photography_start_time_month: ax25_frame.payload.payload.cam1_delayed_photography_start_time_month
    :field cam1_delayed_photography_start_time_day: ax25_frame.payload.payload.cam1_delayed_photography_start_time_day
    :field cam1_delayed_photography_start_time_hour: ax25_frame.payload.payload.cam1_delayed_photography_start_time_hour
    :field cam1_delayed_photography_start_time_minute: ax25_frame.payload.payload.cam1_delayed_photography_start_time_minute
    :field cam1_delayed_photography_start_time_second: ax25_frame.payload.payload.cam1_delayed_photography_start_time_second
    :field cam1_delayed_photography_interval_time_hour: ax25_frame.payload.payload.cam1_delayed_photography_interval_time_hour
    :field cam1_delayed_photography_interval_time_minute: ax25_frame.payload.payload.cam1_delayed_photography_interval_time_minute
    :field cam1_delayed_photography_interval_time_second: ax25_frame.payload.payload.cam1_delayed_photography_interval_time_second
    :field cam1_delayed_photography_frequency: ax25_frame.payload.payload.cam1_delayed_photography_frequency
    :field cam2_delayed_photography_start_time_year: ax25_frame.payload.payload.cam2_delayed_photography_start_time_year
    :field cam2_delayed_photography_start_time_month: ax25_frame.payload.payload.cam2_delayed_photography_start_time_month
    :field cam2_delayed_photography_start_time_day: ax25_frame.payload.payload.cam2_delayed_photography_start_time_day
    :field cam2_delayed_photography_start_time_hour: ax25_frame.payload.payload.cam2_delayed_photography_start_time_hour
    :field cam2_delayed_photography_start_time_minute: ax25_frame.payload.payload.cam2_delayed_photography_start_time_minute
    :field cam2_delayed_photography_start_time_second: ax25_frame.payload.payload.cam2_delayed_photography_start_time_second
    :field cam2_delayed_photography_interval_time_hour: ax25_frame.payload.payload.cam2_delayed_photography_interval_time_hour
    :field cam2_delayed_photography_interval_time_minute: ax25_frame.payload.payload.cam2_delayed_photography_interval_time_minute
    :field cam2_delayed_photography_interval_time_second: ax25_frame.payload.payload.cam2_delayed_photography_interval_time_second
    :field cam2_delayed_photography_frequency: ax25_frame.payload.payload.cam2_delayed_photography_frequency
    :field cam3_delayed_photography_start_time_year: ax25_frame.payload.payload.cam3_delayed_photography_start_time_year
    :field cam3_delayed_photography_start_time_month: ax25_frame.payload.payload.cam3_delayed_photography_start_time_month
    :field cam3_delayed_photography_start_time_day: ax25_frame.payload.payload.cam3_delayed_photography_start_time_day
    :field cam3_delayed_photography_start_time_hour: ax25_frame.payload.payload.cam3_delayed_photography_start_time_hour
    :field cam3_delayed_photography_start_time_minute: ax25_frame.payload.payload.cam3_delayed_photography_start_time_minute
    :field cam3_delayed_photography_start_time_second: ax25_frame.payload.payload.cam3_delayed_photography_start_time_second
    :field cam3_delayed_photography_interval_time_hour: ax25_frame.payload.payload.cam3_delayed_photography_interval_time_hour
    :field cam3_delayed_photography_interval_time_minute: ax25_frame.payload.payload.cam3_delayed_photography_interval_time_minute
    :field cam3_delayed_photography_interval_time_second: ax25_frame.payload.payload.cam3_delayed_photography_interval_time_second
    :field cam3_delayed_photography_frequency: ax25_frame.payload.payload.cam3_delayed_photography_frequency
    :field satellite_current_operating_mode: ax25_frame.payload.payload.satellite_current_operating_mode
    :field satellite_device_switch_status: ax25_frame.payload.payload.satellite_device_switch_status
    :field time_48hrs_reset_year: ax25_frame.payload.payload.time_48hrs_reset_year
    :field time_48hrs_reset_month: ax25_frame.payload.payload.time_48hrs_reset_month
    :field time_48hrs_reset_day: ax25_frame.payload.payload.time_48hrs_reset_day
    :field time_48hrs_reset_hour: ax25_frame.payload.payload.time_48hrs_reset_hour
    :field time_48hrs_reset_minute: ax25_frame.payload.payload.time_48hrs_reset_minute
    :field time_48hrs_reset_second: ax25_frame.payload.payload.time_48hrs_reset_second
    :field att_q0_l: ax25_frame.payload.payload.att_q0_l
    :field att_q0_h: ax25_frame.payload.payload.att_q0_h
    :field att_q1_l: ax25_frame.payload.payload.att_q1_l
    :field att_q1_h: ax25_frame.payload.payload.att_q1_h
    :field att_q2_l: ax25_frame.payload.payload.att_q2_l
    :field att_q2_h: ax25_frame.payload.payload.att_q2_h
    :field att_q3_l: ax25_frame.payload.payload.att_q3_l
    :field att_q3_h: ax25_frame.payload.payload.att_q3_h
    :field cam1_resolution: ax25_frame.payload.payload.cam1_resolution
    :field cam1_image_quality: ax25_frame.payload.payload.cam1_image_quality
    :field cam2_resolution: ax25_frame.payload.payload.cam2_resolution
    :field cam2_image_quality: ax25_frame.payload.payload.cam2_image_quality
    :field cam3_resolution: ax25_frame.payload.payload.cam3_resolution
    :field cam3_image_quality: ax25_frame.payload.payload.cam3_image_quality
    :field current_delayed_telemetry_interval_time_hour: ax25_frame.payload.payload.current_delayed_telemetry_interval_time_hour
    :field current_delayed_telemetry_interval_time_minute: ax25_frame.payload.payload.current_delayed_telemetry_interval_time_minute
    :field current_delayed_telemetry_interval_time_second: ax25_frame.payload.payload.current_delayed_telemetry_interval_time_second
    :field photo_cat_info_content_0_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.year
    :field photo_cat_info_content_0_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.month
    :field photo_cat_info_content_0_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.day
    :field photo_cat_info_content_0_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.hour
    :field photo_cat_info_content_0_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.minute
    :field photo_cat_info_content_0_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.second
    :field photo_cat_info_content_0_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_0.meta
    :field photo_cat_info_content_1_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.year
    :field photo_cat_info_content_1_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.month
    :field photo_cat_info_content_1_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.day
    :field photo_cat_info_content_1_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.hour
    :field photo_cat_info_content_1_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.minute
    :field photo_cat_info_content_1_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.second
    :field photo_cat_info_content_1_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_1.meta
    :field photo_cat_info_content_2_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.year
    :field photo_cat_info_content_2_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.month
    :field photo_cat_info_content_2_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.day
    :field photo_cat_info_content_2_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.hour
    :field photo_cat_info_content_2_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.minute
    :field photo_cat_info_content_2_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.second
    :field photo_cat_info_content_2_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_2.meta
    :field photo_cat_info_content_3_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.year
    :field photo_cat_info_content_3_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.month
    :field photo_cat_info_content_3_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.day
    :field photo_cat_info_content_3_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.hour
    :field photo_cat_info_content_3_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.minute
    :field photo_cat_info_content_3_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.second
    :field photo_cat_info_content_3_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_3.meta
    :field photo_cat_info_content_4_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.year
    :field photo_cat_info_content_4_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.month
    :field photo_cat_info_content_4_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.day
    :field photo_cat_info_content_4_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.hour
    :field photo_cat_info_content_4_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.minute
    :field photo_cat_info_content_4_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.second
    :field photo_cat_info_content_4_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_4.meta
    :field photo_cat_info_content_5_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.year
    :field photo_cat_info_content_5_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.month
    :field photo_cat_info_content_5_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.day
    :field photo_cat_info_content_5_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.hour
    :field photo_cat_info_content_5_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.minute
    :field photo_cat_info_content_5_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.second
    :field photo_cat_info_content_5_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_5.meta
    :field photo_cat_info_content_6_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.year
    :field photo_cat_info_content_6_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.month
    :field photo_cat_info_content_6_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.day
    :field photo_cat_info_content_6_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.hour
    :field photo_cat_info_content_6_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.minute
    :field photo_cat_info_content_6_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.second
    :field photo_cat_info_content_6_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_6.meta
    :field photo_cat_info_content_7_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.year
    :field photo_cat_info_content_7_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.month
    :field photo_cat_info_content_7_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.day
    :field photo_cat_info_content_7_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.hour
    :field photo_cat_info_content_7_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.minute
    :field photo_cat_info_content_7_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.second
    :field photo_cat_info_content_7_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_7.meta
    :field photo_cat_info_content_8_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.year
    :field photo_cat_info_content_8_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.month
    :field photo_cat_info_content_8_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.day
    :field photo_cat_info_content_8_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.hour
    :field photo_cat_info_content_8_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.minute
    :field photo_cat_info_content_8_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.second
    :field photo_cat_info_content_8_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_8.meta
    :field photo_cat_info_content_9_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.year
    :field photo_cat_info_content_9_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.month
    :field photo_cat_info_content_9_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.day
    :field photo_cat_info_content_9_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.hour
    :field photo_cat_info_content_9_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.minute
    :field photo_cat_info_content_9_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.second
    :field photo_cat_info_content_9_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_9.meta
    :field photo_cat_info_content_10_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.year
    :field photo_cat_info_content_10_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.month
    :field photo_cat_info_content_10_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.day
    :field photo_cat_info_content_10_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.hour
    :field photo_cat_info_content_10_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.minute
    :field photo_cat_info_content_10_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.second
    :field photo_cat_info_content_10_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_10.meta
    :field photo_cat_info_content_11_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.year
    :field photo_cat_info_content_11_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.month
    :field photo_cat_info_content_11_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.day
    :field photo_cat_info_content_11_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.hour
    :field photo_cat_info_content_11_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.minute
    :field photo_cat_info_content_11_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.second
    :field photo_cat_info_content_11_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_11.meta
    :field photo_cat_info_content_12_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.year
    :field photo_cat_info_content_12_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.month
    :field photo_cat_info_content_12_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.day
    :field photo_cat_info_content_12_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.hour
    :field photo_cat_info_content_12_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.minute
    :field photo_cat_info_content_12_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.second
    :field photo_cat_info_content_12_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_12.meta
    :field photo_cat_info_content_13_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.year
    :field photo_cat_info_content_13_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.month
    :field photo_cat_info_content_13_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.day
    :field photo_cat_info_content_13_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.hour
    :field photo_cat_info_content_13_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.minute
    :field photo_cat_info_content_13_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.second
    :field photo_cat_info_content_13_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_13.meta
    :field photo_cat_info_content_14_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.year
    :field photo_cat_info_content_14_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.month
    :field photo_cat_info_content_14_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.day
    :field photo_cat_info_content_14_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.hour
    :field photo_cat_info_content_14_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.minute
    :field photo_cat_info_content_14_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.second
    :field photo_cat_info_content_14_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_14.meta
    :field photo_cat_info_content_15_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.year
    :field photo_cat_info_content_15_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.month
    :field photo_cat_info_content_15_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.day
    :field photo_cat_info_content_15_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.hour
    :field photo_cat_info_content_15_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.minute
    :field photo_cat_info_content_15_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.second
    :field photo_cat_info_content_15_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_15.meta
    :field photo_cat_info_content_16_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.year
    :field photo_cat_info_content_16_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.month
    :field photo_cat_info_content_16_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.day
    :field photo_cat_info_content_16_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.hour
    :field photo_cat_info_content_16_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.minute
    :field photo_cat_info_content_16_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.second
    :field photo_cat_info_content_16_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_16.meta
    :field photo_cat_info_content_17_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.year
    :field photo_cat_info_content_17_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.month
    :field photo_cat_info_content_17_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.day
    :field photo_cat_info_content_17_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.hour
    :field photo_cat_info_content_17_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.minute
    :field photo_cat_info_content_17_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.second
    :field photo_cat_info_content_17_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_17.meta
    :field photo_cat_info_content_18_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.year
    :field photo_cat_info_content_18_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.month
    :field photo_cat_info_content_18_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.day
    :field photo_cat_info_content_18_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.hour
    :field photo_cat_info_content_18_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.minute
    :field photo_cat_info_content_18_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.second
    :field photo_cat_info_content_18_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_18.meta
    :field photo_cat_info_content_19_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.year
    :field photo_cat_info_content_19_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.month
    :field photo_cat_info_content_19_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.day
    :field photo_cat_info_content_19_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.hour
    :field photo_cat_info_content_19_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.minute
    :field photo_cat_info_content_19_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.second
    :field photo_cat_info_content_19_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_19.meta
    :field photo_cat_info_content_20_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.year
    :field photo_cat_info_content_20_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.month
    :field photo_cat_info_content_20_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.day
    :field photo_cat_info_content_20_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.hour
    :field photo_cat_info_content_20_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.minute
    :field photo_cat_info_content_20_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.second
    :field photo_cat_info_content_20_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_20.meta
    :field photo_cat_info_content_21_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.year
    :field photo_cat_info_content_21_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.month
    :field photo_cat_info_content_21_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.day
    :field photo_cat_info_content_21_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.hour
    :field photo_cat_info_content_21_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.minute
    :field photo_cat_info_content_21_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.second
    :field photo_cat_info_content_21_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_21.meta
    :field photo_cat_info_content_22_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.year
    :field photo_cat_info_content_22_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.month
    :field photo_cat_info_content_22_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.day
    :field photo_cat_info_content_22_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.hour
    :field photo_cat_info_content_22_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.minute
    :field photo_cat_info_content_22_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.second
    :field photo_cat_info_content_22_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_22.meta
    :field photo_cat_info_content_23_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.year
    :field photo_cat_info_content_23_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.month
    :field photo_cat_info_content_23_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.day
    :field photo_cat_info_content_23_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.hour
    :field photo_cat_info_content_23_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.minute
    :field photo_cat_info_content_23_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.second
    :field photo_cat_info_content_23_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_23.meta
    :field photo_cat_info_content_24_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.year
    :field photo_cat_info_content_24_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.month
    :field photo_cat_info_content_24_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.day
    :field photo_cat_info_content_24_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.hour
    :field photo_cat_info_content_24_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.minute
    :field photo_cat_info_content_24_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.second
    :field photo_cat_info_content_24_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_24.meta
    :field photo_cat_info_content_25_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.year
    :field photo_cat_info_content_25_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.month
    :field photo_cat_info_content_25_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.day
    :field photo_cat_info_content_25_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.hour
    :field photo_cat_info_content_25_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.minute
    :field photo_cat_info_content_25_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.second
    :field photo_cat_info_content_25_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_25.meta
    :field photo_cat_info_content_26_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.year
    :field photo_cat_info_content_26_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.month
    :field photo_cat_info_content_26_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.day
    :field photo_cat_info_content_26_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.hour
    :field photo_cat_info_content_26_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.minute
    :field photo_cat_info_content_26_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.second
    :field photo_cat_info_content_26_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_26.meta
    :field photo_cat_info_content_27_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.year
    :field photo_cat_info_content_27_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.month
    :field photo_cat_info_content_27_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.day
    :field photo_cat_info_content_27_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.hour
    :field photo_cat_info_content_27_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.minute
    :field photo_cat_info_content_27_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.second
    :field photo_cat_info_content_27_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_27.meta
    :field photo_cat_info_content_28_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.year
    :field photo_cat_info_content_28_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.month
    :field photo_cat_info_content_28_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.day
    :field photo_cat_info_content_28_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.hour
    :field photo_cat_info_content_28_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.minute
    :field photo_cat_info_content_28_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.second
    :field photo_cat_info_content_28_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_28.meta
    :field photo_cat_info_content_29_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.year
    :field photo_cat_info_content_29_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.month
    :field photo_cat_info_content_29_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.day
    :field photo_cat_info_content_29_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.hour
    :field photo_cat_info_content_29_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.minute
    :field photo_cat_info_content_29_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.second
    :field photo_cat_info_content_29_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_29.meta
    :field photo_cat_info_content_30_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.year
    :field photo_cat_info_content_30_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.month
    :field photo_cat_info_content_30_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.day
    :field photo_cat_info_content_30_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.hour
    :field photo_cat_info_content_30_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.minute
    :field photo_cat_info_content_30_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.second
    :field photo_cat_info_content_30_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_30.meta
    :field photo_cat_info_content_31_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.year
    :field photo_cat_info_content_31_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.month
    :field photo_cat_info_content_31_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.day
    :field photo_cat_info_content_31_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.hour
    :field photo_cat_info_content_31_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.minute
    :field photo_cat_info_content_31_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.second
    :field photo_cat_info_content_31_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_31.meta
    :field photo_cat_info_content_32_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.year
    :field photo_cat_info_content_32_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.month
    :field photo_cat_info_content_32_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.day
    :field photo_cat_info_content_32_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.hour
    :field photo_cat_info_content_32_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.minute
    :field photo_cat_info_content_32_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.second
    :field photo_cat_info_content_32_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_32.meta
    :field photo_cat_info_content_33_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.year
    :field photo_cat_info_content_33_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.month
    :field photo_cat_info_content_33_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.day
    :field photo_cat_info_content_33_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.hour
    :field photo_cat_info_content_33_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.minute
    :field photo_cat_info_content_33_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.second
    :field photo_cat_info_content_33_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_33.meta
    :field photo_cat_info_content_34_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.year
    :field photo_cat_info_content_34_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.month
    :field photo_cat_info_content_34_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.day
    :field photo_cat_info_content_34_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.hour
    :field photo_cat_info_content_34_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.minute
    :field photo_cat_info_content_34_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.second
    :field photo_cat_info_content_34_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_34.meta
    :field photo_cat_info_content_35_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.year
    :field photo_cat_info_content_35_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.month
    :field photo_cat_info_content_35_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.day
    :field photo_cat_info_content_35_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.hour
    :field photo_cat_info_content_35_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.minute
    :field photo_cat_info_content_35_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.second
    :field photo_cat_info_content_35_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_35.meta
    :field photo_cat_info_content_36_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.year
    :field photo_cat_info_content_36_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.month
    :field photo_cat_info_content_36_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.day
    :field photo_cat_info_content_36_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.hour
    :field photo_cat_info_content_36_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.minute
    :field photo_cat_info_content_36_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.second
    :field photo_cat_info_content_36_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_36.meta
    :field photo_cat_info_content_37_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.year
    :field photo_cat_info_content_37_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.month
    :field photo_cat_info_content_37_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.day
    :field photo_cat_info_content_37_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.hour
    :field photo_cat_info_content_37_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.minute
    :field photo_cat_info_content_37_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.second
    :field photo_cat_info_content_37_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_37.meta
    :field photo_cat_info_content_38_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.year
    :field photo_cat_info_content_38_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.month
    :field photo_cat_info_content_38_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.day
    :field photo_cat_info_content_38_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.hour
    :field photo_cat_info_content_38_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.minute
    :field photo_cat_info_content_38_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.second
    :field photo_cat_info_content_38_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_38.meta
    :field photo_cat_info_content_39_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.year
    :field photo_cat_info_content_39_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.month
    :field photo_cat_info_content_39_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.day
    :field photo_cat_info_content_39_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.hour
    :field photo_cat_info_content_39_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.minute
    :field photo_cat_info_content_39_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.second
    :field photo_cat_info_content_39_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_39.meta
    :field photo_cat_info_content_40_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.year
    :field photo_cat_info_content_40_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.month
    :field photo_cat_info_content_40_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.day
    :field photo_cat_info_content_40_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.hour
    :field photo_cat_info_content_40_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.minute
    :field photo_cat_info_content_40_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.second
    :field photo_cat_info_content_40_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_40.meta
    :field photo_cat_info_content_41_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.year
    :field photo_cat_info_content_41_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.month
    :field photo_cat_info_content_41_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.day
    :field photo_cat_info_content_41_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.hour
    :field photo_cat_info_content_41_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.minute
    :field photo_cat_info_content_41_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.second
    :field photo_cat_info_content_41_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_41.meta
    :field photo_cat_info_content_42_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.year
    :field photo_cat_info_content_42_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.month
    :field photo_cat_info_content_42_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.day
    :field photo_cat_info_content_42_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.hour
    :field photo_cat_info_content_42_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.minute
    :field photo_cat_info_content_42_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.second
    :field photo_cat_info_content_42_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_42.meta
    :field photo_cat_info_content_43_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.year
    :field photo_cat_info_content_43_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.month
    :field photo_cat_info_content_43_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.day
    :field photo_cat_info_content_43_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.hour
    :field photo_cat_info_content_43_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.minute
    :field photo_cat_info_content_43_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.second
    :field photo_cat_info_content_43_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_43.meta
    :field photo_cat_info_content_44_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.year
    :field photo_cat_info_content_44_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.month
    :field photo_cat_info_content_44_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.day
    :field photo_cat_info_content_44_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.hour
    :field photo_cat_info_content_44_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.minute
    :field photo_cat_info_content_44_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.second
    :field photo_cat_info_content_44_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_44.meta
    :field photo_cat_info_content_45_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.year
    :field photo_cat_info_content_45_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.month
    :field photo_cat_info_content_45_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.day
    :field photo_cat_info_content_45_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.hour
    :field photo_cat_info_content_45_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.minute
    :field photo_cat_info_content_45_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.second
    :field photo_cat_info_content_45_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_45.meta
    :field photo_cat_info_content_46_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.year
    :field photo_cat_info_content_46_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.month
    :field photo_cat_info_content_46_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.day
    :field photo_cat_info_content_46_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.hour
    :field photo_cat_info_content_46_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.minute
    :field photo_cat_info_content_46_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.second
    :field photo_cat_info_content_46_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_46.meta
    :field photo_cat_info_content_47_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.year
    :field photo_cat_info_content_47_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.month
    :field photo_cat_info_content_47_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.day
    :field photo_cat_info_content_47_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.hour
    :field photo_cat_info_content_47_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.minute
    :field photo_cat_info_content_47_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.second
    :field photo_cat_info_content_47_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_47.meta
    :field photo_cat_info_content_48_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.year
    :field photo_cat_info_content_48_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.month
    :field photo_cat_info_content_48_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.day
    :field photo_cat_info_content_48_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.hour
    :field photo_cat_info_content_48_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.minute
    :field photo_cat_info_content_48_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.second
    :field photo_cat_info_content_48_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_48.meta
    :field photo_cat_info_content_49_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.year
    :field photo_cat_info_content_49_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.month
    :field photo_cat_info_content_49_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.day
    :field photo_cat_info_content_49_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.hour
    :field photo_cat_info_content_49_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.minute
    :field photo_cat_info_content_49_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.second
    :field photo_cat_info_content_49_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_49.meta
    :field photo_cat_info_content_50_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.year
    :field photo_cat_info_content_50_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.month
    :field photo_cat_info_content_50_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.day
    :field photo_cat_info_content_50_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.hour
    :field photo_cat_info_content_50_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.minute
    :field photo_cat_info_content_50_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.second
    :field photo_cat_info_content_50_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_50.meta
    :field photo_cat_info_content_51_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.year
    :field photo_cat_info_content_51_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.month
    :field photo_cat_info_content_51_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.day
    :field photo_cat_info_content_51_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.hour
    :field photo_cat_info_content_51_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.minute
    :field photo_cat_info_content_51_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.second
    :field photo_cat_info_content_51_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_51.meta
    :field photo_cat_info_content_52_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.year
    :field photo_cat_info_content_52_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.month
    :field photo_cat_info_content_52_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.day
    :field photo_cat_info_content_52_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.hour
    :field photo_cat_info_content_52_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.minute
    :field photo_cat_info_content_52_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.second
    :field photo_cat_info_content_52_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_52.meta
    :field photo_cat_info_content_53_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.year
    :field photo_cat_info_content_53_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.month
    :field photo_cat_info_content_53_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.day
    :field photo_cat_info_content_53_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.hour
    :field photo_cat_info_content_53_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.minute
    :field photo_cat_info_content_53_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.second
    :field photo_cat_info_content_53_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_53.meta
    :field photo_cat_info_content_54_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.year
    :field photo_cat_info_content_54_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.month
    :field photo_cat_info_content_54_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.day
    :field photo_cat_info_content_54_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.hour
    :field photo_cat_info_content_54_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.minute
    :field photo_cat_info_content_54_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.second
    :field photo_cat_info_content_54_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_54.meta
    :field photo_cat_info_content_55_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.year
    :field photo_cat_info_content_55_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.month
    :field photo_cat_info_content_55_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.day
    :field photo_cat_info_content_55_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.hour
    :field photo_cat_info_content_55_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.minute
    :field photo_cat_info_content_55_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.second
    :field photo_cat_info_content_55_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_55.meta
    :field photo_cat_info_content_56_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.year
    :field photo_cat_info_content_56_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.month
    :field photo_cat_info_content_56_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.day
    :field photo_cat_info_content_56_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.hour
    :field photo_cat_info_content_56_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.minute
    :field photo_cat_info_content_56_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.second
    :field photo_cat_info_content_56_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_56.meta
    :field photo_cat_info_content_57_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.year
    :field photo_cat_info_content_57_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.month
    :field photo_cat_info_content_57_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.day
    :field photo_cat_info_content_57_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.hour
    :field photo_cat_info_content_57_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.minute
    :field photo_cat_info_content_57_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.second
    :field photo_cat_info_content_57_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_57.meta
    :field photo_cat_info_content_58_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.year
    :field photo_cat_info_content_58_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.month
    :field photo_cat_info_content_58_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.day
    :field photo_cat_info_content_58_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.hour
    :field photo_cat_info_content_58_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.minute
    :field photo_cat_info_content_58_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.second
    :field photo_cat_info_content_58_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_58.meta
    :field photo_cat_info_content_59_year: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.year
    :field photo_cat_info_content_59_month: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.month
    :field photo_cat_info_content_59_day: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.day
    :field photo_cat_info_content_59_hour: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.hour
    :field photo_cat_info_content_59_minute: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.minute
    :field photo_cat_info_content_59_second: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.second
    :field photo_cat_info_content_59_meta: ax25_frame.payload.payload.photo_cat_data.photo_cat_info_content_59.meta
    :field total_nr_of_frames: ax25_frame.payload.payload.photo_header.total_nr_of_frames
    :field frame_seq_nr: ax25_frame.payload.payload.photo_header.frame_seq_nr
    :field frame_length: ax25_frame.payload.payload.photo_header.frame_length
    :field photo_meta_year: ax25_frame.payload.payload.photo_meta.year
    :field photo_meta_month: ax25_frame.payload.payload.photo_meta.month
    :field photo_meta_day: ax25_frame.payload.payload.photo_meta.day
    :field photo_meta_hour: ax25_frame.payload.payload.photo_meta.hour
    :field photo_meta_minute: ax25_frame.payload.payload.photo_meta.minute
    :field photo_meta_second: ax25_frame.payload.payload.photo_meta.second
    :field cam_meta: ax25_frame.payload.payload.photo_meta.cam_meta
    :field photo_specs: ax25_frame.payload.payload.photo_meta.photo_specs
    :field data_str: ax25_frame.payload.payload.photo_data.data.data_str
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Cas5a.Ax25Frame(self._io, self, self._root)

    class PhotoMetaT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()
            self.cam_meta = self._io.read_u2be()
            self.photo_specs = self._io.read_u1()


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Cas5a.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Cas5a.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Cas5a.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Cas5a.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Cas5a.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Cas5a.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Cas5a.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Cas5a.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Cas5a.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Cas5a.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Cas5a.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Cas5a.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class PhotoCatSecondFrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.photo_cat_info_content_30 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_31 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_32 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_33 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_34 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_35 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_36 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_37 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_38 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_39 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_40 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_41 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_42 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_43 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_44 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_45 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_46 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_47 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_48 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_49 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_50 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_51 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_52 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_53 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_54 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_55 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_56 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_57 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_58 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_59 = Cas5a.PhotoCatInfoT(self._io, self, self._root)


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.function_code_main = self._io.read_u1()
            if self.function_code_main != 3:
                self.function_code_spare1 = self._io.read_u1()

            if self.function_code_main != 3:
                self.function_code_sub = self._io.read_u1()

            if self.function_code_main != 3:
                self.function_code_sub_spare1 = self._io.read_u1()

            if self.function_code_main != 3:
                self.sub_function_code_main = self._io.read_u2be()
                if not  ((self.sub_function_code_main == 256) or (self.sub_function_code_main == 512)) :
                    raise kaitaistruct.ValidationNotAnyOfError(self.sub_function_code_main, self._io, u"/types/ui_frame/seq/5")

            if self.function_code_main != 3:
                self.function_rev = self._io.read_u1()

            _on = self.function_code_main
            if _on == 1:
                self._raw_payload = self._io.read_bytes_full()
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Cas5a.TelemetryT(_io__raw_payload, self, self._root)
            elif _on == 2:
                self._raw_payload = self._io.read_bytes_full()
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Cas5a.PhotoCatT(_io__raw_payload, self, self._root)
            elif _on == 3:
                self._raw_payload = self._io.read_bytes_full()
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Cas5a.PhotoDataT(_io__raw_payload, self, self._root)
            else:
                self.payload = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"CAS5A ") or (self.callsign == u"CQ    ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class StrB64T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_str = (self._io.read_bytes_full()).decode(u"ASCII")


    class PhotoCatFirstFrameT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.photo_cat_info_content_0 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_1 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_2 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_3 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_4 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_5 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_6 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_7 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_8 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_9 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_10 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_11 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_12 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_13 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_14 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_15 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_16 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_17 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_18 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_19 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_20 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_21 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_22 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_23 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_24 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_25 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_26 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_27 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_28 = Cas5a.PhotoCatInfoT(self._io, self, self._root)
            self.photo_cat_info_content_29 = Cas5a.PhotoCatInfoT(self._io, self, self._root)


    class PhotoCatT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.sub_function_code_main
            if _on == 1:
                self.photo_cat_data = Cas5a.PhotoCatFirstFrameT(self._io, self, self._root)
            elif _on == 2:
                self.photo_cat_data = Cas5a.PhotoCatSecondFrameT(self._io, self, self._root)


    class DataB64T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_data = self._io.read_bytes_full()
            _process = satnogsdecoders.process.B64encode()
            self._raw_data = _process.decode(self._raw__raw_data)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = Cas5a.StrB64T(_io__raw_data, self, self._root)


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class PhotoCatInfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.year = self._io.read_u1()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u1()
            self.meta = self._io.read_u2be()


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


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Cas5a.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Cas5a.SsidMask(self._io, self, self._root)


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
                _ = Cas5a.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class PhotoDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.photo_header = Cas5a.PhotoHeaderT(self._io, self, self._root)
            self.photo_meta = Cas5a.PhotoMetaT(self._io, self, self._root)
            self.photo_data = Cas5a.DataB64T(self._io, self, self._root)


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
            self.callsign_ror = Cas5a.Callsign(_io__raw_callsign_ror, self, self._root)


    class TelemetryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sat_time_year = self._io.read_u1()
            self.sat_time_month = self._io.read_u1()
            self.sat_time_day = self._io.read_u1()
            self.sat_time_hour = self._io.read_u1()
            self.sat_time_minute = self._io.read_u1()
            self.sat_time_second = self._io.read_u1()
            self.ihu_total_reset_counter = self._io.read_u1()
            self.battery_status = self._io.read_u1()
            self.remote_control_frame_reception_counter = self._io.read_u1()
            self.remote_control_command_execution_counter = self._io.read_u1()
            self.telemetry_frame_transmission_counter = self._io.read_u1()
            self.ihu_status_1 = self._io.read_u1()
            self.reserved_00 = self._io.read_u1()
            self.i2c_bus_status = self._io.read_u1()
            self.reserved_01 = self._io.read_u1()
            self.reserved_02 = self._io.read_u1()
            self.reserved_03 = self._io.read_u1()
            self.ihu_status_2 = self._io.read_u1()
            self.ihu_status_3 = self._io.read_u1()
            self.px_cabin_inner_plate_temp = self._io.read_u1()
            self.nx_cabin_inner_plate_temp = self._io.read_u1()
            self.pdcu_temp = self._io.read_u1()
            self.dcdc_temp = self._io.read_u1()
            self.pz_cabin_inner_plate_temp = self._io.read_u1()
            self.nz_cabin_inner_plate_temp = self._io.read_u1()
            self.px_solar_array_temp = self._io.read_u1()
            self.nx_solar_array_temp = self._io.read_u1()
            self.py_solar_array_temp = self._io.read_u1()
            self.ny_solar_array_temp = self._io.read_u1()
            self.pz_solar_array_temp = self._io.read_u1()
            self.nz_solar_array_temp = self._io.read_u1()
            self.bat_pack_1_temp_1 = self._io.read_u1()
            self.bat_pack_1_temp_2 = self._io.read_u1()
            self.bat_pack_2_temp_3 = self._io.read_u1()
            self.bat_pack_2_temp_4 = self._io.read_u1()
            self.ihu_temp = self._io.read_u1()
            self.uhf1_pa_temp = self._io.read_u1()
            self.cam3_temp = self._io.read_u1()
            self.cam1_temp = self._io.read_u1()
            self.cam2_temp = self._io.read_u1()
            self.uhf2_pa_temp = self._io.read_u1()
            self.battery_voltage_integer = self._io.read_u1()
            self.battery_voltage_decimal = self._io.read_u1()
            self.primary_power_supply_integer = self._io.read_u1()
            self.primary_power_supply_decimal = self._io.read_u1()
            self.bus_voltage_5v_integer = self._io.read_u1()
            self.bus_voltage_5v_decimal = self._io.read_u1()
            self.bus_voltage_3v8_integer = self._io.read_u1()
            self.bus_voltage_3v8_decimal = self._io.read_u1()
            self.ihu_voltage_3v3_integer = self._io.read_u1()
            self.ihu_voltage_3v3_decimal = self._io.read_u1()
            self.total_solar_array_current = self._io.read_u2be()
            self.primary_bus_current = self._io.read_u2be()
            self.total_load_current = self._io.read_u2be()
            self.ihu_current = self._io.read_u2be()
            self.reserved_04 = self._io.read_u2be()
            self.hf_receiver_current = self._io.read_u2be()
            self.reserved_05 = self._io.read_u2be()
            self.uhf_transmitter_2_current = self._io.read_u2be()
            self.ht_agc_voltage_integer = self._io.read_u1()
            self.ht_agc_voltage_decimal = self._io.read_u1()
            self.uhf_transmitter_1_current = self._io.read_u2be()
            self.uhf1_rf_power = self._io.read_u2be()
            self.uhf2_rf_power = self._io.read_u2be()
            self.vhf_receiver_current = self._io.read_u2be()
            self.vhf_agc_voltage_integer = self._io.read_u1()
            self.vhf_agc_voltage_decimal = self._io.read_u1()
            self.delayed_telemetry_start_time_year = self._io.read_u1()
            self.delayed_telemetry_start_time_month = self._io.read_u1()
            self.delayed_telemetry_start_time_day = self._io.read_u1()
            self.delayed_telemetry_start_time_hour = self._io.read_u1()
            self.delayed_telemetry_start_time_minute = self._io.read_u1()
            self.delayed_telemetry_start_time_second = self._io.read_u1()
            self.delayed_telemetry_interval_time_hour = self._io.read_u1()
            self.delayed_telemetry_interval_time_minute = self._io.read_u1()
            self.delayed_telemetry_interval_time_second = self._io.read_u1()
            self.delayed_telemetry_frequency_h = self._io.read_u1()
            self.delayed_telemetry_frequency_m = self._io.read_u1()
            self.delayed_telemetry_frequency_l = self._io.read_u1()
            self.cam_controller_operating_current = self._io.read_u2be()
            self.cam_controller_operating_voltage_integer = self._io.read_u1()
            self.cam_controller_operating_voltage_decimal = self._io.read_u1()
            self.total_cam_current = self._io.read_u2be()
            self.cam_working_status = self._io.read_u1()
            self.cam1_photo_counter = self._io.read_u2be()
            self.cam2_photo_counter = self._io.read_u2be()
            self.cam3_photo_counter = self._io.read_u2be()
            self.cam1_delayed_photography_start_time_year = self._io.read_u1()
            self.cam1_delayed_photography_start_time_month = self._io.read_u1()
            self.cam1_delayed_photography_start_time_day = self._io.read_u1()
            self.cam1_delayed_photography_start_time_hour = self._io.read_u1()
            self.cam1_delayed_photography_start_time_minute = self._io.read_u1()
            self.cam1_delayed_photography_start_time_second = self._io.read_u1()
            self.cam1_delayed_photography_interval_time_hour = self._io.read_u1()
            self.cam1_delayed_photography_interval_time_minute = self._io.read_u1()
            self.cam1_delayed_photography_interval_time_second = self._io.read_u1()
            self.cam1_delayed_photography_frequency = self._io.read_u1()
            self.cam2_delayed_photography_start_time_year = self._io.read_u1()
            self.cam2_delayed_photography_start_time_month = self._io.read_u1()
            self.cam2_delayed_photography_start_time_day = self._io.read_u1()
            self.cam2_delayed_photography_start_time_hour = self._io.read_u1()
            self.cam2_delayed_photography_start_time_minute = self._io.read_u1()
            self.cam2_delayed_photography_start_time_second = self._io.read_u1()
            self.cam2_delayed_photography_interval_time_hour = self._io.read_u1()
            self.cam2_delayed_photography_interval_time_minute = self._io.read_u1()
            self.cam2_delayed_photography_interval_time_second = self._io.read_u1()
            self.cam2_delayed_photography_frequency = self._io.read_u1()
            self.cam3_delayed_photography_start_time_year = self._io.read_u1()
            self.cam3_delayed_photography_start_time_month = self._io.read_u1()
            self.cam3_delayed_photography_start_time_day = self._io.read_u1()
            self.cam3_delayed_photography_start_time_hour = self._io.read_u1()
            self.cam3_delayed_photography_start_time_minute = self._io.read_u1()
            self.cam3_delayed_photography_start_time_second = self._io.read_u1()
            self.cam3_delayed_photography_interval_time_hour = self._io.read_u1()
            self.cam3_delayed_photography_interval_time_minute = self._io.read_u1()
            self.cam3_delayed_photography_interval_time_second = self._io.read_u1()
            self.cam3_delayed_photography_frequency = self._io.read_u1()
            self.satellite_current_operating_mode = self._io.read_u1()
            self.satellite_device_switch_status = self._io.read_u2be()
            self.time_48hrs_reset_year = self._io.read_u1()
            self.time_48hrs_reset_month = self._io.read_u1()
            self.time_48hrs_reset_day = self._io.read_u1()
            self.time_48hrs_reset_hour = self._io.read_u1()
            self.time_48hrs_reset_minute = self._io.read_u1()
            self.time_48hrs_reset_second = self._io.read_u1()
            self.att_q0_l = self._io.read_u1()
            self.att_q0_h = self._io.read_u1()
            self.att_q1_l = self._io.read_u1()
            self.att_q1_h = self._io.read_u1()
            self.att_q2_l = self._io.read_u1()
            self.att_q2_h = self._io.read_u1()
            self.att_q3_l = self._io.read_u1()
            self.att_q3_h = self._io.read_u1()
            self.cam1_resolution = self._io.read_u1()
            self.cam1_image_quality = self._io.read_u1()
            self.cam2_resolution = self._io.read_u1()
            self.cam2_image_quality = self._io.read_u1()
            self.cam3_resolution = self._io.read_u1()
            self.cam3_image_quality = self._io.read_u1()
            self.current_delayed_telemetry_interval_time_hour = self._io.read_u1()
            self.current_delayed_telemetry_interval_time_minute = self._io.read_u1()
            self.current_delayed_telemetry_interval_time_second = self._io.read_u1()


    class PhotoHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.total_nr_of_frames = self._io.read_u2be()
            self.frame_seq_nr = self._io.read_u2be()
            self.frame_length = self._io.read_u2be()



