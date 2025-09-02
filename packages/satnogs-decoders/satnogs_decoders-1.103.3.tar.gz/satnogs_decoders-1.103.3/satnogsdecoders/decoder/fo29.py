# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Fo29(KaitaiStruct):
    """:field header_hihi: header_hihi
    :field main_relay: main_relay
    :field dcm: dcm
    :field sram: sram
    :field packet: packet
    :field jta: jta
    :field jtd: jtd
    :field geomagnetism_sensor: geomagnetism_sensor
    :field sun_sensor: sun_sensor
    :field uvc: uvc
    :field uvc_level: uvc_level
    :field pcu_mode: pcu_mode
    :field pcu_level: pcu_level
    :field battery_mode: battery_mode
    :field battery_logic: battery_logic
    :field data_collect_mode: data_collect_mode
    :field repro_mode: repro_mode
    :field packet_hk_date_mode: packet_hk_date_mode
    :field packet_date_collect_mode: packet_date_collect_mode
    :field digitalker_mode: digitalker_mode
    :field double_cmd_ena_dis: double_cmd_ena_dis
    :field uvc_active_passive: uvc_active_passive
    :field cpu_run_reset: cpu_run_reset
    :field ecc_1d: ecc_1d
    :field wdt_1d: wdt_1d
    :field crc_error_1d: crc_error_1d
    :field sc_1d: sc_1d
    :field mem_sel_1_1d: mem_sel_1_1d
    :field mem_sel_2_1d: mem_sel_2_1d
    :field frame_counter_error_1d: frame_counter_error_1d
    :field fm_1d: fm_1d
    :field engineering_data_2a: engineering_data_2a
    :field engineering_data_2b: engineering_data_2b
    :field spin_period: spin_period
    :field magnetorquer_mtq_x_1: magnetorquer_mtq_x_1
    :field magnetorquer_mtq_x_2: magnetorquer_mtq_x_2
    :field magnetorquer_mtq_x_mbc_cont: magnetorquer_mtq_x_mbc_cont
    :field magnetorquer_mtq_x_plus: magnetorquer_mtq_x_plus
    :field magnetorquer_mtq_y_spin_null: magnetorquer_mtq_y_spin_null
    :field magnetorquer_mtq_y_spin: magnetorquer_mtq_y_spin
    :field magnetorquer_mtq_y_1: magnetorquer_mtq_y_1
    :field magnetorquer_mtq_y_2: magnetorquer_mtq_y_2
    :field sun_angle_changed: sun_angle_changed
    :field sun_angle: sun_angle
    :field magnet_sensor_z_axis: magnet_sensor_z_axis
    :field magnet_sensor_x_axis: magnet_sensor_x_axis
    :field current_from_solar_cells: current_from_solar_cells
    :field battery_charge_and_discharge_current: battery_charge_and_discharge_current
    :field battery_voltage: battery_voltage
    :field battery_intermediate_terminal_voltage: battery_intermediate_terminal_voltage
    :field bus_voltage: bus_voltage
    :field jta_tx_power: jta_tx_power
    :field structure_temperature_1: structure_temperature_1
    :field structure_temperature_2: structure_temperature_2
    :field structure_temperature_3: structure_temperature_3
    :field structure_temperature_4: structure_temperature_4
    :field battery_temperature: battery_temperature
    :field beacon: beacon
    :field necessary_for_lengthcheck: necessary_for_lengthcheck
    
    .. seealso::
       Source - https://www.jarl.org/Japanese/3_Fuji/teleme/tlm.htm
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.header_hihi = (self._io.read_bytes(4)).decode(u"ASCII")
        if not self.header_hihi == u"HIHI":
            raise kaitaistruct.ValidationNotEqualError(u"HIHI", self.header_hihi, self._io, u"/seq/0")
        self.byte_1a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_1b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_1c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_1d_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_2a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_2b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_2c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_2d_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_3a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_3b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_3c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_3d_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_4a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_4b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_4c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_4d_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_5a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_5b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_5c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_5d_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_6a_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_6b_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.byte_6c_ascii = (self._io.read_bytes(2)).decode(u"ASCII")
        self.lengthcheck = (self._io.read_bytes_full()).decode(u"utf-8")

    @property
    def digitalker_mode(self):
        if hasattr(self, '_m_digitalker_mode'):
            return self._m_digitalker_mode

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_digitalker_mode = ((int(self.byte_1c_ascii, 16) & 16) >> 4)

        return getattr(self, '_m_digitalker_mode', None)

    @property
    def battery_temperature(self):
        if hasattr(self, '_m_battery_temperature'):
            return self._m_battery_temperature

        if  (((self.byte_6c_ascii)[0:1] != u"*") and ((self.byte_6c_ascii)[1:2] != u"*")) :
            self._m_battery_temperature = ((int(self.byte_6c_ascii, 16) * -0.388375) + 81.883)

        return getattr(self, '_m_battery_temperature', None)

    @property
    def necessary_for_lengthcheck(self):
        if hasattr(self, '_m_necessary_for_lengthcheck'):
            return self._m_necessary_for_lengthcheck

        if len(self.lengthcheck) != 0:
            self._m_necessary_for_lengthcheck = int(self.lengthcheck) // 0

        return getattr(self, '_m_necessary_for_lengthcheck', None)

    @property
    def jta_tx_power(self):
        if hasattr(self, '_m_jta_tx_power'):
            return self._m_jta_tx_power

        if  (((self.byte_5b_ascii)[0:1] != u"*") and ((self.byte_5b_ascii)[1:2] != u"*")) :
            self._m_jta_tx_power = ((int(self.byte_5b_ascii, 16) * 6.4997) - 98.0863)

        return getattr(self, '_m_jta_tx_power', None)

    @property
    def mem_sel_1_1d(self):
        if hasattr(self, '_m_mem_sel_1_1d'):
            return self._m_mem_sel_1_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_mem_sel_1_1d = ((int(self.byte_1d_ascii, 16) & 16) >> 4)

        return getattr(self, '_m_mem_sel_1_1d', None)

    @property
    def data_collect_mode(self):
        if hasattr(self, '_m_data_collect_mode'):
            return self._m_data_collect_mode

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_data_collect_mode = (int(self.byte_1c_ascii, 16) & 1)

        return getattr(self, '_m_data_collect_mode', None)

    @property
    def engineering_data_2a(self):
        if hasattr(self, '_m_engineering_data_2a'):
            return self._m_engineering_data_2a

        if  (((self.byte_2a_ascii)[0:1] != u"*") and ((self.byte_2a_ascii)[1:2] != u"*")) :
            self._m_engineering_data_2a = int(self.byte_2a_ascii, 16)

        return getattr(self, '_m_engineering_data_2a', None)

    @property
    def magnet_sensor_x_axis(self):
        if hasattr(self, '_m_magnet_sensor_x_axis'):
            return self._m_magnet_sensor_x_axis

        if  (((self.byte_3d_ascii)[0:1] != u"*") and ((self.byte_3d_ascii)[1:2] != u"*")) :
            self._m_magnet_sensor_x_axis = (((int(self.byte_3d_ascii, 16) + 102) * 490.196) - 50000)

        return getattr(self, '_m_magnet_sensor_x_axis', None)

    @property
    def packet(self):
        if hasattr(self, '_m_packet'):
            return self._m_packet

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_packet = ((int(self.byte_1a_ascii, 16) & 24) >> 3)

        return getattr(self, '_m_packet', None)

    @property
    def sun_bin(self):
        if hasattr(self, '_m_sun_bin'):
            return self._m_sun_bin

        if  (((self.byte_3b_ascii)[0:1] != u"*") and ((self.byte_3b_ascii)[1:2] != u"*") and (self.dcm == 1)) :
            self._m_sun_bin = (int(self.byte_3b_ascii, 16) & 127)

        return getattr(self, '_m_sun_bin', None)

    @property
    def battery_voltage(self):
        if hasattr(self, '_m_battery_voltage'):
            return self._m_battery_voltage

        if  (((self.byte_4c_ascii)[0:1] != u"*") and ((self.byte_4c_ascii)[1:2] != u"*")) :
            self._m_battery_voltage = (int(self.byte_4c_ascii, 16) * 0.10761)

        return getattr(self, '_m_battery_voltage', None)

    @property
    def battery_mode(self):
        if hasattr(self, '_m_battery_mode'):
            return self._m_battery_mode

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_battery_mode = ((int(self.byte_1b_ascii, 16) & 64) >> 6)

        return getattr(self, '_m_battery_mode', None)

    @property
    def crc_error_1d(self):
        if hasattr(self, '_m_crc_error_1d'):
            return self._m_crc_error_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_crc_error_1d = ((int(self.byte_1d_ascii, 16) & 4) >> 2)

        return getattr(self, '_m_crc_error_1d', None)

    @property
    def spin_period(self):
        if hasattr(self, '_m_spin_period'):
            return self._m_spin_period

        if  (((self.byte_2c_ascii)[0:1] != u"*") and ((self.byte_2c_ascii)[1:2] != u"*") and ((self.byte_2d_ascii)[0:1] != u"*") and ((self.byte_2d_ascii)[1:2] != u"*")) :
            self._m_spin_period = ((((((((((((((((int(self.byte_2c_ascii, 16) & 4) >> 2) * 8192) + (((int(self.byte_2c_ascii, 16) & 8) >> 3) * 4096)) + (((int(self.byte_2c_ascii, 16) & 16) >> 4) * 2048)) + (((int(self.byte_2c_ascii, 16) & 32) >> 5) * 1024)) + (((int(self.byte_2c_ascii, 16) & 64) >> 6) * 512)) + (((int(self.byte_2c_ascii, 16) & 128) >> 7) * 256)) + ((int(self.byte_2d_ascii, 16) & 1) * 128)) + (((int(self.byte_2d_ascii, 16) & 2) >> 1) * 64)) + (((int(self.byte_2d_ascii, 16) & 4) >> 2) * 32)) + (((int(self.byte_2d_ascii, 16) & 8) >> 3) * 16)) + (((int(self.byte_2d_ascii, 16) & 16) >> 4) * 8)) + (((int(self.byte_2d_ascii, 16) & 32) >> 5) * 4)) + (((int(self.byte_2d_ascii, 16) & 64) >> 6) * 2)) + ((int(self.byte_2d_ascii, 16) & 128) >> 7))

        return getattr(self, '_m_spin_period', None)

    @property
    def beacon(self):
        if hasattr(self, '_m_beacon'):
            return self._m_beacon

        self._m_beacon = self.header_hihi + u" " + self.byte_1a_ascii + u" " + self.byte_1b_ascii + u" " + self.byte_1c_ascii + u" " + self.byte_1d_ascii + u" " + self.byte_2a_ascii + u" " + self.byte_2b_ascii + u" " + self.byte_2c_ascii + u" " + self.byte_2d_ascii + u" " + self.byte_3a_ascii + u" " + self.byte_3b_ascii + u" " + self.byte_3c_ascii + u" " + self.byte_3d_ascii + u" " + self.byte_4a_ascii + u" " + self.byte_4b_ascii + u" " + self.byte_4c_ascii + u" " + self.byte_4d_ascii + u" " + self.byte_5a_ascii + u" " + self.byte_5b_ascii + u" " + self.byte_5c_ascii + u" " + self.byte_5d_ascii + u" " + self.byte_6a_ascii + u" " + self.byte_6b_ascii + u" " + self.byte_6c_ascii
        return getattr(self, '_m_beacon', None)

    @property
    def sram(self):
        if hasattr(self, '_m_sram'):
            return self._m_sram

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_sram = ((int(self.byte_1a_ascii, 16) & 4) >> 2)

        return getattr(self, '_m_sram', None)

    @property
    def frame_counter_error_1d(self):
        if hasattr(self, '_m_frame_counter_error_1d'):
            return self._m_frame_counter_error_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_frame_counter_error_1d = ((int(self.byte_1d_ascii, 16) & 64) >> 6)

        return getattr(self, '_m_frame_counter_error_1d', None)

    @property
    def main_relay(self):
        if hasattr(self, '_m_main_relay'):
            return self._m_main_relay

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_main_relay = (int(self.byte_1a_ascii, 16) & 1)

        return getattr(self, '_m_main_relay', None)

    @property
    def magnetorquer_mtq_y_2(self):
        if hasattr(self, '_m_magnetorquer_mtq_y_2'):
            return self._m_magnetorquer_mtq_y_2

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_y_2 = ((int(self.byte_3a_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_magnetorquer_mtq_y_2', None)

    @property
    def ecc_1d(self):
        if hasattr(self, '_m_ecc_1d'):
            return self._m_ecc_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_ecc_1d = (int(self.byte_1d_ascii, 16) & 1)

        return getattr(self, '_m_ecc_1d', None)

    @property
    def magnetorquer_mtq_x_2(self):
        if hasattr(self, '_m_magnetorquer_mtq_x_2'):
            return self._m_magnetorquer_mtq_x_2

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_x_2 = ((int(self.byte_3a_ascii, 16) & 2) >> 1)

        return getattr(self, '_m_magnetorquer_mtq_x_2', None)

    @property
    def magnetorquer_mtq_x_mbc_cont(self):
        if hasattr(self, '_m_magnetorquer_mtq_x_mbc_cont'):
            return self._m_magnetorquer_mtq_x_mbc_cont

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_x_mbc_cont = ((int(self.byte_3a_ascii, 16) & 4) >> 2)

        return getattr(self, '_m_magnetorquer_mtq_x_mbc_cont', None)

    @property
    def current_from_solar_cells(self):
        if hasattr(self, '_m_current_from_solar_cells'):
            return self._m_current_from_solar_cells

        if  (((self.byte_4a_ascii)[0:1] != u"*") and ((self.byte_4a_ascii)[1:2] != u"*")) :
            self._m_current_from_solar_cells = (int(self.byte_4a_ascii, 16) * 0.009804)

        return getattr(self, '_m_current_from_solar_cells', None)

    @property
    def pcu_level(self):
        if hasattr(self, '_m_pcu_level'):
            return self._m_pcu_level

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_pcu_level = ((int(self.byte_1b_ascii, 16) & 48) >> 4)

        return getattr(self, '_m_pcu_level', None)

    @property
    def packet_hk_date_mode(self):
        if hasattr(self, '_m_packet_hk_date_mode'):
            return self._m_packet_hk_date_mode

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_packet_hk_date_mode = ((int(self.byte_1c_ascii, 16) & 4) >> 2)

        return getattr(self, '_m_packet_hk_date_mode', None)

    @property
    def fm_1d(self):
        if hasattr(self, '_m_fm_1d'):
            return self._m_fm_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_fm_1d = ((int(self.byte_1d_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_fm_1d', None)

    @property
    def repro_mode(self):
        if hasattr(self, '_m_repro_mode'):
            return self._m_repro_mode

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_repro_mode = ((int(self.byte_1c_ascii, 16) & 2) >> 1)

        return getattr(self, '_m_repro_mode', None)

    @property
    def engineering_data_2b(self):
        if hasattr(self, '_m_engineering_data_2b'):
            return self._m_engineering_data_2b

        if  (((self.byte_2b_ascii)[0:1] != u"*") and ((self.byte_2b_ascii)[1:2] != u"*")) :
            self._m_engineering_data_2b = int(self.byte_2b_ascii, 16)

        return getattr(self, '_m_engineering_data_2b', None)

    @property
    def geomagnetism_sensor(self):
        if hasattr(self, '_m_geomagnetism_sensor'):
            return self._m_geomagnetism_sensor

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_geomagnetism_sensor = ((int(self.byte_1a_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_geomagnetism_sensor', None)

    @property
    def packet_date_collect_mode(self):
        if hasattr(self, '_m_packet_date_collect_mode'):
            return self._m_packet_date_collect_mode

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_packet_date_collect_mode = ((int(self.byte_1c_ascii, 16) & 8) >> 3)

        return getattr(self, '_m_packet_date_collect_mode', None)

    @property
    def jtd(self):
        if hasattr(self, '_m_jtd'):
            return self._m_jtd

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_jtd = ((int(self.byte_1a_ascii, 16) & 64) >> 6)

        return getattr(self, '_m_jtd', None)

    @property
    def mem_sel_2_1d(self):
        if hasattr(self, '_m_mem_sel_2_1d'):
            return self._m_mem_sel_2_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_mem_sel_2_1d = ((int(self.byte_1d_ascii, 16) & 32) >> 5)

        return getattr(self, '_m_mem_sel_2_1d', None)

    @property
    def battery_intermediate_terminal_voltage(self):
        if hasattr(self, '_m_battery_intermediate_terminal_voltage'):
            return self._m_battery_intermediate_terminal_voltage

        if  (((self.byte_4d_ascii)[0:1] != u"*") and ((self.byte_4d_ascii)[1:2] != u"*")) :
            self._m_battery_intermediate_terminal_voltage = (int(self.byte_4d_ascii, 16) * 0.04817)

        return getattr(self, '_m_battery_intermediate_terminal_voltage', None)

    @property
    def jta(self):
        if hasattr(self, '_m_jta'):
            return self._m_jta

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_jta = ((int(self.byte_1a_ascii, 16) & 32) >> 5)

        return getattr(self, '_m_jta', None)

    @property
    def magnetorquer_mtq_x_1(self):
        if hasattr(self, '_m_magnetorquer_mtq_x_1'):
            return self._m_magnetorquer_mtq_x_1

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_x_1 = (int(self.byte_3a_ascii, 16) & 1)

        return getattr(self, '_m_magnetorquer_mtq_x_1', None)

    @property
    def structure_temperature_4(self):
        if hasattr(self, '_m_structure_temperature_4'):
            return self._m_structure_temperature_4

        if  (((self.byte_6b_ascii)[0:1] != u"*") and ((self.byte_6b_ascii)[1:2] != u"*")) :
            self._m_structure_temperature_4 = ((int(self.byte_6b_ascii, 16) * -0.388375) + 81.883)

        return getattr(self, '_m_structure_temperature_4', None)

    @property
    def structure_temperature_3(self):
        if hasattr(self, '_m_structure_temperature_3'):
            return self._m_structure_temperature_3

        if  (((self.byte_6a_ascii)[0:1] != u"*") and ((self.byte_6a_ascii)[1:2] != u"*")) :
            self._m_structure_temperature_3 = ((int(self.byte_6a_ascii, 16) * -0.388375) + 81.883)

        return getattr(self, '_m_structure_temperature_3', None)

    @property
    def double_cmd_ena_dis(self):
        if hasattr(self, '_m_double_cmd_ena_dis'):
            return self._m_double_cmd_ena_dis

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_double_cmd_ena_dis = ((int(self.byte_1c_ascii, 16) & 32) >> 5)

        return getattr(self, '_m_double_cmd_ena_dis', None)

    @property
    def wdt_1d(self):
        if hasattr(self, '_m_wdt_1d'):
            return self._m_wdt_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_wdt_1d = ((int(self.byte_1d_ascii, 16) & 2) >> 1)

        return getattr(self, '_m_wdt_1d', None)

    @property
    def structure_temperature_1(self):
        if hasattr(self, '_m_structure_temperature_1'):
            return self._m_structure_temperature_1

        if  (((self.byte_5c_ascii)[0:1] != u"*") and ((self.byte_5c_ascii)[1:2] != u"*")) :
            self._m_structure_temperature_1 = ((int(self.byte_5c_ascii, 16) * -0.388375) + 81.883)

        return getattr(self, '_m_structure_temperature_1', None)

    @property
    def sc_1d(self):
        if hasattr(self, '_m_sc_1d'):
            return self._m_sc_1d

        if  (((self.byte_1d_ascii)[0:1] != u"*") and ((self.byte_1d_ascii)[1:2] != u"*")) :
            self._m_sc_1d = ((int(self.byte_1d_ascii, 16) & 8) >> 3)

        return getattr(self, '_m_sc_1d', None)

    @property
    def uvc(self):
        if hasattr(self, '_m_uvc'):
            return self._m_uvc

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_uvc = ((int(self.byte_1b_ascii, 16) & 2) >> 1)

        return getattr(self, '_m_uvc', None)

    @property
    def magnetorquer_mtq_y_spin_null(self):
        if hasattr(self, '_m_magnetorquer_mtq_y_spin_null'):
            return self._m_magnetorquer_mtq_y_spin_null

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_y_spin_null = ((int(self.byte_3a_ascii, 16) & 16) >> 4)

        return getattr(self, '_m_magnetorquer_mtq_y_spin_null', None)

    @property
    def uvc_level(self):
        if hasattr(self, '_m_uvc_level'):
            return self._m_uvc_level

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_uvc_level = ((int(self.byte_1b_ascii, 16) & 4) >> 2)

        return getattr(self, '_m_uvc_level', None)

    @property
    def magnetorquer_mtq_y_1(self):
        if hasattr(self, '_m_magnetorquer_mtq_y_1'):
            return self._m_magnetorquer_mtq_y_1

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_y_1 = ((int(self.byte_3a_ascii, 16) & 64) >> 6)

        return getattr(self, '_m_magnetorquer_mtq_y_1', None)

    @property
    def cpu_run_reset(self):
        if hasattr(self, '_m_cpu_run_reset'):
            return self._m_cpu_run_reset

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_cpu_run_reset = ((int(self.byte_1c_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_cpu_run_reset', None)

    @property
    def uvc_active_passive(self):
        if hasattr(self, '_m_uvc_active_passive'):
            return self._m_uvc_active_passive

        if  (((self.byte_1c_ascii)[0:1] != u"*") and ((self.byte_1c_ascii)[1:2] != u"*")) :
            self._m_uvc_active_passive = ((int(self.byte_1c_ascii, 16) & 64) >> 6)

        return getattr(self, '_m_uvc_active_passive', None)

    @property
    def bus_voltage(self):
        if hasattr(self, '_m_bus_voltage'):
            return self._m_bus_voltage

        if  (((self.byte_5a_ascii)[0:1] != u"*") and ((self.byte_5a_ascii)[1:2] != u"*")) :
            self._m_bus_voltage = (int(self.byte_5a_ascii, 16) * 0.09804)

        return getattr(self, '_m_bus_voltage', None)

    @property
    def pcu_mode(self):
        if hasattr(self, '_m_pcu_mode'):
            return self._m_pcu_mode

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_pcu_mode = ((int(self.byte_1b_ascii, 16) & 8) >> 3)

        return getattr(self, '_m_pcu_mode', None)

    @property
    def sun_angle_changed(self):
        if hasattr(self, '_m_sun_angle_changed'):
            return self._m_sun_angle_changed

        if  (((self.byte_3b_ascii)[0:1] != u"*") and ((self.byte_3b_ascii)[1:2] != u"*") and (self.dcm == 1)) :
            self._m_sun_angle_changed = ((int(self.byte_3b_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_sun_angle_changed', None)

    @property
    def magnet_sensor_z_axis(self):
        if hasattr(self, '_m_magnet_sensor_z_axis'):
            return self._m_magnet_sensor_z_axis

        if  (((self.byte_3c_ascii)[0:1] != u"*") and ((self.byte_3c_ascii)[1:2] != u"*")) :
            self._m_magnet_sensor_z_axis = (int(self.byte_3c_ascii, 16) * 490.196)

        return getattr(self, '_m_magnet_sensor_z_axis', None)

    @property
    def battery_charge_and_discharge_current(self):
        if hasattr(self, '_m_battery_charge_and_discharge_current'):
            return self._m_battery_charge_and_discharge_current

        if  (((self.byte_4b_ascii)[0:1] != u"*") and ((self.byte_4b_ascii)[1:2] != u"*")) :
            self._m_battery_charge_and_discharge_current = -((2 - (int(self.byte_4b_ascii, 16) * 0.0196)))

        return getattr(self, '_m_battery_charge_and_discharge_current', None)

    @property
    def structure_temperature_2(self):
        if hasattr(self, '_m_structure_temperature_2'):
            return self._m_structure_temperature_2

        if  (((self.byte_5d_ascii)[0:1] != u"*") and ((self.byte_5d_ascii)[1:2] != u"*")) :
            self._m_structure_temperature_2 = ((int(self.byte_5d_ascii, 16) * -0.388375) + 81.883)

        return getattr(self, '_m_structure_temperature_2', None)

    @property
    def sun_angle(self):
        if hasattr(self, '_m_sun_angle'):
            return self._m_sun_angle

        if  (((self.byte_3b_ascii)[0:1] != u"*") and ((self.byte_3b_ascii)[1:2] != u"*") and (self.dcm == 1)) :
            self._m_sun_angle = (27.5 if self.sun_bin == 1 else (28.5 if self.sun_bin == 3 else (29.5 if self.sun_bin == 2 else (30.5 if self.sun_bin == 6 else (31.5 if self.sun_bin == 7 else (32.5 if self.sun_bin == 5 else (33.5 if self.sun_bin == 4 else (34.5 if self.sun_bin == 12 else (35.5 if self.sun_bin == 13 else (36.5 if self.sun_bin == 15 else (37.5 if self.sun_bin == 14 else (38.5 if self.sun_bin == 10 else (39.5 if self.sun_bin == 11 else (40.5 if self.sun_bin == 9 else (41.5 if self.sun_bin == 8 else (42.5 if self.sun_bin == 24 else (43.5 if self.sun_bin == 25 else (44.5 if self.sun_bin == 27 else (45.5 if self.sun_bin == 26 else (46.5 if self.sun_bin == 30 else (47.5 if self.sun_bin == 31 else (48.5 if self.sun_bin == 29 else (49.5 if self.sun_bin == 28 else (50.5 if self.sun_bin == 20 else (51.5 if self.sun_bin == 21 else (52.5 if self.sun_bin == 23 else (53.5 if self.sun_bin == 22 else (54.5 if self.sun_bin == 18 else (55.5 if self.sun_bin == 19 else (56.5 if self.sun_bin == 17 else (57.5 if self.sun_bin == 16 else (58.5 if self.sun_bin == 48 else (59.5 if self.sun_bin == 49 else (60.5 if self.sun_bin == 51 else (61.5 if self.sun_bin == 50 else (62.5 if self.sun_bin == 54 else (63.5 if self.sun_bin == 55 else (64.5 if self.sun_bin == 53 else (65.5 if self.sun_bin == 52 else (66.5 if self.sun_bin == 60 else (67.5 if self.sun_bin == 61 else (68.5 if self.sun_bin == 63 else (69.5 if self.sun_bin == 62 else (70.5 if self.sun_bin == 58 else (71.5 if self.sun_bin == 59 else (72.5 if self.sun_bin == 57 else (73.5 if self.sun_bin == 56 else (74.5 if self.sun_bin == 40 else (75.5 if self.sun_bin == 41 else (76.5 if self.sun_bin == 43 else (77.5 if self.sun_bin == 42 else (78.5 if self.sun_bin == 46 else (79.5 if self.sun_bin == 47 else (80.5 if self.sun_bin == 45 else (81.5 if self.sun_bin == 44 else (82.5 if self.sun_bin == 36 else (83.5 if self.sun_bin == 37 else (84.5 if self.sun_bin == 39 else (85.5 if self.sun_bin == 38 else (86.5 if self.sun_bin == 34 else (87.5 if self.sun_bin == 35 else (88.5 if self.sun_bin == 33 else (89.5 if self.sun_bin == 32 else (90.5 if self.sun_bin == 96 else (91.5 if self.sun_bin == 97 else (92.5 if self.sun_bin == 99 else (93.5 if self.sun_bin == 98 else (94.5 if self.sun_bin == 102 else (95.5 if self.sun_bin == 103 else (96.5 if self.sun_bin == 101 else (97.5 if self.sun_bin == 100 else (98.5 if self.sun_bin == 108 else (99.5 if self.sun_bin == 109 else (100.5 if self.sun_bin == 111 else (101.5 if self.sun_bin == 110 else (102.5 if self.sun_bin == 106 else (103.5 if self.sun_bin == 107 else (104.5 if self.sun_bin == 105 else (105.5 if self.sun_bin == 104 else (106.5 if self.sun_bin == 120 else (107.5 if self.sun_bin == 121 else (108.5 if self.sun_bin == 123 else (109.5 if self.sun_bin == 122 else (110.5 if self.sun_bin == 126 else (111.5 if self.sun_bin == 127 else (112.5 if self.sun_bin == 125 else (113.5 if self.sun_bin == 124 else (114.5 if self.sun_bin == 116 else (115.5 if self.sun_bin == 117 else (116.5 if self.sun_bin == 119 else (117.5 if self.sun_bin == 118 else (118.5 if self.sun_bin == 114 else (119.5 if self.sun_bin == 115 else (120.5 if self.sun_bin == 113 else (121.5 if self.sun_bin == 112 else (122.5 if self.sun_bin == 80 else (123.5 if self.sun_bin == 81 else (124.5 if self.sun_bin == 83 else (125.5 if self.sun_bin == 82 else (126.5 if self.sun_bin == 86 else (127.5 if self.sun_bin == 87 else (128.5 if self.sun_bin == 85 else (129.5 if self.sun_bin == 84 else (130.5 if self.sun_bin == 92 else (131.5 if self.sun_bin == 93 else (132.5 if self.sun_bin == 95 else (133.5 if self.sun_bin == 94 else (134.5 if self.sun_bin == 90 else (135.5 if self.sun_bin == 91 else (136.5 if self.sun_bin == 89 else (137.5 if self.sun_bin == 88 else (138.5 if self.sun_bin == 72 else (139.5 if self.sun_bin == 73 else (140.5 if self.sun_bin == 75 else (141.5 if self.sun_bin == 74 else (142.5 if self.sun_bin == 78 else (143.5 if self.sun_bin == 79 else (144.5 if self.sun_bin == 77 else (145.5 if self.sun_bin == 76 else (146.5 if self.sun_bin == 68 else (147.5 if self.sun_bin == 69 else (148.5 if self.sun_bin == 71 else (149.5 if self.sun_bin == 70 else (150.5 if self.sun_bin == 66 else (151.5 if self.sun_bin == 67 else (152.5 if self.sun_bin == 65 else (153.5 if self.sun_bin == 64 else 0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

        return getattr(self, '_m_sun_angle', None)

    @property
    def sun_sensor(self):
        if hasattr(self, '_m_sun_sensor'):
            return self._m_sun_sensor

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_sun_sensor = (int(self.byte_1b_ascii, 16) & 1)

        return getattr(self, '_m_sun_sensor', None)

    @property
    def dcm(self):
        if hasattr(self, '_m_dcm'):
            return self._m_dcm

        if  (((self.byte_1a_ascii)[0:1] != u"*") and ((self.byte_1a_ascii)[1:2] != u"*")) :
            self._m_dcm = ((int(self.byte_1a_ascii, 16) & 2) >> 1)

        return getattr(self, '_m_dcm', None)

    @property
    def magnetorquer_mtq_y_spin(self):
        if hasattr(self, '_m_magnetorquer_mtq_y_spin'):
            return self._m_magnetorquer_mtq_y_spin

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_y_spin = ((int(self.byte_3a_ascii, 16) & 32) >> 5)

        return getattr(self, '_m_magnetorquer_mtq_y_spin', None)

    @property
    def battery_logic(self):
        if hasattr(self, '_m_battery_logic'):
            return self._m_battery_logic

        if  (((self.byte_1b_ascii)[0:1] != u"*") and ((self.byte_1b_ascii)[1:2] != u"*")) :
            self._m_battery_logic = ((int(self.byte_1b_ascii, 16) & 128) >> 7)

        return getattr(self, '_m_battery_logic', None)

    @property
    def magnetorquer_mtq_x_plus(self):
        if hasattr(self, '_m_magnetorquer_mtq_x_plus'):
            return self._m_magnetorquer_mtq_x_plus

        if  (((self.byte_3a_ascii)[0:1] != u"*") and ((self.byte_3a_ascii)[1:2] != u"*")) :
            self._m_magnetorquer_mtq_x_plus = ((int(self.byte_3a_ascii, 16) & 8) >> 3)

        return getattr(self, '_m_magnetorquer_mtq_x_plus', None)


