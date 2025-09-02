# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Grbbeta(KaitaiStruct):
    """:field uptime_total: id1.id2.uptime_total
    :field radio_boot_count: id1.id2.radio_boot_count
    :field radio_mcu_act_temperature: id1.id2.radio_mcu_act_temperature
    :field rf_power_amplifier_act_temperature: id1.id2.rf_power_amplifier_act_temperature
    :field cw_beacon: id1.id2.cw_beacon
    :field digi_dest_callsign: id1.id2.id3.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field digi_src_callsign: id1.id2.id3.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field digi_src_ssid: id1.id2.id3.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field digi_dest_ssid: id1.id2.id3.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_instance___callsign: id1.id2.id3.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance___ssid: id1.id2.id3.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.ssid
    :field rpt_instance___hbit: id1.id2.id3.ax25_frame.ax25_header.repeater.rpt_instance.___.rpt_ssid_raw.hbit
    :field digi_ctl: id1.id2.id3.ax25_frame.ax25_header.ctl
    :field digi_pid: id1.id2.id3.ax25_frame.ax25_header.pid
    :field digi_message: id1.id2.id3.ax25_frame.digi_message
    :field uhf_uptime_since_reset: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_uptime_since_reset
    :field uhf_uptime_total: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_uptime_total
    :field uhf_radio_boot_count: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_radio_boot_count
    :field uhf_rf_segment_reset_count: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_rf_segment_reset_count
    :field uhf_radio_mcu_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_radio_mcu_act_temperature
    :field uhf_rf_chip_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_rf_chip_act_temperature
    :field uhf_rf_power_amplifier_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_rf_power_amplifier_act_temperature
    :field uhf_digipeater_forwarded_message_count: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_digipeater_forwarded_message_count
    :field uhf_last_digipeater_user_sender_s_callsign: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_last_digipeater_user_sender_s_callsign
    :field uhf_rx_data_packets: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_rx_data_packets
    :field uhf_tx_data_packets: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_tx_data_packets
    :field uhf_actual_rssi: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_actual_rssi
    :field uhf_value_of_rssi_when_carrier_detected: id1.id2.id3.id4.ax25_frame.ax25_payload.uhf_value_of_rssi_when_carrier_detected
    :field vhf_uptime_since_reset: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_uptime_since_reset
    :field vhf_uptime_total: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_uptime_total
    :field vhf_radio_boot_count: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_radio_boot_count
    :field vhf_rf_segment_reset_count: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_rf_segment_reset_count
    :field vhf_radio_mcu_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_radio_mcu_act_temperature
    :field vhf_rf_chip_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_rf_chip_act_temperature
    :field vhf_rf_power_amplifier_act_temperature: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_rf_power_amplifier_act_temperature
    :field vhf_digipeater_forwarded_message_count: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_digipeater_forwarded_message_count
    :field vhf_last_digipeater_user_sender_s_callsign: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_last_digipeater_user_sender_s_callsign
    :field vhf_rx_data_packets: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_rx_data_packets
    :field vhf_tx_data_packets: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_tx_data_packets
    :field vhf_actual_rssi: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_actual_rssi
    :field vhf_value_of_rssi_when_carrier_detected: id1.id2.id3.id4.ax25_frame.ax25_payload.vhf_value_of_rssi_when_carrier_detected
    :field message: id1.id2.id3.id4.id5.ax25_frame.message
    :field csp_hdr_crc: id1.id2.id3.id4.id5.csp_header.crc
    :field csp_hdr_rdp: id1.id2.id3.id4.id5.csp_header.rdp
    :field csp_hdr_xtea: id1.id2.id3.id4.id5.csp_header.xtea
    :field csp_hdr_hmac: id1.id2.id3.id4.id5.csp_header.hmac
    :field csp_hdr_src_port: id1.id2.id3.id4.id5.csp_header.source_port
    :field csp_hdr_dst_port: id1.id2.id3.id4.id5.csp_header.destination_port
    :field csp_hdr_destination: id1.id2.id3.id4.id5.csp_header.destination
    :field csp_hdr_source: id1.id2.id3.id4.id5.csp_header.source
    :field csp_hdr_priority: id1.id2.id3.id4.id5.csp_header.priority
    :field psu_utc_time_stamp_rtc: id1.id2.id3.id4.id5.csp_data.telemetry.utc_time_stamp_rtc
    :field psu_uptime_rst: id1.id2.id3.id4.id5.csp_data.telemetry.uptime_rst
    :field psu_uptime_tot: id1.id2.id3.id4.id5.csp_data.telemetry.uptime_tot
    :field psu_reset_cnt: id1.id2.id3.id4.id5.csp_data.telemetry.reset_cnt
    :field psu_last_rst_src: id1.id2.id3.id4.id5.csp_data.telemetry.last_rst_src
    :field psu_packets_recvd_cnt: id1.id2.id3.id4.id5.csp_data.telemetry.packets_recvd_cnt
    :field psu_psu_error_count: id1.id2.id3.id4.id5.csp_data.telemetry.psu_error_count
    :field psu_pv_in_volt1: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_volt1
    :field psu_pv_in_volt2: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_volt2
    :field psu_pv_in_volt3: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_volt3
    :field psu_pv_in_amp1: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_amp1
    :field psu_pv_in_amp2: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_amp2
    :field psu_pv_in_amp3: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_amp3
    :field psu_pv_in_power1: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_power1
    :field psu_pv_in_power2: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_power2
    :field psu_pv_in_power3: id1.id2.id3.id4.id5.csp_data.telemetry.pv_in_power3
    :field psu_system_state: id1.id2.id3.id4.id5.csp_data.telemetry.system_state
    :field psu_out_sys_ch_amp1: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp1
    :field psu_out_sys_ch_amp2: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp2
    :field psu_out_sys_ch_amp3: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp3
    :field psu_out_sys_ch_amp4: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp4
    :field psu_out_sys_ch_amp5: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp5
    :field psu_out_sys_ch_amp6: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_ch_amp6
    :field psu_out_sys_bat_unreg_amp: id1.id2.id3.id4.id5.csp_data.telemetry.out_sys_bat_unreg_amp
    :field psu_bat_volt: id1.id2.id3.id4.id5.csp_data.telemetry.bat_volt
    :field psu_bat_amp_charge: id1.id2.id3.id4.id5.csp_data.telemetry.bat_amp_charge
    :field psu_bat_amp_discharge: id1.id2.id3.id4.id5.csp_data.telemetry.bat_amp_discharge
    :field psu_bat_temp_kelvin: id1.id2.id3.id4.id5.csp_data.telemetry.bat_temp_kelvin
    :field psu_system_temp_kelvin: id1.id2.id3.id4.id5.csp_data.telemetry.system_temp_kelvin
    :field psu_channel_0_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_0_status
    :field psu_channel_1_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_1_status
    :field psu_channel_2_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_2_status
    :field psu_channel_3_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_3_status
    :field psu_channel_4_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_4_status
    :field psu_channel_5_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_5_status
    :field psu_channel_6_status: id1.id2.id3.id4.id5.csp_data.telemetry.channel_6_status
    :field psu_mppt_ch1_state: id1.id2.id3.id4.id5.csp_data.telemetry.mppt_ch1_state
    :field psu_mppt_ch2_state: id1.id2.id3.id4.id5.csp_data.telemetry.mppt_ch2_state
    :field psu_mppt_ch3_state: id1.id2.id3.id4.id5.csp_data.telemetry.mppt_ch3_state
    
    .. seealso::
       Source - https://grbbeta.tuke.sk/index.php/en/home/
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id1 = Grbbeta.Type1(self._io, self, self._root)

    class NotCwMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.message_type2
            if _on == 2424464526:
                self.id3 = Grbbeta.Digi(self._io, self, self._root)
            else:
                self.id3 = Grbbeta.NotDigi(self._io, self, self._root)

        @property
        def message_type2(self):
            if hasattr(self, '_m_message_type2'):
                return self._m_message_type2

            _pos = self._io.pos()
            self._io.seek(14)
            self._m_message_type2 = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_message_type2', None)


    class NotMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = Grbbeta.NotMessage.CspHeaderT(self._io, self, self._root)
            self.csp_data = Grbbeta.NotMessage.CspDataT(self._io, self, self._root)

        class CspHeaderT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.csp_header_raw = self._io.read_u4be()

            @property
            def source(self):
                if hasattr(self, '_m_source'):
                    return self._m_source

                self._m_source = ((self.csp_header_raw >> 25) & 31)
                return getattr(self, '_m_source', None)

            @property
            def source_port(self):
                if hasattr(self, '_m_source_port'):
                    return self._m_source_port

                self._m_source_port = ((self.csp_header_raw >> 8) & 63)
                return getattr(self, '_m_source_port', None)

            @property
            def destination_port(self):
                if hasattr(self, '_m_destination_port'):
                    return self._m_destination_port

                self._m_destination_port = ((self.csp_header_raw >> 14) & 63)
                return getattr(self, '_m_destination_port', None)

            @property
            def rdp(self):
                if hasattr(self, '_m_rdp'):
                    return self._m_rdp

                self._m_rdp = ((self.csp_header_raw & 2) >> 1)
                return getattr(self, '_m_rdp', None)

            @property
            def destination(self):
                if hasattr(self, '_m_destination'):
                    return self._m_destination

                self._m_destination = ((self.csp_header_raw >> 20) & 31)
                return getattr(self, '_m_destination', None)

            @property
            def priority(self):
                if hasattr(self, '_m_priority'):
                    return self._m_priority

                self._m_priority = (self.csp_header_raw >> 30)
                return getattr(self, '_m_priority', None)

            @property
            def reserved(self):
                if hasattr(self, '_m_reserved'):
                    return self._m_reserved

                self._m_reserved = ((self.csp_header_raw >> 4) & 15)
                return getattr(self, '_m_reserved', None)

            @property
            def xtea(self):
                if hasattr(self, '_m_xtea'):
                    return self._m_xtea

                self._m_xtea = ((self.csp_header_raw & 4) >> 2)
                return getattr(self, '_m_xtea', None)

            @property
            def hmac(self):
                if hasattr(self, '_m_hmac'):
                    return self._m_hmac

                self._m_hmac = ((self.csp_header_raw & 8) >> 3)
                return getattr(self, '_m_hmac', None)

            @property
            def crc(self):
                if hasattr(self, '_m_crc'):
                    return self._m_crc

                self._m_crc = (self.csp_header_raw & 1)
                return getattr(self, '_m_crc', None)


        class CspDataT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                if  ((self._parent.csp_header.source == 2) and (self._parent.csp_header.source_port == 9)) :
                    self.telemetry = Grbbeta.NotMessage.PsuHkT(self._io, self, self._root)



        class PsuHkT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.utc_time_stamp_rtc = self._io.read_u4le()
                self.uptime_rst = self._io.read_u4le()
                self.uptime_tot = self._io.read_u4le()
                self.reset_cnt = self._io.read_u4le()
                self.last_rst_src = self._io.read_u2le()
                self.packets_recvd_cnt = self._io.read_u4le()
                self.psu_error_count = self._io.read_u4le()
                self.pv_in_volt1 = self._io.read_u2le()
                self.pv_in_volt2 = self._io.read_u2le()
                self.pv_in_volt3 = self._io.read_u2le()
                self.pv_in_amp1 = self._io.read_u2le()
                self.pv_in_amp2 = self._io.read_u2le()
                self.pv_in_amp3 = self._io.read_u2le()
                self.pv_in_power1 = self._io.read_u2le()
                self.pv_in_power2 = self._io.read_u2le()
                self.pv_in_power3 = self._io.read_u2le()
                self.ppt_mode = self._io.read_u1()
                self.channel_status = self._io.read_u1()
                self.system_state = self._io.read_u1()
                self.out_sys_ch_amp1 = self._io.read_u2le()
                self.out_sys_ch_amp2 = self._io.read_u2le()
                self.out_sys_ch_amp3 = self._io.read_u2le()
                self.out_sys_ch_amp4 = self._io.read_u2le()
                self.out_sys_ch_amp5 = self._io.read_u2le()
                self.out_sys_ch_amp6 = self._io.read_u2le()
                self.out_sys_bat_unreg_amp = self._io.read_u2le()
                self.bat_volt = self._io.read_u2le()
                self.bat_amp_charge = self._io.read_u2le()
                self.bat_amp_discharge = self._io.read_u2le()
                self.bat_temp_kelvin = self._io.read_u2le()
                self.system_temp_kelvin = self._io.read_u2le()

            @property
            def channel_2_status(self):
                if hasattr(self, '_m_channel_2_status'):
                    return self._m_channel_2_status

                self._m_channel_2_status = ((self.channel_status >> 2) & 1)
                return getattr(self, '_m_channel_2_status', None)

            @property
            def channel_6_status(self):
                if hasattr(self, '_m_channel_6_status'):
                    return self._m_channel_6_status

                self._m_channel_6_status = ((self.channel_status >> 6) & 1)
                return getattr(self, '_m_channel_6_status', None)

            @property
            def channel_0_status(self):
                if hasattr(self, '_m_channel_0_status'):
                    return self._m_channel_0_status

                self._m_channel_0_status = ((self.channel_status >> 0) & 1)
                return getattr(self, '_m_channel_0_status', None)

            @property
            def mppt_ch3_state(self):
                if hasattr(self, '_m_mppt_ch3_state'):
                    return self._m_mppt_ch3_state

                self._m_mppt_ch3_state = ((self.ppt_mode >> 2) & 1)
                return getattr(self, '_m_mppt_ch3_state', None)

            @property
            def mppt_ch2_state(self):
                if hasattr(self, '_m_mppt_ch2_state'):
                    return self._m_mppt_ch2_state

                self._m_mppt_ch2_state = ((self.ppt_mode >> 1) & 1)
                return getattr(self, '_m_mppt_ch2_state', None)

            @property
            def channel_1_status(self):
                if hasattr(self, '_m_channel_1_status'):
                    return self._m_channel_1_status

                self._m_channel_1_status = ((self.channel_status >> 1) & 1)
                return getattr(self, '_m_channel_1_status', None)

            @property
            def mppt_ch1_state(self):
                if hasattr(self, '_m_mppt_ch1_state'):
                    return self._m_mppt_ch1_state

                self._m_mppt_ch1_state = ((self.ppt_mode >> 0) & 1)
                return getattr(self, '_m_mppt_ch1_state', None)

            @property
            def channel_5_status(self):
                if hasattr(self, '_m_channel_5_status'):
                    return self._m_channel_5_status

                self._m_channel_5_status = ((self.channel_status >> 5) & 1)
                return getattr(self, '_m_channel_5_status', None)

            @property
            def channel_3_status(self):
                if hasattr(self, '_m_channel_3_status'):
                    return self._m_channel_3_status

                self._m_channel_3_status = ((self.channel_status >> 3) & 1)
                return getattr(self, '_m_channel_3_status', None)

            @property
            def channel_4_status(self):
                if hasattr(self, '_m_channel_4_status'):
                    return self._m_channel_4_status

                self._m_channel_4_status = ((self.channel_status >> 4) & 1)
                return getattr(self, '_m_channel_4_status', None)



    class Type1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.message_type1
            if _on == 7234224009119950706:
                self.id2 = Grbbeta.CwMessage(self._io, self, self._root)
            else:
                self.id2 = Grbbeta.NotCwMessage(self._io, self, self._root)

        @property
        def message_type1(self):
            if hasattr(self, '_m_message_type1'):
                return self._m_message_type1

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_message_type1 = self._io.read_u8be()
            self._io.seek(_pos)
            return getattr(self, '_m_message_type1', None)


    class BeaconVhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Grbbeta.BeaconVhf.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Grbbeta.BeaconVhf.Ax25Header(self._io, self, self._root)
                self.ax25_payload = Grbbeta.BeaconVhf.Ax25Payload(self._io, self, self._root)


        class Ax25Payload(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.vhf_beacon_identification = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_uptime_since_reset_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_uptime_total_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_radio_boot_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_rf_segment_reset_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_radio_mcu_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_rf_chip_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_rf_power_amplifier_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_digipeater_forwarded_message_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_last_digipeater_user_sender_s_callsign = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_rx_data_packets_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_tx_data_packets_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_actual_rssi_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.vhf_value_of_rssi_when_carrier_detected_raw = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

            @property
            def vhf_uptime_since_reset(self):
                if hasattr(self, '_m_vhf_uptime_since_reset'):
                    return self._m_vhf_uptime_since_reset

                self._m_vhf_uptime_since_reset = int(self.vhf_uptime_since_reset_raw)
                return getattr(self, '_m_vhf_uptime_since_reset', None)

            @property
            def vhf_digipeater_forwarded_message_count(self):
                if hasattr(self, '_m_vhf_digipeater_forwarded_message_count'):
                    return self._m_vhf_digipeater_forwarded_message_count

                self._m_vhf_digipeater_forwarded_message_count = int(self.vhf_digipeater_forwarded_message_count_raw)
                return getattr(self, '_m_vhf_digipeater_forwarded_message_count', None)

            @property
            def vhf_radio_boot_count(self):
                if hasattr(self, '_m_vhf_radio_boot_count'):
                    return self._m_vhf_radio_boot_count

                self._m_vhf_radio_boot_count = int(self.vhf_radio_boot_count_raw)
                return getattr(self, '_m_vhf_radio_boot_count', None)

            @property
            def vhf_value_of_rssi_when_carrier_detected(self):
                if hasattr(self, '_m_vhf_value_of_rssi_when_carrier_detected'):
                    return self._m_vhf_value_of_rssi_when_carrier_detected

                self._m_vhf_value_of_rssi_when_carrier_detected = int(self.vhf_value_of_rssi_when_carrier_detected_raw)
                return getattr(self, '_m_vhf_value_of_rssi_when_carrier_detected', None)

            @property
            def vhf_tx_data_packets(self):
                if hasattr(self, '_m_vhf_tx_data_packets'):
                    return self._m_vhf_tx_data_packets

                self._m_vhf_tx_data_packets = int(self.vhf_tx_data_packets_raw)
                return getattr(self, '_m_vhf_tx_data_packets', None)

            @property
            def vhf_radio_mcu_act_temperature(self):
                if hasattr(self, '_m_vhf_radio_mcu_act_temperature'):
                    return self._m_vhf_radio_mcu_act_temperature

                self._m_vhf_radio_mcu_act_temperature = int(self.vhf_radio_mcu_act_temperature_raw)
                return getattr(self, '_m_vhf_radio_mcu_act_temperature', None)

            @property
            def vhf_rf_chip_act_temperature(self):
                if hasattr(self, '_m_vhf_rf_chip_act_temperature'):
                    return self._m_vhf_rf_chip_act_temperature

                self._m_vhf_rf_chip_act_temperature = int(self.vhf_rf_chip_act_temperature_raw)
                return getattr(self, '_m_vhf_rf_chip_act_temperature', None)

            @property
            def vhf_rf_power_amplifier_act_temperature(self):
                if hasattr(self, '_m_vhf_rf_power_amplifier_act_temperature'):
                    return self._m_vhf_rf_power_amplifier_act_temperature

                self._m_vhf_rf_power_amplifier_act_temperature = int(self.vhf_rf_power_amplifier_act_temperature_raw)
                return getattr(self, '_m_vhf_rf_power_amplifier_act_temperature', None)

            @property
            def vhf_rx_data_packets(self):
                if hasattr(self, '_m_vhf_rx_data_packets'):
                    return self._m_vhf_rx_data_packets

                self._m_vhf_rx_data_packets = int(self.vhf_rx_data_packets_raw)
                return getattr(self, '_m_vhf_rx_data_packets', None)

            @property
            def vhf_actual_rssi(self):
                if hasattr(self, '_m_vhf_actual_rssi'):
                    return self._m_vhf_actual_rssi

                self._m_vhf_actual_rssi = int(self.vhf_actual_rssi_raw)
                return getattr(self, '_m_vhf_actual_rssi', None)

            @property
            def vhf_rf_segment_reset_count(self):
                if hasattr(self, '_m_vhf_rf_segment_reset_count'):
                    return self._m_vhf_rf_segment_reset_count

                self._m_vhf_rf_segment_reset_count = int(self.vhf_rf_segment_reset_count_raw)
                return getattr(self, '_m_vhf_rf_segment_reset_count', None)

            @property
            def vhf_uptime_total(self):
                if hasattr(self, '_m_vhf_uptime_total'):
                    return self._m_vhf_uptime_total

                self._m_vhf_uptime_total = int(self.vhf_uptime_total_raw)
                return getattr(self, '_m_vhf_uptime_total', None)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Grbbeta.BeaconVhf.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Grbbeta.BeaconVhf.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Grbbeta.BeaconVhf.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Grbbeta.BeaconVhf.SsidMask(self._io, self, self._root)
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
                self.callsign_ror = Grbbeta.BeaconVhf.Callsign(_io__raw_callsign_ror, self, self._root)



    class CwMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.de_ha2grb = (self._io.read_bytes(13)).decode(u"ASCII")
            if not  ((self.de_ha2grb == u"de ha2grb = u") or (self.de_ha2grb == u"DE HA2GRB = U")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.de_ha2grb, self._io, u"/types/cw_message/seq/0")
            self.uptime_total_raw = (self._io.read_bytes_term(114, False, True, True)).decode(u"UTF-8")
            self.radio_boot_count_raw = (self._io.read_bytes_term(116, False, True, True)).decode(u"UTF-8")
            self.radio_mcu_act_temperature_raw = (self._io.read_bytes_term(112, False, True, True)).decode(u"UTF-8")
            self.rf_power_amplifier_act_temperature_raw = (self._io.read_bytes_term(32, False, True, True)).decode(u"UTF-8")

        @property
        def uptime_total(self):
            if hasattr(self, '_m_uptime_total'):
                return self._m_uptime_total

            self._m_uptime_total = (int(self.uptime_total_raw) * 60)
            return getattr(self, '_m_uptime_total', None)

        @property
        def radio_boot_count(self):
            if hasattr(self, '_m_radio_boot_count'):
                return self._m_radio_boot_count

            self._m_radio_boot_count = int(self.radio_boot_count_raw)
            return getattr(self, '_m_radio_boot_count', None)

        @property
        def cw_beacon(self):
            if hasattr(self, '_m_cw_beacon'):
                return self._m_cw_beacon

            self._m_cw_beacon = u"u" + self.uptime_total_raw + u"r" + self.radio_boot_count_raw + u"t" + self.radio_mcu_act_temperature_raw + u"p" + self.rf_power_amplifier_act_temperature_raw
            return getattr(self, '_m_cw_beacon', None)

        @property
        def rf_power_amplifier_act_temperature(self):
            if hasattr(self, '_m_rf_power_amplifier_act_temperature'):
                return self._m_rf_power_amplifier_act_temperature

            self._m_rf_power_amplifier_act_temperature = int(self.rf_power_amplifier_act_temperature_raw)
            return getattr(self, '_m_rf_power_amplifier_act_temperature', None)

        @property
        def radio_mcu_act_temperature(self):
            if hasattr(self, '_m_radio_mcu_act_temperature'):
                return self._m_radio_mcu_act_temperature

            self._m_radio_mcu_act_temperature = int(self.radio_mcu_act_temperature_raw)
            return getattr(self, '_m_radio_mcu_act_temperature', None)


    class BeaconUhf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Grbbeta.BeaconUhf.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Grbbeta.BeaconUhf.Ax25Header(self._io, self, self._root)
                self.ax25_payload = Grbbeta.BeaconUhf.Ax25Payload(self._io, self, self._root)


        class Ax25Payload(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.uhf_beacon_identification = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_uptime_since_reset_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_uptime_total_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_radio_boot_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_rf_segment_reset_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_radio_mcu_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_rf_chip_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_rf_power_amplifier_act_temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_digipeater_forwarded_message_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_last_digipeater_user_sender_s_callsign = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_rx_data_packets_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_tx_data_packets_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_actual_rssi_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.uhf_value_of_rssi_when_carrier_detected_raw = (self._io.read_bytes_term(0, False, True, True)).decode(u"utf8")

            @property
            def uhf_radio_mcu_act_temperature(self):
                if hasattr(self, '_m_uhf_radio_mcu_act_temperature'):
                    return self._m_uhf_radio_mcu_act_temperature

                self._m_uhf_radio_mcu_act_temperature = int(self.uhf_radio_mcu_act_temperature_raw)
                return getattr(self, '_m_uhf_radio_mcu_act_temperature', None)

            @property
            def uhf_uptime_total(self):
                if hasattr(self, '_m_uhf_uptime_total'):
                    return self._m_uhf_uptime_total

                self._m_uhf_uptime_total = int(self.uhf_uptime_total_raw)
                return getattr(self, '_m_uhf_uptime_total', None)

            @property
            def uhf_tx_data_packets(self):
                if hasattr(self, '_m_uhf_tx_data_packets'):
                    return self._m_uhf_tx_data_packets

                self._m_uhf_tx_data_packets = int(self.uhf_tx_data_packets_raw)
                return getattr(self, '_m_uhf_tx_data_packets', None)

            @property
            def uhf_value_of_rssi_when_carrier_detected(self):
                if hasattr(self, '_m_uhf_value_of_rssi_when_carrier_detected'):
                    return self._m_uhf_value_of_rssi_when_carrier_detected

                self._m_uhf_value_of_rssi_when_carrier_detected = int(self.uhf_value_of_rssi_when_carrier_detected_raw)
                return getattr(self, '_m_uhf_value_of_rssi_when_carrier_detected', None)

            @property
            def uhf_actual_rssi(self):
                if hasattr(self, '_m_uhf_actual_rssi'):
                    return self._m_uhf_actual_rssi

                self._m_uhf_actual_rssi = int(self.uhf_actual_rssi_raw)
                return getattr(self, '_m_uhf_actual_rssi', None)

            @property
            def uhf_rf_segment_reset_count(self):
                if hasattr(self, '_m_uhf_rf_segment_reset_count'):
                    return self._m_uhf_rf_segment_reset_count

                self._m_uhf_rf_segment_reset_count = int(self.uhf_rf_segment_reset_count_raw)
                return getattr(self, '_m_uhf_rf_segment_reset_count', None)

            @property
            def uhf_rf_chip_act_temperature(self):
                if hasattr(self, '_m_uhf_rf_chip_act_temperature'):
                    return self._m_uhf_rf_chip_act_temperature

                self._m_uhf_rf_chip_act_temperature = int(self.uhf_rf_chip_act_temperature_raw)
                return getattr(self, '_m_uhf_rf_chip_act_temperature', None)

            @property
            def uhf_rx_data_packets(self):
                if hasattr(self, '_m_uhf_rx_data_packets'):
                    return self._m_uhf_rx_data_packets

                self._m_uhf_rx_data_packets = int(self.uhf_rx_data_packets_raw)
                return getattr(self, '_m_uhf_rx_data_packets', None)

            @property
            def uhf_uptime_since_reset(self):
                if hasattr(self, '_m_uhf_uptime_since_reset'):
                    return self._m_uhf_uptime_since_reset

                self._m_uhf_uptime_since_reset = int(self.uhf_uptime_since_reset_raw)
                return getattr(self, '_m_uhf_uptime_since_reset', None)

            @property
            def uhf_digipeater_forwarded_message_count(self):
                if hasattr(self, '_m_uhf_digipeater_forwarded_message_count'):
                    return self._m_uhf_digipeater_forwarded_message_count

                self._m_uhf_digipeater_forwarded_message_count = int(self.uhf_digipeater_forwarded_message_count_raw)
                return getattr(self, '_m_uhf_digipeater_forwarded_message_count', None)

            @property
            def uhf_rf_power_amplifier_act_temperature(self):
                if hasattr(self, '_m_uhf_rf_power_amplifier_act_temperature'):
                    return self._m_uhf_rf_power_amplifier_act_temperature

                self._m_uhf_rf_power_amplifier_act_temperature = int(self.uhf_rf_power_amplifier_act_temperature_raw)
                return getattr(self, '_m_uhf_rf_power_amplifier_act_temperature', None)

            @property
            def uhf_radio_boot_count(self):
                if hasattr(self, '_m_uhf_radio_boot_count'):
                    return self._m_uhf_radio_boot_count

                self._m_uhf_radio_boot_count = int(self.uhf_radio_boot_count_raw)
                return getattr(self, '_m_uhf_radio_boot_count', None)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Grbbeta.BeaconUhf.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Grbbeta.BeaconUhf.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Grbbeta.BeaconUhf.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Grbbeta.BeaconUhf.SsidMask(self._io, self, self._root)
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
                self.callsign_ror = Grbbeta.BeaconUhf.Callsign(_io__raw_callsign_ror, self, self._root)



    class NotBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.message_type4
            if _on == 2220950512:
                self.id5 = Grbbeta.Msg(self._io, self, self._root)
            else:
                self.id5 = Grbbeta.NotMessage(self._io, self, self._root)

        @property
        def message_type4(self):
            if hasattr(self, '_m_message_type4'):
                return self._m_message_type4

            _pos = self._io.pos()
            self._io.seek(12)
            self._m_message_type4 = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_message_type4', None)


    class Msg(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Grbbeta.Msg.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Grbbeta.Msg.Ax25Header(self._io, self, self._root)
                self.message = (self._io.read_bytes_full()).decode(u"utf-8")


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Grbbeta.Msg.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Grbbeta.Msg.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Grbbeta.Msg.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Grbbeta.Msg.SsidMask(self._io, self, self._root)
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
                self.callsign_ror = Grbbeta.Msg.Callsign(_io__raw_callsign_ror, self, self._root)



    class Digi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Grbbeta.Digi.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Grbbeta.Digi.Ax25Header(self._io, self, self._root)
                self.digi_message = (self._io.read_bytes_full()).decode(u"utf-8")


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Grbbeta.Digi.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Grbbeta.Digi.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Grbbeta.Digi.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Grbbeta.Digi.SsidMask(self._io, self, self._root)
                if (self.src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Grbbeta.Digi.Repeater(self._io, self, self._root)

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
                self.rpt_callsign_raw = Grbbeta.Digi.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Grbbeta.Digi.SsidMask(self._io, self, self._root)


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
                    _ = Grbbeta.Digi.Repeaters(self._io, self, self._root)
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
                self.callsign_ror = Grbbeta.Digi.Callsign(_io__raw_callsign_ror, self, self._root)



    class NotDigi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.message_type3
            if _on == 21804:
                self.id4 = Grbbeta.BeaconUhf(self._io, self, self._root)
            elif _on == 22060:
                self.id4 = Grbbeta.BeaconVhf(self._io, self, self._root)
            else:
                self.id4 = Grbbeta.NotBeacon(self._io, self, self._root)

        @property
        def message_type3(self):
            if hasattr(self, '_m_message_type3'):
                return self._m_message_type3

            _pos = self._io.pos()
            self._io.seek(16)
            self._m_message_type3 = self._io.read_u2be()
            self._io.seek(_pos)
            return getattr(self, '_m_message_type3', None)



