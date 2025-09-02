# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Qube(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field rf_message: ax25_frame.payload.ax25_info.beacon_payload.message
    :field csp_header: ax25_frame.payload.ax25_info.csp_header
    :field compass_header_flags1: ax25_frame.payload.ax25_info.compass_header.flags1
    :field compass_header_flags2: ax25_frame.payload.ax25_info.compass_header.flags2
    :field compass_header_packet_id: ax25_frame.payload.ax25_info.compass_header.packet_id
    :field compass_header_fm_system_id: ax25_frame.payload.ax25_info.compass_header.fm_system_id
    :field compass_header_fm_subsystem_id: ax25_frame.payload.ax25_info.compass_header.fm_subsystem_id
    :field compass_header_to_system_id: ax25_frame.payload.ax25_info.compass_header.to_system_id
    :field compass_header_to_subsystem_id: ax25_frame.payload.ax25_info.compass_header.to_subsystem_id
    :field compass_header_api: ax25_frame.payload.ax25_info.compass_header.api
    :field compass_header_payload_size: ax25_frame.payload.ax25_info.compass_header.payload_size
    :field beacon_header_model: ax25_frame.payload.ax25_info.payload.beacon_header.model_type
    :field beacon_header_uid: ax25_frame.payload.ax25_info.payload.beacon_header.uid
    :field beacon_header_type: ax25_frame.payload.ax25_info.payload.beacon_header.type
    :field beacon_header_length: ax25_frame.payload.ax25_info.payload.beacon_header.length
    :field beacon_header_timestamp: ax25_frame.payload.ax25_info.payload.beacon_header.timestamp_raw.timestamp
    :field beacon_payload_beacon_rate: ax25_frame.payload.ax25_info.payload.beacon_payload.beacon_rate
    :field beacon_payload_uptime: ax25_frame.payload.ax25_info.payload.beacon_payload.uptime
    :field beacon_payload_status_aocs_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.aocs_active
    :field beacon_payload_status_radio2_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.radio2_active
    :field beacon_payload_status_powerpath_b_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.powerpath_b_active
    :field beacon_payload_status_powerpath_a_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.powerpath_a_active
    :field beacon_payload_status_mcub_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.is_mcu_b_active
    :field beacon_payload_status_panel_neg_x_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.panel_x_neg_active
    :field beacon_payload_status_panel_pos_x_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.panel_x_pos_active
    :field beacon_payload_status_panel_neg_y_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.panel_y_neg_active
    :field beacon_payload_status_panel_pos_y_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.panel_y_pos_active
    :field beacon_payload_status_panel_neg_z_active: ax25_frame.payload.ax25_info.payload.beacon_payload.status_flags.panel_z_neg_active
    :field beacon_payload_powerpath_a_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_a_temp_soc.temp
    :field beacon_payload_powerpath_a_state_of_charge: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_a_temp_soc.soc
    :field beacon_payload_powerpath_b_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_b_temp_soc.temp
    :field beacon_payload_powerpath_b_state_of_charge: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_b_temp_soc.soc
    :field beacon_payload_powerpath_a_voltage: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_a_iup.u
    :field beacon_payload_powerpath_a_current: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_a_iup.i
    :field beacon_payload_powerpath_a_power: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_a_iup.p
    :field beacon_payload_powerpath_b_voltage: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_b_iup.u
    :field beacon_payload_powerpath_b_current: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_b_iup.i
    :field beacon_payload_powerpath_b_power: ax25_frame.payload.ax25_info.payload.beacon_payload.powerpath_b_iup.p
    :field beacon_payload_power_consumption: ax25_frame.payload.ax25_info.payload.beacon_payload.power_total
    :field beacon_payload_obc_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_obc
    :field beacon_payload_panel_neg_x_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_panel.xneg
    :field beacon_payload_panel_pos_x_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_panel.xpos
    :field beacon_payload_panel_neg_y_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_panel.yneg
    :field beacon_payload_panel_pos_y_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_panel.ypos
    :field beacon_payload_panel_neg_z_temp: ax25_frame.payload.ax25_info.payload.beacon_payload.temperature_panel.zneg
    :field beacon_payload_seu_ram: ax25_frame.payload.ax25_info.payload.beacon_payload.seu_ram
    :field beacon_payload_seu_rom: ax25_frame.payload.ax25_info.payload.beacon_payload.seu_rom
    :field beacon_payload_freq: ax25_frame.payload.ax25_info.payload.beacon_payload.frequency_radio
    :field beacon_payload_misc: ax25_frame.payload.ax25_info.payload.compass_misc
    :field beacon_payload_crc: ax25_frame.payload.ax25_info.payload.frame_crc32c
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Qube.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Qube.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Qube.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Qube.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Qube.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Qube.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Qube.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Qube.IFrame(self._io, self, self._root)


    class QubeBeacon(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_header = Qube.BeaconHeader(self._io, self, self._root)
            _on = self.beacon_header.length
            if _on == 42:
                self.beacon_payload = Qube.TelemetryPayload(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Qube.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Qube.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Qube.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Qube.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class TemperaturePanel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.xpos = self._io.read_s1()
            self.xneg = self._io.read_s1()
            self.ypos = self._io.read_s1()
            self.yneg = self._io.read_s1()
            self.zneg = self._io.read_s1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            _on = self._parent.ax25_header.src_callsign_raw.callsign_ror.is_qube
            if _on == True:
                self._raw_ax25_info = self._io.read_bytes_full()
                _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
                self.ax25_info = Qube.QubeFrame(_io__raw_ax25_info, self, self._root)
            else:
                self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(5)).decode(u"utf-8")

        @property
        def is_qube(self):
            if hasattr(self, '_m_is_qube'):
                return self._m_is_qube

            self._m_is_qube = self.callsign == u"DP2QU"
            return getattr(self, '_m_is_qube', None)


    class QubeFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = self._io.read_u4le()
            self._raw_compass_header = self._io.read_bytes(10)
            _io__raw_compass_header = KaitaiStream(BytesIO(self._raw_compass_header))
            self.compass_header = Qube.CompassHeader(_io__raw_compass_header, self, self._root)
            _on = self.compass_header.api
            if _on == 14:
                self._raw_payload = self._io.read_bytes(self.compass_header.payload_size)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qube.QubeBeacon(_io__raw_payload, self, self._root)
            elif _on == 103:
                self._raw_payload = self._io.read_bytes(self.compass_header.payload_size)
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = Qube.QubeRfMessage(_io__raw_payload, self, self._root)
            else:
                self.payload = self._io.read_bytes(self.compass_header.payload_size)
            self.compass_misc = self._io.read_u2le()
            self.frame_crc32c = self._io.read_u4le()


    class QubeRfMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.offset_0 = []
            for i in range(6):
                self.offset_0.append(self._io.read_u1())

            self.message = (self._io.read_bytes((self._parent.compass_header.payload_size - 6))).decode(u"utf-8")
            self.rf_message_crc = self._io.read_u2le()


    class BeaconHeaderTimestamp(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_header_ts = []
            for i in range(6):
                self.beacon_header_ts.append(self._io.read_u1())


        @property
        def timestamp_lsb(self):
            if hasattr(self, '_m_timestamp_lsb'):
                return self._m_timestamp_lsb

            self._m_timestamp_lsb = (((self.beacon_header_ts[0] + (self.beacon_header_ts[1] << 8)) + (self.beacon_header_ts[2] << 16)) + (self.beacon_header_ts[3] << 24))
            return getattr(self, '_m_timestamp_lsb', None)

        @property
        def timestamp_msb(self):
            if hasattr(self, '_m_timestamp_msb'):
                return self._m_timestamp_msb

            self._m_timestamp_msb = ((self.beacon_header_ts[4] + (self.beacon_header_ts[5] << 8)) + 1)
            return getattr(self, '_m_timestamp_msb', None)

        @property
        def timestamp(self):
            """padded unix timestamp (64bit) in ms."""
            if hasattr(self, '_m_timestamp'):
                return self._m_timestamp

            self._m_timestamp = (((self.timestamp_msb * 4294967296) + self.timestamp_lsb) - 4294967296)
            return getattr(self, '_m_timestamp', None)


    class PpIUP(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_s2le()
            self.i = self._io.read_s2le()
            self.p = self._io.read_s2le()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


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


    class CompassHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags1 = self._io.read_u1()
            self.flags2 = self._io.read_u1()
            self.packet_id = self._io.read_u2le()
            self.fm_system_id = self._io.read_u1()
            self.fm_subsystem_id = self._io.read_u1()
            self.to_system_id = self._io.read_u1()
            self.to_subsystem_id = self._io.read_u1()
            self.api = self._io.read_u1()
            self.payload_size = self._io.read_u1()


    class BeaconHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.model_type = self._io.read_u1()
            self.uid = self._io.read_u2le()
            self.type = self._io.read_u1()
            self.length = self._io.read_u1()
            self._raw_timestamp_raw = self._io.read_bytes(6)
            _io__raw_timestamp_raw = KaitaiStream(BytesIO(self._raw_timestamp_raw))
            self.timestamp_raw = Qube.BeaconHeaderTimestamp(_io__raw_timestamp_raw, self, self._root)


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
            self.callsign_ror = Qube.Callsign(_io__raw_callsign_ror, self, self._root)


    class TelemetryPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.beacon_rate = self._io.read_u4le()
            self.uptime = self._io.read_u4le()
            self._raw_status_flags = self._io.read_bytes(2)
            _io__raw_status_flags = KaitaiStream(BytesIO(self._raw_status_flags))
            self.status_flags = Qube.BeaconStatusFlags(_io__raw_status_flags, self, self._root)
            self.powerpath_a_temp_soc = Qube.PpTempsoc(self._io, self, self._root)
            self.powerpath_b_temp_soc = Qube.PpTempsoc(self._io, self, self._root)
            self.powerpath_a_iup = Qube.PpIUP(self._io, self, self._root)
            self.powerpath_b_iup = Qube.PpIUP(self._io, self, self._root)
            self.power_total = self._io.read_s4le()
            self.temperature_obc = self._io.read_s1()
            self.temperature_panel = Qube.TemperaturePanel(self._io, self, self._root)
            self.frequency_radio = self._io.read_u4le()
            self.seu_rom = self._io.read_u1()
            self.seu_ram = self._io.read_u1()


    class BeaconStatusFlags(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.blank_012 = self._io.read_bits_int_be(3)
            self.aocs_active = self._io.read_bits_int_be(1) != 0
            self.radio_2_active = self._io.read_bits_int_be(1) != 0
            self.powerpath_b_active = self._io.read_bits_int_be(1) != 0
            self.powerpath_a_active = self._io.read_bits_int_be(1) != 0
            self.is_mcu_b_active = self._io.read_bits_int_be(1) != 0
            self.blank_mode = self._io.read_bits_int_be(2)
            self.panel_xneg_active = self._io.read_bits_int_be(1) != 0
            self.panel_xpos_active = self._io.read_bits_int_be(1) != 0
            self.panel_yneg_active = self._io.read_bits_int_be(1) != 0
            self.panel_ypos_active = self._io.read_bits_int_be(1) != 0
            self.panel_zneg_active = self._io.read_bits_int_be(1) != 0
            self.blank_15 = self._io.read_bits_int_be(1) != 0


    class PpTempsoc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.temp = self._io.read_s1()
            self.soc = self._io.read_s1()



