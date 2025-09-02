# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Grbalpha(KaitaiStruct):
    """:field uptime_total: grbalpha.type_check.uptime_total
    :field uptime_since_last: grbalpha.type_check.uptime_since_last
    :field reset_count: grbalpha.type_check.reset_count
    :field mcu_10mv: grbalpha.type_check.mcu_10mv
    :field batt: grbalpha.type_check.batt
    :field temp_cpu: grbalpha.type_check.temp_cpu
    :field temp_pa_ntc: grbalpha.type_check.temp_pa_ntc
    :field sig_rx_immediate: grbalpha.type_check.sig_rx_immediate
    :field sig_rx_avg: grbalpha.type_check.sig_rx_avg
    :field sig_rx_max: grbalpha.type_check.sig_rx_max
    :field sig_background_avg: grbalpha.type_check.sig_background_avg
    :field sig_background_immediate: grbalpha.type_check.sig_background_immediate
    :field sig_background_max: grbalpha.type_check.sig_background_max
    :field rf_packets_received: grbalpha.type_check.rf_packets_received
    :field rf_packets_transmitted: grbalpha.type_check.rf_packets_transmitted
    :field ax25_packets_received: grbalpha.type_check.ax25_packets_received
    :field ax25_packets_transmitted: grbalpha.type_check.ax25_packets_transmitted
    :field digipeater_rx_count: grbalpha.type_check.digipeater_rx_count
    :field digipeater_tx_count: grbalpha.type_check.digipeater_tx_count
    :field csp_received: grbalpha.type_check.csp_received
    :field csp_transmitted: grbalpha.type_check.csp_transmitted
    :field i2c1_received: grbalpha.type_check.i2c1_received
    :field i2c1_transmitted: grbalpha.type_check.i2c1_transmitted
    :field i2c2_received: grbalpha.type_check.i2c2_received
    :field i2c2_transmitted: grbalpha.type_check.i2c2_transmitted
    :field rs485_received: grbalpha.type_check.rs485_received
    :field rs485_transmitted: grbalpha.type_check.rs485_transmitted
    :field csp_mcu_received: grbalpha.type_check.csp_mcu_received
    :field csp_mcu_transmitted: grbalpha.type_check.csp_mcu_transmitted
    :field unix_time: grbalpha.type_check.obc_gps.type_check_2.unix_time
    :field lock_count: grbalpha.type_check.obc_gps.type_check_2.lock_count
    :field latitude: grbalpha.type_check.obc_gps.type_check_2.latitude
    :field longitude: grbalpha.type_check.obc_gps.type_check_2.longitude
    :field altitude: grbalpha.type_check.obc_gps.type_check_2.altitude
    :field obc_timestamp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_timestamp
    :field obc_temp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_temp
    :field obc_tmp112_xp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_tmp112_xp
    :field obc_tmp112_yp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_tmp112_yp
    :field obc_tmp112_xn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_tmp112_xn
    :field obc_tmp112_yn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_tmp112_yn
    :field obc_tmp112_zp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_tmp112_zp
    :field obc_mag_mmc_x: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mmc_x
    :field obc_mag_mmc_y: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mmc_y
    :field obc_mag_mmc_z: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mmc_z
    :field obc_mag_mpu_x: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mpu_x
    :field obc_mag_mpu_y: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mpu_y
    :field obc_mag_mpu_z: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mag_mpu_z
    :field obc_mpu_temp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_mpu_temp
    :field obc_gyr_mpu_x: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_gyr_mpu_x
    :field obc_gyr_mpu_y: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_gyr_mpu_y
    :field obc_gyr_mpu_z: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_gyr_mpu_z
    :field obc_acc_mpu_x: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_acc_mpu_x
    :field obc_acc_mpu_y: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_acc_mpu_y
    :field obc_acc_mpu_z: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_acc_mpu_z
    :field obc_uptime_rst: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_uptime_rst
    :field obc_uptime_total: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_uptime_total
    :field obc_rst_cnt: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_rst_cnt
    :field obc_packet_rec_cnt: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_packet_rec_cnt
    :field obc_suns_temp_yn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_temp_yn
    :field obc_suns_temp_yp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_temp_yp
    :field obc_suns_temp_xp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_temp_xp
    :field obc_suns_temp_xn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_temp_xn
    :field obc_suns_temp_zn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_temp_zn
    :field obc_suns_irad_yn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_irad_yn
    :field obc_suns_irad_yp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_irad_yp
    :field obc_suns_irad_xp: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_irad_xp
    :field obc_suns_irad_xn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_irad_xn
    :field obc_suns_irad_zn: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_suns_irad_zn
    :field gps_rst_cnt: grbalpha.type_check.obc_gps.type_check_2.bytes.gps_rst_cnt
    :field gps_fix_quality: grbalpha.type_check.obc_gps.type_check_2.bytes.gps_fix_quality
    :field gps_tracked: grbalpha.type_check.obc_gps.type_check_2.bytes.gps_tracked
    :field gps_temp: grbalpha.type_check.obc_gps.type_check_2.bytes.gps_temp
    :field obc_free_mem: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_free_mem
    :field obc_crc: grbalpha.type_check.obc_gps.type_check_2.bytes.obc_crc
    :field src_callsign: grbalpha.type_check.ax25_frame.ax25_header.dnxd_src_callsign_raw.callsign_ror.callsign
    :field src_ssid: grbalpha.type_check.ax25_frame.ax25_header.dnxd_src_ssid_raw.ssid
    :field dest_callsign: grbalpha.type_check.ax25_frame.ax25_header.dnxd_dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: grbalpha.type_check.ax25_frame.ax25_header.dnxd_dest_ssid_raw.ssid
    :field dnxd_message: grbalpha.type_check.ax25_frame.dnxd_message
    :field src_callsign: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.digi_src_callsign_raw.callsign_ror.callsign
    :field src_ssid: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.digi_src_ssid_raw.ssid
    :field dest_callsign: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.digi_dest_callsign_raw.callsign_ror.callsign
    :field dest_ssid: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.digi_dest_ssid_raw.ssid
    :field rpt_instance_callsign: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.repeater.rpt_instance.rpt_callsign_raw.callsign_ror.callsign
    :field rpt_instance_ssid: grbalpha.type_check.digi_ax25_frame.digi_ax25_header.repeater.rpt_instance.rpt_ssid_raw.ssid
    :field digi_message: grbalpha.type_check.digi_ax25_frame.digi_message
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.grbalpha = Grbalpha.GrbalphaT(self._io, self, self._root)

    class ObcOrGps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.skip_ax25_header = self._io.read_bits_int_be(128)
            if not self.skip_ax25_header == 178959006690963876281585086672433775600:
                raise kaitaistruct.ValidationNotEqualError(178959006690963876281585086672433775600, self.skip_ax25_header, self._io, u"/types/obc_or_gps/seq/0")
            self._io.align_to_byte()
            self.obc_gps = Grbalpha.ObcOrGps.ObcGpsT(self._io, self, self._root)

        class ObcGpsT(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                _on = self.check_2
                if _on == 1196446522:
                    self.type_check_2 = Grbalpha.ObcOrGps.Gps(self._io, self, self._root)
                else:
                    self.type_check_2 = Grbalpha.ObcOrGps.Obc(self._io, self, self._root)

            @property
            def check_2(self):
                if hasattr(self, '_m_check_2'):
                    return self._m_check_2

                _pos = self._io.pos()
                self._io.seek(16)
                self._m_check_2 = self._io.read_u4be()
                self._io.seek(_pos)
                return getattr(self, '_m_check_2', None)


        class Gps(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.gps = self._io.read_u4le()
                if not self.gps == 978538567:
                    raise kaitaistruct.ValidationNotEqualError(978538567, self.gps, self._io, u"/types/obc_or_gps/types/gps/seq/0")
                self.unix_time_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.lock_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.latitude_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
                self.latitude_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.longitude_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
                self.longitude_after_dot_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
                self.altitude_before_dot_raw = (self._io.read_bytes_term(46, False, True, True)).decode(u"utf8")
                self.altitude_after_dot_raw = (self._io.read_bytes_full()).decode(u"utf8")

            @property
            def altitude(self):
                if hasattr(self, '_m_altitude'):
                    return self._m_altitude

                self._m_altitude = (self.altitude_before_dot + (0.1 * self.altitude_after_dot))
                return getattr(self, '_m_altitude', None)

            @property
            def altitude_before_dot(self):
                if hasattr(self, '_m_altitude_before_dot'):
                    return self._m_altitude_before_dot

                self._m_altitude_before_dot = int(self.altitude_before_dot_raw)
                return getattr(self, '_m_altitude_before_dot', None)

            @property
            def altitude_after_dot(self):
                if hasattr(self, '_m_altitude_after_dot'):
                    return self._m_altitude_after_dot

                self._m_altitude_after_dot = int(self.altitude_after_dot_raw)
                return getattr(self, '_m_altitude_after_dot', None)

            @property
            def latitude_after_dot(self):
                if hasattr(self, '_m_latitude_after_dot'):
                    return self._m_latitude_after_dot

                self._m_latitude_after_dot = int(self.latitude_after_dot_raw)
                return getattr(self, '_m_latitude_after_dot', None)

            @property
            def latitude(self):
                if hasattr(self, '_m_latitude'):
                    return self._m_latitude

                self._m_latitude = ((self.latitude_before_dot - (0.00001 * self.latitude_after_dot)) if (self.latitude_before_dot_raw)[0:1] == u"-" else (self.latitude_before_dot + (0.00001 * self.latitude_after_dot)))
                return getattr(self, '_m_latitude', None)

            @property
            def longitude(self):
                if hasattr(self, '_m_longitude'):
                    return self._m_longitude

                self._m_longitude = ((self.longitude_before_dot - (0.00001 * self.longitude_after_dot)) if (self.longitude_before_dot_raw)[0:1] == u"-" else (self.longitude_before_dot + (0.00001 * self.longitude_after_dot)))
                return getattr(self, '_m_longitude', None)

            @property
            def longitude_before_dot(self):
                if hasattr(self, '_m_longitude_before_dot'):
                    return self._m_longitude_before_dot

                self._m_longitude_before_dot = int(self.longitude_before_dot_raw)
                return getattr(self, '_m_longitude_before_dot', None)

            @property
            def latitude_before_dot(self):
                if hasattr(self, '_m_latitude_before_dot'):
                    return self._m_latitude_before_dot

                self._m_latitude_before_dot = int(self.latitude_before_dot_raw)
                return getattr(self, '_m_latitude_before_dot', None)

            @property
            def lock_count(self):
                if hasattr(self, '_m_lock_count'):
                    return self._m_lock_count

                self._m_lock_count = int(self.lock_count_raw)
                return getattr(self, '_m_lock_count', None)

            @property
            def longitude_after_dot(self):
                if hasattr(self, '_m_longitude_after_dot'):
                    return self._m_longitude_after_dot

                self._m_longitude_after_dot = int(self.longitude_after_dot_raw)
                return getattr(self, '_m_longitude_after_dot', None)

            @property
            def unix_time(self):
                if hasattr(self, '_m_unix_time'):
                    return self._m_unix_time

                self._m_unix_time = int(self.unix_time_raw)
                return getattr(self, '_m_unix_time', None)


        class Obc(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self._raw__raw_bytes = self._io.read_bytes(124)
                _process = satnogsdecoders.process.B64decode()
                self._raw_bytes = _process.decode(self._raw__raw_bytes)
                _io__raw_bytes = KaitaiStream(BytesIO(self._raw_bytes))
                self.bytes = Grbalpha.ObcOrGps.ObcBytes(_io__raw_bytes, self, self._root)


        class ObcBytes(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.obc_timestamp = self._io.read_u4le()
                self.obc_temp = self._io.read_s2le()
                self.obc_tmp112_xp = self._io.read_s2le()
                self.obc_tmp112_yp = self._io.read_s2le()
                self.obc_tmp112_xn = self._io.read_s2le()
                self.obc_tmp112_yn = self._io.read_s2le()
                self.obc_tmp112_zp = self._io.read_s2le()
                self.obc_mag_mmc_x = self._io.read_s2le()
                self.obc_mag_mmc_y = self._io.read_s2le()
                self.obc_mag_mmc_z = self._io.read_s2le()
                self.obc_mag_mpu_x = self._io.read_s2le()
                self.obc_mag_mpu_y = self._io.read_s2le()
                self.obc_mag_mpu_z = self._io.read_s2le()
                self.obc_mpu_temp = self._io.read_f4le()
                self.obc_gyr_mpu_x = self._io.read_s2le()
                self.obc_gyr_mpu_y = self._io.read_s2le()
                self.obc_gyr_mpu_z = self._io.read_s2le()
                self.obc_acc_mpu_x = self._io.read_s2le()
                self.obc_acc_mpu_y = self._io.read_s2le()
                self.obc_acc_mpu_z = self._io.read_s2le()
                self.obc_uptime_rst = self._io.read_u4le()
                self.obc_uptime_total = self._io.read_u4le()
                self.obc_rst_cnt = self._io.read_u4le()
                self.obc_packet_rec_cnt = self._io.read_u4le()
                self.obc_suns_temp_yn = self._io.read_u2le()
                self.obc_suns_temp_yp = self._io.read_u2le()
                self.obc_suns_temp_xp = self._io.read_u2le()
                self.obc_suns_temp_xn = self._io.read_u2le()
                self.obc_suns_temp_zn = self._io.read_u2le()
                self.obc_suns_irad_yn = self._io.read_u2le()
                self.obc_suns_irad_yp = self._io.read_u2le()
                self.obc_suns_irad_xp = self._io.read_u2le()
                self.obc_suns_irad_xn = self._io.read_u2le()
                self.obc_suns_irad_zn = self._io.read_u2le()
                self.gps_rst_cnt = self._io.read_u4le()
                self.gps_fix_quality = self._io.read_u1()
                self.gps_tracked = self._io.read_u1()
                self.gps_temp = self._io.read_s2le()
                self.obc_free_mem = self._io.read_u2le()
                self.obc_crc = self._io.read_u2le()



    class Dnxd(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Grbalpha.Dnxd.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Grbalpha.Dnxd.Ax25Header(self._io, self, self._root)
                self.dnxd_message = (self._io.read_bytes_full()).decode(u"utf-8")


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dnxd_dest_callsign_raw = Grbalpha.Dnxd.CallsignRaw(self._io, self, self._root)
                self.dnxd_dest_ssid_raw = Grbalpha.Dnxd.SsidMask(self._io, self, self._root)
                self.dnxd_src_callsign_raw = Grbalpha.Dnxd.CallsignRaw(self._io, self, self._root)
                if self.dnxd_src_callsign_raw.callsign_ror.callsign == u"OM9GRB":
                    self.dnxd_src_ssid_raw = Grbalpha.Dnxd.SsidMask(self._io, self, self._root)

                if self.dnxd_src_ssid_raw.ssid == 8:
                    self.ctl_pid = self._io.read_u2le()



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
                self.callsign_ror = Grbalpha.Dnxd.Callsign(_io__raw_callsign_ror, self, self._root)



    class GrbalphaT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.check
            if _on == 2393146465:
                self.type_check = Grbalpha.Comd(self._io, self, self._root)
            elif _on == 2393146495:
                self.type_check = Grbalpha.ObcOrGps(self._io, self, self._root)
            elif _on == 2393146481:
                self.type_check = Grbalpha.Dnxd(self._io, self, self._root)
            else:
                self.type_check = Grbalpha.Digi(self._io, self, self._root)

        @property
        def check(self):
            if hasattr(self, '_m_check'):
                return self._m_check

            _pos = self._io.pos()
            self._io.seek(10)
            self._m_check = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_check', None)


    class Comd(KaitaiStruct):
        """
        .. seealso::
           Source - https://needronix.eu/products/cormorant/hamradio-user-guide/
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.skip_ax25_header_and_first_comma = self._io.read_bits_int_be(136)
            if not self.skip_ax25_header_and_first_comma == 45813505712886752328085782188142543237164:
                raise kaitaistruct.ValidationNotEqualError(45813505712886752328085782188142543237164, self.skip_ax25_header_and_first_comma, self._io, u"/types/comd/seq/0")
            self._io.align_to_byte()
            self.comd = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.comd == u"COMd":
                raise kaitaistruct.ValidationNotEqualError(u"COMd", self.comd, self._io, u"/types/comd/seq/1")
            self.pass_uptime = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_uptime == u"U":
                raise kaitaistruct.ValidationNotEqualError(u"U", self.pass_uptime, self._io, u"/types/comd/seq/2")
            self.uptime_total_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.uptime_since_last_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_resets = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_resets == u"R":
                raise kaitaistruct.ValidationNotEqualError(u"R", self.pass_resets, self._io, u"/types/comd/seq/5")
            self.reset_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_mcuv = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_mcuv == u"V":
                raise kaitaistruct.ValidationNotEqualError(u"V", self.pass_mcuv, self._io, u"/types/comd/seq/7")
            self.mcu_10mv_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_battv = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_battv == u"Ve":
                raise kaitaistruct.ValidationNotEqualError(u"Ve", self.pass_battv, self._io, u"/types/comd/seq/9")
            self.batt_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_temp = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_temp == u"T":
                raise kaitaistruct.ValidationNotEqualError(u"T", self.pass_temp, self._io, u"/types/comd/seq/11")
            self.temp_cpu_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.temp_pa_ntc_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_sig = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_sig == u"Sig":
                raise kaitaistruct.ValidationNotEqualError(u"Sig", self.pass_sig, self._io, u"/types/comd/seq/14")
            self.sig_rx_immediate_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.sig_rx_avg_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.sig_rx_max_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.sig_background_immediate_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.sig_background_avg_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.sig_background_max_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_rf = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_rf == u"RX":
                raise kaitaistruct.ValidationNotEqualError(u"RX", self.pass_rf, self._io, u"/types/comd/seq/21")
            self.rf_packets_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.rf_packets_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_ax25 = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_ax25 == u"Ax":
                raise kaitaistruct.ValidationNotEqualError(u"Ax", self.pass_ax25, self._io, u"/types/comd/seq/24")
            self.ax25_packets_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.ax25_packets_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_digi = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_digi == u"Digi":
                raise kaitaistruct.ValidationNotEqualError(u"Digi", self.pass_digi, self._io, u"/types/comd/seq/27")
            self.digipeater_rx_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.digipeater_tx_count_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_csp = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_csp == u"CSP":
                raise kaitaistruct.ValidationNotEqualError(u"CSP", self.pass_csp, self._io, u"/types/comd/seq/30")
            self.csp_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.csp_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_i2c1 = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_i2c1 == u"I2C1":
                raise kaitaistruct.ValidationNotEqualError(u"I2C1", self.pass_i2c1, self._io, u"/types/comd/seq/33")
            self.i2c1_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.i2c1_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_i2c2 = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_i2c2 == u"I2C2":
                raise kaitaistruct.ValidationNotEqualError(u"I2C2", self.pass_i2c2, self._io, u"/types/comd/seq/36")
            self.i2c2_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.i2c2_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_rs485 = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_rs485 == u"RS485":
                raise kaitaistruct.ValidationNotEqualError(u"RS485", self.pass_rs485, self._io, u"/types/comd/seq/39")
            self.rs485_received_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.rs485_transmitted_raw = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            self.pass_csp_mcu = (self._io.read_bytes_term(44, False, True, True)).decode(u"utf8")
            if not self.pass_csp_mcu == u"MCU":
                raise kaitaistruct.ValidationNotEqualError(u"MCU", self.pass_csp_mcu, self._io, u"/types/comd/seq/42")
            self.csp_mcu_received_raw = (self._io.read_bytes_term(44, False, False, True)).decode(u"utf8")
            self.csp_mcu_transmitted_raw = (self._io.read_bytes_full()).decode(u"utf8")

        @property
        def sig_rx_max(self):
            if hasattr(self, '_m_sig_rx_max'):
                return self._m_sig_rx_max

            self._m_sig_rx_max = int(self.sig_rx_max_raw)
            return getattr(self, '_m_sig_rx_max', None)

        @property
        def temp_pa_ntc(self):
            if hasattr(self, '_m_temp_pa_ntc'):
                return self._m_temp_pa_ntc

            self._m_temp_pa_ntc = int(self.temp_pa_ntc_raw)
            return getattr(self, '_m_temp_pa_ntc', None)

        @property
        def csp_transmitted(self):
            if hasattr(self, '_m_csp_transmitted'):
                return self._m_csp_transmitted

            self._m_csp_transmitted = int(self.csp_transmitted_raw)
            return getattr(self, '_m_csp_transmitted', None)

        @property
        def batt(self):
            if hasattr(self, '_m_batt'):
                return self._m_batt

            self._m_batt = int(self.batt_raw)
            return getattr(self, '_m_batt', None)

        @property
        def sig_rx_avg(self):
            if hasattr(self, '_m_sig_rx_avg'):
                return self._m_sig_rx_avg

            self._m_sig_rx_avg = int(self.sig_rx_avg_raw)
            return getattr(self, '_m_sig_rx_avg', None)

        @property
        def sig_background_immediate(self):
            if hasattr(self, '_m_sig_background_immediate'):
                return self._m_sig_background_immediate

            self._m_sig_background_immediate = int(self.sig_background_immediate_raw)
            return getattr(self, '_m_sig_background_immediate', None)

        @property
        def uptime_total(self):
            if hasattr(self, '_m_uptime_total'):
                return self._m_uptime_total

            self._m_uptime_total = int(self.uptime_total_raw)
            return getattr(self, '_m_uptime_total', None)

        @property
        def rs485_received(self):
            if hasattr(self, '_m_rs485_received'):
                return self._m_rs485_received

            self._m_rs485_received = int(self.rs485_received_raw)
            return getattr(self, '_m_rs485_received', None)

        @property
        def i2c1_received(self):
            if hasattr(self, '_m_i2c1_received'):
                return self._m_i2c1_received

            self._m_i2c1_received = int(self.i2c1_received_raw)
            return getattr(self, '_m_i2c1_received', None)

        @property
        def temp_cpu(self):
            if hasattr(self, '_m_temp_cpu'):
                return self._m_temp_cpu

            self._m_temp_cpu = int(self.temp_cpu_raw)
            return getattr(self, '_m_temp_cpu', None)

        @property
        def ax25_packets_transmitted(self):
            if hasattr(self, '_m_ax25_packets_transmitted'):
                return self._m_ax25_packets_transmitted

            self._m_ax25_packets_transmitted = int(self.ax25_packets_transmitted_raw)
            return getattr(self, '_m_ax25_packets_transmitted', None)

        @property
        def ax25_packets_received(self):
            if hasattr(self, '_m_ax25_packets_received'):
                return self._m_ax25_packets_received

            self._m_ax25_packets_received = int(self.ax25_packets_received_raw)
            return getattr(self, '_m_ax25_packets_received', None)

        @property
        def digipeater_tx_count(self):
            if hasattr(self, '_m_digipeater_tx_count'):
                return self._m_digipeater_tx_count

            self._m_digipeater_tx_count = int(self.digipeater_tx_count_raw)
            return getattr(self, '_m_digipeater_tx_count', None)

        @property
        def csp_mcu_transmitted(self):
            if hasattr(self, '_m_csp_mcu_transmitted'):
                return self._m_csp_mcu_transmitted

            if self.csp_mcu_transmitted_raw != u",":
                self._m_csp_mcu_transmitted = int((self.csp_mcu_transmitted_raw)[1:len(self.csp_mcu_transmitted_raw)])

            return getattr(self, '_m_csp_mcu_transmitted', None)

        @property
        def csp_mcu_received(self):
            if hasattr(self, '_m_csp_mcu_received'):
                return self._m_csp_mcu_received

            self._m_csp_mcu_received = int(self.csp_mcu_received_raw)
            return getattr(self, '_m_csp_mcu_received', None)

        @property
        def i2c1_transmitted(self):
            if hasattr(self, '_m_i2c1_transmitted'):
                return self._m_i2c1_transmitted

            self._m_i2c1_transmitted = int(self.i2c1_transmitted_raw)
            return getattr(self, '_m_i2c1_transmitted', None)

        @property
        def mcu_10mv(self):
            if hasattr(self, '_m_mcu_10mv'):
                return self._m_mcu_10mv

            self._m_mcu_10mv = int(self.mcu_10mv_raw)
            return getattr(self, '_m_mcu_10mv', None)

        @property
        def uptime_since_last(self):
            if hasattr(self, '_m_uptime_since_last'):
                return self._m_uptime_since_last

            self._m_uptime_since_last = int(self.uptime_since_last_raw)
            return getattr(self, '_m_uptime_since_last', None)

        @property
        def sig_background_max(self):
            if hasattr(self, '_m_sig_background_max'):
                return self._m_sig_background_max

            self._m_sig_background_max = int(self.sig_background_max_raw)
            return getattr(self, '_m_sig_background_max', None)

        @property
        def sig_rx_immediate(self):
            if hasattr(self, '_m_sig_rx_immediate'):
                return self._m_sig_rx_immediate

            self._m_sig_rx_immediate = int(self.sig_rx_immediate_raw)
            return getattr(self, '_m_sig_rx_immediate', None)

        @property
        def reset_count(self):
            if hasattr(self, '_m_reset_count'):
                return self._m_reset_count

            self._m_reset_count = int(self.reset_count_raw)
            return getattr(self, '_m_reset_count', None)

        @property
        def rs485_transmitted(self):
            if hasattr(self, '_m_rs485_transmitted'):
                return self._m_rs485_transmitted

            self._m_rs485_transmitted = int(self.rs485_transmitted_raw)
            return getattr(self, '_m_rs485_transmitted', None)

        @property
        def rf_packets_received(self):
            if hasattr(self, '_m_rf_packets_received'):
                return self._m_rf_packets_received

            self._m_rf_packets_received = int(self.rf_packets_received_raw)
            return getattr(self, '_m_rf_packets_received', None)

        @property
        def rf_packets_transmitted(self):
            if hasattr(self, '_m_rf_packets_transmitted'):
                return self._m_rf_packets_transmitted

            self._m_rf_packets_transmitted = int(self.rf_packets_transmitted_raw)
            return getattr(self, '_m_rf_packets_transmitted', None)

        @property
        def digipeater_rx_count(self):
            if hasattr(self, '_m_digipeater_rx_count'):
                return self._m_digipeater_rx_count

            self._m_digipeater_rx_count = int(self.digipeater_rx_count_raw)
            return getattr(self, '_m_digipeater_rx_count', None)

        @property
        def sig_background_avg(self):
            if hasattr(self, '_m_sig_background_avg'):
                return self._m_sig_background_avg

            self._m_sig_background_avg = int(self.sig_background_avg_raw)
            return getattr(self, '_m_sig_background_avg', None)

        @property
        def i2c2_received(self):
            if hasattr(self, '_m_i2c2_received'):
                return self._m_i2c2_received

            self._m_i2c2_received = int(self.i2c2_received_raw)
            return getattr(self, '_m_i2c2_received', None)

        @property
        def i2c2_transmitted(self):
            if hasattr(self, '_m_i2c2_transmitted'):
                return self._m_i2c2_transmitted

            self._m_i2c2_transmitted = int(self.i2c2_transmitted_raw)
            return getattr(self, '_m_i2c2_transmitted', None)

        @property
        def csp_received(self):
            if hasattr(self, '_m_csp_received'):
                return self._m_csp_received

            self._m_csp_received = int(self.csp_received_raw)
            return getattr(self, '_m_csp_received', None)


    class Digi(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.digi_ax25_frame = Grbalpha.Digi.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.digi_ax25_header = Grbalpha.Digi.Ax25Header(self._io, self, self._root)
                self.digi_message = (self._io.read_bytes_full()).decode(u"utf-8")


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.digi_dest_callsign_raw = Grbalpha.Digi.CallsignRaw(self._io, self, self._root)
                self.digi_dest_ssid_raw = Grbalpha.Digi.SsidMask(self._io, self, self._root)
                self.digi_src_callsign_raw = Grbalpha.Digi.CallsignRaw(self._io, self, self._root)
                self.digi_src_ssid_raw = Grbalpha.Digi.SsidMask(self._io, self, self._root)
                if (self.digi_src_ssid_raw.ssid_mask & 1) == 0:
                    self.repeater = Grbalpha.Digi.Repeater(self._io, self, self._root)

                if self.repeater.rpt_instance.rpt_callsign_raw.callsign_ror.callsign == u"OM9GRB":
                    self.ctl = self._io.read_u1()

                if  ((self.repeater.rpt_instance.rpt_ssid_raw.ssid == 7) or (self.repeater.rpt_instance.rpt_ssid_raw.ssid == 8)) :
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


        class Repeaters(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rpt_callsign_raw = Grbalpha.Digi.CallsignRaw(self._io, self, self._root)
                self.rpt_ssid_raw = Grbalpha.Digi.SsidMask(self._io, self, self._root)


        class Repeater(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.rpt_instance = Grbalpha.Digi.Repeaters(self._io, self, self._root)


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
                self.callsign_ror = Grbalpha.Digi.Callsign(_io__raw_callsign_ror, self, self._root)




