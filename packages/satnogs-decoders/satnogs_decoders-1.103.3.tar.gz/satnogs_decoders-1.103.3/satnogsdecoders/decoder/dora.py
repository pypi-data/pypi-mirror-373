# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Dora(KaitaiStruct):
    """:field openlst_header_uart_start_seq: uart_start_seq
    :field openlst_header_packet_size: packet_size
    :field openlst_header_destination_hwid: destination_hwid
    :field openlst_header_sequence_number: sequence_number
    :field openlst_header_system_byte: system_byte
    :field callsign: callsign
    :field ccsds_version: ccsds_frame.ccsds_header.ccsds_version
    :field ccsds_packet_type: ccsds_frame.ccsds_header.packet_type
    :field ccsds_secondary_header_flag: ccsds_frame.ccsds_header.secondary_header_flag
    :field ccsds_apid: ccsds_frame.ccsds_header.apid
    :field ccsds_sequence_flags: ccsds_frame.ccsds_header.sequence_flags
    :field ccsds_sequence_count: ccsds_frame.ccsds_header.sequence_count
    :field ccsds_packet_length: ccsds_frame.ccsds_header.packet_length
    :field obc_timestamp: ccsds_frame.ccsds_data.timestamp
    :field obc_missionticks: ccsds_frame.ccsds_data.missionticks
    :field obc_state: ccsds_frame.ccsds_data.state
    :field obc_received_packets: ccsds_frame.ccsds_data.received_packets
    :field obc_last_logged_error_thread: ccsds_frame.ccsds_data.last_logged_error_thread
    :field obc_last_logged_error_code: ccsds_frame.ccsds_data.last_logged_error_code
    :field obc_obc_reboot_count: ccsds_frame.ccsds_data.obc_reboot_count
    :field adcs_adcs_commissioning_done_flag: ccsds_frame.ccsds_data.adcs_telemetry.adcs_commissioning_done_flag
    :field adcs_adcs_current_commissioning_state: ccsds_frame.ccsds_data.adcs_telemetry.adcs_current_commissioning_state
    :field adcs_boot_status: ccsds_frame.ccsds_data.adcs_telemetry.boot_status
    :field adcs_boot_count: ccsds_frame.ccsds_data.adcs_telemetry.boot_count
    :field adcs_current_adcs_controlmode: ccsds_frame.ccsds_data.adcs_telemetry.current_adcs_controlmode
    :field adcs_current_adcs_attitudeestimation: ccsds_frame.ccsds_data.adcs_telemetry.current_adcs_attitudeestimation
    :field adcs_cubesense2_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubesense2_enabled
    :field adcs_cubesense1_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubesense1_enabled
    :field adcs_cubecontrolmotor_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrolmotor_enabled
    :field adcs_cubecontrolsignal_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrolsignal_enabled
    :field adcs_asgp4_mode: ccsds_frame.ccsds_data.adcs_telemetry.asgp4_mode
    :field adcs_currentadcs_adcs_run_mode: ccsds_frame.ccsds_data.adcs_telemetry.currentadcs_adcs_run_mode
    :field adcs_sun_is_above_local_horizon: ccsds_frame.ccsds_data.adcs_telemetry.sun_is_above_local_horizon
    :field adcs_motor_driver_enabled: ccsds_frame.ccsds_data.adcs_telemetry.motor_driver_enabled
    :field adcs_gps_lna_power_enabled: ccsds_frame.ccsds_data.adcs_telemetry.gps_lna_power_enabled
    :field adcs_gps_receiver_enable: ccsds_frame.ccsds_data.adcs_telemetry.gps_receiver_enable
    :field adcs_cubestar_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubestar_enabled
    :field adcs_cubewheel3_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel3_enabled
    :field adcs_cubewheel2_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel2_enabled
    :field adcs_cubewheel1_enabled: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel1_enabled
    :field adcs_cubestar_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubestar_comms_error
    :field adcs_cubewheel3_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel3_comms_error
    :field adcs_cubewheel2_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel2_comms_error
    :field adcs_cubewheel1_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubewheel1_comms_error
    :field adcs_cubecontrol_motor_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrol_motor_comms_error
    :field adcs_cubecontrol_signal_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrol_signal_comms_error
    :field adcs_cubesense2_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubesense2_comms_error
    :field adcs_cubesense1_comms_error: ccsds_frame.ccsds_data.adcs_telemetry.cubesense1_comms_error
    :field adcs_cam2_3v3_overcurrent_detected: ccsds_frame.ccsds_data.adcs_telemetry.cam2_3v3_overcurrent_detected
    :field adcs_cam2_sram_overcurrent_detected: ccsds_frame.ccsds_data.adcs_telemetry.cam2_sram_overcurrent_detected
    :field adcs_sun_sensor_range_error: ccsds_frame.ccsds_data.adcs_telemetry.sun_sensor_range_error
    :field adcs_cam1_sensor_detection_error: ccsds_frame.ccsds_data.adcs_telemetry.cam1_sensor_detection_error
    :field adcs_cam1_sensor_busy_error: ccsds_frame.ccsds_data.adcs_telemetry.cam1_sensor_busy_error
    :field adcs_cam1_3v3_overcurrent_detected: ccsds_frame.ccsds_data.adcs_telemetry.cam1_3v3_overcurrent_detected
    :field adcs_cam1_sram_overcurrent_detected: ccsds_frame.ccsds_data.adcs_telemetry.cam1_sram_overcurrent_detected
    :field adcs_magnetometer_range_error: ccsds_frame.ccsds_data.adcs_telemetry.magnetometer_range_error
    :field adcs_star_tracker_overcurrent_detected: ccsds_frame.ccsds_data.adcs_telemetry.star_tracker_overcurrent_detected
    :field adcs_startracker_match_error: ccsds_frame.ccsds_data.adcs_telemetry.startracker_match_error
    :field adcs_coarse_sun_sensor_error: ccsds_frame.ccsds_data.adcs_telemetry.coarse_sun_sensor_error
    :field adcs_wheel_speed_range_error: ccsds_frame.ccsds_data.adcs_telemetry.wheel_speed_range_error
    :field adcs_rate_sensor_range_error: ccsds_frame.ccsds_data.adcs_telemetry.rate_sensor_range_error
    :field adcs_nadir_sensor_range_error: ccsds_frame.ccsds_data.adcs_telemetry.nadir_sensor_range_error
    :field adcs_cam2_sensor_detection_error: ccsds_frame.ccsds_data.adcs_telemetry.cam2_sensor_detection_error
    :field adcs_cam2_sensor_busy_error: ccsds_frame.ccsds_data.adcs_telemetry.cam2_sensor_busy_error
    :field adcs_cubecontrl_cur_3v3: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrl_cur_3v3
    :field adcs_cubecontrl_cur_5v: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrl_cur_5v
    :field adcs_cubecontrol_cur_vbat: ccsds_frame.ccsds_data.adcs_telemetry.cubecontrol_cur_vbat
    :field adcs_fine_est_ang_rates_x: ccsds_frame.ccsds_data.adcs_telemetry.fine_est_ang_rates_x
    :field adcs_fine_est_ang_rates_y: ccsds_frame.ccsds_data.adcs_telemetry.fine_est_ang_rates_y
    :field adcs_fine_est_ang_rates_z: ccsds_frame.ccsds_data.adcs_telemetry.fine_est_ang_rates_z
    :field adcs_fine_sv_x: ccsds_frame.ccsds_data.adcs_telemetry.fine_sv_x
    :field adcs_fine_sv_y: ccsds_frame.ccsds_data.adcs_telemetry.fine_sv_y
    :field adcs_fine_sv_z: ccsds_frame.ccsds_data.adcs_telemetry.fine_sv_z
    :field adcs_mcu_temp: ccsds_frame.ccsds_data.adcs_telemetry.mcu_temp
    :field adcs_temp_mag: ccsds_frame.ccsds_data.adcs_telemetry.temp_mag
    :field adcs_temp_redmag: ccsds_frame.ccsds_data.adcs_telemetry.temp_redmag
    :field adcs_wheel1_current: ccsds_frame.ccsds_data.adcs_telemetry.wheel1_current
    :field adcs_wheel2_current: ccsds_frame.ccsds_data.adcs_telemetry.wheel2_current
    :field adcs_wheel3_current: ccsds_frame.ccsds_data.adcs_telemetry.wheel3_current
    :field adcs_magnetorquer_current: ccsds_frame.ccsds_data.adcs_telemetry.magnetorquer_current
    :field adcs_cubesenes1_3v3_current: ccsds_frame.ccsds_data.adcs_telemetry.cubesenes1_3v3_current
    :field adcs_cubesenes1_sram_current: ccsds_frame.ccsds_data.adcs_telemetry.cubesenes1_sram_current
    :field adcs_cubesenes2_3v3_current: ccsds_frame.ccsds_data.adcs_telemetry.cubesenes2_3v3_current
    :field adcs_cubesenes2_sram_current: ccsds_frame.ccsds_data.adcs_telemetry.cubesenes2_sram_current
    :field eps_output_voltage_battery: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_battery
    :field eps_output_current_battery: ccsds_frame.ccsds_data.eps_telemetry.output_current_battery
    :field eps_bcr_output_current: ccsds_frame.ccsds_data.eps_telemetry.bcr_output_current
    :field eps_motherboard_temperature: ccsds_frame.ccsds_data.eps_telemetry.motherboard_temperature
    :field eps_actual_pdm_states_unused: ccsds_frame.ccsds_data.eps_telemetry.actual_pdm_states_unused
    :field eps_sdr_actual_switch_state: ccsds_frame.ccsds_data.eps_telemetry.sdr_actual_switch_state
    :field eps_cm4_pdm_actual_switch_state: ccsds_frame.ccsds_data.eps_telemetry.cm4_pdm_actual_switch_state
    :field eps_sipm_pdm_actual_switch_state: ccsds_frame.ccsds_data.eps_telemetry.sipm_pdm_actual_switch_state
    :field eps_pdm_actual_switch_state_unused2: ccsds_frame.ccsds_data.eps_telemetry.pdm_actual_switch_state_unused2
    :field eps_daughterboard_temperature: ccsds_frame.ccsds_data.eps_telemetry.daughterboard_temperature
    :field eps_output_current_5v: ccsds_frame.ccsds_data.eps_telemetry.output_current_5v
    :field eps_output_voltage_5v: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_5v
    :field eps_output_current_3v3: ccsds_frame.ccsds_data.eps_telemetry.output_current_3v3
    :field eps_output_voltage_3v3: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_3v3
    :field eps_output_voltage_switch_5: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_switch_5
    :field eps_output_current_switch_5: ccsds_frame.ccsds_data.eps_telemetry.output_current_switch_5
    :field eps_output_voltage_switch_6: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_switch_6
    :field eps_output_current_switch_6: ccsds_frame.ccsds_data.eps_telemetry.output_current_switch_6
    :field eps_output_voltage_switch_7: ccsds_frame.ccsds_data.eps_telemetry.output_voltage_switch_7
    :field eps_output_current_switch_7: ccsds_frame.ccsds_data.eps_telemetry.output_current_switch_7
    :field eps_voltage_feeding_bcr6: ccsds_frame.ccsds_data.eps_telemetry.voltage_feeding_bcr6
    :field eps_current_bcr6_connector_sa6a: ccsds_frame.ccsds_data.eps_telemetry.current_bcr6_connector_sa6a
    :field eps_current_bcr6_connector_sa6b: ccsds_frame.ccsds_data.eps_telemetry.current_bcr6_connector_sa6b
    :field eps_voltage_feeding_bcr7: ccsds_frame.ccsds_data.eps_telemetry.voltage_feeding_bcr7
    :field eps_current_bcr7_connector_sa7a: ccsds_frame.ccsds_data.eps_telemetry.current_bcr7_connector_sa7a
    :field eps_current_bcr7_connector_sa7b: ccsds_frame.ccsds_data.eps_telemetry.current_bcr7_connector_sa7b
    :field eps_voltage_feeding_bcr8: ccsds_frame.ccsds_data.eps_telemetry.voltage_feeding_bcr8
    :field eps_current_bcr8_connector_sa8a: ccsds_frame.ccsds_data.eps_telemetry.current_bcr8_connector_sa8a
    :field eps_current_bcr8_connector_sa8b: ccsds_frame.ccsds_data.eps_telemetry.current_bcr8_connector_sa8b
    :field eps_voltage_feeding_bcr9: ccsds_frame.ccsds_data.eps_telemetry.voltage_feeding_bcr9
    :field eps_current_bcr9_connector_sa9a: ccsds_frame.ccsds_data.eps_telemetry.current_bcr9_connector_sa9a
    :field eps_current_bcr9_connector_sa9b: ccsds_frame.ccsds_data.eps_telemetry.current_bcr9_connector_sa9b
    :field battery_motherboard_temperature: ccsds_frame.ccsds_data.battery_telemetry.motherboard_temperature
    :field battery_output_voltage_battery: ccsds_frame.ccsds_data.battery_telemetry.output_voltage_battery
    :field battery_current_magnitude: ccsds_frame.ccsds_data.battery_telemetry.current_magnitude
    :field battery_daughter_temp1: ccsds_frame.ccsds_data.battery_telemetry.daughter_temp1
    :field battery_daughter_temp2: ccsds_frame.ccsds_data.battery_telemetry.daughter_temp2
    :field battery_daughter_temp3: ccsds_frame.ccsds_data.battery_telemetry.daughter_temp3
    :field battery_heater_status1: ccsds_frame.ccsds_data.battery_telemetry.heater_status1
    :field battery_heater_status2: ccsds_frame.ccsds_data.battery_telemetry.heater_status2
    :field battery_heater_status3: ccsds_frame.ccsds_data.battery_telemetry.heater_status3
    :field battery_current_direction: ccsds_frame.ccsds_data.battery_telemetry.current_direction
    :field payload_sipm_adc_value: ccsds_frame.ccsds_data.payload_telemetry_1.sipm_adc_value
    :field payload_current_payload_schedule: ccsds_frame.ccsds_data.payload_telemetry_1.current_payload_schedule
    :field payload_timestamp: ccsds_frame.ccsds_data.payload_telemetry_1.timestamp
    :field payload_mode: ccsds_frame.ccsds_data.payload_telemetry_1.mode
    :field payload_available_storage: ccsds_frame.ccsds_data.payload_telemetry_1.available_storage
    :field payload_available_memory: ccsds_frame.ccsds_data.payload_telemetry_1.available_memory
    :field payload_cpu_load: ccsds_frame.ccsds_data.payload_telemetry_1.cpu_load
    :field payload_rpi_uptime: ccsds_frame.ccsds_data.payload_telemetry_1.rpi_uptime
    :field payload_reboot_count: ccsds_frame.ccsds_data.payload_telemetry_1.reboot_count
    :field payload_number_of_received_commands: ccsds_frame.ccsds_data.payload_telemetry_1.number_of_received_commands
    :field payload_last_received_command: ccsds_frame.ccsds_data.payload_telemetry_1.last_received_command
    :field payload_error_count: ccsds_frame.ccsds_data.payload_telemetry_1.error_count
    :field payload_filter_bank_power_ch1: ccsds_frame.ccsds_data.payload_telemetry_1.filter_bank_power_ch1
    :field payload_filter_bank_power_ch2: ccsds_frame.ccsds_data.payload_telemetry_1.filter_bank_power_ch2
    :field payload_filter_bank_power_ch2: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch3
    :field payload_filter_bank_power_ch4: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch4
    :field payload_filter_bank_power_ch5: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch5
    :field payload_filter_bank_power_ch6: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch6
    :field payload_filter_bank_power_ch7: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch7
    :field payload_filter_bank_power_ch8: ccsds_frame.ccsds_data.payload_telemetry_2.filter_bank_power_ch8
    :field payload_sdr_power: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_power
    :field payload_sdr_bright_1: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_1
    :field payload_sdr_bright_2: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_2
    :field payload_sdr_bright_3: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_3
    :field payload_sdr_bright_4: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_4
    :field payload_sdr_bright_5: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_5
    :field payload_sdr_bright_6: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_6
    :field payload_sdr_bright_7: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_7
    :field payload_sdr_bright_8: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_8
    :field payload_sdr_bright_9: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_9
    :field payload_sdr_bright_10: ccsds_frame.ccsds_data.payload_telemetry_2.sdr_bright_10
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.uart_start_seq = self._io.read_u2be()
        self.packet_size = self._io.read_u1()
        self.destination_hwid = self._io.read_u2be()
        self.sequence_number = self._io.read_u2be()
        self.system_byte = self._io.read_u1()
        self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
        if not  ((self.callsign == u"KE7DHQ")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/seq/5")
        self.dora_syncbytes = self._io.read_bytes(4)
        if not self.dora_syncbytes == b"\x35\x2E\xF8\x53":
            raise kaitaistruct.ValidationNotEqualError(b"\x35\x2E\xF8\x53", self.dora_syncbytes, self._io, u"/seq/6")
        self.ccsds_frame = Dora.CcsdsFrame(self._io, self, self._root)

    class BatteryTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.motherboard_temperature_raw = self._io.read_u2be()
            self.output_voltage_battery_raw = self._io.read_u2be()
            self.current_magnitude_raw = self._io.read_u2be()
            self.daughter_temp1_raw = self._io.read_u2be()
            self.daughter_temp2_raw = self._io.read_u2be()
            self.daughter_temp3_raw = self._io.read_u2be()
            self.heater_status1 = self._io.read_bits_int_be(1) != 0
            self.heater_status2 = self._io.read_bits_int_be(1) != 0
            self.heater_status3 = self._io.read_bits_int_be(1) != 0
            self.current_direction = self._io.read_bits_int_be(5)

        @property
        def output_voltage_battery(self):
            if hasattr(self, '_m_output_voltage_battery'):
                return self._m_output_voltage_battery

            self._m_output_voltage_battery = (self.output_voltage_battery_raw * 0.008993)
            return getattr(self, '_m_output_voltage_battery', None)

        @property
        def daughter_temp1(self):
            if hasattr(self, '_m_daughter_temp1'):
                return self._m_daughter_temp1

            self._m_daughter_temp1 = ((self.daughter_temp1_raw * 0.397600) - 238.57)
            return getattr(self, '_m_daughter_temp1', None)

        @property
        def current_magnitude(self):
            if hasattr(self, '_m_current_magnitude'):
                return self._m_current_magnitude

            self._m_current_magnitude = (self.current_magnitude_raw * 14.662757)
            return getattr(self, '_m_current_magnitude', None)

        @property
        def daughter_temp3(self):
            if hasattr(self, '_m_daughter_temp3'):
                return self._m_daughter_temp3

            self._m_daughter_temp3 = ((self.daughter_temp3_raw * 0.397600) - 238.57)
            return getattr(self, '_m_daughter_temp3', None)

        @property
        def daughter_temp2(self):
            if hasattr(self, '_m_daughter_temp2'):
                return self._m_daughter_temp2

            self._m_daughter_temp2 = ((self.daughter_temp2_raw * 0.397600) - 238.57)
            return getattr(self, '_m_daughter_temp2', None)

        @property
        def motherboard_temperature(self):
            if hasattr(self, '_m_motherboard_temperature'):
                return self._m_motherboard_temperature

            self._m_motherboard_temperature = ((self.motherboard_temperature_raw * 0.372434) - 273.15)
            return getattr(self, '_m_motherboard_temperature', None)


    class CcsdsHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_version = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.apid = self._io.read_bits_int_be(11)
            if not  ((self.apid == 3)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.apid, self._io, u"/types/ccsds_header/seq/3")
            self.sequence_flags = self._io.read_bits_int_be(2)
            self.sequence_count = self._io.read_bits_int_be(14)
            self.packet_length = self._io.read_bits_int_be(16)


    class PayloadTelemetry2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.filter_bank_power_ch3 = self._io.read_u1()
            self.filter_bank_power_ch4 = self._io.read_u1()
            self.filter_bank_power_ch5 = self._io.read_u1()
            self.filter_bank_power_ch6 = self._io.read_u1()
            self.filter_bank_power_ch7 = self._io.read_u1()
            self.filter_bank_power_ch8 = self._io.read_u1()
            self.sdr_power = self._io.read_u2be()
            self.sdr_bright_1 = self._io.read_u2be()
            self.sdr_bright_2 = self._io.read_u2be()
            self.sdr_bright_3 = self._io.read_u2be()
            self.sdr_bright_4 = self._io.read_u2be()
            self.sdr_bright_5 = self._io.read_u2be()
            self.sdr_bright_6 = self._io.read_u2be()
            self.sdr_bright_7 = self._io.read_u2be()
            self.sdr_bright_8 = self._io.read_u2be()
            self.sdr_bright_9 = self._io.read_u2be()
            self.sdr_bright_10 = self._io.read_u2be()


    class PayloadTelemetry1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sipm_adc_value = self._io.read_u2be()
            self.current_payload_schedule = self._io.read_u2be()
            self.timestamp_raw = self._io.read_u8be()
            self.mode = self._io.read_u1()
            self.available_storage = self._io.read_u4be()
            self.available_memory = self._io.read_u4be()
            self.cpu_load = self._io.read_u4be()
            self.rpi_uptime = self._io.read_u4be()
            self.reboot_count = self._io.read_u4be()
            self.number_of_received_commands = self._io.read_u4be()
            self.last_received_command = self._io.read_u1()
            self.error_count = self._io.read_u4be()
            self.filter_bank_power_ch1 = self._io.read_u1()
            self.filter_bank_power_ch2 = self._io.read_u1()

        @property
        def timestamp(self):
            if hasattr(self, '_m_timestamp'):
                return self._m_timestamp

            self._m_timestamp = (self.timestamp_raw & 4294967295)
            return getattr(self, '_m_timestamp', None)


    class AdcsTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_commissioning_done_flag = self._io.read_bits_int_be(1) != 0
            self.adcs_current_commissioning_state = self._io.read_bits_int_be(7)
            self._io.align_to_byte()
            self.boot_status = self._io.read_u1()
            self.boot_count = self._io.read_u2be()
            self.current_adcs_controlmode = self._io.read_bits_int_be(4)
            self.current_adcs_attitudeestimation = self._io.read_bits_int_be(4)
            self.cubesense2_enabled = self._io.read_bits_int_be(1) != 0
            self.cubesense1_enabled = self._io.read_bits_int_be(1) != 0
            self.cubecontrolmotor_enabled = self._io.read_bits_int_be(1) != 0
            self.cubecontrolsignal_enabled = self._io.read_bits_int_be(1) != 0
            self.asgp4_mode = self._io.read_bits_int_be(2)
            self.currentadcs_adcs_run_mode = self._io.read_bits_int_be(2)
            self.sun_is_above_local_horizon = self._io.read_bits_int_be(1) != 0
            self.motor_driver_enabled = self._io.read_bits_int_be(1) != 0
            self.gps_lna_power_enabled = self._io.read_bits_int_be(1) != 0
            self.gps_receiver_enable = self._io.read_bits_int_be(1) != 0
            self.cubestar_enabled = self._io.read_bits_int_be(1) != 0
            self.cubewheel3_enabled = self._io.read_bits_int_be(1) != 0
            self.cubewheel2_enabled = self._io.read_bits_int_be(1) != 0
            self.cubewheel1_enabled = self._io.read_bits_int_be(1) != 0
            self.cubestar_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubewheel3_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubewheel2_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubewheel1_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubecontrol_motor_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubecontrol_signal_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubesense2_comms_error = self._io.read_bits_int_be(1) != 0
            self.cubesense1_comms_error = self._io.read_bits_int_be(1) != 0
            self.cam2_3v3_overcurrent_detected = self._io.read_bits_int_be(1) != 0
            self.cam2_sram_overcurrent_detected = self._io.read_bits_int_be(1) != 0
            self.sun_sensor_range_error = self._io.read_bits_int_be(1) != 0
            self.cam1_sensor_detection_error = self._io.read_bits_int_be(1) != 0
            self.cam1_sensor_busy_error = self._io.read_bits_int_be(1) != 0
            self.cam1_3v3_overcurrent_detected = self._io.read_bits_int_be(1) != 0
            self.cam1_sram_overcurrent_detected = self._io.read_bits_int_be(1) != 0
            self.magnetometer_range_error = self._io.read_bits_int_be(1) != 0
            self.star_tracker_overcurrent_detected = self._io.read_bits_int_be(1) != 0
            self.startracker_match_error = self._io.read_bits_int_be(1) != 0
            self.coarse_sun_sensor_error = self._io.read_bits_int_be(1) != 0
            self.wheel_speed_range_error = self._io.read_bits_int_be(1) != 0
            self.rate_sensor_range_error = self._io.read_bits_int_be(1) != 0
            self.nadir_sensor_range_error = self._io.read_bits_int_be(1) != 0
            self.cam2_sensor_detection_error = self._io.read_bits_int_be(1) != 0
            self.cam2_sensor_busy_error = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.cubecontrl_cur_3v3_raw = self._io.read_u2le()
            self.cubecontrl_cur_5v_raw = self._io.read_u2le()
            self.cubecontrol_cur_vbat_raw = self._io.read_u2le()
            self.fine_est_ang_rates_x_raw = self._io.read_u2le()
            self.fine_est_ang_rates_y_raw = self._io.read_u2le()
            self.fine_est_ang_rates_z_raw = self._io.read_u2le()
            self.fine_sv_x_raw = self._io.read_u2le()
            self.fine_sv_y_raw = self._io.read_u2le()
            self.fine_sv_z_raw = self._io.read_u2le()
            self.mcu_temp = self._io.read_u2le()
            self.temp_mag_raw = self._io.read_u2le()
            self.temp_redmag_raw = self._io.read_u2le()
            self.wheel1_current_raw = self._io.read_u2le()
            self.wheel2_current_raw = self._io.read_u2le()
            self.wheel3_current_raw = self._io.read_u2le()
            self.magnetorquer_current_raw = self._io.read_u2le()
            self.cubesenes1_3v3_current_raw = self._io.read_u2le()
            self.cubesenes1_sram_current_raw = self._io.read_u2le()
            self.cubesenes2_3v3_current_raw = self._io.read_u2le()
            self.cubesenes2_sram_current_raw = self._io.read_u2le()

        @property
        def fine_est_ang_rates_x(self):
            if hasattr(self, '_m_fine_est_ang_rates_x'):
                return self._m_fine_est_ang_rates_x

            self._m_fine_est_ang_rates_x = (self.fine_est_ang_rates_x_raw * 0.001)
            return getattr(self, '_m_fine_est_ang_rates_x', None)

        @property
        def temp_redmag(self):
            if hasattr(self, '_m_temp_redmag'):
                return self._m_temp_redmag

            self._m_temp_redmag = (self.temp_redmag_raw * 0.1)
            return getattr(self, '_m_temp_redmag', None)

        @property
        def temp_mag(self):
            if hasattr(self, '_m_temp_mag'):
                return self._m_temp_mag

            self._m_temp_mag = (self.temp_mag_raw * 0.1)
            return getattr(self, '_m_temp_mag', None)

        @property
        def cubecontrl_cur_5v(self):
            if hasattr(self, '_m_cubecontrl_cur_5v'):
                return self._m_cubecontrl_cur_5v

            self._m_cubecontrl_cur_5v = (self.cubecontrl_cur_5v_raw * 0.48828125)
            return getattr(self, '_m_cubecontrl_cur_5v', None)

        @property
        def wheel3_current(self):
            if hasattr(self, '_m_wheel3_current'):
                return self._m_wheel3_current

            self._m_wheel3_current = (self.wheel3_current_raw * 0.01)
            return getattr(self, '_m_wheel3_current', None)

        @property
        def cubesenes2_3v3_current(self):
            if hasattr(self, '_m_cubesenes2_3v3_current'):
                return self._m_cubesenes2_3v3_current

            self._m_cubesenes2_3v3_current = (self.cubesenes2_3v3_current_raw * 0.01)
            return getattr(self, '_m_cubesenes2_3v3_current', None)

        @property
        def cubesenes1_3v3_current(self):
            if hasattr(self, '_m_cubesenes1_3v3_current'):
                return self._m_cubesenes1_3v3_current

            self._m_cubesenes1_3v3_current = (self.cubesenes1_3v3_current_raw * 0.01)
            return getattr(self, '_m_cubesenes1_3v3_current', None)

        @property
        def wheel2_current(self):
            if hasattr(self, '_m_wheel2_current'):
                return self._m_wheel2_current

            self._m_wheel2_current = (self.wheel2_current_raw * 0.01)
            return getattr(self, '_m_wheel2_current', None)

        @property
        def fine_est_ang_rates_z(self):
            if hasattr(self, '_m_fine_est_ang_rates_z'):
                return self._m_fine_est_ang_rates_z

            self._m_fine_est_ang_rates_z = (self.fine_est_ang_rates_z_raw * 0.001)
            return getattr(self, '_m_fine_est_ang_rates_z', None)

        @property
        def fine_sv_y(self):
            if hasattr(self, '_m_fine_sv_y'):
                return self._m_fine_sv_y

            self._m_fine_sv_y = (self.fine_sv_y_raw * 0.0001)
            return getattr(self, '_m_fine_sv_y', None)

        @property
        def fine_est_ang_rates_y(self):
            if hasattr(self, '_m_fine_est_ang_rates_y'):
                return self._m_fine_est_ang_rates_y

            self._m_fine_est_ang_rates_y = (self.fine_est_ang_rates_y_raw * 0.001)
            return getattr(self, '_m_fine_est_ang_rates_y', None)

        @property
        def magnetorquer_current(self):
            if hasattr(self, '_m_magnetorquer_current'):
                return self._m_magnetorquer_current

            self._m_magnetorquer_current = (self.magnetorquer_current_raw * 0.01)
            return getattr(self, '_m_magnetorquer_current', None)

        @property
        def cubecontrol_cur_vbat(self):
            if hasattr(self, '_m_cubecontrol_cur_vbat'):
                return self._m_cubecontrol_cur_vbat

            self._m_cubecontrol_cur_vbat = (self.cubecontrol_cur_vbat_raw * 0.48828125)
            return getattr(self, '_m_cubecontrol_cur_vbat', None)

        @property
        def cubecontrl_cur_3v3(self):
            if hasattr(self, '_m_cubecontrl_cur_3v3'):
                return self._m_cubecontrl_cur_3v3

            self._m_cubecontrl_cur_3v3 = (self.cubecontrl_cur_3v3_raw * 0.48828125)
            return getattr(self, '_m_cubecontrl_cur_3v3', None)

        @property
        def wheel1_current(self):
            if hasattr(self, '_m_wheel1_current'):
                return self._m_wheel1_current

            self._m_wheel1_current = (self.wheel1_current_raw * 0.01)
            return getattr(self, '_m_wheel1_current', None)

        @property
        def cubesenes1_sram_current(self):
            if hasattr(self, '_m_cubesenes1_sram_current'):
                return self._m_cubesenes1_sram_current

            self._m_cubesenes1_sram_current = (self.cubesenes1_sram_current_raw * 0.01)
            return getattr(self, '_m_cubesenes1_sram_current', None)

        @property
        def fine_sv_x(self):
            if hasattr(self, '_m_fine_sv_x'):
                return self._m_fine_sv_x

            self._m_fine_sv_x = (self.fine_sv_x_raw * 0.0001)
            return getattr(self, '_m_fine_sv_x', None)

        @property
        def cubesenes2_sram_current(self):
            if hasattr(self, '_m_cubesenes2_sram_current'):
                return self._m_cubesenes2_sram_current

            self._m_cubesenes2_sram_current = (self.cubesenes2_sram_current_raw * 0.01)
            return getattr(self, '_m_cubesenes2_sram_current', None)

        @property
        def fine_sv_z(self):
            if hasattr(self, '_m_fine_sv_z'):
                return self._m_fine_sv_z

            self._m_fine_sv_z = (self.fine_sv_z_raw * 0.0001)
            return getattr(self, '_m_fine_sv_z', None)


    class FirstDoraPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u8be()
            self.missionticks_raw = self._io.read_u8be()
            self.state = self._io.read_u1()
            self.received_packets = self._io.read_u4be()
            self.last_logged_error_thread = self._io.read_u1()
            self.last_logged_error_code = self._io.read_u1()
            self.obc_reboot_count = self._io.read_u4be()
            self.adcs_telemetry = Dora.AdcsTelemetry(self._io, self, self._root)
            self.eps_telemetry = Dora.EpsTelemetry(self._io, self, self._root)
            self.battery_telemetry = Dora.BatteryTelemetry(self._io, self, self._root)
            self.payload_telemetry_1 = Dora.PayloadTelemetry1(self._io, self, self._root)

        @property
        def missionticks(self):
            if hasattr(self, '_m_missionticks'):
                return self._m_missionticks

            self._m_missionticks = (self.missionticks_raw & 281474976710655)
            return getattr(self, '_m_missionticks', None)


    class EpsTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.output_voltage_battery_raw = self._io.read_u2be()
            self.output_current_battery_raw = self._io.read_u2be()
            self.bcr_output_current_raw = self._io.read_u2be()
            self.motherboard_temperature_raw = self._io.read_u2be()
            self.actual_pdm_states_unused = self._io.read_bits_int_be(8)
            self.sdr_actual_switch_state = self._io.read_bits_int_be(1) != 0
            self.cm4_pdm_actual_switch_state = self._io.read_bits_int_be(1) != 0
            self.sipm_pdm_actual_switch_state = self._io.read_bits_int_be(1) != 0
            self.pdm_actual_switch_state_unused2 = self._io.read_bits_int_be(5)
            self._io.align_to_byte()
            self.daughterboard_temperature_raw = self._io.read_u2be()
            self.output_current_5v_raw = self._io.read_u2be()
            self.output_voltage_5v_raw = self._io.read_u2be()
            self.output_current_3v3_raw = self._io.read_u2be()
            self.output_voltage_3v3_raw = self._io.read_u2be()
            self.output_voltage_switch_5_raw = self._io.read_u2be()
            self.output_current_switch_5_raw = self._io.read_u2be()
            self.output_voltage_switch_6_raw = self._io.read_u2be()
            self.output_current_switch_6_raw = self._io.read_u2be()
            self.output_voltage_switch_7_raw = self._io.read_u2be()
            self.output_current_switch_7_raw = self._io.read_u2be()
            self.voltage_feeding_bcr6_raw = self._io.read_u2be()
            self.current_bcr6_connector_sa6a_raw = self._io.read_u2be()
            self.current_bcr6_connector_sa6b_raw = self._io.read_u2be()
            self.voltage_feeding_bcr7_raw = self._io.read_u2be()
            self.current_bcr7_connector_sa7a_raw = self._io.read_u2be()
            self.current_bcr7_connector_sa7b_raw = self._io.read_u2be()
            self.voltage_feeding_bcr8_raw = self._io.read_u2be()
            self.current_bcr8_connector_sa8a_raw = self._io.read_u2be()
            self.current_bcr8_connector_sa8b_raw = self._io.read_u2be()
            self.voltage_feeding_bcr9_raw = self._io.read_u2be()
            self.current_bcr9_connector_sa9a_raw = self._io.read_u2be()
            self.current_bcr9_connector_sa9b_raw = self._io.read_u2be()

        @property
        def bcr_output_current(self):
            if hasattr(self, '_m_bcr_output_current'):
                return self._m_bcr_output_current

            self._m_bcr_output_current = (self.bcr_output_current_raw * 0.014662757)
            return getattr(self, '_m_bcr_output_current', None)

        @property
        def daughterboard_temperature(self):
            if hasattr(self, '_m_daughterboard_temperature'):
                return self._m_daughterboard_temperature

            self._m_daughterboard_temperature = ((self.motherboard_temperature_raw * 0.372434) - 273.15)
            return getattr(self, '_m_daughterboard_temperature', None)

        @property
        def output_current_switch_6(self):
            if hasattr(self, '_m_output_current_switch_6'):
                return self._m_output_current_switch_6

            self._m_output_current_switch_6 = (self.output_current_switch_6_raw * 0.001328)
            return getattr(self, '_m_output_current_switch_6', None)

        @property
        def output_voltage_battery(self):
            if hasattr(self, '_m_output_voltage_battery'):
                return self._m_output_voltage_battery

            self._m_output_voltage_battery = (self.output_voltage_battery_raw * 0.008978)
            return getattr(self, '_m_output_voltage_battery', None)

        @property
        def output_current_switch_7(self):
            if hasattr(self, '_m_output_current_switch_7'):
                return self._m_output_current_switch_7

            self._m_output_current_switch_7 = (self.output_current_switch_7_raw * 0.001328)
            return getattr(self, '_m_output_current_switch_7', None)

        @property
        def voltage_feeding_bcr9(self):
            if hasattr(self, '_m_voltage_feeding_bcr9'):
                return self._m_voltage_feeding_bcr9

            self._m_voltage_feeding_bcr9 = (self.voltage_feeding_bcr9_raw * 0.0322581)
            return getattr(self, '_m_voltage_feeding_bcr9', None)

        @property
        def current_bcr7_connector_sa7a(self):
            if hasattr(self, '_m_current_bcr7_connector_sa7a'):
                return self._m_current_bcr7_connector_sa7a

            self._m_current_bcr7_connector_sa7a = (self.current_bcr7_connector_sa7a_raw * 0.0009775)
            return getattr(self, '_m_current_bcr7_connector_sa7a', None)

        @property
        def current_bcr7_connector_sa7b(self):
            if hasattr(self, '_m_current_bcr7_connector_sa7b'):
                return self._m_current_bcr7_connector_sa7b

            self._m_current_bcr7_connector_sa7b = (self.current_bcr7_connector_sa7b_raw * 0.0009775)
            return getattr(self, '_m_current_bcr7_connector_sa7b', None)

        @property
        def output_current_battery(self):
            if hasattr(self, '_m_output_current_battery'):
                return self._m_output_current_battery

            self._m_output_current_battery = (self.output_current_battery_raw * 0.00681988679)
            return getattr(self, '_m_output_current_battery', None)

        @property
        def current_bcr9_connector_sa9b(self):
            if hasattr(self, '_m_current_bcr9_connector_sa9b'):
                return self._m_current_bcr9_connector_sa9b

            self._m_current_bcr9_connector_sa9b = (self.current_bcr9_connector_sa9b_raw * 0.0009775)
            return getattr(self, '_m_current_bcr9_connector_sa9b', None)

        @property
        def output_current_5v(self):
            if hasattr(self, '_m_output_current_5v'):
                return self._m_output_current_5v

            self._m_output_current_5v = (self.output_current_5v_raw * 0.00681988679)
            return getattr(self, '_m_output_current_5v', None)

        @property
        def output_voltage_5v(self):
            if hasattr(self, '_m_output_voltage_5v'):
                return self._m_output_voltage_5v

            self._m_output_voltage_5v = (self.output_voltage_5v_raw * 0.005865)
            return getattr(self, '_m_output_voltage_5v', None)

        @property
        def output_voltage_3v3(self):
            if hasattr(self, '_m_output_voltage_3v3'):
                return self._m_output_voltage_3v3

            self._m_output_voltage_3v3 = (self.output_voltage_3v3_raw * 0.004311)
            return getattr(self, '_m_output_voltage_3v3', None)

        @property
        def voltage_feeding_bcr8(self):
            if hasattr(self, '_m_voltage_feeding_bcr8'):
                return self._m_voltage_feeding_bcr8

            self._m_voltage_feeding_bcr8 = (self.voltage_feeding_bcr8_raw * 0.0322581)
            return getattr(self, '_m_voltage_feeding_bcr8', None)

        @property
        def voltage_feeding_bcr6(self):
            if hasattr(self, '_m_voltage_feeding_bcr6'):
                return self._m_voltage_feeding_bcr6

            self._m_voltage_feeding_bcr6 = (self.voltage_feeding_bcr6_raw * 0.0322581)
            return getattr(self, '_m_voltage_feeding_bcr6', None)

        @property
        def current_bcr9_connector_sa9a(self):
            if hasattr(self, '_m_current_bcr9_connector_sa9a'):
                return self._m_current_bcr9_connector_sa9a

            self._m_current_bcr9_connector_sa9a = (self.current_bcr9_connector_sa9a_raw * 0.0009775)
            return getattr(self, '_m_current_bcr9_connector_sa9a', None)

        @property
        def output_current_switch_5(self):
            if hasattr(self, '_m_output_current_switch_5'):
                return self._m_output_current_switch_5

            self._m_output_current_switch_5 = (self.output_current_switch_5_raw * 0.001328)
            return getattr(self, '_m_output_current_switch_5', None)

        @property
        def output_current_3v3(self):
            if hasattr(self, '_m_output_current_3v3'):
                return self._m_output_current_3v3

            self._m_output_current_3v3 = (self.output_current_3v3_raw * 0.00681988679)
            return getattr(self, '_m_output_current_3v3', None)

        @property
        def output_voltage_switch_6(self):
            if hasattr(self, '_m_output_voltage_switch_6'):
                return self._m_output_voltage_switch_6

            self._m_output_voltage_switch_6 = (self.output_voltage_switch_6_raw * 0.005865)
            return getattr(self, '_m_output_voltage_switch_6', None)

        @property
        def motherboard_temperature(self):
            if hasattr(self, '_m_motherboard_temperature'):
                return self._m_motherboard_temperature

            self._m_motherboard_temperature = ((self.motherboard_temperature_raw * 0.372434) - 273.15)
            return getattr(self, '_m_motherboard_temperature', None)

        @property
        def output_voltage_switch_5(self):
            if hasattr(self, '_m_output_voltage_switch_5'):
                return self._m_output_voltage_switch_5

            self._m_output_voltage_switch_5 = (self.output_voltage_switch_5_raw * 0.005865)
            return getattr(self, '_m_output_voltage_switch_5', None)

        @property
        def output_voltage_switch_7(self):
            if hasattr(self, '_m_output_voltage_switch_7'):
                return self._m_output_voltage_switch_7

            self._m_output_voltage_switch_7 = (self.output_voltage_switch_7_raw * 0.005865)
            return getattr(self, '_m_output_voltage_switch_7', None)

        @property
        def current_bcr8_connector_sa8a(self):
            if hasattr(self, '_m_current_bcr8_connector_sa8a'):
                return self._m_current_bcr8_connector_sa8a

            self._m_current_bcr8_connector_sa8a = (self.current_bcr8_connector_sa8a_raw * 0.0009775)
            return getattr(self, '_m_current_bcr8_connector_sa8a', None)

        @property
        def current_bcr8_connector_sa8b(self):
            if hasattr(self, '_m_current_bcr8_connector_sa8b'):
                return self._m_current_bcr8_connector_sa8b

            self._m_current_bcr8_connector_sa8b = (self.current_bcr8_connector_sa8b_raw * 0.0009775)
            return getattr(self, '_m_current_bcr8_connector_sa8b', None)

        @property
        def current_bcr6_connector_sa6b(self):
            if hasattr(self, '_m_current_bcr6_connector_sa6b'):
                return self._m_current_bcr6_connector_sa6b

            self._m_current_bcr6_connector_sa6b = (self.current_bcr6_connector_sa6b_raw * 0.0009775)
            return getattr(self, '_m_current_bcr6_connector_sa6b', None)

        @property
        def voltage_feeding_bcr7(self):
            if hasattr(self, '_m_voltage_feeding_bcr7'):
                return self._m_voltage_feeding_bcr7

            self._m_voltage_feeding_bcr7 = (self.voltage_feeding_bcr7_raw * 0.0322581)
            return getattr(self, '_m_voltage_feeding_bcr7', None)

        @property
        def current_bcr6_connector_sa6a(self):
            if hasattr(self, '_m_current_bcr6_connector_sa6a'):
                return self._m_current_bcr6_connector_sa6a

            self._m_current_bcr6_connector_sa6a = (self.current_bcr6_connector_sa6a_raw * 0.0009775)
            return getattr(self, '_m_current_bcr6_connector_sa6a', None)


    class SecondDoraPacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.payload_telemetry_2 = Dora.PayloadTelemetry2(self._io, self, self._root)


    class CcsdsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_header = Dora.CcsdsHeader(self._io, self, self._root)
            _on = self.ccsds_header.sequence_flags
            if _on == 1:
                self.ccsds_data = Dora.FirstDoraPacket(self._io, self, self._root)
            elif _on == 2:
                self.ccsds_data = Dora.SecondDoraPacket(self._io, self, self._root)



