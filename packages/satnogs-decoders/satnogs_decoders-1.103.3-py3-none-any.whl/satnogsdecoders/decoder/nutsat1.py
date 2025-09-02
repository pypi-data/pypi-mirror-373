# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Nutsat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field identifier: ax25_frame.payload.ax25_info.tlm.identifier
    :field eps_pv1: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_pv1
    :field eps_pv2: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_pv2
    :field eps_pv3: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_pv3
    :field eps_pv4: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_pv4
    :field eps_battery: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_battery
    :field eps_power33: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_power33
    :field eps_power5: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_power5
    :field eps_vgps: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_vgps
    :field eps_sw: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_sw
    :field eps_t_bat: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_t_bat
    :field eps_day: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_day
    :field eps_vmtq: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_vmtq
    :field eps_vadsb: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_vadsb
    :field eps_vuhf: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_vuhf
    :field eps_t_venv: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_t_venv
    :field eps_hour: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_hour
    :field eps_minute: ax25_frame.payload.ax25_info.tlm.data.eps_str.eps_minute
    :field cdhs_sun1: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_sun1
    :field cdhs_sun2: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_sun2
    :field cdhs_sun3: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_sun3
    :field cdhs_acc_x: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_acc_x
    :field cdhs_acc_y: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_acc_y
    :field cdhs_acc_z: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_acc_z
    :field cdhs_gyro_x: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_gyro_x
    :field cdhs_gyro_y: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_gyro_y
    :field cdhs_gyro_z: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_gyro_z
    :field cdhs_temp: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_temp
    :field cdhs_mx: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_mx
    :field cdhs_my: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_my
    :field cdhs_mz: ax25_frame.payload.ax25_info.tlm.data.obc_str.cdhs_mz
    :field monitor: ax25_frame.payload.ax25_info.tlm.monitor
    :field message: ax25_frame.payload.ax25_info.beacon.message
    :field rx_volt: ax25_frame.payload.ax25_info.beacon.rx_volt
    :field tx_volt: ax25_frame.payload.ax25_info.beacon.tx_volt
    :field ttc_temp: ax25_frame.payload.ax25_info.beacon.ttc_temp
    :field monitor: ax25_frame.payload.ax25_info.beacon.monitor
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Nutsat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Nutsat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Nutsat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Nutsat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Nutsat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Nutsat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Nutsat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Nutsat1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Nutsat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Nutsat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Nutsat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Nutsat1.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Nutsat1.Repeater(self._io, self, self._root)

            self.ctl = self._io.read_u1()


    class UiFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Nutsat1.BeaconT(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"BN0UT ") or (self.callsign == u"APX1S ") or (self.callsign == u"WIDE1 ")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class EpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.eps_pv1 = self._io.read_u2be()
            self.eps_pv2 = self._io.read_u2be()
            self.eps_pv3 = self._io.read_u2be()
            self.eps_pv4 = self._io.read_u2be()
            self.eps_battery = self._io.read_u2be()
            self.eps_power33 = self._io.read_u2be()
            self.eps_power5 = self._io.read_u2be()
            self.eps_vgps = self._io.read_u2be()
            self.eps_sw = self._io.read_u2be()
            self.eps_t_bat = self._io.read_s2be()
            self.eps_day = self._io.read_u2be()
            self.eps_vmtq = self._io.read_u2be()
            self.eps_vadsb = self._io.read_u2be()
            self.eps_vuhf = self._io.read_u2be()
            self.eps_t_venv = self._io.read_s2be()
            self.eps_hour = self._io.read_u2be()
            self.eps_minute = self._io.read_u2be()


    class HeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes_term(58, False, True, True)).decode(u"ASCII")
            _on = self.identifier
            if _on == u">EPS":
                self.data = Nutsat1.EpsStrT(self._io, self, self._root)
            elif _on == u">GPS3":
                self.data = Nutsat1.UnknownT(self._io, self, self._root)
            elif _on == u">GPS1":
                self.data = Nutsat1.UnknownT(self._io, self, self._root)
            elif _on == u">ADSB":
                self.data = Nutsat1.UnknownT(self._io, self, self._root)
            elif _on == u">MTQSD":
                self.data = Nutsat1.UnknownT(self._io, self, self._root)
            elif _on == u">OBC":
                self.data = Nutsat1.ObcStrT(self._io, self, self._root)
            elif _on == u">GPS2":
                self.data = Nutsat1.UnknownT(self._io, self, self._root)
            else:
                self.data = Nutsat1.UnknownT(self._io, self, self._root)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_monitor = (self._io.read_bytes_full()).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_monitor', None)


    class BeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            if self.is_beacon == False:
                self.tlm = Nutsat1.HeaderT(self._io, self, self._root)

            if self.is_beacon:
                self._raw_beacon = self._io.read_bytes_full()
                _io__raw_beacon = KaitaiStream(BytesIO(self._raw_beacon))
                self.beacon = Nutsat1.AsciiBeaconT(_io__raw_beacon, self, self._root)


        @property
        def is_beacon(self):
            if hasattr(self, '_m_is_beacon'):
                return self._m_is_beacon

            self._m_is_beacon = (True if self.beacon_id == 82 else False)
            return getattr(self, '_m_is_beacon', None)

        @property
        def beacon_id(self):
            if hasattr(self, '_m_beacon_id'):
                return self._m_beacon_id

            _pos = self._io.pos()
            self._io.seek(1)
            self._m_beacon_id = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_beacon_id', None)


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


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Nutsat1.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Nutsat1.SsidMask(self._io, self, self._root)


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
                _ = Nutsat1.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class AsciiBeaconT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes(2)).decode(u"ASCII")
            if not  ((self.identifier == u">R")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.identifier, self._io, u"/types/ascii_beacon_t/seq/0")
            self.rx_volt_str = (self._io.read_bytes(2)).decode(u"ASCII")
            self.pad0 = self._io.read_bytes(1)
            self.rx_volt_frac_str = (self._io.read_bytes(1)).decode(u"ASCII")
            self.pad1 = self._io.read_bytes(2)
            self.tx_volt_str = (self._io.read_bytes(1)).decode(u"ASCII")
            self.pad2 = self._io.read_bytes(1)
            self.tx_volt_frac_str = (self._io.read_bytes(1)).decode(u"ASCII")
            self.pad3 = self._io.read_bytes(1)
            self.ttc_temp_str = (self._io.read_bytes(2)).decode(u"ASCII")
            self.pad4 = self._io.read_bytes(1)
            self.ttc_temp_frac_str = (self._io.read_bytes(1)).decode(u"ASCII")
            self.message = (self._io.read_bytes_full()).decode(u"ASCII")

        @property
        def ttc_temp_is_neg(self):
            if hasattr(self, '_m_ttc_temp_is_neg'):
                return self._m_ttc_temp_is_neg

            self._m_ttc_temp_is_neg = (True if self.ttc_temp_sign == 45 else False)
            return getattr(self, '_m_ttc_temp_is_neg', None)

        @property
        def ttc_temp_sign(self):
            if hasattr(self, '_m_ttc_temp_sign'):
                return self._m_ttc_temp_sign

            _pos = self._io.pos()
            self._io.seek(12)
            self._m_ttc_temp_sign = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_ttc_temp_sign', None)

        @property
        def tx_volt(self):
            if hasattr(self, '_m_tx_volt'):
                return self._m_tx_volt

            self._m_tx_volt = (int(self.tx_volt_str) + (int(self.tx_volt_frac_str) / 10.0))
            return getattr(self, '_m_tx_volt', None)

        @property
        def rx_volt(self):
            if hasattr(self, '_m_rx_volt'):
                return self._m_rx_volt

            self._m_rx_volt = (int(self.rx_volt_str) + (int(self.rx_volt_frac_str) / 10.0))
            return getattr(self, '_m_rx_volt', None)

        @property
        def monitor(self):
            if hasattr(self, '_m_monitor'):
                return self._m_monitor

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_monitor = (self._io.read_bytes_full()).decode(u"ASCII")
            self._io.seek(_pos)
            return getattr(self, '_m_monitor', None)

        @property
        def ttc_temp(self):
            if hasattr(self, '_m_ttc_temp'):
                return self._m_ttc_temp

            self._m_ttc_temp = (int(self.ttc_temp_str) + (((-1 * int(self.ttc_temp_frac_str)) / 10.0) if self.ttc_temp_is_neg else (int(self.ttc_temp_frac_str) / 10.0)))
            return getattr(self, '_m_ttc_temp', None)


    class ObcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cdhs_sun1 = self._io.read_s2be()
            self.cdhs_sun2 = self._io.read_s2be()
            self.cdhs_sun3 = self._io.read_s2be()
            self.cdhs_acc_x = self._io.read_s2be()
            self.cdhs_acc_y = self._io.read_s2be()
            self.cdhs_acc_z = self._io.read_s2be()
            self.cdhs_gyro_x = self._io.read_s2be()
            self.cdhs_gyro_y = self._io.read_s2be()
            self.cdhs_gyro_z = self._io.read_s2be()
            self.cdhs_temp = self._io.read_s2be()
            self.cdhs_mx = self._io.read_s2be()
            self.cdhs_my = self._io.read_s2be()
            self.cdhs_mz = self._io.read_s2be()


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
            self.callsign_ror = Nutsat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class UnknownT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.content = self._io.read_bytes_full()


    class ObcStrT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_obc_str = self._io.read_bytes(52)
            _process = satnogsdecoders.process.Unhexl()
            self._raw_obc_str = _process.decode(self._raw__raw_obc_str)
            _io__raw_obc_str = KaitaiStream(BytesIO(self._raw_obc_str))
            self.obc_str = Nutsat1.ObcT(_io__raw_obc_str, self, self._root)


    class EpsStrT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw__raw_eps_str = self._io.read_bytes(68)
            _process = satnogsdecoders.process.Unhexl()
            self._raw_eps_str = _process.decode(self._raw__raw_eps_str)
            _io__raw_eps_str = KaitaiStream(BytesIO(self._raw_eps_str))
            self.eps_str = Nutsat1.EpsT(_io__raw_eps_str, self, self._root)



