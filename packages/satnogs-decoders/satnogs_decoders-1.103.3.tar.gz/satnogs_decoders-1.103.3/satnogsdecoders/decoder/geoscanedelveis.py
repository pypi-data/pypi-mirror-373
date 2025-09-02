# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Geoscanedelveis(KaitaiStruct):
    """:field dest_callsign: data.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: data.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: data.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: data.ax25_header.dest_ssid_raw.ssid
    :field ctl: data.ax25_header.ctl
    :field pid: data.ax25_header.pid
    :field obc_timestamp: data.payload.obc_timestamp
    :field eps_cell_current: data.payload.eps_cell_current
    :field eps_system_current: data.payload.eps_system_current
    :field eps_cell_voltage_half: data.payload.eps_cell_voltage_half
    :field eps_cell_voltage_full: data.payload.eps_cell_voltage_full
    :field adc_temperature_pos_x: data.payload.adc_temperature_pos_x
    :field adc_temperature_neg_x: data.payload.adc_temperature_neg_x
    :field adc_temperature_pos_y: data.payload.adc_temperature_pos_y
    :field adc_temperature_neg_y: data.payload.adc_temperature_neg_y
    :field adc_temperature_pos_z: data.payload.adc_temperature_pos_z
    :field adc_temperature_neg_z: data.payload.adc_temperature_neg_z
    :field adc_temperature_cell1: data.payload.adc_temperature_cell1
    :field adc_temperature_cell2: data.payload.adc_temperature_cell2
    :field obc_cpu_load: data.payload.obc_cpu_load
    :field obc_boot_count: data.payload.obc_boot_count
    :field comm_boot_count: data.payload.comm_boot_count
    :field comm_rssi: data.payload.comm_rssi
    :field sat_id: data.geoscan_header.sat_id
    :field info: data.geoscan_header.info
    :field offset: data.geoscan_header.offset
    :field cmd: data.geoscan_data.cmd
    :field adc_timestamp: data.geoscan_data.payload.adc_timestamp
    :field sun_sensor_pos_x: data.geoscan_data.payload.sun_sensor_pos_x
    :field sun_sensor_neg_x: data.geoscan_data.payload.sun_sensor_neg_x
    :field sun_sensor_pos_y: data.geoscan_data.payload.sun_sensor_pos_y
    :field sun_sensor_neg_y: data.geoscan_data.payload.sun_sensor_neg_y
    :field sun_sensor_neg_z: data.geoscan_data.payload.sun_sensor_neg_z
    :field mag_sensor_pos_x: data.geoscan_data.payload.mag_sensor_pos_x
    :field mag_sensor_neg_x: data.geoscan_data.payload.mag_sensor_neg_x
    :field mag_sensor_pos_y: data.geoscan_data.payload.mag_sensor_pos_y
    :field mag_sensor_neg_y: data.geoscan_data.payload.mag_sensor_neg_y
    :field mag_sensor_pos_z: data.geoscan_data.payload.mag_sensor_pos_z
    :field mag_sensor_neg_z: data.geoscan_data.payload.mag_sensor_neg_z
    :field temperature_pos_x: data.geoscan_data.payload.temperature_pos_x
    :field temperature_neg_x: data.geoscan_data.payload.temperature_neg_x
    :field temperature_pos_y: data.geoscan_data.payload.temperature_pos_y
    :field temperature_neg_y: data.geoscan_data.payload.temperature_neg_y
    :field temperature_pos_z: data.geoscan_data.payload.temperature_pos_z
    :field temperature_neg_z: data.geoscan_data.payload.temperature_neg_z
    :field temperature_cell1: data.geoscan_data.payload.temperature_cell1
    :field temperature_cell2: data.geoscan_data.payload.temperature_cell2
    :field status: data.geoscan_data.payload.status
    :field eps_timestamp: data.geoscan_data.payload.eps_timestamp
    :field geoscan_data_eps_cell_current: data.geoscan_data.payload.eps_cell_current
    :field geoscan_data_eps_system_current: data.geoscan_data.payload.eps_system_current
    :field reserved0: data.geoscan_data.payload.reserved0
    :field reserved1: data.geoscan_data.payload.reserved1
    :field reserved2: data.geoscan_data.payload.reserved2
    :field reserved3: data.geoscan_data.payload.reserved3
    :field geoscan_data_eps_cell_voltage_half: data.geoscan_data.payload.eps_cell_voltage_half
    :field geoscan_data_eps_cell_voltage_full: data.geoscan_data.payload.eps_cell_voltage_full
    :field reserved4: data.geoscan_data.payload.reserved4
    :field reserved5: data.geoscan_data.payload.reserved5
    :field reserved6: data.geoscan_data.payload.reserved6
    :field gnss_timestamp: data.geoscan_data.payload.gnss_timestamp
    :field valid: data.geoscan_data.payload.valid
    :field year: data.geoscan_data.payload.year
    :field month: data.geoscan_data.payload.month
    :field day: data.geoscan_data.payload.day
    :field hour: data.geoscan_data.payload.hour
    :field minute: data.geoscan_data.payload.minute
    :field second: data.geoscan_data.payload.second
    :field dutc: data.geoscan_data.payload.dutc
    :field offset_gnss: data.geoscan_data.payload.offset_gnss
    :field x: data.geoscan_data.payload.x
    :field y: data.geoscan_data.payload.y
    :field z: data.geoscan_data.payload.z
    :field v_x: data.geoscan_data.payload.v_x
    :field v_y: data.geoscan_data.payload.v_y
    :field v_z: data.geoscan_data.payload.v_z
    :field vdop: data.geoscan_data.payload.vdop
    :field hdop: data.geoscan_data.payload.hdop
    :field pdop: data.geoscan_data.payload.pdop
    :field tdop: data.geoscan_data.payload.tdop
    :field fakel_timestamp: data.geoscan_data.payload.fakel_timestamp
    :field bitfield0: data.geoscan_data.payload.bitfield0
    :field bitfield1: data.geoscan_data.payload.bitfield1
    :field voltage_80v: data.geoscan_data.payload.voltage_80v
    :field voltage_13v: data.geoscan_data.payload.voltage_13v
    :field current_valve: data.geoscan_data.payload.current_valve
    :field voltage_valve: data.geoscan_data.payload.voltage_valve
    :field current_control_valve: data.geoscan_data.payload.current_control_valve
    :field voltage_control_valve: data.geoscan_data.payload.voltage_control_valve
    :field current_ek1: data.geoscan_data.payload.current_ek1
    :field voltage_ek1: data.geoscan_data.payload.voltage_ek1
    :field current_ek2: data.geoscan_data.payload.current_ek2
    :field voltage_ek2: data.geoscan_data.payload.voltage_ek2
    :field current_ek: data.geoscan_data.payload.current_ek
    :field voltage_ek: data.geoscan_data.payload.voltage_ek
    :field temperature_td1: data.geoscan_data.payload.temperature_td1
    :field reserved7: data.geoscan_data.payload.reserved7
    :field temperature_tp: data.geoscan_data.payload.temperature_tp
    :field pressure_cylinder: data.geoscan_data.payload.pressure_cylinder
    :field pressure_receiver: data.geoscan_data.payload.pressure_receiver
    :field switch_on_counter: data.geoscan_data.payload.switch_on_counter
    :field time_switched_on_counter: data.geoscan_data.payload.time_switched_on_counter
    :field bitfield3: data.geoscan_data.payload.bitfield3
    :field state: data.geoscan_data.payload.state
    :field reserved8: data.geoscan_data.payload.reserved8
    :field reserved9: data.geoscan_data.payload.reserved9
    :field pump_time: data.geoscan_data.payload.pump_time
    :field time_of_last_pump: data.geoscan_data.payload.time_of_last_pump
    :field reserved10: data.geoscan_data.payload.reserved10
    :field data_str: data.geoscan_data.payload.photo_data.data.data_str
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        _on = self.type
        if _on == 2223669894:
            self.data = Geoscanedelveis.Ax25Frame(self._io, self, self._root)
        elif _on == 16793089:
            self.data = Geoscanedelveis.GeoscanFrame(self._io, self, self._root)
        elif _on == 16793093:
            self.data = Geoscanedelveis.GeoscanFrame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Geoscanedelveis.Ax25Header(self._io, self, self._root)
            self.payload = Geoscanedelveis.GeoscanBeaconTlm(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Geoscanedelveis.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Geoscanedelveis.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Geoscanedelveis.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Geoscanedelveis.SsidMask(self._io, self, self._root)
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
            if not  ((self.callsign == u"BEACON") or (self.callsign == u"RS20S ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class GeoscanFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.geoscan_header = Geoscanedelveis.GeoscanHeader(self._io, self, self._root)
            self.geoscan_data = Geoscanedelveis.GeoscanTlm(self._io, self, self._root)


    class StrB64T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_str = (self._io.read_bytes_full()).decode(u"ASCII")


    class GeoscanPhoto(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_photo_data = self._io.read_bytes_full()
            _io__raw_photo_data = KaitaiStream(BytesIO(self._raw_photo_data))
            self.photo_data = Geoscanedelveis.DataB64T(_io__raw_photo_data, self, self._root)


    class GeoscanHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sat_id = self._io.read_u1()
            self.info = self._io.read_u4le()
            self.offset = self._io.read_u2le()


    class DataB64T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_data = self._io.read_bytes_full()
            _process = satnogsdecoders.process.B64encode()
            self._raw_data = _process.decode(self._raw__raw_data)
            _io__raw_data = KaitaiStream(BytesIO(self._raw_data))
            self.data = Geoscanedelveis.StrB64T(_io__raw_data, self, self._root)


    class GeoscanGnss(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.gnss_timestamp = self._io.read_u4le()
            self.valid = self._io.read_u1()
            if not  ((self.valid == 1)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.valid, self._io, u"/types/geoscan_gnss/seq/1")
            self.year = self._io.read_u2le()
            self.month = self._io.read_u1()
            self.day = self._io.read_u1()
            self.hour = self._io.read_u1()
            self.minute = self._io.read_u1()
            self.second = self._io.read_u2le()
            self.dutc = self._io.read_u1()
            self.offset_gnss = self._io.read_u2le()
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self.z = self._io.read_s4le()
            self.v_x = self._io.read_s4le()
            self.v_y = self._io.read_s4le()
            self.v_z = self._io.read_s4le()
            self.vdop = self._io.read_u2le()
            self.hdop = self._io.read_u2le()
            self.pdop = self._io.read_u2le()
            self.tdop = self._io.read_u2le()


    class GeoscanEps(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_timestamp = self._io.read_u4le()
            self.eps_cell_current = self._io.read_u4le()
            self.eps_system_current = self._io.read_u4le()
            self.reserved0 = self._io.read_u4le()
            self.reserved1 = self._io.read_u4le()
            self.reserved2 = self._io.read_s2le()
            self.reserved3 = self._io.read_u2le()
            self.eps_cell_voltage_half = self._io.read_u1()
            self.eps_cell_voltage_full = self._io.read_u1()
            self.reserved4 = self._io.read_s2le()
            self.reserved5 = self._io.read_s1()
            self.reserved6 = self._io.read_u4le()


    class GeoscanTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cmd = self._io.read_u1()
            _on = self.cmd
            if _on == 10:
                self.payload = Geoscanedelveis.GeoscanGnss(self._io, self, self._root)
            elif _on == 6:
                self.payload = Geoscanedelveis.GeoscanFakel(self._io, self, self._root)
            elif _on == 7:
                self.payload = Geoscanedelveis.GeoscanGnss(self._io, self, self._root)
            elif _on == 1:
                self.payload = Geoscanedelveis.GeoscanAdc(self._io, self, self._root)
            elif _on == 11:
                self.payload = Geoscanedelveis.GeoscanPhoto(self._io, self, self._root)
            elif _on == 5:
                self.payload = Geoscanedelveis.GeoscanFakel(self._io, self, self._root)
            elif _on == 8:
                self.payload = Geoscanedelveis.GeoscanGnss(self._io, self, self._root)
            elif _on == 9:
                self.payload = Geoscanedelveis.GeoscanGnss(self._io, self, self._root)
            elif _on == 2:
                self.payload = Geoscanedelveis.GeoscanEps(self._io, self, self._root)


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


    class GeoscanBeaconTlm(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.obc_timestamp = self._io.read_u4le()
            self.eps_cell_current = self._io.read_u2le()
            self.eps_system_current = self._io.read_u2le()
            self.eps_cell_voltage_half = self._io.read_u2le()
            self.eps_cell_voltage_full = self._io.read_u2le()
            self.adc_temperature_pos_x = self._io.read_s1()
            self.adc_temperature_neg_x = self._io.read_s1()
            self.adc_temperature_pos_y = self._io.read_s1()
            self.adc_temperature_neg_y = self._io.read_s1()
            self.adc_temperature_pos_z = self._io.read_s1()
            self.adc_temperature_neg_z = self._io.read_s1()
            self.adc_temperature_cell1 = self._io.read_s1()
            self.adc_temperature_cell2 = self._io.read_s1()
            self.obc_cpu_load = self._io.read_u1()
            self.obc_boot_count = self._io.read_u2le()
            self.comm_boot_count = self._io.read_u2le()
            self.comm_rssi = self._io.read_s1()


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
            self.callsign_ror = Geoscanedelveis.Callsign(_io__raw_callsign_ror, self, self._root)


    class GeoscanAdc(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adc_timestamp = self._io.read_u4le()
            self.sun_sensor_pos_x = self._io.read_u4le()
            self.sun_sensor_neg_x = self._io.read_u4le()
            self.sun_sensor_pos_y = self._io.read_u4le()
            self.sun_sensor_neg_y = self._io.read_u4le()
            self.sun_sensor_neg_z = self._io.read_u4le()
            self.mag_sensor_pos_x = self._io.read_s1()
            self.mag_sensor_neg_x = self._io.read_s1()
            self.mag_sensor_pos_y = self._io.read_s1()
            self.mag_sensor_neg_y = self._io.read_s1()
            self.mag_sensor_pos_z = self._io.read_s1()
            self.mag_sensor_neg_z = self._io.read_s1()
            self.temperature_pos_x = self._io.read_s1()
            self.temperature_neg_x = self._io.read_s1()
            self.temperature_pos_y = self._io.read_s1()
            self.temperature_neg_y = self._io.read_s1()
            self.temperature_pos_z = self._io.read_s1()
            self.temperature_neg_z = self._io.read_s1()
            self.temperature_cell1 = self._io.read_s1()
            self.temperature_cell2 = self._io.read_s1()
            self.status = self._io.read_u4le()


    class GeoscanFakel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.fakel_timestamp = self._io.read_u4le()
            self.bitfield0 = self._io.read_u1()
            self.bitfield1 = self._io.read_u1()
            self.voltage_80v = self._io.read_u2le()
            self.voltage_13v = self._io.read_u2le()
            self.current_valve = self._io.read_u2le()
            self.voltage_valve = self._io.read_u2le()
            self.current_control_valve = self._io.read_u2le()
            self.voltage_control_valve = self._io.read_u2le()
            self.current_ek1 = self._io.read_u2le()
            self.voltage_ek1 = self._io.read_u2le()
            self.current_ek2 = self._io.read_u2le()
            self.voltage_ek2 = self._io.read_u2le()
            self.current_ek = self._io.read_u2le()
            self.voltage_ek = self._io.read_u2le()
            self.temperature_td1 = self._io.read_u2le()
            self.reserved7 = self._io.read_u2le()
            self.temperature_tp = self._io.read_u2le()
            self.pressure_cylinder = self._io.read_u2le()
            self.pressure_receiver = self._io.read_u2le()
            self.switch_on_counter = self._io.read_u2le()
            self.time_switched_on_counter = self._io.read_u2le()
            self.bitfield3 = self._io.read_u1()
            self.state = self._io.read_u1()
            self.reserved8 = self._io.read_u1()
            self.reserved9 = self._io.read_u1()
            self.pump_time = self._io.read_u2le()
            self.time_of_last_pump = self._io.read_u2le()
            self.reserved10 = self._io.read_u1()


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
        self._m_type = self._io.read_u4be()
        self._io.seek(_pos)
        return getattr(self, '_m_type', None)


