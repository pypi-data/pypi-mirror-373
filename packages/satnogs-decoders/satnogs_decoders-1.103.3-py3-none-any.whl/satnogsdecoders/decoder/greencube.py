# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Greencube(KaitaiStruct):
    """:field header: greencube_raw_frame.csp_header.header
    :field priority: greencube_raw_frame.csp_header.priority
    :field src: greencube_raw_frame.csp_header.src
    :field dest: greencube_raw_frame.csp_header.dest
    :field dest_port: greencube_raw_frame.csp_header.dest_port
    :field src_port: greencube_raw_frame.csp_header.src_port
    :field hmac: greencube_raw_frame.csp_header.hmac
    :field xtea: greencube_raw_frame.csp_header.xtea
    :field rdp: greencube_raw_frame.csp_header.rdp
    :field crc: greencube_raw_frame.csp_header.crc
    :field tlm_id: greencube_raw_frame.tlm_id
    :field unix_time_ms: greencube_raw_frame.tlm_data.unix_time_ms
    :field unix_time: greencube_raw_frame.tlm_data.unix_time
    :field process_time: greencube_raw_frame.tlm_data.process_time
    :field solar_x_voltage: greencube_raw_frame.tlm_data.solar_x_voltage
    :field solar_y_voltage: greencube_raw_frame.tlm_data.solar_y_voltage
    :field solar_x_current: greencube_raw_frame.tlm_data.solar_x_current
    :field solar_y_current: greencube_raw_frame.tlm_data.solar_y_current
    :field eps_bootcause: greencube_raw_frame.tlm_data.eps_bootcause
    :field mppt_x_temperature: greencube_raw_frame.tlm_data.mppt_x_temperature
    :field mppt_y_temperature: greencube_raw_frame.tlm_data.mppt_y_temperature
    :field eps_temperature: greencube_raw_frame.tlm_data.eps_temperature
    :field battery_1_temperature: greencube_raw_frame.tlm_data.battery_1_temperature
    :field battery_2_temperature: greencube_raw_frame.tlm_data.battery_2_temperature
    :field battery_3_temperature: greencube_raw_frame.tlm_data.battery_3_temperature
    :field solar_total_current: greencube_raw_frame.tlm_data.solar_total_current
    :field system_total_current: greencube_raw_frame.tlm_data.system_total_current
    :field battery_voltage: greencube_raw_frame.tlm_data.battery_voltage
    :field eps_outputs: greencube_raw_frame.tlm_data.eps_outputs
    :field radio_pa_temperature: greencube_raw_frame.tlm_data.radio_pa_temperature
    :field radio_tx_count: greencube_raw_frame.tlm_data.radio_tx_count
    :field radio_rx_count: greencube_raw_frame.tlm_data.radio_rx_count
    :field radio_last_rssi: greencube_raw_frame.tlm_data.radio_last_rssi
    :field obc_boot_count: greencube_raw_frame.tlm_data.obc_boot_count
    :field radio_boot_count: greencube_raw_frame.tlm_data.radio_boot_count
    :field eps_boot_count: greencube_raw_frame.tlm_data.eps_boot_count
    :field payload_rx_count: greencube_raw_frame.tlm_data.payload_rx_count
    :field payload_tx_count: greencube_raw_frame.tlm_data.payload_tx_count
    :field software_status: greencube_raw_frame.tlm_data.software_status
    :field heater_status: greencube_raw_frame.tlm_data.heater_status
    :field obc_temperature: greencube_raw_frame.tlm_data.obc_temperature
    :field gyroscope_x: greencube_raw_frame.tlm_data.gyroscope_x
    :field gyroscope_y: greencube_raw_frame.tlm_data.gyroscope_y
    :field gyroscope_z: greencube_raw_frame.tlm_data.gyroscope_z
    :field magnetometer_x: greencube_raw_frame.tlm_data.magnetometer_x
    :field magnetometer_y: greencube_raw_frame.tlm_data.magnetometer_y
    :field magnetometer_z: greencube_raw_frame.tlm_data.magnetometer_z
    :field solarpanel_plus_x_temperature: greencube_raw_frame.tlm_data.solarpanel_plus_x_temperature
    :field solarpanel_plus_y_temperature: greencube_raw_frame.tlm_data.solarpanel_plus_y_temperature
    :field solarpanel_minus_x_temperature: greencube_raw_frame.tlm_data.solarpanel_minus_x_temperature
    :field solarpanel_minus_y_temperature: greencube_raw_frame.tlm_data.solarpanel_minus_y_temperature
    :field coarse_sun_sensor_plus_x: greencube_raw_frame.tlm_data.coarse_sun_sensor_plus_x
    :field coarse_sun_sensor_plus_y: greencube_raw_frame.tlm_data.coarse_sun_sensor_plus_y
    :field coarse_sun_sensor_minus_x: greencube_raw_frame.tlm_data.coarse_sun_sensor_minus_x
    :field coarse_sun_sensor_minus_y: greencube_raw_frame.tlm_data.coarse_sun_sensor_minus_y
    :field gps_status_flag: greencube_raw_frame.tlm_data.gps_status_flag
    :field gps_fix_time: greencube_raw_frame.tlm_data.gps_fix_time
    :field gps_latitude: greencube_raw_frame.tlm_data.gps_latitude
    :field gps_longitude: greencube_raw_frame.tlm_data.gps_longitude
    :field gps_altitude: greencube_raw_frame.tlm_data.gps_altitude
    :field sband_tx_count: greencube_raw_frame.tlm_data.sband_tx_count
    :field antenna_status_flag: greencube_raw_frame.tlm_data.antenna_status_flag
    :field acs_state_flag: greencube_raw_frame.tlm_data.acs_state_flag
    :field acs_parameters_flag: greencube_raw_frame.tlm_data.acs_parameters_flag
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        _on = self._io.size()
        if _on == 101:
            self.greencube_raw_frame = Greencube.GreencubeTlmFrame(self._io, self, self._root)

    class GreencubeTlmFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = Greencube.CspHeader(self._io, self, self._root)
            self.tlm_id = self._io.read_u2be()
            if not  ((self.tlm_id == 13840) or (self.tlm_id == 13841) or (self.tlm_id == 13842) or (self.tlm_id == 30234)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.tlm_id, self._io, u"/types/greencube_tlm_frame/seq/1")
            self.tlm_data = Greencube.TlmData(self._io, self, self._root)


    class CspHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = self._io.read_u4be()

        @property
        def src(self):
            if hasattr(self, '_m_src'):
                return self._m_src

            self._m_src = ((self.header >> 25) & 31)
            return getattr(self, '_m_src', None)

        @property
        def dest(self):
            if hasattr(self, '_m_dest'):
                return self._m_dest

            self._m_dest = ((self.header >> 20) & 31)
            return getattr(self, '_m_dest', None)

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp

            self._m_rdp = ((self.header >> 1) & 1)
            return getattr(self, '_m_rdp', None)

        @property
        def src_port(self):
            if hasattr(self, '_m_src_port'):
                return self._m_src_port

            self._m_src_port = ((self.header >> 8) & 63)
            return getattr(self, '_m_src_port', None)

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority

            self._m_priority = ((self.header >> 30) & 3)
            return getattr(self, '_m_priority', None)

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea

            self._m_xtea = ((self.header >> 2) & 1)
            return getattr(self, '_m_xtea', None)

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac

            self._m_hmac = ((self.header >> 3) & 1)
            return getattr(self, '_m_hmac', None)

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc

            self._m_crc = (self.header & 1)
            return getattr(self, '_m_crc', None)

        @property
        def dest_port(self):
            if hasattr(self, '_m_dest_port'):
                return self._m_dest_port

            self._m_dest_port = ((self.header >> 14) & 63)
            return getattr(self, '_m_dest_port', None)


    class TlmData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unix_time_ms = self._io.read_u2be()
            self.unix_time = self._io.read_u4be()
            self.process_time = self._io.read_u2be()
            self.solar_x_voltage = self._io.read_u2be()
            self.solar_y_voltage = self._io.read_u2be()
            self.solar_x_current = self._io.read_u2be()
            self.solar_y_current = self._io.read_u2be()
            self.eps_bootcause = self._io.read_u1()
            self.mppt_x_temperature = self._io.read_s1()
            self.mppt_y_temperature = self._io.read_s1()
            self.eps_temperature = self._io.read_s1()
            self.battery_1_temperature = self._io.read_s1()
            self.battery_2_temperature = self._io.read_s1()
            self.battery_3_temperature = self._io.read_s1()
            self.solar_total_current = self._io.read_u2be()
            self.system_total_current = self._io.read_u2be()
            self.battery_voltage = self._io.read_u2be()
            self.eps_outputs = self._io.read_u1()
            self.radio_pa_temperature = self._io.read_s1()
            self.radio_tx_count = self._io.read_u2be()
            self.radio_rx_count = self._io.read_u2be()
            self.radio_last_rssi = self._io.read_s2be()
            self.obc_boot_count = self._io.read_u2be()
            self.radio_boot_count = self._io.read_u2be()
            self.eps_boot_count = self._io.read_u2be()
            self.payload_rx_count = self._io.read_u1()
            self.payload_tx_count = self._io.read_u1()
            self.software_status = self._io.read_u1()
            self.heater_status = self._io.read_u1()
            self.obc_temperature = self._io.read_u1()
            self.gyroscope_x = self._io.read_s2be()
            self.gyroscope_y = self._io.read_s2be()
            self.gyroscope_z = self._io.read_s2be()
            self.magnetometer_x = self._io.read_s2be()
            self.magnetometer_y = self._io.read_s2be()
            self.magnetometer_z = self._io.read_s2be()
            self.solarpanel_plus_x_temperature = self._io.read_s1()
            self.solarpanel_plus_y_temperature = self._io.read_s1()
            self.solarpanel_minus_x_temperature = self._io.read_s1()
            self.solarpanel_minus_y_temperature = self._io.read_s1()
            self.coarse_sun_sensor_plus_x = self._io.read_u2be()
            self.coarse_sun_sensor_plus_y = self._io.read_u2be()
            self.coarse_sun_sensor_minus_x = self._io.read_u2be()
            self.coarse_sun_sensor_minus_y = self._io.read_u2be()
            self.gps_status_flag = self._io.read_u1()
            self.gps_fix_time = self._io.read_u4be()
            self.gps_latitude = self._io.read_u4be()
            self.gps_longitude = self._io.read_u4be()
            self.gps_altitude = self._io.read_u4be()
            self.sband_tx_count = self._io.read_u2be()
            self.antenna_status_flag = self._io.read_u2be()
            self.acs_state_flag = self._io.read_u1()
            self.acs_parameters_flag = self._io.read_u1()



