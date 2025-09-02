# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Amicalsat(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field start: ax25_frame.payload.ax25_info.start
    :field tlm_area: ax25_frame.payload.ax25_info.tlm_area
    :field tlm_type: ax25_frame.payload.ax25_info.tlm_area_switch.tlm_type
    :field m1_cpu_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cpu_voltage_volt
    :field m1_boot_number_int: ax25_frame.payload.ax25_info.tlm_area_switch.m1.boot_number_int
    :field m1_cpu_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cpu_temperature_degree
    :field m1_up_time_int: ax25_frame.payload.ax25_info.tlm_area_switch.m1.up_time_int
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.m1.timestamp_int
    :field m1_imc_aocs_ok: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_aocs_ok
    :field m1_imc_cu_l_ok: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_cu_l_ok
    :field m1_imc_cu_r_ok: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_cu_r_ok
    :field m1_imc_vhf1_ok: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_vhf1_ok
    :field m1_imc_uhf2_ok: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_uhf2_ok
    :field m1_vhf1_downlink: ax25_frame.payload.ax25_info.tlm_area_switch.m1.vhf1_downlink
    :field m1_uhf2_downlink: ax25_frame.payload.ax25_info.tlm_area_switch.m1.uhf2_downlink
    :field m1_imc_check: ax25_frame.payload.ax25_info.tlm_area_switch.m1.imc_check
    :field m1_beacon_mode: ax25_frame.payload.ax25_info.tlm_area_switch.m1.beacon_mode
    :field m1_cyclic_reset_on: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cyclic_reset_on
    :field m1_survival_mode: ax25_frame.payload.ax25_info.tlm_area_switch.m1.survival_mode
    :field m1_payload_off: ax25_frame.payload.ax25_info.tlm_area_switch.m1.payload_off
    :field m1_cu_auto_off: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cu_auto_off
    :field m1_tm_log: ax25_frame.payload.ax25_info.tlm_area_switch.m1.tm_log
    :field m1_cul_on: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cul_on
    :field m1_cul_faut: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cul_faut
    :field m1_cur_on: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cur_on
    :field m1_cur_fault: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cur_fault
    :field m1_cu_on: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cu_on
    :field m1_cul_dead: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cul_dead
    :field m1_cur_dead: ax25_frame.payload.ax25_info.tlm_area_switch.m1.cur_dead
    :field m1_fault_3v_r: ax25_frame.payload.ax25_info.tlm_area_switch.m1.fault_3v_r
    :field m1_fault_3v_m: ax25_frame.payload.ax25_info.tlm_area_switch.m1.fault_3v_m
    :field m1_charge_r: ax25_frame.payload.ax25_info.tlm_area_switch.m1.charge_r
    :field m1_charge_m: ax25_frame.payload.ax25_info.tlm_area_switch.m1.charge_m
    :field m1_long_log: ax25_frame.payload.ax25_info.tlm_area_switch.m1.long_log
    :field m1_log_to_flash: ax25_frame.payload.ax25_info.tlm_area_switch.m1.log_to_flash
    :field m1_plan: ax25_frame.payload.ax25_info.tlm_area_switch.m1.plan
    :field m1_stream: ax25_frame.payload.ax25_info.tlm_area_switch.m1.stream
    :field m1_vhf1_packet_ready: ax25_frame.payload.ax25_info.tlm_area_switch.m1.vhf1_packet_ready
    :field m1_uhf2_packet_ready: ax25_frame.payload.ax25_info.tlm_area_switch.m1.uhf2_packet_ready
    :field m1_survival_start: ax25_frame.payload.ax25_info.tlm_area_switch.m1.survival_start
    :field m1_survival_end: ax25_frame.payload.ax25_info.tlm_area_switch.m1.survival_end
    :field a1_adcs_mode: ax25_frame.payload.ax25_info.tlm_area_switch.a1.adcs_mode
    :field a1_faults: ax25_frame.payload.ax25_info.tlm_area_switch.a1.faults
    :field a1_detumbling: ax25_frame.payload.ax25_info.tlm_area_switch.a1.detumbling
    :field a1_adcs_on_off: ax25_frame.payload.ax25_info.tlm_area_switch.a1.adcs_on_off
    :field a1_detumbling_status: ax25_frame.payload.ax25_info.tlm_area_switch.a1.detumbling_status
    :field a1_manual: ax25_frame.payload.ax25_info.tlm_area_switch.a1.manual
    :field a1_act_on_off: ax25_frame.payload.ax25_info.tlm_area_switch.a1.act_on_off
    :field a1_sun_contr: ax25_frame.payload.ax25_info.tlm_area_switch.a1.sun_contr
    :field a1_sens_on_off: ax25_frame.payload.ax25_info.tlm_area_switch.a1.sens_on_off
    :field a1_act_man_contr: ax25_frame.payload.ax25_info.tlm_area_switch.a1.act_man_contr
    :field a1_act_limited_contr: ax25_frame.payload.ax25_info.tlm_area_switch.a1.act_limited_contr
    :field a1_gyro_acc_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.gyro_acc_fault
    :field a1_mag_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_fault
    :field a1_sun_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.sun_fault
    :field a1_l1_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.l1_fault
    :field a1_l2_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.l2_fault
    :field a1_l3_fault: ax25_frame.payload.ax25_info.tlm_area_switch.a1.l3_fault
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.timestamp_int
    :field a1_mag_x: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_x
    :field a1_mag_y: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_y
    :field a1_mag_z: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_z
    :field a1_mag_x_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_x_int
    :field a1_mag_y_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_y_int
    :field a1_mag_z_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.mag_z_int
    :field a1_gyro_x_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.gyro_x_int
    :field a1_gyro_y_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.gyro_y_int
    :field a1_gyro_z_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.gyro_z_int
    :field a1_latitude_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.latitude_int
    :field a1_longitude_int: ax25_frame.payload.ax25_info.tlm_area_switch.a1.longitude_int
    :field em_boot_number_int: ax25_frame.payload.ax25_info.tlm_area_switch.em.boot_number_int
    :field em_input_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.em.input_voltage_volt
    :field em_input_current_ma: ax25_frame.payload.ax25_info.tlm_area_switch.em.input_current_ma
    :field em_input_power_mw: ax25_frame.payload.ax25_info.tlm_area_switch.em.input_power_mw
    :field em_peak_power_mw: ax25_frame.payload.ax25_info.tlm_area_switch.em.peak_power_mw
    :field em_solar_panel_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.em.solar_panel_voltage_volt
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.em.timestamp_int
    :field em_v_in_volt: ax25_frame.payload.ax25_info.tlm_area_switch.em.v_in_volt
    :field em_v_solar_volt: ax25_frame.payload.ax25_info.tlm_area_switch.em.v_solar_volt
    :field em_i_in_ma: ax25_frame.payload.ax25_info.tlm_area_switch.em.i_in_ma
    :field em_p_in_mw: ax25_frame.payload.ax25_info.tlm_area_switch.em.p_in_mw
    :field em_p_peak_mw: ax25_frame.payload.ax25_info.tlm_area_switch.em.p_peak_mw
    :field em_t_cpu_degree: ax25_frame.payload.ax25_info.tlm_area_switch.em.t_cpu_degree
    :field em_v_cpu_volt: ax25_frame.payload.ax25_info.tlm_area_switch.em.v_cpu_volt
    :field timestamp: ax25_frame.payload.ax25_info.tlm_area_switch.er.timestamp
    :field boot_number: ax25_frame.payload.ax25_info.tlm_area_switch.er.boot_number
    :field er_input_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.er.input_voltage_volt
    :field er_input_current_ma: ax25_frame.payload.ax25_info.tlm_area_switch.er.input_current_ma
    :field er_input_power_mw: ax25_frame.payload.ax25_info.tlm_area_switch.er.input_power_mw
    :field er_peak_power_mw: ax25_frame.payload.ax25_info.tlm_area_switch.er.peak_power_mw
    :field er_solar_panel_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.er.solar_panel_voltage_volt
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.er.timestamp_int
    :field er_v_in_volt: ax25_frame.payload.ax25_info.tlm_area_switch.er.v_in_volt
    :field er_v_solar_volt: ax25_frame.payload.ax25_info.tlm_area_switch.er.v_solar_volt
    :field er_i_in_ma: ax25_frame.payload.ax25_info.tlm_area_switch.er.i_in_ma
    :field er_p_in_mw: ax25_frame.payload.ax25_info.tlm_area_switch.er.p_in_mw
    :field er_p_peak_mw: ax25_frame.payload.ax25_info.tlm_area_switch.er.p_peak_mw
    :field er_t_cpu_degree: ax25_frame.payload.ax25_info.tlm_area_switch.er.t_cpu_degree
    :field er_v_cpu_volt: ax25_frame.payload.ax25_info.tlm_area_switch.er.v_cpu_volt
    :field timestamp: ax25_frame.payload.ax25_info.tlm_area_switch.v1.timestamp
    :field v1_cpu_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.v1.cpu_voltage_volt
    :field v1_battery_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.v1.battery_voltage_volt
    :field v1_cpu_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.v1.cpu_temperature_degree
    :field v1_amplifier_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.v1.amplifier_temperature_degree
    :field v1_fec: ax25_frame.payload.ax25_info.tlm_area_switch.v1.fec
    :field v1_downlink: ax25_frame.payload.ax25_info.tlm_area_switch.v1.downlink
    :field v1_band_lock: ax25_frame.payload.ax25_info.tlm_area_switch.v1.band_lock
    :field v1_xor: ax25_frame.payload.ax25_info.tlm_area_switch.v1.xor
    :field v1_aes_128: ax25_frame.payload.ax25_info.tlm_area_switch.v1.aes_128
    :field v1_amp_ovt: ax25_frame.payload.ax25_info.tlm_area_switch.v1.amp_ovt
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.v1.timestamp_int
    :field v1_current_rssi_int: ax25_frame.payload.ax25_info.tlm_area_switch.v1.current_rssi_int
    :field v1_latch_rssi_int: ax25_frame.payload.ax25_info.tlm_area_switch.v1.latch_rssi_int
    :field v1_a_f_c_offset_int: ax25_frame.payload.ax25_info.tlm_area_switch.v1.a_f_c_offset_int
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.u2.timestamp_int
    :field u2_cpu_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.u2.cpu_voltage_volt
    :field u2_battery_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.u2.battery_voltage_volt
    :field u2_cpu_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.u2.cpu_temperature_degree
    :field u2_amplifier_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.u2.amplifier_temperature_degree
    :field u2_fec: ax25_frame.payload.ax25_info.tlm_area_switch.u2.fec
    :field u2_downlink: ax25_frame.payload.ax25_info.tlm_area_switch.u2.downlink
    :field u2_band_lock: ax25_frame.payload.ax25_info.tlm_area_switch.u2.band_lock
    :field u2_xor: ax25_frame.payload.ax25_info.tlm_area_switch.u2.xor
    :field u2_aes_128: ax25_frame.payload.ax25_info.tlm_area_switch.u2.aes_128
    :field u2_amp_ovt: ax25_frame.payload.ax25_info.tlm_area_switch.u2.amp_ovt
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.u2.timestamp_int
    :field u2_current_rssi_int: ax25_frame.payload.ax25_info.tlm_area_switch.u2.current_rssi_int
    :field u2_latch_rssi_int: ax25_frame.payload.ax25_info.tlm_area_switch.u2.latch_rssi_int
    :field u2_a_f_c_offset_int: ax25_frame.payload.ax25_info.tlm_area_switch.u2.a_f_c_offset_int
    :field cu_r_return_value_int: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.return_value_int
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.timestamp_int
    :field cu_r_cpu_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.cpu_voltage_volt
    :field cu_r_cpu_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.cpu_temperature_degree
    :field cu_r_onyx_on: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.onyx_on
    :field cu_r_llc_onyx_fault: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.llc_onyx_fault
    :field cu_r_llc_sram_fault: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.llc_sram_fault
    :field cu_r_fault_1v8_r: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.fault_1v8_r
    :field cu_r_fault_1v8_m: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.fault_1v8_m
    :field cu_r_fault_3v3_12v: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.fault_3v3_12v
    :field cu_r_pic_ready_raw: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.pic_ready_raw
    :field cu_r_pic_ready_conv: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.pic_ready_conv
    :field cu_r_pic_ready_compressed: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.pic_ready_compressed
    :field cu_r_pic_ready_compressed_8: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.pic_ready_compressed_8
    :field cu_r_sd_pic_write_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.sd_pic_write_ok
    :field cu_r_sd_pic_read_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.sd_pic_read_ok
    :field cu_r_sd_get_info_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.sd_get_info_ok
    :field cu_r_sd_erase_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.sd_erase_ok
    :field cu_r_sd_full: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.sd_full
    :field cu_r_adc_ready: ax25_frame.payload.ax25_info.tlm_area_switch.cu_r.adc_ready
    :field timestamp_int: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.timestamp_int
    :field cu_l_cpu_voltage_volt: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.cpu_voltage_volt
    :field cu_l_cpu_temperature_degree: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.cpu_temperature_degree
    :field cu_l_onyx_on: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.onyx_on
    :field cu_l_llc_onyx_fault: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.llc_onyx_fault
    :field cu_l_llc_sram_fault: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.llc_sram_fault
    :field cu_l_fault_1v8_r: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.fault_1v8_r
    :field cu_l_fault_1v8_m: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.fault_1v8_m
    :field cu_l_fault_3v3_12v: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.fault_3v3_12v
    :field cu_l_pic_ready_raw: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.pic_ready_raw
    :field cu_l_pic_ready_conv: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.pic_ready_conv
    :field cu_l_pic_ready_compressed: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.pic_ready_compressed
    :field cu_l_pic_ready_compressed_8: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.pic_ready_compressed_8
    :field cu_l_sd_pic_write_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.sd_pic_write_ok
    :field cu_l_sd_pic_read_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.sd_pic_read_ok
    :field cu_l_sd_get_info_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.sd_get_info_ok
    :field cu_l_sd_erase_ok: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.sd_erase_ok
    :field cu_l_sd_full: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.sd_full
    :field cu_l_adc_ready: ax25_frame.payload.ax25_info.tlm_area_switch.cu_l.adc_ready
    :field aprs_message: ax25_frame.payload.ax25_info.aprs_message
    
    .. seealso::
       Source - https://gitlab.com/librespacefoundation/satnogs-ops/uploads/f6fde8b864f8cdf37d65433bd958e138/AmicalSat_downlinks_v0.3.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Amicalsat.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Amicalsat.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Amicalsat.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Amicalsat.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Amicalsat.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Amicalsat.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Amicalsat.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Amicalsat.IFrame(self._io, self, self._root)


    class CuRLogType(KaitaiStruct):
        """CU_R;LOG;[Timestamp];[CPU voltage];[CPU temperature];[flags]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.flagsmagic = self._io.read_bytes(2)
            if not self.flagsmagic == b"\x30\x78":
                raise kaitaistruct.ValidationNotEqualError(b"\x30\x78", self.flagsmagic, self._io, u"/types/cu_r_log_type/seq/3")
            self.cu_flags = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def cpu_temperature_degree(self):
            if hasattr(self, '_m_cpu_temperature_degree'):
                return self._m_cpu_temperature_degree

            self._m_cpu_temperature_degree = int(self.cpu_temperature)
            return getattr(self, '_m_cpu_temperature_degree', None)

        @property
        def sd_pic_write_ok(self):
            if hasattr(self, '_m_sd_pic_write_ok'):
                return self._m_sd_pic_write_ok

            self._m_sd_pic_write_ok = ((int(self.cu_flags, 16) & 1024) >> 10)
            return getattr(self, '_m_sd_pic_write_ok', None)

        @property
        def sd_pic_read_ok(self):
            if hasattr(self, '_m_sd_pic_read_ok'):
                return self._m_sd_pic_read_ok

            self._m_sd_pic_read_ok = ((int(self.cu_flags, 16) & 2048) >> 11)
            return getattr(self, '_m_sd_pic_read_ok', None)

        @property
        def pic_ready_conv(self):
            if hasattr(self, '_m_pic_ready_conv'):
                return self._m_pic_ready_conv

            self._m_pic_ready_conv = ((int(self.cu_flags, 16) & 128) >> 7)
            return getattr(self, '_m_pic_ready_conv', None)

        @property
        def fault_1v8_r(self):
            if hasattr(self, '_m_fault_1v8_r'):
                return self._m_fault_1v8_r

            self._m_fault_1v8_r = ((int(self.cu_flags, 16) & 8) >> 3)
            return getattr(self, '_m_fault_1v8_r', None)

        @property
        def fault_1v8_m(self):
            if hasattr(self, '_m_fault_1v8_m'):
                return self._m_fault_1v8_m

            self._m_fault_1v8_m = ((int(self.cu_flags, 16) & 16) >> 4)
            return getattr(self, '_m_fault_1v8_m', None)

        @property
        def llc_sram_fault(self):
            if hasattr(self, '_m_llc_sram_fault'):
                return self._m_llc_sram_fault

            self._m_llc_sram_fault = ((int(self.cu_flags, 16) & 4) >> 2)
            return getattr(self, '_m_llc_sram_fault', None)

        @property
        def fault_3v3_12v(self):
            if hasattr(self, '_m_fault_3v3_12v'):
                return self._m_fault_3v3_12v

            self._m_fault_3v3_12v = ((int(self.cu_flags, 16) & 32) >> 5)
            return getattr(self, '_m_fault_3v3_12v', None)

        @property
        def llc_onyx_fault(self):
            if hasattr(self, '_m_llc_onyx_fault'):
                return self._m_llc_onyx_fault

            self._m_llc_onyx_fault = ((int(self.cu_flags, 16) & 2) >> 1)
            return getattr(self, '_m_llc_onyx_fault', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def sd_erase_ok(self):
            if hasattr(self, '_m_sd_erase_ok'):
                return self._m_sd_erase_ok

            self._m_sd_erase_ok = ((int(self.cu_flags, 16) & 8192) >> 13)
            return getattr(self, '_m_sd_erase_ok', None)

        @property
        def sd_get_info_ok(self):
            if hasattr(self, '_m_sd_get_info_ok'):
                return self._m_sd_get_info_ok

            self._m_sd_get_info_ok = ((int(self.cu_flags, 16) & 4096) >> 12)
            return getattr(self, '_m_sd_get_info_ok', None)

        @property
        def onyx_on(self):
            if hasattr(self, '_m_onyx_on'):
                return self._m_onyx_on

            self._m_onyx_on = (int(self.cu_flags, 16) & 1)
            return getattr(self, '_m_onyx_on', None)

        @property
        def pic_ready_raw(self):
            if hasattr(self, '_m_pic_ready_raw'):
                return self._m_pic_ready_raw

            self._m_pic_ready_raw = ((int(self.cu_flags, 16) & 64) >> 6)
            return getattr(self, '_m_pic_ready_raw', None)

        @property
        def cpu_voltage_volt(self):
            if hasattr(self, '_m_cpu_voltage_volt'):
                return self._m_cpu_voltage_volt

            self._m_cpu_voltage_volt = (int(self.cpu_voltage) / 1000.0)
            return getattr(self, '_m_cpu_voltage_volt', None)

        @property
        def sd_full(self):
            if hasattr(self, '_m_sd_full'):
                return self._m_sd_full

            self._m_sd_full = ((int(self.cu_flags, 16) & 16384) >> 14)
            return getattr(self, '_m_sd_full', None)

        @property
        def pic_ready_compressed_8(self):
            if hasattr(self, '_m_pic_ready_compressed_8'):
                return self._m_pic_ready_compressed_8

            self._m_pic_ready_compressed_8 = ((int(self.cu_flags, 16) & 512) >> 9)
            return getattr(self, '_m_pic_ready_compressed_8', None)

        @property
        def adc_ready(self):
            if hasattr(self, '_m_adc_ready'):
                return self._m_adc_ready

            self._m_adc_ready = ((int(self.cu_flags, 16) & 32768) >> 15)
            return getattr(self, '_m_adc_ready', None)

        @property
        def pic_ready_compressed(self):
            if hasattr(self, '_m_pic_ready_compressed'):
                return self._m_pic_ready_compressed

            self._m_pic_ready_compressed = ((int(self.cu_flags, 16) & 256) >> 8)
            return getattr(self, '_m_pic_ready_compressed', None)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Amicalsat.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Amicalsat.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Amicalsat.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Amicalsat.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Amicalsat.Repeater(self._io, self, self._root)

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
            self.ax25_info = Amicalsat.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class A1PositionType(KaitaiStruct):
        """A1;POSITION;[Current timestamp];[Latitude];[Longitude]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.latitude = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.longitude = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def latitude_int(self):
            if hasattr(self, '_m_latitude_int'):
                return self._m_latitude_int

            self._m_latitude_int = int(self.latitude)
            return getattr(self, '_m_latitude_int', None)

        @property
        def longitude_int(self):
            if hasattr(self, '_m_longitude_int'):
                return self._m_longitude_int

            self._m_longitude_int = int(self.longitude)
            return getattr(self, '_m_longitude_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class M1Type(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"LOG":
                self.m1 = Amicalsat.M1LogType(self._io, self, self._root)
            elif _on == u"FLAGS":
                self.m1 = Amicalsat.M1FlagsType(self._io, self, self._root)


    class CuLOnyxType(KaitaiStruct):
        """CU_L;ONYX SENSOR T;[Timestamp];[Return value]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.return_value = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def return_value_int(self):
            if hasattr(self, '_m_return_value_int'):
                return self._m_return_value_int

            self._m_return_value_int = int(self.return_value)
            return getattr(self, '_m_return_value_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class CuLType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"ONYX SENSOR T":
                self.cu_l = Amicalsat.CuLOnyxType(self._io, self, self._root)
            elif _on == u"LOG":
                self.cu_l = Amicalsat.CuLLogType(self._io, self, self._root)


    class V1MsType(KaitaiStruct):
        """V1;MS;[Timestamp];[Current rssi];[Latch rssi];[AFC offset]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.current_rssi = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.latch_rssi = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.a_f_c_offset = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def current_rssi_int(self):
            if hasattr(self, '_m_current_rssi_int'):
                return self._m_current_rssi_int

            self._m_current_rssi_int = int(self.current_rssi)
            return getattr(self, '_m_current_rssi_int', None)

        @property
        def latch_rssi_int(self):
            if hasattr(self, '_m_latch_rssi_int'):
                return self._m_latch_rssi_int

            self._m_latch_rssi_int = int(self.latch_rssi)
            return getattr(self, '_m_latch_rssi_int', None)

        @property
        def a_f_c_offset_int(self):
            if hasattr(self, '_m_a_f_c_offset_int'):
                return self._m_a_f_c_offset_int

            self._m_a_f_c_offset_int = int(self.a_f_c_offset)
            return getattr(self, '_m_a_f_c_offset_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class EmLogType(KaitaiStruct):
        """EM;LOG;[Timestamp];[Boot number];[Input voltage];[Input current];[Input power];[Peak Power];[Solar panel voltage]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.boot_number = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_current = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_power = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.peak_power = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.solar_panel_voltage = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def input_current_ma(self):
            if hasattr(self, '_m_input_current_ma'):
                return self._m_input_current_ma

            self._m_input_current_ma = int(self.input_current)
            return getattr(self, '_m_input_current_ma', None)

        @property
        def peak_power_mw(self):
            if hasattr(self, '_m_peak_power_mw'):
                return self._m_peak_power_mw

            self._m_peak_power_mw = int(self.peak_power)
            return getattr(self, '_m_peak_power_mw', None)

        @property
        def input_power_mw(self):
            if hasattr(self, '_m_input_power_mw'):
                return self._m_input_power_mw

            self._m_input_power_mw = int(self.input_power)
            return getattr(self, '_m_input_power_mw', None)

        @property
        def boot_number_int(self):
            if hasattr(self, '_m_boot_number_int'):
                return self._m_boot_number_int

            self._m_boot_number_int = int(self.boot_number)
            return getattr(self, '_m_boot_number_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def input_voltage_volt(self):
            if hasattr(self, '_m_input_voltage_volt'):
                return self._m_input_voltage_volt

            self._m_input_voltage_volt = (int(self.input_voltage) / 1000.0)
            return getattr(self, '_m_input_voltage_volt', None)

        @property
        def solar_panel_voltage_volt(self):
            if hasattr(self, '_m_solar_panel_voltage_volt'):
                return self._m_solar_panel_voltage_volt

            self._m_solar_panel_voltage_volt = (int(self.solar_panel_voltage) / 1000.0)
            return getattr(self, '_m_solar_panel_voltage_volt', None)


    class ErMnType(KaitaiStruct):
        """ER;MN;[Timestamp];[V in];[V solar];[I in];[P in];[P peak];[T cpu];[V cpu]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_solar = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.i_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.p_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.p_peak = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.t_cpu = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_cpu = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def p_peak_mw(self):
            if hasattr(self, '_m_p_peak_mw'):
                return self._m_p_peak_mw

            self._m_p_peak_mw = int(self.p_peak)
            return getattr(self, '_m_p_peak_mw', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def t_cpu_degree(self):
            if hasattr(self, '_m_t_cpu_degree'):
                return self._m_t_cpu_degree

            self._m_t_cpu_degree = int(self.t_cpu)
            return getattr(self, '_m_t_cpu_degree', None)

        @property
        def v_solar_volt(self):
            if hasattr(self, '_m_v_solar_volt'):
                return self._m_v_solar_volt

            self._m_v_solar_volt = (int(self.v_solar) / 1000.0)
            return getattr(self, '_m_v_solar_volt', None)

        @property
        def v_in_volt(self):
            if hasattr(self, '_m_v_in_volt'):
                return self._m_v_in_volt

            self._m_v_in_volt = (int(self.v_in) / 1000.0)
            return getattr(self, '_m_v_in_volt', None)

        @property
        def p_in_mw(self):
            if hasattr(self, '_m_p_in_mw'):
                return self._m_p_in_mw

            self._m_p_in_mw = int(self.p_in)
            return getattr(self, '_m_p_in_mw', None)

        @property
        def i_in_ma(self):
            if hasattr(self, '_m_i_in_ma'):
                return self._m_i_in_ma

            self._m_i_in_ma = int(self.i_in)
            return getattr(self, '_m_i_in_ma', None)

        @property
        def v_cpu_volt(self):
            if hasattr(self, '_m_v_cpu_volt'):
                return self._m_v_cpu_volt

            self._m_v_cpu_volt = (int(self.v_cpu) / 1000.0)
            return getattr(self, '_m_v_cpu_volt', None)


    class CuRType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"ONYX SENSOR T":
                self.cu_r = Amicalsat.CuROnyxType(self._io, self, self._root)
            elif _on == u"LOG":
                self.cu_r = Amicalsat.CuRLogType(self._io, self, self._root)


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
            self.ax25_info = Amicalsat.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class U2RlType(KaitaiStruct):
        """U2;RL;[Timestamp],[CPU voltage];[Battery voltage];[CPU temperature];[Amplifier temperature];[Flags]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.battery_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.amplifier_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.flagsmagic = self._io.read_bytes(2)
            if not self.flagsmagic == b"\x30\x78":
                raise kaitaistruct.ValidationNotEqualError(b"\x30\x78", self.flagsmagic, self._io, u"/types/u2_rl_type/seq/5")
            self.flags = (self._io.read_bytes(1)).decode(u"ASCII")

        @property
        def cpu_temperature_degree(self):
            if hasattr(self, '_m_cpu_temperature_degree'):
                return self._m_cpu_temperature_degree

            self._m_cpu_temperature_degree = int(self.cpu_temperature)
            return getattr(self, '_m_cpu_temperature_degree', None)

        @property
        def fec(self):
            if hasattr(self, '_m_fec'):
                return self._m_fec

            self._m_fec = (int(self.flags, 16) & 1)
            return getattr(self, '_m_fec', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def band_lock(self):
            if hasattr(self, '_m_band_lock'):
                return self._m_band_lock

            self._m_band_lock = ((int(self.flags, 16) & 4) >> 2)
            return getattr(self, '_m_band_lock', None)

        @property
        def cpu_voltage_volt(self):
            if hasattr(self, '_m_cpu_voltage_volt'):
                return self._m_cpu_voltage_volt

            self._m_cpu_voltage_volt = (int(self.cpu_voltage) / 1000.0)
            return getattr(self, '_m_cpu_voltage_volt', None)

        @property
        def aes_128(self):
            if hasattr(self, '_m_aes_128'):
                return self._m_aes_128

            self._m_aes_128 = ((int(self.flags, 16) & 16) >> 4)
            return getattr(self, '_m_aes_128', None)

        @property
        def amplifier_temperature_degree(self):
            if hasattr(self, '_m_amplifier_temperature_degree'):
                return self._m_amplifier_temperature_degree

            self._m_amplifier_temperature_degree = int(self.amplifier_temperature)
            return getattr(self, '_m_amplifier_temperature_degree', None)

        @property
        def amp_ovt(self):
            if hasattr(self, '_m_amp_ovt'):
                return self._m_amp_ovt

            self._m_amp_ovt = ((int(self.flags, 16) & 32) >> 5)
            return getattr(self, '_m_amp_ovt', None)

        @property
        def xor(self):
            if hasattr(self, '_m_xor'):
                return self._m_xor

            self._m_xor = ((int(self.flags, 16) & 8) >> 3)
            return getattr(self, '_m_xor', None)

        @property
        def downlink(self):
            if hasattr(self, '_m_downlink'):
                return self._m_downlink

            self._m_downlink = ((int(self.flags, 16) & 2) >> 1)
            return getattr(self, '_m_downlink', None)

        @property
        def battery_voltage_volt(self):
            if hasattr(self, '_m_battery_voltage_volt'):
                return self._m_battery_voltage_volt

            self._m_battery_voltage_volt = (int(self.battery_voltage) / 1000.0)
            return getattr(self, '_m_battery_voltage_volt', None)


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


    class V1RlType(KaitaiStruct):
        """V1;RL;[Timestamp],[CPU voltage];[Battery voltage];[CPU temperature];[Amplifier temperature];[Flags]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            self.cpu_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.battery_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.amplifier_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.flagsmagic = self._io.read_bytes(2)
            if not self.flagsmagic == b"\x30\x78":
                raise kaitaistruct.ValidationNotEqualError(b"\x30\x78", self.flagsmagic, self._io, u"/types/v1_rl_type/seq/5")
            self.flags = (self._io.read_bytes(1)).decode(u"ASCII")

        @property
        def cpu_temperature_degree(self):
            if hasattr(self, '_m_cpu_temperature_degree'):
                return self._m_cpu_temperature_degree

            self._m_cpu_temperature_degree = int(self.cpu_temperature)
            return getattr(self, '_m_cpu_temperature_degree', None)

        @property
        def fec(self):
            if hasattr(self, '_m_fec'):
                return self._m_fec

            self._m_fec = (int(self.flags, 16) & 1)
            return getattr(self, '_m_fec', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def band_lock(self):
            if hasattr(self, '_m_band_lock'):
                return self._m_band_lock

            self._m_band_lock = ((int(self.flags, 16) & 4) >> 2)
            return getattr(self, '_m_band_lock', None)

        @property
        def cpu_voltage_volt(self):
            if hasattr(self, '_m_cpu_voltage_volt'):
                return self._m_cpu_voltage_volt

            self._m_cpu_voltage_volt = (int(self.cpu_voltage) / 1000.0)
            return getattr(self, '_m_cpu_voltage_volt', None)

        @property
        def aes_128(self):
            if hasattr(self, '_m_aes_128'):
                return self._m_aes_128

            self._m_aes_128 = ((int(self.flags, 16) & 16) >> 4)
            return getattr(self, '_m_aes_128', None)

        @property
        def amplifier_temperature_degree(self):
            if hasattr(self, '_m_amplifier_temperature_degree'):
                return self._m_amplifier_temperature_degree

            self._m_amplifier_temperature_degree = int(self.amplifier_temperature)
            return getattr(self, '_m_amplifier_temperature_degree', None)

        @property
        def amp_ovt(self):
            if hasattr(self, '_m_amp_ovt'):
                return self._m_amp_ovt

            self._m_amp_ovt = ((int(self.flags, 16) & 32) >> 5)
            return getattr(self, '_m_amp_ovt', None)

        @property
        def xor(self):
            if hasattr(self, '_m_xor'):
                return self._m_xor

            self._m_xor = ((int(self.flags, 16) & 8) >> 3)
            return getattr(self, '_m_xor', None)

        @property
        def downlink(self):
            if hasattr(self, '_m_downlink'):
                return self._m_downlink

            self._m_downlink = ((int(self.flags, 16) & 2) >> 1)
            return getattr(self, '_m_downlink', None)

        @property
        def battery_voltage_volt(self):
            if hasattr(self, '_m_battery_voltage_volt'):
                return self._m_battery_voltage_volt

            self._m_battery_voltage_volt = (int(self.battery_voltage) / 1000.0)
            return getattr(self, '_m_battery_voltage_volt', None)


    class EmMnType(KaitaiStruct):
        """EM;MN;[Timestamp];[V in];[V solar];[I in];[P in];[P peak];[T cpu];[V cpu]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_solar = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.i_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.p_in = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.p_peak = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.t_cpu = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.v_cpu = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def p_peak_mw(self):
            if hasattr(self, '_m_p_peak_mw'):
                return self._m_p_peak_mw

            self._m_p_peak_mw = int(self.p_peak)
            return getattr(self, '_m_p_peak_mw', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def t_cpu_degree(self):
            if hasattr(self, '_m_t_cpu_degree'):
                return self._m_t_cpu_degree

            self._m_t_cpu_degree = int(self.t_cpu)
            return getattr(self, '_m_t_cpu_degree', None)

        @property
        def v_solar_volt(self):
            if hasattr(self, '_m_v_solar_volt'):
                return self._m_v_solar_volt

            self._m_v_solar_volt = (int(self.v_solar) / 1000.0)
            return getattr(self, '_m_v_solar_volt', None)

        @property
        def v_in_volt(self):
            if hasattr(self, '_m_v_in_volt'):
                return self._m_v_in_volt

            self._m_v_in_volt = (int(self.v_in) / 1000.0)
            return getattr(self, '_m_v_in_volt', None)

        @property
        def p_in_mw(self):
            if hasattr(self, '_m_p_in_mw'):
                return self._m_p_in_mw

            self._m_p_in_mw = int(self.p_in)
            return getattr(self, '_m_p_in_mw', None)

        @property
        def i_in_ma(self):
            if hasattr(self, '_m_i_in_ma'):
                return self._m_i_in_ma

            self._m_i_in_ma = int(self.i_in)
            return getattr(self, '_m_i_in_ma', None)

        @property
        def v_cpu_volt(self):
            if hasattr(self, '_m_v_cpu_volt'):
                return self._m_v_cpu_volt

            self._m_v_cpu_volt = (int(self.v_cpu) / 1000.0)
            return getattr(self, '_m_v_cpu_volt', None)


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Amicalsat.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Amicalsat.SsidMask(self._io, self, self._root)


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
                _ = Amicalsat.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class U2MsType(KaitaiStruct):
        """U2;MS;[Timestamp];[Current rssi];[Latch rssi];[AFC offset]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.current_rssi = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.latch_rssi = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.a_f_c_offset = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def current_rssi_int(self):
            if hasattr(self, '_m_current_rssi_int'):
                return self._m_current_rssi_int

            self._m_current_rssi_int = int(self.current_rssi)
            return getattr(self, '_m_current_rssi_int', None)

        @property
        def latch_rssi_int(self):
            if hasattr(self, '_m_latch_rssi_int'):
                return self._m_latch_rssi_int

            self._m_latch_rssi_int = int(self.latch_rssi)
            return getattr(self, '_m_latch_rssi_int', None)

        @property
        def a_f_c_offset_int(self):
            if hasattr(self, '_m_a_f_c_offset_int'):
                return self._m_a_f_c_offset_int

            self._m_a_f_c_offset_int = int(self.a_f_c_offset)
            return getattr(self, '_m_a_f_c_offset_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class CuLLogType(KaitaiStruct):
        """CU_L;LOG;[Timestamp];[CPU voltage];[CPU temperature];[flags]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_temperature = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.flagsmagic = self._io.read_bytes(2)
            if not self.flagsmagic == b"\x30\x78":
                raise kaitaistruct.ValidationNotEqualError(b"\x30\x78", self.flagsmagic, self._io, u"/types/cu_l_log_type/seq/3")
            self.cu_flags = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def cpu_temperature_degree(self):
            if hasattr(self, '_m_cpu_temperature_degree'):
                return self._m_cpu_temperature_degree

            self._m_cpu_temperature_degree = int(self.cpu_temperature)
            return getattr(self, '_m_cpu_temperature_degree', None)

        @property
        def sd_pic_write_ok(self):
            if hasattr(self, '_m_sd_pic_write_ok'):
                return self._m_sd_pic_write_ok

            self._m_sd_pic_write_ok = ((int(self.cu_flags, 16) & 1024) >> 10)
            return getattr(self, '_m_sd_pic_write_ok', None)

        @property
        def sd_pic_read_ok(self):
            if hasattr(self, '_m_sd_pic_read_ok'):
                return self._m_sd_pic_read_ok

            self._m_sd_pic_read_ok = ((int(self.cu_flags, 16) & 2048) >> 11)
            return getattr(self, '_m_sd_pic_read_ok', None)

        @property
        def pic_ready_conv(self):
            if hasattr(self, '_m_pic_ready_conv'):
                return self._m_pic_ready_conv

            self._m_pic_ready_conv = ((int(self.cu_flags, 16) & 128) >> 7)
            return getattr(self, '_m_pic_ready_conv', None)

        @property
        def fault_1v8_r(self):
            if hasattr(self, '_m_fault_1v8_r'):
                return self._m_fault_1v8_r

            self._m_fault_1v8_r = ((int(self.cu_flags, 16) & 8) >> 3)
            return getattr(self, '_m_fault_1v8_r', None)

        @property
        def fault_1v8_m(self):
            if hasattr(self, '_m_fault_1v8_m'):
                return self._m_fault_1v8_m

            self._m_fault_1v8_m = ((int(self.cu_flags, 16) & 16) >> 4)
            return getattr(self, '_m_fault_1v8_m', None)

        @property
        def llc_sram_fault(self):
            if hasattr(self, '_m_llc_sram_fault'):
                return self._m_llc_sram_fault

            self._m_llc_sram_fault = ((int(self.cu_flags, 16) & 4) >> 2)
            return getattr(self, '_m_llc_sram_fault', None)

        @property
        def fault_3v3_12v(self):
            if hasattr(self, '_m_fault_3v3_12v'):
                return self._m_fault_3v3_12v

            self._m_fault_3v3_12v = ((int(self.cu_flags, 16) & 32) >> 5)
            return getattr(self, '_m_fault_3v3_12v', None)

        @property
        def llc_onyx_fault(self):
            if hasattr(self, '_m_llc_onyx_fault'):
                return self._m_llc_onyx_fault

            self._m_llc_onyx_fault = ((int(self.cu_flags, 16) & 2) >> 1)
            return getattr(self, '_m_llc_onyx_fault', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def sd_erase_ok(self):
            if hasattr(self, '_m_sd_erase_ok'):
                return self._m_sd_erase_ok

            self._m_sd_erase_ok = ((int(self.cu_flags, 16) & 8192) >> 13)
            return getattr(self, '_m_sd_erase_ok', None)

        @property
        def sd_get_info_ok(self):
            if hasattr(self, '_m_sd_get_info_ok'):
                return self._m_sd_get_info_ok

            self._m_sd_get_info_ok = ((int(self.cu_flags, 16) & 4096) >> 12)
            return getattr(self, '_m_sd_get_info_ok', None)

        @property
        def onyx_on(self):
            if hasattr(self, '_m_onyx_on'):
                return self._m_onyx_on

            self._m_onyx_on = (int(self.cu_flags, 16) & 1)
            return getattr(self, '_m_onyx_on', None)

        @property
        def pic_ready_raw(self):
            if hasattr(self, '_m_pic_ready_raw'):
                return self._m_pic_ready_raw

            self._m_pic_ready_raw = ((int(self.cu_flags, 16) & 64) >> 6)
            return getattr(self, '_m_pic_ready_raw', None)

        @property
        def cpu_voltage_volt(self):
            if hasattr(self, '_m_cpu_voltage_volt'):
                return self._m_cpu_voltage_volt

            self._m_cpu_voltage_volt = (int(self.cpu_voltage) / 1000.0)
            return getattr(self, '_m_cpu_voltage_volt', None)

        @property
        def sd_full(self):
            if hasattr(self, '_m_sd_full'):
                return self._m_sd_full

            self._m_sd_full = ((int(self.cu_flags, 16) & 16384) >> 14)
            return getattr(self, '_m_sd_full', None)

        @property
        def pic_ready_compressed_8(self):
            if hasattr(self, '_m_pic_ready_compressed_8'):
                return self._m_pic_ready_compressed_8

            self._m_pic_ready_compressed_8 = ((int(self.cu_flags, 16) & 512) >> 9)
            return getattr(self, '_m_pic_ready_compressed_8', None)

        @property
        def adc_ready(self):
            if hasattr(self, '_m_adc_ready'):
                return self._m_adc_ready

            self._m_adc_ready = ((int(self.cu_flags, 16) & 32768) >> 15)
            return getattr(self, '_m_adc_ready', None)

        @property
        def pic_ready_compressed(self):
            if hasattr(self, '_m_pic_ready_compressed'):
                return self._m_pic_ready_compressed

            self._m_pic_ready_compressed = ((int(self.cu_flags, 16) & 256) >> 8)
            return getattr(self, '_m_pic_ready_compressed', None)


    class A1GyroType(KaitaiStruct):
        """A1;GYRO;[Current timestamp];[GyroX];[GyroY];[GyroZ]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.giro_x = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.giro_y = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.giro_z = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")

        @property
        def gyro_x_int(self):
            if hasattr(self, '_m_gyro_x_int'):
                return self._m_gyro_x_int

            self._m_gyro_x_int = int(self.giro_x)
            return getattr(self, '_m_gyro_x_int', None)

        @property
        def gyro_y_int(self):
            if hasattr(self, '_m_gyro_y_int'):
                return self._m_gyro_y_int

            self._m_gyro_y_int = int(self.giro_y)
            return getattr(self, '_m_gyro_y_int', None)

        @property
        def gyro_z_int(self):
            if hasattr(self, '_m_gyro_z_int'):
                return self._m_gyro_z_int

            self._m_gyro_z_int = int(self.giro_z)
            return getattr(self, '_m_gyro_z_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class A1MagType(KaitaiStruct):
        """A1;MAG;[Current timestamp];[MagX];[MagY];[MagZ]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.mag_x = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.mag_y = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.mag_z = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")

        @property
        def mag_x_int(self):
            if hasattr(self, '_m_mag_x_int'):
                return self._m_mag_x_int

            self._m_mag_x_int = int(self.mag_x)
            return getattr(self, '_m_mag_x_int', None)

        @property
        def mag_y_int(self):
            if hasattr(self, '_m_mag_y_int'):
                return self._m_mag_y_int

            self._m_mag_y_int = int(self.mag_y)
            return getattr(self, '_m_mag_y_int', None)

        @property
        def mag_z_int(self):
            if hasattr(self, '_m_mag_z_int'):
                return self._m_mag_z_int

            self._m_mag_z_int = int(self.mag_z)
            return getattr(self, '_m_mag_z_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)


    class EmType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"LOG":
                self.em = Amicalsat.EmLogType(self._io, self, self._root)
            elif _on == u"MN":
                self.em = Amicalsat.EmMnType(self._io, self, self._root)


    class A1Type(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"FLAGS":
                self.a1 = Amicalsat.A1FlagsType(self._io, self, self._root)
            elif _on == u"MAG":
                self.a1 = Amicalsat.A1MagType(self._io, self, self._root)
            elif _on == u"GYRO":
                self.a1 = Amicalsat.A1GyroType(self._io, self, self._root)
            elif _on == u"POSITION":
                self.a1 = Amicalsat.A1PositionType(self._io, self, self._root)


    class A1FlagsType(KaitaiStruct):
        """A1;FLAGS;[timestamp];[mode];[flags];[faults]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.adcs_mode = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.a1_flags = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.faults = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def sens_on_off(self):
            if hasattr(self, '_m_sens_on_off'):
                return self._m_sens_on_off

            self._m_sens_on_off = ((int(self.a1_flags, 16) & 4) >> 2)
            return getattr(self, '_m_sens_on_off', None)

        @property
        def l3_fault(self):
            if hasattr(self, '_m_l3_fault'):
                return self._m_l3_fault

            self._m_l3_fault = ((int(self.faults, 16) & 32) >> 5)
            return getattr(self, '_m_l3_fault', None)

        @property
        def manual(self):
            if hasattr(self, '_m_manual'):
                return self._m_manual

            self._m_manual = ((int(self.adcs_mode, 16) & 240) >> 4)
            return getattr(self, '_m_manual', None)

        @property
        def sun_contr(self):
            if hasattr(self, '_m_sun_contr'):
                return self._m_sun_contr

            self._m_sun_contr = ((int(self.a1_flags, 16) & 2) >> 1)
            return getattr(self, '_m_sun_contr', None)

        @property
        def gyro_acc_fault(self):
            if hasattr(self, '_m_gyro_acc_fault'):
                return self._m_gyro_acc_fault

            self._m_gyro_acc_fault = (int(self.faults, 16) & 1)
            return getattr(self, '_m_gyro_acc_fault', None)

        @property
        def l1_fault(self):
            if hasattr(self, '_m_l1_fault'):
                return self._m_l1_fault

            self._m_l1_fault = ((int(self.faults, 16) & 8) >> 3)
            return getattr(self, '_m_l1_fault', None)

        @property
        def act_man_contr(self):
            if hasattr(self, '_m_act_man_contr'):
                return self._m_act_man_contr

            self._m_act_man_contr = ((int(self.a1_flags, 16) & 8) >> 3)
            return getattr(self, '_m_act_man_contr', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def adcs_on_off(self):
            if hasattr(self, '_m_adcs_on_off'):
                return self._m_adcs_on_off

            self._m_adcs_on_off = ((int(self.adcs_mode, 16) & 2) >> 1)
            return getattr(self, '_m_adcs_on_off', None)

        @property
        def detumbling_status(self):
            if hasattr(self, '_m_detumbling_status'):
                return self._m_detumbling_status

            self._m_detumbling_status = ((int(self.adcs_mode, 16) & 12) >> 2)
            return getattr(self, '_m_detumbling_status', None)

        @property
        def act_limited_contr(self):
            if hasattr(self, '_m_act_limited_contr'):
                return self._m_act_limited_contr

            self._m_act_limited_contr = ((int(self.a1_flags, 16) & 16) >> 4)
            return getattr(self, '_m_act_limited_contr', None)

        @property
        def act_on_off(self):
            if hasattr(self, '_m_act_on_off'):
                return self._m_act_on_off

            self._m_act_on_off = (int(self.a1_flags, 16) & 1)
            return getattr(self, '_m_act_on_off', None)

        @property
        def mag_fault(self):
            if hasattr(self, '_m_mag_fault'):
                return self._m_mag_fault

            self._m_mag_fault = ((int(self.faults, 16) & 2) >> 1)
            return getattr(self, '_m_mag_fault', None)

        @property
        def sun_fault(self):
            if hasattr(self, '_m_sun_fault'):
                return self._m_sun_fault

            self._m_sun_fault = ((int(self.faults, 16) & 4) >> 2)
            return getattr(self, '_m_sun_fault', None)

        @property
        def l2_fault(self):
            if hasattr(self, '_m_l2_fault'):
                return self._m_l2_fault

            self._m_l2_fault = ((int(self.faults, 16) & 16) >> 4)
            return getattr(self, '_m_l2_fault', None)

        @property
        def detumbling(self):
            if hasattr(self, '_m_detumbling'):
                return self._m_detumbling

            self._m_detumbling = (int(self.adcs_mode, 16) & 1)
            return getattr(self, '_m_detumbling', None)


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
            self.callsign_ror = Amicalsat.Callsign(_io__raw_callsign_ror, self, self._root)


    class M1LogType(KaitaiStruct):
        """M1;LOG;[Timestamp];[Boot number];[Up time];[CPU voltage];[CPU temperature]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.boot_number = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.up_time = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.cpu_temperature = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def cpu_temperature_degree(self):
            if hasattr(self, '_m_cpu_temperature_degree'):
                return self._m_cpu_temperature_degree

            self._m_cpu_temperature_degree = int(self.cpu_temperature)
            return getattr(self, '_m_cpu_temperature_degree', None)

        @property
        def up_time_int(self):
            if hasattr(self, '_m_up_time_int'):
                return self._m_up_time_int

            self._m_up_time_int = int(self.up_time)
            return getattr(self, '_m_up_time_int', None)

        @property
        def boot_number_int(self):
            if hasattr(self, '_m_boot_number_int'):
                return self._m_boot_number_int

            self._m_boot_number_int = int(self.boot_number)
            return getattr(self, '_m_boot_number_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def cpu_voltage_volt(self):
            if hasattr(self, '_m_cpu_voltage_volt'):
                return self._m_cpu_voltage_volt

            self._m_cpu_voltage_volt = (int(self.cpu_voltage) / 1000.0)
            return getattr(self, '_m_cpu_voltage_volt', None)


    class ErType(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"LOG":
                self.er = Amicalsat.ErLogType(self._io, self, self._root)
            elif _on == u"MN":
                self.er = Amicalsat.ErMnType(self._io, self, self._root)


    class ErLogType(KaitaiStruct):
        """ER;LOG;[Timestamp];[Boot number];[Input voltage];[Input current];[Input power];[Peak Power];[Solar panel voltage]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.boot_number = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_voltage = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_current = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.input_power = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.peak_power = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.solar_panel_voltage = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def input_current_ma(self):
            if hasattr(self, '_m_input_current_ma'):
                return self._m_input_current_ma

            self._m_input_current_ma = int(self.input_current)
            return getattr(self, '_m_input_current_ma', None)

        @property
        def peak_power_mw(self):
            if hasattr(self, '_m_peak_power_mw'):
                return self._m_peak_power_mw

            self._m_peak_power_mw = int(self.peak_power)
            return getattr(self, '_m_peak_power_mw', None)

        @property
        def input_power_mw(self):
            if hasattr(self, '_m_input_power_mw'):
                return self._m_input_power_mw

            self._m_input_power_mw = int(self.input_power)
            return getattr(self, '_m_input_power_mw', None)

        @property
        def boot_number_int(self):
            if hasattr(self, '_m_boot_number_int'):
                return self._m_boot_number_int

            self._m_boot_number_int = int(self.boot_number)
            return getattr(self, '_m_boot_number_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def input_voltage_volt(self):
            if hasattr(self, '_m_input_voltage_volt'):
                return self._m_input_voltage_volt

            self._m_input_voltage_volt = (int(self.input_voltage) / 1000.0)
            return getattr(self, '_m_input_voltage_volt', None)

        @property
        def solar_panel_voltage_volt(self):
            if hasattr(self, '_m_solar_panel_voltage_volt'):
                return self._m_solar_panel_voltage_volt

            self._m_solar_panel_voltage_volt = (int(self.solar_panel_voltage) / 1000.0)
            return getattr(self, '_m_solar_panel_voltage_volt', None)


    class M1FlagsType(KaitaiStruct):
        """M1;FLAGS;[Timestamp];[Hex flags];
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.hex_part = (self._io.read_bytes_term(120, False, True, True)).decode(u"ASCII")
            self.flags = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = ((int(self.flags, 16) & 256) >> 8)
            return getattr(self, '_m_beacon_mode', None)

        @property
        def cur_dead(self):
            if hasattr(self, '_m_cur_dead'):
                return self._m_cur_dead

            self._m_cur_dead = ((int(self.flags, 16) & 4026531840) >> 28)
            return getattr(self, '_m_cur_dead', None)

        @property
        def cur_on(self):
            if hasattr(self, '_m_cur_on'):
                return self._m_cur_on

            self._m_cur_on = ((int(self.flags, 16) & 262144) >> 18)
            return getattr(self, '_m_cur_on', None)

        @property
        def stream(self):
            if hasattr(self, '_m_stream'):
                return self._m_stream

            self._m_stream = ((int(self.flags, 16) & 281474976710656) >> 48)
            return getattr(self, '_m_stream', None)

        @property
        def imc_aocs_ok(self):
            if hasattr(self, '_m_imc_aocs_ok'):
                return self._m_imc_aocs_ok

            self._m_imc_aocs_ok = (int(self.flags, 16) & 1)
            return getattr(self, '_m_imc_aocs_ok', None)

        @property
        def uhf2_downlink(self):
            if hasattr(self, '_m_uhf2_downlink'):
                return self._m_uhf2_downlink

            self._m_uhf2_downlink = ((int(self.flags, 16) & 64) >> 6)
            return getattr(self, '_m_uhf2_downlink', None)

        @property
        def cul_on(self):
            if hasattr(self, '_m_cul_on'):
                return self._m_cul_on

            self._m_cul_on = ((int(self.flags, 16) & 65536) >> 16)
            return getattr(self, '_m_cul_on', None)

        @property
        def payload_off(self):
            if hasattr(self, '_m_payload_off'):
                return self._m_payload_off

            self._m_payload_off = ((int(self.flags, 16) & 2048) >> 11)
            return getattr(self, '_m_payload_off', None)

        @property
        def cu_auto_off(self):
            if hasattr(self, '_m_cu_auto_off'):
                return self._m_cu_auto_off

            self._m_cu_auto_off = ((int(self.flags, 16) & 4096) >> 12)
            return getattr(self, '_m_cu_auto_off', None)

        @property
        def survival_start(self):
            if hasattr(self, '_m_survival_start'):
                return self._m_survival_start

            self._m_survival_start = ((int(self.flags, 16) & 2251799813685248) >> 51)
            return getattr(self, '_m_survival_start', None)

        @property
        def fault_3v_m(self):
            if hasattr(self, '_m_fault_3v_m'):
                return self._m_fault_3v_m

            self._m_fault_3v_m = ((int(self.flags, 16) & 2199023255552) >> 41)
            return getattr(self, '_m_fault_3v_m', None)

        @property
        def plan(self):
            if hasattr(self, '_m_plan'):
                return self._m_plan

            self._m_plan = ((int(self.flags, 16) & 140737488355328) >> 47)
            return getattr(self, '_m_plan', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)

        @property
        def vhf1_downlink(self):
            if hasattr(self, '_m_vhf1_downlink'):
                return self._m_vhf1_downlink

            self._m_vhf1_downlink = ((int(self.flags, 16) & 32) >> 5)
            return getattr(self, '_m_vhf1_downlink', None)

        @property
        def cyclic_reset_on(self):
            if hasattr(self, '_m_cyclic_reset_on'):
                return self._m_cyclic_reset_on

            self._m_cyclic_reset_on = ((int(self.flags, 16) & 512) >> 9)
            return getattr(self, '_m_cyclic_reset_on', None)

        @property
        def uhf2_packet_ready(self):
            if hasattr(self, '_m_uhf2_packet_ready'):
                return self._m_uhf2_packet_ready

            self._m_uhf2_packet_ready = ((int(self.flags, 16) & 1125899906842624) >> 50)
            return getattr(self, '_m_uhf2_packet_ready', None)

        @property
        def cur_fault(self):
            if hasattr(self, '_m_cur_fault'):
                return self._m_cur_fault

            self._m_cur_fault = ((int(self.flags, 16) & 524288) >> 19)
            return getattr(self, '_m_cur_fault', None)

        @property
        def vhf1_packet_ready(self):
            if hasattr(self, '_m_vhf1_packet_ready'):
                return self._m_vhf1_packet_ready

            self._m_vhf1_packet_ready = ((int(self.flags, 16) & 562949953421312) >> 49)
            return getattr(self, '_m_vhf1_packet_ready', None)

        @property
        def cul_faut(self):
            if hasattr(self, '_m_cul_faut'):
                return self._m_cul_faut

            self._m_cul_faut = ((int(self.flags, 16) & 131072) >> 17)
            return getattr(self, '_m_cul_faut', None)

        @property
        def tm_log(self):
            if hasattr(self, '_m_tm_log'):
                return self._m_tm_log

            self._m_tm_log = ((int(self.flags, 16) & 8192) >> 13)
            return getattr(self, '_m_tm_log', None)

        @property
        def long_log(self):
            if hasattr(self, '_m_long_log'):
                return self._m_long_log

            self._m_long_log = ((int(self.flags, 16) & 35184372088832) >> 45)
            return getattr(self, '_m_long_log', None)

        @property
        def imc_uhf2_ok(self):
            if hasattr(self, '_m_imc_uhf2_ok'):
                return self._m_imc_uhf2_ok

            self._m_imc_uhf2_ok = ((int(self.flags, 16) & 16) >> 4)
            return getattr(self, '_m_imc_uhf2_ok', None)

        @property
        def imc_check(self):
            if hasattr(self, '_m_imc_check'):
                return self._m_imc_check

            self._m_imc_check = ((int(self.flags, 16) & 128) >> 7)
            return getattr(self, '_m_imc_check', None)

        @property
        def charge_m(self):
            if hasattr(self, '_m_charge_m'):
                return self._m_charge_m

            self._m_charge_m = ((int(self.flags, 16) & 8796093022208) >> 43)
            return getattr(self, '_m_charge_m', None)

        @property
        def survival_end(self):
            if hasattr(self, '_m_survival_end'):
                return self._m_survival_end

            self._m_survival_end = ((int(self.flags, 16) & 4503599627370496) >> 52)
            return getattr(self, '_m_survival_end', None)

        @property
        def fault_3v_r(self):
            if hasattr(self, '_m_fault_3v_r'):
                return self._m_fault_3v_r

            self._m_fault_3v_r = ((int(self.flags, 16) & 1099511627776) >> 40)
            return getattr(self, '_m_fault_3v_r', None)

        @property
        def survival_mode(self):
            if hasattr(self, '_m_survival_mode'):
                return self._m_survival_mode

            self._m_survival_mode = ((int(self.flags, 16) & 1024) >> 10)
            return getattr(self, '_m_survival_mode', None)

        @property
        def imc_cu_r_ok(self):
            if hasattr(self, '_m_imc_cu_r_ok'):
                return self._m_imc_cu_r_ok

            self._m_imc_cu_r_ok = ((int(self.flags, 16) & 4) >> 2)
            return getattr(self, '_m_imc_cu_r_ok', None)

        @property
        def cul_dead(self):
            if hasattr(self, '_m_cul_dead'):
                return self._m_cul_dead

            self._m_cul_dead = ((int(self.flags, 16) & 251658240) >> 24)
            return getattr(self, '_m_cul_dead', None)

        @property
        def charge_r(self):
            if hasattr(self, '_m_charge_r'):
                return self._m_charge_r

            self._m_charge_r = ((int(self.flags, 16) & 4398046511104) >> 42)
            return getattr(self, '_m_charge_r', None)

        @property
        def imc_vhf1_ok(self):
            if hasattr(self, '_m_imc_vhf1_ok'):
                return self._m_imc_vhf1_ok

            self._m_imc_vhf1_ok = ((int(self.flags, 16) & 8) >> 3)
            return getattr(self, '_m_imc_vhf1_ok', None)

        @property
        def cu_on(self):
            if hasattr(self, '_m_cu_on'):
                return self._m_cu_on

            self._m_cu_on = ((int(self.flags, 16) & 1048576) >> 20)
            return getattr(self, '_m_cu_on', None)

        @property
        def log_to_flash(self):
            if hasattr(self, '_m_log_to_flash'):
                return self._m_log_to_flash

            self._m_log_to_flash = ((int(self.flags, 16) & 70368744177664) >> 46)
            return getattr(self, '_m_log_to_flash', None)

        @property
        def imc_cu_l_ok(self):
            if hasattr(self, '_m_imc_cu_l_ok'):
                return self._m_imc_cu_l_ok

            self._m_imc_cu_l_ok = ((int(self.flags, 16) & 2) >> 1)
            return getattr(self, '_m_imc_cu_l_ok', None)


    class V1Type(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"RL":
                self.v1 = Amicalsat.V1RlType(self._io, self, self._root)
            elif _on == u"MS":
                self.v1 = Amicalsat.V1MsType(self._io, self, self._root)


    class U2Type(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_type = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_type
            if _on == u"RL":
                self.u2 = Amicalsat.U2RlType(self._io, self, self._root)
            elif _on == u"MS":
                self.u2 = Amicalsat.U2MsType(self._io, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start = self._io.read_u1()
            self.tlm_area = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            _on = self.tlm_area
            if _on == u"EM":
                self.tlm_area_switch = Amicalsat.EmType(self._io, self, self._root)
            elif _on == u"M1":
                self.tlm_area_switch = Amicalsat.M1Type(self._io, self, self._root)
            elif _on == u"V1":
                self.tlm_area_switch = Amicalsat.V1Type(self._io, self, self._root)
            elif _on == u"U2":
                self.tlm_area_switch = Amicalsat.U2Type(self._io, self, self._root)
            elif _on == u"A1":
                self.tlm_area_switch = Amicalsat.A1Type(self._io, self, self._root)
            elif _on == u"CU_L":
                self.tlm_area_switch = Amicalsat.CuLType(self._io, self, self._root)
            elif _on == u"CU_R":
                self.tlm_area_switch = Amicalsat.CuRType(self._io, self, self._root)
            elif _on == u"ER":
                self.tlm_area_switch = Amicalsat.ErType(self._io, self, self._root)

        @property
        def aprs_message(self):
            if hasattr(self, '_m_aprs_message'):
                return self._m_aprs_message

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_aprs_message = (self._io.read_bytes_full()).decode(u"utf-8")
            self._io.seek(_pos)
            return getattr(self, '_m_aprs_message', None)


    class CuROnyxType(KaitaiStruct):
        """CU_R;ONYX SENSOR T;[Timestamp];[Return value]
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = (self._io.read_bytes_term(59, False, True, True)).decode(u"ASCII")
            self.return_value = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def return_value_int(self):
            if hasattr(self, '_m_return_value_int'):
                return self._m_return_value_int

            self._m_return_value_int = int(self.return_value)
            return getattr(self, '_m_return_value_int', None)

        @property
        def timestamp_int(self):
            if hasattr(self, '_m_timestamp_int'):
                return self._m_timestamp_int

            self._m_timestamp_int = int(self.timestamp)
            return getattr(self, '_m_timestamp_int', None)



