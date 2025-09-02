# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sr0(KaitaiStruct):
    """:field callsign_lora: id1.id2.callsign_lora
    :field frame_number: id1.id2.frame_number
    :field message_type: id1.id2.message_type
    :field transmission_power: id1.id2.transmission_power
    :field satellite_unix_time: id1.id2.satellite_unix_time
    :field obc_temperature_celsius: id1.id2.obc_temperature_celsius
    :field battery_temperature_celsius: id1.id2.battery_temperature_celsius
    :field external_temperature_celsius: id1.id2.external_temperature_celsius
    :field base_plate_temperature_celsius: id1.id2.base_plate_temperature_celsius
    :field solar_panel_temperature_celsius: id1.id2.solar_panel_temperature_celsius
    :field radiation_microsv_per_h: id1.id2.radiation_microsv_per_h
    :field bus_voltage_v: id1.id2.bus_voltage_v
    :field bus_current_a: id1.id2.bus_current_a
    :field battery_maximum_capacity_ah: id1.id2.battery_maximum_capacity_ah
    :field battery_remaining_capacity_ah: id1.id2.battery_remaining_capacity_ah
    :field solar_bus_voltage_v: id1.id2.solar_bus_voltage_v
    :field solar_bus_current_a: id1.id2.solar_bus_current_a
    :field boot_counter: id1.id2.boot_counter
    :field checksum: id1.id2.checksum
    :field dest_callsign: id1.id2.ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: id1.id2.ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: id1.id2.ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: id1.id2.ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: id1.id2.ax25_frame.ax25_header.ctl
    :field pid: id1.id2.ax25_frame.ax25_header.pid
    :field callsign_fsk: id1.id2.ax25_frame.ax25_payload.callsign_fsk
    :field frame_number: id1.id2.ax25_frame.ax25_payload.frame_number
    :field message_type: id1.id2.ax25_frame.ax25_payload.message_type
    :field transmission_power: id1.id2.ax25_frame.ax25_payload.transmission_power
    :field satellite_unix_time: id1.id2.ax25_frame.ax25_payload.satellite_unix_time
    :field obc_temperature_celsius: id1.id2.ax25_frame.ax25_payload.obc_temperature_celsius
    :field battery_temperature_celsius: id1.id2.ax25_frame.ax25_payload.battery_temperature_celsius
    :field external_temperature_celsius: id1.id2.ax25_frame.ax25_payload.external_temperature_celsius
    :field base_plate_temperature_celsius: id1.id2.ax25_frame.ax25_payload.base_plate_temperature_celsius
    :field solar_panel_temperature_celsius: id1.id2.ax25_frame.ax25_payload.solar_panel_temperature_celsius
    :field radiation_microsv_per_h: id1.id2.ax25_frame.ax25_payload.radiation_microsv_per_h
    :field bus_voltage_v: id1.id2.ax25_frame.ax25_payload.bus_voltage_v
    :field bus_current_a: id1.id2.ax25_frame.ax25_payload.bus_current_a
    :field battery_maximum_capacity_ah: id1.id2.ax25_frame.ax25_payload.battery_maximum_capacity_ah
    :field battery_remaining_capacity_ah: id1.id2.ax25_frame.ax25_payload.battery_remaining_capacity_ah
    :field solar_bus_voltage_v: id1.id2.ax25_frame.ax25_payload.solar_bus_voltage_v
    :field solar_bus_current_a: id1.id2.ax25_frame.ax25_payload.solar_bus_current_a
    :field boot_counter: id1.id2.ax25_frame.ax25_payload.boot_counter
    :field checksum: id1.id2.ax25_frame.ax25_payload.checksum
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.id1 = Sr0.Type1(self._io, self, self._root)

    class Type1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.lora_or_fsk
            if _on == 1397895251:
                self.id2 = Sr0.Lora(self._io, self, self._root)
            elif _on == 2795545750:
                self.id2 = Sr0.Fsk(self._io, self, self._root)

        @property
        def lora_or_fsk(self):
            if hasattr(self, '_m_lora_or_fsk'):
                return self._m_lora_or_fsk

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_lora_or_fsk = self._io.read_u4be()
            self._io.seek(_pos)
            return getattr(self, '_m_lora_or_fsk', None)


    class Lora(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign_lora = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign_lora == u"SR0SAT")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign_lora, self._io, u"/types/lora/seq/0")
            self.frame_number = self._io.read_u2le()
            self.message_type = self._io.read_u1()
            self.transmission_power = self._io.read_u1()
            self.satellite_unix_time = self._io.read_u4le()
            self.obc_temperature = self._io.read_s2le()
            self.battery_temperature = self._io.read_s2le()
            self.external_temperature = self._io.read_s2le()
            self.base_plate_temperature = self._io.read_s2le()
            self.solar_panel_temperature = self._io.read_s2le()
            self.radiation = self._io.read_s2le()
            self.bus_voltage = self._io.read_u2le()
            self.bus_current = self._io.read_s2le()
            self.battery_maximum_capacity = self._io.read_u2le()
            self.battery_remaining_capacity = self._io.read_u2le()
            self.solar_bus_voltage = self._io.read_u2le()
            self.solar_bus_current = self._io.read_u2le()
            self.boot_counter = self._io.read_u2le()
            self.checksum = self._io.read_u1()

        @property
        def battery_temperature_celsius(self):
            if hasattr(self, '_m_battery_temperature_celsius'):
                return self._m_battery_temperature_celsius

            self._m_battery_temperature_celsius = (self.battery_temperature / 10.0)
            return getattr(self, '_m_battery_temperature_celsius', None)

        @property
        def solar_bus_current_a(self):
            if hasattr(self, '_m_solar_bus_current_a'):
                return self._m_solar_bus_current_a

            self._m_solar_bus_current_a = (self.solar_bus_current / 1000.0)
            return getattr(self, '_m_solar_bus_current_a', None)

        @property
        def base_plate_temperature_celsius(self):
            if hasattr(self, '_m_base_plate_temperature_celsius'):
                return self._m_base_plate_temperature_celsius

            self._m_base_plate_temperature_celsius = (self.base_plate_temperature / 10.0)
            return getattr(self, '_m_base_plate_temperature_celsius', None)

        @property
        def solar_panel_temperature_celsius(self):
            if hasattr(self, '_m_solar_panel_temperature_celsius'):
                return self._m_solar_panel_temperature_celsius

            self._m_solar_panel_temperature_celsius = (self.solar_panel_temperature / 10.0)
            return getattr(self, '_m_solar_panel_temperature_celsius', None)

        @property
        def bus_current_a(self):
            if hasattr(self, '_m_bus_current_a'):
                return self._m_bus_current_a

            self._m_bus_current_a = (self.bus_current / 1000.0)
            return getattr(self, '_m_bus_current_a', None)

        @property
        def solar_bus_voltage_v(self):
            if hasattr(self, '_m_solar_bus_voltage_v'):
                return self._m_solar_bus_voltage_v

            self._m_solar_bus_voltage_v = (self.solar_bus_voltage / 1000.0)
            return getattr(self, '_m_solar_bus_voltage_v', None)

        @property
        def battery_remaining_capacity_ah(self):
            if hasattr(self, '_m_battery_remaining_capacity_ah'):
                return self._m_battery_remaining_capacity_ah

            self._m_battery_remaining_capacity_ah = (self.battery_remaining_capacity / 1000.0)
            return getattr(self, '_m_battery_remaining_capacity_ah', None)

        @property
        def obc_temperature_celsius(self):
            if hasattr(self, '_m_obc_temperature_celsius'):
                return self._m_obc_temperature_celsius

            self._m_obc_temperature_celsius = (self.obc_temperature / 10.0)
            return getattr(self, '_m_obc_temperature_celsius', None)

        @property
        def external_temperature_celsius(self):
            if hasattr(self, '_m_external_temperature_celsius'):
                return self._m_external_temperature_celsius

            self._m_external_temperature_celsius = (self.external_temperature / 10.0)
            return getattr(self, '_m_external_temperature_celsius', None)

        @property
        def bus_voltage_v(self):
            if hasattr(self, '_m_bus_voltage_v'):
                return self._m_bus_voltage_v

            self._m_bus_voltage_v = (self.bus_voltage / 1000.0)
            return getattr(self, '_m_bus_voltage_v', None)

        @property
        def battery_maximum_capacity_ah(self):
            if hasattr(self, '_m_battery_maximum_capacity_ah'):
                return self._m_battery_maximum_capacity_ah

            self._m_battery_maximum_capacity_ah = (self.battery_maximum_capacity / 1000.0)
            return getattr(self, '_m_battery_maximum_capacity_ah', None)

        @property
        def radiation_microsv_per_h(self):
            if hasattr(self, '_m_radiation_microsv_per_h'):
                return self._m_radiation_microsv_per_h

            self._m_radiation_microsv_per_h = (self.radiation / 100.0)
            return getattr(self, '_m_radiation_microsv_per_h', None)


    class Fsk(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_frame = Sr0.Fsk.Ax25Frame(self._io, self, self._root)

        class Ax25Frame(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.ax25_header = Sr0.Fsk.Ax25Header(self._io, self, self._root)
                self.ax25_payload = Sr0.Fsk.Ax25Payload(self._io, self, self._root)


        class Ax25Payload(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.callsign_fsk = (self._io.read_bytes(6)).decode(u"ASCII")
                if not  ((self.callsign_fsk == u"SR0SAT")) :
                    raise kaitaistruct.ValidationNotAnyOfError(self.callsign_fsk, self._io, u"/types/fsk/types/ax25_payload/seq/0")
                self.frame_number = self._io.read_u2le()
                self.message_type = self._io.read_u1()
                self.transmission_power = self._io.read_u1()
                self.satellite_unix_time = self._io.read_u4le()
                self.obc_temperature = self._io.read_s2le()
                self.battery_temperature = self._io.read_s2le()
                self.external_temperature = self._io.read_s2le()
                self.base_plate_temperature = self._io.read_s2le()
                self.solar_panel_temperature = self._io.read_s2le()
                self.radiation = self._io.read_s2le()
                self.bus_voltage = self._io.read_u2le()
                self.bus_current = self._io.read_s2le()
                self.battery_maximum_capacity = self._io.read_u2le()
                self.battery_remaining_capacity = self._io.read_u2le()
                self.solar_bus_voltage = self._io.read_u2le()
                self.solar_bus_current = self._io.read_u2le()
                self.boot_counter = self._io.read_u2le()
                self.checksum = self._io.read_u1()

            @property
            def battery_temperature_celsius(self):
                if hasattr(self, '_m_battery_temperature_celsius'):
                    return self._m_battery_temperature_celsius

                self._m_battery_temperature_celsius = (self.battery_temperature / 10.0)
                return getattr(self, '_m_battery_temperature_celsius', None)

            @property
            def solar_bus_current_a(self):
                if hasattr(self, '_m_solar_bus_current_a'):
                    return self._m_solar_bus_current_a

                self._m_solar_bus_current_a = (self.solar_bus_current / 1000.0)
                return getattr(self, '_m_solar_bus_current_a', None)

            @property
            def base_plate_temperature_celsius(self):
                if hasattr(self, '_m_base_plate_temperature_celsius'):
                    return self._m_base_plate_temperature_celsius

                self._m_base_plate_temperature_celsius = (self.base_plate_temperature / 10.0)
                return getattr(self, '_m_base_plate_temperature_celsius', None)

            @property
            def solar_panel_temperature_celsius(self):
                if hasattr(self, '_m_solar_panel_temperature_celsius'):
                    return self._m_solar_panel_temperature_celsius

                self._m_solar_panel_temperature_celsius = (self.solar_panel_temperature / 10.0)
                return getattr(self, '_m_solar_panel_temperature_celsius', None)

            @property
            def bus_current_a(self):
                if hasattr(self, '_m_bus_current_a'):
                    return self._m_bus_current_a

                self._m_bus_current_a = (self.bus_current / 1000.0)
                return getattr(self, '_m_bus_current_a', None)

            @property
            def solar_bus_voltage_v(self):
                if hasattr(self, '_m_solar_bus_voltage_v'):
                    return self._m_solar_bus_voltage_v

                self._m_solar_bus_voltage_v = (self.solar_bus_voltage / 1000.0)
                return getattr(self, '_m_solar_bus_voltage_v', None)

            @property
            def battery_remaining_capacity_ah(self):
                if hasattr(self, '_m_battery_remaining_capacity_ah'):
                    return self._m_battery_remaining_capacity_ah

                self._m_battery_remaining_capacity_ah = (self.battery_remaining_capacity / 1000.0)
                return getattr(self, '_m_battery_remaining_capacity_ah', None)

            @property
            def obc_temperature_celsius(self):
                if hasattr(self, '_m_obc_temperature_celsius'):
                    return self._m_obc_temperature_celsius

                self._m_obc_temperature_celsius = (self.obc_temperature / 10.0)
                return getattr(self, '_m_obc_temperature_celsius', None)

            @property
            def external_temperature_celsius(self):
                if hasattr(self, '_m_external_temperature_celsius'):
                    return self._m_external_temperature_celsius

                self._m_external_temperature_celsius = (self.external_temperature / 10.0)
                return getattr(self, '_m_external_temperature_celsius', None)

            @property
            def bus_voltage_v(self):
                if hasattr(self, '_m_bus_voltage_v'):
                    return self._m_bus_voltage_v

                self._m_bus_voltage_v = (self.bus_voltage / 1000.0)
                return getattr(self, '_m_bus_voltage_v', None)

            @property
            def battery_maximum_capacity_ah(self):
                if hasattr(self, '_m_battery_maximum_capacity_ah'):
                    return self._m_battery_maximum_capacity_ah

                self._m_battery_maximum_capacity_ah = (self.battery_maximum_capacity / 1000.0)
                return getattr(self, '_m_battery_maximum_capacity_ah', None)

            @property
            def radiation_microsv_per_h(self):
                if hasattr(self, '_m_radiation_microsv_per_h'):
                    return self._m_radiation_microsv_per_h

                self._m_radiation_microsv_per_h = (self.radiation / 100.0)
                return getattr(self, '_m_radiation_microsv_per_h', None)


        class Ax25Header(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.dest_callsign_raw = Sr0.Fsk.CallsignRaw(self._io, self, self._root)
                self.dest_ssid_raw = Sr0.Fsk.SsidMask(self._io, self, self._root)
                self.src_callsign_raw = Sr0.Fsk.CallsignRaw(self._io, self, self._root)
                self.src_ssid_raw = Sr0.Fsk.SsidMask(self._io, self, self._root)
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
                self.callsign_ror = Sr0.Fsk.Callsign(_io__raw_callsign_ror, self, self._root)




