# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Innosat16(KaitaiStruct):
    """:field callsign: data.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: data.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: data.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign: data.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid_raw_ssid_mask: data.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: data.ax25_header.src_ssid_raw.ssid
    :field ctl: data.ax25_header.ctl
    :field pid: data.ax25_header.pid
    :field beacon_id: data.payload.beacon_id
    :field eps_1_mode: data.payload.eps_1_mode
    :field eps_1_consumption_current: data.payload.eps_1_consumption_current
    :field eps_1_solar_cells_current: data.payload.eps_1_solar_cells_current
    :field eps_1_cell_voltage_full: data.payload.eps_1_cell_voltage_full
    :field eps_1_battery_temperature: data.payload.eps_1_battery_temperature
    :field eps_1_temperature_sp_y_pos: data.payload.eps_1_temperature_sp_y_pos
    :field eps_1_temperature_sp_y_neg: data.payload.eps_1_temperature_sp_y_neg
    :field eps_1_temperature_sp_x_pos: data.payload.eps_1_temperature_sp_x_pos
    :field eps_1_temperature_sp_x_neg: data.payload.eps_1_temperature_sp_x_neg
    :field eps_1_systems_status: data.payload.eps_1_systems_status
    :field eps_1_boot_count: data.payload.eps_1_boot_count
    :field eps_2_mode: data.payload.eps_2_mode
    :field eps_2_consumption_current: data.payload.eps_2_consumption_current
    :field eps_2_solar_cells_current: data.payload.eps_2_solar_cells_current
    :field eps_2_cell_voltage_full: data.payload.eps_2_cell_voltage_full
    :field eps_2_battery_temperature: data.payload.eps_2_battery_temperature
    :field eps_2_temperature_sp_y_pos: data.payload.eps_2_temperature_sp_y_pos
    :field eps_2_temperature_sp_y_neg: data.payload.eps_2_temperature_sp_y_neg
    :field eps_2_temperature_sp_x_pos: data.payload.eps_2_temperature_sp_x_pos
    :field eps_2_temperature_sp_x_neg: data.payload.eps_2_temperature_sp_x_neg
    :field eps_2_systems_status: data.payload.eps_2_systems_status
    :field eps_2_boot_count: data.payload.eps_2_boot_count
    :field adcs_mt_mode: data.payload.adcs_mt_mode
    :field adcs_rm_mode: data.payload.adcs_rm_mode
    :field adcs_kf_mode: data.payload.adcs_kf_mode
    :field adcs_filter_reset_count: data.payload.adcs_filter_reset_count
    :field adcs_sensors_state: data.payload.adcs_sensors_state
    :field adcs_flywheel_state: data.payload.adcs_flywheel_state
    :field comm_type: data.payload.comm_type
    :field comm_vbus_voltage: data.payload.comm_vbus_voltage
    :field comm_boot_count: data.payload.comm_boot_count
    :field comm_rssi: data.payload.comm_rssi
    :field comm_rssi_minimal: data.payload.comm_rssi_minimal
    :field comm_received_valid_packets: data.payload.comm_received_valid_packets
    :field comm_received_invalid_packets: data.payload.comm_received_invalid_packets
    :field comm_sent_packets: data.payload.comm_sent_packets
    :field comm_status: data.payload.comm_status
    :field comm_mode: data.payload.comm_mode
    :field comm_amp_temperature: data.payload.comm_amp_temperature
    :field comm_reserved_1: data.payload.comm_reserved_1
    :field comm_reserved_2: data.payload.comm_reserved_2
    :field packet_id: data.data_header.packet_id
    :field packet_size: data.data_header.packet_size
    :field packet_info: data.data_header.packet_info
    :field cmd: data.data_payload.cmd
    :field gnss_timestamp: data.data_payload.payload.gnss_timestamp
    :field gnss_x: data.data_payload.payload.gnss_x
    :field gnss_y: data.data_payload.payload.gnss_y
    :field gnss_z: data.data_payload.payload.gnss_z
    :field gnss_v_x: data.data_payload.payload.gnss_v_x
    :field gnss_v_y: data.data_payload.payload.gnss_v_y
    :field gnss_v_z: data.data_payload.payload.gnss_v_z
    :field gnss_value_1: data.data_payload.payload.gnss_value_1
    :field gnss_value_2: data.data_payload.payload.gnss_value_2
    :field gnss_value_3: data.data_payload.payload.gnss_value_3
    :field gnss_value_4: data.data_payload.payload.gnss_value_4
    :field gnss_value_5: data.data_payload.payload.gnss_value_5
    :field gnss_value_6: data.data_payload.payload.gnss_value_6
    :field gnss_value_7: data.data_payload.payload.gnss_value_7
    :field gnss_value_8: data.data_payload.payload.gnss_value_8
    :field gnss_value_9: data.data_payload.payload.gnss_value_9
    :field gnss_value_10: data.data_payload.payload.gnss_value_10
    :field gnss_value_11: data.data_payload.payload.gnss_value_11
    :field gnss_value_12: data.data_payload.payload.gnss_value_12
    :field len: len
    :field type: type
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        _on = self.type
        if _on == 33930:
            self.data = Innosat16.Ax25Frame(self._io, self, self._root)
        else:
            self.data = Innosat16.DataFrame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Innosat16.Ax25Header(self._io, self, self._root)
            self.payload = Innosat16.GeoscanBeaconTlm(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Innosat16.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Innosat16.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Innosat16.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Innosat16.SsidMask(self._io, self, self._root)
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
            if not  ((self.callsign == u"BEACON") or (self.callsign == u"RS92S7")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class GnssTlm1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gnss_timestamp = self._io.read_u8le()
            self.gnss_x = self._io.read_f4le()
            self.gnss_y = self._io.read_f4le()
            self.gnss_z = self._io.read_f4le()
            self.gnss_v_x = self._io.read_f4le()
            self.gnss_v_y = self._io.read_f4le()
            self.gnss_v_z = self._io.read_f4le()
            self.gnss_value_1 = self._io.read_f4le()
            self.gnss_value_2 = self._io.read_f4le()
            self.gnss_value_3 = self._io.read_f4le()
            self.gnss_value_4 = self._io.read_f4le()
            self.gnss_value_5 = self._io.read_u1()
            self.gnss_value_6 = self._io.read_u1()
            self.gnss_value_7 = self._io.read_u1()
            self.gnss_value_8 = self._io.read_u1()
            self.gnss_value_9 = self._io.read_u2le()
            self.gnss_value_10 = self._io.read_f4le()
            self.gnss_value_11 = self._io.read_f4le()
            self.gnss_value_12 = self._io.read_f4le()


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


    class DataHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_id = self._io.read_u2le()
            self.packet_size = self._io.read_u1()
            self.packet_info = self._io.read_u1()


    class DataTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd = self._io.read_u2le()
            _on = self.cmd
            if _on == 17085:
                self.payload = Innosat16.GnssTlm1(self._io, self, self._root)
            elif _on == 17341:
                self.payload = Innosat16.GnssTlm2(self._io, self, self._root)


    class GnssTlm2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gnss_timestamp = self._io.read_u4le()
            self.gnss_x = self._io.read_f4le()
            self.gnss_y = self._io.read_f4le()
            self.gnss_z = self._io.read_f4le()
            self.gnss_v_x = self._io.read_f4le()
            self.gnss_v_y = self._io.read_f4le()
            self.gnss_v_z = self._io.read_f4le()
            self.gnss_value_1 = self._io.read_f4le()
            self.gnss_value_2 = self._io.read_f4le()
            self.gnss_value_3 = self._io.read_f4le()
            self.gnss_value_4 = self._io.read_f4le()
            self.gnss_value_5 = self._io.read_f4le()
            self.gnss_value_6 = self._io.read_f4le()
            self.gnss_value_7 = self._io.read_f4le()
            self.gnss_value_8 = self._io.read_u2le()
            self.gnss_value_9 = self._io.read_u8le()


    class GeoscanBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_id = self._io.read_u1()
            self.eps_1_mode = self._io.read_u1()
            self.eps_1_consumption_current = self._io.read_u2le()
            self.eps_1_solar_cells_current = self._io.read_u2le()
            self.eps_1_cell_voltage_full = self._io.read_u2le()
            self.eps_1_battery_temperature = self._io.read_s1()
            self.eps_1_temperature_sp_y_pos = self._io.read_s1()
            self.eps_1_temperature_sp_y_neg = self._io.read_s1()
            self.eps_1_temperature_sp_x_pos = self._io.read_s1()
            self.eps_1_temperature_sp_x_neg = self._io.read_s1()
            self.eps_1_systems_status = self._io.read_u2le()
            self.eps_1_boot_count = self._io.read_u2le()
            self.eps_2_mode = self._io.read_u1()
            self.eps_2_consumption_current = self._io.read_u2le()
            self.eps_2_solar_cells_current = self._io.read_u2le()
            self.eps_2_cell_voltage_full = self._io.read_u2le()
            self.eps_2_battery_temperature = self._io.read_s1()
            self.eps_2_temperature_sp_y_pos = self._io.read_s1()
            self.eps_2_temperature_sp_y_neg = self._io.read_s1()
            self.eps_2_temperature_sp_x_pos = self._io.read_s1()
            self.eps_2_temperature_sp_x_neg = self._io.read_s1()
            self.eps_2_systems_status = self._io.read_u2le()
            self.eps_2_boot_count = self._io.read_u2le()
            self.adcs_mt_mode = self._io.read_u1()
            self.adcs_rm_mode = self._io.read_u1()
            self.adcs_kf_mode = self._io.read_u1()
            self.adcs_filter_reset_count = self._io.read_u1()
            self.adcs_sensors_state = self._io.read_u2le()
            self.adcs_flywheel_state = self._io.read_u1()
            self.comm_type = self._io.read_u1()
            self.comm_vbus_voltage = self._io.read_u2le()
            self.comm_boot_count = self._io.read_u2le()
            self.comm_rssi = self._io.read_s1()
            self.comm_rssi_minimal = self._io.read_s1()
            self.comm_received_valid_packets = self._io.read_u1()
            self.comm_received_invalid_packets = self._io.read_u1()
            self.comm_sent_packets = self._io.read_u1()
            self.comm_status = self._io.read_u1()
            self.comm_mode = self._io.read_u1()
            self.comm_amp_temperature = self._io.read_s1()
            self.comm_reserved_1 = self._io.read_u2le()
            self.comm_reserved_2 = self._io.read_u1()


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
            self.callsign_ror = Innosat16.Callsign(_io__raw_callsign_ror, self, self._root)


    class DataFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_header = Innosat16.DataHeader(self._io, self, self._root)
            self.data_payload = Innosat16.DataTlm(self._io, self, self._root)


    @property
    def len(self):
        if hasattr(self, '_m_len'):
            return self._m_len

        self._m_len = self._io.size()
        return getattr(self, '_m_len', None)

    @property
    def type(self):
        if hasattr(self, '_m_type'):
            return self._m_type

        _pos = self._io.pos()
        self._io.seek(0)
        self._m_type = self._io.read_u2be()
        self._io.seek(_pos)
        return getattr(self, '_m_type', None)


