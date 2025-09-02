# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Hadesicm(KaitaiStruct):
    """:field type: cubesat_frame.first_header.type
    :field address: cubesat_frame.first_header.address
    :field sclock: cubesat_frame.metadata.sclock
    :field peaksignal: cubesat_frame.metadata.peaksignal
    :field modasignal: cubesat_frame.metadata.modasignal
    :field lastcmdsignal: cubesat_frame.metadata.lastcmdsignal
    :field lastcmdnoise: cubesat_frame.metadata.lastcmdnoise
    :field spi: cubesat_frame.metadata.spi
    :field spa: cubesat_frame.metadata.spa
    :field spb: cubesat_frame.metadata.spb
    :field spc: cubesat_frame.metadata.spc
    :field spd: cubesat_frame.metadata.spd
    :field vbus1: cubesat_frame.metadata.vbus1
    :field vbus2: cubesat_frame.metadata.vbus2
    :field vbus3: cubesat_frame.metadata.vbus3
    :field vbat1: cubesat_frame.metadata.vbat1
    :field vbat2: cubesat_frame.metadata.vbat2
    :field vbus1_vbat1: cubesat_frame.metadata.vbus1_vbat1
    :field vbus3_vbus2: cubesat_frame.metadata.vbus3_vbus2
    :field vcpu: cubesat_frame.metadata.vcpu
    :field icpu: cubesat_frame.metadata.icpu
    :field ipl: cubesat_frame.metadata.ipl
    :field ibat: cubesat_frame.metadata.ibat
    :field tpa: cubesat_frame.metadata.tpa
    :field tpb: cubesat_frame.metadata.tpb
    :field tpc: cubesat_frame.metadata.tpc
    :field tpd: cubesat_frame.metadata.tpd
    :field ttx: cubesat_frame.metadata.ttx
    :field ttx2: cubesat_frame.metadata.ttx2
    :field trx: cubesat_frame.metadata.trx
    :field tcpu: cubesat_frame.metadata.tcpu
    :field uptime: cubesat_frame.metadata.uptime
    :field nrun: cubesat_frame.metadata.nrun
    :field npayload: cubesat_frame.metadata.npayload
    :field nwire: cubesat_frame.metadata.nwire
    :field ntransponder: cubesat_frame.metadata.ntransponder
    :field ntasksnotexecuted: cubesat_frame.metadata.ntasksnotexecuted
    :field antennadeployed: cubesat_frame.metadata.antennadeployed
    :field nexteepromerrors: cubesat_frame.metadata.nexteepromerrors
    :field last_failed_task_id: cubesat_frame.metadata.last_failed_task_id
    :field messaging_enabled: cubesat_frame.metadata.messaging_enabled
    :field strfwd0_id: cubesat_frame.metadata.strfwd0_id
    :field strfwd1_key: cubesat_frame.metadata.strfwd1_key
    :field strfwd2_value: cubesat_frame.metadata.strfwd2_value
    :field strfwd3_num_tcmds: cubesat_frame.metadata.strfwd3_num_tcmds
    :field npayloadfails: cubesat_frame.metadata.npayloadfails
    :field last_reset_cause: cubesat_frame.metadata.last_reset_cause
    :field bate_battery: cubesat_frame.metadata.bate_battery
    :field mote_transponder: cubesat_frame.metadata.mote_transponder
    :field minicpu: cubesat_frame.metadata.minicpu
    :field minipl: cubesat_frame.metadata.minipl
    :field maxibat: cubesat_frame.metadata.maxibat
    :field maxicpu: cubesat_frame.metadata.maxicpu
    :field ibat_tx_off_charging: cubesat_frame.metadata.ibat_tx_off_charging
    :field ibat_tx_off_discharging: cubesat_frame.metadata.ibat_tx_off_discharging
    :field ibat_tx_low_power_charging: cubesat_frame.metadata.ibat_tx_low_power_charging
    :field ibat_tx_low_power_discharging: cubesat_frame.metadata.ibat_tx_low_power_discharging
    :field ibat_tx_high_power_charging: cubesat_frame.metadata.ibat_tx_high_power_charging
    :field ibat_tx_high_power_discharging: cubesat_frame.metadata.ibat_tx_high_power_discharging
    :field minvbus1: cubesat_frame.metadata.minvbus1
    :field minvbat1: cubesat_frame.metadata.minvbat1
    :field minvcpu: cubesat_frame.metadata.minvcpu
    :field minvbus2: cubesat_frame.metadata.minvbus2
    :field minvbus3: cubesat_frame.metadata.minvbus3
    :field minvbat2: cubesat_frame.metadata.minvbat2
    :field minibat: cubesat_frame.metadata.minibat
    :field maxvbus1: cubesat_frame.metadata.maxvbus1
    :field maxvbat1: cubesat_frame.metadata.maxvbat1
    :field maxvcpu: cubesat_frame.metadata.maxvcpu
    :field maxvbus2: cubesat_frame.metadata.maxvbus2
    :field maxvbus3: cubesat_frame.metadata.maxvbus3
    :field maxvbat2: cubesat_frame.metadata.maxvbat2
    :field maxipl: cubesat_frame.metadata.maxipl
    :field mintpa: cubesat_frame.metadata.mintpa
    :field mintpb: cubesat_frame.metadata.mintpb
    :field mintpc: cubesat_frame.metadata.mintpc
    :field mintpd: cubesat_frame.metadata.mintpd
    :field minttx: cubesat_frame.metadata.minttx
    :field minttx2: cubesat_frame.metadata.minttx2
    :field mintrx: cubesat_frame.metadata.mintrx
    :field mintcpu: cubesat_frame.metadata.mintcpu
    :field maxtpa: cubesat_frame.metadata.maxtpa
    :field maxtpb: cubesat_frame.metadata.maxtpb
    :field maxtpc: cubesat_frame.metadata.maxtpc
    :field maxtpd: cubesat_frame.metadata.maxtpd
    :field maxteps: cubesat_frame.metadata.maxteps
    :field maxttx: cubesat_frame.metadata.maxttx
    :field maxttx2: cubesat_frame.metadata.maxttx2
    :field maxtrx: cubesat_frame.metadata.maxtrx
    :field maxtcpu: cubesat_frame.metadata.maxtcpu
    :field vloc: cubesat_frame.metadata.vloc
    :field v1: cubesat_frame.metadata.v1
    :field i1: cubesat_frame.metadata.i1
    :field i1pk: cubesat_frame.metadata.i1pk
    :field r1: cubesat_frame.metadata.r1
    :field v2oc: cubesat_frame.metadata.v2oc
    :field v2: cubesat_frame.metadata.v2
    :field r2: cubesat_frame.metadata.r2
    :field t0: cubesat_frame.metadata.t0
    :field td: cubesat_frame.metadata.td
    :field state_begin: cubesat_frame.metadata.state_begin
    :field state_end: cubesat_frame.metadata.state_end
    :field state_now: cubesat_frame.metadata.state_now
    :field enable: cubesat_frame.metadata.enable
    :field counter: cubesat_frame.metadata.counter
    :field tmp: cubesat_frame.metadata.tmp
    :field v0: cubesat_frame.metadata.v0
    :field i0: cubesat_frame.metadata.i0
    :field p0: cubesat_frame.metadata.p0
    :field vp0: cubesat_frame.metadata.vp0
    :field ip0: cubesat_frame.metadata.ip0
    :field pp0: cubesat_frame.metadata.pp0
    :field p1: cubesat_frame.metadata.p1
    :field vp1: cubesat_frame.metadata.vp1
    :field ip1: cubesat_frame.metadata.ip1
    :field pp1: cubesat_frame.metadata.pp1
    :field i2: cubesat_frame.metadata.i2
    :field p2: cubesat_frame.metadata.p2
    :field vp2: cubesat_frame.metadata.vp2
    :field ip2: cubesat_frame.metadata.ip2
    :field pp2: cubesat_frame.metadata.pp2
    :field v3: cubesat_frame.metadata.v3
    :field i3: cubesat_frame.metadata.i3
    :field p3: cubesat_frame.metadata.p3
    :field vp3: cubesat_frame.metadata.vp3
    :field ip3: cubesat_frame.metadata.ip3
    :field pp3: cubesat_frame.metadata.pp3
    :field v4: cubesat_frame.metadata.v4
    :field i4: cubesat_frame.metadata.i4
    :field p4: cubesat_frame.metadata.p4
    :field vp4: cubesat_frame.metadata.vp4
    :field ip4: cubesat_frame.metadata.ip4
    :field pp4: cubesat_frame.metadata.pp4
    :field v5: cubesat_frame.metadata.v5
    :field i5: cubesat_frame.metadata.i5
    :field p5: cubesat_frame.metadata.p5
    :field vp5: cubesat_frame.metadata.vp5
    :field ip5: cubesat_frame.metadata.ip5
    :field pp5: cubesat_frame.metadata.pp5
    :field v6: cubesat_frame.metadata.v6
    :field i6: cubesat_frame.metadata.i6
    :field p6: cubesat_frame.metadata.p6
    :field vp6: cubesat_frame.metadata.vp6
    :field ip6: cubesat_frame.metadata.ip6
    :field pp6: cubesat_frame.metadata.pp6
    :field v7: cubesat_frame.metadata.v7
    :field i7: cubesat_frame.metadata.i7
    :field p7: cubesat_frame.metadata.p7
    :field vp7: cubesat_frame.metadata.vp7
    :field ip7: cubesat_frame.metadata.ip7
    :field pp7: cubesat_frame.metadata.pp7
    :field v8: cubesat_frame.metadata.v8
    :field i8: cubesat_frame.metadata.i8
    :field p8: cubesat_frame.metadata.p8
    :field vp8: cubesat_frame.metadata.vp8
    :field ip8: cubesat_frame.metadata.ip8
    :field pp8: cubesat_frame.metadata.pp8
    :field v9: cubesat_frame.metadata.v9
    :field i9: cubesat_frame.metadata.i9
    :field p9: cubesat_frame.metadata.p9
    :field vp9: cubesat_frame.metadata.vp9
    :field ip9: cubesat_frame.metadata.ip9
    :field pp9: cubesat_frame.metadata.pp9
    :field experiment_clock: cubesat_frame.metadata.experiment_clock
    :field experiment_id: cubesat_frame.metadata.experiment_id
    :field frame_number: cubesat_frame.metadata.frame_number
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.cubesat_frame = Hadesicm.CubesatFrame(self._io, self, self._root)

    class IcmgamemsgFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.msg_num = self._io.read_u1()
            self.message = (self._io.read_bytes_full()).decode(u"UTF-8")

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)


    class TimeseriesFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_value = self._io.read_bytes(0)


    class EphemerisFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time_utc = self._io.read_u4le()
            self.adr = self._io.read_u2le()
            self.ful = self._io.read_u4le()
            self.fdl = self._io.read_u4le()
            self.tle_epoch = self._io.read_u4le()
            self.tle_xndt2o = self._io.read_u4le()
            self.tle_xndd6o = self._io.read_u4le()
            self.tle_bstar = self._io.read_u4le()
            self.tle_xincl = self._io.read_u4le()
            self.tle_xnodeo = self._io.read_u4le()
            self.tle_eo = self._io.read_u4le()
            self.tle_omegao = self._io.read_u4le()
            self.tle_xmo = self._io.read_u4le()
            self.tle_xno = self._io.read_u4le()
            self.lat = self._io.read_u2le()
            self.lon = self._io.read_u2le()
            self.alt = self._io.read_u2le()
            self.cnt = self._io.read_u1()


    class PowerFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.spa_tmp = self._io.read_u1()
            self.spb_tmp = self._io.read_u1()
            self.spc_tmp = self._io.read_u1()
            self.spd_tmp = self._io.read_u1()
            self.spi_tmp = self._io.read_u2le()
            self.vbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.vbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.vcpuadc_lo_vbus2_tmp = self._io.read_u2le()
            self.vbus3_vbat2_hi_tmp = self._io.read_u2le()
            self.vbat2_lo_ibat_hi_tmp = self._io.read_u2le()
            self.ibat_lo_icpu_hi_tmp = self._io.read_u2le()
            self.icpu_lo_ipl_tmp = self._io.read_u2le()
            self.peaksignal = self._io.read_u1()
            self.modasignal = self._io.read_u1()
            self.lastcmdsignal = self._io.read_u1()
            self.lastcmdnoise = self._io.read_u1()

        @property
        def ibat(self):
            if hasattr(self, '_m_ibat'):
                return self._m_ibat

            self._m_ibat = (((((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)) - 4096) if (((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)) > 2047 else (((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)))
            return getattr(self, '_m_ibat', None)

        @property
        def spb(self):
            if hasattr(self, '_m_spb'):
                return self._m_spb

            self._m_spb = (self.spb_tmp << 1)
            return getattr(self, '_m_spb', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)

        @property
        def spa(self):
            if hasattr(self, '_m_spa'):
                return self._m_spa

            self._m_spa = (self.spa_tmp << 1)
            return getattr(self, '_m_spa', None)

        @property
        def spd(self):
            if hasattr(self, '_m_spd'):
                return self._m_spd

            self._m_spd = (self.spd_tmp << 1)
            return getattr(self, '_m_spd', None)

        @property
        def spc(self):
            if hasattr(self, '_m_spc'):
                return self._m_spc

            self._m_spc = (self.spc_tmp << 1)
            return getattr(self, '_m_spc', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def icpu(self):
            if hasattr(self, '_m_icpu'):
                return self._m_icpu

            self._m_icpu = (((self.ibat_lo_icpu_hi_tmp << 4) & 4080) | (self.icpu_lo_ipl_tmp >> 12))
            return getattr(self, '_m_icpu', None)

        @property
        def spi(self):
            if hasattr(self, '_m_spi'):
                return self._m_spi

            self._m_spi = (self.spi_tmp << 1)
            return getattr(self, '_m_spi', None)

        @property
        def ipl(self):
            if hasattr(self, '_m_ipl'):
                return self._m_ipl

            self._m_ipl = (self.icpu_lo_ipl_tmp & 4095)
            return getattr(self, '_m_ipl', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def vbat2(self):
            if hasattr(self, '_m_vbat2'):
                return self._m_vbat2

            self._m_vbat2 = ((((self.vbus3_vbat2_hi_tmp << 8) & 3840) | (self.vbat2_lo_ibat_hi_tmp >> 8)) * 4)
            return getattr(self, '_m_vbat2', None)

        @property
        def vbus3(self):
            if hasattr(self, '_m_vbus3'):
                return self._m_vbus3

            self._m_vbus3 = ((self.vbus3_vbat2_hi_tmp >> 4) * 4)
            return getattr(self, '_m_vbus3', None)

        @property
        def vcpu(self):
            if hasattr(self, '_m_vcpu'):
                return self._m_vcpu

            self._m_vcpu = (1210 * 4096) // (((self.vbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | (self.vcpuadc_lo_vbus2_tmp >> 12))
            return getattr(self, '_m_vcpu', None)

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)

        @property
        def vbat1(self):
            if hasattr(self, '_m_vbat1'):
                return self._m_vbat1

            self._m_vbat1 = ((((self.vbatadc_lo_vcpuadc_hi_tmp << 8) & 3840) | ((self.vbatadc_lo_vcpuadc_hi_tmp >> 8) & 4095)) * 1400) // 1000
            return getattr(self, '_m_vbat1', None)

        @property
        def vbus2(self):
            if hasattr(self, '_m_vbus2'):
                return self._m_vbus2

            self._m_vbus2 = ((self.vcpuadc_lo_vbus2_tmp & 4095) * 4)
            return getattr(self, '_m_vbus2', None)

        @property
        def vbus1_vbat1(self):
            if hasattr(self, '_m_vbus1_vbat1'):
                return self._m_vbus1_vbat1

            self._m_vbus1_vbat1 = (self.vbus1 - self.vbat1)
            return getattr(self, '_m_vbus1_vbat1', None)

        @property
        def vbus3_vbus2(self):
            if hasattr(self, '_m_vbus3_vbus2'):
                return self._m_vbus3_vbus2

            self._m_vbus3_vbus2 = (self.vbus3 - self.vbus2)
            return getattr(self, '_m_vbus3_vbus2', None)

        @property
        def vbus1(self):
            if hasattr(self, '_m_vbus1'):
                return self._m_vbus1

            self._m_vbus1 = ((self.vbusadc_vbatadc_hi_tmp >> 4) * 1400) // 1000
            return getattr(self, '_m_vbus1', None)


    class SunsensorsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_value = self._io.read_bytes(0)


    class StatusFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.uptime = self._io.read_u4le()
            self.nrun = self._io.read_u2le()
            self.npayload = self._io.read_u1()
            self.nwire = self._io.read_u1()
            self.ntransponder = self._io.read_u1()
            self.npayloadfails_lstrst_tmp = self._io.read_u1()
            self.bate_mote_tmp = self._io.read_u1()
            self.ntasksnotexecuted = self._io.read_u1()
            self.antennadeployed = self._io.read_u1()
            self.nexteepromerrors = self._io.read_u1()
            self.last_failed_task_id = self._io.read_u1()
            self.messaging_enabled = self._io.read_u1()
            self.strfwd0_id = self._io.read_u1()
            self.strfwd1_key = self._io.read_u2le()
            self.strfwd2_value = self._io.read_u2le()
            self.strfwd3_num_tcmds = self._io.read_u1()

        @property
        def npayloadfails(self):
            if hasattr(self, '_m_npayloadfails'):
                return self._m_npayloadfails

            self._m_npayloadfails = (self.npayloadfails_lstrst_tmp >> 4)
            return getattr(self, '_m_npayloadfails', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)

        @property
        def minutesup(self):
            if hasattr(self, '_m_minutesup'):
                return self._m_minutesup

            self._m_minutesup = (self.uptime % 3600) // 60
            return getattr(self, '_m_minutesup', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def hoursup(self):
            if hasattr(self, '_m_hoursup'):
                return self._m_hoursup

            self._m_hoursup = (self.uptime % 86400) // 3600
            return getattr(self, '_m_hoursup', None)

        @property
        def secondsup(self):
            if hasattr(self, '_m_secondsup'):
                return self._m_secondsup

            self._m_secondsup = (self.uptime % 60)
            return getattr(self, '_m_secondsup', None)

        @property
        def mote_transponder(self):
            if hasattr(self, '_m_mote_transponder'):
                return self._m_mote_transponder

            self._m_mote_transponder = (self.bate_mote_tmp & 15)
            return getattr(self, '_m_mote_transponder', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def daysup(self):
            if hasattr(self, '_m_daysup'):
                return self._m_daysup

            self._m_daysup = self.uptime // 86400
            return getattr(self, '_m_daysup', None)

        @property
        def bate_battery(self):
            if hasattr(self, '_m_bate_battery'):
                return self._m_bate_battery

            self._m_bate_battery = (self.bate_mote_tmp >> 4)
            return getattr(self, '_m_bate_battery', None)

        @property
        def last_reset_cause(self):
            if hasattr(self, '_m_last_reset_cause'):
                return self._m_last_reset_cause

            self._m_last_reset_cause = (self.npayloadfails_lstrst_tmp & 15)
            return getattr(self, '_m_last_reset_cause', None)

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)


    class FirstHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_bits_int_be(4)
            if not  ((self.type == 1) or (self.type == 2) or (self.type == 3) or (self.type == 4) or (self.type == 5) or (self.type == 6) or (self.type == 7) or (self.type == 8) or (self.type == 9) or (self.type == 10) or (self.type == 11) or (self.type == 12) or (self.type == 14) or (self.type == 15)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.type, self._io, u"/types/first_header/seq/0")
            self.address = self._io.read_bits_int_be(4)
            if not  ((self.address == 2)) :
                raise kaitaistruct.ValidationNotAnyOfError(self.address, self._io, u"/types/first_header/seq/1")


    class NebrijagameFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_value = self._io.read_bytes(0)


    class TempstatsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.mintpa_tmp = self._io.read_u1()
            self.mintpb_tmp = self._io.read_u1()
            self.mintpc_tmp = self._io.read_u1()
            self.mintpd_tmp = self._io.read_u1()
            self.mintpe = self._io.read_u1()
            self.minteps_tmp = self._io.read_u1()
            self.minttx_tmp = self._io.read_u1()
            self.minttx2_tmp = self._io.read_u1()
            self.mintrx_tmp = self._io.read_u1()
            self.mintcpu_tmp = self._io.read_u1()
            self.maxtpa_tmp = self._io.read_u1()
            self.maxtpb_tmp = self._io.read_u1()
            self.maxtpc_tmp = self._io.read_u1()
            self.maxtpd_tmp = self._io.read_u1()
            self.maxtpe = self._io.read_u1()
            self.maxteps_tmp = self._io.read_u1()
            self.maxttx_tmp = self._io.read_u1()
            self.maxttx2_tmp = self._io.read_u1()
            self.maxtrx_tmp = self._io.read_u1()
            self.maxtcpu_tmp = self._io.read_u1()

        @property
        def mintpc(self):
            if hasattr(self, '_m_mintpc'):
                return self._m_mintpc

            self._m_mintpc = ((self.mintpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpc', None)

        @property
        def maxttx(self):
            if hasattr(self, '_m_maxttx'):
                return self._m_maxttx

            self._m_maxttx = ((self.maxttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxttx', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)

        @property
        def mintpa(self):
            if hasattr(self, '_m_mintpa'):
                return self._m_mintpa

            self._m_mintpa = ((self.mintpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpa', None)

        @property
        def maxttx2(self):
            if hasattr(self, '_m_maxttx2'):
                return self._m_maxttx2

            self._m_maxttx2 = ((self.maxttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxttx2', None)

        @property
        def maxtpd(self):
            if hasattr(self, '_m_maxtpd'):
                return self._m_maxtpd

            self._m_maxtpd = ((self.maxtpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpd', None)

        @property
        def maxtcpu(self):
            if hasattr(self, '_m_maxtcpu'):
                return self._m_maxtcpu

            self._m_maxtcpu = ((self.maxtcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtcpu', None)

        @property
        def minteps(self):
            if hasattr(self, '_m_minteps'):
                return self._m_minteps

            self._m_minteps = ((self.minteps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minteps', None)

        @property
        def maxtpc(self):
            if hasattr(self, '_m_maxtpc'):
                return self._m_maxtpc

            self._m_maxtpc = ((self.maxtpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpc', None)

        @property
        def mintcpu(self):
            if hasattr(self, '_m_mintcpu'):
                return self._m_mintcpu

            self._m_mintcpu = ((self.mintcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintcpu', None)

        @property
        def minttx(self):
            if hasattr(self, '_m_minttx'):
                return self._m_minttx

            self._m_minttx = ((self.minttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minttx', None)

        @property
        def maxteps(self):
            if hasattr(self, '_m_maxteps'):
                return self._m_maxteps

            self._m_maxteps = ((self.maxteps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxteps', None)

        @property
        def maxtpb(self):
            if hasattr(self, '_m_maxtpb'):
                return self._m_maxtpb

            self._m_maxtpb = ((self.maxtpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpb', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def mintpd(self):
            if hasattr(self, '_m_mintpd'):
                return self._m_mintpd

            self._m_mintpd = ((self.mintpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpd', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def mintrx(self):
            if hasattr(self, '_m_mintrx'):
                return self._m_mintrx

            self._m_mintrx = ((self.mintrx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintrx', None)

        @property
        def minttx2(self):
            if hasattr(self, '_m_minttx2'):
                return self._m_minttx2

            self._m_minttx2 = ((self.minttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minttx2', None)

        @property
        def maxtrx(self):
            if hasattr(self, '_m_maxtrx'):
                return self._m_maxtrx

            self._m_maxtrx = ((self.maxtrx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtrx', None)

        @property
        def mintpb(self):
            if hasattr(self, '_m_mintpb'):
                return self._m_mintpb

            self._m_mintpb = ((self.mintpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpb', None)

        @property
        def maxtpa(self):
            if hasattr(self, '_m_maxtpa'):
                return self._m_maxtpa

            self._m_maxtpa = ((self.maxtpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpa', None)

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)


    class ExtpowerstatsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.v0 = self._io.read_u2le()
            self.i0 = self._io.read_u2le()
            self.p0 = self._io.read_u2le()
            self.vp0 = self._io.read_u2le()
            self.ip0 = self._io.read_u2le()
            self.pp0 = self._io.read_u2le()
            self.v1 = self._io.read_u2le()
            self.i1 = self._io.read_u2le()
            self.p1 = self._io.read_u2le()
            self.vp1 = self._io.read_u2le()
            self.ip1 = self._io.read_u2le()
            self.pp1 = self._io.read_u2le()
            self.v2 = self._io.read_u2le()
            self.i2 = self._io.read_u2le()
            self.p2 = self._io.read_u2le()
            self.vp2 = self._io.read_u2le()
            self.ip2 = self._io.read_u2le()
            self.pp2 = self._io.read_u2le()
            self.v3 = self._io.read_u2le()
            self.i3 = self._io.read_u2le()
            self.p3 = self._io.read_u2le()
            self.vp3 = self._io.read_u2le()
            self.ip3 = self._io.read_u2le()
            self.pp3 = self._io.read_u2le()
            self.v4 = self._io.read_u2le()
            self.i4 = self._io.read_u2le()
            self.p4 = self._io.read_u2le()
            self.vp4 = self._io.read_u2le()
            self.ip4 = self._io.read_u2le()
            self.pp4 = self._io.read_u2le()
            self.v5 = self._io.read_u2le()
            self.i5 = self._io.read_u2le()
            self.p5 = self._io.read_u2le()
            self.vp5 = self._io.read_u2le()
            self.ip5 = self._io.read_u2le()
            self.pp5 = self._io.read_u2le()
            self.v6 = self._io.read_u2le()
            self.i6 = self._io.read_u2le()
            self.p6 = self._io.read_u2le()
            self.vp6 = self._io.read_u2le()
            self.ip6 = self._io.read_u2le()
            self.pp6 = self._io.read_u2le()
            self.v7 = self._io.read_u2le()
            self.i7 = self._io.read_u2le()
            self.p7 = self._io.read_u2le()
            self.vp7 = self._io.read_u2le()
            self.ip7 = self._io.read_u2le()
            self.pp7 = self._io.read_u2le()
            self.v8 = self._io.read_u2le()
            self.i8 = self._io.read_u2le()
            self.p8 = self._io.read_u2le()
            self.vp8 = self._io.read_u2le()
            self.ip8 = self._io.read_u2le()
            self.pp8 = self._io.read_u2le()
            self.v9 = self._io.read_u2le()
            self.i9 = self._io.read_u2le()
            self.p9 = self._io.read_u2le()
            self.vp9 = self._io.read_u2le()
            self.ip9 = self._io.read_u2le()
            self.pp9 = self._io.read_u2le()


    class PowerstatsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.minvbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.minvbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.minvcpuadc_lo_free_tmp = self._io.read_u1()
            self.minvbus2_tmp = self._io.read_u1()
            self.minvbus3_tmp = self._io.read_u1()
            self.minvbat2_tmp = self._io.read_u1()
            self.minibat_tmp = self._io.read_u1()
            self.minicpu = self._io.read_u1()
            self.minipl = self._io.read_u1()
            self.maxvbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.maxvbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.maxvcpuadc_lo_free_tmp = self._io.read_u1()
            self.maxvbus2_tmp = self._io.read_u1()
            self.maxvbus3_tmp = self._io.read_u1()
            self.maxvbat2_tmp = self._io.read_u1()
            self.maxibat = self._io.read_u1()
            self.maxicpu = self._io.read_u1()
            self.maxipl_tmp = self._io.read_u1()
            self.ibat_tx_off_charging = self._io.read_u1()
            self.ibat_tx_off_discharging = self._io.read_u1()
            self.ibat_tx_low_power_charging = self._io.read_u1()
            self.ibat_tx_low_power_discharging = self._io.read_u1()
            self.ibat_tx_high_power_charging = self._io.read_u1()
            self.ibat_tx_high_power_discharging = self._io.read_u1()

        @property
        def minvbus2(self):
            if hasattr(self, '_m_minvbus2'):
                return self._m_minvbus2

            self._m_minvbus2 = ((self.minvbus2_tmp * 16) * 4)
            return getattr(self, '_m_minvbus2', None)

        @property
        def minvbus3(self):
            if hasattr(self, '_m_minvbus3'):
                return self._m_minvbus3

            self._m_minvbus3 = ((self.minvbus3_tmp * 16) * 4)
            return getattr(self, '_m_minvbus3', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)

        @property
        def maxvbat2(self):
            if hasattr(self, '_m_maxvbat2'):
                return self._m_maxvbat2

            self._m_maxvbat2 = ((self.maxvbat2_tmp * 16) * 4)
            return getattr(self, '_m_maxvbat2', None)

        @property
        def maxvcpu(self):
            if hasattr(self, '_m_maxvcpu'):
                return self._m_maxvcpu

            self._m_maxvcpu = (1210 * 4096) // (((self.maxvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | (self.maxvcpuadc_lo_free_tmp >> 4))
            return getattr(self, '_m_maxvcpu', None)

        @property
        def maxvbus1(self):
            if hasattr(self, '_m_maxvbus1'):
                return self._m_maxvbus1

            self._m_maxvbus1 = (1400 * (self.maxvbusadc_vbatadc_hi_tmp >> 4)) // 1000
            return getattr(self, '_m_maxvbus1', None)

        @property
        def maxvbat1(self):
            if hasattr(self, '_m_maxvbat1'):
                return self._m_maxvbat1

            self._m_maxvbat1 = (1400 * (((self.maxvbusadc_vbatadc_hi_tmp << 8) & 3840) | ((self.maxvbatadc_lo_vcpuadc_hi_tmp >> 8) & 255))) // 1000
            return getattr(self, '_m_maxvbat1', None)

        @property
        def maxvbus3(self):
            if hasattr(self, '_m_maxvbus3'):
                return self._m_maxvbus3

            self._m_maxvbus3 = ((self.maxvbus3_tmp * 16) * 4)
            return getattr(self, '_m_maxvbus3', None)

        @property
        def maxipl(self):
            if hasattr(self, '_m_maxipl'):
                return self._m_maxipl

            self._m_maxipl = (self.maxipl_tmp << 2)
            return getattr(self, '_m_maxipl', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def maxvbus2(self):
            if hasattr(self, '_m_maxvbus2'):
                return self._m_maxvbus2

            self._m_maxvbus2 = ((self.maxvbus2_tmp * 16) * 4)
            return getattr(self, '_m_maxvbus2', None)

        @property
        def minvbat1(self):
            if hasattr(self, '_m_minvbat1'):
                return self._m_minvbat1

            self._m_minvbat1 = (1400 * (((self.minvbusadc_vbatadc_hi_tmp << 8) & 3840) | ((self.minvbatadc_lo_vcpuadc_hi_tmp >> 8) & 255))) // 1000
            return getattr(self, '_m_minvbat1', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def minibat(self):
            if hasattr(self, '_m_minibat'):
                return self._m_minibat

            self._m_minibat = (self.minibat_tmp * -1)
            return getattr(self, '_m_minibat', None)

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)

        @property
        def minvbus1(self):
            if hasattr(self, '_m_minvbus1'):
                return self._m_minvbus1

            self._m_minvbus1 = (1400 * (self.minvbusadc_vbatadc_hi_tmp >> 4)) // 1000
            return getattr(self, '_m_minvbus1', None)

        @property
        def minvcpu(self):
            if hasattr(self, '_m_minvcpu'):
                return self._m_minvcpu

            self._m_minvcpu = (1210 * 4096) // (((self.minvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | (self.minvcpuadc_lo_free_tmp >> 4))
            return getattr(self, '_m_minvcpu', None)

        @property
        def minvbat2(self):
            if hasattr(self, '_m_minvbat2'):
                return self._m_minvbat2

            self._m_minvbat2 = ((self.minvbat2_tmp * 16) * 4)
            return getattr(self, '_m_minvbat2', None)


    class FraunhoferexpFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.no_value = self._io.read_bytes(0)


    class TempFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock = self._io.read_u4le()
            self.tpa_tmp = self._io.read_u1()
            self.tpb_tmp = self._io.read_u1()
            self.tpc_tmp = self._io.read_u1()
            self.tpd_tmp = self._io.read_u1()
            self.tpe_tmp = self._io.read_u1()
            self.teps_tmp = self._io.read_u1()
            self.ttx_tmp = self._io.read_u1()
            self.ttx2_tmp = self._io.read_u1()
            self.trx_tmp = self._io.read_u1()
            self.tcpu_tmp = self._io.read_u1()

        @property
        def teps(self):
            if hasattr(self, '_m_teps'):
                return self._m_teps

            self._m_teps = ((self.teps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_teps', None)

        @property
        def seconds(self):
            if hasattr(self, '_m_seconds'):
                return self._m_seconds

            self._m_seconds = (self.sclock % 60)
            return getattr(self, '_m_seconds', None)

        @property
        def tpb(self):
            if hasattr(self, '_m_tpb'):
                return self._m_tpb

            self._m_tpb = ((self.tpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpb', None)

        @property
        def trx(self):
            if hasattr(self, '_m_trx'):
                return self._m_trx

            self._m_trx = ((self.trx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_trx', None)

        @property
        def minutes(self):
            if hasattr(self, '_m_minutes'):
                return self._m_minutes

            self._m_minutes = (self.sclock % 3600) // 60
            return getattr(self, '_m_minutes', None)

        @property
        def hours(self):
            if hasattr(self, '_m_hours'):
                return self._m_hours

            self._m_hours = (self.sclock % 86400) // 3600
            return getattr(self, '_m_hours', None)

        @property
        def ttx(self):
            if hasattr(self, '_m_ttx'):
                return self._m_ttx

            self._m_ttx = ((self.ttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_ttx', None)

        @property
        def tpd(self):
            if hasattr(self, '_m_tpd'):
                return self._m_tpd

            self._m_tpd = ((self.tpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpd', None)

        @property
        def tpa(self):
            if hasattr(self, '_m_tpa'):
                return self._m_tpa

            self._m_tpa = ((self.tpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpa', None)

        @property
        def tcpu(self):
            if hasattr(self, '_m_tcpu'):
                return self._m_tcpu

            self._m_tcpu = ((self.tcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tcpu', None)

        @property
        def days(self):
            if hasattr(self, '_m_days'):
                return self._m_days

            self._m_days = self.sclock // 86400
            return getattr(self, '_m_days', None)

        @property
        def ttx2(self):
            if hasattr(self, '_m_ttx2'):
                return self._m_ttx2

            self._m_ttx2 = ((self.ttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_ttx2', None)

        @property
        def tpc(self):
            if hasattr(self, '_m_tpc'):
                return self._m_tpc

            self._m_tpc = ((self.tpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpc', None)


    class ExperimentFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.experiment_clock = self._io.read_u4le()
            self.experiment_id = self._io.read_u1()
            self.frame_number = self._io.read_u1()
            self.experiment_data = self._io.read_bytes_full()


    class DeployFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vloc = self._io.read_u2le()
            self.v1 = self._io.read_u2le()
            self.i1 = self._io.read_u2le()
            self.i1pk = self._io.read_u2le()
            self.r1 = self._io.read_u2le()
            self.v2oc = self._io.read_u2le()
            self.v2 = self._io.read_u2le()
            self.r2 = self._io.read_u2le()
            self.t0 = self._io.read_u4le()
            self.td = self._io.read_u2le()
            self.state_begin = self._io.read_u1()
            self.state_end = self._io.read_u1()
            self.state_now = self._io.read_u1()
            self.enable = self._io.read_u1()
            self.counter = self._io.read_u1()
            self.tmp = self._io.read_u1()


    class CubesatFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_header = Hadesicm.FirstHeader(self._io, self, self._root)
            _on = self.first_header.type
            if _on == 14:
                self.metadata = Hadesicm.TimeseriesFrame(self._io, self, self._root)
            elif _on == 10:
                self.metadata = Hadesicm.NebrijagameFrame(self._io, self, self._root)
            elif _on == 4:
                self.metadata = Hadesicm.PowerstatsFrame(self._io, self, self._root)
            elif _on == 6:
                self.metadata = Hadesicm.SunsensorsFrame(self._io, self, self._root)
            elif _on == 7:
                self.metadata = Hadesicm.IcmgamemsgFrame(self._io, self, self._root)
            elif _on == 1:
                self.metadata = Hadesicm.PowerFrame(self._io, self, self._root)
            elif _on == 11:
                self.metadata = Hadesicm.FraunhoferexpFrame(self._io, self, self._root)
            elif _on == 12:
                self.metadata = Hadesicm.EphemerisFrame(self._io, self, self._root)
            elif _on == 3:
                self.metadata = Hadesicm.StatusFrame(self._io, self, self._root)
            elif _on == 5:
                self.metadata = Hadesicm.TempstatsFrame(self._io, self, self._root)
            elif _on == 15:
                self.metadata = Hadesicm.ExperimentFrame(self._io, self, self._root)
            elif _on == 8:
                self.metadata = Hadesicm.DeployFrame(self._io, self, self._root)
            elif _on == 9:
                self.metadata = Hadesicm.ExtpowerstatsFrame(self._io, self, self._root)
            elif _on == 2:
                self.metadata = Hadesicm.TempFrame(self._io, self, self._root)



