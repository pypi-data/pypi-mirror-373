# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Yomogi(KaitaiStruct):
    """:field beacon_type: yomogi.type_check.beacon_type
    :field header: yomogi.type_check.header
    :field rssi_temp_or_sms: yomogi.type_check.rssi_temp_or_sms
    :field type_id: yomogi.type_check.type_id
    :field batt_v: yomogi.type_check.batt_v
    :field batt_i: yomogi.type_check.batt_i
    :field batt_t: yomogi.type_check.batt_t
    :field ad_counter: yomogi.type_check.ad_counter
    :field batt_heater: yomogi.type_check.batt_heater
    :field kill_sw_main: yomogi.type_check.kill_sw_main
    :field kill_sw_fab: yomogi.type_check.kill_sw_fab
    :field sap_minus_x: yomogi.type_check.sap_minus_x
    :field sap_plus_y: yomogi.type_check.sap_plus_y
    :field sap_minus_y: yomogi.type_check.sap_minus_y
    :field sap_plus_z: yomogi.type_check.sap_plus_z
    :field sap_minus_z: yomogi.type_check.sap_minus_z
    :field time_after_reset: yomogi.type_check.time_after_reset
    :field raw_i: yomogi.type_check.raw_i
    :field reset_raw_v_mon: yomogi.type_check.reset_raw_v_mon
    :field lcl_uhf_com: yomogi.type_check.lcl_uhf_com
    :field lcl_5v0: yomogi.type_check.lcl_5v0
    :field dcdc_fab: yomogi.type_check.dcdc_fab
    :field lcl_depant: yomogi.type_check.lcl_depant
    :field lcl_3v3_2: yomogi.type_check.lcl_3v3_2
    :field lcl_fab: yomogi.type_check.lcl_fab
    :field dcdc_5v0: yomogi.type_check.dcdc_5v0
    :field dcdc_3v3_2: yomogi.type_check.dcdc_3v3_2
    :field lcl_compic: yomogi.type_check.lcl_compic
    :field lcl_mainpic: yomogi.type_check.lcl_mainpic
    :field gmsk_cmd_counter: yomogi.type_check.gmsk_cmd_counter
    :field reserve_cmd_counter: yomogi.type_check.reserve_cmd_counter
    :field uplink_success: yomogi.type_check.uplink_success
    :field kill_counter: yomogi.type_check.kill_counter
    :field bpb_t: yomogi.type_check.bpb_t
    :field cw_beacon: yomogi.type_check.cw_beacon
    :field hk_header_2: yomogi.type_check.hk_header_2
    :field hk_seconds: yomogi.type_check.hk_seconds
    :field hk_minutes: yomogi.type_check.hk_minutes
    :field hk_hours: yomogi.type_check.hk_hours
    :field hk_days: yomogi.type_check.hk_days
    :field hk_temp_plus_x: yomogi.type_check.hk_temp_plus_x
    :field hk_temp_minus_x: yomogi.type_check.hk_temp_minus_x
    :field hk_temp_plus_y: yomogi.type_check.hk_temp_plus_y
    :field hk_temp_minus_y: yomogi.type_check.hk_temp_minus_y
    :field hk_temp_plus_z: yomogi.type_check.hk_temp_plus_z
    :field hk_temp_minus_z: yomogi.type_check.hk_temp_minus_z
    :field hk_bpb_t: yomogi.type_check.hk_bpb_t
    :field hk_voltage_minus_x: yomogi.type_check.hk_voltage_minus_x
    :field hk_voltage_plus_y: yomogi.type_check.hk_voltage_plus_y
    :field hk_voltage_minus_y: yomogi.type_check.hk_voltage_minus_y
    :field hk_voltage_plus_z: yomogi.type_check.hk_voltage_plus_z
    :field hk_voltage_minus_z: yomogi.type_check.hk_voltage_minus_z
    :field hk_current_minus_x: yomogi.type_check.hk_current_minus_x
    :field hk_current_plus_y: yomogi.type_check.hk_current_plus_y
    :field hk_current_minus_y: yomogi.type_check.hk_current_minus_y
    :field hk_current_plus_z: yomogi.type_check.hk_current_plus_z
    :field hk_current_minus_z: yomogi.type_check.hk_current_minus_z
    :field hk_batt_t: yomogi.type_check.hk_batt_t
    :field hk_batt_v: yomogi.type_check.hk_batt_v
    :field hk_batt_i: yomogi.type_check.hk_batt_i
    :field hk_fab_raw_v: yomogi.type_check.hk_fab_raw_v
    :field hk_fab_raw_i: yomogi.type_check.hk_fab_raw_i
    :field hk_src_v: yomogi.type_check.hk_src_v
    :field hk_src_i: yomogi.type_check.hk_src_i
    :field hk_heater_flag: yomogi.type_check.hk_heater_flag
    :field hk_kill_sw: yomogi.type_check.hk_kill_sw
    :field hk_reset_raw_v: yomogi.type_check.hk_reset_raw_v
    :field hk_v3_3_no1_i: yomogi.type_check.hk_v3_3_no1_i
    :field hk_v3_3_no2_i: yomogi.type_check.hk_v3_3_no2_i
    :field hk_uhf_com_i: yomogi.type_check.hk_uhf_com_i
    :field hk_ant_dep_i: yomogi.type_check.hk_ant_dep_i
    :field hk_v5_0_i: yomogi.type_check.hk_v5_0_i
    :field hk_reset_sw_status: yomogi.type_check.hk_reset_sw_status
    :field hk_reserve_cmd_0_cmd0: yomogi.type_check.hk_reserve_cmd_0_cmd0
    :field hk_reserve_cmd_0_cmd1: yomogi.type_check.hk_reserve_cmd_0_cmd1
    :field hk_reserve_cmd_0_cmd2: yomogi.type_check.hk_reserve_cmd_0_cmd2
    :field hk_reserve_cmd_0_cmd3: yomogi.type_check.hk_reserve_cmd_0_cmd3
    :field hk_reserve_cmd_0_cmd4: yomogi.type_check.hk_reserve_cmd_0_cmd4
    :field hk_reserve_cmd_0_cmd5: yomogi.type_check.hk_reserve_cmd_0_cmd5
    :field hk_reserve_cmd_0_cmd6: yomogi.type_check.hk_reserve_cmd_0_cmd6
    :field hk_reserve_cmd_0_cmd7: yomogi.type_check.hk_reserve_cmd_0_cmd7
    :field hk_reserve_cmd_1_cmd0: yomogi.type_check.hk_reserve_cmd_1_cmd0
    :field hk_reserve_cmd_1_cmd1: yomogi.type_check.hk_reserve_cmd_1_cmd1
    :field hk_reserve_cmd_1_cmd2: yomogi.type_check.hk_reserve_cmd_1_cmd2
    :field hk_reserve_cmd_1_cmd3: yomogi.type_check.hk_reserve_cmd_1_cmd3
    :field hk_reserve_cmd_1_cmd4: yomogi.type_check.hk_reserve_cmd_1_cmd4
    :field hk_reserve_cmd_1_cmd5: yomogi.type_check.hk_reserve_cmd_1_cmd5
    :field hk_reserve_cmd_1_cmd6: yomogi.type_check.hk_reserve_cmd_1_cmd6
    :field hk_reserve_cmd_1_cmd7: yomogi.type_check.hk_reserve_cmd_1_cmd7
    :field digi_dest_callsign: yomogi.type_check.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field digi_src_callsign: yomogi.type_check.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field digi_src_ssid: yomogi.type_check.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field digi_dest_ssid: yomogi.type_check.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: yomogi.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: yomogi.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: yomogi.type_check.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field digi_ctl: yomogi.type_check.ax25_frame.ax25_header.ctl
    :field digi_pid: yomogi.type_check.ax25_frame.ax25_header.pid
    :field digi_message: yomogi.type_check.ax25_frame.ax25_info.digi_message
          
    
    .. seealso::
       Source - https://sites.google.com/s.chibakoudai.jp/gardens-01-yomogi/eng/satellite-eng/documents/transmission-format
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.yomogi = Yomogi.YomogiT(self._io, self, self._root)

    class YomogiT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.format_identifier
            if _on == 8750332926247903338:
                self.type_check = Yomogi.Cw(self._io, self, self._root)
            elif _on == 5352306439146123338:
                self.type_check = Yomogi.Hk(self._io, self, self._root)
            else:
                self.type_check = Yomogi.Aprs(self._io, self, self._root)

        @property
        def format_identifier(self):
            if hasattr(self, '_m_format_identifier'):
                return self._m_format_identifier

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_format_identifier = self._io.read_u8be()
            self._io.seek(_pos)
            return getattr(self, '_m_format_identifier', None)


    class Cw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = (self._io.read_bytes(14)).decode(u"ASCII")
            if not self.header == u"yomogi js1ymx ":
                raise kaitaistruct.ValidationNotEqualError(u"yomogi js1ymx ", self.header, self._io, u"/types/cw/seq/0")
            self.rssi_temp_or_sms = (self._io.read_bytes(6)).decode(u"ASCII")
            self.space = (self._io.read_bytes(1)).decode(u"ASCII")
            if not self.space == u" ":
                raise kaitaistruct.ValidationNotEqualError(u" ", self.space, self._io, u"/types/cw/seq/2")
            self.byte_1 = self._io.read_u1()
            self.byte_2 = self._io.read_u1()
            self.byte_3 = self._io.read_u1()
            self.byte_4 = self._io.read_u1()
            self.byte_5 = self._io.read_u1()
            self.lengthcheck = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def reserve_cmd_counter(self):
            if hasattr(self, '_m_reserve_cmd_counter'):
                return self._m_reserve_cmd_counter

            if self.type_id == 1:
                self._m_reserve_cmd_counter = ((self.byte_4 & 14) >> 1)

            return getattr(self, '_m_reserve_cmd_counter', None)

        @property
        def batt_heater(self):
            if hasattr(self, '_m_batt_heater'):
                return self._m_batt_heater

            if self.type_id == 0:
                self._m_batt_heater = ((self.byte_4 & 8) >> 3)

            return getattr(self, '_m_batt_heater', None)

        @property
        def byte_3_hex_left(self):
            if hasattr(self, '_m_byte_3_hex_left'):
                return self._m_byte_3_hex_left

            self._m_byte_3_hex_left = self.byte_3 // 16
            return getattr(self, '_m_byte_3_hex_left', None)

        @property
        def reset_raw_v_mon(self):
            if hasattr(self, '_m_reset_raw_v_mon'):
                return self._m_reset_raw_v_mon

            if self.type_id == 1:
                self._m_reset_raw_v_mon = (self.byte_2 & 1)

            return getattr(self, '_m_reset_raw_v_mon', None)

        @property
        def lcl_uhf_com(self):
            if hasattr(self, '_m_lcl_uhf_com'):
                return self._m_lcl_uhf_com

            if self.type_id == 1:
                self._m_lcl_uhf_com = ((self.byte_2 & 2) >> 1)

            return getattr(self, '_m_lcl_uhf_com', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.lengthcheck) != 0:
                self._m_necessary_for_lengthcheck = int(self.lengthcheck) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)

        @property
        def lcl_fab(self):
            if hasattr(self, '_m_lcl_fab'):
                return self._m_lcl_fab

            if self.type_id == 1:
                self._m_lcl_fab = ((self.byte_2 & 64) >> 6)

            return getattr(self, '_m_lcl_fab', None)

        @property
        def lcl_5v0(self):
            if hasattr(self, '_m_lcl_5v0'):
                return self._m_lcl_5v0

            if self.type_id == 1:
                self._m_lcl_5v0 = ((self.byte_2 & 4) >> 2)

            return getattr(self, '_m_lcl_5v0', None)

        @property
        def byte_4_hex_right_digit(self):
            if hasattr(self, '_m_byte_4_hex_right_digit'):
                return self._m_byte_4_hex_right_digit

            self._m_byte_4_hex_right_digit = (u"a" if str(self.byte_4_hex_right) == u"10" else (u"b" if str(self.byte_4_hex_right) == u"11" else (u"c" if str(self.byte_4_hex_right) == u"12" else (u"d" if str(self.byte_4_hex_right) == u"13" else (u"e" if str(self.byte_4_hex_right) == u"14" else (u"f" if str(self.byte_4_hex_right) == u"15" else str(self.byte_4_hex_right)))))))
            return getattr(self, '_m_byte_4_hex_right_digit', None)

        @property
        def ad_counter(self):
            if hasattr(self, '_m_ad_counter'):
                return self._m_ad_counter

            if self.type_id == 0:
                self._m_ad_counter = ((self.byte_4 & 6) >> 1)

            return getattr(self, '_m_ad_counter', None)

        @property
        def sap_minus_y(self):
            if hasattr(self, '_m_sap_minus_y'):
                return self._m_sap_minus_y

            if self.type_id == 0:
                self._m_sap_minus_y = (self.byte_5 & 1)

            return getattr(self, '_m_sap_minus_y', None)

        @property
        def byte_3_hex_right_digit(self):
            if hasattr(self, '_m_byte_3_hex_right_digit'):
                return self._m_byte_3_hex_right_digit

            self._m_byte_3_hex_right_digit = (u"a" if str(self.byte_3_hex_right) == u"10" else (u"b" if str(self.byte_3_hex_right) == u"11" else (u"c" if str(self.byte_3_hex_right) == u"12" else (u"d" if str(self.byte_3_hex_right) == u"13" else (u"e" if str(self.byte_3_hex_right) == u"14" else (u"f" if str(self.byte_3_hex_right) == u"15" else str(self.byte_3_hex_right)))))))
            return getattr(self, '_m_byte_3_hex_right_digit', None)

        @property
        def byte_1_hex_right(self):
            if hasattr(self, '_m_byte_1_hex_right'):
                return self._m_byte_1_hex_right

            self._m_byte_1_hex_right = (self.byte_1 % 16)
            return getattr(self, '_m_byte_1_hex_right', None)

        @property
        def batt_t(self):
            if hasattr(self, '_m_batt_t'):
                return self._m_batt_t

            if self.type_id == 0:
                self._m_batt_t = self.byte_3

            return getattr(self, '_m_batt_t', None)

        @property
        def byte_1_hex_left_digit(self):
            if hasattr(self, '_m_byte_1_hex_left_digit'):
                return self._m_byte_1_hex_left_digit

            self._m_byte_1_hex_left_digit = (u"a" if str(self.byte_1_hex_left) == u"10" else (u"b" if str(self.byte_1_hex_left) == u"11" else (u"c" if str(self.byte_1_hex_left) == u"12" else (u"d" if str(self.byte_1_hex_left) == u"13" else (u"e" if str(self.byte_1_hex_left) == u"14" else (u"f" if str(self.byte_1_hex_left) == u"15" else str(self.byte_1_hex_left)))))))
            return getattr(self, '_m_byte_1_hex_left_digit', None)

        @property
        def byte_3_hex(self):
            if hasattr(self, '_m_byte_3_hex'):
                return self._m_byte_3_hex

            self._m_byte_3_hex = self.byte_3_hex_left_digit + self.byte_3_hex_right_digit
            return getattr(self, '_m_byte_3_hex', None)

        @property
        def byte_5_hex_left_digit(self):
            if hasattr(self, '_m_byte_5_hex_left_digit'):
                return self._m_byte_5_hex_left_digit

            self._m_byte_5_hex_left_digit = (u"a" if str(self.byte_5_hex_left) == u"10" else (u"b" if str(self.byte_5_hex_left) == u"11" else (u"c" if str(self.byte_5_hex_left) == u"12" else (u"d" if str(self.byte_5_hex_left) == u"13" else (u"e" if str(self.byte_5_hex_left) == u"14" else (u"f" if str(self.byte_5_hex_left) == u"15" else str(self.byte_5_hex_left)))))))
            return getattr(self, '_m_byte_5_hex_left_digit', None)

        @property
        def byte_5_hex(self):
            if hasattr(self, '_m_byte_5_hex'):
                return self._m_byte_5_hex

            self._m_byte_5_hex = self.byte_5_hex_left_digit + self.byte_5_hex_right_digit
            return getattr(self, '_m_byte_5_hex', None)

        @property
        def byte_2_hex_left(self):
            if hasattr(self, '_m_byte_2_hex_left'):
                return self._m_byte_2_hex_left

            self._m_byte_2_hex_left = self.byte_2 // 16
            return getattr(self, '_m_byte_2_hex_left', None)

        @property
        def bpb_t(self):
            if hasattr(self, '_m_bpb_t'):
                return self._m_bpb_t

            if self.type_id == 1:
                self._m_bpb_t = self.byte_5

            return getattr(self, '_m_bpb_t', None)

        @property
        def lcl_depant(self):
            if hasattr(self, '_m_lcl_depant'):
                return self._m_lcl_depant

            if self.type_id == 1:
                self._m_lcl_depant = ((self.byte_2 & 16) >> 4)

            return getattr(self, '_m_lcl_depant', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"CW" if 0 == 0 else u"CW")
            return getattr(self, '_m_beacon_type', None)

        @property
        def byte_2_hex_right(self):
            if hasattr(self, '_m_byte_2_hex_right'):
                return self._m_byte_2_hex_right

            self._m_byte_2_hex_right = (self.byte_2 % 16)
            return getattr(self, '_m_byte_2_hex_right', None)

        @property
        def byte_1_hex_left(self):
            if hasattr(self, '_m_byte_1_hex_left'):
                return self._m_byte_1_hex_left

            self._m_byte_1_hex_left = self.byte_1 // 16
            return getattr(self, '_m_byte_1_hex_left', None)

        @property
        def byte_5_hex_right(self):
            if hasattr(self, '_m_byte_5_hex_right'):
                return self._m_byte_5_hex_right

            self._m_byte_5_hex_right = (self.byte_5 % 16)
            return getattr(self, '_m_byte_5_hex_right', None)

        @property
        def byte_1_hex_right_digit(self):
            if hasattr(self, '_m_byte_1_hex_right_digit'):
                return self._m_byte_1_hex_right_digit

            self._m_byte_1_hex_right_digit = (u"a" if str(self.byte_1_hex_right) == u"10" else (u"b" if str(self.byte_1_hex_right) == u"11" else (u"c" if str(self.byte_1_hex_right) == u"12" else (u"d" if str(self.byte_1_hex_right) == u"13" else (u"e" if str(self.byte_1_hex_right) == u"14" else (u"f" if str(self.byte_1_hex_right) == u"15" else str(self.byte_1_hex_right)))))))
            return getattr(self, '_m_byte_1_hex_right_digit', None)

        @property
        def byte_3_hex_right(self):
            if hasattr(self, '_m_byte_3_hex_right'):
                return self._m_byte_3_hex_right

            self._m_byte_3_hex_right = (self.byte_3 % 16)
            return getattr(self, '_m_byte_3_hex_right', None)

        @property
        def byte_2_hex_right_digit(self):
            if hasattr(self, '_m_byte_2_hex_right_digit'):
                return self._m_byte_2_hex_right_digit

            self._m_byte_2_hex_right_digit = (u"a" if str(self.byte_2_hex_right) == u"10" else (u"b" if str(self.byte_2_hex_right) == u"11" else (u"c" if str(self.byte_2_hex_right) == u"12" else (u"d" if str(self.byte_2_hex_right) == u"13" else (u"e" if str(self.byte_2_hex_right) == u"14" else (u"f" if str(self.byte_2_hex_right) == u"15" else str(self.byte_2_hex_right)))))))
            return getattr(self, '_m_byte_2_hex_right_digit', None)

        @property
        def byte_4_hex_left_digit(self):
            if hasattr(self, '_m_byte_4_hex_left_digit'):
                return self._m_byte_4_hex_left_digit

            self._m_byte_4_hex_left_digit = (u"a" if str(self.byte_4_hex_left) == u"10" else (u"b" if str(self.byte_4_hex_left) == u"11" else (u"c" if str(self.byte_4_hex_left) == u"12" else (u"d" if str(self.byte_4_hex_left) == u"13" else (u"e" if str(self.byte_4_hex_left) == u"14" else (u"f" if str(self.byte_4_hex_left) == u"15" else str(self.byte_4_hex_left)))))))
            return getattr(self, '_m_byte_4_hex_left_digit', None)

        @property
        def byte_4_hex(self):
            if hasattr(self, '_m_byte_4_hex'):
                return self._m_byte_4_hex

            self._m_byte_4_hex = self.byte_4_hex_left_digit + self.byte_4_hex_right_digit
            return getattr(self, '_m_byte_4_hex', None)

        @property
        def batt_v(self):
            if hasattr(self, '_m_batt_v'):
                return self._m_batt_v

            if self.type_id == 0:
                self._m_batt_v = self.byte_1

            return getattr(self, '_m_batt_v', None)

        @property
        def sap_minus_z(self):
            if hasattr(self, '_m_sap_minus_z'):
                return self._m_sap_minus_z

            if self.type_id == 0:
                self._m_sap_minus_z = ((self.byte_5 & 4) >> 2)

            return getattr(self, '_m_sap_minus_z', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = self.byte_1_hex + u" " + self.byte_2_hex + u" " + self.byte_3_hex + u" " + self.byte_4_hex + u" " + self.byte_5_hex
            return getattr(self, '_m_cw_beacon', None)

        @property
        def byte_2_hex_left_digit(self):
            if hasattr(self, '_m_byte_2_hex_left_digit'):
                return self._m_byte_2_hex_left_digit

            self._m_byte_2_hex_left_digit = (u"a" if str(self.byte_2_hex_left) == u"10" else (u"b" if str(self.byte_2_hex_left) == u"11" else (u"c" if str(self.byte_2_hex_left) == u"12" else (u"d" if str(self.byte_2_hex_left) == u"13" else (u"e" if str(self.byte_2_hex_left) == u"14" else (u"f" if str(self.byte_2_hex_left) == u"15" else str(self.byte_2_hex_left)))))))
            return getattr(self, '_m_byte_2_hex_left_digit', None)

        @property
        def gmsk_cmd_counter(self):
            if hasattr(self, '_m_gmsk_cmd_counter'):
                return self._m_gmsk_cmd_counter

            if self.type_id == 1:
                self._m_gmsk_cmd_counter = ((self.byte_3 & 248) >> 3)

            return getattr(self, '_m_gmsk_cmd_counter', None)

        @property
        def lcl_compic(self):
            if hasattr(self, '_m_lcl_compic'):
                return self._m_lcl_compic

            if self.type_id == 1:
                self._m_lcl_compic = ((self.byte_3 & 2) >> 1)

            return getattr(self, '_m_lcl_compic', None)

        @property
        def lcl_3v3_2(self):
            if hasattr(self, '_m_lcl_3v3_2'):
                return self._m_lcl_3v3_2

            if self.type_id == 1:
                self._m_lcl_3v3_2 = ((self.byte_2 & 32) >> 5)

            return getattr(self, '_m_lcl_3v3_2', None)

        @property
        def raw_i(self):
            if hasattr(self, '_m_raw_i'):
                return self._m_raw_i

            if self.type_id == 1:
                self._m_raw_i = self.byte_1

            return getattr(self, '_m_raw_i', None)

        @property
        def byte_4_hex_left(self):
            if hasattr(self, '_m_byte_4_hex_left'):
                return self._m_byte_4_hex_left

            self._m_byte_4_hex_left = self.byte_4 // 16
            return getattr(self, '_m_byte_4_hex_left', None)

        @property
        def lcl_mainpic(self):
            if hasattr(self, '_m_lcl_mainpic'):
                return self._m_lcl_mainpic

            if self.type_id == 1:
                self._m_lcl_mainpic = ((self.byte_3 & 4) >> 2)

            return getattr(self, '_m_lcl_mainpic', None)

        @property
        def dcdc_fab(self):
            if hasattr(self, '_m_dcdc_fab'):
                return self._m_dcdc_fab

            if self.type_id == 1:
                self._m_dcdc_fab = ((self.byte_2 & 8) >> 3)

            return getattr(self, '_m_dcdc_fab', None)

        @property
        def batt_i(self):
            if hasattr(self, '_m_batt_i'):
                return self._m_batt_i

            if self.type_id == 0:
                self._m_batt_i = self.byte_2

            return getattr(self, '_m_batt_i', None)

        @property
        def kill_counter(self):
            if hasattr(self, '_m_kill_counter'):
                return self._m_kill_counter

            if self.type_id == 1:
                self._m_kill_counter = ((self.byte_4 & 224) >> 5)

            return getattr(self, '_m_kill_counter', None)

        @property
        def kill_sw_main(self):
            if hasattr(self, '_m_kill_sw_main'):
                return self._m_kill_sw_main

            if self.type_id == 0:
                self._m_kill_sw_main = ((self.byte_4 & 16) >> 4)

            return getattr(self, '_m_kill_sw_main', None)

        @property
        def sap_plus_y(self):
            if hasattr(self, '_m_sap_plus_y'):
                return self._m_sap_plus_y

            if self.type_id == 0:
                self._m_sap_plus_y = ((self.byte_4 & 128) >> 7)

            return getattr(self, '_m_sap_plus_y', None)

        @property
        def byte_5_hex_right_digit(self):
            if hasattr(self, '_m_byte_5_hex_right_digit'):
                return self._m_byte_5_hex_right_digit

            self._m_byte_5_hex_right_digit = (u"a" if str(self.byte_5_hex_right) == u"10" else (u"b" if str(self.byte_5_hex_right) == u"11" else (u"c" if str(self.byte_5_hex_right) == u"12" else (u"d" if str(self.byte_5_hex_right) == u"13" else (u"e" if str(self.byte_5_hex_right) == u"14" else (u"f" if str(self.byte_5_hex_right) == u"15" else str(self.byte_5_hex_right)))))))
            return getattr(self, '_m_byte_5_hex_right_digit', None)

        @property
        def byte_3_hex_left_digit(self):
            if hasattr(self, '_m_byte_3_hex_left_digit'):
                return self._m_byte_3_hex_left_digit

            self._m_byte_3_hex_left_digit = (u"a" if str(self.byte_3_hex_left) == u"10" else (u"b" if str(self.byte_3_hex_left) == u"11" else (u"c" if str(self.byte_3_hex_left) == u"12" else (u"d" if str(self.byte_3_hex_left) == u"13" else (u"e" if str(self.byte_3_hex_left) == u"14" else (u"f" if str(self.byte_3_hex_left) == u"15" else str(self.byte_3_hex_left)))))))
            return getattr(self, '_m_byte_3_hex_left_digit', None)

        @property
        def type_id(self):
            if hasattr(self, '_m_type_id'):
                return self._m_type_id

            self._m_type_id = ((self.byte_4 & 128) >> 7)
            return getattr(self, '_m_type_id', None)

        @property
        def dcdc_3v3_2(self):
            if hasattr(self, '_m_dcdc_3v3_2'):
                return self._m_dcdc_3v3_2

            if self.type_id == 1:
                self._m_dcdc_3v3_2 = (self.byte_3 & 1)

            return getattr(self, '_m_dcdc_3v3_2', None)

        @property
        def dcdc_5v0(self):
            if hasattr(self, '_m_dcdc_5v0'):
                return self._m_dcdc_5v0

            if self.type_id == 1:
                self._m_dcdc_5v0 = ((self.byte_2 & 128) >> 7)

            return getattr(self, '_m_dcdc_5v0', None)

        @property
        def byte_2_hex(self):
            if hasattr(self, '_m_byte_2_hex'):
                return self._m_byte_2_hex

            self._m_byte_2_hex = self.byte_2_hex_left_digit + self.byte_2_hex_right_digit
            return getattr(self, '_m_byte_2_hex', None)

        @property
        def byte_4_hex_right(self):
            if hasattr(self, '_m_byte_4_hex_right'):
                return self._m_byte_4_hex_right

            self._m_byte_4_hex_right = (self.byte_4 % 16)
            return getattr(self, '_m_byte_4_hex_right', None)

        @property
        def kill_sw_fab(self):
            if hasattr(self, '_m_kill_sw_fab'):
                return self._m_kill_sw_fab

            if self.type_id == 0:
                self._m_kill_sw_fab = ((self.byte_4 & 32) >> 5)

            return getattr(self, '_m_kill_sw_fab', None)

        @property
        def time_after_reset(self):
            if hasattr(self, '_m_time_after_reset'):
                return self._m_time_after_reset

            if self.type_id == 0:
                self._m_time_after_reset = ((self.byte_5 & 248) >> 3)

            return getattr(self, '_m_time_after_reset', None)

        @property
        def sap_minus_x(self):
            if hasattr(self, '_m_sap_minus_x'):
                return self._m_sap_minus_x

            if self.type_id == 0:
                self._m_sap_minus_x = ((self.byte_4 & 64) >> 6)

            return getattr(self, '_m_sap_minus_x', None)

        @property
        def sap_plus_z(self):
            if hasattr(self, '_m_sap_plus_z'):
                return self._m_sap_plus_z

            if self.type_id == 0:
                self._m_sap_plus_z = ((self.byte_5 & 2) >> 1)

            return getattr(self, '_m_sap_plus_z', None)

        @property
        def uplink_success(self):
            if hasattr(self, '_m_uplink_success'):
                return self._m_uplink_success

            if self.type_id == 1:
                self._m_uplink_success = ((self.byte_4 & 16) >> 4)

            return getattr(self, '_m_uplink_success', None)

        @property
        def byte_5_hex_left(self):
            if hasattr(self, '_m_byte_5_hex_left'):
                return self._m_byte_5_hex_left

            self._m_byte_5_hex_left = self.byte_5 // 16
            return getattr(self, '_m_byte_5_hex_left', None)

        @property
        def byte_1_hex(self):
            if hasattr(self, '_m_byte_1_hex'):
                return self._m_byte_1_hex

            self._m_byte_1_hex = self.byte_1_hex_left_digit + self.byte_1_hex_right_digit
            return getattr(self, '_m_byte_1_hex', None)


    class Hk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_header_1 = (self._io.read_bytes(14)).decode(u"ASCII")
            if not self.hk_header_1 == u"JG6YBW0JG6YMX0":
                raise kaitaistruct.ValidationNotEqualError(u"JG6YBW0JG6YMX0", self.hk_header_1, self._io, u"/types/hk/seq/0")
            self.hk_header_2 = self._io.read_u8be()
            self.hk_header_3 = self._io.read_u2be()
            if not self.hk_header_3 == 13107:
                raise kaitaistruct.ValidationNotEqualError(13107, self.hk_header_3, self._io, u"/types/hk/seq/2")
            self.hk_seconds = self._io.read_u1()
            self.hk_minutes = self._io.read_u1()
            self.hk_hours = self._io.read_u1()
            self.hk_days = self._io.read_u2be()
            self.hk_delimiter_1 = self._io.read_bits_int_be(24)
            if not self.hk_delimiter_1 == 11184810:
                raise kaitaistruct.ValidationNotEqualError(11184810, self.hk_delimiter_1, self._io, u"/types/hk/seq/7")
            self._io.align_to_byte()
            self.hk_temp_plus_x = self._io.read_u2be()
            self.hk_temp_minus_x = self._io.read_u2be()
            self.hk_temp_plus_y = self._io.read_u2be()
            self.hk_temp_minus_y = self._io.read_u2be()
            self.hk_temp_plus_z = self._io.read_u2be()
            self.hk_temp_minus_z = self._io.read_u2be()
            self.hk_bpb_t = self._io.read_u2be()
            self.hk_voltage_minus_x = self._io.read_u2be()
            self.hk_voltage_plus_y = self._io.read_u2be()
            self.hk_voltage_minus_y = self._io.read_u2be()
            self.hk_voltage_plus_z = self._io.read_u2be()
            self.hk_voltage_minus_z = self._io.read_u2be()
            self.hk_current_minus_x = self._io.read_u1()
            self.hk_current_plus_y = self._io.read_u1()
            self.hk_current_minus_y = self._io.read_u1()
            self.hk_current_plus_z = self._io.read_u1()
            self.hk_current_minus_z = self._io.read_u1()
            self.hk_batt_t = self._io.read_u1()
            self.hk_batt_v = self._io.read_u1()
            self.hk_batt_i = self._io.read_u2be()
            self.hk_fab_raw_v = self._io.read_u1()
            self.hk_fab_raw_i = self._io.read_u1()
            self.hk_src_v = self._io.read_u1()
            self.hk_src_i = self._io.read_u2be()
            self.hk_heater_flag = self._io.read_u1()
            self.hk_kill_sw = self._io.read_u1()
            self.delimiter_2 = self._io.read_u1()
            if not self.delimiter_2 == 187:
                raise kaitaistruct.ValidationNotEqualError(187, self.delimiter_2, self._io, u"/types/hk/seq/34")
            self.hk_reset_raw_v = self._io.read_u1()
            self.hk_v3_3_no1_i = self._io.read_u1()
            self.hk_v3_3_no2_i = self._io.read_u1()
            self.hk_uhf_com_i = self._io.read_u1()
            self.hk_ant_dep_i = self._io.read_u1()
            self.hk_v5_i = self._io.read_u1()
            self.hk_reset_sw_status = self._io.read_u2be()
            self.delimiter_3 = self._io.read_u1()
            if not self.delimiter_3 == 204:
                raise kaitaistruct.ValidationNotEqualError(204, self.delimiter_3, self._io, u"/types/hk/seq/42")
            self.hk_reserve_cmd_0_cmd0 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd1 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd2 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd3 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd4 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd5 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd6 = self._io.read_u1()
            self.hk_reserve_cmd_0_cmd7 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd0 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd1 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd2 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd3 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd4 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd5 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd6 = self._io.read_u1()
            self.hk_reserve_cmd_1_cmd7 = self._io.read_u1()
            self.delimiter_4 = self._io.read_u4be()
            if not self.delimiter_4 == 1145324612:
                raise kaitaistruct.ValidationNotEqualError(1145324612, self.delimiter_4, self._io, u"/types/hk/seq/59")

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"HK" if 0 == 0 else u"HK")
            return getattr(self, '_m_beacon_type', None)


    class Aprs(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Yomogi.Aprs.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Yomogi.Aprs.Ax25Header(self._io, self, self._root)
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Yomogi.Aprs.Ax25InfoData(_io__raw_ax25_info, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Yomogi.Aprs.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Yomogi.Aprs.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Yomogi.Aprs.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Yomogi.Aprs.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Yomogi.Aprs.Repeater(self._io, self, self._root)

                self.ctl = self._io.read_u1()
                self.pid = self._io.read_u1()


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

                self._m_ssid = ((self.ssid_mask & 31) >> 1)
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
                self.rpt_callsign_raw = Yomogi.Aprs.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Yomogi.Aprs.SsidMask(self._io, self, self._root)


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
                    _ = Yomogi.Aprs.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Yomogi.Aprs.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.digi_message = (self._io.read_bytes_full()).decode(u"utf-8")


        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"DIGI" if 0 == 0 else u"DIGI")
            return getattr(self, '_m_beacon_type', None)



