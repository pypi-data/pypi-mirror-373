# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Cosmogirlsat(KaitaiStruct):
    """:field satellitename_and_callsign: cosmo.cw_or_digi.satellitename_and_callsign
    :field type_id: cosmo.cw_or_digi.type_id
    :field battery_voltage_v: cosmo.cw_or_digi.battery_voltage_v
    :field battery_current_ma: cosmo.cw_or_digi.battery_current_ma
    :field battery_temperature_c: cosmo.cw_or_digi.battery_temperature_c
    :field operation_modes: cosmo.cw_or_digi.operation_modes
    :field kill_switch_main: cosmo.cw_or_digi.kill_switch_main
    :field kill_switch_fab: cosmo.cw_or_digi.kill_switch_fab
    :field antenna_deploy_status: cosmo.cw_or_digi.antenna_deploy_status
    :field solar_cell_plus_y: cosmo.cw_or_digi.solar_cell_plus_y
    :field solar_cell_plus_x: cosmo.cw_or_digi.solar_cell_plus_x
    :field solar_cell_minus_z: cosmo.cw_or_digi.solar_cell_minus_z
    :field solar_cell_minus_x: cosmo.cw_or_digi.solar_cell_minus_x
    :field solar_cell_plus_z: cosmo.cw_or_digi.solar_cell_plus_z
    :field hours_after_last_reset: cosmo.cw_or_digi.hours_after_last_reset
    :field gyro_x: cosmo.cw_or_digi.gyro_x
    :field gyro_y: cosmo.cw_or_digi.gyro_y
    :field gyro_z: cosmo.cw_or_digi.gyro_z
    :field hssc_automatical_trial: cosmo.cw_or_digi.hssc_automatical_trial
    :field com_to_main_flag: cosmo.cw_or_digi.com_to_main_flag
    :field reset_to_main_flag: cosmo.cw_or_digi.reset_to_main_flag
    :field fab_to_main_flag: cosmo.cw_or_digi.fab_to_main_flag
    :field battery_heater: cosmo.cw_or_digi.battery_heater
    :field reservation_command: cosmo.cw_or_digi.reservation_command
    :field uplink_success: cosmo.cw_or_digi.uplink_success
    :field mission_satus: cosmo.cw_or_digi.mission_satus
    :field mission_operating_status: cosmo.cw_or_digi.mission_operating_status
    :field cw_beacon: cosmo.cw_or_digi.cw_beacon
    :field dest_callsign: cosmo.cw_or_digi.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: cosmo.cw_or_digi.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: cosmo.cw_or_digi.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: cosmo.cw_or_digi.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: cosmo.cw_or_digi.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: cosmo.cw_or_digi.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: cosmo.cw_or_digi.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field ctl: cosmo.cw_or_digi.ax25_frame.ax25_header.ctl
    :field pid: cosmo.cw_or_digi.ax25_frame.payload.pid
    :field monitor: cosmo.cw_or_digi.ax25_frame.payload.ax25_info.data_monitor
    
    .. seealso::
       Source - https://cosmosgirlham.org/communication/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.cosmo = Cosmogirlsat.CosmoT(self._io, self, self._root)

    class CosmoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.cw_or_digi_switch_on
            if _on == 7165072446023802986:
                self.cw_or_digi = Cosmogirlsat.Cw(self._io, self, self._root)
            else:
                self.cw_or_digi = Cosmogirlsat.Digi(self._io, self, self._root)

        @property
        def cw_or_digi_switch_on(self):
            if hasattr(self, '_m_cw_or_digi_switch_on'):
                return self._m_cw_or_digi_switch_on

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_cw_or_digi_switch_on = self._io.read_u8be()
            self._io.seek(_pos)
            return getattr(self, '_m_cw_or_digi_switch_on', None)


    class Cw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.satellitename_and_callsign = (self._io.read_bytes(21)).decode(u"ASCII")
            if not self.satellitename_and_callsign == u"cosmo0 js1yoi 000000 ":
                raise kaitaistruct.ValidationNotEqualError(u"cosmo0 js1yoi 000000 ", self.satellitename_and_callsign, self._io, u"/types/cw/seq/0")
            self.byte_1 = self._io.read_u1()
            self.byte_2 = self._io.read_u1()
            self.byte_3 = self._io.read_u1()
            self.byte_4 = self._io.read_u1()
            self.byte_5 = self._io.read_u1()

        @property
        def byte_3_hex_left(self):
            if hasattr(self, '_m_byte_3_hex_left'):
                return self._m_byte_3_hex_left

            self._m_byte_3_hex_left = self.byte_3 // 16
            return getattr(self, '_m_byte_3_hex_left', None)

        @property
        def gyro_y(self):
            if hasattr(self, '_m_gyro_y'):
                return self._m_gyro_y

            if self.type_id == 1:
                self._m_gyro_y = self.byte_2

            return getattr(self, '_m_gyro_y', None)

        @property
        def byte_4_hex_right_digit(self):
            if hasattr(self, '_m_byte_4_hex_right_digit'):
                return self._m_byte_4_hex_right_digit

            self._m_byte_4_hex_right_digit = (u"a" if str(self.byte_4_hex_right) == u"10" else (u"b" if str(self.byte_4_hex_right) == u"11" else (u"c" if str(self.byte_4_hex_right) == u"12" else (u"d" if str(self.byte_4_hex_right) == u"13" else (u"e" if str(self.byte_4_hex_right) == u"14" else (u"f" if str(self.byte_4_hex_right) == u"15" else str(self.byte_4_hex_right)))))))
            return getattr(self, '_m_byte_4_hex_right_digit', None)

        @property
        def battery_temperature_c(self):
            if hasattr(self, '_m_battery_temperature_c'):
                return self._m_battery_temperature_c

            if self.type_id == 0:
                self._m_battery_temperature_c = self.byte_3

            return getattr(self, '_m_battery_temperature_c', None)

        @property
        def mission_operating_status(self):
            if hasattr(self, '_m_mission_operating_status'):
                return self._m_mission_operating_status

            if self.type_id == 1:
                self._m_mission_operating_status = (self.byte_5 & 15)

            return getattr(self, '_m_mission_operating_status', None)

        @property
        def kill_switch_fab(self):
            if hasattr(self, '_m_kill_switch_fab'):
                return self._m_kill_switch_fab

            if self.type_id == 0:
                self._m_kill_switch_fab = ((self.byte_4 & 8) >> 3)

            return getattr(self, '_m_kill_switch_fab', None)

        @property
        def byte_3_hex_right_digit(self):
            if hasattr(self, '_m_byte_3_hex_right_digit'):
                return self._m_byte_3_hex_right_digit

            self._m_byte_3_hex_right_digit = (u"a" if str(self.byte_3_hex_right) == u"10" else (u"b" if str(self.byte_3_hex_right) == u"11" else (u"c" if str(self.byte_3_hex_right) == u"12" else (u"d" if str(self.byte_3_hex_right) == u"13" else (u"e" if str(self.byte_3_hex_right) == u"14" else (u"f" if str(self.byte_3_hex_right) == u"15" else str(self.byte_3_hex_right)))))))
            return getattr(self, '_m_byte_3_hex_right_digit', None)

        @property
        def reservation_command(self):
            if hasattr(self, '_m_reservation_command'):
                return self._m_reservation_command

            if self.type_id == 1:
                self._m_reservation_command = ((self.byte_4 & 2) >> 1)

            return getattr(self, '_m_reservation_command', None)

        @property
        def solar_cell_plus_y(self):
            if hasattr(self, '_m_solar_cell_plus_y'):
                return self._m_solar_cell_plus_y

            if self.type_id == 0:
                self._m_solar_cell_plus_y = ((self.byte_4 & 2) >> 1)

            return getattr(self, '_m_solar_cell_plus_y', None)

        @property
        def byte_1_hex_right(self):
            if hasattr(self, '_m_byte_1_hex_right'):
                return self._m_byte_1_hex_right

            self._m_byte_1_hex_right = (self.byte_1 % 16)
            return getattr(self, '_m_byte_1_hex_right', None)

        @property
        def operation_modes(self):
            if hasattr(self, '_m_operation_modes'):
                return self._m_operation_modes

            if self.type_id == 0:
                self._m_operation_modes = ((self.byte_4 & 96) >> 5)

            return getattr(self, '_m_operation_modes', None)

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
        def gyro_x(self):
            if hasattr(self, '_m_gyro_x'):
                return self._m_gyro_x

            if self.type_id == 1:
                self._m_gyro_x = self.byte_1

            return getattr(self, '_m_gyro_x', None)

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
        def gyro_z(self):
            if hasattr(self, '_m_gyro_z'):
                return self._m_gyro_z

            if self.type_id == 1:
                self._m_gyro_z = self.byte_3

            return getattr(self, '_m_gyro_z', None)

        @property
        def byte_3_hex_right(self):
            if hasattr(self, '_m_byte_3_hex_right'):
                return self._m_byte_3_hex_right

            self._m_byte_3_hex_right = (self.byte_3 % 16)
            return getattr(self, '_m_byte_3_hex_right', None)

        @property
        def solar_cell_plus_z(self):
            if hasattr(self, '_m_solar_cell_plus_z'):
                return self._m_solar_cell_plus_z

            if self.type_id == 0:
                self._m_solar_cell_plus_z = ((self.byte_5 & 32) >> 5)

            return getattr(self, '_m_solar_cell_plus_z', None)

        @property
        def solar_cell_minus_x(self):
            if hasattr(self, '_m_solar_cell_minus_x'):
                return self._m_solar_cell_minus_x

            if self.type_id == 0:
                self._m_solar_cell_minus_x = ((self.byte_5 & 64) >> 6)

            return getattr(self, '_m_solar_cell_minus_x', None)

        @property
        def mission_satus(self):
            if hasattr(self, '_m_mission_satus'):
                return self._m_mission_satus

            if self.type_id == 1:
                self._m_mission_satus = ((self.byte_5 & 240) >> 4)

            return getattr(self, '_m_mission_satus', None)

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
        def hours_after_last_reset(self):
            if hasattr(self, '_m_hours_after_last_reset'):
                return self._m_hours_after_last_reset

            if self.type_id == 0:
                self._m_hours_after_last_reset = (self.byte_5 & 31)

            return getattr(self, '_m_hours_after_last_reset', None)

        @property
        def hssc_automatical_trial(self):
            if hasattr(self, '_m_hssc_automatical_trial'):
                return self._m_hssc_automatical_trial

            if self.type_id == 1:
                self._m_hssc_automatical_trial = ((self.byte_4 & 64) >> 6)

            return getattr(self, '_m_hssc_automatical_trial', None)

        @property
        def fab_to_main_flag(self):
            if hasattr(self, '_m_fab_to_main_flag'):
                return self._m_fab_to_main_flag

            if self.type_id == 1:
                self._m_fab_to_main_flag = ((self.byte_4 & 8) >> 3)

            return getattr(self, '_m_fab_to_main_flag', None)

        @property
        def battery_voltage_v(self):
            if hasattr(self, '_m_battery_voltage_v'):
                return self._m_battery_voltage_v

            if self.type_id == 0:
                self._m_battery_voltage_v = self.byte_1

            return getattr(self, '_m_battery_voltage_v', None)

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
        def kill_switch_main(self):
            if hasattr(self, '_m_kill_switch_main'):
                return self._m_kill_switch_main

            if self.type_id == 0:
                self._m_kill_switch_main = ((self.byte_4 & 16) >> 4)

            return getattr(self, '_m_kill_switch_main', None)

        @property
        def byte_4_hex_left(self):
            if hasattr(self, '_m_byte_4_hex_left'):
                return self._m_byte_4_hex_left

            self._m_byte_4_hex_left = self.byte_4 // 16
            return getattr(self, '_m_byte_4_hex_left', None)

        @property
        def solar_cell_plus_x(self):
            if hasattr(self, '_m_solar_cell_plus_x'):
                return self._m_solar_cell_plus_x

            if self.type_id == 0:
                self._m_solar_cell_plus_x = (self.byte_4 & 1)

            return getattr(self, '_m_solar_cell_plus_x', None)

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
        def reset_to_main_flag(self):
            if hasattr(self, '_m_reset_to_main_flag'):
                return self._m_reset_to_main_flag

            if self.type_id == 1:
                self._m_reset_to_main_flag = ((self.byte_4 & 16) >> 4)

            return getattr(self, '_m_reset_to_main_flag', None)

        @property
        def solar_cell_minus_z(self):
            if hasattr(self, '_m_solar_cell_minus_z'):
                return self._m_solar_cell_minus_z

            if self.type_id == 0:
                self._m_solar_cell_minus_z = ((self.byte_5 & 128) >> 7)

            return getattr(self, '_m_solar_cell_minus_z', None)

        @property
        def battery_current_ma(self):
            if hasattr(self, '_m_battery_current_ma'):
                return self._m_battery_current_ma

            if self.type_id == 0:
                self._m_battery_current_ma = self.byte_2

            return getattr(self, '_m_battery_current_ma', None)

        @property
        def byte_2_hex(self):
            if hasattr(self, '_m_byte_2_hex'):
                return self._m_byte_2_hex

            self._m_byte_2_hex = self.byte_2_hex_left_digit + self.byte_2_hex_right_digit
            return getattr(self, '_m_byte_2_hex', None)

        @property
        def battery_heater(self):
            if hasattr(self, '_m_battery_heater'):
                return self._m_battery_heater

            if self.type_id == 1:
                self._m_battery_heater = ((self.byte_4 & 4) >> 2)

            return getattr(self, '_m_battery_heater', None)

        @property
        def byte_4_hex_right(self):
            if hasattr(self, '_m_byte_4_hex_right'):
                return self._m_byte_4_hex_right

            self._m_byte_4_hex_right = (self.byte_4 % 16)
            return getattr(self, '_m_byte_4_hex_right', None)

        @property
        def com_to_main_flag(self):
            if hasattr(self, '_m_com_to_main_flag'):
                return self._m_com_to_main_flag

            if self.type_id == 1:
                self._m_com_to_main_flag = ((self.byte_4 & 32) >> 5)

            return getattr(self, '_m_com_to_main_flag', None)

        @property
        def uplink_success(self):
            if hasattr(self, '_m_uplink_success'):
                return self._m_uplink_success

            if self.type_id == 1:
                self._m_uplink_success = (self.byte_4 & 1)

            return getattr(self, '_m_uplink_success', None)

        @property
        def antenna_deploy_status(self):
            if hasattr(self, '_m_antenna_deploy_status'):
                return self._m_antenna_deploy_status

            if self.type_id == 0:
                self._m_antenna_deploy_status = ((self.byte_4 & 4) >> 2)

            return getattr(self, '_m_antenna_deploy_status', None)

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


    class Digi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Cosmogirlsat.Digi.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Cosmogirlsat.Digi.Ax25Header(self._io, self, self._root)
                _on = (self.ax25_header.ctl & 19)
                if _on == 0:
                    self.payload = Cosmogirlsat.Digi.IFrame(self._io, self, self._root)
                elif _on == 3:
                    self.payload = Cosmogirlsat.Digi.UiFrame(self._io, self, self._root)
                elif _on == 19:
                    self.payload = Cosmogirlsat.Digi.UiFrame(self._io, self, self._root)
                elif _on == 16:
                    self.payload = Cosmogirlsat.Digi.IFrame(self._io, self, self._root)
                elif _on == 18:
                    self.payload = Cosmogirlsat.Digi.IFrame(self._io, self, self._root)
                elif _on == 2:
                    self.payload = Cosmogirlsat.Digi.IFrame(self._io, self, self._root)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Cosmogirlsat.Digi.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Cosmogirlsat.Digi.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Cosmogirlsat.Digi.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Cosmogirlsat.Digi.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Cosmogirlsat.Digi.Repeater(self._io, self, self._root)

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
                self.ax25_info = Cosmogirlsat.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.ax25_info = Cosmogirlsat.Digi.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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
                self.rpt_callsign_raw = Cosmogirlsat.Digi.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Cosmogirlsat.Digi.SsidMask(self._io, self, self._root)


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
                    _ = Cosmogirlsat.Digi.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Cosmogirlsat.Digi.Callsign(_io__raw_callsign_ror, self, self._root)


        class Ax25InfoData(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.data_monitor = (self._io.read_bytes_full()).decode(u"utf-8")




