# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Celesta(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.dest_callsign_ror.dest_callsign
    :field dest_ssid_raw: ax25_frame.ax25_header.dest_ssid_raw
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.src_callsign_ror.src_callsign
    :field src_ssid_raw: ax25_frame.ax25_header.src_ssid_raw
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.ax25_data.pid
    :field size: ax25_frame.ax25_data.size
    :field frame_type: ax25_frame.ax25_data.frame_type
    :field ts: ax25_frame.ax25_data.ts
    :field timestamp: ax25_frame.ax25_data.obdh.timestamp
    :field temperature: ax25_frame.ax25_data.obdh.temperature
    :field satellite_mode: ax25_frame.ax25_data.obdh.satellite_mode
    :field obdh_mode: ax25_frame.ax25_data.obdh.obdh_mode
    :field bytes_to_transmit: ax25_frame.ax25_data.obdh.bytes_to_transmit
    :field number_of_resets: ax25_frame.ax25_data.obdh.number_of_resets
    :field number_of_errors: ax25_frame.ax25_data.obdh.number_of_errors
    :field eps_mode: ax25_frame.ax25_data.eps.eps_mode
    :field battery_voltage_raw: ax25_frame.ax25_data.eps.battery_voltage_raw
    :field battery_temperature: ax25_frame.ax25_data.eps.battery_temperature
    :field min_battery_voltage_raw: ax25_frame.ax25_data.eps.min_battery_voltage_raw
    :field max_battery_voltage_raw: ax25_frame.ax25_data.eps.max_battery_voltage_raw
    :field avg_battery_voltage_raw: ax25_frame.ax25_data.eps.avg_battery_voltage_raw
    :field avg_charge_current_raw: ax25_frame.ax25_data.eps.avg_charge_current_raw
    :field max_charge_current_raw: ax25_frame.ax25_data.eps.max_charge_current_raw
    :field z_minu_face_temperature: ax25_frame.ax25_data.eps.z_minu_face_temperature
    :field o_b_d_h_current: ax25_frame.ax25_data.eps.o_b_d_h_current
    :field e_p_s_current: ax25_frame.ax25_data.eps.e_p_s_current
    :field t_t_c_micro_c_current: ax25_frame.ax25_data.eps.t_t_c_micro_c_current
    :field t_t_c_p_a_current_raw: ax25_frame.ax25_data.eps.t_t_c_p_a_current_raw
    :field d_o_s_i_current: ax25_frame.ax25_data.eps.d_o_s_i_current
    :field charge_current_raw: ax25_frame.ax25_data.eps.charge_current_raw
    :field spare: ax25_frame.ax25_data.eps.spare
    :field last_battery_voltage: ax25_frame.ax25_data.eps.last_battery_voltage
    :field minimum_battery_voltage_measured_since_reboot: ax25_frame.ax25_data.eps.minimum_battery_voltage_measured_since_reboot
    :field maximum_battery_voltage_measured_since_reboot: ax25_frame.ax25_data.eps.maximum_battery_voltage_measured_since_reboot
    :field average_battery_voltage_measured_since_reboot: ax25_frame.ax25_data.eps.average_battery_voltage_measured_since_reboot
    :field average_charge_current_measured_since_reboot: ax25_frame.ax25_data.eps.average_charge_current_measured_since_reboot
    :field maximum_charge_current_measured_since_reboot: ax25_frame.ax25_data.eps.maximum_charge_current_measured_since_reboot
    :field current_consumption_of_the_power_amplifier_of_the_ttc: ax25_frame.ax25_data.eps.current_consumption_of_the_power_amplifier_of_the_ttc
    :field total_charge_current_of_the_battery: ax25_frame.ax25_data.eps.total_charge_current_of_the_battery
    :field mode: ax25_frame.ax25_data.ttc.mode
    :field number_of_ttc_resets: ax25_frame.ax25_data.ttc.number_of_ttc_resets
    :field last_reset_cause: ax25_frame.ax25_data.ttc.last_reset_cause
    :field number_of_received_valid_packets: ax25_frame.ax25_data.ttc.number_of_received_valid_packets
    :field number_of_transmitted_packets: ax25_frame.ax25_data.ttc.number_of_transmitted_packets
    :field measured_transmission_power: ax25_frame.ax25_data.ttc.measured_transmission_power
    :field last_error_code: ax25_frame.ax25_data.ttc.last_error_code
    :field power_configuration: ax25_frame.ax25_data.ttc.power_configuration
    :field power_amplifier_temperature: ax25_frame.ax25_data.ttc.power_amplifier_temperature
    :field rssi_of_last_received_packet_raw: ax25_frame.ax25_data.ttc.rssi_of_last_received_packet_raw
    :field frequency_deviation_of_last_received_packet_raw: ax25_frame.ax25_data.ttc.frequency_deviation_of_last_received_packet_raw
    :field beacon_period: ax25_frame.ax25_data.ttc.beacon_period
    :field rssi_of_last_received_packet: ax25_frame.ax25_data.ttc.rssi_of_last_received_packet
    :field frequency_deviation_of_last_received_packet_with_valid_crc: ax25_frame.ax25_data.ttc.frequency_deviation_of_last_received_packet_with_valid_crc
    :field last_message_rssi_raw: ax25_frame.ax25_data.ham_message.last_message_rssi_raw
    :field radio_message: ax25_frame.ax25_data.ham_message.radio_message
    :field last_msg_rssi_dbm: ax25_frame.ax25_data.ham_message.last_msg_rssi_dbm
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Celesta.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Celesta.Ax25Header(self._io, self, self._root)
            self.ax25_data = Celesta.Ax25Data(self._io, self, self._root)


    class DestCallsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Celesta.DestCallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = self._io.read_u1()
            self.src_callsign_raw = Celesta.SrcCallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = self._io.read_u1()
            self.ctl = self._io.read_u1()


    class HamMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.last_message_rssi_raw = self._io.read_u1()
            self.radio_message = (self._io.read_bytes(133)).decode(u"ASCII")

        @property
        def last_msg_rssi_dbm(self):
            if hasattr(self, '_m_last_msg_rssi_dbm'):
                return self._m_last_msg_rssi_dbm

            self._m_last_msg_rssi_dbm = (-1 * self.last_message_rssi_raw)
            return getattr(self, '_m_last_msg_rssi_dbm', None)


    class SrcCallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_src_callsign_ror = self._io.read_bytes(6)
            self._raw_src_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_src_callsign_ror, 8 - (1), 1)
            _io__raw_src_callsign_ror = KaitaiStream(BytesIO(self._raw_src_callsign_ror))
            self.src_callsign_ror = Celesta.SrcCallsign(_io__raw_src_callsign_ror, self, self._root)


    class Ttc(KaitaiStruct):

        class EMode(Enum):
            idle = 1
            beacon = 17
            commissionning = 34
            silent = 68

        class ELastResetCause(Enum):
            power_supply_reset = 17
            watchdog = 34
            oscillator_error = 51
            reset_pin = 68
            debugger_reset = 85
            software_reset = 119

        class ELastErrorCode(Enum):
            nothing = 0
            obdh_status_req = 1
            obdh_bdr_req = 2
            radio_hw_error = 17
            tx_queue_full = 34
            rx_queue_full = 51
            tx_bus_queue_full = 68
            rx_bus_queue_full = 85
            obc_temp_hw_error = 102
            obc_temp_h_limit_error = 119
            obc_temp_l_limit_error = 136
            pa_temp_hw_error = 153
            fram_id_error = 161
            fram_hw_error = 162
            fram_read_error = 163
            fram_write_error = 164
            event_queue_read_error = 165
            pa_temp_h_limit_error = 170
            pa_temp_l_limit_error = 187
            obdh_nack = 204
            ttc_reset_req = 209
            pf_reset_req = 221
            radio_task_timeout = 238
            radio_unqueue = 255
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = KaitaiStream.resolve_enum(Celesta.Ttc.EMode, self._io.read_u1())
            self.number_of_ttc_resets = self._io.read_u2le()
            self.last_reset_cause = KaitaiStream.resolve_enum(Celesta.Ttc.ELastResetCause, self._io.read_u1())
            self.number_of_received_valid_packets = self._io.read_u2le()
            self.number_of_transmitted_packets = self._io.read_u2le()
            self.measured_transmission_power = self._io.read_u2le()
            self.last_error_code = KaitaiStream.resolve_enum(Celesta.Ttc.ELastErrorCode, self._io.read_u1())
            self.power_configuration = self._io.read_u1()
            self.power_amplifier_temperature = self._io.read_s1()
            self.rssi_of_last_received_packet_raw = self._io.read_u1()
            self.frequency_deviation_of_last_received_packet_raw = self._io.read_u1()
            self.beacon_period = self._io.read_u1()

        @property
        def rssi_of_last_received_packet(self):
            if hasattr(self, '_m_rssi_of_last_received_packet'):
                return self._m_rssi_of_last_received_packet

            self._m_rssi_of_last_received_packet = (-1 * self.rssi_of_last_received_packet_raw)
            return getattr(self, '_m_rssi_of_last_received_packet', None)

        @property
        def frequency_deviation_of_last_received_packet_with_valid_crc(self):
            if hasattr(self, '_m_frequency_deviation_of_last_received_packet_with_valid_crc'):
                return self._m_frequency_deviation_of_last_received_packet_with_valid_crc

            self._m_frequency_deviation_of_last_received_packet_with_valid_crc = (self.frequency_deviation_of_last_received_packet_raw * 17)
            return getattr(self, '_m_frequency_deviation_of_last_received_packet_with_valid_crc', None)


    class Obdh(KaitaiStruct):

        class ESatelliteMode(Enum):
            standby = 0
            deploy = 1
            commissionning = 2
            comm_pl = 3
            mission = 4
            low_p_mission = 5
            transmit = 6
            survival = 7
            silent = 8

        class EObdhMode(Enum):
            standby = 17
            deploy = 34
            commissionning = 51
            comm_pl = 68
            mission = 85
            low_power_mission = 102
            silent = 119
            por = 255
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4be()
            self.temperature = self._io.read_u2le()
            self.satellite_mode = KaitaiStream.resolve_enum(Celesta.Obdh.ESatelliteMode, self._io.read_u1())
            self.obdh_mode = KaitaiStream.resolve_enum(Celesta.Obdh.EObdhMode, self._io.read_u1())
            self.bytes_to_transmit = self._io.read_u4le()
            self.number_of_resets = self._io.read_u2le()
            self.number_of_errors = self._io.read_u2le()


    class Eps(KaitaiStruct):

        class EEpsMode(Enum):
            idle = 0
            survival = 17
            stnadby = 34
            deploy = 51
            commissionnong = 68
            mission = 85
            low_power_mission = 102
            silent = 119
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_mode = KaitaiStream.resolve_enum(Celesta.Eps.EEpsMode, self._io.read_u1())
            self.battery_voltage_raw = self._io.read_u1()
            self.battery_temperature = self._io.read_s1()
            self.min_battery_voltage_raw = self._io.read_u1()
            self.max_battery_voltage_raw = self._io.read_u1()
            self.avg_battery_voltage_raw = self._io.read_u1()
            self.avg_charge_current_raw = self._io.read_u1()
            self.max_charge_current_raw = self._io.read_u1()
            self.z_minu_face_temperature = self._io.read_s1()
            self.o_b_d_h_current = self._io.read_u1()
            self.e_p_s_current = self._io.read_u1()
            self.t_t_c_micro_c_current = self._io.read_u1()
            self.t_t_c_p_a_current_raw = self._io.read_u1()
            self.d_o_s_i_current = self._io.read_u1()
            self.charge_current_raw = self._io.read_u1()
            self.spare = self._io.read_u1()

        @property
        def total_charge_current_of_the_battery(self):
            if hasattr(self, '_m_total_charge_current_of_the_battery'):
                return self._m_total_charge_current_of_the_battery

            self._m_total_charge_current_of_the_battery = (self.charge_current_raw * 12)
            return getattr(self, '_m_total_charge_current_of_the_battery', None)

        @property
        def current_consumption_of_the_power_amplifier_of_the_ttc(self):
            if hasattr(self, '_m_current_consumption_of_the_power_amplifier_of_the_ttc'):
                return self._m_current_consumption_of_the_power_amplifier_of_the_ttc

            self._m_current_consumption_of_the_power_amplifier_of_the_ttc = (self.t_t_c_p_a_current_raw * 5)
            return getattr(self, '_m_current_consumption_of_the_power_amplifier_of_the_ttc', None)

        @property
        def average_charge_current_measured_since_reboot(self):
            if hasattr(self, '_m_average_charge_current_measured_since_reboot'):
                return self._m_average_charge_current_measured_since_reboot

            self._m_average_charge_current_measured_since_reboot = (self.avg_charge_current_raw * 12)
            return getattr(self, '_m_average_charge_current_measured_since_reboot', None)

        @property
        def maximum_charge_current_measured_since_reboot(self):
            if hasattr(self, '_m_maximum_charge_current_measured_since_reboot'):
                return self._m_maximum_charge_current_measured_since_reboot

            self._m_maximum_charge_current_measured_since_reboot = (self.max_charge_current_raw * 12)
            return getattr(self, '_m_maximum_charge_current_measured_since_reboot', None)

        @property
        def maximum_battery_voltage_measured_since_reboot(self):
            if hasattr(self, '_m_maximum_battery_voltage_measured_since_reboot'):
                return self._m_maximum_battery_voltage_measured_since_reboot

            self._m_maximum_battery_voltage_measured_since_reboot = (self.max_battery_voltage_raw * 20)
            return getattr(self, '_m_maximum_battery_voltage_measured_since_reboot', None)

        @property
        def last_battery_voltage(self):
            if hasattr(self, '_m_last_battery_voltage'):
                return self._m_last_battery_voltage

            self._m_last_battery_voltage = (self.battery_voltage_raw * 20)
            return getattr(self, '_m_last_battery_voltage', None)

        @property
        def minimum_battery_voltage_measured_since_reboot(self):
            if hasattr(self, '_m_minimum_battery_voltage_measured_since_reboot'):
                return self._m_minimum_battery_voltage_measured_since_reboot

            self._m_minimum_battery_voltage_measured_since_reboot = (self.min_battery_voltage_raw * 20)
            return getattr(self, '_m_minimum_battery_voltage_measured_since_reboot', None)

        @property
        def average_battery_voltage_measured_since_reboot(self):
            if hasattr(self, '_m_average_battery_voltage_measured_since_reboot'):
                return self._m_average_battery_voltage_measured_since_reboot

            self._m_average_battery_voltage_measured_since_reboot = (self.avg_battery_voltage_raw * 20)
            return getattr(self, '_m_average_battery_voltage_measured_since_reboot', None)


    class DestCallsignRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_dest_callsign_ror = self._io.read_bytes(6)
            self._raw_dest_callsign_ror = KaitaiStream.process_rotate_left(self._raw__raw_dest_callsign_ror, 8 - (1), 1)
            _io__raw_dest_callsign_ror = KaitaiStream(BytesIO(self._raw_dest_callsign_ror))
            self.dest_callsign_ror = Celesta.DestCallsign(_io__raw_dest_callsign_ror, self, self._root)


    class Ax25Data(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.size = self._io.read_u1()
            self.frame_type = self._io.read_u1()
            self.ts = self._io.read_u4be()
            self.obdh = Celesta.Obdh(self._io, self, self._root)
            self.eps = Celesta.Eps(self._io, self, self._root)
            self.ttc = Celesta.Ttc(self._io, self, self._root)
            self.payload = self._io.read_bytes(48)
            self.ham_message = Celesta.HamMessage(self._io, self, self._root)


    class SrcCallsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.src_callsign = (self._io.read_bytes(6)).decode(u"ASCII")



