# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Hype(KaitaiStruct):
    """:field service: service
    :field callsign: callsign
    :field counter: counter
    :field sat_mode: sat_mode
    :field vbus: vbus
    :field balance: balance
    :field charge: charge
    :field sat_temp: sat_temp
    :field sw_ver: sw_ver
    :field restart_counter: restart_counter
    :field uptime: uptime
    :field x_rate: x_rate
    :field y_rate: y_rate
    :field z_rate: z_rate
    :field sys_status: sys_status
    :field sys_status_dbm: sys_status_dbm
    :field sys_status_reserved: sys_status_reserved
    :field sys_status_software_slot_selected: sys_status_software_slot_selected
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.service = self._io.read_u1()
        self.callsign = (self._io.read_bytes(4)).decode(u"ASCII")
        if not self.callsign == u"HYPE":
            raise kaitaistruct.ValidationNotEqualError(u"HYPE", self.callsign, self._io, u"/seq/1")
        self.counter = self._io.read_u4be()
        self.sat_mode = self._io.read_u1()
        self.vbus = self._io.read_u2be()
        self.balance_raw = self._io.read_s2be()
        self.charge_raw = self._io.read_u2be()
        self.sat_temp = self._io.read_s2be()
        self.sw_ver = self._io.read_u2be()
        self.restart_counter = self._io.read_u4be()
        self.uptime = self._io.read_u4be()
        self.x_rate_raw = self._io.read_s2be()
        self.y_rate_raw = self._io.read_s2be()
        self.z_rate_raw = self._io.read_s2be()
        self.sys_status = self._io.read_u1()

    @property
    def sys_status_dbm(self):
        if hasattr(self, '_m_sys_status_dbm'):
            return self._m_sys_status_dbm

        self._m_sys_status_dbm = (self.sys_status & 63)
        return getattr(self, '_m_sys_status_dbm', None)

    @property
    def charge(self):
        if hasattr(self, '_m_charge'):
            return self._m_charge

        if self.sat_mode != 0:
            self._m_charge = self.charge_raw

        return getattr(self, '_m_charge', None)

    @property
    def z_rate(self):
        if hasattr(self, '_m_z_rate'):
            return self._m_z_rate

        if self.sat_mode != 0:
            self._m_z_rate = self.z_rate_raw

        return getattr(self, '_m_z_rate', None)

    @property
    def y_rate(self):
        if hasattr(self, '_m_y_rate'):
            return self._m_y_rate

        if self.sat_mode != 0:
            self._m_y_rate = self.y_rate_raw

        return getattr(self, '_m_y_rate', None)

    @property
    def sys_status_reserved(self):
        if hasattr(self, '_m_sys_status_reserved'):
            return self._m_sys_status_reserved

        self._m_sys_status_reserved = ((self.sys_status & 64) >> 6)
        return getattr(self, '_m_sys_status_reserved', None)

    @property
    def balance(self):
        if hasattr(self, '_m_balance'):
            return self._m_balance

        if self.sat_mode != 0:
            self._m_balance = self.balance_raw

        return getattr(self, '_m_balance', None)

    @property
    def sys_status_software_slot_selected(self):
        if hasattr(self, '_m_sys_status_software_slot_selected'):
            return self._m_sys_status_software_slot_selected

        self._m_sys_status_software_slot_selected = ((self.sys_status & 128) >> 7)
        return getattr(self, '_m_sys_status_software_slot_selected', None)

    @property
    def x_rate(self):
        if hasattr(self, '_m_x_rate'):
            return self._m_x_rate

        if self.sat_mode != 0:
            self._m_x_rate = self.x_rate_raw

        return getattr(self, '_m_x_rate', None)


