# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sanosat1(KaitaiStruct):
    """:field callsign: sanosat1_telemetry.body.callsign
    :field packet_type: sanosat1_telemetry.body.packet_type
    :field com_temperature: sanosat1_telemetry.body.com_temperature
    :field battery_voltage: sanosat1_telemetry.body.battery_voltage
    :field charging_current: sanosat1_telemetry.body.charging_current
    :field battery_temperature: sanosat1_telemetry.body.battery_temperature
    :field radiation_level: sanosat1_telemetry.body.radiation_level
    :field no_of_resets: sanosat1_telemetry.body.no_of_resets
    :field antenna_deployment_status: sanosat1_telemetry.body.antenna_deployment_status
    :field beacon_type: sanosat1_telemetry.body.beacon_type
    :field digimessage: sanosat1_telemetry.body.decision.digimessage
    :field cwmessage: sanosat1_telemetry.body.decision.cwmessage
    :field com_temperature: sanosat1_telemetry.body.decision.com_temperature
    :field battery_temperature: sanosat1_telemetry.body.decision.battery_temperature
    :field charging_current: sanosat1_telemetry.body.decision.charging_current
    :field battery_voltage: sanosat1_telemetry.body.decision.battery_voltage
    :field antenna_deployment_status: sanosat1_telemetry.body.decision.antenna_deployment_status
    :field beacon_type: sanosat1_telemetry.body.decision.beacon_type
    :field callsign: sanosat1_telemetry.body.decision.callsign
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.sanosat1_telemetry = Sanosat1.Sanosat1TelemetryT(self._io, self, self._root)

    class WithDelimiter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.delimiter = self._io.read_s4le()
            if not  ((self.delimiter == 65535)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.delimiter, self._io, u"/types/with_delimiter/seq/0")
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(7), 0, False)).decode(u"ASCII")
            if not  ((self.callsign == u"AM9NPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/with_delimiter/seq/1")
            self.packet_type = self._io.read_s2le()
            self.com_temperature = self._io.read_s2le()
            self.battery_voltage = self._io.read_s2le()
            self.charging_current = self._io.read_s2le()
            self.battery_temperature = self._io.read_s2le()
            self.radiation_level = self._io.read_s2le()
            self.no_of_resets = self._io.read_s2le()
            self.antenna_deployment_status = self._io.read_u1()

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"GFSK" if 0 == 0 else u"GFSK")
            return getattr(self, '_m_beacon_type', None)


    class Rtty(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes_term(44, False, True, True)).decode(u"ASCII")
            if not  ((self.callsign == u"AM9NPQ") or (self.callsign == u"am9npq")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/rtty/seq/0")
            self.skip_dollar = self._io.read_s1()
            self.battery_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.charging_current_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.battery_voltage_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"UTF-8")
            self.battery_voltage_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.no_of_resets_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.antenna_deployment_status_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.radiation_level_raw = (self._io.read_bytes_term(63, False, True, True)).decode(u"UTF-8")
            self.checksum_rtty_raw = (self._io.read_bytes(2)).decode(u"UTF-8")
            if not  ((self.checksum_rtty_raw == self.checksum_compare)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.checksum_rtty_raw, self._io, u"/types/rtty/seq/9")

        @property
        def battery_temperature(self):
            if hasattr(self, '_m_battery_temperature'):
                return self._m_battery_temperature

            self._m_battery_temperature = int(self.battery_temperature_raw)
            return getattr(self, '_m_battery_temperature', None)

        @property
        def checksum_battery_temperature_2(self):
            if hasattr(self, '_m_checksum_battery_temperature_2'):
                return self._m_checksum_battery_temperature_2

            self._m_checksum_battery_temperature_2 = (0 if (self.battery_temperature_raw)[2:3] == u"" else (int((self.battery_temperature_raw)[2:3], 16) + 48))
            return getattr(self, '_m_checksum_battery_temperature_2', None)

        @property
        def battery_voltage_before_dot(self):
            if hasattr(self, '_m_battery_voltage_before_dot'):
                return self._m_battery_voltage_before_dot

            self._m_battery_voltage_before_dot = int(self.battery_voltage_before_dot_raw)
            return getattr(self, '_m_battery_voltage_before_dot', None)

        @property
        def checksum_battery_voltage_before_dot(self):
            if hasattr(self, '_m_checksum_battery_voltage_before_dot'):
                return self._m_checksum_battery_voltage_before_dot

            self._m_checksum_battery_voltage_before_dot = (int(self.battery_voltage_before_dot_raw, 16) + 48)
            return getattr(self, '_m_checksum_battery_voltage_before_dot', None)

        @property
        def battery_voltage_after_dot(self):
            if hasattr(self, '_m_battery_voltage_after_dot'):
                return self._m_battery_voltage_after_dot

            self._m_battery_voltage_after_dot = int(self.battery_voltage_after_dot_raw)
            return getattr(self, '_m_battery_voltage_after_dot', None)

        @property
        def battery_voltage(self):
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage

            self._m_battery_voltage = (self.battery_voltage_after_dot + (self.battery_voltage_before_dot * 100))
            return getattr(self, '_m_battery_voltage', None)

        @property
        def checksum_compare(self):
            if hasattr(self, '_m_checksum_compare'):
                return self._m_checksum_compare

            self._m_checksum_compare = (self.checksum_rtty_raw if self.checksum_calculation == int(self.checksum_rtty_raw, 16) else u"checksum invalid")
            return getattr(self, '_m_checksum_compare', None)

        @property
        def radiation_level(self):
            if hasattr(self, '_m_radiation_level'):
                return self._m_radiation_level

            self._m_radiation_level = int(self.radiation_level_raw)
            return getattr(self, '_m_radiation_level', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"RTTY" if 0 == 0 else u"RTTY")
            return getattr(self, '_m_beacon_type', None)

        @property
        def checksum_no_of_resets_raw_1(self):
            if hasattr(self, '_m_checksum_no_of_resets_raw_1'):
                return self._m_checksum_no_of_resets_raw_1

            self._m_checksum_no_of_resets_raw_1 = (0 if (self.no_of_resets_raw)[1:2] == u"" else (int((self.no_of_resets_raw)[1:2], 16) + 48))
            return getattr(self, '_m_checksum_no_of_resets_raw_1', None)

        @property
        def checksum_charging_current_0(self):
            if hasattr(self, '_m_checksum_charging_current_0'):
                return self._m_checksum_charging_current_0

            self._m_checksum_charging_current_0 = (int((self.charging_current_raw)[0:1], 16) + 48)
            return getattr(self, '_m_checksum_charging_current_0', None)

        @property
        def checksum_no_of_resets_raw_0(self):
            if hasattr(self, '_m_checksum_no_of_resets_raw_0'):
                return self._m_checksum_no_of_resets_raw_0

            self._m_checksum_no_of_resets_raw_0 = (int((self.no_of_resets_raw)[0:1], 16) + 48)
            return getattr(self, '_m_checksum_no_of_resets_raw_0', None)

        @property
        def checksum_radiation_level_raw_1(self):
            if hasattr(self, '_m_checksum_radiation_level_raw_1'):
                return self._m_checksum_radiation_level_raw_1

            self._m_checksum_radiation_level_raw_1 = (0 if (self.radiation_level_raw)[1:2] == u"" else (int((self.radiation_level_raw)[1:2], 16) + 48))
            return getattr(self, '_m_checksum_radiation_level_raw_1', None)

        @property
        def charging_current(self):
            if hasattr(self, '_m_charging_current'):
                return self._m_charging_current

            self._m_charging_current = int(self.charging_current_raw)
            return getattr(self, '_m_charging_current', None)

        @property
        def checksum_battery_voltage_after_dot_1(self):
            if hasattr(self, '_m_checksum_battery_voltage_after_dot_1'):
                return self._m_checksum_battery_voltage_after_dot_1

            self._m_checksum_battery_voltage_after_dot_1 = (int((self.battery_voltage_after_dot_raw)[1:2], 16) + 48)
            return getattr(self, '_m_checksum_battery_voltage_after_dot_1', None)

        @property
        def checksum_five_commata_and_one_dot(self):
            if hasattr(self, '_m_checksum_five_commata_and_one_dot'):
                return self._m_checksum_five_commata_and_one_dot

            self._m_checksum_five_commata_and_one_dot = 2
            return getattr(self, '_m_checksum_five_commata_and_one_dot', None)

        @property
        def checksum_radiation_level_raw_0(self):
            if hasattr(self, '_m_checksum_radiation_level_raw_0'):
                return self._m_checksum_radiation_level_raw_0

            self._m_checksum_radiation_level_raw_0 = (int((self.radiation_level_raw)[0:1], 16) + 48)
            return getattr(self, '_m_checksum_radiation_level_raw_0', None)

        @property
        def checksum_charging_current_2(self):
            if hasattr(self, '_m_checksum_charging_current_2'):
                return self._m_checksum_charging_current_2

            self._m_checksum_charging_current_2 = (0 if (self.charging_current_raw)[2:3] == u"" else (int((self.charging_current_raw)[2:3], 16) + 48))
            return getattr(self, '_m_checksum_charging_current_2', None)

        @property
        def checksum_charging_current_1(self):
            if hasattr(self, '_m_checksum_charging_current_1'):
                return self._m_checksum_charging_current_1

            self._m_checksum_charging_current_1 = (0 if (self.charging_current_raw)[1:2] == u"" else (int((self.charging_current_raw)[1:2], 16) + 48))
            return getattr(self, '_m_checksum_charging_current_1', None)

        @property
        def checksum_calculation(self):
            if hasattr(self, '_m_checksum_calculation'):
                return self._m_checksum_calculation

            self._m_checksum_calculation = (((((((((((((((((self.checksum_battery_temperature_0 ^ self.checksum_battery_temperature_1) ^ self.checksum_battery_temperature_2) ^ self.checksum_battery_temperature_3) ^ self.checksum_charging_current_0) ^ self.checksum_charging_current_1) ^ self.checksum_charging_current_2) ^ self.checksum_battery_voltage_before_dot) ^ self.checksum_battery_voltage_after_dot_0) ^ self.checksum_battery_voltage_after_dot_1) ^ self.checksum_no_of_resets_raw_0) ^ self.checksum_no_of_resets_raw_1) ^ self.checksum_no_of_resets_raw_2) ^ self.checksum_antenna_deployment_status_raw) ^ self.checksum_radiation_level_raw_0) ^ self.checksum_radiation_level_raw_1) ^ self.checksum_radiation_level_raw_2) ^ self.checksum_five_commata_and_one_dot)
            return getattr(self, '_m_checksum_calculation', None)

        @property
        def antenna_deployment_status(self):
            if hasattr(self, '_m_antenna_deployment_status'):
                return self._m_antenna_deployment_status

            self._m_antenna_deployment_status = int(self.antenna_deployment_status_raw)
            return getattr(self, '_m_antenna_deployment_status', None)

        @property
        def checksum_radiation_level_raw_2(self):
            if hasattr(self, '_m_checksum_radiation_level_raw_2'):
                return self._m_checksum_radiation_level_raw_2

            self._m_checksum_radiation_level_raw_2 = (0 if (self.radiation_level_raw)[2:3] == u"" else (int((self.radiation_level_raw)[2:3], 16) + 48))
            return getattr(self, '_m_checksum_radiation_level_raw_2', None)

        @property
        def no_of_resets(self):
            if hasattr(self, '_m_no_of_resets'):
                return self._m_no_of_resets

            self._m_no_of_resets = int(self.no_of_resets_raw)
            return getattr(self, '_m_no_of_resets', None)

        @property
        def checksum_battery_voltage_after_dot_0(self):
            if hasattr(self, '_m_checksum_battery_voltage_after_dot_0'):
                return self._m_checksum_battery_voltage_after_dot_0

            self._m_checksum_battery_voltage_after_dot_0 = (int((self.battery_voltage_after_dot_raw)[0:1], 16) + 48)
            return getattr(self, '_m_checksum_battery_voltage_after_dot_0', None)

        @property
        def checksum_battery_temperature_1(self):
            if hasattr(self, '_m_checksum_battery_temperature_1'):
                return self._m_checksum_battery_temperature_1

            self._m_checksum_battery_temperature_1 = (0 if (self.battery_temperature_raw)[1:2] == u"" else (int((self.battery_temperature_raw)[1:2], 16) + 48))
            return getattr(self, '_m_checksum_battery_temperature_1', None)

        @property
        def checksum_antenna_deployment_status_raw(self):
            if hasattr(self, '_m_checksum_antenna_deployment_status_raw'):
                return self._m_checksum_antenna_deployment_status_raw

            self._m_checksum_antenna_deployment_status_raw = (int((self.antenna_deployment_status_raw)[0:1], 16) + 48)
            return getattr(self, '_m_checksum_antenna_deployment_status_raw', None)

        @property
        def checksum_no_of_resets_raw_2(self):
            if hasattr(self, '_m_checksum_no_of_resets_raw_2'):
                return self._m_checksum_no_of_resets_raw_2

            self._m_checksum_no_of_resets_raw_2 = (0 if (self.no_of_resets_raw)[2:3] == u"" else (int((self.no_of_resets_raw)[2:3], 16) + 48))
            return getattr(self, '_m_checksum_no_of_resets_raw_2', None)

        @property
        def checksum_battery_temperature_3(self):
            if hasattr(self, '_m_checksum_battery_temperature_3'):
                return self._m_checksum_battery_temperature_3

            self._m_checksum_battery_temperature_3 = (0 if (self.battery_temperature_raw)[3:4] == u"" else (int((self.battery_temperature_raw)[3:4], 16) + 48))
            return getattr(self, '_m_checksum_battery_temperature_3', None)

        @property
        def checksum_battery_temperature_0(self):
            if hasattr(self, '_m_checksum_battery_temperature_0'):
                return self._m_checksum_battery_temperature_0

            self._m_checksum_battery_temperature_0 = (45 if (self.battery_temperature_raw)[0:1] == u"-" else (int((self.battery_temperature_raw)[0:1], 16) + 48))
            return getattr(self, '_m_checksum_battery_temperature_0', None)


    class DecisionDigiOrCw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 65535:
                self.decision = Sanosat1.DigiWithDelimiter(self._io, self, self._root)
            elif _on == 19777:
                self.decision = Sanosat1.Cw(self._io, self, self._root)
            elif _on == 28001:
                self.decision = Sanosat1.Cw(self._io, self, self._root)
            else:
                self.decision = Sanosat1.DigiWithoutDelimiter(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_check = self._io.read_u2le()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class WithoutDelimiter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(7), 0, False)).decode(u"ASCII")
            if not  ((self.callsign == u"AM9NPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/without_delimiter/seq/0")
            self.packet_type = self._io.read_s2le()
            self.com_temperature = self._io.read_s2le()
            self.battery_voltage = self._io.read_s2le()
            self.charging_current = self._io.read_s2le()
            self.battery_temperature = self._io.read_s2le()
            self.radiation_level = self._io.read_s2le()
            self.no_of_resets = self._io.read_s2le()
            self.antenna_deployment_status = self._io.read_u1()

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"GFSK" if 0 == 0 else u"GFSK")
            return getattr(self, '_m_beacon_type', None)


    class DigiWithoutDelimiter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = (self._io.read_bytes(3)).decode(u"ASCII")
            if not  ((self.header == u"NPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header, self._io, u"/types/digi_without_delimiter/seq/0")
            self.digimessage = (self._io.read_bytes_full()).decode(u"UTF-8")

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"DIGI" if 0 == 0 else u"DIGI")
            return getattr(self, '_m_beacon_type', None)


    class Cw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"AM9NPQ") or (self.callsign == u"am9npq")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/cw/seq/0")
            self.cwmessage = (self._io.read_bytes_term(63, False, True, True)).decode(u"UTF-8")
            self.checksum_cw_raw = (self._io.read_bytes(2)).decode(u"UTF-8")
            if not  ((self.checksum_cw_raw == self.checksum_compare)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.checksum_cw_raw, self._io, u"/types/cw/seq/2")

        @property
        def calc_checksum_cw_9(self):
            if hasattr(self, '_m_calc_checksum_cw_9'):
                return self._m_calc_checksum_cw_9

            self._m_calc_checksum_cw_9 = (0 if (self.cwmessage)[9:10] == u"" else ((int((self.cwmessage)[9:10], 16) + 48) if int((self.cwmessage)[9:10], 16) < 10 else (int((self.cwmessage)[9:10], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_9', None)

        @property
        def battery_temperature(self):
            if hasattr(self, '_m_battery_temperature'):
                return self._m_battery_temperature

            self._m_battery_temperature = ((int((self.cwmessage)[self.length_of_obc_temp:(self.length_of_obc_temp + self.length_of_bat_temp)]) * -1) if self.sign_of_bat_temp == u"-" else int((self.cwmessage)[self.length_of_obc_temp:(self.length_of_obc_temp + self.length_of_bat_temp)]))
            return getattr(self, '_m_battery_temperature', None)

        @property
        def residuals(self):
            if hasattr(self, '_m_residuals'):
                return self._m_residuals

            self._m_residuals = int((self.cwmessage)[(len(self.cwmessage) - 2):len(self.cwmessage)], 16)
            return getattr(self, '_m_residuals', None)

        @property
        def calc_checksum_cw_6(self):
            if hasattr(self, '_m_calc_checksum_cw_6'):
                return self._m_calc_checksum_cw_6

            self._m_calc_checksum_cw_6 = ((int((self.cwmessage)[6:7], 16) + 48) if int((self.cwmessage)[6:7], 16) < 10 else (int((self.cwmessage)[6:7], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_6', None)

        @property
        def battery_voltage(self):
            if hasattr(self, '_m_battery_voltage'):
                return self._m_battery_voltage

            self._m_battery_voltage = (int((self.cwmessage)[((self.length_of_obc_temp + self.length_of_bat_temp) + self.length_of_current):(((self.length_of_obc_temp + self.length_of_bat_temp) + self.length_of_current) + 2)]) * 10)
            return getattr(self, '_m_battery_voltage', None)

        @property
        def calc_checksum_cw_1(self):
            if hasattr(self, '_m_calc_checksum_cw_1'):
                return self._m_calc_checksum_cw_1

            self._m_calc_checksum_cw_1 = ((int((self.cwmessage)[1:2], 16) + 48) if int((self.cwmessage)[1:2], 16) < 10 else (int((self.cwmessage)[1:2], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_1', None)

        @property
        def checksum_compare(self):
            if hasattr(self, '_m_checksum_compare'):
                return self._m_checksum_compare

            self._m_checksum_compare = (self.checksum_cw_raw if self.checksum_calculation == int(self.checksum_cw_raw, 16) else u"checksum invalid")
            return getattr(self, '_m_checksum_compare', None)

        @property
        def sign_of_obc_temp(self):
            if hasattr(self, '_m_sign_of_obc_temp'):
                return self._m_sign_of_obc_temp

            self._m_sign_of_obc_temp = (u"+" if ((self.residuals & 64) >> 6) == 0 else u"-")
            return getattr(self, '_m_sign_of_obc_temp', None)

        @property
        def calc_checksum_cw_4(self):
            if hasattr(self, '_m_calc_checksum_cw_4'):
                return self._m_calc_checksum_cw_4

            self._m_calc_checksum_cw_4 = ((int((self.cwmessage)[4:5], 16) + 48) if int((self.cwmessage)[4:5], 16) < 10 else (int((self.cwmessage)[4:5], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_4', None)

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"CW" if 0 == 0 else u"CW")
            return getattr(self, '_m_beacon_type', None)

        @property
        def calc_checksum_cw_3(self):
            if hasattr(self, '_m_calc_checksum_cw_3'):
                return self._m_calc_checksum_cw_3

            self._m_calc_checksum_cw_3 = ((int((self.cwmessage)[3:4], 16) + 48) if int((self.cwmessage)[3:4], 16) < 10 else (int((self.cwmessage)[3:4], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_3', None)

        @property
        def calc_checksum_cw_5(self):
            if hasattr(self, '_m_calc_checksum_cw_5'):
                return self._m_calc_checksum_cw_5

            self._m_calc_checksum_cw_5 = ((int((self.cwmessage)[5:6], 16) + 48) if int((self.cwmessage)[5:6], 16) < 10 else (int((self.cwmessage)[5:6], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_5', None)

        @property
        def calc_checksum_cw_7(self):
            if hasattr(self, '_m_calc_checksum_cw_7'):
                return self._m_calc_checksum_cw_7

            self._m_calc_checksum_cw_7 = (0 if (self.cwmessage)[7:8] == u"" else ((int((self.cwmessage)[7:8], 16) + 48) if int((self.cwmessage)[7:8], 16) < 10 else (int((self.cwmessage)[7:8], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_7', None)

        @property
        def calc_checksum_cw_11(self):
            if hasattr(self, '_m_calc_checksum_cw_11'):
                return self._m_calc_checksum_cw_11

            self._m_calc_checksum_cw_11 = (0 if (self.cwmessage)[11:12] == u"" else ((int((self.cwmessage)[11:12], 16) + 48) if int((self.cwmessage)[11:12], 16) < 10 else (int((self.cwmessage)[11:12], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_11', None)

        @property
        def calc_checksum_cw_2(self):
            if hasattr(self, '_m_calc_checksum_cw_2'):
                return self._m_calc_checksum_cw_2

            self._m_calc_checksum_cw_2 = ((int((self.cwmessage)[2:3], 16) + 48) if int((self.cwmessage)[2:3], 16) < 10 else (int((self.cwmessage)[2:3], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_2', None)

        @property
        def length_of_obc_temp(self):
            if hasattr(self, '_m_length_of_obc_temp'):
                return self._m_length_of_obc_temp

            self._m_length_of_obc_temp = (((len(self.cwmessage) - 4) - self.length_of_current) - self.length_of_bat_temp)
            return getattr(self, '_m_length_of_obc_temp', None)

        @property
        def charging_current(self):
            if hasattr(self, '_m_charging_current'):
                return self._m_charging_current

            self._m_charging_current = int((self.cwmessage)[(self.length_of_obc_temp + self.length_of_bat_temp):((self.length_of_obc_temp + self.length_of_bat_temp) + self.length_of_current)])
            return getattr(self, '_m_charging_current', None)

        @property
        def calc_checksum_cw_10(self):
            if hasattr(self, '_m_calc_checksum_cw_10'):
                return self._m_calc_checksum_cw_10

            self._m_calc_checksum_cw_10 = (0 if (self.cwmessage)[10:11] == u"" else ((int((self.cwmessage)[10:11], 16) + 48) if int((self.cwmessage)[10:11], 16) < 10 else (int((self.cwmessage)[10:11], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_10', None)

        @property
        def length_of_bat_temp(self):
            if hasattr(self, '_m_length_of_bat_temp'):
                return self._m_length_of_bat_temp

            self._m_length_of_bat_temp = ((self.residuals & 3) >> 0)
            return getattr(self, '_m_length_of_bat_temp', None)

        @property
        def checksum_calculation(self):
            if hasattr(self, '_m_checksum_calculation'):
                return self._m_checksum_calculation

            self._m_checksum_calculation = ((((((((((((self.calc_checksum_cw_0 ^ self.calc_checksum_cw_1) ^ self.calc_checksum_cw_2) ^ self.calc_checksum_cw_3) ^ self.calc_checksum_cw_4) ^ self.calc_checksum_cw_5) ^ self.calc_checksum_cw_6) ^ self.calc_checksum_cw_7) ^ self.calc_checksum_cw_8) ^ self.calc_checksum_cw_9) ^ self.calc_checksum_cw_10) ^ self.calc_checksum_cw_11) ^ self.calc_checksum_cw_12)
            return getattr(self, '_m_checksum_calculation', None)

        @property
        def antenna_deployment_status(self):
            if hasattr(self, '_m_antenna_deployment_status'):
                return self._m_antenna_deployment_status

            self._m_antenna_deployment_status = (1 if ((self.residuals & 128) >> 7) == 1 else 0)
            return getattr(self, '_m_antenna_deployment_status', None)

        @property
        def calc_checksum_cw_12(self):
            if hasattr(self, '_m_calc_checksum_cw_12'):
                return self._m_calc_checksum_cw_12

            self._m_calc_checksum_cw_12 = (0 if (self.cwmessage)[12:13] == u"" else ((int((self.cwmessage)[12:13], 16) + 48) if int((self.cwmessage)[12:13], 16) < 10 else (int((self.cwmessage)[12:13], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_12', None)

        @property
        def length_of_current(self):
            if hasattr(self, '_m_length_of_current'):
                return self._m_length_of_current

            self._m_length_of_current = ((self.residuals & 28) >> 2)
            return getattr(self, '_m_length_of_current', None)

        @property
        def sign_of_bat_temp(self):
            if hasattr(self, '_m_sign_of_bat_temp'):
                return self._m_sign_of_bat_temp

            self._m_sign_of_bat_temp = (u"+" if ((self.residuals & 32) >> 5) == 0 else u"-")
            return getattr(self, '_m_sign_of_bat_temp', None)

        @property
        def calc_checksum_cw_8(self):
            if hasattr(self, '_m_calc_checksum_cw_8'):
                return self._m_calc_checksum_cw_8

            self._m_calc_checksum_cw_8 = (0 if (self.cwmessage)[8:9] == u"" else ((int((self.cwmessage)[8:9], 16) + 48) if int((self.cwmessage)[8:9], 16) < 10 else (int((self.cwmessage)[8:9], 16) + 87)))
            return getattr(self, '_m_calc_checksum_cw_8', None)

        @property
        def com_temperature(self):
            if hasattr(self, '_m_com_temperature'):
                return self._m_com_temperature

            self._m_com_temperature = ((int((self.cwmessage)[0:self.length_of_obc_temp]) * -1) if self.sign_of_obc_temp == u"-" else int((self.cwmessage)[0:self.length_of_obc_temp]))
            return getattr(self, '_m_com_temperature', None)

        @property
        def calc_checksum_cw_0(self):
            if hasattr(self, '_m_calc_checksum_cw_0'):
                return self._m_calc_checksum_cw_0

            self._m_calc_checksum_cw_0 = ((int((self.cwmessage)[0:1], 16) + 48) if int((self.cwmessage)[0:1], 16) < 10 else (int((self.cwmessage)[0:1], 16) + 87))
            return getattr(self, '_m_calc_checksum_cw_0', None)


    class Sanosat1TelemetryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 2606547689692286273:
                self.body = Sanosat1.Rtty(self._io, self, self._root)
            elif _on == 2606583012040207713:
                self.body = Sanosat1.Rtty(self._io, self, self._root)
            elif _on == 5636621350199164927:
                self.body = Sanosat1.WithDelimiter(self._io, self, self._root)
            elif _on == 72146999389539649:
                self.body = Sanosat1.WithoutDelimiter(self._io, self, self._root)
            else:
                self.body = Sanosat1.DecisionDigiOrCw(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_check = self._io.read_u8le()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class DigiWithDelimiter(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.delimiter = self._io.read_s4le()
            if not  ((self.delimiter == 65535)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.delimiter, self._io, u"/types/digi_with_delimiter/seq/0")
            self.header = (self._io.read_bytes(3)).decode(u"ASCII")
            if not  ((self.header == u"NPQ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.header, self._io, u"/types/digi_with_delimiter/seq/1")
            self.digimessage = (self._io.read_bytes_full()).decode(u"UTF-8")

        @property
        def beacon_type(self):
            if hasattr(self, '_m_beacon_type'):
                return self._m_beacon_type

            self._m_beacon_type = (u"DIGI" if 0 == 0 else u"DIGI")
            return getattr(self, '_m_beacon_type', None)



