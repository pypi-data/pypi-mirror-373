# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Estcube2(KaitaiStruct):
    """:field timestamp: icp_data.eps.common.unix_time
    :field eps_uptime: icp_data.eps.common.uptime
    :field eps_cpu_temperature: icp_data.eps.common.cpu_temperature
    :field eps_bus_voltage: icp_data.eps.bus_voltage
    :field eps_avg_power_balance: icp_data.eps.avg_power_balance
    :field eps_enable_st: icp_data.eps.enable_st
    :field eps_enable_obc: icp_data.eps.enable_obc
    :field eps_enable_com3v3: icp_data.eps.enable_com_3v3
    :field eps_enable_comdcdc: icp_data.eps.enable_com_dcdc
    :field eps_enable_com_pa: icp_data.eps.enable_com_pa
    :field eps_enable_eps_dcdc1: icp_data.eps.enable_eps_dcdc1
    :field eps_enable_eps_dcdc2: icp_data.eps.enable_eps_dcdc2
    :field eps_enable_sp: icp_data.eps.enable_sp
    :field eps_enable_cgp: icp_data.eps.enable_cgp
    :field eps_enable_hscom: icp_data.eps.enable_hscom
    :field eps_enable_eop1: icp_data.eps.enable_eop1
    :field eps_enable_eop2: icp_data.eps.enable_eop2
    :field eps_enable_esail: icp_data.eps.enable_esail
    :field eps_enable_rw: icp_data.eps.enable_obc_rw
    
    :field eps_battery_current_a: icp_data.eps.battery_current_a
    :field eps_battery_current_b: icp_data.eps.battery_current_b
    :field eps_battery_voltage_a: icp_data.eps.battery_voltage_a
    :field eps_battery_voltage_b: icp_data.eps.battery_voltage_b
    :field eps_battery_voltage_c: icp_data.eps.battery_voltage_c
    :field eps_battery_voltage_d: icp_data.eps.battery_voltage_d
    :field eps_battery_temperature_a: icp_data.eps.battery_temperature_a
    :field eps_battery_temperature_b: icp_data.eps.battery_temperature_b
    :field eps_battery_temperature_c: icp_data.eps.battery_temperature_c
    :field eps_battery_temperature_d: icp_data.eps.battery_temperature_d
    
    :field eps_st_voltage: icp_data.eps.st_voltage
    :field eps_st_current: icp_data.eps.st_current
    :field eps_obc_voltage: icp_data.eps.obc_voltage
    :field eps_obc_current: icp_data.eps.obc_current
    :field eps_com_3v3_voltage: icp_data.eps.com_3v3_voltage
    :field eps_com_pa_voltage: icp_data.eps.com_pa_voltage
    :field eps_com_3v3_current: icp_data.eps.com_3v3_current
    :field eps_com_pa_current: icp_data.eps.com_pa_current
    :field eps_eps_voltage: icp_data.eps.eps_voltage
    :field eps_eps_dcdc_3v3_voltage: icp_data.eps.eps_dcdc_3v3_voltage
    :field eps_eps_current: icp_data.eps.eps_current
    :field eps_eps_dcdc1_current: icp_data.eps.eps_dcdc1_current
    :field eps_eps_dcdc2_current: icp_data.eps.eps_dcdc2_current
    :field eps_sp_voltage: icp_data.eps.sp_voltage
    :field eps_sp_current: icp_data.eps.sp_current
    :field eps_cpd_voltage: icp_data.eps.cpd_voltage
    :field eps_cpd_current: icp_data.eps.cpd_current
    :field eps_cam1_voltage: icp_data.eps.cam1_voltage
    :field eps_cam1_current: icp_data.eps.cam1_current
    :field eps_cam2_voltage: icp_data.eps.cam2_voltage
    :field eps_cam2_current: icp_data.eps.cam2_current
    :field eps_hsom_voltage: icp_data.eps.hsom_voltage
    :field eps_hsom_current: icp_data.eps.hsom_current
    :field eps_cgp_5v_voltage: icp_data.eps.cgp_5v_voltage
    :field eps_cgp_mpb_voltage: icp_data.eps.cgp_mpb_voltage
    :field eps_cgp_current: icp_data.eps.cgp_current
    
    :field timestamp: icp_data.obc.common.unix_time
    :field obc_uptime: icp_data.obc.common.uptime
    :field obc_cpu_temperature: icp_data.obc.common.cpu_temperature
    :field obc_fmc_mram_temperature: icp_data.obc.fmc_mram_temperature
    :field obc_qspi_fram_temperature: icp_data.obc.qspi_fram_temperature
    :field obc_io_expander_temperature: icp_data.obc.io_expander_temperature
    
    :field aocs_gyroscope_x: icp_data.aocs.bmg160_gyroscope_x
    :field aocs_gyroscope_y: icp_data.aocs.bmg160_gyroscope_y
    :field aocs_gyroscope_z: icp_data.aocs.bmg160_gyroscope_z
    :field aocs_magnetometer_x: icp_data.aocs.lis3mdl_magnetometer_x
    :field aocs_magnetometer_y: icp_data.aocs.lis3mdl_magnetometer_y
    :field aocs_magnetometer_z: icp_data.aocs.lis3mdl_magnetometer_z
    :field aocs_sun_x_intensity1: icp_data.aocs.sun_x_intensity1
    :field aocs_sun_x_intensity2: icp_data.aocs.sun_x_intensity2
    :field aocs_sun_x_intensity3: icp_data.aocs.sun_x_intensity3
    :field aocs_sun_x_intensity4: icp_data.aocs.sun_x_intensity4
    :field aocs_sun_x_intensity5: icp_data.aocs.sun_x_intensity5
    :field aocs_sun_x_intensity6: icp_data.aocs.sun_x_intensity6
    :field aocs_sun_x_intensity_location1: icp_data.aocs.sun_x_intensity_location1
    :field aocs_sun_x_intensity_location2: icp_data.aocs.sun_x_intensity_location2
    :field aocs_sun_x_intensity_location3: icp_data.aocs.sun_x_intensity_location3
    :field aocs_sun_x_intensity_location4: icp_data.aocs.sun_x_intensity_location4
    :field aocs_sun_x_intensity_location5: icp_data.aocs.sun_x_intensity_location5
    :field aocs_sun_x_intensity_location6: icp_data.aocs.sun_x_intensity_location6
    :field aocs_sun_y_intensity1: icp_data.aocs.sun_y_intensity1
    :field aocs_sun_y_intensity2: icp_data.aocs.sun_y_intensity2
    :field aocs_sun_y_intensity3: icp_data.aocs.sun_y_intensity3
    :field aocs_sun_y_intensity4: icp_data.aocs.sun_y_intensity4
    :field aocs_sun_y_intensity5: icp_data.aocs.sun_y_intensity5
    :field aocs_sun_y_intensity6: icp_data.aocs.sun_y_intensity6
    :field aocs_sun_y_intensity_location1: icp_data.aocs.sun_y_intensity_location1
    :field aocs_sun_y_intensity_location2: icp_data.aocs.sun_y_intensity_location2
    :field aocs_sun_y_intensity_location3: icp_data.aocs.sun_y_intensity_location3
    :field aocs_sun_y_intensity_location4: icp_data.aocs.sun_y_intensity_location4
    :field aocs_sun_y_intensity_location5: icp_data.aocs.sun_y_intensity_location5
    :field aocs_sun_y_intensity_location6: icp_data.aocs.sun_y_intensity_location6
    :field aocs_temperature1: icp_data.aocs.mcp9808_temperature1
    :field aocs_temperature2: icp_data.aocs.mcp9808_temperature2
    :field aocs_mode_pointing: icp_data.aocs.pointing
    :field aocs_mode_detumbling: icp_data.aocs.detumbling
    :field aocs_mode_spin_up: icp_data.aocs.spin_up
    :field aocs_mode_diagnostics: icp_data.aocs.diagnostics
    :field aocs_mode_custom: icp_data.aocs.custom
    :field aocs_mode_low_precision: icp_data.aocs.low_precision
    :field aocs_mode_high_precision: icp_data.aocs.high_precision
    :field aocs_reaction_wheel1: icp_data.aocs.reaction_wheel1_rpm
    :field aocs_reaction_wheel2: icp_data.aocs.reaction_wheel2_rpm
    :field aocs_reaction_wheel3: icp_data.aocs.reaction_wheel3_rpm
    
    :field timestamp: icp_data.pcom.common.unix_time
    :field com_uptime: icp_data.pcom.common.uptime
    :field com_cpu_temperature: icp_data.pcom.common.cpu_temperature
    
    :field pcom_rssi: icp_data.pcom.rssi
    :field pcom_last_packet_time: icp_data.pcom.last_packet_time
    :field pcom_dropped_packets: icp_data.pcom.dropped_packets
    :field pcom_gs_packets: icp_data.pcom.gs_packets
    :field pcom_sent_packets: icp_data.pcom.sent_packets
    :field pcom_power_amplifier_temperature: icp_data.pcom.power_amplifier_temperature
    :field pcom_forward_rf_power: icp_data.pcom.forward_rf_power
    :field pcom_reflected_rf_power: icp_data.pcom.reflected_rf_power
    
    :field timestamp: icp_data.scom.common.unix_time
    :field scom_rssi: icp_data.scom.rssi
    :field scom_last_packet_time: icp_data.scom.last_packet_time
    :field scom_dropped_packets: icp_data.scom.dropped_packets
    :field scom_gs_packets: icp_data.scom.gs_packets
    :field scom_sent_packets: icp_data.scom.sent_packets
    :field scom_digipeated_packets: icp_data.scom.digipeated_packets
    :field scom_power_amplifier_temperature: icp_data.scom.power_amplifier_temperature
    :field scom_forward_rf_power: icp_data.scom.forward_rf_power
    :field scom_reflected_rf_power: icp_data.scom.reflected_rf_power
    
    :field timestamp: icp_data.sp_xplus.common.unix_time
    :field sp_xplus_uptime: icp_data.sp_xplus.common.uptime
    :field sp_xplus_cpu_temperature: icp_data.sp_xplus.common.cpu_temperature
    :field sp_xplus_temperature: icp_data.sp_xplus.temperature
    
    :field timestamp: icp_data.sp_xminus.common.unix_time
    :field sp_xminus_uptime: icp_data.sp_xminus.common.uptime
    :field sp_xminus_cpu_temperature: icp_data.sp_xminus.common.cpu_temperature
    :field sp_xminus_temperature: icp_data.sp_xminus.temperature
    :field sp_xminus_mppt_current: icp_data.sp_xminus.mppt_current
    :field sp_xminus_coil_current: icp_data.sp_xminus.coil_current
    
    :field timestamp: icp_data.sp_yplus.common.unix_time
    :field sp_yplus_uptime: icp_data.sp_yplus.common.uptime
    :field sp_yplus_cpu_temperature: icp_data.sp_yplus.common.cpu_temperature
    :field sp_yplus_temperature: icp_data.sp_yplus.temperature
    :field sp_yplus_mppt_current: icp_data.sp_yplus.mppt_current
    :field sp_yplus_coil_current: icp_data.sp_yplus.coil_current
    
    :field timestamp: icp_data.sp_yminus.common.unix_time
    :field sp_yminus_uptime: icp_data.sp_yminus.common.uptime
    :field sp_yminus_cpu_temperature: icp_data.sp_yminus.common.cpu_temperature
    :field sp_yminus_temperature: icp_data.sp_yminus.temperature
    :field sp_yminus_mppt_current: icp_data.sp_yminus.mppt_current
    
    :field timestamp: icp_data.sp_zplus.common.unix_time
    :field sp_zplus_uptime: icp_data.sp_zplus.common.uptime
    :field sp_zplus_cpu_temperature: icp_data.sp_zplus.common.cpu_temperature
    :field sp_zplus_temperature: icp_data.sp_zplus.temperature
    
    :field timestamp: icp_data.sp_zminus.common.unix_time
    :field sp_zminus_uptime: icp_data.sp_zminus.common.uptime
    :field sp_zminus_cpu_temperature: icp_data.sp_zminus.common.cpu_temperature
    :field sp_zminus_temperature: icp_data.sp_zminus.temperature
    :field sp_zminus_coil_current: icp_data.sp_zminus.coil_current
    
    :field timestamp: icp_data.st.common.unix_time
    :field st_uptime: icp_data.st.common.uptime
    :field st_cpu_temperature: icp_data.st.common.cpu_temperature
    :field st_fpga_temperature: icp_data.st.fpga_temperature
    :field st_sensor_temperature: icp_data.st.sensor_temperature
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_header = Estcube2.Ax25Header(self._io, self, self._root)
        self.icp_header = Estcube2.IcpHeader(self._io, self, self._root)
        self._raw_icp_data = self._io.read_bytes(self.icp_header.len)
        _io__raw_icp_data = KaitaiStream(BytesIO(self._raw_icp_data))
        self.icp_data = Estcube2.IcpData(_io__raw_icp_data, self, self._root)
        self.icp_crc = self._io.read_u2be()

    class IcpHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dst = self._io.read_u1()
            self.src = self._io.read_u1()
            self.len = self._io.read_u1()
            self.cmd = self._io.read_u1()
            self.uuid = self._io.read_bits_int_be(24)
            self._io.align_to_byte()
            self.mode = self._io.read_u1()


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Estcube2.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Estcube2.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Estcube2.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Estcube2.SsidMask(self._io, self, self._root)
            self.control = self._io.read_u1()
            self.pid = self._io.read_u1()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class EpsHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = Estcube2.CommonHousekeeping(self._io, self, self._root)
            self.enable_reserved0 = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_adc1 = self._io.read_bits_int_be(1) != 0
            self.enable_adc2 = self._io.read_bits_int_be(1) != 0
            self.enable_adc3 = self._io.read_bits_int_be(1) != 0
            self.enable_fram1 = self._io.read_bits_int_be(1) != 0
            self.enable_fram2 = self._io.read_bits_int_be(1) != 0
            self.enable_rtc = self._io.read_bits_int_be(1) != 0
            self.enable_icp0 = self._io.read_bits_int_be(1) != 0
            self.enable_icp1 = self._io.read_bits_int_be(1) != 0
            self.enable_st = self._io.read_bits_int_be(1) != 0
            self.enable_obc = self._io.read_bits_int_be(1) != 0
            self.enable_com_3v3 = self._io.read_bits_int_be(1) != 0
            self.enable_com_dcdc = self._io.read_bits_int_be(1) != 0
            self.enable_com_pa = self._io.read_bits_int_be(1) != 0
            self.enable_eps_dcdc1 = self._io.read_bits_int_be(1) != 0
            self.enable_eps_dcdc2 = self._io.read_bits_int_be(1) != 0
            self.enable_sp = self._io.read_bits_int_be(1) != 0
            self.enable_cgp = self._io.read_bits_int_be(1) != 0
            self.enable_hscom = self._io.read_bits_int_be(1) != 0
            self.enable_eop1 = self._io.read_bits_int_be(1) != 0
            self.enable_eop2 = self._io.read_bits_int_be(1) != 0
            self.enable_esail = self._io.read_bits_int_be(1) != 0
            self.enable_obc_rw = self._io.read_bits_int_be(1) != 0
            self.enable_reserved25 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved26 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved27 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved28 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved29 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved30 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved31 = self._io.read_bits_int_be(1) != 0
            self.error_reserved0 = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_adc1 = self._io.read_bits_int_be(1) != 0
            self.error_adc2 = self._io.read_bits_int_be(1) != 0
            self.error_adc3 = self._io.read_bits_int_be(1) != 0
            self.error_fram1 = self._io.read_bits_int_be(1) != 0
            self.error_fram2 = self._io.read_bits_int_be(1) != 0
            self.error_rtc = self._io.read_bits_int_be(1) != 0
            self.error_icp0 = self._io.read_bits_int_be(1) != 0
            self.error_icp1 = self._io.read_bits_int_be(1) != 0
            self.error_st = self._io.read_bits_int_be(1) != 0
            self.error_dcdc1 = self._io.read_bits_int_be(1) != 0
            self.error_dcdc2 = self._io.read_bits_int_be(1) != 0
            self.error_chg1 = self._io.read_bits_int_be(1) != 0
            self.error_chg2 = self._io.read_bits_int_be(1) != 0
            self.error_dchg1 = self._io.read_bits_int_be(1) != 0
            self.error_dchg2 = self._io.read_bits_int_be(1) != 0
            self.error_reserved17 = self._io.read_bits_int_be(1) != 0
            self.error_reserved18 = self._io.read_bits_int_be(1) != 0
            self.error_reserved19 = self._io.read_bits_int_be(1) != 0
            self.error_reserved20 = self._io.read_bits_int_be(1) != 0
            self.error_reserved21 = self._io.read_bits_int_be(1) != 0
            self.error_reserved22 = self._io.read_bits_int_be(1) != 0
            self.error_reserved23 = self._io.read_bits_int_be(1) != 0
            self.error_reserved24 = self._io.read_bits_int_be(1) != 0
            self.error_reserved25 = self._io.read_bits_int_be(1) != 0
            self.error_reserved26 = self._io.read_bits_int_be(1) != 0
            self.error_reserved27 = self._io.read_bits_int_be(1) != 0
            self.error_reserved28 = self._io.read_bits_int_be(1) != 0
            self.error_reserved29 = self._io.read_bits_int_be(1) != 0
            self.error_reserved30 = self._io.read_bits_int_be(1) != 0
            self.error_reserved31 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.bus_voltage = self._io.read_u2le()
            self.avg_power_balance = self._io.read_s2le()
            self.battery_status_a = self._io.read_bits_int_be(1) != 0
            self.battery_status_b = self._io.read_bits_int_be(1) != 0
            self.battery_status_c = self._io.read_bits_int_be(1) != 0
            self.battery_status_d = self._io.read_bits_int_be(1) != 0
            self.battery_reserved4 = self._io.read_bits_int_be(1) != 0
            self.battery_reserved5 = self._io.read_bits_int_be(1) != 0
            self.battery_reserved6 = self._io.read_bits_int_be(1) != 0
            self.battery_reserved7 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.battery_current_a = self._io.read_u2le()
            self.battery_current_b = self._io.read_u2le()
            self.battery_voltage_a = self._io.read_u2le()
            self.battery_voltage_b = self._io.read_u2le()
            self.battery_voltage_c = self._io.read_u2le()
            self.battery_voltage_d = self._io.read_u2le()
            self.battery_temperature_a = self._io.read_u2le()
            self.battery_temperature_b = self._io.read_u2le()
            self.battery_temperature_c = self._io.read_u2le()
            self.battery_temperature_d = self._io.read_u2le()
            self.st_voltage = self._io.read_u2le()
            self.st_current = self._io.read_u2le()
            self.obc_voltage = self._io.read_u2le()
            self.obc_current = self._io.read_u2le()
            self.com_3v3_voltage = self._io.read_u2le()
            self.com_pa_voltage = self._io.read_u2le()
            self.com_3v3_current = self._io.read_u2le()
            self.com_pa_current = self._io.read_u2le()
            self.eps_voltage = self._io.read_u2le()
            self.eps_dcdc_3v3_voltage = self._io.read_u2le()
            self.eps_current = self._io.read_u2le()
            self.eps_dcdc1_current = self._io.read_u2le()
            self.eps_dcdc2_current = self._io.read_u2le()
            self.sp_voltage = self._io.read_u2le()
            self.sp_current = self._io.read_u2le()
            self.cpd_voltage = self._io.read_u2le()
            self.cpd_current = self._io.read_u2le()
            self.cam1_voltage = self._io.read_u2le()
            self.cam1_current = self._io.read_u2le()
            self.cam2_voltage = self._io.read_u2le()
            self.cam2_current = self._io.read_u2le()
            self.hsom_voltage = self._io.read_u2le()
            self.hsom_current = self._io.read_u2le()
            self.cgp_5v_voltage = self._io.read_u2le()
            self.cgp_mpb_voltage = self._io.read_u2le()
            self.cgp_current = self._io.read_u2le()


    class IcpData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if  ((self.src == 2) and (self.cmd == 131)) :
                self.pcom = Estcube2.PcomHousekeeping(self._io, self, self._root)

            if  ((self.src == 2) and (self.cmd == 131)) :
                self.scom = Estcube2.ScomHousekeeping(self._io, self, self._root)

            if  ((self.src == 3) and (self.cmd == 131)) :
                self.eps = Estcube2.EpsHousekeeping(self._io, self, self._root)

            if  ((self.src == 4) and (self.cmd == 131)) :
                self.obc = Estcube2.ObcHousekeeping(self._io, self, self._root)

            if  ((self.src == 4) and (self.cmd == 131)) :
                self.aocs = Estcube2.AocsHousekeeping(self._io, self, self._root)

            if  ((self.src == 5) and (self.cmd == 131)) :
                self.st = Estcube2.StarTrackerHousekeeping(self._io, self, self._root)

            if  ((self.src == 6) and (self.cmd == 131)) :
                self.sp_xplus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)

            if  ((self.src == 7) and (self.cmd == 131)) :
                self.sp_xminus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)

            if  ((self.src == 8) and (self.cmd == 131)) :
                self.sp_yplus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)

            if  ((self.src == 9) and (self.cmd == 131)) :
                self.sp_yminus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)

            if  ((self.src == 10) and (self.cmd == 131)) :
                self.sp_zplus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)

            if  ((self.src == 11) and (self.cmd == 131)) :
                self.sp_zminus = Estcube2.SidePanelHousekeeping(self._io, self, self._root)


        @property
        def src(self):
            if hasattr(self, '_m_src'):
                return self._m_src

            self._m_src = self._parent.icp_header.src
            return getattr(self, '_m_src', None)

        @property
        def cmd(self):
            if hasattr(self, '_m_cmd'):
                return self._m_cmd

            self._m_cmd = self._parent.icp_header.cmd
            return getattr(self, '_m_cmd', None)


    class AocsHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.bmg160_gyroscope_x = self._io.read_s2le()
            self.bmg160_gyroscope_y = self._io.read_s2le()
            self.bmg160_gyroscope_z = self._io.read_s2le()
            self.lis3mdl_magnetometer_x = self._io.read_s2le()
            self.lis3mdl_magnetometer_y = self._io.read_s2le()
            self.lis3mdl_magnetometer_z = self._io.read_s2le()
            self.sun_x_intensity1 = self._io.read_u2le()
            self.sun_x_intensity2 = self._io.read_u2le()
            self.sun_x_intensity3 = self._io.read_u2le()
            self.sun_x_intensity4 = self._io.read_u2le()
            self.sun_x_intensity5 = self._io.read_u2le()
            self.sun_x_intensity6 = self._io.read_u2le()
            self.sun_x_intensity_location1 = self._io.read_u2le()
            self.sun_x_intensity_location2 = self._io.read_u2le()
            self.sun_x_intensity_location3 = self._io.read_u2le()
            self.sun_x_intensity_location4 = self._io.read_u2le()
            self.sun_x_intensity_location5 = self._io.read_u2le()
            self.sun_x_intensity_location6 = self._io.read_u2le()
            self.sun_y_intensity1 = self._io.read_u2le()
            self.sun_y_intensity2 = self._io.read_u2le()
            self.sun_y_intensity3 = self._io.read_u2le()
            self.sun_y_intensity4 = self._io.read_u2le()
            self.sun_y_intensity5 = self._io.read_u2le()
            self.sun_y_intensity6 = self._io.read_u2le()
            self.sun_y_intensity_location1 = self._io.read_u2le()
            self.sun_y_intensity_location2 = self._io.read_u2le()
            self.sun_y_intensity_location3 = self._io.read_u2le()
            self.sun_y_intensity_location4 = self._io.read_u2le()
            self.sun_y_intensity_location5 = self._io.read_u2le()
            self.sun_y_intensity_location6 = self._io.read_u2le()
            self.mcp9808_temperature1 = self._io.read_u1()
            self.mcp9808_temperature2 = self._io.read_u1()
            self.pointing = self._io.read_bits_int_be(1) != 0
            self.detumbling = self._io.read_bits_int_be(1) != 0
            self.spin_up = self._io.read_bits_int_be(1) != 0
            self.diagnostics = self._io.read_bits_int_be(1) != 0
            self.custom_mode = self._io.read_bits_int_be(1) != 0
            self.reserved = self._io.read_bits_int_be(1) != 0
            self.low_precision = self._io.read_bits_int_be(1) != 0
            self.high_precision = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.reaction_wheel1_rpm = self._io.read_s2le()
            self.reaction_wheel2_rpm = self._io.read_s2le()
            self.reaction_wheel3_rpm = self._io.read_s2le()


    class CommonHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.info_validity = self._io.read_bits_int_be(1) != 0
            self.hk_mode = self._io.read_bits_int_be(2)
            self.flags = self._io.read_bits_int_be(5)
            self._io.align_to_byte()
            self.unix_time = self._io.read_u4le()
            self.commands_queued = self._io.read_u1()
            self.commands_handled = self._io.read_u4le()
            self.commands_mcs = self._io.read_u2le()
            self.resets = self._io.read_u2le()
            self.last_reset_reason = self._io.read_u4le()
            self.uptime = self._io.read_u4le()
            self.errors = self._io.read_u4le()
            self.last_error_time = self._io.read_u4le()
            self.free_heap = self._io.read_u4le()
            self.active_tasks = self._io.read_u1()
            self.cpu_temperature = self._io.read_u1()
            self.current_firmware_slot = self._io.read_u1()
            self.slot1_firmware_version = self._io.read_u2le()
            self.slot2_firmware_version = self._io.read_u2le()
            self.slot3_firmware_version = self._io.read_u2le()
            self.slot4_firmware_version = self._io.read_u2le()
            self.slot1_crc_ok = self._io.read_bits_int_be(1) != 0
            self.slot2_crc_ok = self._io.read_bits_int_be(1) != 0
            self.slot3_crc_ok = self._io.read_bits_int_be(1) != 0
            self.slot4_crc_ok = self._io.read_bits_int_be(1) != 0
            self.reserved = self._io.read_bits_int_be(4)


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


    class StarTrackerHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = Estcube2.CommonHousekeeping(self._io, self, self._root)
            self.enable_reserved0 = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_camera = self._io.read_bits_int_be(1) != 0
            self.enable_fpga = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram = self._io.read_bits_int_be(1) != 0
            self.enable_spi_flash = self._io.read_bits_int_be(1) != 0
            self.enable_sdram = self._io.read_bits_int_be(1) != 0
            self.enable_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_reserved8 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved9 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved10 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved11 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved12 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved13 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved14 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved15 = self._io.read_bits_int_be(1) != 0
            self.error_mcu = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_camera = self._io.read_bits_int_be(1) != 0
            self.error_fpga = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram = self._io.read_bits_int_be(1) != 0
            self.error_spi_flash = self._io.read_bits_int_be(1) != 0
            self.error_sdram = self._io.read_bits_int_be(1) != 0
            self.error_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_reserved8 = self._io.read_bits_int_be(1) != 0
            self.error_reserved9 = self._io.read_bits_int_be(1) != 0
            self.error_reserved10 = self._io.read_bits_int_be(1) != 0
            self.error_reserved11 = self._io.read_bits_int_be(1) != 0
            self.error_reserved12 = self._io.read_bits_int_be(1) != 0
            self.error_reserved13 = self._io.read_bits_int_be(1) != 0
            self.error_reserved14 = self._io.read_bits_int_be(1) != 0
            self.error_reserved15 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.number_of_images_taken = self._io.read_u4le()
            self.number_of_successfull = self._io.read_u4le()
            self.number_of_fails = self._io.read_u4le()
            self.center_coordinate_x = self._io.read_f8le()
            self.center_coordinate_y = self._io.read_f8le()
            self.timestamp = self._io.read_u4le()
            self.database_version = self._io.read_u1()
            self.fpga_temperature = self._io.read_u2le()
            self.sensor_temperature = self._io.read_u2le()


    class SidePanelHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = Estcube2.CommonHousekeeping(self._io, self, self._root)
            self.enable_reserved0 = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_sunsensor = self._io.read_bits_int_be(1) != 0
            self.enable_fram1 = self._io.read_bits_int_be(1) != 0
            self.enable_fram2 = self._io.read_bits_int_be(1) != 0
            self.enable_icp0 = self._io.read_bits_int_be(1) != 0
            self.enable_mag = self._io.read_bits_int_be(1) != 0
            self.enable_temp = self._io.read_bits_int_be(1) != 0
            self.enable_mppt = self._io.read_bits_int_be(1) != 0
            self.enable_coil = self._io.read_bits_int_be(1) != 0
            self.enable_reserved11 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved12 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved13 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved14 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved15 = self._io.read_bits_int_be(1) != 0
            self.error_mcu = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_sunsensor = self._io.read_bits_int_be(1) != 0
            self.error_fram1 = self._io.read_bits_int_be(1) != 0
            self.error_fram2 = self._io.read_bits_int_be(1) != 0
            self.error_icp0 = self._io.read_bits_int_be(1) != 0
            self.error_mag = self._io.read_bits_int_be(1) != 0
            self.error_temp = self._io.read_bits_int_be(1) != 0
            self.error_mppt = self._io.read_bits_int_be(1) != 0
            self.error_coil = self._io.read_bits_int_be(1) != 0
            self.error_reserved11 = self._io.read_bits_int_be(1) != 0
            self.error_reserved12 = self._io.read_bits_int_be(1) != 0
            self.error_reserved13 = self._io.read_bits_int_be(1) != 0
            self.error_reserved14 = self._io.read_bits_int_be(1) != 0
            self.error_reserved15 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.temperature = self._io.read_u1()
            self.mppt_current = self._io.read_u2le()
            self.coil_current = self._io.read_u2le()


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
            self.callsign_ror = Estcube2.Callsign(_io__raw_callsign_ror, self, self._root)


    class ObcHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = Estcube2.CommonHousekeeping(self._io, self, self._root)
            self.enable_reserved = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_qspi_flash1 = self._io.read_bits_int_be(1) != 0
            self.enable_qspi_flash2 = self._io.read_bits_int_be(1) != 0
            self.enable_fmc_mram = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram1_obc = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram2_aocs1 = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram3_aocs2 = self._io.read_bits_int_be(1) != 0
            self.enable_io_expander = self._io.read_bits_int_be(1) != 0
            self.enable_fmc_mram_temp_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_qspi_flash_temp_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_io_expander_temp_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_rtc = self._io.read_bits_int_be(1) != 0
            self.enable_current_adc = self._io.read_bits_int_be(1) != 0
            self.enable_aocs1_gyroscope1 = self._io.read_bits_int_be(1) != 0
            self.enable_aocs1_gyroscope2 = self._io.read_bits_int_be(1) != 0
            self.enable_aocs1_magnetometer = self._io.read_bits_int_be(1) != 0
            self.enable_aocs1_accelerometer = self._io.read_bits_int_be(1) != 0
            self.enable_aocs1_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_aocs2_gyroscope1 = self._io.read_bits_int_be(1) != 0
            self.enable_aocs2_gyroscope2 = self._io.read_bits_int_be(1) != 0
            self.enable_aocs2_magnetometer = self._io.read_bits_int_be(1) != 0
            self.enable_aocs2_accelerometer = self._io.read_bits_int_be(1) != 0
            self.enable_aocs2_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.enable_payload_bus = self._io.read_bits_int_be(1) != 0
            self.enable_icp1_bus = self._io.read_bits_int_be(1) != 0
            self.enable_icp2_bus = self._io.read_bits_int_be(1) != 0
            self.enable_reaction_wheel1 = self._io.read_bits_int_be(1) != 0
            self.enable_reaction_wheel2 = self._io.read_bits_int_be(1) != 0
            self.enable_reaction_wheel3 = self._io.read_bits_int_be(1) != 0
            self.enable_oscillator = self._io.read_bits_int_be(1) != 0
            self.error_mcu = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_qspi_flash1 = self._io.read_bits_int_be(1) != 0
            self.error_qspi_flash2 = self._io.read_bits_int_be(1) != 0
            self.error_fmc_mram = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram1_obc = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram2_aocs1 = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram3_aocs2 = self._io.read_bits_int_be(1) != 0
            self.error_io_expander = self._io.read_bits_int_be(1) != 0
            self.error_mram_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_qspi_flash_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_io_expander_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_rtc = self._io.read_bits_int_be(1) != 0
            self.error_current_adc = self._io.read_bits_int_be(1) != 0
            self.error_aocs1_gyro1 = self._io.read_bits_int_be(1) != 0
            self.error_aocs1_gyro2 = self._io.read_bits_int_be(1) != 0
            self.error_aocs1_magnet = self._io.read_bits_int_be(1) != 0
            self.error_aocs1_accelerometer = self._io.read_bits_int_be(1) != 0
            self.error_aocs1_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_aocs2_gyro1 = self._io.read_bits_int_be(1) != 0
            self.error_aocs2_gyro2 = self._io.read_bits_int_be(1) != 0
            self.error_aocs2_magnet = self._io.read_bits_int_be(1) != 0
            self.error_aocs2_accelerometer = self._io.read_bits_int_be(1) != 0
            self.error_aocs2_temperature_sensor = self._io.read_bits_int_be(1) != 0
            self.error_payload_bus = self._io.read_bits_int_be(1) != 0
            self.error_icp1_bus = self._io.read_bits_int_be(1) != 0
            self.error_icp2_bus = self._io.read_bits_int_be(1) != 0
            self.error_reaction_wheel1 = self._io.read_bits_int_be(1) != 0
            self.error_reaction_wheel2 = self._io.read_bits_int_be(1) != 0
            self.error_reaction_wheel3 = self._io.read_bits_int_be(1) != 0
            self.error_oscillator = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.fmc_mram_temperature = self._io.read_u1()
            self.qspi_fram_temperature = self._io.read_u1()
            self.io_expander_temperature = self._io.read_u1()


    class PcomHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.common = Estcube2.CommonHousekeeping(self._io, self, self._root)
            self.enable_reserved0 = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_qspi_fram = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram = self._io.read_bits_int_be(1) != 0
            self.enable_transceiver = self._io.read_bits_int_be(1) != 0
            self.enable_dac = self._io.read_bits_int_be(1) != 0
            self.enable_icp0 = self._io.read_bits_int_be(1) != 0
            self.enable_icp1 = self._io.read_bits_int_be(1) != 0
            self.enable_icp2 = self._io.read_bits_int_be(1) != 0
            self.enable_oscillator = self._io.read_bits_int_be(1) != 0
            self.enable_temperature_sensor1 = self._io.read_bits_int_be(1) != 0
            self.enable_temperature_sensor2 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved2 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved3 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved4 = self._io.read_bits_int_be(1) != 0
            self.error_mcu = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_qspi_fram = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram = self._io.read_bits_int_be(1) != 0
            self.error_transceiver = self._io.read_bits_int_be(1) != 0
            self.error_dac = self._io.read_bits_int_be(1) != 0
            self.error_icp0 = self._io.read_bits_int_be(1) != 0
            self.error_icp1 = self._io.read_bits_int_be(1) != 0
            self.error_icp2 = self._io.read_bits_int_be(1) != 0
            self.error_oscillator = self._io.read_bits_int_be(1) != 0
            self.error_temperature_sensor1 = self._io.read_bits_int_be(1) != 0
            self.error_temperature_sensor2 = self._io.read_bits_int_be(1) != 0
            self.error_reserved1 = self._io.read_bits_int_be(1) != 0
            self.error_reserved2 = self._io.read_bits_int_be(1) != 0
            self.error_reserved3 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.rssi = self._io.read_u1()
            self.last_packet_time = self._io.read_bits_int_be(31)
            self.last_packet_time_invalid = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.dropped_packets = self._io.read_u4le()
            self.gs_packets = self._io.read_u4le()
            self.sent_packets = self._io.read_u4le()
            self.transceiver_gain = self._io.read_u1()
            self.power_amplifier_temperature = self._io.read_u1()
            self.forward_rf_power = self._io.read_s1()
            self.reflected_rf_power = self._io.read_s1()


    class ScomHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.enable_reserved1 = self._io.read_bits_int_be(1) != 0
            self.enable_internal_flash = self._io.read_bits_int_be(1) != 0
            self.enable_internal_sram = self._io.read_bits_int_be(1) != 0
            self.enable_qspi_fram = self._io.read_bits_int_be(1) != 0
            self.enable_spi_fram = self._io.read_bits_int_be(1) != 0
            self.enable_transceiver = self._io.read_bits_int_be(1) != 0
            self.enable_dac = self._io.read_bits_int_be(1) != 0
            self.enable_icp2 = self._io.read_bits_int_be(1) != 0
            self.enable_oscillator = self._io.read_bits_int_be(1) != 0
            self.enable_temperature_sensor1 = self._io.read_bits_int_be(1) != 0
            self.enable_temperature_sensor2 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved2 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved3 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved4 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved5 = self._io.read_bits_int_be(1) != 0
            self.enable_reserved6 = self._io.read_bits_int_be(1) != 0
            self.error_mcu = self._io.read_bits_int_be(1) != 0
            self.error_internal_flash = self._io.read_bits_int_be(1) != 0
            self.error_internal_sram = self._io.read_bits_int_be(1) != 0
            self.error_qspi_fram = self._io.read_bits_int_be(1) != 0
            self.error_spi_fram = self._io.read_bits_int_be(1) != 0
            self.error_transceiver = self._io.read_bits_int_be(1) != 0
            self.error_dac = self._io.read_bits_int_be(1) != 0
            self.error_icp2 = self._io.read_bits_int_be(1) != 0
            self.error_oscillator = self._io.read_bits_int_be(1) != 0
            self.error_temperature_sensor1 = self._io.read_bits_int_be(1) != 0
            self.error_temperature_sensor2 = self._io.read_bits_int_be(1) != 0
            self.error_reserved1 = self._io.read_bits_int_be(1) != 0
            self.error_reserved2 = self._io.read_bits_int_be(1) != 0
            self.error_reserved3 = self._io.read_bits_int_be(1) != 0
            self.error_reserved4 = self._io.read_bits_int_be(1) != 0
            self.error_reserved5 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.rssi = self._io.read_u1()
            self.last_packet_time = self._io.read_bits_int_be(31)
            self.last_packet_time_invalid = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.dropped_packets = self._io.read_u4le()
            self.gs_packets = self._io.read_u4le()
            self.sent_packets = self._io.read_u4le()
            self.digipeated_packets = self._io.read_u4le()
            self.power_amplifier_temperature = self._io.read_u1()
            self.forward_rf_power = self._io.read_s1()
            self.reflected_rf_power = self._io.read_s1()



