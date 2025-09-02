# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sakura(KaitaiStruct):
    """:field cw_callsign_and_satellite_name: sakura.type_check.cw_callsign_and_satellite_name
    :field cw_batt_v: sakura.type_check.cw_batt_v
    :field cw_batt_i: sakura.type_check.cw_batt_i
    :field cw_batt_t: sakura.type_check.cw_batt_t
    :field cw_bpb_t: sakura.type_check.cw_bpb_t
    :field cw_raw_i: sakura.type_check.cw_raw_i
    :field cw_power_5v0: sakura.type_check.cw_power_5v0
    :field cw_pwr_ant_dep: sakura.type_check.cw_pwr_ant_dep
    :field cw_power_com: sakura.type_check.cw_power_com
    :field cw_sap_minus_x: sakura.type_check.cw_sap_minus_x
    :field cw_sap_plus_y: sakura.type_check.cw_sap_plus_y
    :field cw_sap_minus_y: sakura.type_check.cw_sap_minus_y
    :field cw_sap_plus_z: sakura.type_check.cw_sap_plus_z
    :field cw_sap_minus_z: sakura.type_check.cw_sap_minus_z
    :field cw_reserve_cmd_counter: sakura.type_check.cw_reserve_cmd_counter
    :field cw_gmsk_cmd_counter: sakura.type_check.cw_gmsk_cmd_counter
    :field cw_kill_sw: sakura.type_check.cw_kill_sw
    :field cw_kill_counter: sakura.type_check.cw_kill_counter
    :field cw_mission_pic_on_off: sakura.type_check.cw_mission_pic_on_off
    :field cw_mis_error_flag: sakura.type_check.cw_mis_error_flag
    :field cw_mis_end_flag: sakura.type_check.cw_mis_end_flag
    :field cw_aprs_flag: sakura.type_check.cw_aprs_flag
    :field cw_current_mis: sakura.type_check.cw_current_mis
    :field cw_beacon: sakura.type_check.cw_beacon
    :field beacon_type: sakura.type_check.beacon_type
    :field cam_callsign_header: sakura.type_check.type_check_1.cam_callsign_header
    :field cam_ctrl: sakura.type_check.type_check_1.cam_ctrl
    :field cam_pid: sakura.type_check.type_check_1.cam_pid
    :field cam_sat_id: sakura.type_check.type_check_1.cam_sat_id
    :field cam_packet_id: sakura.type_check.type_check_1.cam_packet_id
    :field cam_reserved: sakura.type_check.type_check_1.cam_reserved
    :field cam_packet_number: sakura.type_check.type_check_1.cam_packet_number
    :field cam_soi: sakura.type_check.type_check_1.cam_soi
    :field cam_jfif_marker: sakura.type_check.type_check_1.cam_jfif_marker
    :field cam_data_length: sakura.type_check.type_check_1.cam_data_length
    :field cam_jfif_id: sakura.type_check.type_check_1.cam_jfif_id
    :field cam_data_b64_encoded: sakura.type_check.type_check_1.cam_data.b64encstring.cam_data_b64_encoded
    :field beacon_type: sakura.type_check.type_check_1.beacon_type
    :field hk_callsign_header: sakura.type_check.type_check_1.type_check_2.hk_callsign_header
    :field seconds: sakura.type_check.type_check_1.type_check_2.seconds
    :field minutes: sakura.type_check.type_check_1.type_check_2.minutes
    :field hours: sakura.type_check.type_check_1.type_check_2.hours
    :field days: sakura.type_check.type_check_1.type_check_2.days
    :field n_a: sakura.type_check.type_check_1.type_check_2.n_a
    :field temp_minus_x: sakura.type_check.type_check_1.type_check_2.temp_minus_x
    :field temp_plus_y: sakura.type_check.type_check_1.type_check_2.temp_plus_y
    :field temp_minus_y: sakura.type_check.type_check_1.type_check_2.temp_minus_y
    :field temp_plus_z: sakura.type_check.type_check_1.type_check_2.temp_minus_z
    :field temp_minus_z: sakura.type_check.type_check_1.type_check_2.temp_plus_z
    :field bpb_t: sakura.type_check.type_check_1.type_check_2.bpb_t
    :field voltage_minus_x: sakura.type_check.type_check_1.type_check_2.voltage_minus_x
    :field voltage_plus_y: sakura.type_check.type_check_1.type_check_2.voltage_plus_y
    :field voltage_minus_y: sakura.type_check.type_check_1.type_check_2.voltage_minus_y
    :field voltage_plus_z: sakura.type_check.type_check_1.type_check_2.voltage_plus_z
    :field voltage_minus_z: sakura.type_check.type_check_1.type_check_2.voltage_minus_z
    :field current_minus_x: sakura.type_check.type_check_1.type_check_2.current_minus_x
    :field current_plus_y: sakura.type_check.type_check_1.type_check_2.current_plus_y
    :field current_minus_y: sakura.type_check.type_check_1.type_check_2.current_minus_y
    :field current_plus_z: sakura.type_check.type_check_1.type_check_2.current_plus_z
    :field current_minus_z: sakura.type_check.type_check_1.type_check_2.current_plus_z
    :field batt_t: sakura.type_check.type_check_1.type_check_2.batt_t
    :field batt_v: sakura.type_check.type_check_1.type_check_2.batt_v
    :field batt_i: sakura.type_check.type_check_1.type_check_2.batt_i
    :field raw_v: sakura.type_check.type_check_1.type_check_2.raw_v
    :field raw_i: sakura.type_check.type_check_1.type_check_2.raw_i
    :field src_v: sakura.type_check.type_check_1.type_check_2.src_v
    :field src_i: sakura.type_check.type_check_1.type_check_2.src_i
    :field kill_sw: sakura.type_check.type_check_1.type_check_2.kill_sw
    :field raw_v_1: sakura.type_check.type_check_1.type_check_2.raw_v_1
    :field q3v3_1_i: sakura.type_check.type_check_1.type_check_2.q3v3_1_i
    :field q3v3_2_i: sakura.type_check.type_check_1.type_check_2.q3v3_2_i
    :field com_i: sakura.type_check.type_check_1.type_check_2.com_i
    :field ant_dep_i: sakura.type_check.type_check_1.type_check_2.ant_dep_i
    :field q5v0_i: sakura.type_check.type_check_1.type_check_2.q5v0_i
    :field reset_raw_v_mon: sakura.type_check.type_check_1.type_check_2.reset_raw_v_mon
    :field power_com: sakura.type_check.type_check_1.type_check_2.power_com
    :field power_5v0: sakura.type_check.type_check_1.type_check_2.power_5v0
    :field dcdc_3v3_1: sakura.type_check.type_check_1.type_check_2.dcdc_3v3_1
    :field pwr_ant_dep: sakura.type_check.type_check_1.type_check_2.pwr_ant_dep
    :field pwr_3v3_2: sakura.type_check.type_check_1.type_check_2.pwr_3v3_2
    :field pwr_3v3_1: sakura.type_check.type_check_1.type_check_2.pwr_3v3_1
    :field dcdc_5v0: sakura.type_check.type_check_1.type_check_2.dcdc_5v0
    :field dcdc_3v3_2: sakura.type_check.type_check_1.type_check_2.dcdc_3v3_2
    :field pwr_compic: sakura.type_check.type_check_1.type_check_2.pwr_compic
    :field pwr_mainpic: sakura.type_check.type_check_1.type_check_2.pwr_mainpic
    :field empty: sakura.type_check.type_check_1.type_check_2.empty
    :field mp_reset_counter: sakura.type_check.type_check_1.type_check_2.mp_reset_counter
    :field rssi: sakura.type_check.type_check_1.type_check_2.rssi
    :field com_t: sakura.type_check.type_check_1.type_check_2.com_t
    :field com_seq_counter: sakura.type_check.type_check_1.type_check_2.com_seq_counter
    :field cmd_uplink_counter: sakura.type_check.type_check_1.type_check_2.cmd_uplink_counter
    :field mis_ack: sakura.type_check.type_check_1.type_check_2.mis_ack
    :field n_a_2: sakura.type_check.type_check_1.type_check_2.n_a_2
    :field current_mis: sakura.type_check.type_check_1.type_check_2.current_mis
    :field mis_counter: sakura.type_check.type_check_1.type_check_2.mis_counter
    :field checksum: sakura.type_check.type_check_1.type_check_2.checksum
    :field beacon_type: sakura.type_check.type_check_1.type_check_2.beacon_type
    :field auto_gmsk_callsign_header: sakura.type_check.type_check_1.type_check_2.auto_gmsk_callsign_header
    :field flag_data_address: sakura.type_check.type_check_1.type_check_2.flag_data_address
    :field commands_reserved_data_address: sakura.type_check.type_check_1.type_check_2.commands_reserved_data_address
    :field log_data_address: sakura.type_check.type_check_1.type_check_2.log_data_address
    :field hk_data_address: sakura.type_check.type_check_1.type_check_2.hk_data_address
    :field cw_data_address: sakura.type_check.type_check_1.type_check_2.cw_data_address
    :field high_sampling_hk_data_address: sakura.type_check.type_check_1.type_check_2.high_sampling_hk_data_address
    :field aprs_message_data_address: sakura.type_check.type_check_1.type_check_2type_check.aprs_message_data_address
    :field aprs_log_data_address: sakura.type_check.type_check_1.type_check_2.aprs_log_data_address
    :field mission_log_data_address: sakura.type_check.type_check_1.type_check_2.mission_log_data_address
    :field sun_camera_thumbnail_address: sakura.type_check.type_check_1.type_check_2.sun_camera_thumbnail_address
    :field earth_camera_thumbnail_address: sakura.type_check.type_check_1.type_check_2.earth_camera_image_address
    :field sun_camera_image_address: sakura.type_check.type_check_1.type_check_2.sun_camera_image_address
    :field earth_camera_image_address: sakura.type_check.type_check_1.type_check_2.earth_camera_image_address
    :field sun_sensor_log_data_address: sakura.type_check.type_check_1.type_check_2.sun_sensor_log_data_address
    :field flash_memory_rewrite_count: sakura.type_check.type_check_1.type_check_2.flash_memory_rewrite_count
    :field antenna_deployment_attempts_count: sakura.type_check.type_check_1.type_check_2.antenna_deployment_attempts_count
    :field ongoing_mission: sakura.type_check.type_check_1.type_check_2.type_check_1.type_check_2type_check.ongoing_mission
    :field reserved_command: sakura.type_check.type_check_1.type_check_2.reserved_command
    :field kill_switch_flag: sakura.type_check.type_check_1.type_check_2.kill_switch_flag
    :field beacon_type: sakura.type_check.type_check_1.type_check_2.beacon_type
    :field dest_callsign: sakura.type_check.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: sakura.type_check.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: sakura.type_check.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: sakura.type_check.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: sakura.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: sakura.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: sakura.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field ctl: sakura.type_check.ax25_frame.ax25_header.ctl
    :field pid: sakura.type_check.ax25_frame.payload.pid
    :field monitor: sakura.type_check.ax25_frame.payload.ax25_info.data_monitor
    :field beacon_type: sakura.type_check.beacon_type
    
    .. seealso::
       Source - https://sites.google.com/p.chibakoudai.jp/gardens-03/home-english/documents/transmission-format
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.sakura = Sakura.SakuraT(self._io, self, self._root)

    class AutoGmskOrHk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check_2
            if _on == 51:
                self.type_check_2 = Sakura.Hk(self._io, self, self._root)
            else:
                self.type_check_2 = Sakura.AutoGmsk(self._io, self, self._root)

        @property
        def check_2(self):
            if hasattr(self, '_m_check_2'):
                return self._m_check_2

            _pos = self._io.pos()
            self._io.seek(22)
            self._m_check_2 = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_check_2', None)


    class Cam(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cam_callsign_header = (self._io.read_bytes(14)).decode(u"ASCII")
            if not self.cam_callsign_header == u"JS1YMY0JS1YNI0":
                raise kaitaistruct.ValidationNotEqualError(u"JS1YMY0JS1YNI0", self.cam_callsign_header, self._io, u"/types/cam/seq/0")
            self.cam_ctrl = self._io.read_u1()
            if not self.cam_ctrl == 62:
                raise kaitaistruct.ValidationNotEqualError(62, self.cam_ctrl, self._io, u"/types/cam/seq/1")
            self.cam_pid = self._io.read_u1()
            if not self.cam_pid == 240:
                raise kaitaistruct.ValidationNotEqualError(240, self.cam_pid, self._io, u"/types/cam/seq/2")
            self.cam_sat_id = self._io.read_u1()
            if not self.cam_sat_id == 83:
                raise kaitaistruct.ValidationNotEqualError(83, self.cam_sat_id, self._io, u"/types/cam/seq/3")
            self.cam_packet_id = self._io.read_u1()
            if not self.cam_packet_id == 204:
                raise kaitaistruct.ValidationNotEqualError(204, self.cam_packet_id, self._io, u"/types/cam/seq/4")
            self.cam_reserved = self._io.read_u1()
            self.packet_number_byte1 = self._io.read_u1()
            self.packet_number_byte2 = self._io.read_u1()
            self.packet_number_byte3 = self._io.read_u1()
            self.cam_soi = self._io.read_u2be()
            if not self.cam_soi == 65496:
                raise kaitaistruct.ValidationNotEqualError(65496, self.cam_soi, self._io, u"/types/cam/seq/9")
            self.cam_jfif_marker = self._io.read_u2be()
            if not self.cam_jfif_marker == 65504:
                raise kaitaistruct.ValidationNotEqualError(65504, self.cam_jfif_marker, self._io, u"/types/cam/seq/10")
            self.cam_data_length = self._io.read_u2be()
            self.cam_jfif_id = (self._io.read_bytes(4)).decode(u"ASCII")
            if not self.cam_jfif_id == u"JFIF":
                raise kaitaistruct.ValidationNotEqualError(u"JFIF", self.cam_jfif_id, self._io, u"/types/cam/seq/12")
            self._raw_cam_data = self._io.read_bytes_full()
            _io__raw_cam_data = KaitaiStream(BytesIO(self._raw_cam_data))
            self.cam_data = Sakura.Cam.Base64(_io__raw_cam_data, self, self._root)

        class Base64(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self._raw__raw_b64encstring = self._io.read_bytes_full()
                _process = satnogsdecoders.process.B64encode()
                self._raw_b64encstring = _process.decode(self._raw__raw_b64encstring)
                _io__raw_b64encstring = KaitaiStream(BytesIO(self._raw_b64encstring))
                self.b64encstring = Sakura.Cam.Base64string(_io__raw_b64encstring, self, self._root)


        class Base64string(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.cam_data_b64_encoded = (self._io.read_bytes_full()).decode(u"UTF-8")


        @property
        def cam_packet_number(self):
            if hasattr(self, '_m_cam_packet_number'):
                return self._m_cam_packet_number

            self._m_cam_packet_number = (((self.packet_number_byte1 << 16) | (self.packet_number_byte2 << 8)) | self.packet_number_byte3)
            return getattr(self, '_m_cam_packet_number', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"CAM" if 0 == 0 else u"CAM")
            return getattr(self, '_m_beacon_type', None)


    class AutoGmsk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.auto_gmsk_callsign_header = (self._io.read_bytes(14)).decode(u"ASCII")
            if not self.auto_gmsk_callsign_header == u"JS1YMY0JS1YNI0":
                raise kaitaistruct.ValidationNotEqualError(u"JS1YMY0JS1YNI0", self.auto_gmsk_callsign_header, self._io, u"/types/auto_gmsk/seq/0")
            self.auto_gmsk_header_last_part = self._io.read_u2be()
            if not self.auto_gmsk_header_last_part == 16112:
                raise kaitaistruct.ValidationNotEqualError(16112, self.auto_gmsk_header_last_part, self._io, u"/types/auto_gmsk/seq/1")
            self.auto_gmsk_header_last_part_1 = self._io.read_u2be()
            if not self.auto_gmsk_header_last_part_1 == 21265:
                raise kaitaistruct.ValidationNotEqualError(21265, self.auto_gmsk_header_last_part_1, self._io, u"/types/auto_gmsk/seq/2")
            self.auto_gmsk_header_last_part_2 = self._io.read_u2be()
            if not self.auto_gmsk_header_last_part_2 == 65280:
                raise kaitaistruct.ValidationNotEqualError(65280, self.auto_gmsk_header_last_part_2, self._io, u"/types/auto_gmsk/seq/3")
            self.auto_gmsk_header_last_part_3 = self._io.read_u2be()
            if not self.auto_gmsk_header_last_part_3 == 1:
                raise kaitaistruct.ValidationNotEqualError(1, self.auto_gmsk_header_last_part_3, self._io, u"/types/auto_gmsk/seq/4")
            self.flag_data_address = self._io.read_u4be()
            self.commands_reserved_data_address = self._io.read_u4be()
            self.log_data_address = self._io.read_u4be()
            self.hk_data_address = self._io.read_u4be()
            self.cw_data_address = self._io.read_u4be()
            self.high_sampling_hk_data_address = self._io.read_u4be()
            self.aprs_message_data_address = self._io.read_u4be()
            self.aprs_log_data_address = self._io.read_u4be()
            self.mission_log_data_address = self._io.read_u4be()
            self.sun_camera_thumbnail_address = self._io.read_u4be()
            self.earth_camera_thumbnail_address = self._io.read_u4be()
            self.sun_camera_image_address = self._io.read_u4be()
            self.earth_camera_image_address = self._io.read_u4be()
            self.sun_sensor_log_data_address = self._io.read_u4be()
            self.flash_memory_rewrite_count = self._io.read_u4be()
            self.antenna_deployment_attempts_count = self._io.read_u1()
            self.ongoing_mission = self._io.read_u1()
            self.reserved_command = self._io.read_u1()
            self.kill_switch_flag = self._io.read_u1()

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"AUTO GMSK" if 0 == 0 else u"AUTO GMSK")
            return getattr(self, '_m_beacon_type', None)


    class Discard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_byte = self._io.read_u1()
            if not self.first_byte == 0:
                raise kaitaistruct.ValidationNotEqualError(0, self.first_byte, self._io, u"/types/discard/seq/0")


    class Cw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cw_callsign_and_satellite_name = (self._io.read_bytes(21)).decode(u"ASCII")
            if not self.cw_callsign_and_satellite_name == u"sakura js1ymy js1yni ":
                raise kaitaistruct.ValidationNotEqualError(u"sakura js1ymy js1yni ", self.cw_callsign_and_satellite_name, self._io, u"/types/cw/seq/0")
            self.cw_batt_v = self._io.read_u1()
            self.cw_batt_i = self._io.read_u1()
            self.cw_batt_t = self._io.read_u1()
            self.cw_bpb_t = self._io.read_u1()
            self.cw_raw_i = self._io.read_u1()
            self.cw_power_5v0 = self._io.read_bits_int_be(1) != 0
            self.cw_pwr_ant_dep = self._io.read_bits_int_be(1) != 0
            self.cw_power_com = self._io.read_bits_int_be(1) != 0
            self.cw_sap_minus_x = self._io.read_bits_int_be(1) != 0
            self.cw_sap_plus_y = self._io.read_bits_int_be(1) != 0
            self.cw_sap_minus_y = self._io.read_bits_int_be(1) != 0
            self.cw_sap_plus_z = self._io.read_bits_int_be(1) != 0
            self.cw_sap_minus_z = self._io.read_bits_int_be(1) != 0
            self.cw_reserve_cmd_counter = self._io.read_bits_int_be(4)
            self.cw_gmsk_cmd_counter = self._io.read_bits_int_be(3)
            self.cw_kill_sw = self._io.read_bits_int_be(1) != 0
            self.cw_kill_counter = self._io.read_bits_int_be(2)
            self.cw_mission_pic_on_off = self._io.read_bits_int_be(1) != 0
            self.cw_mis_error_flag = self._io.read_bits_int_be(1) != 0
            self.cw_mis_end_flag = self._io.read_bits_int_be(1) != 0
            self.cw_aprs_flag = self._io.read_bits_int_be(1) != 0
            self.cw_current_mis = self._io.read_bits_int_be(2)

        @property
        def data_1_dec_value_5(self):
            if hasattr(self, '_m_data_1_dec_value_5'):
                return self._m_data_1_dec_value_5

            self._m_data_1_dec_value_5 = (8 if int(self.cw_sap_plus_y) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_5', None)

        @property
        def raw_i_hex_left_digit(self):
            if hasattr(self, '_m_raw_i_hex_left_digit'):
                return self._m_raw_i_hex_left_digit

            self._m_raw_i_hex_left_digit = (u"a" if str(self.raw_i_hex_left) == u"10" else (u"b" if str(self.raw_i_hex_left) == u"11" else (u"c" if str(self.raw_i_hex_left) == u"12" else (u"d" if str(self.raw_i_hex_left) == u"13" else (u"e" if str(self.raw_i_hex_left) == u"14" else (u"f" if str(self.raw_i_hex_left) == u"15" else str(self.raw_i_hex_left)))))))
            return getattr(self, '_m_raw_i_hex_left_digit', None)

        @property
        def data_1_dec(self):
            if hasattr(self, '_m_data_1_dec'):
                return self._m_data_1_dec

            self._m_data_1_dec = (((((((self.data_1_dec_value_1 + self.data_1_dec_value_2) + self.data_1_dec_value_3) + self.data_1_dec_value_4) + self.data_1_dec_value_5) + self.data_1_dec_value_6) + self.data_1_dec_value_7) + self.data_1_dec_value_8)
            return getattr(self, '_m_data_1_dec', None)

        @property
        def data_1_dec_value_4(self):
            if hasattr(self, '_m_data_1_dec_value_4'):
                return self._m_data_1_dec_value_4

            self._m_data_1_dec_value_4 = (16 if int(self.cw_sap_minus_x) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_4', None)

        @property
        def batt_t_hex(self):
            if hasattr(self, '_m_batt_t_hex'):
                return self._m_batt_t_hex

            self._m_batt_t_hex = self.batt_t_hex_left_digit + self.batt_t_hex_right_digit
            return getattr(self, '_m_batt_t_hex', None)

        @property
        def data_2_hex_left(self):
            if hasattr(self, '_m_data_2_hex_left'):
                return self._m_data_2_hex_left

            self._m_data_2_hex_left = self.data_2_dec // 16
            return getattr(self, '_m_data_2_hex_left', None)

        @property
        def data_3_hex_right_digit(self):
            if hasattr(self, '_m_data_3_hex_right_digit'):
                return self._m_data_3_hex_right_digit

            self._m_data_3_hex_right_digit = (u"a" if str(self.data_3_hex_right) == u"10" else (u"b" if str(self.data_3_hex_right) == u"11" else (u"c" if str(self.data_3_hex_right) == u"12" else (u"d" if str(self.data_3_hex_right) == u"13" else (u"e" if str(self.data_3_hex_right) == u"14" else (u"f" if str(self.data_3_hex_right) == u"15" else str(self.data_3_hex_right)))))))
            return getattr(self, '_m_data_3_hex_right_digit', None)

        @property
        def data_1_dec_value_6(self):
            if hasattr(self, '_m_data_1_dec_value_6'):
                return self._m_data_1_dec_value_6

            self._m_data_1_dec_value_6 = (4 if int(self.cw_sap_minus_y) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_6', None)

        @property
        def raw_i_hex(self):
            if hasattr(self, '_m_raw_i_hex'):
                return self._m_raw_i_hex

            self._m_raw_i_hex = self.raw_i_hex_left_digit + self.raw_i_hex_right_digit
            return getattr(self, '_m_raw_i_hex', None)

        @property
        def batt_i_hex(self):
            if hasattr(self, '_m_batt_i_hex'):
                return self._m_batt_i_hex

            self._m_batt_i_hex = self.batt_i_hex_left_digit + self.batt_i_hex_right_digit
            return getattr(self, '_m_batt_i_hex', None)

        @property
        def data_1_hex_left(self):
            if hasattr(self, '_m_data_1_hex_left'):
                return self._m_data_1_hex_left

            self._m_data_1_hex_left = self.data_1_dec // 16
            return getattr(self, '_m_data_1_hex_left', None)

        @property
        def data_1_dec_value_7(self):
            if hasattr(self, '_m_data_1_dec_value_7'):
                return self._m_data_1_dec_value_7

            self._m_data_1_dec_value_7 = (2 if int(self.cw_sap_plus_z) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_7', None)

        @property
        def data_3_hex(self):
            if hasattr(self, '_m_data_3_hex'):
                return self._m_data_3_hex

            self._m_data_3_hex = self.data_3_hex_left_digit + self.data_3_hex_right_digit
            return getattr(self, '_m_data_3_hex', None)

        @property
        def data_2_dec(self):
            if hasattr(self, '_m_data_2_dec'):
                return self._m_data_2_dec

            self._m_data_2_dec = ((self.data_2_dec_value_1 + self.data_2_dec_value_2) + self.data_2_dec_value_3)
            return getattr(self, '_m_data_2_dec', None)

        @property
        def data_1_hex_left_digit(self):
            if hasattr(self, '_m_data_1_hex_left_digit'):
                return self._m_data_1_hex_left_digit

            self._m_data_1_hex_left_digit = (u"a" if str(self.data_1_hex_left) == u"10" else (u"b" if str(self.data_1_hex_left) == u"11" else (u"c" if str(self.data_1_hex_left) == u"12" else (u"d" if str(self.data_1_hex_left) == u"13" else (u"e" if str(self.data_1_hex_left) == u"14" else (u"f" if str(self.data_1_hex_left) == u"15" else str(self.data_1_hex_left)))))))
            return getattr(self, '_m_data_1_hex_left_digit', None)

        @property
        def data_2_dec_value_2(self):
            if hasattr(self, '_m_data_2_dec_value_2'):
                return self._m_data_2_dec_value_2

            self._m_data_2_dec_value_2 = (self.cw_gmsk_cmd_counter * 2)
            return getattr(self, '_m_data_2_dec_value_2', None)

        @property
        def data_3_hex_right(self):
            if hasattr(self, '_m_data_3_hex_right'):
                return self._m_data_3_hex_right

            self._m_data_3_hex_right = (self.data_3_dec % 16)
            return getattr(self, '_m_data_3_hex_right', None)

        @property
        def bpb_t_hex_right_digit(self):
            if hasattr(self, '_m_bpb_t_hex_right_digit'):
                return self._m_bpb_t_hex_right_digit

            self._m_bpb_t_hex_right_digit = (u"a" if str(self.bpb_t_hex_right) == u"10" else (u"b" if str(self.bpb_t_hex_right) == u"11" else (u"c" if str(self.bpb_t_hex_right) == u"12" else (u"d" if str(self.bpb_t_hex_right) == u"13" else (u"e" if str(self.bpb_t_hex_right) == u"14" else (u"f" if str(self.bpb_t_hex_right) == u"15" else str(self.bpb_t_hex_right)))))))
            return getattr(self, '_m_bpb_t_hex_right_digit', None)

        @property
        def batt_t_hex_left_digit(self):
            if hasattr(self, '_m_batt_t_hex_left_digit'):
                return self._m_batt_t_hex_left_digit

            self._m_batt_t_hex_left_digit = (u"a" if str(self.batt_t_hex_left) == u"10" else (u"b" if str(self.batt_t_hex_left) == u"11" else (u"c" if str(self.batt_t_hex_left) == u"12" else (u"d" if str(self.batt_t_hex_left) == u"13" else (u"e" if str(self.batt_t_hex_left) == u"14" else (u"f" if str(self.batt_t_hex_left) == u"15" else str(self.batt_t_hex_left)))))))
            return getattr(self, '_m_batt_t_hex_left_digit', None)

        @property
        def data_2_dec_value_1(self):
            if hasattr(self, '_m_data_2_dec_value_1'):
                return self._m_data_2_dec_value_1

            self._m_data_2_dec_value_1 = (self.cw_reserve_cmd_counter * 16)
            return getattr(self, '_m_data_2_dec_value_1', None)

        @property
        def data_3_dec_value_3(self):
            if hasattr(self, '_m_data_3_dec_value_3'):
                return self._m_data_3_dec_value_3

            self._m_data_3_dec_value_3 = (16 if int(self.cw_mis_error_flag) == 1 else 0)
            return getattr(self, '_m_data_3_dec_value_3', None)

        @property
        def data_1_dec_value_1(self):
            if hasattr(self, '_m_data_1_dec_value_1'):
                return self._m_data_1_dec_value_1

            self._m_data_1_dec_value_1 = (128 if int(self.cw_power_5v0) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_1', None)

        @property
        def data_3_dec_value_6(self):
            if hasattr(self, '_m_data_3_dec_value_6'):
                return self._m_data_3_dec_value_6

            self._m_data_3_dec_value_6 = self.cw_current_mis
            return getattr(self, '_m_data_3_dec_value_6', None)

        @property
        def batt_i_hex_right_digit(self):
            if hasattr(self, '_m_batt_i_hex_right_digit'):
                return self._m_batt_i_hex_right_digit

            self._m_batt_i_hex_right_digit = (u"a" if str(self.batt_i_hex_right) == u"10" else (u"b" if str(self.batt_i_hex_right) == u"11" else (u"c" if str(self.batt_i_hex_right) == u"12" else (u"d" if str(self.batt_i_hex_right) == u"13" else (u"e" if str(self.batt_i_hex_right) == u"14" else (u"f" if str(self.batt_i_hex_right) == u"15" else str(self.batt_i_hex_right)))))))
            return getattr(self, '_m_batt_i_hex_right_digit', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"CW" if 0 == 0 else u"CW")
            return getattr(self, '_m_beacon_type', None)

        @property
        def data_3_dec_value_4(self):
            if hasattr(self, '_m_data_3_dec_value_4'):
                return self._m_data_3_dec_value_4

            self._m_data_3_dec_value_4 = (8 if int(self.cw_mis_end_flag) == 1 else 0)
            return getattr(self, '_m_data_3_dec_value_4', None)

        @property
        def batt_v_hex_left_digit(self):
            if hasattr(self, '_m_batt_v_hex_left_digit'):
                return self._m_batt_v_hex_left_digit

            self._m_batt_v_hex_left_digit = (u"a" if str(self.batt_v_hex_left) == u"10" else (u"b" if str(self.batt_v_hex_left) == u"11" else (u"c" if str(self.batt_v_hex_left) == u"12" else (u"d" if str(self.batt_v_hex_left) == u"13" else (u"e" if str(self.batt_v_hex_left) == u"14" else (u"f" if str(self.batt_v_hex_left) == u"15" else str(self.batt_v_hex_left)))))))
            return getattr(self, '_m_batt_v_hex_left_digit', None)

        @property
        def data_2_hex_right(self):
            if hasattr(self, '_m_data_2_hex_right'):
                return self._m_data_2_hex_right

            self._m_data_2_hex_right = (self.data_2_dec % 16)
            return getattr(self, '_m_data_2_hex_right', None)

        @property
        def data_3_dec_value_1(self):
            if hasattr(self, '_m_data_3_dec_value_1'):
                return self._m_data_3_dec_value_1

            self._m_data_3_dec_value_1 = (self.cw_kill_counter * 64)
            return getattr(self, '_m_data_3_dec_value_1', None)

        @property
        def batt_t_hex_right(self):
            if hasattr(self, '_m_batt_t_hex_right'):
                return self._m_batt_t_hex_right

            self._m_batt_t_hex_right = (self.cw_batt_t % 16)
            return getattr(self, '_m_batt_t_hex_right', None)

        @property
        def data_1_dec_value_2(self):
            if hasattr(self, '_m_data_1_dec_value_2'):
                return self._m_data_1_dec_value_2

            self._m_data_1_dec_value_2 = (64 if int(self.cw_pwr_ant_dep) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_2', None)

        @property
        def data_3_dec_value_2(self):
            if hasattr(self, '_m_data_3_dec_value_2'):
                return self._m_data_3_dec_value_2

            self._m_data_3_dec_value_2 = (32 if int(self.cw_mission_pic_on_off) == 1 else 0)
            return getattr(self, '_m_data_3_dec_value_2', None)

        @property
        def data_2_hex_left_digit(self):
            if hasattr(self, '_m_data_2_hex_left_digit'):
                return self._m_data_2_hex_left_digit

            self._m_data_2_hex_left_digit = (u"a" if str(self.data_2_hex_left) == u"10" else (u"b" if str(self.data_2_hex_left) == u"11" else (u"c" if str(self.data_2_hex_left) == u"12" else (u"d" if str(self.data_2_hex_left) == u"13" else (u"e" if str(self.data_2_hex_left) == u"14" else (u"f" if str(self.data_2_hex_left) == u"15" else str(self.data_2_hex_left)))))))
            return getattr(self, '_m_data_2_hex_left_digit', None)

        @property
        def batt_i_hex_left_digit(self):
            if hasattr(self, '_m_batt_i_hex_left_digit'):
                return self._m_batt_i_hex_left_digit

            self._m_batt_i_hex_left_digit = (u"a" if str(self.batt_i_hex_left) == u"10" else (u"b" if str(self.batt_i_hex_left) == u"11" else (u"c" if str(self.batt_i_hex_left) == u"12" else (u"d" if str(self.batt_i_hex_left) == u"13" else (u"e" if str(self.batt_i_hex_left) == u"14" else (u"f" if str(self.batt_i_hex_left) == u"15" else str(self.batt_i_hex_left)))))))
            return getattr(self, '_m_batt_i_hex_left_digit', None)

        @property
        def data_2_hex_right_digit(self):
            if hasattr(self, '_m_data_2_hex_right_digit'):
                return self._m_data_2_hex_right_digit

            self._m_data_2_hex_right_digit = (u"a" if str(self.data_2_hex_right) == u"10" else (u"b" if str(self.data_2_hex_right) == u"11" else (u"c" if str(self.data_2_hex_right) == u"12" else (u"d" if str(self.data_2_hex_right) == u"13" else (u"e" if str(self.data_2_hex_right) == u"14" else (u"f" if str(self.data_2_hex_right) == u"15" else str(self.data_2_hex_right)))))))
            return getattr(self, '_m_data_2_hex_right_digit', None)

        @property
        def batt_v_hex_right_digit(self):
            if hasattr(self, '_m_batt_v_hex_right_digit'):
                return self._m_batt_v_hex_right_digit

            self._m_batt_v_hex_right_digit = (u"a" if str(self.batt_v_hex_right) == u"10" else (u"b" if str(self.batt_v_hex_right) == u"11" else (u"c" if str(self.batt_v_hex_right) == u"12" else (u"d" if str(self.batt_v_hex_right) == u"13" else (u"e" if str(self.batt_v_hex_right) == u"14" else (u"f" if str(self.batt_v_hex_right) == u"15" else str(self.batt_v_hex_right)))))))
            return getattr(self, '_m_batt_v_hex_right_digit', None)

        @property
        def batt_t_hex_left(self):
            if hasattr(self, '_m_batt_t_hex_left'):
                return self._m_batt_t_hex_left

            self._m_batt_t_hex_left = self.cw_batt_t // 16
            return getattr(self, '_m_batt_t_hex_left', None)

        @property
        def raw_i_hex_left(self):
            if hasattr(self, '_m_raw_i_hex_left'):
                return self._m_raw_i_hex_left

            self._m_raw_i_hex_left = self.cw_raw_i // 16
            return getattr(self, '_m_raw_i_hex_left', None)

        @property
        def bpb_t_hex_right(self):
            if hasattr(self, '_m_bpb_t_hex_right'):
                return self._m_bpb_t_hex_right

            self._m_bpb_t_hex_right = (self.cw_bpb_t % 16)
            return getattr(self, '_m_bpb_t_hex_right', None)

        @property
        def data_3_hex_left(self):
            if hasattr(self, '_m_data_3_hex_left'):
                return self._m_data_3_hex_left

            self._m_data_3_hex_left = self.data_3_dec // 16
            return getattr(self, '_m_data_3_hex_left', None)

        @property
        def bpb_t_hex_left_digit(self):
            if hasattr(self, '_m_bpb_t_hex_left_digit'):
                return self._m_bpb_t_hex_left_digit

            self._m_bpb_t_hex_left_digit = (u"a" if str(self.bpb_t_hex_left) == u"10" else (u"b" if str(self.bpb_t_hex_left) == u"11" else (u"c" if str(self.bpb_t_hex_left) == u"12" else (u"d" if str(self.bpb_t_hex_left) == u"13" else (u"e" if str(self.bpb_t_hex_left) == u"14" else (u"f" if str(self.bpb_t_hex_left) == u"15" else str(self.bpb_t_hex_left)))))))
            return getattr(self, '_m_bpb_t_hex_left_digit', None)

        @property
        def bpb_t_hex_left(self):
            if hasattr(self, '_m_bpb_t_hex_left'):
                return self._m_bpb_t_hex_left

            self._m_bpb_t_hex_left = self.cw_bpb_t // 16
            return getattr(self, '_m_bpb_t_hex_left', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = self.batt_v_hex + self.batt_i_hex + self.batt_t_hex + self.bpb_t_hex + self.raw_i_hex + self.data_1_hex + self.data_2_hex + self.data_3_hex
            return getattr(self, '_m_cw_beacon', None)

        @property
        def data_3_hex_left_digit(self):
            if hasattr(self, '_m_data_3_hex_left_digit'):
                return self._m_data_3_hex_left_digit

            self._m_data_3_hex_left_digit = (u"a" if str(self.data_3_hex_left) == u"10" else (u"b" if str(self.data_3_hex_left) == u"11" else (u"c" if str(self.data_3_hex_left) == u"12" else (u"d" if str(self.data_3_hex_left) == u"13" else (u"e" if str(self.data_3_hex_left) == u"14" else (u"f" if str(self.data_3_hex_left) == u"15" else str(self.data_3_hex_left)))))))
            return getattr(self, '_m_data_3_hex_left_digit', None)

        @property
        def data_3_dec(self):
            if hasattr(self, '_m_data_3_dec'):
                return self._m_data_3_dec

            self._m_data_3_dec = (((((self.data_3_dec_value_1 + self.data_3_dec_value_2) + self.data_3_dec_value_3) + self.data_3_dec_value_4) + self.data_3_dec_value_5) + self.data_3_dec_value_6)
            return getattr(self, '_m_data_3_dec', None)

        @property
        def batt_t_hex_right_digit(self):
            if hasattr(self, '_m_batt_t_hex_right_digit'):
                return self._m_batt_t_hex_right_digit

            self._m_batt_t_hex_right_digit = (u"a" if str(self.batt_t_hex_right) == u"10" else (u"b" if str(self.batt_t_hex_right) == u"11" else (u"c" if str(self.batt_t_hex_right) == u"12" else (u"d" if str(self.batt_t_hex_right) == u"13" else (u"e" if str(self.batt_t_hex_right) == u"14" else (u"f" if str(self.batt_t_hex_right) == u"15" else str(self.batt_t_hex_right)))))))
            return getattr(self, '_m_batt_t_hex_right_digit', None)

        @property
        def data_1_dec_value_3(self):
            if hasattr(self, '_m_data_1_dec_value_3'):
                return self._m_data_1_dec_value_3

            self._m_data_1_dec_value_3 = (32 if int(self.cw_power_com) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_3', None)

        @property
        def data_2_hex(self):
            if hasattr(self, '_m_data_2_hex'):
                return self._m_data_2_hex

            self._m_data_2_hex = self.data_2_hex_left_digit + self.data_2_hex_right_digit
            return getattr(self, '_m_data_2_hex', None)

        @property
        def batt_i_hex_right(self):
            if hasattr(self, '_m_batt_i_hex_right'):
                return self._m_batt_i_hex_right

            self._m_batt_i_hex_right = (self.cw_batt_i % 16)
            return getattr(self, '_m_batt_i_hex_right', None)

        @property
        def raw_i_hex_right(self):
            if hasattr(self, '_m_raw_i_hex_right'):
                return self._m_raw_i_hex_right

            self._m_raw_i_hex_right = (self.cw_raw_i % 16)
            return getattr(self, '_m_raw_i_hex_right', None)

        @property
        def data_1_dec_value_8(self):
            if hasattr(self, '_m_data_1_dec_value_8'):
                return self._m_data_1_dec_value_8

            self._m_data_1_dec_value_8 = (1 if int(self.cw_sap_minus_z) == 1 else 0)
            return getattr(self, '_m_data_1_dec_value_8', None)

        @property
        def raw_i_hex_right_digit(self):
            if hasattr(self, '_m_raw_i_hex_right_digit'):
                return self._m_raw_i_hex_right_digit

            self._m_raw_i_hex_right_digit = (u"a" if str(self.raw_i_hex_right) == u"10" else (u"b" if str(self.raw_i_hex_right) == u"11" else (u"c" if str(self.raw_i_hex_right) == u"12" else (u"d" if str(self.raw_i_hex_right) == u"13" else (u"e" if str(self.raw_i_hex_right) == u"14" else (u"f" if str(self.raw_i_hex_right) == u"15" else str(self.raw_i_hex_right)))))))
            return getattr(self, '_m_raw_i_hex_right_digit', None)

        @property
        def data_1_hex(self):
            if hasattr(self, '_m_data_1_hex'):
                return self._m_data_1_hex

            self._m_data_1_hex = self.data_1_hex_left_digit + self.data_1_hex_right_digit
            return getattr(self, '_m_data_1_hex', None)

        @property
        def batt_v_hex_left(self):
            if hasattr(self, '_m_batt_v_hex_left'):
                return self._m_batt_v_hex_left

            self._m_batt_v_hex_left = self.cw_batt_v // 16
            return getattr(self, '_m_batt_v_hex_left', None)

        @property
        def bpb_t_hex(self):
            if hasattr(self, '_m_bpb_t_hex'):
                return self._m_bpb_t_hex

            self._m_bpb_t_hex = self.bpb_t_hex_left_digit + self.bpb_t_hex_right_digit
            return getattr(self, '_m_bpb_t_hex', None)

        @property
        def batt_v_hex_right(self):
            if hasattr(self, '_m_batt_v_hex_right'):
                return self._m_batt_v_hex_right

            self._m_batt_v_hex_right = (self.cw_batt_v % 16)
            return getattr(self, '_m_batt_v_hex_right', None)

        @property
        def data_2_dec_value_3(self):
            if hasattr(self, '_m_data_2_dec_value_3'):
                return self._m_data_2_dec_value_3

            self._m_data_2_dec_value_3 = (1 if int(self.cw_kill_sw) == 1 else 0)
            return getattr(self, '_m_data_2_dec_value_3', None)

        @property
        def batt_v_hex(self):
            if hasattr(self, '_m_batt_v_hex'):
                return self._m_batt_v_hex

            self._m_batt_v_hex = self.batt_v_hex_left_digit + self.batt_v_hex_right_digit
            return getattr(self, '_m_batt_v_hex', None)

        @property
        def batt_i_hex_left(self):
            if hasattr(self, '_m_batt_i_hex_left'):
                return self._m_batt_i_hex_left

            self._m_batt_i_hex_left = self.cw_batt_i // 16
            return getattr(self, '_m_batt_i_hex_left', None)

        @property
        def data_1_hex_right_digit(self):
            if hasattr(self, '_m_data_1_hex_right_digit'):
                return self._m_data_1_hex_right_digit

            self._m_data_1_hex_right_digit = (u"a" if str(self.data_1_hex_right) == u"10" else (u"b" if str(self.data_1_hex_right) == u"11" else (u"c" if str(self.data_1_hex_right) == u"12" else (u"d" if str(self.data_1_hex_right) == u"13" else (u"e" if str(self.data_1_hex_right) == u"14" else (u"f" if str(self.data_1_hex_right) == u"15" else str(self.data_1_hex_right)))))))
            return getattr(self, '_m_data_1_hex_right_digit', None)

        @property
        def data_1_hex_right(self):
            if hasattr(self, '_m_data_1_hex_right'):
                return self._m_data_1_hex_right

            self._m_data_1_hex_right = (self.data_1_dec % 16)
            return getattr(self, '_m_data_1_hex_right', None)

        @property
        def data_3_dec_value_5(self):
            if hasattr(self, '_m_data_3_dec_value_5'):
                return self._m_data_3_dec_value_5

            self._m_data_3_dec_value_5 = (4 if int(self.cw_aprs_flag) == 1 else 0)
            return getattr(self, '_m_data_3_dec_value_5', None)


    class Hk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_callsign_header = (self._io.read_bytes(14)).decode(u"ASCII")
            if not self.hk_callsign_header == u"JS1YMY0JS1YNI0":
                raise kaitaistruct.ValidationNotEqualError(u"JS1YMY0JS1YNI0", self.hk_callsign_header, self._io, u"/types/hk/seq/0")
            self.hk_header_last_part_0 = self._io.read_u2be()
            if not self.hk_header_last_part_0 == 16112:
                raise kaitaistruct.ValidationNotEqualError(16112, self.hk_header_last_part_0, self._io, u"/types/hk/seq/1")
            self.hk_header_last_part_1 = self._io.read_u2be()
            if not self.hk_header_last_part_1 == 21265:
                raise kaitaistruct.ValidationNotEqualError(21265, self.hk_header_last_part_1, self._io, u"/types/hk/seq/2")
            self.hk_header_last_part_2 = self._io.read_u2be()
            if not self.hk_header_last_part_2 == 65280:
                raise kaitaistruct.ValidationNotEqualError(65280, self.hk_header_last_part_2, self._io, u"/types/hk/seq/3")
            self.hk_header_last_part_3 = self._io.read_u2be()
            if not self.hk_header_last_part_3 == 1:
                raise kaitaistruct.ValidationNotEqualError(1, self.hk_header_last_part_3, self._io, u"/types/hk/seq/4")
            self.hk_header = self._io.read_u1()
            if not self.hk_header == 51:
                raise kaitaistruct.ValidationNotEqualError(51, self.hk_header, self._io, u"/types/hk/seq/5")
            self.seconds = self._io.read_u1()
            self.minutes = self._io.read_u1()
            self.hours = self._io.read_u1()
            self.days = self._io.read_u2be()
            self.n_a = self._io.read_u2be()
            self.temp_minus_x = self._io.read_u2be()
            self.temp_plus_y = self._io.read_u2be()
            self.temp_minus_y = self._io.read_u2be()
            self.temp_plus_z = self._io.read_u2be()
            self.temp_minus_z = self._io.read_u2be()
            self.bpb_t = self._io.read_u2be()
            self.voltage_minus_x = self._io.read_u2be()
            self.voltage_plus_y = self._io.read_u2be()
            self.voltage_minus_y = self._io.read_u2be()
            self.voltage_plus_z = self._io.read_u2be()
            self.voltage_minus_z = self._io.read_u2be()
            self.current_minus_x = self._io.read_u1()
            self.current_plus_y = self._io.read_u1()
            self.current_minus_y = self._io.read_u1()
            self.current_plus_z = self._io.read_u1()
            self.current_minus_z = self._io.read_u1()
            self.batt_t = self._io.read_u1()
            self.batt_v = self._io.read_u1()
            self.batt_i = self._io.read_u2be()
            self.raw_v = self._io.read_u1()
            self.raw_i = self._io.read_u2be()
            self.src_v = self._io.read_u1()
            self.src_i = self._io.read_u2be()
            self.kill_sw = self._io.read_u1()
            self.raw_v_1 = self._io.read_u1()
            self.q3v3_1_i = self._io.read_u1()
            self.q3v3_2_i = self._io.read_u1()
            self.com_i = self._io.read_u1()
            self.ant_dep_i = self._io.read_u1()
            self.q5v0_i = self._io.read_u1()
            self.reset_raw_v_mon = self._io.read_bits_int_be(1) != 0
            self.power_com = self._io.read_bits_int_be(1) != 0
            self.power_5v0 = self._io.read_bits_int_be(1) != 0
            self.dcdc_3v3_1 = self._io.read_bits_int_be(1) != 0
            self.pwr_ant_dep = self._io.read_bits_int_be(1) != 0
            self.pwr_3v3_2 = self._io.read_bits_int_be(1) != 0
            self.pwr_3v3_1 = self._io.read_bits_int_be(1) != 0
            self.dcdc_5v0 = self._io.read_bits_int_be(1) != 0
            self.dcdc_3v3_2 = self._io.read_bits_int_be(1) != 0
            self.pwr_compic = self._io.read_bits_int_be(1) != 0
            self.pwr_mainpic = self._io.read_bits_int_be(1) != 0
            self.empty = self._io.read_bits_int_be(5)
            self._io.align_to_byte()
            self.mp_reset_counter = self._io.read_u1()
            self.rssi = self._io.read_u1()
            self.com_t = self._io.read_u1()
            self.com_seq_counter = self._io.read_u1()
            self.cmd_uplink_counter = self._io.read_u1()
            self.mis_ack = self._io.read_u1()
            self.n_a_2 = self._io.read_u1()
            self.current_mis = self._io.read_u1()
            self.mis_counter = self._io.read_u1()
            self.checksum = self._io.read_u1()

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"HK" if 0 == 0 else u"HK")
            return getattr(self, '_m_beacon_type', None)


    class Digi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Sakura.Digi.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Sakura.Digi.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = Sakura.Digi.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Sakura.Digi.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = Sakura.Digi.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = Sakura.Digi.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = Sakura.Digi.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = Sakura.Digi.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Sakura.Digi.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Sakura.Digi.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Sakura.Digi.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Sakura.Digi.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Sakura.Digi.Repeater(self._io, self, self._root)

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
                self.ax25_info = Sakura.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


        class Callsign(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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
                self.ax25_info = Sakura.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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

            @property
            def hbit(self):
                if hasattr(self, '_m_hbit'):
                    return self._m_hbit

                self._m_hbit = ((self.ssid_mask & 128) >> 7)
                return getattr(self, '_m_hbit', None)


        class Repeaters(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rpt_callsign_raw = Sakura.Digi.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Sakura.Digi.SsidMask(self._io, self, self._root)


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
                    _ = Sakura.Digi.Repeaters(self._io, self, self._root)
                    self.rpt_instance.append(_)
                    if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                        break
                    i += 1


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
                self.callsign_ror = Sakura.Digi.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_monitor = (self._io.read_bytes_full()).decode(u"utf-8")


        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"DIGI" if 0 == 0 else u"DIGI")
            return getattr(self, '_m_beacon_type', None)


    class SakuraT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 8314044539276959850:
                self.type_check = Sakura.Cw(self._io, self, self._root)
            elif _on == 5355678641493192778:
                self.type_check = Sakura.DigitalBeacon(self._io, self, self._root)
            else:
                self.type_check = Sakura.Digi(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_check = self._io.read_u8be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class DigitalBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check_1
            if _on == 204:
                self.type_check_1 = Sakura.Cam(self._io, self, self._root)
            elif _on == 17:
                self.type_check_1 = Sakura.AutoGmskOrHk(self._io, self, self._root)
            else:
                self.type_check_1 = Sakura.Discard(self._io, self, self._root)

        @property
        def check_1(self):
            if hasattr(self, '_m_check_1'):
                return self._m_check_1

            _pos = self._io.pos()
            self._io.seek(17)
            self._m_check_1 = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_check_1', None)



