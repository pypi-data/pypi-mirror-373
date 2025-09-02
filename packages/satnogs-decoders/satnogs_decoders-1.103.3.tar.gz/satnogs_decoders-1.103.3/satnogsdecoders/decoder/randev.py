# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Randev(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid_raw_ssid_mask: ax25_frame.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field system_leading: ax25_frame.payload.system_leading
    :field system_time: ax25_frame.payload.system_time
    :field system_mode: ax25_frame.payload.system_mode
    :field system_wod_mode: ax25_frame.payload.system_wod_mode
    :field system_wod_counter: ax25_frame.payload.system_wod_counter
    :field raw_temp: ax25_frame.payload.obc.raw_temp
    :field raw_gps: ax25_frame.payload.obc.raw_gps
    :field temp1_celcius: ax25_frame.payload.obc.temp1_celcius
    :field temp2_celcius: ax25_frame.payload.obc.temp2_celcius
    :field eps_board_status: ax25_frame.payload.eps.eps_board_status
    :field eps_pdm_status: ax25_frame.payload.eps.eps_pdm_status
    :field raw_measure: ax25_frame.payload.eps.raw_measure
    :field eps_bcr_current_ampere: ax25_frame.payload.eps.eps_bcr_current_ampere
    :field eps_bcr_voltage_volts: ax25_frame.payload.eps.eps_bcr_voltage_volts
    :field eps_3v3_current_ampere: ax25_frame.payload.eps.eps_3v3_current_ampere
    :field eps_5v_current_ampere: ax25_frame.payload.eps.eps_5v_current_ampere
    :field eps_battery_current_ampere: ax25_frame.payload.eps.eps_battery_current_ampere
    :field eps_battery_voltage_volts: ax25_frame.payload.eps.eps_battery_voltage_volts
    :field eps_sw1_current_ampere: ax25_frame.payload.eps.eps_sw1_current_ampere
    :field eps_sw1_voltage_volts: ax25_frame.payload.eps.eps_sw1_voltage_volts
    :field eps_sw2_current_ampere: ax25_frame.payload.eps.eps_sw2_current_ampere
    :field eps_sw2_voltage_volts: ax25_frame.payload.eps.eps_sw2_voltage_volts
    :field eps_sw3_voltage_volts: ax25_frame.payload.eps.eps_sw3_voltage_volts
    :field eps_sw3_current_ampere: ax25_frame.payload.eps.eps_sw3_current_ampere
    :field eps_sw4_voltage_volts: ax25_frame.payload.eps.eps_sw4_voltage_volts
    :field eps_sw4_current_ampere: ax25_frame.payload.eps.eps_sw4_current_ampere
    :field eps_sw5_voltage_volts: ax25_frame.payload.eps.eps_sw5_voltage_volts
    :field eps_sw5_current_ampere: ax25_frame.payload.eps.eps_sw5_current_ampere
    :field eps_sw6_voltage_volts: ax25_frame.payload.eps.eps_sw6_voltage_volts
    :field eps_sw6_current_ampere: ax25_frame.payload.eps.eps_sw6_current_ampere
    :field eps_sw7_voltage_volts: ax25_frame.payload.eps.eps_sw7_voltage_volts
    :field eps_sw7_current_ampere: ax25_frame.payload.eps.eps_sw7_current_ampere
    :field eps_sw8_voltage_volts: ax25_frame.payload.eps.eps_sw8_voltage_volts
    :field eps_sw8_current_ampere: ax25_frame.payload.eps.eps_sw8_current_ampere
    :field eps_sw9_voltage_volts: ax25_frame.payload.eps.eps_sw9_voltage_volts
    :field eps_sw9_current_ampere: ax25_frame.payload.eps.eps_sw9_current_ampere
    :field eps_temp_celcius: ax25_frame.payload.eps.eps_temp_celcius
    :field eps_bcr1_voltage_volts: ax25_frame.payload.eps.eps_bcr1_voltage_volts
    :field eps_bcr2_voltage_volts: ax25_frame.payload.eps.eps_bcr2_voltage_volts
    :field eps_bcr4_voltage_volts: ax25_frame.payload.eps.eps_bcr4_voltage_volts
    :field eps_bcr5_voltage_volts: ax25_frame.payload.eps.eps_bcr5_voltage_volts
    :field bat_voltage_volts: ax25_frame.payload.eps.bat_voltage_volts
    :field bat_current_ampere: ax25_frame.payload.eps.bat_current_ampere
    :field bat_temp_celcius: ax25_frame.payload.eps.bat_temp_celcius
    :field bat_heater_on: ax25_frame.payload.eps.bat_heater_on
    :field bat_heate_ctrl_on: ax25_frame.payload.eps.bat_heate_ctrl_on
    :field raw: ax25_frame.payload.comm_rx.raw
    :field comm_rx_doppler_hz: ax25_frame.payload.comm_rx.comm_rx_doppler_hz
    :field comm_rx_rssi_dbm: ax25_frame.payload.comm_rx.comm_rx_rssi_dbm
    :field comm_rx_voltage_volts: ax25_frame.payload.comm_rx.comm_rx_voltage_volts
    :field comm_rx_total_current_ampere: ax25_frame.payload.comm_rx.comm_rx_total_current_ampere
    :field comm_rx_tr_current_ampere: ax25_frame.payload.comm_rx.comm_rx_tr_current_ampere
    :field comm_rx_rx_current_ampere: ax25_frame.payload.comm_rx.comm_rx_rx_current_ampere
    :field comm_rx_pa_current_ampere: ax25_frame.payload.comm_rx.comm_rx_pa_current_ampere
    :field comm_rx_pa_temp_degree: ax25_frame.payload.comm_rx.comm_rx_pa_temp_degree
    :field comm_rx_osci_temp_degree: ax25_frame.payload.comm_rx.comm_rx_osci_temp_degree
    :field comm_tx_raw: ax25_frame.payload.comm_tx.raw
    :field comm_tx_reflected_db: ax25_frame.payload.comm_tx.comm_tx_reflected_db
    :field comm_tx_forward_db: ax25_frame.payload.comm_tx.comm_tx_forward_db
    :field comm_tx_voltage_volts: ax25_frame.payload.comm_tx.comm_tx_voltage_volts
    :field comm_tx_total_current_ampere: ax25_frame.payload.comm_tx.comm_tx_total_current_ampere
    :field comm_tx_tr_current_ampere: ax25_frame.payload.comm_tx.comm_tx_tr_current_ampere
    :field comm_tx_rx_current_ampere: ax25_frame.payload.comm_tx.comm_tx_rx_current_ampere
    :field comm_tx_pa_current_ampere: ax25_frame.payload.comm_tx.comm_tx_pa_current_ampere
    :field comm_tx_pa_temp_degree: ax25_frame.payload.comm_tx.comm_tx_pa_temp_degree
    :field comm_tx_osci_temp_degree: ax25_frame.payload.comm_tx.comm_tx_osci_temp_degree
    :field comm_antenna_raw_temp: ax25_frame.payload.comm_antenna.raw_temp
    :field notdeployed1: ax25_frame.payload.comm_antenna.notdeployed1
    :field timeout1: ax25_frame.payload.comm_antenna.timeout1
    :field deploying1: ax25_frame.payload.comm_antenna.deploying1
    :field dummy: ax25_frame.payload.comm_antenna.dummy
    :field notdeployed2: ax25_frame.payload.comm_antenna.notdeployed2
    :field timeout2: ax25_frame.payload.comm_antenna.timeout2
    :field deploying2: ax25_frame.payload.comm_antenna.deploying2
    :field ignore: ax25_frame.payload.comm_antenna.ignore
    :field notdeployed3: ax25_frame.payload.comm_antenna.notdeployed3
    :field timeout3: ax25_frame.payload.comm_antenna.timeout3
    :field deploying3: ax25_frame.payload.comm_antenna.deploying3
    :field independant_burn: ax25_frame.payload.comm_antenna.independant_burn
    :field notdeployed4: ax25_frame.payload.comm_antenna.notdeployed4
    :field timeout4: ax25_frame.payload.comm_antenna.timeout4
    :field deploying4: ax25_frame.payload.comm_antenna.deploying4
    :field armed: ax25_frame.payload.comm_antenna.armed
    :field deployment_count: ax25_frame.payload.comm_antenna.deployment_count
    :field raw_deployment_time: ax25_frame.payload.comm_antenna.raw_deployment_time
    :field temperature_celcius: ax25_frame.payload.comm_antenna.temperature_celcius
    :field deployment_time1: ax25_frame.payload.comm_antenna.deployment_time1
    :field deployment_time2: ax25_frame.payload.comm_antenna.deployment_time2
    :field deployment_time3: ax25_frame.payload.comm_antenna.deployment_time3
    :field deployment_time4: ax25_frame.payload.comm_antenna.deployment_time4
    :field estimation_mode: ax25_frame.payload.adcs.cubesense_tm190.estimation_mode
    :field control_mode: ax25_frame.payload.adcs.cubesense_tm190.control_mode
    :field adcs_mode: ax25_frame.payload.adcs.cubesense_tm190.adcs_mode
    :field asgp4_mode: ax25_frame.payload.adcs.cubesense_tm190.asgp4_mode
    :field cubecontrol_signal_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_signal_enabled
    :field cubecontrol_motor_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_motor_enabled
    :field cubesence1_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubesence1_enabled
    :field cubesence2_enable: ax25_frame.payload.adcs.cubesense_tm190.cubesence2_enable
    :field cubewheel1_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubewheel1_enabled
    :field cubewheel2_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubewheel2_enabled
    :field cubewheel3_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubewheel3_enabled
    :field cubestar_enabled: ax25_frame.payload.adcs.cubesense_tm190.cubestar_enabled
    :field gps_reciver_enabled: ax25_frame.payload.adcs.cubesense_tm190.gps_reciver_enabled
    :field gps_lna_power_enabled: ax25_frame.payload.adcs.cubesense_tm190.gps_lna_power_enabled
    :field motor_driver_enabled: ax25_frame.payload.adcs.cubesense_tm190.motor_driver_enabled
    :field sun_is_above_local_horizon: ax25_frame.payload.adcs.cubesense_tm190.sun_is_above_local_horizon
    :field errors: ax25_frame.payload.adcs.cubesense_tm190.errors
    :field cubesence1_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubesence1_comm_error
    :field cubesence2_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubesence2_comm_error
    :field cubecontrol_signal_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_signal_comm_error
    :field cubecontrol_motor_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_motor_comm_error
    :field cubewheel1_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubewheel1_comm_error
    :field cubewhee2_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubewhee2_comm_error
    :field cubewheel3_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubewheel3_comm_error
    :field cubestar_comm_error: ax25_frame.payload.adcs.cubesense_tm190.cubestar_comm_error
    :field magnetometer_range_error: ax25_frame.payload.adcs.cubesense_tm190.magnetometer_range_error
    :field sunsensor_sram_overcurrent_detected: ax25_frame.payload.adcs.cubesense_tm190.sunsensor_sram_overcurrent_detected
    :field sunsensor_3v3_overcurrent_detected: ax25_frame.payload.adcs.cubesense_tm190.sunsensor_3v3_overcurrent_detected
    :field sunsensor_busy_error: ax25_frame.payload.adcs.cubesense_tm190.sunsensor_busy_error
    :field sunsensor_detection_error: ax25_frame.payload.adcs.cubesense_tm190.sunsensor_detection_error
    :field sunsensor_range_error: ax25_frame.payload.adcs.cubesense_tm190.sunsensor_range_error
    :field nadir_sensor_sram_overcurrent_detected: ax25_frame.payload.adcs.cubesense_tm190.nadir_sensor_sram_overcurrent_detected
    :field nadir_sensor_3v3_overcurrent_detected: ax25_frame.payload.adcs.cubesense_tm190.nadir_sensor_3v3_overcurrent_detected
    :field nadir_sensor_busy_error: ax25_frame.payload.adcs.cubesense_tm190.nadir_sensor_busy_error
    :field nadir_sensor_detection_error: ax25_frame.payload.adcs.cubesense_tm190.nadir_sensor_detection_error
    :field nadir_sensor_range_error: ax25_frame.payload.adcs.cubesense_tm190.nadir_sensor_range_error
    :field rate_sensor_range_error: ax25_frame.payload.adcs.cubesense_tm190.rate_sensor_range_error
    :field wheel_speed_range_error: ax25_frame.payload.adcs.cubesense_tm190.wheel_speed_range_error
    :field coarse_sunsensor_error: ax25_frame.payload.adcs.cubesense_tm190.coarse_sunsensor_error
    :field startracker_match_error: ax25_frame.payload.adcs.cubesense_tm190.startracker_match_error
    :field startracker_overcurrent_detected: ax25_frame.payload.adcs.cubesense_tm190.startracker_overcurrent_detected
    :field orbit_parameters_invalid: ax25_frame.payload.adcs.cubesense_tm190.orbit_parameters_invalid
    :field configuration_invalid: ax25_frame.payload.adcs.cubesense_tm190.configuration_invalid
    :field control_mode_change_allowed: ax25_frame.payload.adcs.cubesense_tm190.control_mode_change_allowed
    :field estimator_change_not_allowed: ax25_frame.payload.adcs.cubesense_tm190.estimator_change_not_allowed
    :field magnetometer_mode: ax25_frame.payload.adcs.cubesense_tm190.magnetometer_mode
    :field modelled_measured_magnetic_field_missmatch: ax25_frame.payload.adcs.cubesense_tm190.modelled_measured_magnetic_field_missmatch
    :field node_recovery_error: ax25_frame.payload.adcs.cubesense_tm190.node_recovery_error
    :field cubesense1_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubesense1_runtime_error
    :field cubesense2_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubesense2_runtime_error
    :field cubecontrol_signal_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_signal_runtime_error
    :field cubecontrol_motor_untime_error: ax25_frame.payload.adcs.cubesense_tm190.cubecontrol_motor_untime_error
    :field cubewheel1_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubewheel1_runtime_error
    :field cubewheel2_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubewheel2_runtime_error
    :field cubewheel3_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubewheel3_runtime_error
    :field cubestar_runtime_error: ax25_frame.payload.adcs.cubesense_tm190.cubestar_runtime_error
    :field magnetometer_error: ax25_frame.payload.adcs.cubesense_tm190.magnetometer_error
    :field rate_sensor_failure: ax25_frame.payload.adcs.cubesense_tm190.rate_sensor_failure
    :field adcs_cubesense_tm146_raw: ax25_frame.payload.adcs.cubesense_tm146.raw
    :field roll_degree: ax25_frame.payload.adcs.cubesense_tm146.roll_degree
    :field pitch_degree: ax25_frame.payload.adcs.cubesense_tm146.pitch_degree
    :field yaw_degree: ax25_frame.payload.adcs.cubesense_tm146.yaw_degree
    :field q1: ax25_frame.payload.adcs.cubesense_tm146.q1
    :field q2: ax25_frame.payload.adcs.cubesense_tm146.q2
    :field q3: ax25_frame.payload.adcs.cubesense_tm146.q3
    :field x_angular_rate_degree_s: ax25_frame.payload.adcs.cubesense_tm146.x_angular_rate_degree_s
    :field y_angular_rate_degree_s: ax25_frame.payload.adcs.cubesense_tm146.y_angular_rate_degree_s
    :field z_angular_rate_degree_s: ax25_frame.payload.adcs.cubesense_tm146.z_angular_rate_degree_s
    :field hstx_raw: ax25_frame.payload.hstx.raw
    :field rf_output_volts: ax25_frame.payload.hstx.rf_output_volts
    :field pa_temp: ax25_frame.payload.hstx.pa_temp
    :field board_temp_top: ax25_frame.payload.hstx.board_temp_top
    :field board_temp_bottom: ax25_frame.payload.hstx.board_temp_bottom
    :field bat_current: ax25_frame.payload.hstx.bat_current
    :field bat_voltasge: ax25_frame.payload.hstx.bat_voltasge
    :field pa_current: ax25_frame.payload.hstx.pa_current
    :field pa_voltage: ax25_frame.payload.hstx.pa_voltage
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Randev.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Randev.Ax25Header(self._io, self, self._root)
            self.payload = Randev.RandevPayload(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Randev.Ax25Header.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Randev.Ax25Header.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Randev.Ax25Header.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Randev.Ax25Header.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()

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
                self.callsign_ror = Randev.Ax25Header.Callsign(_io__raw_callsign_ror, self, self._root)


        class Callsign(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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



    class RandevPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.system_leading = self._io.read_u1()
            self.system_time = self._io.read_u4le()
            self.system_mode = self._io.read_u1()
            self.system_wod_mode = self._io.read_u1()
            self.system_wod_counter = self._io.read_u2le()
            self.obc = Randev.RandevPayload.ObcInfo(self._io, self, self._root)
            self.eps = Randev.RandevPayload.EpsInfo(self._io, self, self._root)
            self.comm_rx = Randev.RandevPayload.CommRxInfo(self._io, self, self._root)
            self.comm_tx = Randev.RandevPayload.CommTxInfo(self._io, self, self._root)
            self.comm_antenna = Randev.RandevPayload.CommAntennaInfo(self._io, self, self._root)
            self.adcs = Randev.RandevPayload.AdcsInfo(self._io, self, self._root)
            self.hstx = Randev.RandevPayload.HstxInfo(self._io, self, self._root)

        class CommTxInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.raw = []
                for i in range(9):
                    self.raw.append(self._io.read_u2le())


            @property
            def comm_tx_pa_temp_degree(self):
                if hasattr(self, '_m_comm_tx_pa_temp_degree'):
                    return self._m_comm_tx_pa_temp_degree

                self._m_comm_tx_pa_temp_degree = ((-0.07669 * self.raw[7]) + 195.6038)
                return getattr(self, '_m_comm_tx_pa_temp_degree', None)

            @property
            def comm_tx_total_current_ampere(self):
                if hasattr(self, '_m_comm_tx_total_current_ampere'):
                    return self._m_comm_tx_total_current_ampere

                self._m_comm_tx_total_current_ampere = ((self.raw[3] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_tx_total_current_ampere', None)

            @property
            def comm_tx_forward_db(self):
                if hasattr(self, '_m_comm_tx_forward_db'):
                    return self._m_comm_tx_forward_db

                self._m_comm_tx_forward_db = (((self.raw[1] * self.raw[1]) * 5.887) * 0.00001)
                return getattr(self, '_m_comm_tx_forward_db', None)

            @property
            def comm_tx_tr_current_ampere(self):
                if hasattr(self, '_m_comm_tx_tr_current_ampere'):
                    return self._m_comm_tx_tr_current_ampere

                self._m_comm_tx_tr_current_ampere = ((self.raw[4] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_tx_tr_current_ampere', None)

            @property
            def comm_tx_osci_temp_degree(self):
                if hasattr(self, '_m_comm_tx_osci_temp_degree'):
                    return self._m_comm_tx_osci_temp_degree

                self._m_comm_tx_osci_temp_degree = ((-0.07669 * self.raw[8]) + 195.6038)
                return getattr(self, '_m_comm_tx_osci_temp_degree', None)

            @property
            def comm_tx_reflected_db(self):
                if hasattr(self, '_m_comm_tx_reflected_db'):
                    return self._m_comm_tx_reflected_db

                self._m_comm_tx_reflected_db = (((self.raw[0] * self.raw[0]) * 5.887) * 0.00001)
                return getattr(self, '_m_comm_tx_reflected_db', None)

            @property
            def comm_tx_voltage_volts(self):
                if hasattr(self, '_m_comm_tx_voltage_volts'):
                    return self._m_comm_tx_voltage_volts

                self._m_comm_tx_voltage_volts = (self.raw[2] * 0.00488)
                return getattr(self, '_m_comm_tx_voltage_volts', None)

            @property
            def comm_tx_pa_current_ampere(self):
                if hasattr(self, '_m_comm_tx_pa_current_ampere'):
                    return self._m_comm_tx_pa_current_ampere

                self._m_comm_tx_pa_current_ampere = ((self.raw[6] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_tx_pa_current_ampere', None)

            @property
            def comm_tx_rx_current_ampere(self):
                if hasattr(self, '_m_comm_tx_rx_current_ampere'):
                    return self._m_comm_tx_rx_current_ampere

                self._m_comm_tx_rx_current_ampere = ((self.raw[5] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_tx_rx_current_ampere', None)


        class ObcInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.raw_temp = []
                for i in range(2):
                    self.raw_temp.append(self._io.read_s2le())

                self.raw_gps = []
                for i in range(6):
                    self.raw_gps.append(self._io.read_u8le())


            @property
            def temp1_celcius(self):
                if hasattr(self, '_m_temp1_celcius'):
                    return self._m_temp1_celcius

                self._m_temp1_celcius = (self.raw_temp[0] * 0.1)
                return getattr(self, '_m_temp1_celcius', None)

            @property
            def temp2_celcius(self):
                if hasattr(self, '_m_temp2_celcius'):
                    return self._m_temp2_celcius

                self._m_temp2_celcius = (self.raw_temp[1] * 0.1)
                return getattr(self, '_m_temp2_celcius', None)


        class CommAntennaInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.raw_temp = self._io.read_u2le()
                self.notdeployed1 = self._io.read_bits_int_be(1) != 0
                self.timeout1 = self._io.read_bits_int_be(1) != 0
                self.deploying1 = self._io.read_bits_int_be(1) != 0
                self.dummy = self._io.read_bits_int_be(1) != 0
                self.notdeployed2 = self._io.read_bits_int_be(1) != 0
                self.timeout2 = self._io.read_bits_int_be(1) != 0
                self.deploying2 = self._io.read_bits_int_be(1) != 0
                self.ignore = self._io.read_bits_int_be(1) != 0
                self.notdeployed3 = self._io.read_bits_int_be(1) != 0
                self.timeout3 = self._io.read_bits_int_be(1) != 0
                self.deploying3 = self._io.read_bits_int_be(1) != 0
                self.independant_burn = self._io.read_bits_int_be(1) != 0
                self.notdeployed4 = self._io.read_bits_int_be(1) != 0
                self.timeout4 = self._io.read_bits_int_be(1) != 0
                self.deploying4 = self._io.read_bits_int_be(1) != 0
                self.armed = self._io.read_bits_int_be(1) != 0
                self._io.align_to_byte()
                self.deployment_count = []
                for i in range(4):
                    self.deployment_count.append(self._io.read_u1())

                self.raw_deployment_time = []
                for i in range(4):
                    self.raw_deployment_time.append(self._io.read_u2le())


            @property
            def deployment_time3(self):
                if hasattr(self, '_m_deployment_time3'):
                    return self._m_deployment_time3

                self._m_deployment_time3 = (self.raw_deployment_time[2] * 0.05)
                return getattr(self, '_m_deployment_time3', None)

            @property
            def deployment_time4(self):
                if hasattr(self, '_m_deployment_time4'):
                    return self._m_deployment_time4

                self._m_deployment_time4 = (self.raw_deployment_time[3] * 0.05)
                return getattr(self, '_m_deployment_time4', None)

            @property
            def deployment_time1(self):
                if hasattr(self, '_m_deployment_time1'):
                    return self._m_deployment_time1

                self._m_deployment_time1 = (self.raw_deployment_time[0] * 0.05)
                return getattr(self, '_m_deployment_time1', None)

            @property
            def temperature_celcius(self):
                if hasattr(self, '_m_temperature_celcius'):
                    return self._m_temperature_celcius

                self._m_temperature_celcius = ((-201 / (2.616 - 0.420)) * ((((self.raw_temp & 1023) * 3.3) / 1024) - 2.100))
                return getattr(self, '_m_temperature_celcius', None)

            @property
            def deployment_time2(self):
                if hasattr(self, '_m_deployment_time2'):
                    return self._m_deployment_time2

                self._m_deployment_time2 = (self.raw_deployment_time[1] * 0.05)
                return getattr(self, '_m_deployment_time2', None)


        class CommRxInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.raw = []
                for i in range(9):
                    self.raw.append(self._io.read_u2le())


            @property
            def comm_rx_rssi_dbm(self):
                if hasattr(self, '_m_comm_rx_rssi_dbm'):
                    return self._m_comm_rx_rssi_dbm

                self._m_comm_rx_rssi_dbm = ((self.raw[1] * 0.03) - 152)
                return getattr(self, '_m_comm_rx_rssi_dbm', None)

            @property
            def comm_rx_pa_temp_degree(self):
                if hasattr(self, '_m_comm_rx_pa_temp_degree'):
                    return self._m_comm_rx_pa_temp_degree

                self._m_comm_rx_pa_temp_degree = ((-0.07669 * self.raw[7]) + 195.6038)
                return getattr(self, '_m_comm_rx_pa_temp_degree', None)

            @property
            def comm_rx_tr_current_ampere(self):
                if hasattr(self, '_m_comm_rx_tr_current_ampere'):
                    return self._m_comm_rx_tr_current_ampere

                self._m_comm_rx_tr_current_ampere = ((self.raw[4] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_rx_tr_current_ampere', None)

            @property
            def comm_rx_pa_current_ampere(self):
                if hasattr(self, '_m_comm_rx_pa_current_ampere'):
                    return self._m_comm_rx_pa_current_ampere

                self._m_comm_rx_pa_current_ampere = ((self.raw[6] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_rx_pa_current_ampere', None)

            @property
            def comm_rx_doppler_hz(self):
                if hasattr(self, '_m_comm_rx_doppler_hz'):
                    return self._m_comm_rx_doppler_hz

                self._m_comm_rx_doppler_hz = ((self.raw[0] * 13.352) - 22300)
                return getattr(self, '_m_comm_rx_doppler_hz', None)

            @property
            def comm_rx_rx_current_ampere(self):
                if hasattr(self, '_m_comm_rx_rx_current_ampere'):
                    return self._m_comm_rx_rx_current_ampere

                self._m_comm_rx_rx_current_ampere = ((self.raw[5] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_rx_rx_current_ampere', None)

            @property
            def comm_rx_total_current_ampere(self):
                if hasattr(self, '_m_comm_rx_total_current_ampere'):
                    return self._m_comm_rx_total_current_ampere

                self._m_comm_rx_total_current_ampere = ((self.raw[3] * 0.16643964) / 1000)
                return getattr(self, '_m_comm_rx_total_current_ampere', None)

            @property
            def comm_rx_voltage_volts(self):
                if hasattr(self, '_m_comm_rx_voltage_volts'):
                    return self._m_comm_rx_voltage_volts

                self._m_comm_rx_voltage_volts = (self.raw[2] * 0.00488)
                return getattr(self, '_m_comm_rx_voltage_volts', None)

            @property
            def comm_rx_osci_temp_degree(self):
                if hasattr(self, '_m_comm_rx_osci_temp_degree'):
                    return self._m_comm_rx_osci_temp_degree

                self._m_comm_rx_osci_temp_degree = ((-0.07669 * self.raw[8]) + 195.6038)
                return getattr(self, '_m_comm_rx_osci_temp_degree', None)


        class HstxInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.raw = []
                for i in range(8):
                    self.raw.append(self._io.read_u2le())


            @property
            def bat_voltage(self):
                if hasattr(self, '_m_bat_voltage'):
                    return self._m_bat_voltage

                self._m_bat_voltage = (self.raw[5] * 0.004)
                return getattr(self, '_m_bat_voltage', None)

            @property
            def board_temp_bottom(self):
                if hasattr(self, '_m_board_temp_bottom'):
                    return self._m_board_temp_bottom

                self._m_board_temp_bottom = (self.raw[3] * 0.0625)
                return getattr(self, '_m_board_temp_bottom', None)

            @property
            def bat_current(self):
                if hasattr(self, '_m_bat_current'):
                    return self._m_bat_current

                self._m_bat_current = (self.raw[4] * 0.000004)
                return getattr(self, '_m_bat_current', None)

            @property
            def board_temp_top(self):
                if hasattr(self, '_m_board_temp_top'):
                    return self._m_board_temp_top

                self._m_board_temp_top = (self.raw[2] * 0.0625)
                return getattr(self, '_m_board_temp_top', None)

            @property
            def pa_voltage(self):
                if hasattr(self, '_m_pa_voltage'):
                    return self._m_pa_voltage

                self._m_pa_voltage = (self.raw[7] * 0.004)
                return getattr(self, '_m_pa_voltage', None)

            @property
            def pa_current(self):
                if hasattr(self, '_m_pa_current'):
                    return self._m_pa_current

                self._m_pa_current = (self.raw[6] * 0.000004)
                return getattr(self, '_m_pa_current', None)

            @property
            def rf_output_volts(self):
                if hasattr(self, '_m_rf_output_volts'):
                    return self._m_rf_output_volts

                self._m_rf_output_volts = (self.raw[0] * 0.001139)
                return getattr(self, '_m_rf_output_volts', None)

            @property
            def pa_temp(self):
                if hasattr(self, '_m_pa_temp'):
                    return self._m_pa_temp

                self._m_pa_temp = ((self.raw[1] * 0.073242) - 50)
                return getattr(self, '_m_pa_temp', None)


        class AdcsInfo(KaitaiStruct):

            class CubesenseEstimationModeEnum(Enum):
                disabled = 0
                mems_rate = 1
                magnetometer_filter = 2
                magnetometer_filter_pitch = 3
                magnetometer_fine_sun_triad = 4
                full_ekf = 5
                mems_gyro_ekf = 6

            class MagnetometerModeEnum(Enum):
                main_signal = 0
                redundant_signal = 1
                main_motor = 2
                none = 3

            class CubesenseAdcsModeEnum(Enum):
                disabled = 0
                enabled = 1
                triggered = 2

            class CubesenseControlModeEnum(Enum):
                disabled = 0
                detumbling = 1
                y_thomson = 2
                y_wheel_momentum_stabilized_initial = 3
                y_wheel_momentum_stabilized_steady_state = 4
                xyz_wheel = 5
                sun_tracking = 6
                target_tracking = 7
                very_fast_detumbling = 8
                fast_detumbling = 9
                user1 = 10
                user2 = 11
                rw_off = 12
                user3 = 13

            class CubesenseAsgp4ModeEnum(Enum):
                disabled = 0
                trigger = 1
                background = 2
                augment = 3
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.cubesense_tm190 = Randev.RandevPayload.AdcsInfo.CubesenseTm190Info(self._io, self, self._root)
                self.cubesense_tm146 = Randev.RandevPayload.AdcsInfo.CubesenseTm146Info(self._io, self, self._root)

            class CubesenseTm190Info(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._read()

                def _read(self):
                    self.estimation_mode = KaitaiStream.resolve_enum(Randev.RandevPayload.AdcsInfo.CubesenseEstimationModeEnum, self._io.read_bits_int_be(4))
                    self.control_mode = KaitaiStream.resolve_enum(Randev.RandevPayload.AdcsInfo.CubesenseControlModeEnum, self._io.read_bits_int_be(4))
                    self.adcs_mode = KaitaiStream.resolve_enum(Randev.RandevPayload.AdcsInfo.CubesenseAdcsModeEnum, self._io.read_bits_int_be(2))
                    self.asgp4_mode = KaitaiStream.resolve_enum(Randev.RandevPayload.AdcsInfo.CubesenseAsgp4ModeEnum, self._io.read_bits_int_be(2))
                    self.cubecontrol_signal_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubecontrol_motor_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubesence1_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubesence2_enable = self._io.read_bits_int_be(1) != 0
                    self.cubewheel1_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubewheel2_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubewheel3_enabled = self._io.read_bits_int_be(1) != 0
                    self.cubestar_enabled = self._io.read_bits_int_be(1) != 0
                    self.gps_reciver_enabled = self._io.read_bits_int_be(1) != 0
                    self.gps_lna_power_enabled = self._io.read_bits_int_be(1) != 0
                    self.motor_driver_enabled = self._io.read_bits_int_be(1) != 0
                    self.sun_is_above_local_horizon = self._io.read_bits_int_be(1) != 0
                    self.errors = self._io.read_bits_int_be(1) != 0
                    self.cubesence1_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubesence2_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubecontrol_signal_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubecontrol_motor_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubewheel1_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubewhee2_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubewheel3_comm_error = self._io.read_bits_int_be(1) != 0
                    self.cubestar_comm_error = self._io.read_bits_int_be(1) != 0
                    self.magnetometer_range_error = self._io.read_bits_int_be(1) != 0
                    self.sunsensor_sram_overcurrent_detected = self._io.read_bits_int_be(1) != 0
                    self.sunsensor_3v3_overcurrent_detected = self._io.read_bits_int_be(1) != 0
                    self.sunsensor_busy_error = self._io.read_bits_int_be(1) != 0
                    self.sunsensor_detection_error = self._io.read_bits_int_be(1) != 0
                    self.sunsensor_range_error = self._io.read_bits_int_be(1) != 0
                    self.nadir_sensor_sram_overcurrent_detected = self._io.read_bits_int_be(1) != 0
                    self.nadir_sensor_3v3_overcurrent_detected = self._io.read_bits_int_be(1) != 0
                    self.nadir_sensor_busy_error = self._io.read_bits_int_be(1) != 0
                    self.nadir_sensor_detection_error = self._io.read_bits_int_be(1) != 0
                    self.nadir_sensor_range_error = self._io.read_bits_int_be(1) != 0
                    self.rate_sensor_range_error = self._io.read_bits_int_be(1) != 0
                    self.wheel_speed_range_error = self._io.read_bits_int_be(1) != 0
                    self.coarse_sunsensor_error = self._io.read_bits_int_be(1) != 0
                    self.startracker_match_error = self._io.read_bits_int_be(1) != 0
                    self.startracker_overcurrent_detected = self._io.read_bits_int_be(1) != 0
                    self.orbit_parameters_invalid = self._io.read_bits_int_be(1) != 0
                    self.configuration_invalid = self._io.read_bits_int_be(1) != 0
                    self.control_mode_change_allowed = self._io.read_bits_int_be(1) != 0
                    self.estimator_change_not_allowed = self._io.read_bits_int_be(1) != 0
                    self.magnetometer_mode = KaitaiStream.resolve_enum(Randev.RandevPayload.AdcsInfo.MagnetometerModeEnum, self._io.read_bits_int_be(2))
                    self.modelled_measured_magnetic_field_missmatch = self._io.read_bits_int_be(1) != 0
                    self.node_recovery_error = self._io.read_bits_int_be(1) != 0
                    self.cubesense1_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubesense2_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubecontrol_signal_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubecontrol_motor_untime_error = self._io.read_bits_int_be(1) != 0
                    self.cubewheel1_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubewheel2_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubewheel3_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.cubestar_runtime_error = self._io.read_bits_int_be(1) != 0
                    self.magnetometer_error = self._io.read_bits_int_be(1) != 0
                    self.rate_sensor_failure = self._io.read_bits_int_be(1) != 0


            class CubesenseTm146Info(KaitaiStruct):
                def __init__(self, _io, _parent=None, _root=None):
                    self._io = _io
                    self._parent = _parent
                    self._root = _root if _root else self
                    self._read()

                def _read(self):
                    self.raw = []
                    for i in range((3 * 3)):
                        self.raw.append(self._io.read_s2le())


                @property
                def pitch_degree(self):
                    if hasattr(self, '_m_pitch_degree'):
                        return self._m_pitch_degree

                    self._m_pitch_degree = (self.raw[1] * 0.01)
                    return getattr(self, '_m_pitch_degree', None)

                @property
                def y_angular_rate_degree_s(self):
                    if hasattr(self, '_m_y_angular_rate_degree_s'):
                        return self._m_y_angular_rate_degree_s

                    self._m_y_angular_rate_degree_s = (self.raw[7] * 0.01)
                    return getattr(self, '_m_y_angular_rate_degree_s', None)

                @property
                def q1(self):
                    if hasattr(self, '_m_q1'):
                        return self._m_q1

                    self._m_q1 = (self.raw[3] * 0.0001)
                    return getattr(self, '_m_q1', None)

                @property
                def x_angular_rate_degree_s(self):
                    if hasattr(self, '_m_x_angular_rate_degree_s'):
                        return self._m_x_angular_rate_degree_s

                    self._m_x_angular_rate_degree_s = (self.raw[6] * 0.01)
                    return getattr(self, '_m_x_angular_rate_degree_s', None)

                @property
                def roll_degree(self):
                    if hasattr(self, '_m_roll_degree'):
                        return self._m_roll_degree

                    self._m_roll_degree = (self.raw[0] * 0.01)
                    return getattr(self, '_m_roll_degree', None)

                @property
                def yaw_degree(self):
                    if hasattr(self, '_m_yaw_degree'):
                        return self._m_yaw_degree

                    self._m_yaw_degree = (self.raw[2] * 0.01)
                    return getattr(self, '_m_yaw_degree', None)

                @property
                def z_angular_rate_degree_s(self):
                    if hasattr(self, '_m_z_angular_rate_degree_s'):
                        return self._m_z_angular_rate_degree_s

                    self._m_z_angular_rate_degree_s = (self.raw[8] * 0.01)
                    return getattr(self, '_m_z_angular_rate_degree_s', None)

                @property
                def q2(self):
                    if hasattr(self, '_m_q2'):
                        return self._m_q2

                    self._m_q2 = (self.raw[4] * 0.0001)
                    return getattr(self, '_m_q2', None)

                @property
                def q3(self):
                    if hasattr(self, '_m_q3'):
                        return self._m_q3

                    self._m_q3 = (self.raw[5] * 0.0001)
                    return getattr(self, '_m_q3', None)



        class EpsInfo(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.eps_board_status = self._io.read_bits_int_be(16)
                self.eps_pdm_status = self._io.read_bits_int_be(16)
                self._io.align_to_byte()
                self.raw_measure = []
                for i in range(35):
                    self.raw_measure.append(self._io.read_u2le())


            @property
            def eps_sw8_current_ampere(self):
                if hasattr(self, '_m_eps_sw8_current_ampere'):
                    return self._m_eps_sw8_current_ampere

                self._m_eps_sw8_current_ampere = (self.raw_measure[21] * 0.001328)
                return getattr(self, '_m_eps_sw8_current_ampere', None)

            @property
            def bat_voltage_volts(self):
                if hasattr(self, '_m_bat_voltage_volts'):
                    return self._m_bat_voltage_volts

                self._m_bat_voltage_volts = (self.raw_measure[29] * 0.008993)
                return getattr(self, '_m_bat_voltage_volts', None)

            @property
            def bat_current_ampere(self):
                if hasattr(self, '_m_bat_current_ampere'):
                    return self._m_bat_current_ampere

                self._m_bat_current_ampere = ((-(self.raw_measure[30]) * 0.014662757) if self.raw_measure[31] < 512 else (self.raw_measure[30] * 0.014662757))
                return getattr(self, '_m_bat_current_ampere', None)

            @property
            def eps_sw6_current_ampere(self):
                if hasattr(self, '_m_eps_sw6_current_ampere'):
                    return self._m_eps_sw6_current_ampere

                self._m_eps_sw6_current_ampere = (self.raw_measure[17] * 0.001328)
                return getattr(self, '_m_eps_sw6_current_ampere', None)

            @property
            def eps_sw2_current_ampere(self):
                if hasattr(self, '_m_eps_sw2_current_ampere'):
                    return self._m_eps_sw2_current_ampere

                self._m_eps_sw2_current_ampere = (self.raw_measure[8] * 0.005237)
                return getattr(self, '_m_eps_sw2_current_ampere', None)

            @property
            def eps_sw1_current_ampere(self):
                if hasattr(self, '_m_eps_sw1_current_ampere'):
                    return self._m_eps_sw1_current_ampere

                self._m_eps_sw1_current_ampere = (self.raw_measure[6] * 0.005237)
                return getattr(self, '_m_eps_sw1_current_ampere', None)

            @property
            def bat_temp_celcius(self):
                if hasattr(self, '_m_bat_temp_celcius'):
                    return self._m_bat_temp_celcius

                self._m_bat_temp_celcius = ((0.3976 * self.raw_measure[32]) - 238.57)
                return getattr(self, '_m_bat_temp_celcius', None)

            @property
            def eps_3v3_current_ampere(self):
                if hasattr(self, '_m_eps_3v3_current_ampere'):
                    return self._m_eps_3v3_current_ampere

                self._m_eps_3v3_current_ampere = (self.raw_measure[2] * 0.001327547)
                return getattr(self, '_m_eps_3v3_current_ampere', None)

            @property
            def eps_sw9_voltage_volts(self):
                if hasattr(self, '_m_eps_sw9_voltage_volts'):
                    return self._m_eps_sw9_voltage_volts

                self._m_eps_sw9_voltage_volts = (self.raw_measure[22] * 0.004311)
                return getattr(self, '_m_eps_sw9_voltage_volts', None)

            @property
            def eps_sw2_voltage_volts(self):
                if hasattr(self, '_m_eps_sw2_voltage_volts'):
                    return self._m_eps_sw2_voltage_volts

                self._m_eps_sw2_voltage_volts = (self.raw_measure[9] * 0.004311)
                return getattr(self, '_m_eps_sw2_voltage_volts', None)

            @property
            def bat_heate_ctrl_on(self):
                if hasattr(self, '_m_bat_heate_ctrl_on'):
                    return self._m_bat_heate_ctrl_on

                self._m_bat_heate_ctrl_on = (False if self.raw_measure[34] < 1 else True)
                return getattr(self, '_m_bat_heate_ctrl_on', None)

            @property
            def eps_sw1_voltage_volts(self):
                if hasattr(self, '_m_eps_sw1_voltage_volts'):
                    return self._m_eps_sw1_voltage_volts

                self._m_eps_sw1_voltage_volts = (self.raw_measure[7] * 0.005865)
                return getattr(self, '_m_eps_sw1_voltage_volts', None)

            @property
            def eps_sw7_current_ampere(self):
                if hasattr(self, '_m_eps_sw7_current_ampere'):
                    return self._m_eps_sw7_current_ampere

                self._m_eps_sw7_current_ampere = (self.raw_measure[19] * 0.001328)
                return getattr(self, '_m_eps_sw7_current_ampere', None)

            @property
            def eps_sw4_voltage_volts(self):
                if hasattr(self, '_m_eps_sw4_voltage_volts'):
                    return self._m_eps_sw4_voltage_volts

                self._m_eps_sw4_voltage_volts = (self.raw_measure[12] * 0.008993)
                return getattr(self, '_m_eps_sw4_voltage_volts', None)

            @property
            def eps_temp_celcius(self):
                if hasattr(self, '_m_eps_temp_celcius'):
                    return self._m_eps_temp_celcius

                self._m_eps_temp_celcius = ((0.372434 * self.raw_measure[24]) - 273.15)
                return getattr(self, '_m_eps_temp_celcius', None)

            @property
            def eps_sw5_voltage_volts(self):
                if hasattr(self, '_m_eps_sw5_voltage_volts'):
                    return self._m_eps_sw5_voltage_volts

                self._m_eps_sw5_voltage_volts = (self.raw_measure[14] * 0.005865)
                return getattr(self, '_m_eps_sw5_voltage_volts', None)

            @property
            def eps_sw7_voltage_volts(self):
                if hasattr(self, '_m_eps_sw7_voltage_volts'):
                    return self._m_eps_sw7_voltage_volts

                self._m_eps_sw7_voltage_volts = (self.raw_measure[18] * 0.005865)
                return getattr(self, '_m_eps_sw7_voltage_volts', None)

            @property
            def eps_5v_current_ampere(self):
                if hasattr(self, '_m_eps_5v_current_ampere'):
                    return self._m_eps_5v_current_ampere

                self._m_eps_5v_current_ampere = (self.raw_measure[3] * 0.001327547)
                return getattr(self, '_m_eps_5v_current_ampere', None)

            @property
            def eps_bcr5_voltage_volts(self):
                if hasattr(self, '_m_eps_bcr5_voltage_volts'):
                    return self._m_eps_bcr5_voltage_volts

                self._m_eps_bcr5_voltage_volts = (self.raw_measure[28] * 0.0322581)
                return getattr(self, '_m_eps_bcr5_voltage_volts', None)

            @property
            def eps_battery_voltage_volts(self):
                if hasattr(self, '_m_eps_battery_voltage_volts'):
                    return self._m_eps_battery_voltage_volts

                self._m_eps_battery_voltage_volts = (self.raw_measure[5] * 0.008978)
                return getattr(self, '_m_eps_battery_voltage_volts', None)

            @property
            def eps_bcr4_voltage_volts(self):
                if hasattr(self, '_m_eps_bcr4_voltage_volts'):
                    return self._m_eps_bcr4_voltage_volts

                self._m_eps_bcr4_voltage_volts = (self.raw_measure[27] * 0.0322581)
                return getattr(self, '_m_eps_bcr4_voltage_volts', None)

            @property
            def eps_battery_current_ampere(self):
                if hasattr(self, '_m_eps_battery_current_ampere'):
                    return self._m_eps_battery_current_ampere

                self._m_eps_battery_current_ampere = (self.raw_measure[4] * 0.005237)
                return getattr(self, '_m_eps_battery_current_ampere', None)

            @property
            def eps_bcr1_voltage_volts(self):
                if hasattr(self, '_m_eps_bcr1_voltage_volts'):
                    return self._m_eps_bcr1_voltage_volts

                self._m_eps_bcr1_voltage_volts = (self.raw_measure[25] * 0.0322581)
                return getattr(self, '_m_eps_bcr1_voltage_volts', None)

            @property
            def eps_bcr2_voltage_volts(self):
                if hasattr(self, '_m_eps_bcr2_voltage_volts'):
                    return self._m_eps_bcr2_voltage_volts

                self._m_eps_bcr2_voltage_volts = (self.raw_measure[26] * 0.0322581)
                return getattr(self, '_m_eps_bcr2_voltage_volts', None)

            @property
            def eps_bcr_voltage_volts(self):
                if hasattr(self, '_m_eps_bcr_voltage_volts'):
                    return self._m_eps_bcr_voltage_volts

                self._m_eps_bcr_voltage_volts = (self.raw_measure[1] * 0.008993157)
                return getattr(self, '_m_eps_bcr_voltage_volts', None)

            @property
            def eps_sw4_current_ampere(self):
                if hasattr(self, '_m_eps_sw4_current_ampere'):
                    return self._m_eps_sw4_current_ampere

                self._m_eps_sw4_current_ampere = (self.raw_measure[13] * 0.006239)
                return getattr(self, '_m_eps_sw4_current_ampere', None)

            @property
            def bat_heater_on(self):
                if hasattr(self, '_m_bat_heater_on'):
                    return self._m_bat_heater_on

                self._m_bat_heater_on = (False if self.raw_measure[33] < 512 else True)
                return getattr(self, '_m_bat_heater_on', None)

            @property
            def eps_sw6_voltage_volts(self):
                if hasattr(self, '_m_eps_sw6_voltage_volts'):
                    return self._m_eps_sw6_voltage_volts

                self._m_eps_sw6_voltage_volts = (self.raw_measure[16] * 0.005865)
                return getattr(self, '_m_eps_sw6_voltage_volts', None)

            @property
            def eps_sw3_current_ampere(self):
                if hasattr(self, '_m_eps_sw3_current_ampere'):
                    return self._m_eps_sw3_current_ampere

                self._m_eps_sw3_current_ampere = (self.raw_measure[11] * 0.006239)
                return getattr(self, '_m_eps_sw3_current_ampere', None)

            @property
            def eps_bcr_current_ampere(self):
                if hasattr(self, '_m_eps_bcr_current_ampere'):
                    return self._m_eps_bcr_current_ampere

                self._m_eps_bcr_current_ampere = (self.raw_measure[0] * 14.662757)
                return getattr(self, '_m_eps_bcr_current_ampere', None)

            @property
            def eps_sw3_voltage_volts(self):
                if hasattr(self, '_m_eps_sw3_voltage_volts'):
                    return self._m_eps_sw3_voltage_volts

                self._m_eps_sw3_voltage_volts = (self.raw_measure[10] * 0.008993)
                return getattr(self, '_m_eps_sw3_voltage_volts', None)

            @property
            def eps_sw9_current_ampere(self):
                if hasattr(self, '_m_eps_sw9_current_ampere'):
                    return self._m_eps_sw9_current_ampere

                self._m_eps_sw9_current_ampere = (self.raw_measure[23] * 0.001328)
                return getattr(self, '_m_eps_sw9_current_ampere', None)

            @property
            def eps_sw5_current_ampere(self):
                if hasattr(self, '_m_eps_sw5_current_ampere'):
                    return self._m_eps_sw5_current_ampere

                self._m_eps_sw5_current_ampere = (self.raw_measure[15] * 0.001328)
                return getattr(self, '_m_eps_sw5_current_ampere', None)

            @property
            def eps_sw8_voltage_volts(self):
                if hasattr(self, '_m_eps_sw8_voltage_volts'):
                    return self._m_eps_sw8_voltage_volts

                self._m_eps_sw8_voltage_volts = (self.raw_measure[20] * 0.004311)
                return getattr(self, '_m_eps_sw8_voltage_volts', None)




