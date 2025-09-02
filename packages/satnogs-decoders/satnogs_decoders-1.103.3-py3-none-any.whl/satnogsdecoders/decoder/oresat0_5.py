# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Oresat05(KaitaiStruct):
    """:field callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid_raw_ssid_mask: ax25_frame.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field beacon_start_chars: ax25_frame.payload.ax25_info.beacon_start_chars
    :field satellite_id: ax25_frame.payload.ax25_info.satellite_id
    :field beacon_revision: ax25_frame.payload.ax25_info.beacon_revision
    :field status: ax25_frame.payload.ax25_info.status
    :field mode: ax25_frame.payload.ax25_info.mode
    :field system_uptime: ax25_frame.payload.ax25_info.system_uptime
    :field system_unix_time: ax25_frame.payload.ax25_info.system_unix_time
    :field system_power_cycles: ax25_frame.payload.ax25_info.system_power_cycles
    :field system_storage_percent: ax25_frame.payload.ax25_info.system_storage_percent
    :field lband_rx_bytes: ax25_frame.payload.ax25_info.lband_rx_bytes
    :field lband_rx_packets: ax25_frame.payload.ax25_info.lband_rx_packets
    :field lband_rssi: ax25_frame.payload.ax25_info.lband_rssi
    :field lband_synth_relock_count: ax25_frame.payload.ax25_info.lband_synth_relock_count
    :field uhf_rx_bytes: ax25_frame.payload.ax25_info.uhf_rx_bytes
    :field uhf_rx_packets: ax25_frame.payload.ax25_info.uhf_rx_packets
    :field uhf_rssi: ax25_frame.payload.ax25_info.uhf_rssi
    :field edl_sequence_count: ax25_frame.payload.ax25_info.edl_sequence_count
    :field edl_rejected_count: ax25_frame.payload.ax25_info.edl_rejected_count
    :field fread_cache_length: ax25_frame.payload.ax25_info.fread_cache_length
    :field fwrite_cache_length: ax25_frame.payload.ax25_info.fwrite_cache_length
    :field updater_cache_length: ax25_frame.payload.ax25_info.updater_cache_length
    :field adcs_manager_mode: ax25_frame.payload.ax25_info.adcs_manager_mode
    :field battery_1_pack_1_vbatt: ax25_frame.payload.ax25_info.battery_1_pack_1_vbatt
    :field battery_1_pack_1_vcell: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell
    :field battery_1_pack_1_vcell_max: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell_max
    :field battery_1_pack_1_vcell_min: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell_min
    :field battery_1_pack_1_vcell_1: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell_1
    :field battery_1_pack_1_vcell_2: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell_2
    :field battery_1_pack_1_vcell_avg: ax25_frame.payload.ax25_info.battery_1_pack_1_vcell_avg
    :field battery_1_pack_1_temperature: ax25_frame.payload.ax25_info.battery_1_pack_1_temperature
    :field battery_1_pack_1_temperature_avg: ax25_frame.payload.ax25_info.battery_1_pack_1_temperature_avg
    :field battery_1_pack_1_temperature_max: ax25_frame.payload.ax25_info.battery_1_pack_1_temperature_max
    :field battery_1_pack_1_temperature_min: ax25_frame.payload.ax25_info.battery_1_pack_1_temperature_min
    :field battery_1_pack_1_current: ax25_frame.payload.ax25_info.battery_1_pack_1_current
    :field battery_1_pack_1_current_avg: ax25_frame.payload.ax25_info.battery_1_pack_1_current_avg
    :field battery_1_pack_1_current_max: ax25_frame.payload.ax25_info.battery_1_pack_1_current_max
    :field battery_1_pack_1_current_min: ax25_frame.payload.ax25_info.battery_1_pack_1_current_min
    :field battery_1_pack_1_status: ax25_frame.payload.ax25_info.battery_1_pack_1_status
    :field battery_1_pack_1_reported_state_of_charge: ax25_frame.payload.ax25_info.battery_1_pack_1_reported_state_of_charge
    :field battery_1_pack_1_full_capacity: ax25_frame.payload.ax25_info.battery_1_pack_1_full_capacity
    :field battery_1_pack_1_reported_capacity: ax25_frame.payload.ax25_info.battery_1_pack_1_reported_capacity
    :field battery_1_pack_2_vbatt: ax25_frame.payload.ax25_info.battery_1_pack_2_vbatt
    :field battery_1_pack_2_vcell: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell
    :field battery_1_pack_2_vcell_max: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell_max
    :field battery_1_pack_2_vcell_min: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell_min
    :field battery_1_pack_2_vcell_1: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell_1
    :field battery_1_pack_2_vcell_2: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell_2
    :field battery_1_pack_2_vcell_avg: ax25_frame.payload.ax25_info.battery_1_pack_2_vcell_avg
    :field battery_1_pack_2_temperature: ax25_frame.payload.ax25_info.battery_1_pack_2_temperature
    :field battery_1_pack_2_temperature_avg: ax25_frame.payload.ax25_info.battery_1_pack_2_temperature_avg
    :field battery_1_pack_2_temperature_max: ax25_frame.payload.ax25_info.battery_1_pack_2_temperature_max
    :field battery_1_pack_2_temperature_min: ax25_frame.payload.ax25_info.battery_1_pack_2_temperature_min
    :field battery_1_pack_2_current: ax25_frame.payload.ax25_info.battery_1_pack_2_current
    :field battery_1_pack_2_current_avg: ax25_frame.payload.ax25_info.battery_1_pack_2_current_avg
    :field battery_1_pack_2_current_max: ax25_frame.payload.ax25_info.battery_1_pack_2_current_max
    :field battery_1_pack_2_current_min: ax25_frame.payload.ax25_info.battery_1_pack_2_current_min
    :field battery_1_pack_2_status: ax25_frame.payload.ax25_info.battery_1_pack_2_status
    :field battery_1_pack_2_reported_state_of_charge: ax25_frame.payload.ax25_info.battery_1_pack_2_reported_state_of_charge
    :field battery_1_pack_2_full_capacity: ax25_frame.payload.ax25_info.battery_1_pack_2_full_capacity
    :field battery_1_pack_2_reported_capacity: ax25_frame.payload.ax25_info.battery_1_pack_2_reported_capacity
    :field solar_1_output_voltage_avg: ax25_frame.payload.ax25_info.solar_1_output_voltage_avg
    :field solar_1_output_current_avg: ax25_frame.payload.ax25_info.solar_1_output_current_avg
    :field solar_1_output_power_avg: ax25_frame.payload.ax25_info.solar_1_output_power_avg
    :field solar_1_output_voltage_max: ax25_frame.payload.ax25_info.solar_1_output_voltage_max
    :field solar_1_output_current_max: ax25_frame.payload.ax25_info.solar_1_output_current_max
    :field solar_1_output_power_max: ax25_frame.payload.ax25_info.solar_1_output_power_max
    :field solar_1_output_energy: ax25_frame.payload.ax25_info.solar_1_output_energy
    :field solar_2_output_voltage_avg: ax25_frame.payload.ax25_info.solar_2_output_voltage_avg
    :field solar_2_output_current_avg: ax25_frame.payload.ax25_info.solar_2_output_current_avg
    :field solar_2_output_power_avg: ax25_frame.payload.ax25_info.solar_2_output_power_avg
    :field solar_2_output_voltage_max: ax25_frame.payload.ax25_info.solar_2_output_voltage_max
    :field solar_2_output_current_max: ax25_frame.payload.ax25_info.solar_2_output_current_max
    :field solar_2_output_power_max: ax25_frame.payload.ax25_info.solar_2_output_power_max
    :field solar_2_output_energy: ax25_frame.payload.ax25_info.solar_2_output_energy
    :field solar_3_output_voltage_avg: ax25_frame.payload.ax25_info.solar_3_output_voltage_avg
    :field solar_3_output_current_avg: ax25_frame.payload.ax25_info.solar_3_output_current_avg
    :field solar_3_output_power_avg: ax25_frame.payload.ax25_info.solar_3_output_power_avg
    :field solar_3_output_voltage_max: ax25_frame.payload.ax25_info.solar_3_output_voltage_max
    :field solar_3_output_current_max: ax25_frame.payload.ax25_info.solar_3_output_current_max
    :field solar_3_output_power_max: ax25_frame.payload.ax25_info.solar_3_output_power_max
    :field solar_3_output_energy: ax25_frame.payload.ax25_info.solar_3_output_energy
    :field solar_4_output_voltage_avg: ax25_frame.payload.ax25_info.solar_4_output_voltage_avg
    :field solar_4_output_current_avg: ax25_frame.payload.ax25_info.solar_4_output_current_avg
    :field solar_4_output_power_avg: ax25_frame.payload.ax25_info.solar_4_output_power_avg
    :field solar_4_output_voltage_max: ax25_frame.payload.ax25_info.solar_4_output_voltage_max
    :field solar_4_output_current_max: ax25_frame.payload.ax25_info.solar_4_output_current_max
    :field solar_4_output_power_max: ax25_frame.payload.ax25_info.solar_4_output_power_max
    :field solar_4_output_energy: ax25_frame.payload.ax25_info.solar_4_output_energy
    :field solar_5_output_voltage_avg: ax25_frame.payload.ax25_info.solar_5_output_voltage_avg
    :field solar_5_output_current_avg: ax25_frame.payload.ax25_info.solar_5_output_current_avg
    :field solar_5_output_power_avg: ax25_frame.payload.ax25_info.solar_5_output_power_avg
    :field solar_5_output_voltage_max: ax25_frame.payload.ax25_info.solar_5_output_voltage_max
    :field solar_5_output_current_max: ax25_frame.payload.ax25_info.solar_5_output_current_max
    :field solar_5_output_power_max: ax25_frame.payload.ax25_info.solar_5_output_power_max
    :field solar_5_output_energy: ax25_frame.payload.ax25_info.solar_5_output_energy
    :field solar_6_output_voltage_avg: ax25_frame.payload.ax25_info.solar_6_output_voltage_avg
    :field solar_6_output_current_avg: ax25_frame.payload.ax25_info.solar_6_output_current_avg
    :field solar_6_output_power_avg: ax25_frame.payload.ax25_info.solar_6_output_power_avg
    :field solar_6_output_voltage_max: ax25_frame.payload.ax25_info.solar_6_output_voltage_max
    :field solar_6_output_current_max: ax25_frame.payload.ax25_info.solar_6_output_current_max
    :field solar_6_output_power_max: ax25_frame.payload.ax25_info.solar_6_output_power_max
    :field solar_6_output_energy: ax25_frame.payload.ax25_info.solar_6_output_energy
    :field star_tracker_1_system_storage_percent: ax25_frame.payload.ax25_info.star_tracker_1_system_storage_percent
    :field star_tracker_1_status: ax25_frame.payload.ax25_info.star_tracker_1_status
    :field gps_system_storage_percent: ax25_frame.payload.ax25_info.gps_system_storage_percent
    :field gps_status: ax25_frame.payload.ax25_info.gps_status
    :field gps_skytraq_number_of_sv: ax25_frame.payload.ax25_info.gps_skytraq_number_of_sv
    :field gps_skytraq_fix_mode: ax25_frame.payload.ax25_info.gps_skytraq_fix_mode
    :field adcs_gyroscope_roll_rate: ax25_frame.payload.ax25_info.adcs_gyroscope_roll_rate
    :field adcs_gyroscope_pitch_rate: ax25_frame.payload.ax25_info.adcs_gyroscope_pitch_rate
    :field adcs_gyroscope_yaw_rate: ax25_frame.payload.ax25_info.adcs_gyroscope_yaw_rate
    :field dxwifi_system_storage_percent: ax25_frame.payload.ax25_info.dxwifi_system_storage_percent
    :field dxwifi_status: ax25_frame.payload.ax25_info.dxwifi_status
    :field dxwifi_radio_temperature: ax25_frame.payload.ax25_info.dxwifi_radio_temperature
    :field cfc_processor_system_storage_percent: ax25_frame.payload.ax25_info.cfc_processor_system_storage_percent
    :field cfc_processor_camera_status: ax25_frame.payload.ax25_info.cfc_processor_camera_status
    :field cfc_processor_camera_temperature: ax25_frame.payload.ax25_info.cfc_processor_camera_temperature
    :field cfc_processor_tec_status: ax25_frame.payload.ax25_info.cfc_processor_tec_status
    :field refcs: ax25_frame.ax25_trunk.refcs
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Oresat05.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Oresat05.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Oresat05.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Oresat05.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Oresat05.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Oresat05.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Oresat05.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Oresat05.IFrame(self._io, self, self._root)
            self.ax25_trunk = Oresat05.Ax25Trunk(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Oresat05.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Oresat05.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Oresat05.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Oresat05.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Oresat05.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes(216)
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Oresat05.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"KJ7SAT") or (self.callsign == u"SPACE ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes(216)
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Oresat05.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Oresat05.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Oresat05.SsidMask(self._io, self, self._root)


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
                _ = Oresat05.Repeaters(self._io, self, self._root)
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
            self.callsign_ror = Oresat05.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25Trunk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.refcs = self._io.read_u4le()


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_start_chars = (self._io.read_bytes(3)).decode(u"ASCII")
            self.satellite_id = self._io.read_u1()
            self.beacon_revision = self._io.read_u1()
            self.status = self._io.read_u1()
            self.mode = self._io.read_u1()
            self.system_uptime = self._io.read_u4le()
            self.system_unix_time = self._io.read_u4le()
            self.system_power_cycles = self._io.read_u2le()
            self.system_storage_percent = self._io.read_u1()
            self.lband_rx_bytes = self._io.read_u4le()
            self.lband_rx_packets = self._io.read_u4le()
            self.lband_rssi = self._io.read_s1()
            self.lband_synth_relock_count = self._io.read_u1()
            self.uhf_rx_bytes = self._io.read_u4le()
            self.uhf_rx_packets = self._io.read_u4le()
            self.uhf_rssi = self._io.read_s1()
            self.edl_sequence_count = self._io.read_u4le()
            self.edl_rejected_count = self._io.read_u4le()
            self.fread_cache_length = self._io.read_u1()
            self.fwrite_cache_length = self._io.read_u1()
            self.updater_cache_length = self._io.read_u1()
            self.adcs_manager_mode = self._io.read_u1()
            self.battery_1_pack_1_vbatt = self._io.read_u2le()
            self.battery_1_pack_1_vcell = self._io.read_u2le()
            self.battery_1_pack_1_vcell_max = self._io.read_u2le()
            self.battery_1_pack_1_vcell_min = self._io.read_u2le()
            self.battery_1_pack_1_vcell_1 = self._io.read_u2le()
            self.battery_1_pack_1_vcell_2 = self._io.read_u2le()
            self.battery_1_pack_1_vcell_avg = self._io.read_u2le()
            self.battery_1_pack_1_temperature = self._io.read_s1()
            self.battery_1_pack_1_temperature_avg = self._io.read_s1()
            self.battery_1_pack_1_temperature_max = self._io.read_s1()
            self.battery_1_pack_1_temperature_min = self._io.read_s1()
            self.battery_1_pack_1_current = self._io.read_s2le()
            self.battery_1_pack_1_current_avg = self._io.read_s2le()
            self.battery_1_pack_1_current_max = self._io.read_s2le()
            self.battery_1_pack_1_current_min = self._io.read_s2le()
            self.battery_1_pack_1_status = self._io.read_u1()
            self.battery_1_pack_1_reported_state_of_charge = self._io.read_u1()
            self.battery_1_pack_1_full_capacity = self._io.read_u2le()
            self.battery_1_pack_1_reported_capacity = self._io.read_u2le()
            self.battery_1_pack_2_vbatt = self._io.read_u2le()
            self.battery_1_pack_2_vcell = self._io.read_u2le()
            self.battery_1_pack_2_vcell_max = self._io.read_u2le()
            self.battery_1_pack_2_vcell_min = self._io.read_u2le()
            self.battery_1_pack_2_vcell_1 = self._io.read_u2le()
            self.battery_1_pack_2_vcell_2 = self._io.read_u2le()
            self.battery_1_pack_2_vcell_avg = self._io.read_u2le()
            self.battery_1_pack_2_temperature = self._io.read_s1()
            self.battery_1_pack_2_temperature_avg = self._io.read_s1()
            self.battery_1_pack_2_temperature_max = self._io.read_s1()
            self.battery_1_pack_2_temperature_min = self._io.read_s1()
            self.battery_1_pack_2_current = self._io.read_s2le()
            self.battery_1_pack_2_current_avg = self._io.read_s2le()
            self.battery_1_pack_2_current_max = self._io.read_s2le()
            self.battery_1_pack_2_current_min = self._io.read_s2le()
            self.battery_1_pack_2_status = self._io.read_u1()
            self.battery_1_pack_2_reported_state_of_charge = self._io.read_u1()
            self.battery_1_pack_2_full_capacity = self._io.read_u2le()
            self.battery_1_pack_2_reported_capacity = self._io.read_u2le()
            self.solar_1_output_voltage_avg = self._io.read_u2le()
            self.solar_1_output_current_avg = self._io.read_s2le()
            self.solar_1_output_power_avg = self._io.read_u2le()
            self.solar_1_output_voltage_max = self._io.read_u2le()
            self.solar_1_output_current_max = self._io.read_s2le()
            self.solar_1_output_power_max = self._io.read_u2le()
            self.solar_1_output_energy = self._io.read_u2le()
            self.solar_2_output_voltage_avg = self._io.read_u2le()
            self.solar_2_output_current_avg = self._io.read_s2le()
            self.solar_2_output_power_avg = self._io.read_u2le()
            self.solar_2_output_voltage_max = self._io.read_u2le()
            self.solar_2_output_current_max = self._io.read_s2le()
            self.solar_2_output_power_max = self._io.read_u2le()
            self.solar_2_output_energy = self._io.read_u2le()
            self.solar_3_output_voltage_avg = self._io.read_u2le()
            self.solar_3_output_current_avg = self._io.read_s2le()
            self.solar_3_output_power_avg = self._io.read_u2le()
            self.solar_3_output_voltage_max = self._io.read_u2le()
            self.solar_3_output_current_max = self._io.read_s2le()
            self.solar_3_output_power_max = self._io.read_u2le()
            self.solar_3_output_energy = self._io.read_u2le()
            self.solar_4_output_voltage_avg = self._io.read_u2le()
            self.solar_4_output_current_avg = self._io.read_s2le()
            self.solar_4_output_power_avg = self._io.read_u2le()
            self.solar_4_output_voltage_max = self._io.read_u2le()
            self.solar_4_output_current_max = self._io.read_s2le()
            self.solar_4_output_power_max = self._io.read_u2le()
            self.solar_4_output_energy = self._io.read_u2le()
            self.solar_5_output_voltage_avg = self._io.read_u2le()
            self.solar_5_output_current_avg = self._io.read_s2le()
            self.solar_5_output_power_avg = self._io.read_u2le()
            self.solar_5_output_voltage_max = self._io.read_u2le()
            self.solar_5_output_current_max = self._io.read_s2le()
            self.solar_5_output_power_max = self._io.read_u2le()
            self.solar_5_output_energy = self._io.read_u2le()
            self.solar_6_output_voltage_avg = self._io.read_u2le()
            self.solar_6_output_current_avg = self._io.read_s2le()
            self.solar_6_output_power_avg = self._io.read_u2le()
            self.solar_6_output_voltage_max = self._io.read_u2le()
            self.solar_6_output_current_max = self._io.read_s2le()
            self.solar_6_output_power_max = self._io.read_u2le()
            self.solar_6_output_energy = self._io.read_u2le()
            self.star_tracker_1_system_storage_percent = self._io.read_u1()
            self.star_tracker_1_status = self._io.read_u1()
            self.gps_system_storage_percent = self._io.read_u1()
            self.gps_status = self._io.read_u1()
            self.gps_skytraq_number_of_sv = self._io.read_u1()
            self.gps_skytraq_fix_mode = self._io.read_u1()
            self.adcs_gyroscope_roll_rate = self._io.read_s2le()
            self.adcs_gyroscope_pitch_rate = self._io.read_s2le()
            self.adcs_gyroscope_yaw_rate = self._io.read_s2le()
            self.dxwifi_system_storage_percent = self._io.read_u1()
            self.dxwifi_status = self._io.read_u1()
            self.dxwifi_radio_temperature = self._io.read_s1()
            self.cfc_processor_system_storage_percent = self._io.read_u1()
            self.cfc_processor_camera_status = self._io.read_u1()
            self.cfc_processor_camera_temperature = self._io.read_s1()
            self.cfc_processor_tec_status = self._io.read_bits_int_be(1) != 0



