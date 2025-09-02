# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sharjahsat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field rpt_callsign: ax25_frame.ax25_header.repeater.rpt_instance[0].rpt_callsign_raw.callsign_ror.callsign
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field identifier: ax25_frame.payload.ax25_info.identifier
    :field tm_id: ax25_frame.payload.ax25_info.tm_id
    :field data_length: ax25_frame.payload.ax25_info.data_length
    :field packet_counter: ax25_frame.payload.ax25_info.packet_counter
    :field image_data: ax25_frame.payload.ax25_info.data.image_data.data.data_str
    :field op_mode: ax25_frame.payload.ax25_info.data.system_info.op_mode
    :field restart_count: ax25_frame.payload.ax25_info.data.system_info.restart_count
    :field last_reset_cause: ax25_frame.payload.ax25_info.data.system_info.last_reset_cause
    :field system_uptime: ax25_frame.payload.ax25_info.data.system_info.system_uptime
    :field system_time: ax25_frame.payload.ax25_info.data.system_info.system_time
    :field tlm_board_temp1: ax25_frame.payload.ax25_info.data.obc.tlm_board_temp1
    :field tlm_board_temp2: ax25_frame.payload.ax25_info.data.obc.tlm_board_temp2
    :field tlm_board_temp3: ax25_frame.payload.ax25_info.data.obc.tlm_board_temp3
    :field tlm_vbat_v: ax25_frame.payload.ax25_info.data.obc.tlm_vbat_v
    :field tlm_vbat_i: ax25_frame.payload.ax25_info.data.obc.tlm_vbat_i
    :field tlm_vbat_plat_v: ax25_frame.payload.ax25_info.data.obc.tlm_vbat_plat_v
    :field tlm_3v3_plat_v: ax25_frame.payload.ax25_info.data.obc.tlm_3v3_plat_v
    :field tlm_vbat_periph_i: ax25_frame.payload.ax25_info.data.obc.tlm_vbat_periph_i
    :field tlm_3v3_periph_i: ax25_frame.payload.ax25_info.data.obc.tlm_3v3_periph_i
    :field tlm_vbat_periph_v: ax25_frame.payload.ax25_info.data.obc.tlm_vbat_periph_v
    :field tlm_3v3_periph_v: ax25_frame.payload.ax25_info.data.obc.tlm_3v3_periph_v
    :field timestamp_hh: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_hh
    :field timestamp_mm: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_mm
    :field timestamp_ss: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_ss
    :field timestamp_dd: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_dd
    :field timestamp_mo: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_mo
    :field timestamp_yy: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_yy
    :field timestamp_dow: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.timestamp_dow
    :field temperature: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.temperature
    :field antenna_status: ax25_frame.payload.ax25_info.data.interfacebrd_rtc.antenna_status
    :field vbat: ax25_frame.payload.ax25_info.data.battery.vbat
    :field ibat: ax25_frame.payload.ax25_info.data.battery.ibat
    :field vpcm3v3: ax25_frame.payload.ax25_info.data.battery.vpcm3v3
    :field vpcm5v: ax25_frame.payload.ax25_info.data.battery.vpcm5v
    :field ipcm3v3: ax25_frame.payload.ax25_info.data.battery.ipcm3v3
    :field ipcm5v: ax25_frame.payload.ax25_info.data.battery.ipcm5v
    :field tbrd: ax25_frame.payload.ax25_info.data.battery.tbrd
    :field tbat1: ax25_frame.payload.ax25_info.data.battery.tbat1
    :field tbat2: ax25_frame.payload.ax25_info.data.battery.tbat2
    :field tbat3: ax25_frame.payload.ax25_info.data.battery.tbat3
    :field vpcmbatv: ax25_frame.payload.ax25_info.data.eps.vpcmbatv
    :field ipcmbatv: ax25_frame.payload.ax25_info.data.eps.ipcmbatv
    :field eps_vpcm3v3: ax25_frame.payload.ax25_info.data.eps.vpcm3v3
    :field eps_ipcm3v3: ax25_frame.payload.ax25_info.data.eps.ipcm3v3
    :field eps_vpcm5v: ax25_frame.payload.ax25_info.data.eps.vpcm5v
    :field eps_ipcm5v: ax25_frame.payload.ax25_info.data.eps.ipcm5v
    :field i3v3drw: ax25_frame.payload.ax25_info.data.eps.i3v3drw
    :field i5vdrw: ax25_frame.payload.ax25_info.data.eps.i5vdrw
    :field eps_tbrd: ax25_frame.payload.ax25_info.data.eps.tbrd
    :field tbrd_db: ax25_frame.payload.ax25_info.data.eps.tbrd_db
    :field ipcm12v: ax25_frame.payload.ax25_info.data.eps.ipcm12v
    :field vpcm12v: ax25_frame.payload.ax25_info.data.eps.vpcm12v
    :field adcs_state: ax25_frame.payload.ax25_info.data.adcs.adcs_state
    :field sat_pos_llh_lat: ax25_frame.payload.ax25_info.data.adcs.sat_pos_llh_lat
    :field sat_pos_llh_lon: ax25_frame.payload.ax25_info.data.adcs.sat_pos_llh_lon
    :field sat_pos_llh_alt: ax25_frame.payload.ax25_info.data.adcs.sat_pos_llh_alt
    :field estm_att_angle_yaw: ax25_frame.payload.ax25_info.data.adcs.estm_att_angle_yaw
    :field estm_att_angle_pitch: ax25_frame.payload.ax25_info.data.adcs.estm_att_angle_pitch
    :field estm_att_angle_roll: ax25_frame.payload.ax25_info.data.adcs.estm_att_angle_roll
    :field estm_ang_rate_yaw: ax25_frame.payload.ax25_info.data.adcs.estm_ang_rate_yaw
    :field estm_ang_rate_pitch: ax25_frame.payload.ax25_info.data.adcs.estm_ang_rate_pitch
    :field estm_ang_rate_roll: ax25_frame.payload.ax25_info.data.adcs.estm_ang_rate_roll
    :field adcs_gps: ax25_frame.payload.ax25_info.data.adcs.gps.data.data_str
    :field smps_temp: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.smps_temp
    :field pa_temp: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.pa_temp
    :field current_3v3: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.current_3v3
    :field voltage_3v3: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.voltage_3v3
    :field current_5v: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.current_5v
    :field voltage_5v: ax25_frame.payload.ax25_info.data.uhf_vhf_modem.voltage_5v
    :field battery_current: ax25_frame.payload.ax25_info.data.s_band_modem.battery_current
    :field pa_current: ax25_frame.payload.ax25_info.data.s_band_modem.pa_current
    :field battery_voltage: ax25_frame.payload.ax25_info.data.s_band_modem.battery_voltage
    :field pa_voltage: ax25_frame.payload.ax25_info.data.s_band_modem.pa_voltage
    :field pa_temperature: ax25_frame.payload.ax25_info.data.s_band_modem.pa_temperature
    :field rf_output_power: ax25_frame.payload.ax25_info.data.s_band_modem.rf_output_power
    :field board_temp_top: ax25_frame.payload.ax25_info.data.s_band_modem.board_temp_top
    :field board_temp_bottom: ax25_frame.payload.ax25_info.data.s_band_modem.board_temp_bottom
    :field vbcr1: ax25_frame.payload.ax25_info.data.solar_panels.vbcr1
    :field vbcr2: ax25_frame.payload.ax25_info.data.solar_panels.vbcr2
    :field vbcr3: ax25_frame.payload.ax25_info.data.solar_panels.vbcr3
    :field vbcr4: ax25_frame.payload.ax25_info.data.solar_panels.vbcr4
    :field vbcr5: ax25_frame.payload.ax25_info.data.solar_panels.vbcr5
    :field vbcr6: ax25_frame.payload.ax25_info.data.solar_panels.vbcr6
    :field vbcr7: ax25_frame.payload.ax25_info.data.solar_panels.vbcr7
    :field vbcr8: ax25_frame.payload.ax25_info.data.solar_panels.vbcr8
    :field vbcr9: ax25_frame.payload.ax25_info.data.solar_panels.vbcr9
    :field ibcra1: ax25_frame.payload.ax25_info.data.solar_panels.ibcra1
    :field ibcra2: ax25_frame.payload.ax25_info.data.solar_panels.ibcra2
    :field ibcra3: ax25_frame.payload.ax25_info.data.solar_panels.ibcra3
    :field ibcra4: ax25_frame.payload.ax25_info.data.solar_panels.ibcra4
    :field ibcra5: ax25_frame.payload.ax25_info.data.solar_panels.ibcra5
    :field ibcra6: ax25_frame.payload.ax25_info.data.solar_panels.ibcra6
    :field ibcra7: ax25_frame.payload.ax25_info.data.solar_panels.ibcra7
    :field ibcra8: ax25_frame.payload.ax25_info.data.solar_panels.ibcra8
    :field ibcra9: ax25_frame.payload.ax25_info.data.solar_panels.ibcra9
    :field ibcrb1: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb1
    :field ibcrb2: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb2
    :field ibcrb3: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb3
    :field ibcrb4: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb4
    :field ibcrb5: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb5
    :field ibcrb6: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb6
    :field ibcrb7: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb7
    :field ibcrb8: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb8
    :field ibcrb9: ax25_frame.payload.ax25_info.data.solar_panels.ibcrb9
    :field tbcra1: ax25_frame.payload.ax25_info.data.solar_panels.tbcra1
    :field tbcra2: ax25_frame.payload.ax25_info.data.solar_panels.tbcra2
    :field tbcra3: ax25_frame.payload.ax25_info.data.solar_panels.tbcra3
    :field tbcra4: ax25_frame.payload.ax25_info.data.solar_panels.tbcra4
    :field tbcra5: ax25_frame.payload.ax25_info.data.solar_panels.tbcra5
    :field tbcra6: ax25_frame.payload.ax25_info.data.solar_panels.tbcra6
    :field tbcra7: ax25_frame.payload.ax25_info.data.solar_panels.tbcra7
    :field tbcra8: ax25_frame.payload.ax25_info.data.solar_panels.tbcra8
    :field tbcra9: ax25_frame.payload.ax25_info.data.solar_panels.tbcra9
    :field tbcrb1: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb1
    :field tbcrb2: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb2
    :field tbcrb3: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb3
    :field tbcrb4: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb4
    :field tbcrb5: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb5
    :field tbcrb6: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb6
    :field tbcrb7: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb7
    :field tbcrb8: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb8
    :field tbcrb9: ax25_frame.payload.ax25_info.data.solar_panels.tbcrb9
    :field vidiodeout: ax25_frame.payload.ax25_info.data.solar_panels.vidiodeout
    :field iidiodeout: ax25_frame.payload.ax25_info.data.solar_panels.iidiodeout
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Sharjahsat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Sharjahsat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Sharjahsat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Sharjahsat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Sharjahsat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Sharjahsat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Sharjahsat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Sharjahsat1.IFrame(self._io, self, self._root)


    class SystemInfoT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.op_mode = self._io.read_u2le()
            self.restart_count = self._io.read_u2le()
            self.last_reset_cause = self._io.read_u1()
            self.system_uptime = self._io.read_u4le()
            self.system_time = self._io.read_u4le()


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Sharjahsat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Sharjahsat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Sharjahsat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Sharjahsat1.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Sharjahsat1.Repeater(self._io, self, self._root)

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
            self.ax25_info = Sharjahsat1.HeaderT(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"A60UOS") or (self.callsign == u"A62UOS")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


    class ImageT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_image_data = self._io.read_bytes_full()
            _io__raw_image_data = KaitaiStream(BytesIO(self._raw_image_data))
            self.image_data = Sharjahsat1.DataB64T(_io__raw_image_data, self, self._root)


    class StrB64T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data_str = (self._io.read_bytes_full()).decode(u"ASCII")


    class EpsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vpcmbatv = self._io.read_u2le()
            self.ipcmbatv = self._io.read_s2le()
            self.vpcm3v3 = self._io.read_u2le()
            self.ipcm3v3 = self._io.read_u2le()
            self.vpcm5v = self._io.read_u2le()
            self.ipcm5v = self._io.read_u2le()
            self.i3v3drw = self._io.read_u2le()
            self.i5vdrw = self._io.read_u2le()
            self.tbrd = self._io.read_u2le()
            self.tbrd_db = self._io.read_u2le()
            self.ipcm12v = self._io.read_u2le()
            self.vpcm12v = self._io.read_u2le()


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
            self.data = Sharjahsat1.StrB64T(_io__raw_data, self, self._root)


    class AdcsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.adcs_state = self._io.read_u1()
            self.sat_pos_llh_lat = self._io.read_s2le()
            self.sat_pos_llh_lon = self._io.read_s2le()
            self.sat_pos_llh_alt = self._io.read_s2le()
            self.estm_att_angle_yaw = self._io.read_s2le()
            self.estm_att_angle_pitch = self._io.read_s2le()
            self.estm_att_angle_roll = self._io.read_s2le()
            self.estm_ang_rate_yaw = self._io.read_s2le()
            self.estm_ang_rate_pitch = self._io.read_s2le()
            self.estm_ang_rate_roll = self._io.read_s2le()
            self._raw_gps = self._io.read_bytes(18)
            _io__raw_gps = KaitaiStream(BytesIO(self._raw_gps))
            self.gps = Sharjahsat1.DataB64T(_io__raw_gps, self, self._root)


    class HeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.identifier = (self._io.read_bytes(4)).decode(u"ASCII")
            if not  ((self.identifier == u"ESER")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.identifier, self._io, u"/types/header_t/seq/0")
            self.tm_id = self._io.read_u1()
            self.data_length = self._io.read_u1()
            self.packet_counter = self._io.read_u4le()
            _on = self.tm_id
            if _on == 65:
                self.data = Sharjahsat1.ImageT(self._io, self, self._root)
            elif _on == 80:
                self.data = Sharjahsat1.TlmT(self._io, self, self._root)


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


    class UhfVhfModemT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.smps_temp = self._io.read_u1()
            self.pa_temp = self._io.read_u1()
            self.current_3v3 = self._io.read_u2le()
            self.voltage_3v3 = self._io.read_u2le()
            self.current_5v = self._io.read_u2le()
            self.voltage_5v = self._io.read_u2le()


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Sharjahsat1.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Sharjahsat1.SsidMask(self._io, self, self._root)


    class InterfacebrdRtcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.timestamp_hh = self._io.read_u1()
            self.timestamp_mm = self._io.read_u1()
            self.timestamp_ss = self._io.read_u1()
            self.timestamp_dd = self._io.read_u1()
            self.timestamp_mo = self._io.read_u1()
            self.timestamp_yy = self._io.read_u1()
            self.timestamp_dow = self._io.read_u1()
            self.temperature = self._io.read_s2le()
            self.antenna_status = self._io.read_u1()


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
                _ = Sharjahsat1.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


    class SolarPanelsT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vbcr1 = self._io.read_u2le()
            self.vbcr2 = self._io.read_u2le()
            self.vbcr3 = self._io.read_u2le()
            self.vbcr4 = self._io.read_u2le()
            self.vbcr5 = self._io.read_u2le()
            self.vbcr6 = self._io.read_u2le()
            self.vbcr7 = self._io.read_u2le()
            self.vbcr8 = self._io.read_u2le()
            self.vbcr9 = self._io.read_u2le()
            self.ibcra1 = self._io.read_u2le()
            self.ibcra2 = self._io.read_u2le()
            self.ibcra3 = self._io.read_u2le()
            self.ibcra4 = self._io.read_u2le()
            self.ibcra5 = self._io.read_u2le()
            self.ibcra6 = self._io.read_u2le()
            self.ibcra7 = self._io.read_u2le()
            self.ibcra8 = self._io.read_u2le()
            self.ibcra9 = self._io.read_u2le()
            self.ibcrb1 = self._io.read_u2le()
            self.ibcrb2 = self._io.read_u2le()
            self.ibcrb3 = self._io.read_u2le()
            self.ibcrb4 = self._io.read_u2le()
            self.ibcrb5 = self._io.read_u2le()
            self.ibcrb6 = self._io.read_u2le()
            self.ibcrb7 = self._io.read_u2le()
            self.ibcrb8 = self._io.read_u2le()
            self.ibcrb9 = self._io.read_u2le()
            self.tbcra1 = self._io.read_s2le()
            self.tbcra2 = self._io.read_s2le()
            self.tbcra3 = self._io.read_s2le()
            self.tbcra4 = self._io.read_s2le()
            self.tbcra5 = self._io.read_s2le()
            self.tbcra6 = self._io.read_s2le()
            self.tbcra7 = self._io.read_s2le()
            self.tbcra8 = self._io.read_s2le()
            self.tbcra9 = self._io.read_s2le()
            self.tbcrb1 = self._io.read_s2le()
            self.tbcrb2 = self._io.read_s2le()
            self.tbcrb3 = self._io.read_s2le()
            self.tbcrb4 = self._io.read_s2le()
            self.tbcrb5 = self._io.read_s2le()
            self.tbcrb6 = self._io.read_s2le()
            self.tbcrb7 = self._io.read_s2le()
            self.tbcrb8 = self._io.read_s2le()
            self.tbcrb9 = self._io.read_s2le()
            self.vidiodeout = self._io.read_u2le()
            self.iidiodeout = self._io.read_u2le()


    class SBandModemT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.battery_current = self._io.read_u2le()
            self.pa_current = self._io.read_u2le()
            self.battery_voltage = self._io.read_u2le()
            self.pa_voltage = self._io.read_u2le()
            self.pa_temperature = self._io.read_u2le()
            self.rf_output_power = self._io.read_u2le()
            self.board_temp_top = self._io.read_s2le()
            self.board_temp_bottom = self._io.read_s2le()


    class ObcT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.tlm_board_temp1 = self._io.read_s2le()
            self.tlm_board_temp2 = self._io.read_s2le()
            self.tlm_board_temp3 = self._io.read_s2le()
            self.tlm_vbat_v = self._io.read_u2le()
            self.tlm_vbat_i = self._io.read_u2le()
            self.tlm_vbat_plat_v = self._io.read_u2le()
            self.tlm_3v3_plat_v = self._io.read_u2le()
            self.tlm_vbat_periph_i = self._io.read_u2le()
            self.tlm_3v3_periph_i = self._io.read_u2le()
            self.tlm_vbat_periph_v = self._io.read_u2le()
            self.tlm_3v3_periph_v = self._io.read_u2le()


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
            self.callsign_ror = Sharjahsat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class TlmT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.system_info = Sharjahsat1.SystemInfoT(self._io, self, self._root)
            self.obc = Sharjahsat1.ObcT(self._io, self, self._root)
            self.interfacebrd_rtc = Sharjahsat1.InterfacebrdRtcT(self._io, self, self._root)
            self.battery = Sharjahsat1.BatteryT(self._io, self, self._root)
            self.eps = Sharjahsat1.EpsT(self._io, self, self._root)
            self.adcs = Sharjahsat1.AdcsT(self._io, self, self._root)
            self.uhf_vhf_modem = Sharjahsat1.UhfVhfModemT(self._io, self, self._root)
            self.s_band_modem = Sharjahsat1.SBandModemT(self._io, self, self._root)
            self.solar_panels = Sharjahsat1.SolarPanelsT(self._io, self, self._root)


    class BatteryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vbat = self._io.read_u2le()
            self.ibat = self._io.read_s2le()
            self.vpcm3v3 = self._io.read_u2le()
            self.vpcm5v = self._io.read_u2le()
            self.ipcm3v3 = self._io.read_u2le()
            self.ipcm5v = self._io.read_u2le()
            self.tbrd = self._io.read_s2le()
            self.tbat1 = self._io.read_s2le()
            self.tbat2 = self._io.read_s2le()
            self.tbat3 = self._io.read_s2le()



