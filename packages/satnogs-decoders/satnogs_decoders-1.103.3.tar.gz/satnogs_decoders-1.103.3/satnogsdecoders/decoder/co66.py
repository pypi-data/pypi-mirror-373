# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Co66(KaitaiStruct):
    """:field whole_beacon_ascii: mode.mode_check.whole_beacon_ascii
    :field beacon_mode: mode.mode_check.beacon_mode
    :field satellite_time: mode.mode_check.satellite_time
    :field batteries_voltage: mode.mode_check.batteries_voltage
    :field bus_voltage: mode.mode_check.bus_voltage
    :field solar_cell_1_current: mode.mode_check.solar_cell_1_current
    :field solar_cell_2_current: mode.mode_check.solar_cell_2_current
    :field solar_cell_3_current: mode.mode_check.solar_cell_3_current
    :field solar_cell_4_current: mode.mode_check.solar_cell_4_current
    :field solar_cell_5_current: mode.mode_check.solar_cell_5_current
    :field solar_cell_6_current: mode.mode_check.solar_cell_6_current
    :field battery_1_temperature: mode.mode_check.battery_1_temperature
    :field battery_2_temperature: mode.mode_check.battery_2_temperature
    :field transmitter_temperature: mode.mode_check.transmitter_temperature
    :field receiver_temperature: mode.mode_check.receiver_temperature
    :field cw_transmission_interval: mode.mode_check.cw_transmission_interval
    :field status_of_switch_1: mode.mode_check.status_of_switch_1
    :field status_of_switch_2: mode.mode_check.status_of_switch_2
    :field status_of_switch_3: mode.mode_check.status_of_switch_3
    :field mpu_reset_times_eps: mode.mode_check.mpu_reset_times_eps
    :field mpu_reset_times_fmr: mode.mode_check.mpu_reset_times_fmr
    :field mpu_reset_times_cdh: mode.mode_check.mpu_reset_times_cdh
    :field mpu_reset_times_cw: mode.mode_check.mpu_reset_times_cw
    :field cw_transmission_count: mode.mode_check.cw_transmission_count
    :field uplink_count: mode.mode_check.uplink_count
    :field command_status: mode.mode_check.command_status
    :field forced_no_charge_mode: mode.mode_check.forced_no_charge_mode
    :field mode_of_shunt_circuit: mode.mode_check.mode_of_shunt_circuit
    :field status_of_shunt_circuit: mode.mode_check.status_of_shunt_circuit
    :field address_block: mode.mode_check.address_block
    :field necessary_for_lengthcheck: mode.mode_check.necessary_for_lengthcheck
    
    .. seealso::
       Source - https://web.archive.org/web/20100215214032/http://cubesat.aero.cst.nihon-u.ac.jp/image/telemetry/CW_e/CW_Telemetry_Format_For_SEEDS_English.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.preamble = (self._io.read_bytes(5)).decode(u"ASCII")
        if not self.preamble == u"seeds":
            raise kaitaistruct.ValidationNotEqualError(u"seeds", self.preamble, self._io, u"/seq/0")
        self.mode = Co66.ModeT(self._io, self, self._root)

    class Four(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.whole_beacon_ascii = (self._io.read_bytes(72)).decode(u"utf-8")
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = 4
            return getattr(self, '_m_beacon_mode', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.discard) != 0:
                self._m_necessary_for_lengthcheck = int(self.discard) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)

        @property
        def solar_cell_3_current(self):
            if hasattr(self, '_m_solar_cell_3_current'):
                return self._m_solar_cell_3_current

            if  (((self.whole_beacon_ascii)[20:21] != u"*") and ((self.whole_beacon_ascii)[21:22] != u"*") and ((self.whole_beacon_ascii)[22:23] != u"*")) :
                self._m_solar_cell_3_current = (((5.0 * int((self.whole_beacon_ascii)[20:23], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_3_current', None)

        @property
        def solar_cell_5_current(self):
            if hasattr(self, '_m_solar_cell_5_current'):
                return self._m_solar_cell_5_current

            if  (((self.whole_beacon_ascii)[26:27] != u"*") and ((self.whole_beacon_ascii)[27:28] != u"*") and ((self.whole_beacon_ascii)[28:29] != u"*")) :
                self._m_solar_cell_5_current = (((5.0 * int((self.whole_beacon_ascii)[26:29], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_5_current', None)

        @property
        def command_status(self):
            if hasattr(self, '_m_command_status'):
                return self._m_command_status

            if  (((self.whole_beacon_ascii)[68:69] != u"*") and ((self.whole_beacon_ascii)[69:70] != u"*")) :
                self._m_command_status = int((self.whole_beacon_ascii)[68:70], 16)

            return getattr(self, '_m_command_status', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            if  (((self.whole_beacon_ascii)[0:1] != u"*") and ((self.whole_beacon_ascii)[1:2] != u"*") and ((self.whole_beacon_ascii)[2:3] != u"*") and ((self.whole_beacon_ascii)[3:4] != u"*") and ((self.whole_beacon_ascii)[4:5] != u"*") and ((self.whole_beacon_ascii)[5:6] != u"*") and ((self.whole_beacon_ascii)[6:7] != u"*") and ((self.whole_beacon_ascii)[7:8] != u"*")) :
                self._m_satellite_time = int((self.whole_beacon_ascii)[0:8], 16) // 2

            return getattr(self, '_m_satellite_time', None)

        @property
        def receiver_temperature(self):
            if hasattr(self, '_m_receiver_temperature'):
                return self._m_receiver_temperature

            if  (((self.whole_beacon_ascii)[41:42] != u"*") and ((self.whole_beacon_ascii)[42:43] != u"*") and ((self.whole_beacon_ascii)[43:44] != u"*")) :
                self._m_receiver_temperature = (((-0.062626 * (((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096))) - (38.305 * ((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096))) + 126.89)

            return getattr(self, '_m_receiver_temperature', None)

        @property
        def status_of_switch_2(self):
            if hasattr(self, '_m_status_of_switch_2'):
                return self._m_status_of_switch_2

            if (self.whole_beacon_ascii)[45:46] != u"*":
                self._m_status_of_switch_2 = ((int((self.whole_beacon_ascii)[45:46], 16) >> 1) & 1)

            return getattr(self, '_m_status_of_switch_2', None)

        @property
        def solar_cell_4_current(self):
            if hasattr(self, '_m_solar_cell_4_current'):
                return self._m_solar_cell_4_current

            if  (((self.whole_beacon_ascii)[23:24] != u"*") and ((self.whole_beacon_ascii)[24:25] != u"*") and ((self.whole_beacon_ascii)[25:26] != u"*")) :
                self._m_solar_cell_4_current = (((5.0 * int((self.whole_beacon_ascii)[23:26], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_4_current', None)

        @property
        def solar_cell_6_current(self):
            if hasattr(self, '_m_solar_cell_6_current'):
                return self._m_solar_cell_6_current

            if  (((self.whole_beacon_ascii)[29:30] != u"*") and ((self.whole_beacon_ascii)[30:31] != u"*") and ((self.whole_beacon_ascii)[31:32] != u"*")) :
                self._m_solar_cell_6_current = (((5.0 * int((self.whole_beacon_ascii)[29:32], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_6_current', None)

        @property
        def cw_transmission_count(self):
            if hasattr(self, '_m_cw_transmission_count'):
                return self._m_cw_transmission_count

            if  (((self.whole_beacon_ascii)[62:63] != u"*") and ((self.whole_beacon_ascii)[63:64] != u"*") and ((self.whole_beacon_ascii)[64:65] != u"*") and ((self.whole_beacon_ascii)[65:66] != u"*")) :
                self._m_cw_transmission_count = int((self.whole_beacon_ascii)[62:66], 16)

            return getattr(self, '_m_cw_transmission_count', None)

        @property
        def mode_of_shunt_circuit(self):
            if hasattr(self, '_m_mode_of_shunt_circuit'):
                return self._m_mode_of_shunt_circuit

            if (self.whole_beacon_ascii)[71:72] != u"*":
                self._m_mode_of_shunt_circuit = (int((self.whole_beacon_ascii)[71:72], 16) & 3)

            return getattr(self, '_m_mode_of_shunt_circuit', None)

        @property
        def mpu_reset_times_eps(self):
            if hasattr(self, '_m_mpu_reset_times_eps'):
                return self._m_mpu_reset_times_eps

            if  (((self.whole_beacon_ascii)[46:47] != u"*") and ((self.whole_beacon_ascii)[47:48] != u"*") and ((self.whole_beacon_ascii)[48:49] != u"*") and ((self.whole_beacon_ascii)[49:50] != u"*")) :
                self._m_mpu_reset_times_eps = int((self.whole_beacon_ascii)[46:50], 16)

            return getattr(self, '_m_mpu_reset_times_eps', None)

        @property
        def uplink_count(self):
            if hasattr(self, '_m_uplink_count'):
                return self._m_uplink_count

            if  (((self.whole_beacon_ascii)[66:67] != u"*") and ((self.whole_beacon_ascii)[67:68] != u"*")) :
                self._m_uplink_count = int((self.whole_beacon_ascii)[66:68], 16)

            return getattr(self, '_m_uplink_count', None)

        @property
        def forced_no_charge_mode(self):
            if hasattr(self, '_m_forced_no_charge_mode'):
                return self._m_forced_no_charge_mode

            if (self.whole_beacon_ascii)[70:71] != u"*":
                self._m_forced_no_charge_mode = (int((self.whole_beacon_ascii)[70:71], 16) >> 3)

            return getattr(self, '_m_forced_no_charge_mode', None)

        @property
        def cw_transmission_interval(self):
            if hasattr(self, '_m_cw_transmission_interval'):
                return self._m_cw_transmission_interval

            if (self.whole_beacon_ascii)[44:45] != u"*":
                self._m_cw_transmission_interval = (int((self.whole_beacon_ascii)[44:45], 16) * 3)

            return getattr(self, '_m_cw_transmission_interval', None)

        @property
        def batteries_voltage(self):
            if hasattr(self, '_m_batteries_voltage'):
                return self._m_batteries_voltage

            if  (((self.whole_beacon_ascii)[8:9] != u"*") and ((self.whole_beacon_ascii)[9:10] != u"*") and ((self.whole_beacon_ascii)[10:11] != u"*")) :
                self._m_batteries_voltage = ((5.0 * int((self.whole_beacon_ascii)[8:11], 16)) / 4096)

            return getattr(self, '_m_batteries_voltage', None)

        @property
        def transmitter_temperature(self):
            if hasattr(self, '_m_transmitter_temperature'):
                return self._m_transmitter_temperature

            if  (((self.whole_beacon_ascii)[38:39] != u"*") and ((self.whole_beacon_ascii)[39:40] != u"*") and ((self.whole_beacon_ascii)[40:41] != u"*")) :
                self._m_transmitter_temperature = (((-0.38082 * (((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096))) - (36.125 * ((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096))) + 121.31)

            return getattr(self, '_m_transmitter_temperature', None)

        @property
        def mpu_reset_times_cdh(self):
            if hasattr(self, '_m_mpu_reset_times_cdh'):
                return self._m_mpu_reset_times_cdh

            if  (((self.whole_beacon_ascii)[54:55] != u"*") and ((self.whole_beacon_ascii)[55:56] != u"*") and ((self.whole_beacon_ascii)[56:57] != u"*") and ((self.whole_beacon_ascii)[57:58] != u"*")) :
                self._m_mpu_reset_times_cdh = int((self.whole_beacon_ascii)[54:58], 16)

            return getattr(self, '_m_mpu_reset_times_cdh', None)

        @property
        def mpu_reset_times_fmr(self):
            if hasattr(self, '_m_mpu_reset_times_fmr'):
                return self._m_mpu_reset_times_fmr

            if  (((self.whole_beacon_ascii)[50:51] != u"*") and ((self.whole_beacon_ascii)[51:52] != u"*") and ((self.whole_beacon_ascii)[52:53] != u"*") and ((self.whole_beacon_ascii)[53:54] != u"*")) :
                self._m_mpu_reset_times_fmr = int((self.whole_beacon_ascii)[50:54], 16)

            return getattr(self, '_m_mpu_reset_times_fmr', None)

        @property
        def status_of_switch_3(self):
            if hasattr(self, '_m_status_of_switch_3'):
                return self._m_status_of_switch_3

            if (self.whole_beacon_ascii)[45:46] != u"*":
                self._m_status_of_switch_3 = ((int((self.whole_beacon_ascii)[45:46], 16) >> 2) & 1)

            return getattr(self, '_m_status_of_switch_3', None)

        @property
        def mpu_reset_times_cw(self):
            if hasattr(self, '_m_mpu_reset_times_cw'):
                return self._m_mpu_reset_times_cw

            if  (((self.whole_beacon_ascii)[58:59] != u"*") and ((self.whole_beacon_ascii)[59:60] != u"*") and ((self.whole_beacon_ascii)[60:61] != u"*") and ((self.whole_beacon_ascii)[61:62] != u"*")) :
                self._m_mpu_reset_times_cw = int((self.whole_beacon_ascii)[58:62], 16)

            return getattr(self, '_m_mpu_reset_times_cw', None)

        @property
        def solar_cell_1_current(self):
            if hasattr(self, '_m_solar_cell_1_current'):
                return self._m_solar_cell_1_current

            if  (((self.whole_beacon_ascii)[14:15] != u"*") and ((self.whole_beacon_ascii)[15:16] != u"*") and ((self.whole_beacon_ascii)[16:17] != u"*")) :
                self._m_solar_cell_1_current = (((5.0 * int((self.whole_beacon_ascii)[14:17], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_1_current', None)

        @property
        def status_of_shunt_circuit(self):
            if hasattr(self, '_m_status_of_shunt_circuit'):
                return self._m_status_of_shunt_circuit

            if (self.whole_beacon_ascii)[71:72] != u"*":
                self._m_status_of_shunt_circuit = ((int((self.whole_beacon_ascii)[71:72], 16) >> 2) & 1)

            return getattr(self, '_m_status_of_shunt_circuit', None)

        @property
        def bus_voltage(self):
            if hasattr(self, '_m_bus_voltage'):
                return self._m_bus_voltage

            if  (((self.whole_beacon_ascii)[11:12] != u"*") and ((self.whole_beacon_ascii)[12:13] != u"*") and ((self.whole_beacon_ascii)[13:14] != u"*")) :
                self._m_bus_voltage = ((5.0 * int((self.whole_beacon_ascii)[11:14], 16)) / 4096)

            return getattr(self, '_m_bus_voltage', None)

        @property
        def battery_1_temperature(self):
            if hasattr(self, '_m_battery_1_temperature'):
                return self._m_battery_1_temperature

            if  (((self.whole_beacon_ascii)[32:33] != u"*") and ((self.whole_beacon_ascii)[33:34] != u"*") and ((self.whole_beacon_ascii)[34:35] != u"*")) :
                self._m_battery_1_temperature = (((0.15797 * (((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096))) - (39.553 * ((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096))) + 129.59)

            return getattr(self, '_m_battery_1_temperature', None)

        @property
        def battery_2_temperature(self):
            if hasattr(self, '_m_battery_2_temperature'):
                return self._m_battery_2_temperature

            if  (((self.whole_beacon_ascii)[35:36] != u"*") and ((self.whole_beacon_ascii)[36:37] != u"*") and ((self.whole_beacon_ascii)[37:38] != u"*")) :
                self._m_battery_2_temperature = (((0.18923 * (((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096))) - (39.27 * ((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096))) + 128.33)

            return getattr(self, '_m_battery_2_temperature', None)

        @property
        def status_of_switch_1(self):
            if hasattr(self, '_m_status_of_switch_1'):
                return self._m_status_of_switch_1

            if (self.whole_beacon_ascii)[45:46] != u"*":
                self._m_status_of_switch_1 = (int((self.whole_beacon_ascii)[45:46], 16) & 1)

            return getattr(self, '_m_status_of_switch_1', None)

        @property
        def solar_cell_2_current(self):
            if hasattr(self, '_m_solar_cell_2_current'):
                return self._m_solar_cell_2_current

            if  (((self.whole_beacon_ascii)[17:18] != u"*") and ((self.whole_beacon_ascii)[18:19] != u"*") and ((self.whole_beacon_ascii)[19:20] != u"*")) :
                self._m_solar_cell_2_current = (((5.0 * int((self.whole_beacon_ascii)[17:20], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_2_current', None)


    class Three(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.whole_beacon_ascii = (self._io.read_bytes(48)).decode(u"utf-8")
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = 3
            return getattr(self, '_m_beacon_mode', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.discard) != 0:
                self._m_necessary_for_lengthcheck = int(self.discard) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)

        @property
        def solar_cell_3_current(self):
            if hasattr(self, '_m_solar_cell_3_current'):
                return self._m_solar_cell_3_current

            if  (((self.whole_beacon_ascii)[18:19] != u"*") and ((self.whole_beacon_ascii)[19:20] != u"*") and ((self.whole_beacon_ascii)[20:21] != u"*")) :
                self._m_solar_cell_3_current = (((5.0 * int((self.whole_beacon_ascii)[18:21], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_3_current', None)

        @property
        def solar_cell_5_current(self):
            if hasattr(self, '_m_solar_cell_5_current'):
                return self._m_solar_cell_5_current

            if  (((self.whole_beacon_ascii)[24:25] != u"*") and ((self.whole_beacon_ascii)[25:26] != u"*") and ((self.whole_beacon_ascii)[26:27] != u"*")) :
                self._m_solar_cell_5_current = (((5.0 * int((self.whole_beacon_ascii)[24:27], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_5_current', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            if  (((self.whole_beacon_ascii)[0:1] != u"*") and ((self.whole_beacon_ascii)[1:2] != u"*") and ((self.whole_beacon_ascii)[2:3] != u"*") and ((self.whole_beacon_ascii)[3:4] != u"*") and ((self.whole_beacon_ascii)[4:5] != u"*") and ((self.whole_beacon_ascii)[5:6] != u"*") and ((self.whole_beacon_ascii)[6:7] != u"*") and ((self.whole_beacon_ascii)[7:8] != u"*")) :
                self._m_satellite_time = int((self.whole_beacon_ascii)[0:8], 16) // 2

            return getattr(self, '_m_satellite_time', None)

        @property
        def receiver_temperature(self):
            if hasattr(self, '_m_receiver_temperature'):
                return self._m_receiver_temperature

            if  (((self.whole_beacon_ascii)[39:40] != u"*") and ((self.whole_beacon_ascii)[40:41] != u"*") and ((self.whole_beacon_ascii)[41:42] != u"*")) :
                self._m_receiver_temperature = (((-0.062626 * (((5.0 * int((self.whole_beacon_ascii)[39:42], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[39:42], 16)) / 4096))) - (38.305 * ((5.0 * int((self.whole_beacon_ascii)[39:42], 16)) / 4096))) + 126.89)

            return getattr(self, '_m_receiver_temperature', None)

        @property
        def solar_cell_4_current(self):
            if hasattr(self, '_m_solar_cell_4_current'):
                return self._m_solar_cell_4_current

            if  (((self.whole_beacon_ascii)[21:22] != u"*") and ((self.whole_beacon_ascii)[22:23] != u"*") and ((self.whole_beacon_ascii)[23:24] != u"*")) :
                self._m_solar_cell_4_current = (((5.0 * int((self.whole_beacon_ascii)[21:24], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_4_current', None)

        @property
        def solar_cell_6_current(self):
            if hasattr(self, '_m_solar_cell_6_current'):
                return self._m_solar_cell_6_current

            if  (((self.whole_beacon_ascii)[27:28] != u"*") and ((self.whole_beacon_ascii)[28:29] != u"*") and ((self.whole_beacon_ascii)[29:30] != u"*")) :
                self._m_solar_cell_6_current = (((5.0 * int((self.whole_beacon_ascii)[27:30], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_6_current', None)

        @property
        def batteries_voltage(self):
            if hasattr(self, '_m_batteries_voltage'):
                return self._m_batteries_voltage

            if  (((self.whole_beacon_ascii)[42:43] != u"*") and ((self.whole_beacon_ascii)[43:44] != u"*") and ((self.whole_beacon_ascii)[44:45] != u"*")) :
                self._m_batteries_voltage = ((5.0 * int((self.whole_beacon_ascii)[42:45], 16)) / 4096)

            return getattr(self, '_m_batteries_voltage', None)

        @property
        def transmitter_temperature(self):
            if hasattr(self, '_m_transmitter_temperature'):
                return self._m_transmitter_temperature

            if  (((self.whole_beacon_ascii)[36:37] != u"*") and ((self.whole_beacon_ascii)[37:38] != u"*") and ((self.whole_beacon_ascii)[38:39] != u"*")) :
                self._m_transmitter_temperature = (((-0.38082 * (((5.0 * int((self.whole_beacon_ascii)[36:39], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[36:39], 16)) / 4096))) - (36.125 * ((5.0 * int((self.whole_beacon_ascii)[36:39], 16)) / 4096))) + 121.31)

            return getattr(self, '_m_transmitter_temperature', None)

        @property
        def solar_cell_1_current(self):
            if hasattr(self, '_m_solar_cell_1_current'):
                return self._m_solar_cell_1_current

            if  (((self.whole_beacon_ascii)[12:13] != u"*") and ((self.whole_beacon_ascii)[13:14] != u"*") and ((self.whole_beacon_ascii)[14:115] != u"*")) :
                self._m_solar_cell_1_current = (((5.0 * int((self.whole_beacon_ascii)[12:15], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_1_current', None)

        @property
        def bus_voltage(self):
            if hasattr(self, '_m_bus_voltage'):
                return self._m_bus_voltage

            if  (((self.whole_beacon_ascii)[45:46] != u"*") and ((self.whole_beacon_ascii)[46:47] != u"*") and ((self.whole_beacon_ascii)[47:48] != u"*")) :
                self._m_bus_voltage = ((5.0 * int((self.whole_beacon_ascii)[45:48], 16)) / 4096)

            return getattr(self, '_m_bus_voltage', None)

        @property
        def battery_1_temperature(self):
            if hasattr(self, '_m_battery_1_temperature'):
                return self._m_battery_1_temperature

            if  (((self.whole_beacon_ascii)[30:31] != u"*") and ((self.whole_beacon_ascii)[31:32] != u"*") and ((self.whole_beacon_ascii)[32:33] != u"*")) :
                self._m_battery_1_temperature = (((0.15797 * (((5.0 * int((self.whole_beacon_ascii)[30:33], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[30:33], 16)) / 4096))) - (39.553 * ((5.0 * int((self.whole_beacon_ascii)[30:33], 16)) / 4096))) + 129.59)

            return getattr(self, '_m_battery_1_temperature', None)

        @property
        def address_block(self):
            if hasattr(self, '_m_address_block'):
                return self._m_address_block

            if  (((self.whole_beacon_ascii)[8:9] != u"*") and ((self.whole_beacon_ascii)[9:10] != u"*") and ((self.whole_beacon_ascii)[10:11] != u"*") and ((self.whole_beacon_ascii)[11:12] != u"*")) :
                self._m_address_block = int((self.whole_beacon_ascii)[8:12], 16)

            return getattr(self, '_m_address_block', None)

        @property
        def battery_2_temperature(self):
            if hasattr(self, '_m_battery_2_temperature'):
                return self._m_battery_2_temperature

            if  (((self.whole_beacon_ascii)[33:34] != u"*") and ((self.whole_beacon_ascii)[34:35] != u"*") and ((self.whole_beacon_ascii)[35:36] != u"*")) :
                self._m_battery_2_temperature = (((0.18923 * (((5.0 * int((self.whole_beacon_ascii)[33:36], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[33:36], 16)) / 4096))) - (39.27 * ((5.0 * int((self.whole_beacon_ascii)[33:36], 16)) / 4096))) + 128.33)

            return getattr(self, '_m_battery_2_temperature', None)

        @property
        def solar_cell_2_current(self):
            if hasattr(self, '_m_solar_cell_2_current'):
                return self._m_solar_cell_2_current

            if  (((self.whole_beacon_ascii)[15:16] != u"*") and ((self.whole_beacon_ascii)[16:17] != u"*") and ((self.whole_beacon_ascii)[17:18] != u"*")) :
                self._m_solar_cell_2_current = (((5.0 * int((self.whole_beacon_ascii)[15:18], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_2_current', None)


    class Zero(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.whole_beacon_ascii = (self._io.read_bytes(6)).decode(u"utf-8")
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = 0
            return getattr(self, '_m_beacon_mode', None)

        @property
        def batteries_voltage(self):
            if hasattr(self, '_m_batteries_voltage'):
                return self._m_batteries_voltage

            if  (((self.whole_beacon_ascii)[0:1] != u"*") and ((self.whole_beacon_ascii)[1:2] != u"*") and ((self.whole_beacon_ascii)[2:3] != u"*")) :
                self._m_batteries_voltage = ((5.0 * int((self.whole_beacon_ascii)[0:3], 16)) / 4096)

            return getattr(self, '_m_batteries_voltage', None)

        @property
        def bus_voltage(self):
            if hasattr(self, '_m_bus_voltage'):
                return self._m_bus_voltage

            if  (((self.whole_beacon_ascii)[3:4] != u"*") and ((self.whole_beacon_ascii)[4:5] != u"*") and ((self.whole_beacon_ascii)[5:6] != u"*")) :
                self._m_bus_voltage = ((5.0 * int((self.whole_beacon_ascii)[3:6], 16)) / 4096)

            return getattr(self, '_m_bus_voltage', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.discard) != 0:
                self._m_necessary_for_lengthcheck = int(self.discard) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)


    class Discard(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.discard = self._io.read_bits_int_be(1) != 0

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            self._m_necessary_for_lengthcheck = int(self.discard) // 0
            return getattr(self, '_m_necessary_for_lengthcheck', None)


    class Six(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.whole_beacon_ascii = (self._io.read_bytes(3)).decode(u"utf-8")
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = 6
            return getattr(self, '_m_beacon_mode', None)

        @property
        def batteries_voltage(self):
            if hasattr(self, '_m_batteries_voltage'):
                return self._m_batteries_voltage

            if  (((self.whole_beacon_ascii)[0:1] != u"*") and ((self.whole_beacon_ascii)[1:2] != u"*") and ((self.whole_beacon_ascii)[2:3] != u"*")) :
                self._m_batteries_voltage = ((5.0 * int((self.whole_beacon_ascii)[0:3], 16)) / 4096)

            return getattr(self, '_m_batteries_voltage', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.discard) != 0:
                self._m_necessary_for_lengthcheck = int(self.discard) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)


    class ModeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 52:
                self.mode_check = Co66.Four(self._io, self, self._root)
            elif _on == 51:
                self.mode_check = Co66.Three(self._io, self, self._root)
            elif _on == 48:
                self.mode_check = Co66.Zero(self._io, self, self._root)
            elif _on == 49:
                self.mode_check = Co66.One(self._io, self, self._root)
            elif _on == 54:
                self.mode_check = Co66.Six(self._io, self, self._root)
            else:
                self.mode_check = Co66.Discard(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            self._m_check = self._io.read_u1()
            return getattr(self, '_m_check', None)


    class One(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.whole_beacon_ascii = (self._io.read_bytes(45)).decode(u"utf-8")
            self.discard = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def beacon_mode(self):
            if hasattr(self, '_m_beacon_mode'):
                return self._m_beacon_mode

            self._m_beacon_mode = 1
            return getattr(self, '_m_beacon_mode', None)

        @property
        def necessary_for_lengthcheck(self):
            if hasattr(self, '_m_necessary_for_lengthcheck'):
                return self._m_necessary_for_lengthcheck

            if len(self.discard) != 0:
                self._m_necessary_for_lengthcheck = int(self.discard) // 0

            return getattr(self, '_m_necessary_for_lengthcheck', None)

        @property
        def solar_cell_3_current(self):
            if hasattr(self, '_m_solar_cell_3_current'):
                return self._m_solar_cell_3_current

            if  (((self.whole_beacon_ascii)[20:21] != u"*") and ((self.whole_beacon_ascii)[21:22] != u"*") and ((self.whole_beacon_ascii)[22:23] != u"*")) :
                self._m_solar_cell_3_current = (((5.0 * int((self.whole_beacon_ascii)[20:23], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_3_current', None)

        @property
        def solar_cell_5_current(self):
            if hasattr(self, '_m_solar_cell_5_current'):
                return self._m_solar_cell_5_current

            if  (((self.whole_beacon_ascii)[26:27] != u"*") and ((self.whole_beacon_ascii)[27:28] != u"*") and ((self.whole_beacon_ascii)[28:29] != u"*")) :
                self._m_solar_cell_5_current = (((5.0 * int((self.whole_beacon_ascii)[26:29], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_5_current', None)

        @property
        def satellite_time(self):
            if hasattr(self, '_m_satellite_time'):
                return self._m_satellite_time

            if  (((self.whole_beacon_ascii)[0:1] != u"*") and ((self.whole_beacon_ascii)[1:2] != u"*") and ((self.whole_beacon_ascii)[2:3] != u"*") and ((self.whole_beacon_ascii)[3:4] != u"*") and ((self.whole_beacon_ascii)[4:5] != u"*") and ((self.whole_beacon_ascii)[5:6] != u"*") and ((self.whole_beacon_ascii)[6:7] != u"*") and ((self.whole_beacon_ascii)[7:8] != u"*")) :
                self._m_satellite_time = int((self.whole_beacon_ascii)[0:8], 16) // 2

            return getattr(self, '_m_satellite_time', None)

        @property
        def receiver_temperature(self):
            if hasattr(self, '_m_receiver_temperature'):
                return self._m_receiver_temperature

            if  (((self.whole_beacon_ascii)[41:42] != u"*") and ((self.whole_beacon_ascii)[42:43] != u"*") and ((self.whole_beacon_ascii)[43:44] != u"*")) :
                self._m_receiver_temperature = (((-0.062626 * (((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096))) - (38.305 * ((5.0 * int((self.whole_beacon_ascii)[41:44], 16)) / 4096))) + 126.89)

            return getattr(self, '_m_receiver_temperature', None)

        @property
        def solar_cell_4_current(self):
            if hasattr(self, '_m_solar_cell_4_current'):
                return self._m_solar_cell_4_current

            if  (((self.whole_beacon_ascii)[23:24] != u"*") and ((self.whole_beacon_ascii)[24:25] != u"*") and ((self.whole_beacon_ascii)[25:26] != u"*")) :
                self._m_solar_cell_4_current = (((5.0 * int((self.whole_beacon_ascii)[23:26], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_4_current', None)

        @property
        def solar_cell_6_current(self):
            if hasattr(self, '_m_solar_cell_6_current'):
                return self._m_solar_cell_6_current

            if  (((self.whole_beacon_ascii)[29:30] != u"*") and ((self.whole_beacon_ascii)[30:31] != u"*") and ((self.whole_beacon_ascii)[31:32] != u"*")) :
                self._m_solar_cell_6_current = (((5.0 * int((self.whole_beacon_ascii)[29:32], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_6_current', None)

        @property
        def cw_transmission_interval(self):
            if hasattr(self, '_m_cw_transmission_interval'):
                return self._m_cw_transmission_interval

            if (self.whole_beacon_ascii)[44:45] != u"*":
                self._m_cw_transmission_interval = (int((self.whole_beacon_ascii)[44:45], 16) * 3)

            return getattr(self, '_m_cw_transmission_interval', None)

        @property
        def batteries_voltage(self):
            if hasattr(self, '_m_batteries_voltage'):
                return self._m_batteries_voltage

            if  (((self.whole_beacon_ascii)[8:9] != u"*") and ((self.whole_beacon_ascii)[9:10] != u"*") and ((self.whole_beacon_ascii)[10:11] != u"*")) :
                self._m_batteries_voltage = ((5.0 * int((self.whole_beacon_ascii)[8:11], 16)) / 4096)

            return getattr(self, '_m_batteries_voltage', None)

        @property
        def transmitter_temperature(self):
            if hasattr(self, '_m_transmitter_temperature'):
                return self._m_transmitter_temperature

            if  (((self.whole_beacon_ascii)[38:39] != u"*") and ((self.whole_beacon_ascii)[39:40] != u"*") and ((self.whole_beacon_ascii)[40:41] != u"*")) :
                self._m_transmitter_temperature = (((-0.38082 * (((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096))) - (36.125 * ((5.0 * int((self.whole_beacon_ascii)[38:41], 16)) / 4096))) + 121.31)

            return getattr(self, '_m_transmitter_temperature', None)

        @property
        def solar_cell_1_current(self):
            if hasattr(self, '_m_solar_cell_1_current'):
                return self._m_solar_cell_1_current

            if  (((self.whole_beacon_ascii)[14:15] != u"*") and ((self.whole_beacon_ascii)[15:16] != u"*") and ((self.whole_beacon_ascii)[16:17] != u"*")) :
                self._m_solar_cell_1_current = (((5.0 * int((self.whole_beacon_ascii)[14:17], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_1_current', None)

        @property
        def bus_voltage(self):
            if hasattr(self, '_m_bus_voltage'):
                return self._m_bus_voltage

            if  (((self.whole_beacon_ascii)[11:12] != u"*") and ((self.whole_beacon_ascii)[12:13] != u"*") and ((self.whole_beacon_ascii)[13:14] != u"*")) :
                self._m_bus_voltage = ((5.0 * int((self.whole_beacon_ascii)[11:14], 16)) / 4096)

            return getattr(self, '_m_bus_voltage', None)

        @property
        def battery_1_temperature(self):
            if hasattr(self, '_m_battery_1_temperature'):
                return self._m_battery_1_temperature

            if  (((self.whole_beacon_ascii)[32:33] != u"*") and ((self.whole_beacon_ascii)[33:34] != u"*") and ((self.whole_beacon_ascii)[34:35] != u"*")) :
                self._m_battery_1_temperature = (((0.15797 * (((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096))) - (39.553 * ((5.0 * int((self.whole_beacon_ascii)[32:35], 16)) / 4096))) + 129.59)

            return getattr(self, '_m_battery_1_temperature', None)

        @property
        def battery_2_temperature(self):
            if hasattr(self, '_m_battery_2_temperature'):
                return self._m_battery_2_temperature

            if  (((self.whole_beacon_ascii)[35:36] != u"*") and ((self.whole_beacon_ascii)[36:37] != u"*") and ((self.whole_beacon_ascii)[37:38] != u"*")) :
                self._m_battery_2_temperature = (((0.18923 * (((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096) * ((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096))) - (39.27 * ((5.0 * int((self.whole_beacon_ascii)[35:38], 16)) / 4096))) + 128.33)

            return getattr(self, '_m_battery_2_temperature', None)

        @property
        def solar_cell_2_current(self):
            if hasattr(self, '_m_solar_cell_2_current'):
                return self._m_solar_cell_2_current

            if  (((self.whole_beacon_ascii)[17:18] != u"*") and ((self.whole_beacon_ascii)[18:19] != u"*") and ((self.whole_beacon_ascii)[19:20] != u"*")) :
                self._m_solar_cell_2_current = (((5.0 * int((self.whole_beacon_ascii)[17:20], 16)) / 4096) * 90.90909)

            return getattr(self, '_m_solar_cell_2_current', None)



