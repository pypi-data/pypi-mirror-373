# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Co65(KaitaiStruct):
    """:field v3_3: v3_3
    :field v5: v5
    :field v_batt: v_batt
    :field v_batt_main_bus: v_batt_main_bus
    :field digipeater_mode: digipeater_mode
    :field dtmf_permission: dtmf_permission
    :field antenna_deployment: antenna_deployment
    :field tx_mutual_monitor: tx_mutual_monitor
    :field rx_mutual_monitor: rx_mutual_monitor
    :field usb_enable: usb_enable
    :field satellite_mode: satellite_mode
    :field temp_com_board: temp_com_board
    :field temp_batt: temp_batt
    :field i_batt: i_batt
    :field s_meter_144: s_meter_144
    :field s_meter_1200: s_meter_1200
    :field power_dj_c5_tx: power_dj_c5_tx
    :field power_cw_430_beacon: power_cw_430_beacon
    :field power_th_59_1200_uplink: power_th_59_1200_uplink
    :field power_pda: power_pda
    :field power_daq: power_daq
    :field power_apd_main: power_apd_main
    :field power_apd_3_3b: power_apd_3_3b
    :field power_apd_3_3a: power_apd_3_3a
    
    .. seealso::
       Source - https://web.archive.org/web/20210928003812/http://lss.mes.titech.ac.jp/ssp/cute1.7/cwtelemetry_e.html
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.callsign = (self._io.read_bytes(4)).decode(u"ASCII")
        if not  ((self.callsign == u"CUTE") or (self.callsign == u"cute")) :
            raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/seq/0")
        self.v3_3_raw = self._io.read_u1()
        self.v5_raw = self._io.read_u1()
        self.v_batt_raw = self._io.read_u1()
        self.v_batt_main_bus_raw = self._io.read_u1()
        self.sat_status = self._io.read_u1()
        self.temp_com_board_raw = self._io.read_u1()
        self.temp_batt_raw = self._io.read_u1()
        self.i_batt_raw = self._io.read_u1()
        self.s_meter_144_raw = self._io.read_u1()
        self.s_meter_1200_raw = self._io.read_u1()
        self.fet_status = self._io.read_u1()

    @property
    def power_cw_430_beacon(self):
        if hasattr(self, '_m_power_cw_430_beacon'):
            return self._m_power_cw_430_beacon

        self._m_power_cw_430_beacon = ((self.fet_status & 2) >> 1)
        return getattr(self, '_m_power_cw_430_beacon', None)

    @property
    def power_apd_3_3b(self):
        if hasattr(self, '_m_power_apd_3_3b'):
            return self._m_power_apd_3_3b

        self._m_power_apd_3_3b = ((self.fet_status & 64) >> 6)
        return getattr(self, '_m_power_apd_3_3b', None)

    @property
    def v3_3(self):
        if hasattr(self, '_m_v3_3'):
            return self._m_v3_3

        self._m_v3_3 = ((self.v3_3_raw * 6.16) / 255)
        return getattr(self, '_m_v3_3', None)

    @property
    def power_apd_3_3a(self):
        if hasattr(self, '_m_power_apd_3_3a'):
            return self._m_power_apd_3_3a

        self._m_power_apd_3_3a = ((self.fet_status & 128) >> 7)
        return getattr(self, '_m_power_apd_3_3a', None)

    @property
    def tx_mutual_monitor(self):
        if hasattr(self, '_m_tx_mutual_monitor'):
            return self._m_tx_mutual_monitor

        self._m_tx_mutual_monitor = ((self.sat_status & 16) >> 4)
        return getattr(self, '_m_tx_mutual_monitor', None)

    @property
    def s_meter_144(self):
        if hasattr(self, '_m_s_meter_144'):
            return self._m_s_meter_144

        self._m_s_meter_144 = (((202.972 * self.s_meter_144_raw) / 255) - 171.5)
        return getattr(self, '_m_s_meter_144', None)

    @property
    def power_pda(self):
        if hasattr(self, '_m_power_pda'):
            return self._m_power_pda

        self._m_power_pda = ((self.fet_status & 8) >> 3)
        return getattr(self, '_m_power_pda', None)

    @property
    def v_batt_main_bus(self):
        if hasattr(self, '_m_v_batt_main_bus'):
            return self._m_v_batt_main_bus

        self._m_v_batt_main_bus = ((self.v_batt_main_bus_raw * 9.24) / 255)
        return getattr(self, '_m_v_batt_main_bus', None)

    @property
    def s_meter_1200(self):
        if hasattr(self, '_m_s_meter_1200'):
            return self._m_s_meter_1200

        self._m_s_meter_1200 = (((54.824 * self.s_meter_1200_raw) / 255) - 151.9)
        return getattr(self, '_m_s_meter_1200', None)

    @property
    def power_daq(self):
        if hasattr(self, '_m_power_daq'):
            return self._m_power_daq

        self._m_power_daq = ((self.fet_status & 16) >> 4)
        return getattr(self, '_m_power_daq', None)

    @property
    def temp_com_board(self):
        if hasattr(self, '_m_temp_com_board'):
            return self._m_temp_com_board

        self._m_temp_com_board = ((((3.08 * self.temp_com_board_raw) / 255) - 0.424) / 0.00625)
        return getattr(self, '_m_temp_com_board', None)

    @property
    def power_apd_main(self):
        if hasattr(self, '_m_power_apd_main'):
            return self._m_power_apd_main

        self._m_power_apd_main = ((self.fet_status & 32) >> 5)
        return getattr(self, '_m_power_apd_main', None)

    @property
    def temp_batt(self):
        if hasattr(self, '_m_temp_batt'):
            return self._m_temp_batt

        self._m_temp_batt = ((((3.08 * self.temp_batt_raw) / 255) - 0.424) / 0.00625)
        return getattr(self, '_m_temp_batt', None)

    @property
    def power_th_59_1200_uplink(self):
        if hasattr(self, '_m_power_th_59_1200_uplink'):
            return self._m_power_th_59_1200_uplink

        self._m_power_th_59_1200_uplink = ((self.fet_status & 4) >> 2)
        return getattr(self, '_m_power_th_59_1200_uplink', None)

    @property
    def rx_mutual_monitor(self):
        if hasattr(self, '_m_rx_mutual_monitor'):
            return self._m_rx_mutual_monitor

        self._m_rx_mutual_monitor = ((self.sat_status & 32) >> 5)
        return getattr(self, '_m_rx_mutual_monitor', None)

    @property
    def antenna_deployment(self):
        if hasattr(self, '_m_antenna_deployment'):
            return self._m_antenna_deployment

        self._m_antenna_deployment = ((self.sat_status & 8) >> 3)
        return getattr(self, '_m_antenna_deployment', None)

    @property
    def satellite_mode(self):
        if hasattr(self, '_m_satellite_mode'):
            return self._m_satellite_mode

        self._m_satellite_mode = ((self.sat_status & 128) >> 7)
        return getattr(self, '_m_satellite_mode', None)

    @property
    def i_batt(self):
        if hasattr(self, '_m_i_batt'):
            return self._m_i_batt

        self._m_i_batt = (((-3.08924 * self.i_batt_raw) / 255) + 1.486)
        return getattr(self, '_m_i_batt', None)

    @property
    def usb_enable(self):
        if hasattr(self, '_m_usb_enable'):
            return self._m_usb_enable

        self._m_usb_enable = ((self.sat_status & 64) >> 6)
        return getattr(self, '_m_usb_enable', None)

    @property
    def dtmf_permission(self):
        if hasattr(self, '_m_dtmf_permission'):
            return self._m_dtmf_permission

        self._m_dtmf_permission = ((self.sat_status & 4) >> 2)
        return getattr(self, '_m_dtmf_permission', None)

    @property
    def digipeater_mode(self):
        if hasattr(self, '_m_digipeater_mode'):
            return self._m_digipeater_mode

        self._m_digipeater_mode = (self.sat_status & 3)
        return getattr(self, '_m_digipeater_mode', None)

    @property
    def v5(self):
        if hasattr(self, '_m_v5'):
            return self._m_v5

        self._m_v5 = ((self.v5_raw * 6.16) / 255)
        return getattr(self, '_m_v5', None)

    @property
    def v_batt(self):
        if hasattr(self, '_m_v_batt'):
            return self._m_v_batt

        self._m_v_batt = ((self.v_batt_raw * 6.16) / 255)
        return getattr(self, '_m_v_batt', None)

    @property
    def power_dj_c5_tx(self):
        if hasattr(self, '_m_power_dj_c5_tx'):
            return self._m_power_dj_c5_tx

        self._m_power_dj_c5_tx = (self.fet_status & 1)
        return getattr(self, '_m_power_dj_c5_tx', None)


