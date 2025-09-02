# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Foresail1(KaitaiStruct):
    """:field timestamp: pus.obc_housekeeping.timestamp.timestamp
    :field obc_side: pus.obc_housekeeping.side
    :field obc_fdir: pus.obc_housekeeping.fdir
    :field obc_scheduler: pus.obc_housekeeping.scheduler
    :field obc_sw_revision: pus.obc_housekeeping.software_revision
    :field obc_uptime: pus.obc_housekeeping.uptime
    :field obc_heap_free: pus.obc_housekeeping.heap_free
    :field obc_cpu_load: pus.obc_housekeeping.cpu_load
    :field obc_fs_free_space: pus.obc_housekeeping.fs_free_space
    :field arbiter_uptime: pus.obc_housekeeping.arbiter_uptime
    :field arbiter_age: pus.obc_housekeeping.arbiter_age
    :field arbiter_bootcount: pus.obc_housekeeping.arbiter_bootcount
    :field arbiter_temperature: pus.obc_housekeeping.arbiter_temperature
    :field side_a_bootcount: pus.obc_housekeeping.side_a_bootcount
    :field side_a_heartbeat: pus.obc_housekeeping.side_a_heartbeat
    :field side_a_fail_counter: pus.obc_housekeeping.side_a_fail_counter
    :field side_a_fail_reason: pus.obc_housekeeping.side_a_fail_reason
    :field side_b_bootcount: pus.obc_housekeeping.side_b_bootcount
    :field side_b_heartbeat: pus.obc_housekeeping.side_b_heartbeat
    :field side_b_fail_counter: pus.obc_housekeeping.side_b_fail_counter
    :field side_b_fail_reason: pus.obc_housekeeping.side_b_fail_reason
    
    :field timestamp: pus.eps_housekeeping.timestamp.timestamp
    :field pcdu_uptime: pus.eps_housekeeping.pcdu_uptime
    :field pcdu_boot_count: pus.eps_housekeeping.pcdu_boot_count
    :field pdm_expected: pus.eps_housekeeping.pdm_expected
    :field pdm_faulted: pus.eps_housekeeping.pdm_faulted
    :field pcdu_peak_detect_index: pus.eps_housekeeping.pcdu_peak_detect_index
    :field panel_x_minus_voltage: pus.eps_housekeeping.v_in_x_minus
    :field panel_x_plus_voltage: pus.eps_housekeeping.v_in_x_plus
    :field panel_y_minus_voltage: pus.eps_housekeeping.v_in_y_minus
    :field panel_y_plus_voltage: pus.eps_housekeeping.v_in_y_plus
    :field panel_x_minus_max_voltage: pus.eps_housekeeping.v_in_max_x_minus
    :field panel_x_plus_max_voltage: pus.eps_housekeeping.v_in_max_x_plus
    :field panel_y_minus_max_voltage: pus.eps_housekeeping.v_in_max_y_minus
    :field panel_y_plus_max_voltage: pus.eps_housekeeping.v_in_max_y_plus
    :field panel_x_minus_current: pus.eps_housekeeping.i_in_x_minus
    :field panel_x_plus_current: pus.eps_housekeeping.i_in_x_plus
    :field panel_y_minus_current: pus.eps_housekeeping.i_in_y_minus
    :field panel_y_plus_current: pus.eps_housekeeping.i_in_y_plus
    :field panel_x_minus_max_current: pus.eps_housekeeping.i_in_max_x_minus
    :field panel_x_plus_max_current: pus.eps_housekeeping.i_in_max_x_plus
    :field panel_y_minus_max_current: pus.eps_housekeeping.i_in_max_y_minus
    :field panel_y_plus_max_current: pus.eps_housekeeping.i_in_max_y_plus
    :field v_batt_bus: pus.eps_housekeeping.v_batt_bus
    :field temp_x_minus: pus.eps_housekeeping.temp_x_minus
    :field temp_x_plus: pus.eps_housekeeping.temp_x_plus
    :field temp_y_minus: pus.eps_housekeeping.temp_y_minus
    :field temp_y_plus: pus.eps_housekeeping.temp_y_plus
    :field temp_pcdu: pus.eps_housekeeping.temp_pcdu
    :field v_3v6_uhd_adcs: pus.eps_housekeeping.v_3v6_uhd_adcs
    :field v_3v6_mag_obc: pus.eps_housekeeping.v_3v6_mag_obc
    :field v_3v6_epb_cam: pus.eps_housekeeping.v_3v6_epb_cam
    :field i_pate_batt: pus.eps_housekeeping.i_pate_batt
    :field pb_batt_current: pus.eps_housekeeping.i_pb_batt
    :field pb_3v6_current: pus.eps_housekeeping.i_pb_3v6
    :field cam_3v6_current: pus.eps_housekeeping.i_cam_3v6
    :field mag_3v6_current: pus.eps_housekeeping.i_mag_3v6
    :field obc_3v6_current: pus.eps_housekeeping.i_obc_3v6
    :field uhf_3v6_current: pus.eps_housekeeping.i_uhf_3v6
    :field adcs_3v6_current: pus.eps_housekeeping.i_adcs_3v6
    :field pate_batt_current_max: pus.eps_housekeeping.i_pate_batt_max
    :field pb_batt_current_max: pus.eps_housekeeping.i_pb_batt_max
    :field pb_3v6_current_max: pus.eps_housekeeping.i_pb_3v6_max
    :field cam_3v6_current_max: pus.eps_housekeeping.i_cam_3v6_max
    :field mag_3v6_current_max: pus.eps_housekeeping.i_mag_3v6_max
    :field obc_3v6_current_max: pus.eps_housekeeping.i_obc_3v6_max
    :field uhf_3v6_current_max: pus.eps_housekeeping.i_uhf_3v6_max
    :field adcs_3v6_current_max: pus.eps_housekeeping.i_adcs_3v6_max
    :field pate_batt_current_min: pus.eps_housekeeping.i_pate_batt_min
    :field pb_batt_current_min: pus.eps_housekeeping.i_pb_batt_min
    :field pb_3v6_current_min: pus.eps_housekeeping.i_pb_3v6_min
    :field cam_3v6_current_min: pus.eps_housekeeping.i_cam_3v6_min
    :field mag_3v6_current_min: pus.eps_housekeeping.i_mag_3v6_min
    :field obc_3v6_current_min: pus.eps_housekeeping.i_obc_3v6_min
    :field uhf_3v6_current_min: pus.eps_housekeeping.i_uhf_3v6_min
    :field adcs_3v6_current_min: pus.eps_housekeeping.i_adcs_3v6_min
    :field batt_status: pus.eps_housekeeping.batt_status
    :field batt_boot_count: pus.eps_housekeeping.batt_boot_count
    :field batt_wdt_reset_count: pus.eps_housekeeping.batt_wdt_reset_count
    :field batt_bus_timeout_count: pus.eps_housekeeping.batt_bus_timeout_count
    :field batt_bpc_fail_count: pus.eps_housekeeping.batt_bpc_fail_count
    :field batt_pack_voltage: pus.eps_housekeeping.batt_pack_voltage
    :field batt_pack_lower_voltage: pus.eps_housekeeping.batt_pack_lower_voltage
    :field batt_pack_current: pus.eps_housekeeping.batt_pack_current
    :field batt_pack_min_current: pus.eps_housekeeping.batt_pack_min_current
    :field batt_pack_max_current: pus.eps_housekeeping.batt_pack_max_current
    :field batt_pack_temp: pus.eps_housekeeping.batt_pack_temp
    :field batt_board_temp: pus.eps_housekeeping.batt_board_temp
    :field batt_heater_pwm_on_time: pus.eps_housekeeping.heater_pwm_on_time
    
    :field timestamp: pus.uhf_housekeeping.timestamp.timestamp
    :field uhf_uptime: pus.uhf_housekeeping.uptime
    :field uhf_bootcount: pus.uhf_housekeeping.bootcount
    :field uhf_wdt_resets: pus.uhf_housekeeping.wdt_reset_count
    :field uhf_sbe_count: pus.uhf_housekeeping.sbe_count
    :field uhf_mbe_count: pus.uhf_housekeeping.mbe_count
    :field uhf_total_tx_frames: pus.uhf_housekeeping.total_tx_frames
    :field uhf_total_rx_frames: pus.uhf_housekeeping.total_rx_frames
    :field uhf_total_ham_tx_frames: pus.uhf_housekeeping.total_ham_tx_frames
    :field uhf_total_ham_rx_frames: pus.uhf_housekeeping.total_ham_rx_frames
    :field uhf_side: pus.uhf_housekeeping.side
    :field uhf_rx_mode: pus.uhf_housekeeping.rx_mode
    :field uhf_tx_mode: pus.uhf_housekeeping.tx_mode
    :field uhf_mcu_temperature: pus.uhf_housekeeping.mcu_temperature
    :field uhf_pa_temperature: pus.uhf_housekeeping.pa_temperature
    :field uhf_background_rssi: pus.uhf_housekeeping.backogrund_rssi
    :field uhf_last_rssi: pus.uhf_housekeeping.last_rssi
    :field uhf_last_freq_offset: pus.uhf_housekeeping.last_freq_offset
    
    :field timestamp: pus.adcs_housekeeping.timestamp.timestamp
    :field determination_mode: pus.adcs_housekeeping.determination_mode
    :field control_mode: pus.adcs_housekeeping.control_mode
    :field mjd: pus.adcs_housekeeping.mjd
    :field position_x: pus.adcs_housekeeping.position_x
    :field position_y: pus.adcs_housekeeping.position_y
    :field position_z: pus.adcs_housekeeping.position_z
    :field velocity_x: pus.adcs_housekeeping.velocity_x
    :field velocity_y: pus.adcs_housekeeping.velocity_y
    :field velocity_z: pus.adcs_housekeeping.velocity_z
    :field quaternion_x: pus.adcs_housekeeping.quaternion_x
    :field quaternion_y: pus.adcs_housekeeping.quaternion_y
    :field quaternion_z: pus.adcs_housekeeping.quaternion_z
    :field quaternion_w: pus.adcs_housekeeping.quaternion_w
    :field angular_rate_x: pus.adcs_housekeeping.angular_rate_x
    :field angular_rate_y: pus.adcs_housekeeping.angular_rate_y
    :field angular_rate_z: pus.adcs_housekeeping.angular_rate_z
    
    :field timestamp: pus.event.timestamp.timestamp
    :field event_severity: pus.event.severity
    :field event_rid: pus.event.rid
    :field event_info: pus.event.info
    
    :field repeater_dest_callsign: repeater.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field repeater_dest_ssid: repeater.ax25_header.dest_ssid_raw.ssid
    :field repeater_src_callsign: repeater.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field repeater_src_ssid: repeater.ax25_header.src_ssid_raw.ssid
    :field repeater_payload: repeater.payload
    
    .. seealso::
       Source - https://foresail.github.io/docs/FS1_Space_Ground_Interface_Control_Sheet.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.skylink = Foresail1.SkylinkFrame(self._io, self, self._root)
        if  ((self.skylink.vc == 0) or (self.skylink.vc == 1)) :
            self._raw_pus = self._io.read_bytes(((self._io.size() - self._io.pos()) - (8 * self.skylink.is_authenticated)))
            _io__raw_pus = KaitaiStream(BytesIO(self._raw_pus))
            self.pus = Foresail1.ForesailPusFrame(_io__raw_pus, self, self._root)

        if self.skylink.vc == 3:
            self._raw_repeater = self._io.read_bytes(((self._io.size() - self._io.pos()) - (8 * self.skylink.is_authenticated)))
            _io__raw_repeater = KaitaiStream(BytesIO(self._raw_repeater))
            self.repeater = Foresail1.Ax25Frame(_io__raw_repeater, self, self._root)

        if self.skylink.is_authenticated == 1:
            self.auth = self._io.read_bytes(8)


    class Ax25Frame(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.tapr.org/pdf/AX25.2.2.pdf
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start_flag = self._io.read_bytes(1)
            if not self.start_flag == b"\x7E":
                raise kaitaistruct.ValidationNotEqualError(b"\x7E", self.start_flag, self._io, u"/types/ax25_frame/seq/0")
            self.ax25_header = Foresail1.Ax25Header(self._io, self, self._root)
            self.payload = (KaitaiStream.bytes_terminate(self._io.read_bytes((((self._io.size() - self._io.pos()) - 3) - (8 * self._root.skylink.is_authenticated))), 0, False)).decode(u"ascii")
            self.fcs = self._io.read_u2be()
            self.end_flag = self._io.read_bytes(1)
            if not self.end_flag == b"\x7E":
                raise kaitaistruct.ValidationNotEqualError(b"\x7E", self.end_flag, self._io, u"/types/ax25_frame/seq/4")


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Foresail1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Foresail1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Foresail1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Foresail1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()
            self.pid = self._io.read_u1()


    class PusHeader(KaitaiStruct):
        """CCSDS PUS header."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.packet_id = self._io.read_u2be()
            self.sequence = self._io.read_u2be()
            self.length = self._io.read_u2be()
            self.secondary_header = self._io.read_u1()
            self.service_type = self._io.read_u1()
            self.service_subtype = self._io.read_u1()


    class AdcsHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Foresail1.UnixTimestamp(self._io, self, self._root)
            self.determination_mode = self._io.read_u1()
            self.control_mode = self._io.read_u1()
            self.mjd = self._io.read_f4le()
            self.position_x = self._io.read_f4le()
            self.position_y = self._io.read_f4le()
            self.position_z = self._io.read_f4le()
            self.velocity_x = self._io.read_f4le()
            self.velocity_y = self._io.read_f4le()
            self.velocity_z = self._io.read_f4le()
            self.angular_rate_x = self._io.read_f4le()
            self.angular_rate_y = self._io.read_f4le()
            self.angular_rate_z = self._io.read_f4le()
            self.quaternion_x = self._io.read_f4le()
            self.quaternion_y = self._io.read_f4le()
            self.quaternion_z = self._io.read_f4le()
            self.quaternion_w = self._io.read_f4le()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self.ax25_info = self._io.read_bytes_full()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class UhfHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Foresail1.UnixTimestamp(self._io, self, self._root)
            self.uptime = self._io.read_u4le()
            self.bootcount = self._io.read_u2le()
            self.wdt_reset_count = self._io.read_u1()
            self.sbe_count = self._io.read_u1()
            self.mbe_count = self._io.read_u1()
            self.bus_sync_errors = self._io.read_u1()
            self.bus_len_errors = self._io.read_u1()
            self.bus_crc_errors = self._io.read_u1()
            self.bus_bug_errors = self._io.read_u1()
            self.total_tx_frames = self._io.read_u4le()
            self.total_rx_frames = self._io.read_u4le()
            self.total_ham_tx_frames = self._io.read_u4le()
            self.total_ham_rx_frames = self._io.read_u4le()
            self.side = self._io.read_u1()
            self.rx_mode = self._io.read_u1()
            self.tx_mode = self._io.read_u1()
            self.mcu_temperature = self._io.read_s2le()
            self.pa_temperature = self._io.read_s2le()
            self.background_rssi = self._io.read_s1()
            self.last_rssi = self._io.read_s1()
            self.last_freq_offset = self._io.read_s2le()


    class UnixTimestamp(KaitaiStruct):
        """Unix timestamp."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = self._io.read_u4be()


    class Event(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Foresail1.UnixTimestamp(self._io, self, self._root)
            self.rid = self._io.read_u2be()
            self.info = self._io.read_bytes_full()


    class EpsHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Foresail1.UnixTimestamp(self._io, self, self._root)
            self.pcdu_uptime = self._io.read_u4le()
            self.pcdu_boot_count = self._io.read_u1()
            self.pdm_expected = self._io.read_u1()
            self.pdm_faulted = self._io.read_u1()
            self.pcdu_peak_detect_index = self._io.read_u1()
            self.v_in_x_minus = self._io.read_u2le()
            self.v_in_x_plus = self._io.read_u2le()
            self.v_in_y_minus = self._io.read_u2le()
            self.v_in_y_plus = self._io.read_u2le()
            self.v_in_max_x_minus = self._io.read_u2le()
            self.v_in_max_x_plus = self._io.read_u2le()
            self.v_in_max_y_minus = self._io.read_u2le()
            self.v_in_max_y_plus = self._io.read_u2le()
            self.i_in_x_minus = self._io.read_u2le()
            self.i_in_x_plus = self._io.read_u2le()
            self.i_in_y_minus = self._io.read_u2le()
            self.i_in_y_plus = self._io.read_u2le()
            self.i_in_max_x_minus = self._io.read_u2le()
            self.i_in_max_x_plus = self._io.read_u2le()
            self.i_in_max_y_minus = self._io.read_u2le()
            self.i_in_max_y_plus = self._io.read_u2le()
            self.v_batt_bus = self._io.read_u2le()
            self.temp_x_minus = self._io.read_s2le()
            self.temp_x_plus = self._io.read_s2le()
            self.temp_y_minus = self._io.read_s2le()
            self.temp_y_plus = self._io.read_s2le()
            self.temp_pcdu = self._io.read_s2le()
            self.v_3v6_uhd_adcs = self._io.read_u2le()
            self.v_3v6_mag_obc = self._io.read_u2le()
            self.v_3v6_epb_cam = self._io.read_u2le()
            self.i_pate_batt = self._io.read_u2le()
            self.i_pb_batt = self._io.read_u2le()
            self.i_pb_3v6 = self._io.read_u2le()
            self.i_cam_3v6 = self._io.read_u2le()
            self.i_mag_3v6 = self._io.read_u2le()
            self.i_obc_3v6 = self._io.read_u2le()
            self.i_uhf_3v6 = self._io.read_u2le()
            self.i_adcs_3v6 = self._io.read_u2le()
            self.i_pate_batt_max = self._io.read_u2le()
            self.i_pb_batt_max = self._io.read_u2le()
            self.i_pb_3v6_max = self._io.read_u2le()
            self.i_cam_3v6_max = self._io.read_u2le()
            self.i_mag_3v6_max = self._io.read_u2le()
            self.i_obc_3v6_max = self._io.read_u2le()
            self.i_uhf_3v6_max = self._io.read_u2le()
            self.i_adcs_3v6_max = self._io.read_u2le()
            self.i_pate_batt_min = self._io.read_u2le()
            self.i_pb_batt_min = self._io.read_u2le()
            self.i_pb_3v6_min = self._io.read_u2le()
            self.i_cam_3v6_min = self._io.read_u2le()
            self.i_mag_3v6_min = self._io.read_u2le()
            self.i_obc_3v6_min = self._io.read_u2le()
            self.i_uhf_3v6_min = self._io.read_u2le()
            self.i_adcs_3v6_min = self._io.read_u2le()
            self.batt_status = self._io.read_u2le()
            self.batt_boot_count = self._io.read_u1()
            self.batt_wdt_reset_count = self._io.read_u1()
            self.batt_bus_timeout_count = self._io.read_u1()
            self.batt_bpc_fail_count = self._io.read_u1()
            self.batt_pack_voltage = self._io.read_u2le()
            self.batt_pack_lower_voltage = self._io.read_u2le()
            self.batt_pack_current = self._io.read_s2le()
            self.batt_pack_min_current = self._io.read_s2le()
            self.batt_pack_max_current = self._io.read_s2le()
            self.batt_pack_temp = self._io.read_s2le()
            self.batt_board_temp = self._io.read_s2le()
            self.heater_pwm_on_time = self._io.read_u2le()


    class ForesailPusFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Foresail1.PusHeader(self._io, self, self._root)
            if  ((self.header.service_type == 3) and (self.header.service_subtype == 2)) :
                self.obc_housekeeping = Foresail1.ObcHousekeeping(self._io, self, self._root)

            if  ((self.header.service_type == 3) and (self.header.service_subtype == 3)) :
                self.eps_housekeeping = Foresail1.EpsHousekeeping(self._io, self, self._root)

            if  ((self.header.service_type == 3) and (self.header.service_subtype == 4)) :
                self.uhf_housekeeping = Foresail1.UhfHousekeeping(self._io, self, self._root)

            if  ((self.header.service_type == 3) and (self.header.service_subtype == 5)) :
                self.adcs_housekeeping = Foresail1.AdcsHousekeeping(self._io, self, self._root)

            if  ((self.header.service_type == 4) and ( ((self.header.service_subtype == 1) or (self.header.service_subtype == 2) or (self.header.service_subtype == 3) or (self.header.service_subtype == 4)) )) :
                self.event = Foresail1.Event(self._io, self, self._root)



    class Pdms(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.val = self._io.read_u1()

        @property
        def mag_3v6(self):
            if hasattr(self, '_m_mag_3v6'):
                return self._m_mag_3v6

            self._m_mag_3v6 = ((self.val & 16) >> 4)
            return getattr(self, '_m_mag_3v6', None)

        @property
        def uhf_3v6(self):
            if hasattr(self, '_m_uhf_3v6'):
                return self._m_uhf_3v6

            self._m_uhf_3v6 = ((self.val & 64) >> 6)
            return getattr(self, '_m_uhf_3v6', None)

        @property
        def pate_batt(self):
            if hasattr(self, '_m_pate_batt'):
                return self._m_pate_batt

            self._m_pate_batt = ((self.val & 1) >> 0)
            return getattr(self, '_m_pate_batt', None)

        @property
        def obc_3v6(self):
            if hasattr(self, '_m_obc_3v6'):
                return self._m_obc_3v6

            self._m_obc_3v6 = ((self.val & 32) >> 5)
            return getattr(self, '_m_obc_3v6', None)

        @property
        def cam_3v6(self):
            if hasattr(self, '_m_cam_3v6'):
                return self._m_cam_3v6

            self._m_cam_3v6 = ((self.val & 8) >> 3)
            return getattr(self, '_m_cam_3v6', None)

        @property
        def pb_3v6(self):
            if hasattr(self, '_m_pb_3v6'):
                return self._m_pb_3v6

            self._m_pb_3v6 = ((self.val & 4) >> 2)
            return getattr(self, '_m_pb_3v6', None)

        @property
        def adcs_3v6(self):
            if hasattr(self, '_m_adcs_3v6'):
                return self._m_adcs_3v6

            self._m_adcs_3v6 = ((self.val & 128) >> 7)
            return getattr(self, '_m_adcs_3v6', None)

        @property
        def pb_batt(self):
            if hasattr(self, '_m_pb_batt'):
                return self._m_pb_batt

            self._m_pb_batt = ((self.val & 2) >> 1)
            return getattr(self, '_m_pb_batt', None)


    class SkylinkFrame(KaitaiStruct):
        """
        .. seealso::
           Skylink Protocol Specification.pdf
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start_byte = self._io.read_bytes(1)
            if not self.start_byte == b"\x66":
                raise kaitaistruct.ValidationNotEqualError(b"\x66", self.start_byte, self._io, u"/types/skylink_frame/seq/0")
            self.identity = self._io.read_bytes(6)
            if not self.identity == b"\x4F\x48\x32\x46\x31\x53":
                raise kaitaistruct.ValidationNotEqualError(b"\x4F\x48\x32\x46\x31\x53", self.identity, self._io, u"/types/skylink_frame/seq/1")
            self.control = self._io.read_u1()
            self.len_extension = self._io.read_u1()
            self.sequence_number = self._io.read_u2be()
            self.extensions = self._io.read_bytes(self.len_extension)

        @property
        def has_payload(self):
            if hasattr(self, '_m_has_payload'):
                return self._m_has_payload

            self._m_has_payload = ((self.control & 32) >> 5)
            return getattr(self, '_m_has_payload', None)

        @property
        def arq_on(self):
            if hasattr(self, '_m_arq_on'):
                return self._m_arq_on

            self._m_arq_on = ((self.control & 16) >> 4)
            return getattr(self, '_m_arq_on', None)

        @property
        def is_authenticated(self):
            if hasattr(self, '_m_is_authenticated'):
                return self._m_is_authenticated

            self._m_is_authenticated = ((self.control & 8) >> 3)
            return getattr(self, '_m_is_authenticated', None)

        @property
        def vc(self):
            if hasattr(self, '_m_vc'):
                return self._m_vc

            self._m_vc = ((self.control & 7) >> 0)
            return getattr(self, '_m_vc', None)


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
            self.callsign_ror = Foresail1.Callsign(_io__raw_callsign_ror, self, self._root)


    class ObcHousekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp = Foresail1.UnixTimestamp(self._io, self, self._root)
            self.side = self._io.read_u1()
            self.fdir = self._io.read_u1()
            self.scheduler = self._io.read_u1()
            self.software_revision = self._io.read_u1()
            self.uptime = self._io.read_u4le()
            self.heap_free = self._io.read_u1()
            self.cpu_load = self._io.read_u1()
            self.fs_free_space = self._io.read_u2le()
            self.arbiter_uptime = self._io.read_u2le()
            self.arbiter_age = self._io.read_u2le()
            self.arbiter_bootcount = self._io.read_u2le()
            self.arbiter_temperature = self._io.read_s2le()
            self.side_a_bootcount = self._io.read_u1()
            self.side_a_heartbeat = self._io.read_u1()
            self.side_a_fail_counter = self._io.read_u1()
            self.side_a_fail_reason = self._io.read_u1()
            self.side_b_bootcount = self._io.read_u1()
            self.side_b_heartbeat = self._io.read_u1()
            self.side_b_fail_counter = self._io.read_u1()
            self.side_b_fail_reason = self._io.read_u1()
            self.arbiter_log_1 = self._io.read_u1()
            self.arbiter_log_2 = self._io.read_u1()
            self.arbiter_log_3 = self._io.read_u1()
            self.arbiter_log_4 = self._io.read_u1()



