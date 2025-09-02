# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pegasus(KaitaiStruct):
    """:field pid: tt64_frame.pid
    :field call: tt64_frame.beacon.call
    :field trx_temp: tt64_frame.beacon.trx_temp
    :field antenna_deployment: tt64_frame.beacon.antenna_deployment
    :field stacie_op: tt64_frame.beacon.stacie_op
    :field temp_compensation: tt64_frame.beacon.temp_compensation
    :field reset_counter: tt64_frame.beacon.reset_counter
    :field uplink_error: tt64_frame.beacon.uplink_error
    :field obc_sent_packet_counter_between_s_beacons: tt64_frame.beacon.obc_sent_packet_counter_between_s_beacons
    :field beacon_interval: tt64_frame.beacon.beacon_interval
    :field sid_s: tt64_frame.beacon.sid_s
    :field tx_sel_reason: tt64_frame.beacon.tx_sel_reason
    :field reason_remote: tt64_frame.beacon.reason_remote
    :field gs_cmd_counter: tt64_frame.beacon.gs_cmd_counter
    :field beacon_count: tt64_frame.beacon.beacon_count
    :field prim_freq_start: tt64_frame.beacon.prim_freq_start
    :field sec_freq_start: tt64_frame.beacon.sec_freq_start
    :field usp: tt64_frame.beacon.usp
    :field rssi_idle: tt64_frame.beacon.rssi_idle
    :field rssi_rx: tt64_frame.beacon.rssi_rx
    :field primary_carrier: tt64_frame.beacon.primary_carrier
    :field secondary_carrier: tt64_frame.beacon.secondary_carrier
    :field used_carrier: tt64_frame.beacon.used_carrier
    :field temperature_compensation_carrier: tt64_frame.beacon.temperature_compensation_carrier
    :field s_time: tt64_frame.beacon.s_time
    :field temp_bat1sw: tt64_frame.beacon.temp_bat1sw
    :field temp_5v: tt64_frame.beacon.temp_5v
    :field eps_version: tt64_frame.beacon.eps_version
    :field sid_e: tt64_frame.beacon.sid_e
    :field temp_bat1: tt64_frame.beacon.temp_bat1
    :field temp_bat2: tt64_frame.beacon.temp_bat2
    :field status_1_3v3_1: tt64_frame.beacon.status_1_3v3_1
    :field status_1_3v3_2: tt64_frame.beacon.status_1_3v3_2
    :field status_1_3v3_3: tt64_frame.beacon.status_1_3v3_3
    :field status_1_3v3_bu: tt64_frame.beacon.status_1_3v3_bu
    :field status_1_5v_1: tt64_frame.beacon.status_1_5v_1
    :field status_1_5v_2: tt64_frame.beacon.status_1_5v_2
    :field status_1_5v_3: tt64_frame.beacon.status_1_5v_3
    :field status_1_5v_4: tt64_frame.beacon.status_1_5v_4
    :field status_2_power_low: tt64_frame.beacon.status_2_power_low
    :field status_2_bat1_pv1: tt64_frame.beacon.status_2_bat1_pv1
    :field status_2_bat2_pv2: tt64_frame.beacon.status_2_bat2_pv2
    :field status_2_3v3: tt64_frame.beacon.status_2_3v3
    :field status_2_5v: tt64_frame.beacon.status_2_5v
    :field status_2_mode: tt64_frame.beacon.status_2_mode
    :field status_3_3v3_burst: tt64_frame.beacon.status_3_3v3_burst
    :field status_3_5v_burst: tt64_frame.beacon.status_3_5v_burst
    :field status_3_bat1_pv2: tt64_frame.beacon.status_3_bat1_pv2
    :field status_3_bat2_pv1: tt64_frame.beacon.status_3_bat2_pv1
    :field status_3_temp_warning: tt64_frame.beacon.status_3_temp_warning
    :field status_3_cc1: tt64_frame.beacon.status_3_cc1
    :field status_3_cc2: tt64_frame.beacon.status_3_cc2
    :field status_3_rbf: tt64_frame.beacon.status_3_rbf
    :field s_beacon_count: tt64_frame.beacon.s_beacon_count
    :field reboot_mc: tt64_frame.beacon.reboot_mc
    :field reboot_cc1: tt64_frame.beacon.reboot_cc1
    :field reboot_cc2: tt64_frame.beacon.reboot_cc2
    :field temp_cc1: tt64_frame.beacon.temp_cc1
    :field temp_cc2: tt64_frame.beacon.temp_cc2
    :field status_cc1_mode: tt64_frame.beacon.status_cc1_mode
    :field status_cc1_mc_timeout: tt64_frame.beacon.status_cc1_mc_timeout
    :field status_cc1_tbd: tt64_frame.beacon.status_cc1_tbd
    :field status_cc1_en_i2c: tt64_frame.beacon.status_cc1_en_i2c
    :field status_cc1_bat1_pv1: tt64_frame.beacon.status_cc1_bat1_pv1
    :field status_cc1_bat2_pv2: tt64_frame.beacon.status_cc1_bat2_pv2
    :field status_cc1_3v3_backup: tt64_frame.beacon.status_cc1_3v3_backup
    :field status_cc2_mode: tt64_frame.beacon.status_cc2_mode
    :field status_cc2_mc_timeout: tt64_frame.beacon.status_cc2_mc_timeout
    :field status_cc2_tbd: tt64_frame.beacon.status_cc2_tbd
    :field status_cc2_en_i2c: tt64_frame.beacon.status_cc2_en_i2c
    :field status_cc2_bat1_pv1: tt64_frame.beacon.status_cc2_bat1_pv1
    :field status_cc2_bat2_pv2: tt64_frame.beacon.status_cc2_bat2_pv2
    :field status_cc2_3v3_backup: tt64_frame.beacon.status_cc2_3v3_backup
    :field v_pv2: tt64_frame.beacon.v_pv2
    :field v_5v_in: tt64_frame.beacon.v_5v_in
    :field v_pv1: tt64_frame.beacon.v_pv1
    :field v_3v3_in: tt64_frame.beacon.v_3v3_in
    :field v_3v3_out: tt64_frame.beacon.v_3v3_out
    :field v_hv: tt64_frame.beacon.v_hv
    :field v_5v_out: tt64_frame.beacon.v_5v_out
    :field v_bat1: tt64_frame.beacon.v_bat1
    :field v_bat2: tt64_frame.beacon.v_bat2
    :field vcc_cc2: tt64_frame.beacon.vcc_cc2
    :field vcc_cc1: tt64_frame.beacon.vcc_cc1
    :field i_pv1_5v: tt64_frame.beacon.i_pv1_5v
    :field i_pv2_5v: tt64_frame.beacon.i_pv2_5v
    :field i_pv1_3v3: tt64_frame.beacon.i_pv1_3v3
    :field i_pv2_3v3: tt64_frame.beacon.i_pv2_3v3
    :field i_pv1_bat1: tt64_frame.beacon.i_pv1_bat1
    :field i_pv2_bat1: tt64_frame.beacon.i_pv2_bat1
    :field i_pv1_bat2: tt64_frame.beacon.i_pv1_bat2
    :field i_pv2_bat2: tt64_frame.beacon.i_pv2_bat2
    :field ant_deploy_status_mb: tt64_frame.beacon.ant_deploy_status_mb
    :field ant_deploy_status_lb: tt64_frame.beacon.ant_deploy_status_lb
    :field temp_comp_hw: tt64_frame.beacon.temp_comp_hw
    :field rbf_state: tt64_frame.beacon.rbf_state
    :field sid_a: tt64_frame.beacon.sid_a
    :field stacie_version: tt64_frame.beacon.stacie_version
    :field ant_temp: tt64_frame.beacon.ant_temp
    :field temp_a: tt64_frame.beacon.temp_a
    :field temp_c: tt64_frame.beacon.temp_c
    :field state_machine_su_script: tt64_frame.beacon.state_machine_su_script
    :field state_machine_su_powered: tt64_frame.beacon.state_machine_su_powered
    :field state_machine_adcs: tt64_frame.beacon.state_machine_adcs
    :field state_machine_not_used: tt64_frame.beacon.state_machine_not_used
    :field state_machine_obc: tt64_frame.beacon.state_machine_obc
    :field mission_counter: tt64_frame.beacon.mission_counter
    :field mission_counter_2: tt64_frame.beacon.mission_counter_2
    :field rssi_a: tt64_frame.beacon.rssi_a
    :field rssi_b: tt64_frame.beacon.rssi_b
    :field stacie_mode_a: tt64_frame.beacon.stacie_mode_a
    :field stacie_mode_c: tt64_frame.beacon.stacie_mode_c
    :field status_task_sensors_running: tt64_frame.beacon.status_task_sensors_running
    :field status_obc_3v3_spa_enabled: tt64_frame.beacon.status_obc_3v3_spa_enabled
    :field status_obc_power_saving_mode: tt64_frame.beacon.status_obc_power_saving_mode
    :field status_eps_cc_used: tt64_frame.beacon.status_eps_cc_used
    :field status_last_reset_source: tt64_frame.beacon.status_last_reset_source
    :field status_power_source: tt64_frame.beacon.status_power_source
    :field status_crystal_osicallation_in_use: tt64_frame.beacon.status_crystal_osicallation_in_use
    :field status_ssp1_initialized: tt64_frame.beacon.status_ssp1_initialized
    :field status_ssp0_initialized: tt64_frame.beacon.status_ssp0_initialized
    :field status_i2c2_initialized: tt64_frame.beacon.status_i2c2_initialized
    :field status_i2c1_initialized: tt64_frame.beacon.status_i2c1_initialized
    :field status_i2c0_initialized: tt64_frame.beacon.status_i2c0_initialized
    :field status_rtc_synchronized: tt64_frame.beacon.status_rtc_synchronized
    :field status_statemachine_initialized: tt64_frame.beacon.status_statemachine_initialized
    :field status_task_maintenance_running: tt64_frame.beacon.status_task_maintenance_running
    :field status_uart_ttc1_initialized: tt64_frame.beacon.status_uart_ttc1_initialized
    :field status_uart_mnlp_initialized: tt64_frame.beacon.status_uart_mnlp_initialized
    :field status_uart_ttc2_initialized: tt64_frame.beacon.status_uart_ttc2_initialized
    :field status_uart_gps_initialized: tt64_frame.beacon.status_uart_gps_initialized
    :field status_adc_initialized: tt64_frame.beacon.status_adc_initialized
    :field status_rtc_initialized: tt64_frame.beacon.status_rtc_initialized
    :field status_i2c_switches_initialized: tt64_frame.beacon.status_i2c_switches_initialized
    :field status_supply_switches_initialized: tt64_frame.beacon.status_supply_switches_initialized
    :field status_eeprom3_initialized: tt64_frame.beacon.status_eeprom3_initialized
    :field status_eeprom2_initialized: tt64_frame.beacon.status_eeprom2_initialized
    :field status_eeprom1_initialized: tt64_frame.beacon.status_eeprom1_initialized
    :field status_eps_cc2_operational: tt64_frame.beacon.status_eps_cc2_operational
    :field status_eps_cc1_opeational: tt64_frame.beacon.status_eps_cc1_opeational
    :field status_timer1_initialized: tt64_frame.beacon.status_timer1_initialized
    :field status_watchdog_initialized: tt64_frame.beacon.status_watchdog_initialized
    :field status_timer0_initialized: tt64_frame.beacon.status_timer0_initialized
    :field status_mpu_initialized: tt64_frame.beacon.status_mpu_initialized
    :field status_onboard_tmp100_initialized: tt64_frame.beacon.status_onboard_tmp100_initialized
    :field status_onboard_mag_initialized: tt64_frame.beacon.status_onboard_mag_initialized
    :field status_msp_initialized: tt64_frame.beacon.status_msp_initialized
    :field status_gyro2_initialized: tt64_frame.beacon.status_gyro2_initialized
    :field status_gyro1_initialized: tt64_frame.beacon.status_gyro1_initialized
    :field status_mag_bp_boom_initialized: tt64_frame.beacon.status_mag_bp_boom_initialized
    :field status_mag_bp_initialized: tt64_frame.beacon.status_mag_bp_initialized
    :field status_bp_initialized: tt64_frame.beacon.status_bp_initialized
    :field status_sa_initailized: tt64_frame.beacon.status_sa_initailized
    :field status_spd_initialized: tt64_frame.beacon.status_spd_initialized
    :field status_spc_initialized: tt64_frame.beacon.status_spc_initialized
    :field status_spb_initialized: tt64_frame.beacon.status_spb_initialized
    :field status_spa_initialized: tt64_frame.beacon.status_spa_initialized
    :field status_flash2_initialized: tt64_frame.beacon.status_flash2_initialized
    :field status_flash1_initialized: tt64_frame.beacon.status_flash1_initialized
    :field status_spd_vcc_on: tt64_frame.beacon.status_spd_vcc_on
    :field status_spc_vcc_on: tt64_frame.beacon.status_spc_vcc_on
    :field status_spb_vcc_on: tt64_frame.beacon.status_spb_vcc_on
    :field status_spa_vcc_on: tt64_frame.beacon.status_spa_vcc_on
    :field status_science_module_initialized: tt64_frame.beacon.status_science_module_initialized
    :field status_ttc2_initialized: tt64_frame.beacon.status_ttc2_initialized
    :field status_ttc1_initialized: tt64_frame.beacon.status_ttc1_initialized
    :field status_gps_initialized: tt64_frame.beacon.status_gps_initialized
    :field status_onboard_mag_powersafe: tt64_frame.beacon.status_onboard_mag_powersafe
    :field status_i2c_sw_d_on: tt64_frame.beacon.status_i2c_sw_d_on
    :field status_i2c_sw_c_on: tt64_frame.beacon.status_i2c_sw_c_on
    :field status_i2c_sw_b_on: tt64_frame.beacon.status_i2c_sw_b_on
    :field status_i2c_sw_a_on: tt64_frame.beacon.status_i2c_sw_a_on
    :field status_sa_vcc_on: tt64_frame.beacon.status_sa_vcc_on
    :field status_bp2_vcc_on: tt64_frame.beacon.status_bp2_vcc_on
    :field status_bp1_vcc_on: tt64_frame.beacon.status_bp1_vcc_on
    :field status_eeprom_page_cycle_overflow: tt64_frame.beacon.status_eeprom_page_cycle_overflow
    :field status_rtc_oscillator_error: tt64_frame.beacon.status_rtc_oscillator_error
    :field status_mnlp_5v_enabled: tt64_frame.beacon.status_mnlp_5v_enabled
    :field status_mag_bp_boom_power_saving_mode: tt64_frame.beacon.status_mag_bp_boom_power_saving_mode
    :field status_mag_bp_power_saving_mode: tt64_frame.beacon.status_mag_bp_power_saving_mode
    :field status_tmp100_powersafe: tt64_frame.beacon.status_tmp100_powersafe
    :field status_mpu_powersafe: tt64_frame.beacon.status_mpu_powersafe
    :field status_gyro_powersafe: tt64_frame.beacon.status_gyro_powersafe
    :field status_default_config_used: tt64_frame.beacon.status_default_config_used
    :field status_timer1_running: tt64_frame.beacon.status_timer1_running
    :field status_timer0_running: tt64_frame.beacon.status_timer0_running
    :field status_i2c2_frequent_errors: tt64_frame.beacon.status_i2c2_frequent_errors
    :field status_i2c1_frequent_errors: tt64_frame.beacon.status_i2c1_frequent_errors
    :field status_i2c0_frequent_errors: tt64_frame.beacon.status_i2c0_frequent_errors
    :field status_ssp1_frequent_errors: tt64_frame.beacon.status_ssp1_frequent_errors
    :field status_ssp0_frequent_errors: tt64_frame.beacon.status_ssp0_frequent_errors
    :field error_code: tt64_frame.beacon.error_code
    :field error_code_before_reset: tt64_frame.beacon.error_code_before_reset
    :field resets_counter: tt64_frame.beacon.resets_counter
    :field script_slot_cs1: tt64_frame.beacon.script_slot_cs1
    :field script_slot_su7: tt64_frame.beacon.script_slot_su7
    :field script_slot_su6: tt64_frame.beacon.script_slot_su6
    :field script_slot_su5: tt64_frame.beacon.script_slot_su5
    :field script_slot_su4: tt64_frame.beacon.script_slot_su4
    :field script_slot_su3: tt64_frame.beacon.script_slot_su3
    :field script_slot_su2: tt64_frame.beacon.script_slot_su2
    :field script_slot_su1: tt64_frame.beacon.script_slot_su1
    :field script_slot_cs5: tt64_frame.beacon.script_slot_cs5
    :field script_slot_cs4: tt64_frame.beacon.script_slot_cs4
    :field script_slot_cs3: tt64_frame.beacon.script_slot_cs3
    :field script_slot_cs2: tt64_frame.beacon.script_slot_cs2
    :field temp_sp_x_minus: tt64_frame.beacon.temp_sp_x_minus
    :field temp_sp_x_plus: tt64_frame.beacon.temp_sp_x_plus
    :field temp_sp_y_minus: tt64_frame.beacon.temp_sp_y_minus
    :field temp_sp_y_plus: tt64_frame.beacon.temp_sp_y_plus
    
    .. seealso::
       Source - https://spacedatacenter.at/pegasus/img/hamoperatormanual12.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.tt64_frame = Pegasus.Tt64Frame(self._io, self, self._root)

    class HkdDownload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.padding_hkd1 = self._io.read_bytes(10)
            self.v_pv1_raw = self._io.read_u1()
            self.v_pv2_raw = self._io.read_u1()
            self.v_5v_in_raw = self._io.read_u1()
            self.v_3v3_in_raw = self._io.read_u1()
            self.v_5v_out_raw = self._io.read_u1()
            self.v_3v3_out_raw = self._io.read_u1()
            self.i_pv1_5v_raw = self._io.read_u1()
            self.i_pv2_5v_raw = self._io.read_u1()
            self.i_pv1_3v3_raw = self._io.read_u1()
            self.i_pv2_3v3_raw = self._io.read_u1()
            self.temp_bat1sw = self._io.read_s1()
            self.temp_5v = self._io.read_s1()
            self.v_hv_raw = self._io.read_u1()
            self.i_pv1_bat1_raw = self._io.read_u1()
            self.i_pv2_bat1_raw = self._io.read_u1()
            self.i_pv1_bat2_raw = self._io.read_u1()
            self.i_pv2_bat2_raw = self._io.read_u1()
            self.v_bat1_raw = self._io.read_u1()
            self.v_bat2_raw = self._io.read_u1()
            self.vcc_cc2_raw = self._io.read_u1()
            self.vcc_cc1_raw = self._io.read_u1()
            self.temp_bat1 = self._io.read_s1()
            self.temp_bat2 = self._io.read_s1()
            self.status_1_3v3_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_bu = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_4 = self._io.read_bits_int_be(1) != 0
            self.status_2_power_low = self._io.read_bits_int_be(1) != 0
            self.status_2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_2_3v3 = self._io.read_bits_int_be(1) != 0
            self.status_2_5v = self._io.read_bits_int_be(1) != 0
            self.status_2_mode = self._io.read_bits_int_be(3)
            self.status_3_3v3_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_5v_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_bat1_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_3_bat2_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_3_temp_warning = self._io.read_bits_int_be(1) != 0
            self.status_3_cc1 = self._io.read_bits_int_be(1) != 0
            self.status_3_cc2 = self._io.read_bits_int_be(1) != 0
            self.status_3_rbf = self._io.read_bits_int_be(1) != 0
            self.status_cc1_mode = self._io.read_bits_int_be(2)
            self.status_cc1_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc1_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc1_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_3v3_backup = self._io.read_bits_int_be(1) != 0
            self.status_cc2_mode = self._io.read_bits_int_be(2)
            self.status_cc2_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc2_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc2_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_3v3_backup = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.temp_a = self._io.read_s1()
            self.temp_c = self._io.read_s1()
            self.rssi_a_raw = self._io.read_u1()
            self.rssi_b_raw = self._io.read_u1()
            self.state_machine_su_script = self._io.read_bits_int_be(1) != 0
            self.state_machine_su_powered = self._io.read_bits_int_be(1) != 0
            self.state_machine_adcs = self._io.read_bits_int_be(1) != 0
            self.state_machine_not_used = self._io.read_bits_int_be(1) != 0
            self.state_machine_obc = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.mission_counter = self._io.read_u1()
            self.mission_counter_2 = self._io.read_u1()

        @property
        def vcc_cc2(self):
            """Supply voltage of CC2 (communication controller 2) [V]."""
            if hasattr(self, '_m_vcc_cc2'):
                return self._m_vcc_cc2

            self._m_vcc_cc2 = (((((((((self.vcc_cc2_raw & 128) // 128 * 4) + ((self.vcc_cc2_raw & 64) // 64 * 2)) + ((self.vcc_cc2_raw & 32) // 32 * 1)) + ((self.vcc_cc2_raw & 16) // 16 * 0.5)) + ((self.vcc_cc2_raw & 8) // 8 * 0.25)) + ((self.vcc_cc2_raw & 4) // 4 * 0.125)) + ((self.vcc_cc2_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc2', None)

        @property
        def v_bat2(self):
            """Voltage of the battery 2 [V]."""
            if hasattr(self, '_m_v_bat2'):
                return self._m_v_bat2

            self._m_v_bat2 = (((((((((self.v_bat2_raw & 128) // 128 * 4) + ((self.v_bat2_raw & 64) // 64 * 2)) + ((self.v_bat2_raw & 32) // 32 * 1)) + ((self.v_bat2_raw & 16) // 16 * 0.5)) + ((self.v_bat2_raw & 8) // 8 * 0.25)) + ((self.v_bat2_raw & 4) // 4 * 0.125)) + ((self.v_bat2_raw & 2) // 2 * 0.0625)) + ((self.v_bat2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat2', None)

        @property
        def rssi_a(self):
            """Received Signal Strength Indication of TRX module A during the last uplink [dBm]."""
            if hasattr(self, '_m_rssi_a'):
                return self._m_rssi_a

            self._m_rssi_a = (-132.0 + self.rssi_a_raw // 2)
            return getattr(self, '_m_rssi_a', None)

        @property
        def rssi_b(self):
            """Received Signal Strength Indication of TRX module C during the last uplink [dBm]."""
            if hasattr(self, '_m_rssi_b'):
                return self._m_rssi_b

            self._m_rssi_b = (-132.0 + self.rssi_b_raw // 2)
            return getattr(self, '_m_rssi_b', None)

        @property
        def v_pv1(self):
            """Voltage at PV1-bus (Solarbus 1) [V]."""
            if hasattr(self, '_m_v_pv1'):
                return self._m_v_pv1

            self._m_v_pv1 = (((((((((self.v_pv1_raw & 128) // 128 * 4) + ((self.v_pv1_raw & 64) // 64 * 2)) + ((self.v_pv1_raw & 32) // 32 * 1)) + ((self.v_pv1_raw & 16) // 16 * 0.5)) + ((self.v_pv1_raw & 8) // 8 * 0.25)) + ((self.v_pv1_raw & 4) // 4 * 0.125)) + ((self.v_pv1_raw & 2) // 2 * 0.0625)) + ((self.v_pv1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv1', None)

        @property
        def v_hv(self):
            """Voltage at the output of the HV supply to the PPTs measured at FET4-2 [V]."""
            if hasattr(self, '_m_v_hv'):
                return self._m_v_hv

            self._m_v_hv = (((((((((self.v_hv_raw & 128) // 128 * 4) + ((self.v_hv_raw & 64) // 64 * 2)) + ((self.v_hv_raw & 32) // 32 * 1)) + ((self.v_hv_raw & 16) // 16 * 0.5)) + ((self.v_hv_raw & 8) // 8 * 0.25)) + ((self.v_hv_raw & 4) // 4 * 0.125)) + ((self.v_hv_raw & 2) // 2 * 0.0625)) + ((self.v_hv_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_hv', None)

        @property
        def v_bat1(self):
            """Voltage of the battery 1 [V]."""
            if hasattr(self, '_m_v_bat1'):
                return self._m_v_bat1

            self._m_v_bat1 = (((((((((self.v_bat1_raw & 128) // 128 * 4) + ((self.v_bat1_raw & 64) // 64 * 2)) + ((self.v_bat1_raw & 32) // 32 * 1)) + ((self.v_bat1_raw & 16) // 16 * 0.5)) + ((self.v_bat1_raw & 8) // 8 * 0.25)) + ((self.v_bat1_raw & 4) // 4 * 0.125)) + ((self.v_bat1_raw & 2) // 2 * 0.0625)) + ((self.v_bat1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat1', None)

        @property
        def i_pv1_bat2(self):
            """Current through FET2-1 between PV1-bus and battery 2 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat2'):
                return self._m_i_pv1_bat2

            self._m_i_pv1_bat2 = (((((((((self.i_pv1_bat2_raw & 128) // 128 * -8) + ((self.i_pv1_bat2_raw & 64) // 64 * 4)) + ((self.i_pv1_bat2_raw & 32) // 32 * 2)) + ((self.i_pv1_bat2_raw & 16) // 16 * 1)) + ((self.i_pv1_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat2', None)

        @property
        def v_3v3_out(self):
            """Voltage at the output of the 3V3 converter [V]."""
            if hasattr(self, '_m_v_3v3_out'):
                return self._m_v_3v3_out

            self._m_v_3v3_out = (((((((((self.v_3v3_out_raw & 128) // 128 * 4) + ((self.v_3v3_out_raw & 64) // 64 * 2)) + ((self.v_3v3_out_raw & 32) // 32 * 1)) + ((self.v_3v3_out_raw & 16) // 16 * 0.5)) + ((self.v_3v3_out_raw & 8) // 8 * 0.25)) + ((self.v_3v3_out_raw & 4) // 4 * 0.125)) + ((self.v_3v3_out_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_out', None)

        @property
        def v_3v3_in(self):
            """Voltage at the input of the 3V3 converter measured at FET5-2 [V]."""
            if hasattr(self, '_m_v_3v3_in'):
                return self._m_v_3v3_in

            self._m_v_3v3_in = (((((((((self.v_3v3_in_raw & 128) // 128 * 4) + ((self.v_3v3_in_raw & 64) // 64 * 2)) + ((self.v_3v3_in_raw & 32) // 32 * 1)) + ((self.v_3v3_in_raw & 16) // 16 * 0.5)) + ((self.v_3v3_in_raw & 8) // 8 * 0.25)) + ((self.v_3v3_in_raw & 4) // 4 * 0.125)) + ((self.v_3v3_in_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_in', None)

        @property
        def i_pv1_bat1(self):
            """Current through FET1-1 between PV1-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat1'):
                return self._m_i_pv1_bat1

            self._m_i_pv1_bat1 = (((((((((self.i_pv1_bat1_raw & 128) // 128 * -8) + ((self.i_pv1_bat1_raw & 64) // 64 * 4)) + ((self.i_pv1_bat1_raw & 32) // 32 * 2)) + ((self.i_pv1_bat1_raw & 16) // 16 * 1)) + ((self.i_pv1_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat1', None)

        @property
        def i_pv2_3v3(self):
            """Current through FET5-2 between PV2-bus and 3V3 converter [A]."""
            if hasattr(self, '_m_i_pv2_3v3'):
                return self._m_i_pv2_3v3

            self._m_i_pv2_3v3 = (((((((((self.i_pv2_3v3_raw & 128) // 128 * -8) + ((self.i_pv2_3v3_raw & 64) // 64 * 4)) + ((self.i_pv2_3v3_raw & 32) // 32 * 2)) + ((self.i_pv2_3v3_raw & 16) // 16 * 1)) + ((self.i_pv2_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv2_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv2_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv2_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_3v3', None)

        @property
        def vcc_cc1(self):
            """Supply voltage of CC1 (communication controller 1) [V]."""
            if hasattr(self, '_m_vcc_cc1'):
                return self._m_vcc_cc1

            self._m_vcc_cc1 = (((((((((self.vcc_cc1_raw & 128) // 128 * 4) + ((self.vcc_cc1_raw & 64) // 64 * 2)) + ((self.vcc_cc1_raw & 32) // 32 * 1)) + ((self.vcc_cc1_raw & 16) // 16 * 0.5)) + ((self.vcc_cc1_raw & 8) // 8 * 0.25)) + ((self.vcc_cc1_raw & 4) // 4 * 0.125)) + ((self.vcc_cc1_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc1', None)

        @property
        def v_5v_out(self):
            """Voltage at the output of the 5V converter [V]."""
            if hasattr(self, '_m_v_5v_out'):
                return self._m_v_5v_out

            self._m_v_5v_out = (((((((((self.v_5v_out_raw & 128) // 128 * 4) + ((self.v_5v_out_raw & 64) // 64 * 2)) + ((self.v_5v_out_raw & 32) // 32 * 1)) + ((self.v_5v_out_raw & 16) // 16 * 0.5)) + ((self.v_5v_out_raw & 8) // 8 * 0.25)) + ((self.v_5v_out_raw & 4) // 4 * 0.125)) + ((self.v_5v_out_raw & 2) // 2 * 0.0625)) + ((self.v_5v_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_out', None)

        @property
        def v_5v_in(self):
            """Voltage at the input of the 5V converter measured at FET3-1 [V]."""
            if hasattr(self, '_m_v_5v_in'):
                return self._m_v_5v_in

            self._m_v_5v_in = (((((((((self.v_5v_in_raw & 128) // 128 * 4) + ((self.v_5v_in_raw & 64) // 64 * 2)) + ((self.v_5v_in_raw & 32) // 32 * 1)) + ((self.v_5v_in_raw & 16) // 16 * 0.5)) + ((self.v_5v_in_raw & 8) // 8 * 0.25)) + ((self.v_5v_in_raw & 4) // 4 * 0.125)) + ((self.v_5v_in_raw & 2) // 2 * 0.0625)) + ((self.v_5v_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_in', None)

        @property
        def i_pv1_5v(self):
            """Current through FET3-1 between PV1-bus and 5V converter [A]."""
            if hasattr(self, '_m_i_pv1_5v'):
                return self._m_i_pv1_5v

            self._m_i_pv1_5v = (((((((((self.i_pv1_5v_raw & 128) // 128 * -8) + ((self.i_pv1_5v_raw & 64) // 64 * 4)) + ((self.i_pv1_5v_raw & 32) // 32 * 2)) + ((self.i_pv1_5v_raw & 16) // 16 * 1)) + ((self.i_pv1_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv1_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv1_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv1_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_5v', None)

        @property
        def i_pv2_bat2(self):
            """Current through FET2-2 between PV2-bus and battery 2 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv2_bat2'):
                return self._m_i_pv2_bat2

            self._m_i_pv2_bat2 = (((((((((self.i_pv2_bat2_raw & 128) // 128 * -8) + ((self.i_pv2_bat2_raw & 64) // 64 * 4)) + ((self.i_pv2_bat2_raw & 32) // 32 * 2)) + ((self.i_pv2_bat2_raw & 16) // 16 * 1)) + ((self.i_pv2_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat2', None)

        @property
        def i_pv2_bat1(self):
            """Current through FET1-2 between PV2-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv2_bat1'):
                return self._m_i_pv2_bat1

            self._m_i_pv2_bat1 = (((((((((self.i_pv2_bat1_raw & 128) // 128 * -8) + ((self.i_pv2_bat1_raw & 64) // 64 * 4)) + ((self.i_pv2_bat1_raw & 32) // 32 * 2)) + ((self.i_pv2_bat1_raw & 16) // 16 * 1)) + ((self.i_pv2_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat1', None)

        @property
        def i_pv1_3v3(self):
            """Current through FET5-1 between PV1-bus and 3V3 converter [A]."""
            if hasattr(self, '_m_i_pv1_3v3'):
                return self._m_i_pv1_3v3

            self._m_i_pv1_3v3 = (((((((((self.i_pv1_3v3_raw & 128) // 128 * -8) + ((self.i_pv1_3v3_raw & 64) // 64 * 4)) + ((self.i_pv1_3v3_raw & 32) // 32 * 2)) + ((self.i_pv1_3v3_raw & 16) // 16 * 1)) + ((self.i_pv1_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv1_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv1_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv1_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_3v3', None)

        @property
        def v_pv2(self):
            """Voltage at PV2-bus (Solarbus 1) [V]."""
            if hasattr(self, '_m_v_pv2'):
                return self._m_v_pv2

            self._m_v_pv2 = (((((((((self.v_pv2_raw & 128) // 128 * 4) + ((self.v_pv2_raw & 64) // 64 * 2)) + ((self.v_pv2_raw & 32) // 32 * 1)) + ((self.v_pv2_raw & 16) // 16 * 0.5)) + ((self.v_pv2_raw & 8) // 8 * 0.25)) + ((self.v_pv2_raw & 4) // 4 * 0.125)) + ((self.v_pv2_raw & 2) // 2 * 0.0625)) + ((self.v_pv2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv2', None)

        @property
        def i_pv2_5v(self):
            """Current through FET3-2 between PV2-bus and 5V converter [A]."""
            if hasattr(self, '_m_i_pv2_5v'):
                return self._m_i_pv2_5v

            self._m_i_pv2_5v = (((((((((self.i_pv2_5v_raw & 128) // 128 * -8) + ((self.i_pv2_5v_raw & 64) // 64 * 4)) + ((self.i_pv2_5v_raw & 32) // 32 * 2)) + ((self.i_pv2_5v_raw & 16) // 16 * 1)) + ((self.i_pv2_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv2_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv2_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv2_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_5v', None)


    class O2Beacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call = (self._io.read_bytes(6)).decode(u"ASCII")
            self.gps_time_padding = self._io.read_bytes(4)
            self.geo_location_padding = self._io.read_bytes(11)
            self.adcs_status_padding = self._io.read_bytes(1)
            self.adcs_angle_deviation_padding = self._io.read_bytes(1)
            self.status_task_sensors_running = self._io.read_bits_int_be(1) != 0
            self.status_obc_3v3_spa_enabled = self._io.read_bits_int_be(1) != 0
            self.status_obc_power_saving_mode = self._io.read_bits_int_be(1) != 0
            self.status_eps_cc_used = self._io.read_bits_int_be(1) != 0
            self.status_last_reset_source = self._io.read_bits_int_be(2)
            self.status_power_source = self._io.read_bits_int_be(1) != 0
            self.status_crystal_osicallation_in_use = self._io.read_bits_int_be(1) != 0
            self.status_ssp1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_ssp0_initialized = self._io.read_bits_int_be(1) != 0
            self.status_i2c2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_i2c1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_i2c0_initialized = self._io.read_bits_int_be(1) != 0
            self.status_rtc_synchronized = self._io.read_bits_int_be(1) != 0
            self.status_statemachine_initialized = self._io.read_bits_int_be(1) != 0
            self.status_task_maintenance_running = self._io.read_bits_int_be(1) != 0
            self.status_uart_ttc1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_uart_mnlp_initialized = self._io.read_bits_int_be(1) != 0
            self.status_uart_ttc2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_uart_gps_initialized = self._io.read_bits_int_be(1) != 0
            self.status_adc_initialized = self._io.read_bits_int_be(1) != 0
            self.status_rtc_initialized = self._io.read_bits_int_be(1) != 0
            self.status_i2c_switches_initialized = self._io.read_bits_int_be(1) != 0
            self.status_supply_switches_initialized = self._io.read_bits_int_be(1) != 0
            self.status_eeprom3_initialized = self._io.read_bits_int_be(1) != 0
            self.status_eeprom2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_eeprom1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_eps_cc2_operational = self._io.read_bits_int_be(1) != 0
            self.status_eps_cc1_opeational = self._io.read_bits_int_be(1) != 0
            self.status_timer1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_watchdog_initialized = self._io.read_bits_int_be(1) != 0
            self.status_timer0_initialized = self._io.read_bits_int_be(1) != 0
            self.status_mpu_initialized = self._io.read_bits_int_be(1) != 0
            self.status_onboard_tmp100_initialized = self._io.read_bits_int_be(1) != 0
            self.status_onboard_mag_initialized = self._io.read_bits_int_be(1) != 0
            self.status_msp_initialized = self._io.read_bits_int_be(1) != 0
            self.status_gyro2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_gyro1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_mag_bp_boom_initialized = self._io.read_bits_int_be(1) != 0
            self.status_mag_bp_initialized = self._io.read_bits_int_be(1) != 0
            self.status_bp_initialized = self._io.read_bits_int_be(1) != 0
            self.status_sa_initailized = self._io.read_bits_int_be(1) != 0
            self.status_spd_initialized = self._io.read_bits_int_be(1) != 0
            self.status_spc_initialized = self._io.read_bits_int_be(1) != 0
            self.status_spb_initialized = self._io.read_bits_int_be(1) != 0
            self.status_spa_initialized = self._io.read_bits_int_be(1) != 0
            self.status_flash2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_flash1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_spd_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_spc_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_spb_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_spa_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_science_module_initialized = self._io.read_bits_int_be(1) != 0
            self.status_ttc2_initialized = self._io.read_bits_int_be(1) != 0
            self.status_ttc1_initialized = self._io.read_bits_int_be(1) != 0
            self.status_gps_initialized = self._io.read_bits_int_be(1) != 0
            self.status_onboard_mag_powersafe = self._io.read_bits_int_be(1) != 0
            self.status_i2c_sw_d_on = self._io.read_bits_int_be(1) != 0
            self.status_i2c_sw_c_on = self._io.read_bits_int_be(1) != 0
            self.status_i2c_sw_b_on = self._io.read_bits_int_be(1) != 0
            self.status_i2c_sw_a_on = self._io.read_bits_int_be(1) != 0
            self.status_sa_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_bp2_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_bp1_vcc_on = self._io.read_bits_int_be(1) != 0
            self.status_eeprom_page_cycle_overflow = self._io.read_bits_int_be(1) != 0
            self.status_rtc_oscillator_error = self._io.read_bits_int_be(1) != 0
            self.status_mnlp_5v_enabled = self._io.read_bits_int_be(1) != 0
            self.status_mag_bp_boom_power_saving_mode = self._io.read_bits_int_be(1) != 0
            self.status_mag_bp_power_saving_mode = self._io.read_bits_int_be(1) != 0
            self.status_tmp100_powersafe = self._io.read_bits_int_be(1) != 0
            self.status_mpu_powersafe = self._io.read_bits_int_be(1) != 0
            self.status_gyro_powersafe = self._io.read_bits_int_be(1) != 0
            self.status_default_config_used = self._io.read_bits_int_be(1) != 0
            self.status_timer1_running = self._io.read_bits_int_be(1) != 0
            self.status_timer0_running = self._io.read_bits_int_be(1) != 0
            self.status_i2c2_frequent_errors = self._io.read_bits_int_be(1) != 0
            self.status_i2c1_frequent_errors = self._io.read_bits_int_be(1) != 0
            self.status_i2c0_frequent_errors = self._io.read_bits_int_be(1) != 0
            self.status_ssp1_frequent_errors = self._io.read_bits_int_be(1) != 0
            self.status_ssp0_frequent_errors = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.error_code = self._io.read_u1()
            self.error_code_before_reset = self._io.read_u1()
            self.resets_counter = self._io.read_u4le()
            self.temp_sp_x_minus_raw = self._io.read_u1()
            self.temp_sp_x_plus_raw = self._io.read_u1()
            self.temp_sp_y_minus_raw = self._io.read_u1()
            self.temp_sp_y_plus_raw = self._io.read_u1()
            self.script_slot_cs1 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su7 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su6 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su5 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su4 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su3 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su2 = self._io.read_bits_int_be(1) != 0
            self.script_slot_su1 = self._io.read_bits_int_be(1) != 0
            self.script_slot_padding = self._io.read_bits_int_be(4)
            self.script_slot_cs5 = self._io.read_bits_int_be(1) != 0
            self.script_slot_cs4 = self._io.read_bits_int_be(1) != 0
            self.script_slot_cs3 = self._io.read_bits_int_be(1) != 0
            self.script_slot_cs2 = self._io.read_bits_int_be(1) != 0

        @property
        def temp_sp_x_minus(self):
            """Temperature sidepanel X- [°C]."""
            if hasattr(self, '_m_temp_sp_x_minus'):
                return self._m_temp_sp_x_minus

            self._m_temp_sp_x_minus = ((self.temp_sp_x_minus_raw * 2.65) - 273.15)
            return getattr(self, '_m_temp_sp_x_minus', None)

        @property
        def temp_sp_x_plus(self):
            """Temperature sidepanel X+ [°C]."""
            if hasattr(self, '_m_temp_sp_x_plus'):
                return self._m_temp_sp_x_plus

            self._m_temp_sp_x_plus = ((self.temp_sp_x_plus_raw * 2.65) - 273.15)
            return getattr(self, '_m_temp_sp_x_plus', None)

        @property
        def temp_sp_y_minus(self):
            """Temperature sidepanel Y- [°C]."""
            if hasattr(self, '_m_temp_sp_y_minus'):
                return self._m_temp_sp_y_minus

            self._m_temp_sp_y_minus = ((self.temp_sp_y_minus_raw * 2.65) - 273.15)
            return getattr(self, '_m_temp_sp_y_minus', None)

        @property
        def temp_sp_y_plus(self):
            """Temperature sidepanel Y+ [°C]."""
            if hasattr(self, '_m_temp_sp_y_plus'):
                return self._m_temp_sp_y_plus

            self._m_temp_sp_y_plus = ((self.temp_sp_y_plus_raw * 2.65) - 273.15)
            return getattr(self, '_m_temp_sp_y_plus', None)


    class Tt64Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self.pid
            if _on == 192:
                self.beacon = Pegasus.SBeacon(self._io, self, self._root)
            elif _on == 82:
                self.beacon = Pegasus.HkdDownload(self._io, self, self._root)
            elif _on == 86:
                self.beacon = Pegasus.O2Beacon(self._io, self, self._root)
            elif _on == 83:
                self.beacon = Pegasus.O1Beacon(self._io, self, self._root)
            elif _on == 195:
                self.beacon = Pegasus.ABeacon(self._io, self, self._root)
            elif _on == 193:
                self.beacon = Pegasus.EBeacon(self._io, self, self._root)


    class O1Beacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call = (self._io.read_bytes(6)).decode(u"ASCII")
            self.v_pv1_raw = self._io.read_u1()
            self.v_pv2_raw = self._io.read_u1()
            self.v_5v_in_raw = self._io.read_u1()
            self.v_3v3_in_raw = self._io.read_u1()
            self.v_5v_out_raw = self._io.read_u1()
            self.v_3v3_out_raw = self._io.read_u1()
            self.i_pv1_5v_raw = self._io.read_u1()
            self.i_pv2_5v_raw = self._io.read_u1()
            self.i_pv1_3v3_raw = self._io.read_u1()
            self.i_pv2_3v3_raw = self._io.read_u1()
            self.temp_bat1sw = self._io.read_s1()
            self.temp_5v = self._io.read_s1()
            self.v_hv_raw = self._io.read_u1()
            self.i_pv1_bat1_raw = self._io.read_u1()
            self.i_pv2_bat1_raw = self._io.read_u1()
            self.i_pv1_bat2_raw = self._io.read_u1()
            self.i_pv2_bat2_raw = self._io.read_u1()
            self.v_bat1_raw = self._io.read_u1()
            self.v_bat2_raw = self._io.read_u1()
            self.vcc_cc2_raw = self._io.read_u1()
            self.vcc_cc1_raw = self._io.read_u1()
            self.temp_bat1 = self._io.read_s1()
            self.temp_bat2 = self._io.read_s1()
            self.status_1_3v3_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_bu = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_4 = self._io.read_bits_int_be(1) != 0
            self.status_2_power_low = self._io.read_bits_int_be(1) != 0
            self.status_2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_2_3v3 = self._io.read_bits_int_be(1) != 0
            self.status_2_5v = self._io.read_bits_int_be(1) != 0
            self.status_2_mode = self._io.read_bits_int_be(3)
            self.status_3_3v3_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_5v_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_bat1_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_3_bat2_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_3_temp_warning = self._io.read_bits_int_be(1) != 0
            self.status_3_cc1 = self._io.read_bits_int_be(1) != 0
            self.status_3_cc2 = self._io.read_bits_int_be(1) != 0
            self.status_3_rbf = self._io.read_bits_int_be(1) != 0
            self.status_cc1_mode = self._io.read_bits_int_be(2)
            self.status_cc1_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc1_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc1_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_3v3_backup = self._io.read_bits_int_be(1) != 0
            self.status_cc2_mode = self._io.read_bits_int_be(2)
            self.status_cc2_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc2_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc2_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_3v3_backup = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.reboot_mc = self._io.read_u1()
            self.reboot_cc1 = self._io.read_u1()
            self.reboot_cc2 = self._io.read_u1()
            self.temp_a = self._io.read_s1()
            self.temp_c = self._io.read_s1()
            self.rssi_a_raw = self._io.read_u1()
            self.rssi_b_raw = self._io.read_u1()
            self.stacie_mode_a = self._io.read_bits_int_be(4)
            self.stacie_mode_c = self._io.read_bits_int_be(4)
            self.state_machine_su_script = self._io.read_bits_int_be(1) != 0
            self.state_machine_su_powered = self._io.read_bits_int_be(1) != 0
            self.state_machine_adcs = self._io.read_bits_int_be(1) != 0
            self.state_machine_not_used = self._io.read_bits_int_be(1) != 0
            self.state_machine_obc = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.mission_counter = self._io.read_u1()
            self.mission_counter_2 = self._io.read_u1()

        @property
        def vcc_cc2(self):
            """Supply voltage of CC2 (communication controller 2) [V]."""
            if hasattr(self, '_m_vcc_cc2'):
                return self._m_vcc_cc2

            self._m_vcc_cc2 = (((((((((self.vcc_cc2_raw & 128) // 128 * 4) + ((self.vcc_cc2_raw & 64) // 64 * 2)) + ((self.vcc_cc2_raw & 32) // 32 * 1)) + ((self.vcc_cc2_raw & 16) // 16 * 0.5)) + ((self.vcc_cc2_raw & 8) // 8 * 0.25)) + ((self.vcc_cc2_raw & 4) // 4 * 0.125)) + ((self.vcc_cc2_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc2', None)

        @property
        def v_bat2(self):
            """Voltage of the battery 2 [V]."""
            if hasattr(self, '_m_v_bat2'):
                return self._m_v_bat2

            self._m_v_bat2 = (((((((((self.v_bat2_raw & 128) // 128 * 4) + ((self.v_bat2_raw & 64) // 64 * 2)) + ((self.v_bat2_raw & 32) // 32 * 1)) + ((self.v_bat2_raw & 16) // 16 * 0.5)) + ((self.v_bat2_raw & 8) // 8 * 0.25)) + ((self.v_bat2_raw & 4) // 4 * 0.125)) + ((self.v_bat2_raw & 2) // 2 * 0.0625)) + ((self.v_bat2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat2', None)

        @property
        def rssi_a(self):
            """Received Signal Strength Indication of TRX module A during the last uplink [dBm]."""
            if hasattr(self, '_m_rssi_a'):
                return self._m_rssi_a

            self._m_rssi_a = (-132.0 + self.rssi_a_raw // 2)
            return getattr(self, '_m_rssi_a', None)

        @property
        def rssi_b(self):
            """Received Signal Strength Indication of TRX module C during the last uplink [dBm]."""
            if hasattr(self, '_m_rssi_b'):
                return self._m_rssi_b

            self._m_rssi_b = (-132.0 + self.rssi_b_raw // 2)
            return getattr(self, '_m_rssi_b', None)

        @property
        def v_pv1(self):
            """Voltage at PV1-bus (Solarbus 1) [V]."""
            if hasattr(self, '_m_v_pv1'):
                return self._m_v_pv1

            self._m_v_pv1 = (((((((((self.v_pv1_raw & 128) // 128 * 4) + ((self.v_pv1_raw & 64) // 64 * 2)) + ((self.v_pv1_raw & 32) // 32 * 1)) + ((self.v_pv1_raw & 16) // 16 * 0.5)) + ((self.v_pv1_raw & 8) // 8 * 0.25)) + ((self.v_pv1_raw & 4) // 4 * 0.125)) + ((self.v_pv1_raw & 2) // 2 * 0.0625)) + ((self.v_pv1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv1', None)

        @property
        def v_hv(self):
            """Voltage at the output of the HV supply to the PPTs measured at FET4-2 [V]."""
            if hasattr(self, '_m_v_hv'):
                return self._m_v_hv

            self._m_v_hv = (((((((((self.v_hv_raw & 128) // 128 * 4) + ((self.v_hv_raw & 64) // 64 * 2)) + ((self.v_hv_raw & 32) // 32 * 1)) + ((self.v_hv_raw & 16) // 16 * 0.5)) + ((self.v_hv_raw & 8) // 8 * 0.25)) + ((self.v_hv_raw & 4) // 4 * 0.125)) + ((self.v_hv_raw & 2) // 2 * 0.0625)) + ((self.v_hv_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_hv', None)

        @property
        def v_bat1(self):
            """Voltage of the battery 1 [V]."""
            if hasattr(self, '_m_v_bat1'):
                return self._m_v_bat1

            self._m_v_bat1 = (((((((((self.v_bat1_raw & 128) // 128 * 4) + ((self.v_bat1_raw & 64) // 64 * 2)) + ((self.v_bat1_raw & 32) // 32 * 1)) + ((self.v_bat1_raw & 16) // 16 * 0.5)) + ((self.v_bat1_raw & 8) // 8 * 0.25)) + ((self.v_bat1_raw & 4) // 4 * 0.125)) + ((self.v_bat1_raw & 2) // 2 * 0.0625)) + ((self.v_bat1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat1', None)

        @property
        def i_pv1_bat2(self):
            """Current through FET2-1 between PV1-bus and battery 2 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat2'):
                return self._m_i_pv1_bat2

            self._m_i_pv1_bat2 = (((((((((self.i_pv1_bat2_raw & 128) // 128 * -8) + ((self.i_pv1_bat2_raw & 64) // 64 * 4)) + ((self.i_pv1_bat2_raw & 32) // 32 * 2)) + ((self.i_pv1_bat2_raw & 16) // 16 * 1)) + ((self.i_pv1_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat2', None)

        @property
        def v_3v3_out(self):
            """Voltage at the output of the 3V3 converter [V]."""
            if hasattr(self, '_m_v_3v3_out'):
                return self._m_v_3v3_out

            self._m_v_3v3_out = (((((((((self.v_3v3_out_raw & 128) // 128 * 4) + ((self.v_3v3_out_raw & 64) // 64 * 2)) + ((self.v_3v3_out_raw & 32) // 32 * 1)) + ((self.v_3v3_out_raw & 16) // 16 * 0.5)) + ((self.v_3v3_out_raw & 8) // 8 * 0.25)) + ((self.v_3v3_out_raw & 4) // 4 * 0.125)) + ((self.v_3v3_out_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_out', None)

        @property
        def v_3v3_in(self):
            """Voltage at the input of the 3V3 converter measured at FET5-2 [V]."""
            if hasattr(self, '_m_v_3v3_in'):
                return self._m_v_3v3_in

            self._m_v_3v3_in = (((((((((self.v_3v3_in_raw & 128) // 128 * 4) + ((self.v_3v3_in_raw & 64) // 64 * 2)) + ((self.v_3v3_in_raw & 32) // 32 * 1)) + ((self.v_3v3_in_raw & 16) // 16 * 0.5)) + ((self.v_3v3_in_raw & 8) // 8 * 0.25)) + ((self.v_3v3_in_raw & 4) // 4 * 0.125)) + ((self.v_3v3_in_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_in', None)

        @property
        def i_pv1_bat1(self):
            """Current through FET1-1 between PV1-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat1'):
                return self._m_i_pv1_bat1

            self._m_i_pv1_bat1 = (((((((((self.i_pv1_bat1_raw & 128) // 128 * -8) + ((self.i_pv1_bat1_raw & 64) // 64 * 4)) + ((self.i_pv1_bat1_raw & 32) // 32 * 2)) + ((self.i_pv1_bat1_raw & 16) // 16 * 1)) + ((self.i_pv1_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat1', None)

        @property
        def i_pv2_3v3(self):
            """Current through FET5-2 between PV2-bus and 3V3 converter [A]."""
            if hasattr(self, '_m_i_pv2_3v3'):
                return self._m_i_pv2_3v3

            self._m_i_pv2_3v3 = (((((((((self.i_pv2_3v3_raw & 128) // 128 * -8) + ((self.i_pv2_3v3_raw & 64) // 64 * 4)) + ((self.i_pv2_3v3_raw & 32) // 32 * 2)) + ((self.i_pv2_3v3_raw & 16) // 16 * 1)) + ((self.i_pv2_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv2_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv2_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv2_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_3v3', None)

        @property
        def vcc_cc1(self):
            """Supply voltage of CC1 (communication controller 1) [V]."""
            if hasattr(self, '_m_vcc_cc1'):
                return self._m_vcc_cc1

            self._m_vcc_cc1 = (((((((((self.vcc_cc1_raw & 128) // 128 * 4) + ((self.vcc_cc1_raw & 64) // 64 * 2)) + ((self.vcc_cc1_raw & 32) // 32 * 1)) + ((self.vcc_cc1_raw & 16) // 16 * 0.5)) + ((self.vcc_cc1_raw & 8) // 8 * 0.25)) + ((self.vcc_cc1_raw & 4) // 4 * 0.125)) + ((self.vcc_cc1_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc1', None)

        @property
        def v_5v_out(self):
            """Voltage at the output of the 5V converter [V]."""
            if hasattr(self, '_m_v_5v_out'):
                return self._m_v_5v_out

            self._m_v_5v_out = (((((((((self.v_5v_out_raw & 128) // 128 * 4) + ((self.v_5v_out_raw & 64) // 64 * 2)) + ((self.v_5v_out_raw & 32) // 32 * 1)) + ((self.v_5v_out_raw & 16) // 16 * 0.5)) + ((self.v_5v_out_raw & 8) // 8 * 0.25)) + ((self.v_5v_out_raw & 4) // 4 * 0.125)) + ((self.v_5v_out_raw & 2) // 2 * 0.0625)) + ((self.v_5v_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_out', None)

        @property
        def v_5v_in(self):
            """Voltage at the input of the 5V converter measured at FET3-1 [V]."""
            if hasattr(self, '_m_v_5v_in'):
                return self._m_v_5v_in

            self._m_v_5v_in = (((((((((self.v_5v_in_raw & 128) // 128 * 4) + ((self.v_5v_in_raw & 64) // 64 * 2)) + ((self.v_5v_in_raw & 32) // 32 * 1)) + ((self.v_5v_in_raw & 16) // 16 * 0.5)) + ((self.v_5v_in_raw & 8) // 8 * 0.25)) + ((self.v_5v_in_raw & 4) // 4 * 0.125)) + ((self.v_5v_in_raw & 2) // 2 * 0.0625)) + ((self.v_5v_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_in', None)

        @property
        def i_pv1_5v(self):
            """Current through FET3-1 between PV1-bus and 5V converter [A]."""
            if hasattr(self, '_m_i_pv1_5v'):
                return self._m_i_pv1_5v

            self._m_i_pv1_5v = (((((((((self.i_pv1_5v_raw & 128) // 128 * -8) + ((self.i_pv1_5v_raw & 64) // 64 * 4)) + ((self.i_pv1_5v_raw & 32) // 32 * 2)) + ((self.i_pv1_5v_raw & 16) // 16 * 1)) + ((self.i_pv1_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv1_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv1_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv1_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_5v', None)

        @property
        def i_pv2_bat2(self):
            """Current through FET2-2 between PV2-bus and battery 2 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv2_bat2'):
                return self._m_i_pv2_bat2

            self._m_i_pv2_bat2 = (((((((((self.i_pv2_bat2_raw & 128) // 128 * -8) + ((self.i_pv2_bat2_raw & 64) // 64 * 4)) + ((self.i_pv2_bat2_raw & 32) // 32 * 2)) + ((self.i_pv2_bat2_raw & 16) // 16 * 1)) + ((self.i_pv2_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat2', None)

        @property
        def i_pv2_bat1(self):
            """Current through FET1-2 between PV2-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv2_bat1'):
                return self._m_i_pv2_bat1

            self._m_i_pv2_bat1 = (((((((((self.i_pv2_bat1_raw & 128) // 128 * -8) + ((self.i_pv2_bat1_raw & 64) // 64 * 4)) + ((self.i_pv2_bat1_raw & 32) // 32 * 2)) + ((self.i_pv2_bat1_raw & 16) // 16 * 1)) + ((self.i_pv2_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat1', None)

        @property
        def i_pv1_3v3(self):
            """Current through FET5-1 between PV1-bus and 3V3 converter [A]."""
            if hasattr(self, '_m_i_pv1_3v3'):
                return self._m_i_pv1_3v3

            self._m_i_pv1_3v3 = (((((((((self.i_pv1_3v3_raw & 128) // 128 * -8) + ((self.i_pv1_3v3_raw & 64) // 64 * 4)) + ((self.i_pv1_3v3_raw & 32) // 32 * 2)) + ((self.i_pv1_3v3_raw & 16) // 16 * 1)) + ((self.i_pv1_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv1_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv1_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv1_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_3v3', None)

        @property
        def v_pv2(self):
            """Voltage at PV2-bus (Solarbus 1) [V]."""
            if hasattr(self, '_m_v_pv2'):
                return self._m_v_pv2

            self._m_v_pv2 = (((((((((self.v_pv2_raw & 128) // 128 * 4) + ((self.v_pv2_raw & 64) // 64 * 2)) + ((self.v_pv2_raw & 32) // 32 * 1)) + ((self.v_pv2_raw & 16) // 16 * 0.5)) + ((self.v_pv2_raw & 8) // 8 * 0.25)) + ((self.v_pv2_raw & 4) // 4 * 0.125)) + ((self.v_pv2_raw & 2) // 2 * 0.0625)) + ((self.v_pv2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv2', None)

        @property
        def i_pv2_5v(self):
            """Current through FET3-2 between PV2-bus and 5V converter [A]."""
            if hasattr(self, '_m_i_pv2_5v'):
                return self._m_i_pv2_5v

            self._m_i_pv2_5v = (((((((((self.i_pv2_5v_raw & 128) // 128 * -8) + ((self.i_pv2_5v_raw & 64) // 64 * 4)) + ((self.i_pv2_5v_raw & 32) // 32 * 2)) + ((self.i_pv2_5v_raw & 16) // 16 * 1)) + ((self.i_pv2_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv2_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv2_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv2_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_5v', None)


    class ABeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call = (self._io.read_bytes(6)).decode(u"ASCII")
            self.ant_temp_raw = self._io.read_u2le()
            self.ant_deploy_status_mb = self._io.read_u1()
            self.ant_deploy_status_lb = self._io.read_u1()
            self.temp_comp_hw = self._io.read_u1()
            self.padding_a1 = self._io.read_bytes(11)
            self.rbf_state = self._io.read_u1()
            self.sid_a = self._io.read_u1()
            self.stacie_version = self._io.read_u1()

        @property
        def ant_temp(self):
            """Antenna temperature [mA]."""
            if hasattr(self, '_m_ant_temp'):
                return self._m_ant_temp

            self._m_ant_temp = (((3.3 / 1023) * (((self.ant_temp_raw & 255) * 256) + (self.ant_temp_raw & 65280))) * 1000)
            return getattr(self, '_m_ant_temp', None)


    class SBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call = (self._io.read_bytes(6)).decode(u"ASCII")
            self.usp_raw = self._io.read_u2le()
            self.trx_temp = self._io.read_s1()
            self.rssi_idle_raw = self._io.read_u1()
            self.rssi_rx_raw = self._io.read_u1()
            self.antenna_deployment = self._io.read_bits_int_be(8)
            self._io.align_to_byte()
            self.stacie_op = self._io.read_u1()
            self.temp_compensation = self._io.read_u1()
            self.reset_counter = self._io.read_u2le()
            self.uplink_error = self._io.read_u1()
            self.obc_sent_packet_counter_between_s_beacons = self._io.read_u1()
            self.beacon_interval = self._io.read_u2le()
            self.primary_carrier_raw = self._io.read_u2le()
            self.secondary_carrier_raw = self._io.read_u2le()
            self.used_carrier_raw = self._io.read_u2le()
            self.temperature_compensation_carrier_raw = self._io.read_u2le()
            self.sid_s = self._io.read_u1()
            self.tx_sel_reason = self._io.read_u1()
            self.reason_remote = self._io.read_u1()
            self.s_time_raw = self._io.read_u4le()
            self.gs_cmd_counter = self._io.read_u1()
            self.beacon_count = self._io.read_u1()
            self.prim_freq_start = self._io.read_u2le()
            self.sec_freq_start = self._io.read_u2le()

        @property
        def used_carrier(self):
            """Used carrier frequency for this S-beacon [Hz]."""
            if hasattr(self, '_m_used_carrier'):
                return self._m_used_carrier

            self._m_used_carrier = ((((self.used_carrier_raw * 156.25) / 1000) + 430000) * 100)
            return getattr(self, '_m_used_carrier', None)

        @property
        def s_time(self):
            """STACIE uptime since last reset [s]."""
            if hasattr(self, '_m_s_time'):
                return self._m_s_time

            self._m_s_time = self.s_time_raw // 1000
            return getattr(self, '_m_s_time', None)

        @property
        def usp(self):
            """Supply voltage of STACIE [V]."""
            if hasattr(self, '_m_usp'):
                return self._m_usp

            self._m_usp = ((((self.usp_raw & 255) * 256) + (self.usp_raw & 65280)) / ((1023 * 2) * 3.3))
            return getattr(self, '_m_usp', None)

        @property
        def rssi_idle(self):
            """Received Signal Strength Indication of TRX module without TX [dBm]."""
            if hasattr(self, '_m_rssi_idle'):
                return self._m_rssi_idle

            self._m_rssi_idle = ((((((((((self.rssi_idle_raw & 128) // 128 * 64) + ((self.rssi_idle_raw & 64) // 64 * 32)) + ((self.rssi_idle_raw & 32) // 32 * 16)) + ((self.rssi_idle_raw & 16) // 16 * 8)) + ((self.rssi_idle_raw & 8) // 8 * 4)) + ((self.rssi_idle_raw & 4) // 4 * 2)) + ((self.rssi_idle_raw & 2) // 2 * 1)) + ((self.rssi_idle_raw & 1) // 1 * 0.5)) - 132.0)
            return getattr(self, '_m_rssi_idle', None)

        @property
        def primary_carrier(self):
            """Carrier Frequency of the primary RX frequency [Hz]."""
            if hasattr(self, '_m_primary_carrier'):
                return self._m_primary_carrier

            self._m_primary_carrier = ((((self.primary_carrier_raw * 156.25) / 1000) + 430000) * 100)
            return getattr(self, '_m_primary_carrier', None)

        @property
        def rssi_rx(self):
            """Received Signal Strength Indication of TRX module during RX [dBm]."""
            if hasattr(self, '_m_rssi_rx'):
                return self._m_rssi_rx

            self._m_rssi_rx = ((((((((((self.rssi_rx_raw & 128) // 128 * 64) + ((self.rssi_rx_raw & 64) // 64 * 32)) + ((self.rssi_rx_raw & 32) // 32 * 16)) + ((self.rssi_rx_raw & 16) // 16 * 8)) + ((self.rssi_rx_raw & 8) // 8 * 4)) + ((self.rssi_rx_raw & 4) // 4 * 2)) + ((self.rssi_rx_raw & 2) // 2 * 1)) + ((self.rssi_rx_raw & 1) // 1 * 0.5)) - 132.0)
            return getattr(self, '_m_rssi_rx', None)

        @property
        def temperature_compensation_carrier(self):
            """Frequency compensated carrier [Hz]."""
            if hasattr(self, '_m_temperature_compensation_carrier'):
                return self._m_temperature_compensation_carrier

            self._m_temperature_compensation_carrier = ((((self.temperature_compensation_carrier_raw * 156.25) / 1000) + 430000) * 100)
            return getattr(self, '_m_temperature_compensation_carrier', None)

        @property
        def secondary_carrier(self):
            """Carrier Frequency of the secondary RX frequency [Hz]."""
            if hasattr(self, '_m_secondary_carrier'):
                return self._m_secondary_carrier

            self._m_secondary_carrier = ((((self.secondary_carrier_raw * 156.25) / 1000) + 430000) * 100)
            return getattr(self, '_m_secondary_carrier', None)


    class EBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.call = (self._io.read_bytes(6)).decode(u"ASCII")
            self.i_pv2_5v_raw = self._io.read_s1()
            self.i_pv1_5v_raw = self._io.read_s1()
            self.v_pv2_raw = self._io.read_u1()
            self.v_5v_in_raw = self._io.read_u1()
            self.i_pv1_3v3_raw = self._io.read_s1()
            self.i_pv2_3v3_raw = self._io.read_s1()
            self.v_pv1_raw = self._io.read_u1()
            self.v_3v3_in_raw = self._io.read_u1()
            self.temp_bat1sw = self._io.read_s1()
            self.temp_5v = self._io.read_s1()
            self.i_pv1_hv_raw = self._io.read_s1()
            self.i_pv2_hv_raw = self._io.read_s1()
            self.v_3v3_out_raw = self._io.read_u1()
            self.v_hv_raw = self._io.read_u1()
            self.i_pv2_bat1_raw = self._io.read_s1()
            self.i_pv1_bat1_raw = self._io.read_s1()
            self.v_5v_out_raw = self._io.read_u1()
            self.v_bat1_raw = self._io.read_u1()
            self.i_pv2_bat2_raw = self._io.read_s1()
            self.i_pv1_bat2_raw = self._io.read_s1()
            self.eps_version = self._io.read_u1()
            self.sid_e = self._io.read_u1()
            self.v_bat2_raw = self._io.read_u1()
            self.temp_bat1 = self._io.read_s1()
            self.temp_bat2 = self._io.read_s1()
            self.status_1_3v3_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_3v3_bu = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_1 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_2 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_3 = self._io.read_bits_int_be(1) != 0
            self.status_1_5v_4 = self._io.read_bits_int_be(1) != 0
            self.status_2_power_low = self._io.read_bits_int_be(1) != 0
            self.status_2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_2_3v3 = self._io.read_bits_int_be(1) != 0
            self.status_2_5v = self._io.read_bits_int_be(1) != 0
            self.status_2_mode = self._io.read_bits_int_be(3)
            self.status_3_3v3_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_5v_burst = self._io.read_bits_int_be(1) != 0
            self.status_3_bat1_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_3_bat2_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_3_temp_warning = self._io.read_bits_int_be(1) != 0
            self.status_3_cc1 = self._io.read_bits_int_be(1) != 0
            self.status_3_cc2 = self._io.read_bits_int_be(1) != 0
            self.status_3_rbf = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.padding_e1 = self._io.read_bytes(1)
            self.s_beacon_count = self._io.read_u1()
            self.reboot_mc = self._io.read_u1()
            self.reboot_cc1 = self._io.read_u1()
            self.reboot_cc2 = self._io.read_u1()
            self.vcc_cc1_raw = self._io.read_u1()
            self.temp_cc1 = self._io.read_s1()
            self.vcc_cc2_raw = self._io.read_u1()
            self.temp_cc2 = self._io.read_s1()
            self.status_cc1_mode = self._io.read_bits_int_be(2)
            self.status_cc1_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc1_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc1_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc1_3v3_backup = self._io.read_bits_int_be(1) != 0
            self.status_cc2_mode = self._io.read_bits_int_be(2)
            self.status_cc2_mc_timeout = self._io.read_bits_int_be(1) != 0
            self.status_cc2_tbd = self._io.read_bits_int_be(1) != 0
            self.status_cc2_en_i2c = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat1_pv1 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_bat2_pv2 = self._io.read_bits_int_be(1) != 0
            self.status_cc2_3v3_backup = self._io.read_bits_int_be(1) != 0

        @property
        def vcc_cc2(self):
            """Supply voltage of CC (communication controller) [V]."""
            if hasattr(self, '_m_vcc_cc2'):
                return self._m_vcc_cc2

            self._m_vcc_cc2 = (((((((((self.vcc_cc2_raw & 128) // 128 * 4) + ((self.vcc_cc2_raw & 64) // 64 * 2)) + ((self.vcc_cc2_raw & 32) // 32 * 1)) + ((self.vcc_cc2_raw & 16) // 16 * 0.5)) + ((self.vcc_cc2_raw & 8) // 8 * 0.25)) + ((self.vcc_cc2_raw & 4) // 4 * 0.125)) + ((self.vcc_cc2_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc2', None)

        @property
        def v_bat2(self):
            """Voltage of the battery 2."""
            if hasattr(self, '_m_v_bat2'):
                return self._m_v_bat2

            self._m_v_bat2 = (((((((((self.v_bat2_raw & 128) // 128 * 4) + ((self.v_bat2_raw & 64) // 64 * 2)) + ((self.v_bat2_raw & 32) // 32 * 1)) + ((self.v_bat2_raw & 16) // 16 * 0.5)) + ((self.v_bat2_raw & 8) // 8 * 0.25)) + ((self.v_bat2_raw & 4) // 4 * 0.125)) + ((self.v_bat2_raw & 2) // 2 * 0.0625)) + ((self.v_bat2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat2', None)

        @property
        def v_pv1(self):
            """Voltage at PV1-bus (Solarbus 1) [V]."""
            if hasattr(self, '_m_v_pv1'):
                return self._m_v_pv1

            self._m_v_pv1 = (((((((((self.v_pv1_raw & 128) // 128 * 4) + ((self.v_pv1_raw & 64) // 64 * 2)) + ((self.v_pv1_raw & 32) // 32 * 1)) + ((self.v_pv1_raw & 16) // 16 * 0.5)) + ((self.v_pv1_raw & 8) // 8 * 0.25)) + ((self.v_pv1_raw & 4) // 4 * 0.125)) + ((self.v_pv1_raw & 2) // 2 * 0.0625)) + ((self.v_pv1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv1', None)

        @property
        def v_hv(self):
            """Voltage at the output of the HV supply to the PPTs measured at FET4-2 [V]."""
            if hasattr(self, '_m_v_hv'):
                return self._m_v_hv

            self._m_v_hv = (((((((((self.v_hv_raw & 128) // 128 * 4) + ((self.v_hv_raw & 64) // 64 * 2)) + ((self.v_hv_raw & 32) // 32 * 1)) + ((self.v_hv_raw & 16) // 16 * 0.5)) + ((self.v_hv_raw & 8) // 8 * 0.25)) + ((self.v_hv_raw & 4) // 4 * 0.125)) + ((self.v_hv_raw & 2) // 2 * 0.0625)) + ((self.v_hv_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_hv', None)

        @property
        def v_bat1(self):
            """Voltage of the battery 1 [V]."""
            if hasattr(self, '_m_v_bat1'):
                return self._m_v_bat1

            self._m_v_bat1 = (((((((((self.v_bat1_raw & 128) // 128 * 4) + ((self.v_bat1_raw & 64) // 64 * 2)) + ((self.v_bat1_raw & 32) // 32 * 1)) + ((self.v_bat1_raw & 16) // 16 * 0.5)) + ((self.v_bat1_raw & 8) // 8 * 0.25)) + ((self.v_bat1_raw & 4) // 4 * 0.125)) + ((self.v_bat1_raw & 2) // 2 * 0.0625)) + ((self.v_bat1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_bat1', None)

        @property
        def i_pv1_bat2(self):
            """Current through FET2-1 between PV1-bus and battery 2 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat2'):
                return self._m_i_pv1_bat2

            self._m_i_pv1_bat2 = (((((((((self.i_pv1_bat2_raw & 128) // 128 * -8) + ((self.i_pv1_bat2_raw & 64) // 64 * 4)) + ((self.i_pv1_bat2_raw & 32) // 32 * 2)) + ((self.i_pv1_bat2_raw & 16) // 16 * 1)) + ((self.i_pv1_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat2', None)

        @property
        def v_3v3_out(self):
            """Voltage at the output of the 3V3 converter [V]."""
            if hasattr(self, '_m_v_3v3_out'):
                return self._m_v_3v3_out

            self._m_v_3v3_out = (((((((((self.v_3v3_out_raw & 128) // 128 * 4) + ((self.v_3v3_out_raw & 64) // 64 * 2)) + ((self.v_3v3_out_raw & 32) // 32 * 1)) + ((self.v_3v3_out_raw & 16) // 16 * 0.5)) + ((self.v_3v3_out_raw & 8) // 8 * 0.25)) + ((self.v_3v3_out_raw & 4) // 4 * 0.125)) + ((self.v_3v3_out_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_out', None)

        @property
        def v_3v3_in(self):
            """Voltage at the input of the 3V3 converter measured at FET5-2 [V]."""
            if hasattr(self, '_m_v_3v3_in'):
                return self._m_v_3v3_in

            self._m_v_3v3_in = (((((((((self.v_3v3_in_raw & 128) // 128 * 4) + ((self.v_3v3_in_raw & 64) // 64 * 2)) + ((self.v_3v3_in_raw & 32) // 32 * 1)) + ((self.v_3v3_in_raw & 16) // 16 * 0.5)) + ((self.v_3v3_in_raw & 8) // 8 * 0.25)) + ((self.v_3v3_in_raw & 4) // 4 * 0.125)) + ((self.v_3v3_in_raw & 2) // 2 * 0.0625)) + ((self.v_3v3_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_3v3_in', None)

        @property
        def i_pv1_bat1(self):
            """Current through FET1-1 between PV1-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv1_bat1'):
                return self._m_i_pv1_bat1

            self._m_i_pv1_bat1 = (((((((((self.i_pv1_bat1_raw & 128) // 128 * -8) + ((self.i_pv1_bat1_raw & 64) // 64 * 4)) + ((self.i_pv1_bat1_raw & 32) // 32 * 2)) + ((self.i_pv1_bat1_raw & 16) // 16 * 1)) + ((self.i_pv1_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv1_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv1_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv1_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_bat1', None)

        @property
        def i_pv2_3v3(self):
            """Current through FET5-2 between PV2-bus and 3V3 converter."""
            if hasattr(self, '_m_i_pv2_3v3'):
                return self._m_i_pv2_3v3

            self._m_i_pv2_3v3 = (((((((((self.i_pv2_3v3_raw & 128) // 128 * -8) + ((self.i_pv2_3v3_raw & 64) // 64 * 4)) + ((self.i_pv2_3v3_raw & 32) // 32 * 2)) + ((self.i_pv2_3v3_raw & 16) // 16 * 1)) + ((self.i_pv2_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv2_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv2_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv2_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_3v3', None)

        @property
        def vcc_cc1(self):
            """Supply voltage of CC1 (communication controller 1) [V]."""
            if hasattr(self, '_m_vcc_cc1'):
                return self._m_vcc_cc1

            self._m_vcc_cc1 = (((((((((self.vcc_cc1_raw & 128) // 128 * 4) + ((self.vcc_cc1_raw & 64) // 64 * 2)) + ((self.vcc_cc1_raw & 32) // 32 * 1)) + ((self.vcc_cc1_raw & 16) // 16 * 0.5)) + ((self.vcc_cc1_raw & 8) // 8 * 0.25)) + ((self.vcc_cc1_raw & 4) // 4 * 0.125)) + ((self.vcc_cc1_raw & 2) // 2 * 0.0625)) + ((self.vcc_cc1_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_vcc_cc1', None)

        @property
        def v_5v_out(self):
            """Voltage at the output of the 5V converter [V]."""
            if hasattr(self, '_m_v_5v_out'):
                return self._m_v_5v_out

            self._m_v_5v_out = (((((((((self.v_5v_out_raw & 128) // 128 * 4) + ((self.v_5v_out_raw & 64) // 64 * 2)) + ((self.v_5v_out_raw & 32) // 32 * 1)) + ((self.v_5v_out_raw & 16) // 16 * 0.5)) + ((self.v_5v_out_raw & 8) // 8 * 0.25)) + ((self.v_5v_out_raw & 4) // 4 * 0.125)) + ((self.v_5v_out_raw & 2) // 2 * 0.0625)) + ((self.v_5v_out_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_out', None)

        @property
        def v_5v_in(self):
            """Voltage at input 5V converter measured at FET3-1 [V]."""
            if hasattr(self, '_m_v_5v_in'):
                return self._m_v_5v_in

            self._m_v_5v_in = (((((((((self.v_5v_in_raw & 128) // 128 * 4) + ((self.v_5v_in_raw & 64) // 64 * 2)) + ((self.v_5v_in_raw & 32) // 32 * 1)) + ((self.v_5v_in_raw & 16) // 16 * 0.5)) + ((self.v_5v_in_raw & 8) // 8 * 0.25)) + ((self.v_5v_in_raw & 4) // 4 * 0.125)) + ((self.v_5v_in_raw & 2) // 2 * 0.0625)) + ((self.v_5v_in_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_5v_in', None)

        @property
        def i_pv1_5v(self):
            """Current through FET3-1 between PV1-bus and 5V converter."""
            if hasattr(self, '_m_i_pv1_5v'):
                return self._m_i_pv1_5v

            self._m_i_pv1_5v = (((((((((self.i_pv1_5v_raw & 128) // 128 * -8) + ((self.i_pv1_5v_raw & 64) // 64 * 4)) + ((self.i_pv1_5v_raw & 32) // 32 * 2)) + ((self.i_pv1_5v_raw & 16) // 16 * 1)) + ((self.i_pv1_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv1_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv1_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv1_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_5v', None)

        @property
        def i_pv2_bat2(self):
            """Current through FET2-2 between PV2-bus and battery 2 [A]
            + charging, - discharging  
            """
            if hasattr(self, '_m_i_pv2_bat2'):
                return self._m_i_pv2_bat2

            self._m_i_pv2_bat2 = (((((((((self.i_pv2_bat2_raw & 128) // 128 * -8) + ((self.i_pv2_bat2_raw & 64) // 64 * 4)) + ((self.i_pv2_bat2_raw & 32) // 32 * 2)) + ((self.i_pv2_bat2_raw & 16) // 16 * 1)) + ((self.i_pv2_bat2_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat2_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat2_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat2_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat2', None)

        @property
        def i_pv2_bat1(self):
            """Current through FET1-2 between PV2-bus and battery 1 [A]
            + charging, - discharging
            """
            if hasattr(self, '_m_i_pv2_bat1'):
                return self._m_i_pv2_bat1

            self._m_i_pv2_bat1 = (((((((((self.i_pv2_bat1_raw & 128) // 128 * -8) + ((self.i_pv2_bat1_raw & 64) // 64 * 4)) + ((self.i_pv2_bat1_raw & 32) // 32 * 2)) + ((self.i_pv2_bat1_raw & 16) // 16 * 1)) + ((self.i_pv2_bat1_raw & 8) // 8 * 0.5)) + ((self.i_pv2_bat1_raw & 4) // 4 * 0.25)) + ((self.i_pv2_bat1_raw & 2) // 2 * 0.125)) + ((self.i_pv2_bat1_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_bat1', None)

        @property
        def i_pv1_3v3(self):
            """Current through FET5-1 between PV1-bus and 3V3 converter [A]."""
            if hasattr(self, '_m_i_pv1_3v3'):
                return self._m_i_pv1_3v3

            self._m_i_pv1_3v3 = (((((((((self.i_pv1_3v3_raw & 128) // 128 * -8) + ((self.i_pv1_3v3_raw & 64) // 64 * 4)) + ((self.i_pv1_3v3_raw & 32) // 32 * 2)) + ((self.i_pv1_3v3_raw & 16) // 16 * 1)) + ((self.i_pv1_3v3_raw & 8) // 8 * 0.5)) + ((self.i_pv1_3v3_raw & 4) // 4 * 0.25)) + ((self.i_pv1_3v3_raw & 2) // 2 * 0.125)) + ((self.i_pv1_3v3_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv1_3v3', None)

        @property
        def v_pv2(self):
            """Voltage at PV2-bus (Solarbus 2) [V]."""
            if hasattr(self, '_m_v_pv2'):
                return self._m_v_pv2

            self._m_v_pv2 = (((((((((self.v_pv2_raw & 128) // 128 * 4) + ((self.v_pv2_raw & 64) // 64 * 2)) + ((self.v_pv2_raw & 32) // 32 * 1)) + ((self.v_pv2_raw & 16) // 16 * 0.5)) + ((self.v_pv2_raw & 8) // 8 * 0.25)) + ((self.v_pv2_raw & 4) // 4 * 0.125)) + ((self.v_pv2_raw & 2) // 2 * 0.0625)) + ((self.v_pv2_raw & 1) // 1 * 0.03125))
            return getattr(self, '_m_v_pv2', None)

        @property
        def i_pv2_5v(self):
            """Current through FET3-2 between PV2-bus and 5V converter [A]."""
            if hasattr(self, '_m_i_pv2_5v'):
                return self._m_i_pv2_5v

            self._m_i_pv2_5v = (((((((((self.i_pv2_5v_raw & 128) // 128 * -8) + ((self.i_pv2_5v_raw & 64) // 64 * 4)) + ((self.i_pv2_5v_raw & 32) // 32 * 2)) + ((self.i_pv2_5v_raw & 16) // 16 * 1)) + ((self.i_pv2_5v_raw & 8) // 8 * 0.5)) + ((self.i_pv2_5v_raw & 4) // 4 * 0.25)) + ((self.i_pv2_5v_raw & 2) // 2 * 0.125)) + ((self.i_pv2_5v_raw & 1) // 1 * 0.0625))
            return getattr(self, '_m_i_pv2_5v', None)



