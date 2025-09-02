# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cubebel2(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field beacon_trx_id: ax25_frame.payload.ax25_info.trx_beacon.beacon_id
    :field beacon_uptime: ax25_frame.payload.ax25_info.trx_beacon.beacon_uptime
    :field beacon_vbus: ax25_frame.payload.ax25_info.trx_beacon.beacon_vbus
    :field beacon_reset_total_cnt: ax25_frame.payload.ax25_info.trx_beacon.beacon_reset_total_cnt
    :field beacon_reset_iwdg_cnt: ax25_frame.payload.ax25_info.trx_beacon.beacon_reset_iwdg_cnt
    :field beacon_reset_iwdg_time: ax25_frame.payload.ax25_info.trx_beacon.beacon_reset_iwdg_time
    :field beacon_pamp_temp: ax25_frame.payload.ax25_info.trx_beacon.beacon_pamp_temp
    :field beacon_rx_settings: ax25_frame.payload.ax25_info.trx_beacon.beacon_rx_settings
    :field beacon_rx_period_on: ax25_frame.payload.ax25_info.trx_beacon.beacon_rx_period_on
    :field beacon_rx_seqnum: ax25_frame.payload.ax25_info.trx_beacon.beacon_rx_seqnum
    :field beacon_rx_cnt_total: ax25_frame.payload.ax25_info.trx_beacon.beacon_rx_cnt_total
    :field beacon_rx_cnt_valid: ax25_frame.payload.ax25_info.trx_beacon.beacon_rx_cnt_valid
    :field beacon_tx_settings: ax25_frame.payload.ax25_info.trx_beacon.beacon_tx_settings
    :field beacon_tx_pwr: ax25_frame.payload.ax25_info.trx_beacon.beacon_tx_pwr
    :field beacon_tx_cnt: ax25_frame.payload.ax25_info.trx_beacon.beacon_tx_cnt
    :field cdm_id: ax25_frame.payload.ax25_info.cdm_header.cdm_id
    :field cdm_addr_src: ax25_frame.payload.ax25_info.cdm_header.cdm_addr_src
    :field config_mb_1: ax25_frame.payload.ax25_info.cdm_payload.record_mb.0.value
    :field config_mb_2: ax25_frame.payload.ax25_info.cdm_payload.record_mb.1.value
    :field config_mb_3: ax25_frame.payload.ax25_info.cdm_payload.record_mb.2.value
    :field config_mb_4: ax25_frame.payload.ax25_info.cdm_payload.record_mb.3.value
    :field config_mb_5: ax25_frame.payload.ax25_info.cdm_payload.record_mb.4.value
    :field config_mb_6: ax25_frame.payload.ax25_info.cdm_payload.record_mb.5.value
    :field config_mb_7: ax25_frame.payload.ax25_info.cdm_payload.record_mb.6.value
    :field config_mb_8: ax25_frame.payload.ax25_info.cdm_payload.record_mb.7.value
    :field config_mb_9: ax25_frame.payload.ax25_info.cdm_payload.record_mb.8.value
    :field config_mb_10: ax25_frame.payload.ax25_info.cdm_payload.record_mb.9.value
    :field config_mb_11: ax25_frame.payload.ax25_info.cdm_payload.record_mb.10.value
    :field config_mb_12: ax25_frame.payload.ax25_info.cdm_payload.record_mb.11.value
    :field config_mb_13: ax25_frame.payload.ax25_info.cdm_payload.record_mb.12.value
    :field config_mb_14: ax25_frame.payload.ax25_info.cdm_payload.record_mb.13.value
    :field config_mb_15: ax25_frame.payload.ax25_info.cdm_payload.record_mb.14.value
    :field config_mb_16: ax25_frame.payload.ax25_info.cdm_payload.record_mb.15.value
    :field config_mb_17: ax25_frame.payload.ax25_info.cdm_payload.record_mb.16.value
    :field config_mb_18: ax25_frame.payload.ax25_info.cdm_payload.record_mb.17.value
    :field config_mb_19: ax25_frame.payload.ax25_info.cdm_payload.record_mb.18.value
    :field config_trx_1: ax25_frame.payload.ax25_info.cdm_payload.record_trx.0.value
    :field config_trx_2: ax25_frame.payload.ax25_info.cdm_payload.record_trx.1.value
    :field config_trx_3: ax25_frame.payload.ax25_info.cdm_payload.record_trx.2.value
    :field config_trx_4: ax25_frame.payload.ax25_info.cdm_payload.record_trx.3.value
    :field config_trx_5: ax25_frame.payload.ax25_info.cdm_payload.record_trx.4.value
    :field config_trx_6: ax25_frame.payload.ax25_info.cdm_payload.record_trx.5.value
    :field config_trx_7: ax25_frame.payload.ax25_info.cdm_payload.record_trx.6.value
    :field config_trx_8: ax25_frame.payload.ax25_info.cdm_payload.record_trx.7.value
    :field config_trx_9: ax25_frame.payload.ax25_info.cdm_payload.record_trx.8.value
    :field config_trx_10: ax25_frame.payload.ax25_info.cdm_payload.record_trx.9.value
    :field config_trx_11: ax25_frame.payload.ax25_info.cdm_payload.record_trx.10.value
    :field config_trx_12: ax25_frame.payload.ax25_info.cdm_payload.record_trx.11.value
    :field config_trx_13: ax25_frame.payload.ax25_info.cdm_payload.record_trx.12.value
    :field config_trx_14: ax25_frame.payload.ax25_info.cdm_payload.record_trx.13.value
    :field config_trx_15: ax25_frame.payload.ax25_info.cdm_payload.record_trx.14.value
    :field config_trx_16: ax25_frame.payload.ax25_info.cdm_payload.record_trx.15.value
    :field config_trx_17: ax25_frame.payload.ax25_info.cdm_payload.record_trx.16.value
    :field config_trx_18: ax25_frame.payload.ax25_info.cdm_payload.record_trx.17.value
    :field config_trx_19: ax25_frame.payload.ax25_info.cdm_payload.record_trx.18.value
    :field config_trx_20: ax25_frame.payload.ax25_info.cdm_payload.record_trx.19.value
    :field config_trx_21: ax25_frame.payload.ax25_info.cdm_payload.record_trx.20.value
    :field config_trx_22: ax25_frame.payload.ax25_info.cdm_payload.record_trx.21.value
    :field config_trx_23: ax25_frame.payload.ax25_info.cdm_payload.record_trx.22.value
    :field config_trx_24: ax25_frame.payload.ax25_info.cdm_payload.record_trx.23.value
    :field config_trx_25: ax25_frame.payload.ax25_info.cdm_payload.record_trx.24.value
    :field config_trx_26: ax25_frame.payload.ax25_info.cdm_payload.record_trx.25.value
    :field fwver_githash: ax25_frame.payload.ax25_info.cdm_payload.version_githash
    :field rfreply_rssi: ax25_frame.payload.ax25_info.cdm_payload.ax5043_rssi
    :field rfreply_agc: ax25_frame.payload.ax25_info.cdm_payload.ax5043_agc
    :field rfreply_seq_enabled: ax25_frame.payload.ax25_info.cdm_payload.command_seq_enabled
    :field rfreply_seq_valid: ax25_frame.payload.ax25_info.cdm_payload.command_seq_valid
    :field rfreply_seq_num: ax25_frame.payload.ax25_info.cdm_payload.command_seq_num
    :field tlm_mb_time: ax25_frame.payload.ax25_info.cdm_payload.time
    :field tlm_mb_mcusr: ax25_frame.payload.ax25_info.cdm_payload.mcusr
    :field tlm_mb_rst_cnt_total: ax25_frame.payload.ax25_info.cdm_payload.rst_cnt_total
    :field tlm_mb_rst_cnt_iwdg: ax25_frame.payload.ax25_info.cdm_payload.rst_cnt_iwdg
    :field tlm_mb_adc_status: ax25_frame.payload.ax25_info.cdm_payload.adc_status
    :field tlm_mb_adc_temp_1: ax25_frame.payload.ax25_info.cdm_payload.adc_temp_1
    :field tlm_mb_adc_temp_2: ax25_frame.payload.ax25_info.cdm_payload.adc_temp_2
    :field tlm_mb_ant_1_v: ax25_frame.payload.ax25_info.cdm_payload.ant_1_v
    :field tlm_mb_ant_2_v: ax25_frame.payload.ax25_info.cdm_payload.ant_2_v
    :field tlm_mb_solar_common_v: ax25_frame.payload.ax25_info.cdm_payload.solar_common_v
    :field tlm_mb_sat_bus_v: ax25_frame.payload.ax25_info.cdm_payload.sat_bus_v
    :field tlm_mb_sat_bus_c: ax25_frame.payload.ax25_info.cdm_payload.sat_bus_c
    :field tlm_mb_uc_v: ax25_frame.payload.ax25_info.cdm_payload.uc_v
    :field tlm_mb_uc_c: ax25_frame.payload.ax25_info.cdm_payload.uc_c
    :field tlm_mb_battpack_0_voltage: ax25_frame.payload.ax25_info.cdm_payload.battery_back.0.voltage
    :field tlm_mb_battpack_0_element_0_current: ax25_frame.payload.ax25_info.cdm_payload.battery_back.0.element.0.current
    :field tlm_mb_battpack_0_element_0_temp: ax25_frame.payload.ax25_info.cdm_payload.battery_back.0.element.0.temp
    :field tlm_mb_battpack_0_element_1_current: ax25_frame.payload.ax25_info.cdm_payload.battery_back.0.element.1.current
    :field tlm_mb_battpack_0_element_1_temp: ax25_frame.payload.ax25_info.cdm_payload.battery_back.0.element.1.temp
    :field tlm_mb_battpack_1_voltage: ax25_frame.payload.ax25_info.cdm_payload.battery_back.1.voltage
    :field tlm_mb_battpack_1_element_0_current: ax25_frame.payload.ax25_info.cdm_payload.battery_back.1.element.0.current
    :field tlm_mb_battpack_1_element_0_temp: ax25_frame.payload.ax25_info.cdm_payload.battery_back.1.element.0.temp
    :field tlm_mb_battpack_1_element_1_current: ax25_frame.payload.ax25_info.cdm_payload.battery_back.1.element.1.current
    :field tlm_mb_battpack_1_element_1_temp: ax25_frame.payload.ax25_info.cdm_payload.battery_back.1.element.1.temp
    :field tlm_mb_solarpanel_0_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.0.current
    :field tlm_mb_solarpanel_0_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.0.volt_pos
    :field tlm_mb_solarpanel_0_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.0.volt_neg
    :field tlm_mb_solarpanel_1_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.1.current
    :field tlm_mb_solarpanel_1_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.1.volt_pos
    :field tlm_mb_solarpanel_1_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.1.volt_neg
    :field tlm_mb_solarpanel_2_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.2.current
    :field tlm_mb_solarpanel_2_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.2.volt_pos
    :field tlm_mb_solarpanel_2_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.2.volt_neg
    :field tlm_mb_solarpanel_3_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.3.current
    :field tlm_mb_solarpanel_3_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.3.volt_pos
    :field tlm_mb_solarpanel_3_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.3.volt_neg
    :field tlm_mb_solarpanel_4_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.4.current
    :field tlm_mb_solarpanel_4_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.4.volt_pos
    :field tlm_mb_solarpanel_4_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.4.volt_neg
    :field tlm_mb_solarpanel_5_current: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.5.current
    :field tlm_mb_solarpanel_5_volt_pos: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.5.volt_pos
    :field tlm_mb_solarpanel_5_volt_neg: ax25_frame.payload.ax25_info.cdm_payload.solarpanel.5.volt_neg
    :field tlm_mb_slot_0_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.0.voltage
    :field tlm_mb_slot_0_current: ax25_frame.payload.ax25_info.cdm_payload.slot.0.current
    :field tlm_mb_slot_1_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.1.voltage
    :field tlm_mb_slot_1_current: ax25_frame.payload.ax25_info.cdm_payload.slot.1.current
    :field tlm_mb_slot_2_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.2.voltage
    :field tlm_mb_slot_2_current: ax25_frame.payload.ax25_info.cdm_payload.slot.2.current
    :field tlm_mb_slot_3_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.3.voltage
    :field tlm_mb_slot_3_current: ax25_frame.payload.ax25_info.cdm_payload.slot.3.current
    :field tlm_mb_slot_4_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.4.voltage
    :field tlm_mb_slot_4_current: ax25_frame.payload.ax25_info.cdm_payload.slot.4.current
    :field tlm_mb_slot_5_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.5.voltage
    :field tlm_mb_slot_5_current: ax25_frame.payload.ax25_info.cdm_payload.slot.5.current
    :field tlm_mb_slot_6_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.6.voltage
    :field tlm_mb_slot_6_current: ax25_frame.payload.ax25_info.cdm_payload.slot.6.current
    :field tlm_mb_slot_7_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.7.voltage
    :field tlm_mb_slot_7_current: ax25_frame.payload.ax25_info.cdm_payload.slot.7.current
    :field tlm_mb_slot_8_voltage: ax25_frame.payload.ax25_info.cdm_payload.slot.8.voltage
    :field tlm_mb_slot_8_current: ax25_frame.payload.ax25_info.cdm_payload.slot.8.current
    :field tlm_mb_solartemp_0_temp_0: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.0.temp.0
    :field tlm_mb_solartemp_0_temp_1: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.0.temp.1
    :field tlm_mb_solartemp_0_temp_2: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.0.temp.2
    :field tlm_mb_solartemp_0_temp_3: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.0.temp.3
    :field tlm_mb_solartemp_1_temp_0: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.1.temp.0
    :field tlm_mb_solartemp_1_temp_1: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.1.temp.1
    :field tlm_mb_solartemp_1_temp_2: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.1.temp.2
    :field tlm_mb_solartemp_1_temp_3: ax25_frame.payload.ax25_info.cdm_payload.solar_temp.1.temp.3
    :field tlm_mb_oc_cnt_solar: ax25_frame.payload.ax25_info.cdm_payload.solar_bus_oc_cnt
    :field tlm_mb_oc_cnt_batt_0: ax25_frame.payload.ax25_info.cdm_payload.batt_pack_oc_cnt.0
    :field tlm_mb_oc_cnt_batt_1: ax25_frame.payload.ax25_info.cdm_payload.batt_pack_oc_cnt.1
    :field tlm_mb_powerswitch_trx: ax25_frame.payload.ax25_info.cdm_payload.power_switch_trx
    :field tlm_mb_powerswitch_0: ax25_frame.payload.ax25_info.cdm_payload.power_switch_state.raw.0
    :field tlm_mb_powerswitch_1: ax25_frame.payload.ax25_info.cdm_payload.power_switch_state.raw.1
    :field tlm_mb_powerswitch_2: ax25_frame.payload.ax25_info.cdm_payload.power_switch_state.raw.2
    :field tlm_trx_cmn_boardid: ax25_frame.payload.ax25_info.cdm_payload.common_trx.board_id_cdm
    :field tlm_trx_cmn_reset_cnt: ax25_frame.payload.ax25_info.cdm_payload.common_trx.board_rst_total_cnt
    :field tlm_trx_cmn_reset_iwdg_cnt: ax25_frame.payload.ax25_info.cdm_payload.common_trx.board_rst_iwdg_cnt
    :field tlm_trx_cmn_reset_iwdg_timestamp: ax25_frame.payload.ax25_info.cdm_payload.common_trx.board_rst_iwdg_timestamp
    :field tlm_trx_cmn_mcu_csr: ax25_frame.payload.ax25_info.cdm_payload.common_trx.mcu_rcc_csr
    :field tlm_trx_cmn_mcu_uptime: ax25_frame.payload.ax25_info.cdm_payload.common_trx.mcu_uptime
    :field tlm_trx_cmn_mcu_temp: ax25_frame.payload.ax25_info.cdm_payload.common_trx.mcu_temp
    :field tlm_trx_cmn_rtc_unixtime: ax25_frame.payload.ax25_info.cdm_payload.common_trx.rtc_unixtime
    :field tlm_trx_cmn_rtc_vbat: ax25_frame.payload.ax25_info.cdm_payload.common_trx.rtc_bat
    :field tlm_trx_boardid: ax25_frame.payload.ax25_info.cdm_payload.board_id_modem
    :field tlm_trx_vbus: ax25_frame.payload.ax25_info.cdm_payload.board_vbus
    :field tlm_trx_startup_previous: ax25_frame.payload.ax25_info.cdm_payload.startup_unixtime_previous
    :field tlm_trx_startup_current: ax25_frame.payload.ax25_info.cdm_payload.startup_unixtime_current
    :field tlm_trx_ds600_temp: ax25_frame.payload.ax25_info.cdm_payload.ds600_temp
    :field tlm_trx_tmp75_temp: ax25_frame.payload.ax25_info.cdm_payload.tmp75_temp
    :field tlm_trx_pamp_current_tx: ax25_frame.payload.ax25_info.cdm_payload.ina226_temp_current_tx
    :field tlm_trx_pamp_voltage_tx: ax25_frame.payload.ax25_info.cdm_payload.ina226_temp_voltage_tx
    :field tlm_trx_ax5043_enabled: ax25_frame.payload.ax25_info.cdm_payload.tps2042_ch1_enabled
    :field tlm_trx_ax5043_oc: ax25_frame.payload.ax25_info.cdm_payload.tps2042_ch1_oc
    :field tlm_trx_lna_enabled: ax25_frame.payload.ax25_info.cdm_payload.tps2042_ch2_enabled
    :field tlm_trx_lna_oc: ax25_frame.payload.ax25_info.cdm_payload.tps2042_ch2_oc
    :field tlm_trx_pamp_oc: ax25_frame.payload.ax25_info.cdm_payload.tps2032_oc
    :field tlm_trx_pamp_enabled: ax25_frame.payload.ax25_info.cdm_payload.tps61078_enabled
    :field tlm_trx_modem_state: ax25_frame.payload.ax25_info.cdm_payload.modem_state
    :field tlm_trx_modem_pwr_fwd: ax25_frame.payload.ax25_info.cdm_payload.modem_pwr_fwd
    :field tlm_trx_modem_pwr_rev: ax25_frame.payload.ax25_info.cdm_payload.modem_pwr_rev
    :field tlm_trx_modem_rx_freq: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_freq
    :field tlm_trx_modem_rx_datarate: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_datarate
    :field tlm_trx_modem_rx_mode: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_mode
    :field tlm_trx_modem_rx_period_on: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_period_on
    :field tlm_trx_modem_rx_period_off: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_period_off
    :field tlm_trx_modem_rx_cnt_all: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_cnt_all
    :field tlm_trx_modem_rx_cnt_valid: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_cnt_valid
    :field tlm_trx_modem_rx_seqnum: ax25_frame.payload.ax25_info.cdm_payload.modem_rx_seqnum
    :field tlm_trx_modem_tx_freq: ax25_frame.payload.ax25_info.cdm_payload.modem_tx_freq
    :field tlm_trx_modem_tx_datarate: ax25_frame.payload.ax25_info.cdm_payload.modem_tx_datarate
    :field tlm_trx_modem_tx_pwr: ax25_frame.payload.ax25_info.cdm_payload.modem_tx_pwr
    :field tlm_trx_modem_tx_cnt_all: ax25_frame.payload.ax25_info.cdm_payload.modem_tx_cnt_all
    :field tlm_trx_modem_cnt_digipeater_ax25: ax25_frame.payload.ax25_info.cdm_payload.modem_cnt_digipeater_ax25
    :field tlm_trx_modem_cnt_digipeater_greencube_rx: ax25_frame.payload.ax25_info.cdm_payload.modem_cnt_digipeater_greencube_rx
    :field tlm_trx_modem_cnt_digipeater_greencube_tx: ax25_frame.payload.ax25_info.cdm_payload.modem_cnt_digipeater_greencube_tx
    :field tlm_trx_message: ax25_frame.payload.ax25_info.cdm_payload.text_msg
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Cubebel2.Ax25Frame(self._io, self, self._root)

    class MbSolarpanelTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.current = self._io.read_u2le()
            self.volt_pos = self._io.read_u2le()
            self.volt_neg = self._io.read_u2le()


    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Cubebel2.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 3:
                self.payload = Cubebel2.UiFrame(self._io, self, self._root)


    class TrxBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_id = self._io.read_u1()
            self.beacon_uptime = self._io.read_u4le()
            self.beacon_vbus = self._io.read_u2le()
            self.beacon_reset_total_cnt = self._io.read_u1()
            self.beacon_reset_iwdg_cnt = self._io.read_u1()
            self.beacon_reset_iwdg_time = self._io.read_u4le()
            self.beacon_pamp_temp = self._io.read_u2le()
            self.beacon_rx_settings = self._io.read_u1()
            self.beacon_rx_period_on = self._io.read_u2le()
            self.beacon_rx_seqnum = self._io.read_u2le()
            self.beacon_rx_cnt_total = self._io.read_u1()
            self.beacon_rx_cnt_valid = self._io.read_u1()
            self.beacon_tx_settings = self._io.read_u1()
            self.beacon_tx_pwr = self._io.read_s1()
            self.beacon_tx_cnt = self._io.read_u1()


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Cubebel2.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Cubebel2.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Cubebel2.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Cubebel2.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class MbSlotTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2le()
            self.current = self._io.read_u2le()
            self.oc_cnt = self._io.read_u1()


    class MbSolarpanelTempTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temp = []
            for i in range(4):
                self.temp.append(self._io.read_u2le())



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
            self.ax25_info = Cubebel2.Frame(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"EU11S ") or (self.callsign == u"EU1XX ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.trx_beacon = Cubebel2.TrxBeacon(self._io, self, self._root)
            self.cdm_datalen = self._io.read_u1()
            self.cdm_header = Cubebel2.CdmHeader(self._io, self, self._root)
            _on = self.cdm_header.cdm_id
            if _on == 33272:
                self.cdm_payload = Cubebel2.CdmConfigTrxAns(self._io, self, self._root)
            elif _on == 36770:
                self.cdm_payload = Cubebel2.CdmTrxRfreplyAns(self._io, self, self._root)
            elif _on == 33372:
                self.cdm_payload = Cubebel2.CdmConfigTrxAns(self._io, self, self._root)
            elif _on == 33179:
                self.cdm_payload = Cubebel2.CdmConfigMotherboardAns(self._io, self, self._root)
            elif _on == 33169:
                self.cdm_payload = Cubebel2.CdmTelemetryGetAnsMotherboard(self._io, self, self._root)
            elif _on == 33369:
                self.cdm_payload = Cubebel2.CdmConfigMotherboardAns(self._io, self, self._root)
            elif _on == 33172:
                self.cdm_payload = Cubebel2.CdmTelemetryGetAnsTrx(self._io, self, self._root)
            elif _on == 32770:
                self.cdm_payload = Cubebel2.CdmVersionGetAns(self._io, self, self._root)


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


    class CdmTrxRfreplyAns(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax5043_timer = self._io.read_u4le()
            self.ax5043_track_rf_freq = self._io.read_u4le()
            self.ax5043_datarate = self._io.read_u4le()
            self.ax5043_track_freq = self._io.read_s2le()
            self.ax5043_rssi = self._io.read_u1()
            self.ax5043_agc = self._io.read_u1()
            self.ax5043_background_noise = self._io.read_u1()
            self.command_hash = []
            for i in range(28):
                self.command_hash.append(self._io.read_u1())

            self.command_key_idx = self._io.read_u4le()
            self.command_seq_enabled = self._io.read_u1()
            self.command_seq_valid = self._io.read_u1()
            self.command_seq_num = self._io.read_u2le()


    class MbBattTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.element = []
            for i in range(2):
                self.element.append(Cubebel2.MbBattElementTelemetry(self._io, self, self._root))

            self.voltage = self._io.read_u2le()


    class MbBattElementTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.voltage = self._io.read_u2le()
            self.current = self._io.read_u2le()
            self.temp = self._io.read_u2le()


    class CdmTelemetryGetAnsTrx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common_trx = Cubebel2.CdmTelemetryGetAnsCommonTrx(self._io, self, self._root)
            self.board_id_modem = self._io.read_u1()
            self.board_vbus = self._io.read_f4le()
            self.startup_unixtime_previous = self._io.read_u4le()
            self.startup_unixtime_current = self._io.read_u4le()
            self.ds600_inited = self._io.read_u1()
            self.ds600_enabled = self._io.read_u1()
            self.ds600_temp = self._io.read_f4le()
            self.tmp75_inited = self._io.read_u1()
            self.tmp75_temp = self._io.read_f4le()
            self.ina226_pamp_inited = self._io.read_u1()
            self.ina226_pamp_current = self._io.read_f4le()
            self.ina226_temp_current_tx = self._io.read_f4le()
            self.ina226_pamp_voltage = self._io.read_f4le()
            self.ina226_temp_voltage_tx = self._io.read_f4le()
            self.tps2042_inited = self._io.read_u1()
            self.tps2042_ch1_enabled = self._io.read_u1()
            self.tps2042_ch1_oc = self._io.read_u1()
            self.tps2042_ch2_enabled = self._io.read_u1()
            self.tps2042_ch2_oc = self._io.read_u1()
            self.tps2032_inited = self._io.read_u1()
            self.tps2032_oc = self._io.read_u1()
            self.tps61078_inited = self._io.read_u1()
            self.tps61078_enabled = self._io.read_u1()
            self.modem_inited = self._io.read_u1()
            self.modem_state = self._io.read_u1()
            self.modem_pwr_fwd = self._io.read_f4le()
            self.modem_pwr_rev = self._io.read_f4le()
            self.modem_rx_freq = self._io.read_u4le()
            self.modem_rx_datarate = self._io.read_u4le()
            self.modem_rx_mode = self._io.read_u1()
            self.modem_rx_period_on = self._io.read_u4le()
            self.modem_rx_period_off = self._io.read_u4le()
            self.modem_rx_cnt_all = self._io.read_u4le()
            self.modem_rx_cnt_valid = self._io.read_u4le()
            self.modem_rx_seqnum = self._io.read_u4le()
            self.modem_tx_freq = self._io.read_u4le()
            self.modem_tx_datarate = self._io.read_u4le()
            self.modem_tx_pwr = self._io.read_s1()
            self.modem_tx_cnt_all = self._io.read_u4le()
            self.modem_cnt_digipeater_ax25 = self._io.read_u4le()
            self.modem_cnt_digipeater_greencube_rx = self._io.read_u4le()
            self.modem_cnt_digipeater_greencube_tx = self._io.read_u4le()
            self.text_msg = (self._io.read_bytes_full()).decode(u"ASCII")


    class CdmTelemetryGetAnsMotherboard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time = self._io.read_u2le()
            self.mcusr = self._io.read_u1()
            self.rst_cnt_total = self._io.read_u1()
            self.rst_cnt_iwdg = self._io.read_u1()
            self.adc_status = self._io.read_u1()
            self.adc_temp_1 = self._io.read_u2le()
            self.adc_temp_2 = self._io.read_u2le()
            self.ant_1_v = self._io.read_u2le()
            self.ant_2_v = self._io.read_u2le()
            self.solar_common_v = self._io.read_u2le()
            self.sat_bus_v = self._io.read_u2le()
            self.sat_bus_c = self._io.read_u2le()
            self.uc_v = self._io.read_u2le()
            self.uc_c = self._io.read_u2le()
            self.battery_back = []
            for i in range(2):
                self.battery_back.append(Cubebel2.MbBattTelemetry(self._io, self, self._root))

            self.solarpanel = []
            for i in range(6):
                self.solarpanel.append(Cubebel2.MbSolarpanelTelemetry(self._io, self, self._root))

            self.slot = []
            for i in range(9):
                self.slot.append(Cubebel2.MbSlotTelemetry(self._io, self, self._root))

            self.solar_temp = []
            for i in range(2):
                self.solar_temp.append(Cubebel2.MbSolarpanelTempTelemetry(self._io, self, self._root))

            self.solar_bus_oc_cnt = self._io.read_u1()
            self.batt_pack_oc_cnt = []
            for i in range(2):
                self.batt_pack_oc_cnt.append(self._io.read_u1())

            self.power_switch_trx = self._io.read_u2le()
            self.power_switch_state = Cubebel2.MbPowerSwitchState(self._io, self, self._root)


    class CdmConfigMotherboardRecord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u1()
            self.value = self._io.read_u2le()


    class CdmConfigMotherboardAns(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.record_mb = []
            i = 0
            while not self._io.is_eof():
                self.record_mb.append(Cubebel2.CdmConfigMotherboardRecord(self._io, self, self._root))
                i += 1



    class MbPowerSwitchState(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = []
            for i in range(3):
                self.raw.append(self._io.read_u1())



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
            self.callsign_ror = Cubebel2.Callsign(_io__raw_callsign_ror, self, self._root)


    class CdmConfigStm32l4Record(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.id = self._io.read_u1()
            self.value = self._io.read_u4le()


    class CdmVersionGetAns(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_githash = (self._io.read_bytes_full()).decode(u"ASCII")


    class CdmHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cdm_id = self._io.read_u2le()
            self.cdm_addr_src = self._io.read_u1()
            self.cdm_addr_dst = self._io.read_u1()
            self.cdm_priority = self._io.read_u1()
            self.cdm_delay = self._io.read_u2le()
            self.cdm_datalen = self._io.read_u1()


    class CdmConfigTrxAns(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.record_trx = []
            i = 0
            while not self._io.is_eof():
                self.record_trx.append(Cubebel2.CdmConfigStm32l4Record(self._io, self, self._root))
                i += 1



    class CdmTelemetryGetAnsCommonTrx(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.board_id_cdm = self._io.read_u1()
            self.board_rst_total_cnt = self._io.read_u1()
            self.board_rst_iwdg_cnt = self._io.read_u1()
            self.board_rst_iwdg_timestamp = self._io.read_u4le()
            self.mcu_rcc_csr = self._io.read_u1()
            self.mcu_uptime = self._io.read_u4le()
            self.rtc_unixtime = self._io.read_s8le()
            self.rtc_bat = self._io.read_f4le()
            self.mcu_temp = self._io.read_f4le()



