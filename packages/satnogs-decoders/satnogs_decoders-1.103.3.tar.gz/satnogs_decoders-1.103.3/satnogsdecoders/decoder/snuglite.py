# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Snuglite(KaitaiStruct):
    """:field destination_callsign: beacon_types.type_check.destination_callsign
    :field source_callsign: beacon_types.type_check.source_callsign
    :field csp_header_priority: beacon_types.type_check.csp_header_priority
    :field csp_header_source: beacon_types.type_check.csp_header_source
    :field csp_header_destination: beacon_types.type_check.csp_header_destination
    :field csp_header_destination_port: beacon_types.type_check.csp_header_destination_port
    :field csp_header_source_port: beacon_types.type_check.csp_header_source_port
    :field csp_header_reserved: beacon_types.type_check.csp_header_reserved
    :field csp_header_flags: beacon_types.type_check.csp_header_flags
    :field firmware_version: beacon_types.type_check.firmware_version
    :field positioning_flag: beacon_types.type_check.positioning_flag
    :field position_x: beacon_types.type_check.position_x
    :field position_y: beacon_types.type_check.position_y
    :field position_z: beacon_types.type_check.position_z
    :field velocity_x: beacon_types.type_check.velocity_x
    :field velocity_y: beacon_types.type_check.velocity_y
    :field velocity_z: beacon_types.type_check.velocity_z
    :field battery_mode: beacon_types.type_check.battery_mode
    :field battery_voltage: beacon_types.type_check.battery_voltage
    :field battery_current: beacon_types.type_check.battery_current
    :field power_switch_gps_side: beacon_types.type_check.power_switch_gps_side
    :field power_switch_magnetometer: beacon_types.type_check.power_switch_magnetometer
    :field power_switch_sd_card: beacon_types.type_check.power_switch_sd_card
    :field power_switch_gps_up: beacon_types.type_check.power_switch_gps_up
    :field power_switch_uhf: beacon_types.type_check.power_switch_uhf
    :field power_switch_boom: beacon_types.type_check.power_switch_boom
    :field power_supply_current_boom: beacon_types.type_check.power_supply_current_boom
    :field power_supply_current_uhf: beacon_types.type_check.power_supply_current_uhf
    :field power_supply_current_gps_up: beacon_types.type_check.power_supply_current_gps_up
    :field power_supply_current_sd_card: beacon_types.type_check.power_supply_current_sd_card
    :field power_supply_current_magnetometer: beacon_types.type_check.power_supply_current_magnetometer
    :field power_supply_current_gps_side: beacon_types.type_check.power_supply_current_gps_side
    :field solar_cell_input_voltage_x: beacon_types.type_check.solar_cell_input_voltage_x
    :field solar_cell_input_voltage_y: beacon_types.type_check.solar_cell_input_voltage_y
    :field solar_cell_input_voltage_z: beacon_types.type_check.solar_cell_input_voltage_z
    :field solar_cell_input_current_x: beacon_types.type_check.solar_cell_input_current_x
    :field solar_cell_input_current_y: beacon_types.type_check.solar_cell_input_current_y
    :field solar_cell_input_current_z: beacon_types.type_check.solar_cell_input_current_z
    :field estimated_attitude_q0: beacon_types.type_check.estimated_attitude_q0
    :field estimated_attitude_q1: beacon_types.type_check.estimated_attitude_q1
    :field estimated_attitude_q2: beacon_types.type_check.estimated_attitude_q2
    :field estimated_attitude_q3: beacon_types.type_check.estimated_attitude_q3
    :field estimated_gyro_bias_roll: beacon_types.type_check.estimated_gyro_bias_roll
    :field estimated_gyro_bias_pitch: beacon_types.type_check.estimated_gyro_bias_pitch
    :field estimated_gyro_bias_yaw: beacon_types.type_check.estimated_gyro_bias_yaw
    :field estimated_angular_rate_roll: beacon_types.type_check.estimated_angular_rate_roll
    :field estimated_angular_rate_pitch: beacon_types.type_check.estimated_angular_rate_pitch
    :field estimated_angular_rate_yaw: beacon_types.type_check.estimated_angular_rate_yaw
    :field measured_angular_rate_roll: beacon_types.type_check.measured_angular_rate_roll
    :field measured_angular_rate_pitch: beacon_types.type_check.measured_angular_rate_pitch
    :field measured_angular_rate_yaw: beacon_types.type_check.measured_angular_rate_yaw
    :field sun_eclipse: beacon_types.type_check.sun_eclipse
    :field attitude_convergence: beacon_types.type_check.attitude_convergence
    :field attitude_variance_q0: beacon_types.type_check.attitude_variance_q0
    :field attitude_variance_q1: beacon_types.type_check.attitude_variance_q1
    :field attitude_variance_q2: beacon_types.type_check.attitude_variance_q2
    :field attitude_variance_q3: beacon_types.type_check.attitude_variance_q3
    :field current_operation_mode: beacon_types.type_check.current_operation_mode
    :field elapsed_time: beacon_types.type_check.elapsed_time
    :field temperature_solar_panel_plus_x: beacon_types.type_check.temperature_solar_panel_plus_x
    :field temperature_solar_panel_plus_y: beacon_types.type_check.temperature_solar_panel_plus_y
    :field temperature_solar_panel_minus_x: beacon_types.type_check.temperature_solar_panel_minus_x
    :field temperature_solar_panel_minus_y: beacon_types.type_check.temperature_solar_panel_minus_y
    :field temperature_solar_panel_minus_z: beacon_types.type_check.temperature_solar_panel_minus_z
    :field temperature_obc_1: beacon_types.type_check.temperature_obc_1
    :field temperature_obc_2: beacon_types.type_check.temperature_obc_2
    :field temperature_eps_module_1: beacon_types.type_check.temperature_eps_module_1
    :field temperature_eps_module_2: beacon_types.type_check.temperature_eps_module_2
    :field temperature_eps_module_3: beacon_types.type_check.temperature_eps_module_3
    :field temperature_eps_module_4: beacon_types.type_check.temperature_eps_module_4
    :field temperature_uhf_module_1: beacon_types.type_check.temperature_uhf_module_1
    :field temperature_uhf_module_2: beacon_types.type_check.temperature_uhf_module_2
    :field boom_release_status: beacon_types.type_check.boom_release_status
    :field antenna_release_status: beacon_types.type_check.antenna_release_status
    :field count_antenna_release_trial: beacon_types.type_check.count_antenna_release_trial
    :field count_boom_release_trial: beacon_types.type_check.count_boom_release_trial
    :field beacon_type: beacon_types.type_check.beacon_type
    :field satellite_time: beacon_types.type_check.satellite_time
    
    .. seealso::
       Source - https://snuglitecubesat.wixsite.com/website/post/snuglite-beacon-structure
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.beacon_types = Snuglite.BeaconTypesT(self._io, self, self._root)

    class BeaconTypesT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 1011438661:
                self.type_check = Snuglite.Simple(self._io, self, self._root)
            else:
                self.type_check = Snuglite.Full(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(61)
            self._m_check = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class Full(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.destination_callsign = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.destination_callsign == u"DS0DH":
                raise kaitaistruct.ValidationNotEqualError(u"DS0DH", self.destination_callsign, self._io, u"/types/full/seq/0")
            self.last_digit_of_destination_callsign_and_destination_ssid = self._io.read_u2be()
            self.source_callsign = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.source_callsign == u"DS0DH":
                raise kaitaistruct.ValidationNotEqualError(u"DS0DH", self.source_callsign, self._io, u"/types/full/seq/2")
            self.last_digit_of_source_callsign_and_source_ssid = self._io.read_u2be()
            self.control_and_pid = self._io.read_u2be()
            self.csp_header_priority = self._io.read_bits_int_be(2)
            self.csp_header_source = self._io.read_bits_int_be(5)
            self.csp_header_destination = self._io.read_bits_int_be(5)
            self.csp_header_destination_port = self._io.read_bits_int_be(6)
            self.csp_header_source_port = self._io.read_bits_int_be(6)
            self.csp_header_reserved = self._io.read_bits_int_be(4)
            self.csp_header_flags = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.start_id = (self._io.read_bytes(6)).decode(u"UTF-8")
            if not self.start_id == u"SNUGL>":
                raise kaitaistruct.ValidationNotEqualError(u"SNUGL>", self.start_id, self._io, u"/types/full/seq/12")
            self.firmware_version = self._io.read_u1()
            self.time_year = self._io.read_u1()
            self.time_month = self._io.read_u1()
            self.time_day = self._io.read_u1()
            self.time_hour = self._io.read_u1()
            self.time_minute = self._io.read_u1()
            self.time_second = self._io.read_u1()
            self.positioning_flag = self._io.read_u1()
            self.position_x = self._io.read_s4be()
            self.position_y = self._io.read_s4be()
            self.position_z = self._io.read_s4be()
            self.velocity_x = self._io.read_s4be()
            self.velocity_y = self._io.read_s4be()
            self.velocity_z = self._io.read_s4be()
            self.battery_mode = self._io.read_u1()
            self.battery_voltage = self._io.read_u2be()
            self.battery_current = self._io.read_u2be()
            self.not_used = self._io.read_bits_int_be(2)
            self.power_switch_gps_side = self._io.read_bits_int_be(1) != 0
            self.power_switch_magnetometer = self._io.read_bits_int_be(1) != 0
            self.power_switch_sd_card = self._io.read_bits_int_be(1) != 0
            self.power_switch_gps_up = self._io.read_bits_int_be(1) != 0
            self.power_switch_uhf = self._io.read_bits_int_be(1) != 0
            self.power_switch_boom = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.power_supply_current_boom = self._io.read_u2be()
            self.power_supply_current_uhf = self._io.read_u2be()
            self.power_supply_current_gps_up = self._io.read_u2be()
            self.power_supply_current_sd_card = self._io.read_u2be()
            self.power_supply_current_magnetometer = self._io.read_u2be()
            self.power_supply_current_gps_side = self._io.read_u2be()
            self.solar_cell_input_voltage_x = self._io.read_u2be()
            self.solar_cell_input_voltage_y = self._io.read_u2be()
            self.solar_cell_input_voltage_z = self._io.read_u2be()
            self.solar_cell_input_current_x = self._io.read_u2be()
            self.solar_cell_input_current_y = self._io.read_u2be()
            self.solar_cell_input_current_z = self._io.read_u2be()
            self.estimated_attitude_q0 = self._io.read_f4be()
            self.estimated_attitude_q1 = self._io.read_f4be()
            self.estimated_attitude_q2 = self._io.read_f4be()
            self.estimated_attitude_q3 = self._io.read_f4be()
            self.estimated_gyro_bias_roll = self._io.read_f4be()
            self.estimated_gyro_bias_pitch = self._io.read_f4be()
            self.estimated_gyro_bias_yaw = self._io.read_f4be()
            self.estimated_angular_rate_roll = self._io.read_f4be()
            self.estimated_angular_rate_pitch = self._io.read_f4be()
            self.estimated_angular_rate_yaw = self._io.read_f4be()
            self.measured_angular_rate_roll = self._io.read_f4be()
            self.measured_angular_rate_pitch = self._io.read_f4be()
            self.measured_angular_rate_yaw = self._io.read_f4be()
            self.not_used_1 = self._io.read_bits_int_be(6)
            self.sun_eclipse = self._io.read_bits_int_be(1) != 0
            self.attitude_convergence = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.attitude_variance_q0 = self._io.read_f4be()
            self.attitude_variance_q1 = self._io.read_f4be()
            self.attitude_variance_q2 = self._io.read_f4be()
            self.attitude_variance_q3 = self._io.read_f4be()
            self.current_operation_mode = self._io.read_u1()
            self.elapsed_time = self._io.read_s4be()
            self.temperature_solar_panel_plus_x = self._io.read_s1()
            self.temperature_solar_panel_plus_y = self._io.read_s1()
            self.temperature_solar_panel_minus_x = self._io.read_s1()
            self.temperature_solar_panel_minus_y = self._io.read_s1()
            self.temperature_solar_panel_minus_z = self._io.read_s1()
            self.temperature_obc_1 = self._io.read_s1()
            self.temperature_obc_2 = self._io.read_s1()
            self.temperature_eps_module_1 = self._io.read_s1()
            self.temperature_eps_module_2 = self._io.read_s1()
            self.temperature_eps_module_3 = self._io.read_s1()
            self.temperature_eps_module_4 = self._io.read_s1()
            self.temperature_uhf_module_1 = self._io.read_s1()
            self.temperature_uhf_module_2 = self._io.read_s1()
            self.not_used_2 = self._io.read_bits_int_be(6)
            self.boom_release_status = self._io.read_bits_int_be(1) != 0
            self.antenna_release_status = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.count_antenna_release_trial = self._io.read_u1()
            self.count_boom_release_trial = self._io.read_u1()
            self.end_id = (self._io.read_bytes(4)).decode(u"UTF-8")
            if not self.end_id == u"<ITE":
                raise kaitaistruct.ValidationNotEqualError(u"<ITE", self.end_id, self._io, u"/types/full/seq/89")

        @property
        def month(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_month'):
                return self._m_month

            self._m_month = (u"0" + str(self.time_month) if len(str(self.time_month)) == 1 else str(self.time_month))
            return getattr(self, '_m_month', None)

        @property
        def minute(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_minute'):
                return self._m_minute

            self._m_minute = (u"0" + str(self.time_minute) if len(str(self.time_minute)) == 1 else str(self.time_minute))
            return getattr(self, '_m_minute', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            self._m_satellite_time = u"20" + self.year + u"-" + self.month + u"-" + self.day + u"T" + self.hour + u":" + self.minute + u":" + self.second + u"Z"
            return getattr(self, '_m_satellite_time', None)

        @property
        def year(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_year'):
                return self._m_year

            self._m_year = (u"0" + str(self.time_year) if len(str(self.time_year)) == 1 else str(self.time_year))
            return getattr(self, '_m_year', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = u"full"
            return getattr(self, '_m_beacon_type', None)

        @property
        def second(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_second'):
                return self._m_second

            self._m_second = (u"0" + str(self.time_second) if len(str(self.time_second)) == 1 else str(self.time_second))
            return getattr(self, '_m_second', None)

        @property
        def day(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_day'):
                return self._m_day

            self._m_day = (u"0" + str(self.time_day) if len(str(self.time_day)) == 1 else str(self.time_day))
            return getattr(self, '_m_day', None)

        @property
        def hour(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_hour'):
                return self._m_hour

            self._m_hour = (u"0" + str(self.time_hour) if len(str(self.time_hour)) == 1 else str(self.time_hour))
            return getattr(self, '_m_hour', None)


    class Simple(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.destination_callsign = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.destination_callsign == u"DS0DH":
                raise kaitaistruct.ValidationNotEqualError(u"DS0DH", self.destination_callsign, self._io, u"/types/simple/seq/0")
            self.last_digit_of_destination_callsign_and_destination_ssid = self._io.read_u2be()
            self.source_callsign = (self._io.read_bytes(5)).decode(u"UTF-8")
            if not self.source_callsign == u"DS0DH":
                raise kaitaistruct.ValidationNotEqualError(u"DS0DH", self.source_callsign, self._io, u"/types/simple/seq/2")
            self.last_digit_of_source_callsign_and_source_ssid = self._io.read_u2be()
            self.control_and_pid = self._io.read_u2be()
            self.csp_header_priority = self._io.read_bits_int_be(2)
            self.csp_header_source = self._io.read_bits_int_be(5)
            self.csp_header_destination = self._io.read_bits_int_be(5)
            self.csp_header_destination_port = self._io.read_bits_int_be(6)
            self.csp_header_source_port = self._io.read_bits_int_be(6)
            self.csp_header_reserved = self._io.read_bits_int_be(4)
            self.csp_header_flags = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.start_id = (self._io.read_bytes(6)).decode(u"UTF-8")
            if not self.start_id == u"SNUGL>":
                raise kaitaistruct.ValidationNotEqualError(u"SNUGL>", self.start_id, self._io, u"/types/simple/seq/12")
            self.firmware_version = self._io.read_u1()
            self.time_year = self._io.read_u1()
            self.time_month = self._io.read_u1()
            self.time_day = self._io.read_u1()
            self.time_hour = self._io.read_u1()
            self.time_minute = self._io.read_u1()
            self.time_second = self._io.read_u1()
            self.positioning_flag = self._io.read_u1()
            self.position_x = self._io.read_s4be()
            self.position_y = self._io.read_s4be()
            self.position_z = self._io.read_s4be()
            self.velocity_x = self._io.read_s4be()
            self.velocity_y = self._io.read_s4be()
            self.velocity_z = self._io.read_s4be()
            self.battery_mode = self._io.read_u1()
            self.battery_voltage = self._io.read_u2be()
            self.end_id = (self._io.read_bytes(4)).decode(u"UTF-8")
            if not self.end_id == u"<ITE":
                raise kaitaistruct.ValidationNotEqualError(u"<ITE", self.end_id, self._io, u"/types/simple/seq/29")

        @property
        def month(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_month'):
                return self._m_month

            self._m_month = (u"0" + str(self.time_month) if len(str(self.time_month)) == 1 else str(self.time_month))
            return getattr(self, '_m_month', None)

        @property
        def minute(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_minute'):
                return self._m_minute

            self._m_minute = (u"0" + str(self.time_minute) if len(str(self.time_minute)) == 1 else str(self.time_minute))
            return getattr(self, '_m_minute', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            self._m_satellite_time = u"20" + self.year + u"-" + self.month + u"-" + self.day + u"T" + self.hour + u":" + self.minute + u":" + self.second + u"Z"
            return getattr(self, '_m_satellite_time', None)

        @property
        def year(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_year'):
                return self._m_year

            self._m_year = (u"0" + str(self.time_year) if len(str(self.time_year)) == 1 else str(self.time_year))
            return getattr(self, '_m_year', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = u"simple"
            return getattr(self, '_m_beacon_type', None)

        @property
        def second(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_second'):
                return self._m_second

            self._m_second = (u"0" + str(self.time_second) if len(str(self.time_second)) == 1 else str(self.time_second))
            return getattr(self, '_m_second', None)

        @property
        def day(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_day'):
                return self._m_day

            self._m_day = (u"0" + str(self.time_day) if len(str(self.time_day)) == 1 else str(self.time_day))
            return getattr(self, '_m_day', None)

        @property
        def hour(self):
            """only for calculation, do not display."""
            if hasattr(self, '_m_hour'):
                return self._m_hour

            self._m_hour = (u"0" + str(self.time_hour) if len(str(self.time_hour)) == 1 else str(self.time_hour))
            return getattr(self, '_m_hour', None)



