# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Astrocast(KaitaiStruct):
    """:field dest_callsign: ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_header.src_callsign_raw.callsign_ror.callsign
    :field utc_time_of_position_h: gprmc.utc_time_of_position_h
    :field utc_time_of_position_m: gprmc.utc_time_of_position_m
    :field utc_time_of_position_s: gprmc.utc_time_of_position_s
    :field status: gprmc.status
    :field latitude: gprmc.latitude
    :field latitude_n_or_s: gprmc.latitude_n_or_s
    :field longitude: gprmc.longitude
    :field longitude_e_or_w: gprmc.longitude_e_or_w
    :field ground_speed_knots: gprmc.ground_speed_knots
    :field course_over_ground: gprmc.course_over_ground
    :field date_yy: gprmc.date_yy
    :field date_mm: gprmc.date_mm
    :field date_dd: gprmc.date_dd
    :field magnetic_variation: gprmc.magnetic_variation
    :field magnetic_variation_e_or_w: gprmc.magnetic_variation_e_or_w
    :field timestamp_seconds: tlm.timestamp_seconds
    :field voltage_v: tlm.voltage_v
    :field current_ma: tlm.current_ma
    :field temperature_c: tlm.temperature_c
    :field rssi_dbm: tlm.rssi_dbm
    :field afc_hz: tlm.afc_hz
    :field link_settings: tlm.link_settings
    :field transfer_layer_idle_frames: tlm.transfer_layer_idle_frames
    :field downlink_reed_solomon: tlm.downlink_reed_solomon
    :field downlink_randomizer: tlm.downlink_randomizer
    :field downlink_convolutional: tlm.downlink_convolutional
    :field uplink_bch: tlm.uplink_bch
    :field uplink_derandomizer: tlm.uplink_derandomizer
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_header = Astrocast.Ax25Header(self._io, self, self._root)
        self.gprmc = Astrocast.Gprmc(self._io, self, self._root)
        self.tlm = Astrocast.Tlm(self._io, self, self._root)

    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Astrocast.CallsignRaw(self._io, self, self._root)
            self.dest_ssid = self._io.read_u1()
            self.src_callsign_raw = Astrocast.CallsignRaw(self._io, self, self._root)
            self.src_ssid = self._io.read_u1()
            self.ctl_pid = self._io.read_u2be()


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


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
            self.callsign_ror = Astrocast.Callsign(_io__raw_callsign_ror, self, self._root)


    class Tlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_prefix = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.skip_0x = self._io.read_u2be()
            self.timestamp_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.voltage_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"UTF-8")
            self.voltage_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.current_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.temperature_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.rssi_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.afc_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.skipping_0x = self._io.read_u2be()
            self.link_settings_raw = (self._io.read_bytes(2)).decode(u"UTF-8")

        @property
        def current_ma(self):
            if hasattr(self, '_m_current_ma'):
                return self._m_current_ma

            self._m_current_ma = int(self.current_raw)
            return getattr(self, '_m_current_ma', None)

        @property
        def uplink_bch(self):
            if hasattr(self, '_m_uplink_bch'):
                return self._m_uplink_bch

            self._m_uplink_bch = (True if ((self.link_settings & 8) >> 3) == 1 else False)
            return getattr(self, '_m_uplink_bch', None)

        @property
        def downlink_randomizer(self):
            if hasattr(self, '_m_downlink_randomizer'):
                return self._m_downlink_randomizer

            self._m_downlink_randomizer = (True if ((self.link_settings & 32) >> 5) == 1 else False)
            return getattr(self, '_m_downlink_randomizer', None)

        @property
        def voltage_after_dot(self):
            if hasattr(self, '_m_voltage_after_dot'):
                return self._m_voltage_after_dot

            self._m_voltage_after_dot = int(self.voltage_after_dot_raw)
            return getattr(self, '_m_voltage_after_dot', None)

        @property
        def rssi_dbm(self):
            if hasattr(self, '_m_rssi_dbm'):
                return self._m_rssi_dbm

            self._m_rssi_dbm = int(self.rssi_raw)
            return getattr(self, '_m_rssi_dbm', None)

        @property
        def voltage_v(self):
            if hasattr(self, '_m_voltage_v'):
                return self._m_voltage_v

            self._m_voltage_v = ((self.voltage_after_dot * 0.001) + self.voltage_before_dot)
            return getattr(self, '_m_voltage_v', None)

        @property
        def downlink_convolutional(self):
            if hasattr(self, '_m_downlink_convolutional'):
                return self._m_downlink_convolutional

            self._m_downlink_convolutional = (True if ((self.link_settings & 16) >> 4) == 1 else False)
            return getattr(self, '_m_downlink_convolutional', None)

        @property
        def transfer_layer_idle_frames(self):
            if hasattr(self, '_m_transfer_layer_idle_frames'):
                return self._m_transfer_layer_idle_frames

            self._m_transfer_layer_idle_frames = (True if ((self.link_settings & 128) >> 7) == 1 else False)
            return getattr(self, '_m_transfer_layer_idle_frames', None)

        @property
        def downlink_reed_solomon(self):
            if hasattr(self, '_m_downlink_reed_solomon'):
                return self._m_downlink_reed_solomon

            self._m_downlink_reed_solomon = (True if ((self.link_settings & 64) >> 6) == 1 else False)
            return getattr(self, '_m_downlink_reed_solomon', None)

        @property
        def timestamp_ticks(self):
            if hasattr(self, '_m_timestamp_ticks'):
                return self._m_timestamp_ticks

            self._m_timestamp_ticks = int(self.timestamp_raw, 16)
            return getattr(self, '_m_timestamp_ticks', None)

        @property
        def uplink_derandomizer(self):
            if hasattr(self, '_m_uplink_derandomizer'):
                return self._m_uplink_derandomizer

            self._m_uplink_derandomizer = (True if ((self.link_settings & 4) >> 2) == 1 else False)
            return getattr(self, '_m_uplink_derandomizer', None)

        @property
        def afc_hz(self):
            if hasattr(self, '_m_afc_hz'):
                return self._m_afc_hz

            self._m_afc_hz = int(self.afc_raw)
            return getattr(self, '_m_afc_hz', None)

        @property
        def timestamp_seconds(self):
            if hasattr(self, '_m_timestamp_seconds'):
                return self._m_timestamp_seconds

            self._m_timestamp_seconds = self.timestamp_ticks // 65536
            return getattr(self, '_m_timestamp_seconds', None)

        @property
        def temperature_c(self):
            if hasattr(self, '_m_temperature_c'):
                return self._m_temperature_c

            self._m_temperature_c = int(self.temperature_raw)
            return getattr(self, '_m_temperature_c', None)

        @property
        def link_settings(self):
            if hasattr(self, '_m_link_settings'):
                return self._m_link_settings

            self._m_link_settings = int(self.link_settings_raw, 16)
            return getattr(self, '_m_link_settings', None)

        @property
        def voltage_before_dot(self):
            if hasattr(self, '_m_voltage_before_dot'):
                return self._m_voltage_before_dot

            self._m_voltage_before_dot = int(self.voltage_before_dot_raw)
            return getattr(self, '_m_voltage_before_dot', None)


    class Gprmc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gprmc_prefix = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.utc_time_of_position_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.status = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.latitude_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.latitude_n_or_s = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.longitude_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.longitude_e_or_w = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.ground_speed_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.course_over_ground_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"UTF-8")
            self.course_over_ground_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.date_str = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.magnetic_variation_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"UTF-8")
            self.magnetic_variation_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"UTF-8")
            self.magnetic_variation_e_or_w = (self._io.read_bytes_term(42, False, True, True)).decode(u"UTF-8")

        @property
        def utc_time_of_position_ss_after_dot(self):
            if hasattr(self, '_m_utc_time_of_position_ss_after_dot'):
                return self._m_utc_time_of_position_ss_after_dot

            self._m_utc_time_of_position_ss_after_dot = int((self.utc_time_of_position_raw)[7:9])
            return getattr(self, '_m_utc_time_of_position_ss_after_dot', None)

        @property
        def latitude_deg(self):
            if hasattr(self, '_m_latitude_deg'):
                return self._m_latitude_deg

            self._m_latitude_deg = int((self.latitude_str)[0:2])
            return getattr(self, '_m_latitude_deg', None)

        @property
        def date_mm(self):
            if hasattr(self, '_m_date_mm'):
                return self._m_date_mm

            self._m_date_mm = int((self.date_str)[2:4])
            return getattr(self, '_m_date_mm', None)

        @property
        def ground_speed_knots(self):
            if hasattr(self, '_m_ground_speed_knots'):
                return self._m_ground_speed_knots

            self._m_ground_speed_knots = int(self.ground_speed_raw)
            return getattr(self, '_m_ground_speed_knots', None)

        @property
        def magnetic_variation_after_dot(self):
            if hasattr(self, '_m_magnetic_variation_after_dot'):
                return self._m_magnetic_variation_after_dot

            self._m_magnetic_variation_after_dot = int(self.magnetic_variation_after_dot_raw)
            return getattr(self, '_m_magnetic_variation_after_dot', None)

        @property
        def utc_time_of_position_s(self):
            if hasattr(self, '_m_utc_time_of_position_s'):
                return self._m_utc_time_of_position_s

            self._m_utc_time_of_position_s = ((self.utc_time_of_position_ss_after_dot * 0.01) + self.utc_time_of_position_ss_before_dot)
            return getattr(self, '_m_utc_time_of_position_s', None)

        @property
        def date_dd(self):
            if hasattr(self, '_m_date_dd'):
                return self._m_date_dd

            self._m_date_dd = int((self.date_str)[0:2])
            return getattr(self, '_m_date_dd', None)

        @property
        def course_over_ground(self):
            if hasattr(self, '_m_course_over_ground'):
                return self._m_course_over_ground

            self._m_course_over_ground = ((self.course_over_ground_after_dot * 0.1) + self.course_over_ground_before_dot)
            return getattr(self, '_m_course_over_ground', None)

        @property
        def latitude(self):
            if hasattr(self, '_m_latitude'):
                return self._m_latitude

            self._m_latitude = ((((self.latitude_min_after_dot * 0.01) + self.latitude_min_before_dot) / 60) + self.latitude_deg)
            return getattr(self, '_m_latitude', None)

        @property
        def course_over_ground_before_dot(self):
            if hasattr(self, '_m_course_over_ground_before_dot'):
                return self._m_course_over_ground_before_dot

            self._m_course_over_ground_before_dot = int(self.course_over_ground_before_dot_raw)
            return getattr(self, '_m_course_over_ground_before_dot', None)

        @property
        def longitude(self):
            if hasattr(self, '_m_longitude'):
                return self._m_longitude

            self._m_longitude = ((((self.longitude_min_after_dot * 0.01) + self.longitude_min_before_dot) / 60) + self.longitude_deg)
            return getattr(self, '_m_longitude', None)

        @property
        def latitude_min_after_dot(self):
            if hasattr(self, '_m_latitude_min_after_dot'):
                return self._m_latitude_min_after_dot

            self._m_latitude_min_after_dot = int((self.latitude_str)[5:7])
            return getattr(self, '_m_latitude_min_after_dot', None)

        @property
        def longitude_min_before_dot(self):
            if hasattr(self, '_m_longitude_min_before_dot'):
                return self._m_longitude_min_before_dot

            self._m_longitude_min_before_dot = int((self.longitude_str)[3:5])
            return getattr(self, '_m_longitude_min_before_dot', None)

        @property
        def latitude_min_before_dot(self):
            if hasattr(self, '_m_latitude_min_before_dot'):
                return self._m_latitude_min_before_dot

            self._m_latitude_min_before_dot = int((self.latitude_str)[2:4])
            return getattr(self, '_m_latitude_min_before_dot', None)

        @property
        def longitude_deg(self):
            if hasattr(self, '_m_longitude_deg'):
                return self._m_longitude_deg

            self._m_longitude_deg = int((self.longitude_str)[0:3])
            return getattr(self, '_m_longitude_deg', None)

        @property
        def magnetic_variation(self):
            if hasattr(self, '_m_magnetic_variation'):
                return self._m_magnetic_variation

            self._m_magnetic_variation = ((self.magnetic_variation_after_dot * 0.1) + self.magnetic_variation_before_dot)
            return getattr(self, '_m_magnetic_variation', None)

        @property
        def utc_time_of_position_h(self):
            if hasattr(self, '_m_utc_time_of_position_h'):
                return self._m_utc_time_of_position_h

            self._m_utc_time_of_position_h = int((self.utc_time_of_position_raw)[0:2])
            return getattr(self, '_m_utc_time_of_position_h', None)

        @property
        def magnetic_variation_before_dot(self):
            if hasattr(self, '_m_magnetic_variation_before_dot'):
                return self._m_magnetic_variation_before_dot

            self._m_magnetic_variation_before_dot = int(self.magnetic_variation_before_dot_raw)
            return getattr(self, '_m_magnetic_variation_before_dot', None)

        @property
        def utc_time_of_position_m(self):
            if hasattr(self, '_m_utc_time_of_position_m'):
                return self._m_utc_time_of_position_m

            self._m_utc_time_of_position_m = int((self.utc_time_of_position_raw)[2:4])
            return getattr(self, '_m_utc_time_of_position_m', None)

        @property
        def course_over_ground_after_dot(self):
            if hasattr(self, '_m_course_over_ground_after_dot'):
                return self._m_course_over_ground_after_dot

            self._m_course_over_ground_after_dot = int(self.course_over_ground_after_dot_raw)
            return getattr(self, '_m_course_over_ground_after_dot', None)

        @property
        def longitude_min_after_dot(self):
            if hasattr(self, '_m_longitude_min_after_dot'):
                return self._m_longitude_min_after_dot

            self._m_longitude_min_after_dot = int((self.longitude_str)[6:8])
            return getattr(self, '_m_longitude_min_after_dot', None)

        @property
        def utc_time_of_position_ss_before_dot(self):
            if hasattr(self, '_m_utc_time_of_position_ss_before_dot'):
                return self._m_utc_time_of_position_ss_before_dot

            self._m_utc_time_of_position_ss_before_dot = int((self.utc_time_of_position_raw)[4:6])
            return getattr(self, '_m_utc_time_of_position_ss_before_dot', None)

        @property
        def date_yy(self):
            if hasattr(self, '_m_date_yy'):
                return self._m_date_yy

            self._m_date_yy = (int((self.date_str)[4:6]) + 2000)
            return getattr(self, '_m_date_yy', None)



