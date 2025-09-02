# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Geoscan(KaitaiStruct):
    """:field callsign_start_str: data.ax25_header.dest_callsign_raw.callsign_ror.callsign_start.callsign_start_str
    :field callsign_end_str: data.ax25_header.dest_callsign_raw.callsign_ror.callsign_end.callsign_end_str
    :field ssid_mask: data.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: data.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign_start_str: data.ax25_header.src_callsign_raw.callsign_ror.callsign_start.callsign_start_str
    :field src_callsign_raw_callsign_end_str: data.ax25_header.src_callsign_raw.callsign_ror.callsign_end.callsign_end_str
    :field src_ssid_raw_ssid_mask: data.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: data.ax25_header.src_ssid_raw.ssid
    :field ctl: data.ax25_header.ctl
    :field pid: data.ax25_header.pid
    :field beacon_id: data.payload.beacon_id
    :field eps_timestamp: data.payload.eps_timestamp
    :field eps_mode: data.payload.eps_mode
    :field eps_switch_count: data.payload.eps_switch_count
    :field eps_consumption_current: data.payload.eps_consumption_current
    :field eps_solar_cells_current: data.payload.eps_solar_cells_current
    :field eps_cell_voltage_half: data.payload.eps_cell_voltage_half
    :field eps_cell_voltage_full: data.payload.eps_cell_voltage_full
    :field eps_systems_status: data.payload.eps_systems_status
    :field eps_temperature_cell1: data.payload.eps_temperature_cell1
    :field eps_temperature_cell2: data.payload.eps_temperature_cell2
    :field eps_boot_count: data.payload.eps_boot_count
    :field eps_heater_mode: data.payload.eps_heater_mode
    :field eps_reserved: data.payload.eps_reserved
    :field obc_boot_count: data.payload.obc_boot_count
    :field obc_active_status: data.payload.obc_active_status
    :field obc_temperature_pos_x: data.payload.obc_temperature_pos_x
    :field obc_temperature_neg_x: data.payload.obc_temperature_neg_x
    :field obc_temperature_pos_y: data.payload.obc_temperature_pos_y
    :field obc_temperature_neg_y: data.payload.obc_temperature_neg_y
    :field gnss_sat_number: data.payload.gnss_sat_number
    :field adcs_mode: data.payload.adcs_mode
    :field adcs_reserved: data.payload.adcs_reserved
    :field cam_photos_number: data.payload.cam_photos_number
    :field cam_mode: data.payload.cam_mode
    :field cam_reserved: data.payload.cam_reserved
    :field comm_type: data.payload.comm_type
    :field comm_bus_voltage: data.payload.comm_bus_voltage
    :field comm_boot_count: data.payload.comm_boot_count
    :field comm_rssi: data.payload.comm_rssi
    :field comm_rssi_minimal: data.payload.comm_rssi_minimal
    :field comm_received_valid_packets: data.payload.comm_received_valid_packets
    :field comm_received_invalid_packets: data.payload.comm_received_invalid_packets
    :field comm_sent_packets: data.payload.comm_sent_packets
    :field comm_status: data.payload.comm_status
    :field comm_mode: data.payload.comm_mode
    :field comm_temperature: data.payload.comm_temperature
    :field comm_qso_received: data.payload.comm_qso_received
    :field comm_reserved: data.payload.comm_reserved
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
            self.data = Geoscan.Ax25Frame(self._io, self, self._root)
        else:
            self.data = Geoscan.DataFrame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Geoscan.Ax25Header(self._io, self, self._root)
            self.payload = Geoscan.GeoscanBeaconTlm(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Geoscan.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Geoscan.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Geoscan.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Geoscan.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_start = Geoscan.CallsignStartRaw(self._io, self, self._root)
            self.callsign_end = Geoscan.CallsignEndRaw(self._io, self, self._root)


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


    class CallsignStartRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_start_str = (self._io.read_bytes(2)).decode(u"ASCII")
            if not  ((self.callsign_start_str == u"BE") or (self.callsign_start_str == u"RS")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign_start_str, self._io, u"/types/callsign_start_raw/seq/0")


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
                self.payload = Geoscan.GnssTlm1(self._io, self, self._root)
            elif _on == 17341:
                self.payload = Geoscan.GnssTlm2(self._io, self, self._root)


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
            self.eps_timestamp = self._io.read_u4le()
            self.eps_mode = self._io.read_u1()
            self.eps_switch_count = self._io.read_u1()
            self.eps_consumption_current = self._io.read_u2le()
            self.eps_solar_cells_current = self._io.read_u2le()
            self.eps_cell_voltage_half = self._io.read_u2le()
            self.eps_cell_voltage_full = self._io.read_u2le()
            self.eps_systems_status = self._io.read_u2le()
            self.eps_temperature_cell1 = self._io.read_s1()
            self.eps_temperature_cell2 = self._io.read_s1()
            self.eps_boot_count = self._io.read_u2le()
            self.eps_heater_mode = self._io.read_u1()
            self.eps_reserved = self._io.read_u2le()
            self.obc_boot_count = self._io.read_u2le()
            self.obc_active_status = self._io.read_u1()
            self.obc_temperature_pos_x = self._io.read_s1()
            self.obc_temperature_neg_x = self._io.read_s1()
            self.obc_temperature_pos_y = self._io.read_s1()
            self.obc_temperature_neg_y = self._io.read_s1()
            self.gnss_sat_number = self._io.read_u1()
            self.adcs_mode = self._io.read_u1()
            self.adcs_reserved = self._io.read_u1()
            self.cam_photos_number = self._io.read_u1()
            self.cam_mode = self._io.read_u1()
            self.cam_reserved = self._io.read_u4le()
            self.comm_type = self._io.read_u1()
            self.comm_bus_voltage = self._io.read_u2le()
            self.comm_boot_count = self._io.read_u2le()
            self.comm_rssi = self._io.read_s1()
            self.comm_rssi_minimal = self._io.read_s1()
            self.comm_received_valid_packets = self._io.read_u1()
            self.comm_received_invalid_packets = self._io.read_u1()
            self.comm_sent_packets = self._io.read_u1()
            self.comm_status = self._io.read_u1()
            self.comm_mode = self._io.read_u1()
            self.comm_temperature = self._io.read_s1()
            self.comm_qso_received = self._io.read_u1()
            self.comm_reserved = self._io.read_u2le()


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
            self.callsign_ror = Geoscan.Callsign(_io__raw_callsign_ror, self, self._root)


    class CallsignEndRaw(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_end_str = (self._io.read_bytes(4)).decode(u"ASCII")


    class DataFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_header = Geoscan.DataHeader(self._io, self, self._root)
            self.data_payload = Geoscan.DataTlm(self._io, self, self._root)


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


