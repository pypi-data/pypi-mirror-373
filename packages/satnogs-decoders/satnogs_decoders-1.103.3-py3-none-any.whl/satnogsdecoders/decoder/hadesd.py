# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Hadesd(KaitaiStruct):
    """# General
    :field hadesd_type: cubesat_frame.first_header.type
    :field hadesd_address: cubesat_frame.first_header.address
    # Type1 Frame (Power):
    :field hadesd_power_spa_tmp: cubesat_frame.metadata.spa_tmp
    :field hadesd_power_spb_tmp: cubesat_frame.metadata.spb_tmp
    :field hadesd_power_spc_tmp: cubesat_frame.metadata.spc_tmp
    :field hadesd_power_spd_tmp: cubesat_frame.metadata.spd_tmp
    :field hadesd_power_spe_tmp: cubesat_frame.metadata.spe_tmp
    :field hadesd_power_spf_tmp: cubesat_frame.metadata.spf_tmp
    :field hadesd_power_vbusadc_vbatadc_hi_tmp: cubesat_frame.metadata.vbusadc_vbatadc_hi_tmp
    :field hadesd_power_vbatadc_lo_vcpuadc_hi_tmp: cubesat_frame.metadata.vbatadc_lo_vcpuadc_hi_tmp
    :field hadesd_power_vcpuadc_lo_vbus2_tmp: cubesat_frame.metadata.vcpuadc_lo_vbus2_tmp
    :field hadesd_power_vbus3_vbat2_hi_tmp: cubesat_frame.metadata.vbus3_vbat2_hi_tmp
    :field hadesd_power_vbat2_lo_ibat_hi_tmp: cubesat_frame.metadata.vbat2_lo_ibat_hi_tmp
    :field hadesd_power_ibat_lo_icpu_hi_tmp: cubesat_frame.metadata.ibat_lo_icpu_hi_tmp
    :field hadesd_power_icpu_lo_ipl_tmp: cubesat_frame.metadata.icpu_lo_ipl_tmp
    :field hadesd_power_powerdul_tmp: cubesat_frame.metadata.powerdul_tmp
    :field hadesd_power_powerdul455_tmp: cubesat_frame.metadata.powerdul455_tmp
    :field hadesd_power_vdac_tmp: cubesat_frame.metadata.vdac_tmp
    :field hadesd_power_spa_dec: cubesat_frame.metadata.spa_dec
    :field hadesd_power_spb_dec: cubesat_frame.metadata.spb_dec
    :field hadesd_power_spc_dec: cubesat_frame.metadata.spc_dec
    :field hadesd_power_spd_dec: cubesat_frame.metadata.spd_dec
    :field hadesd_power_vbus1_dec: cubesat_frame.metadata.vbus1_dec
    :field hadesd_power_vbus2_dec: cubesat_frame.metadata.vbus2_dec
    :field hadesd_power_vbus3_dec: cubesat_frame.metadata.vbus3_dec
    :field hadesd_power_vbat1_dec: cubesat_frame.metadata.vbat1_dec
    :field hadesd_power_vbat2_dec: cubesat_frame.metadata.vbat2_dec
    :field hadesd_power_vbus1_vbat1_dec: cubesat_frame.metadata.vbus1_vbat1_dec
    :field hadesd_power_vbus3_vbus2_dec: cubesat_frame.metadata.vbus3_vbus2_dec
    :field hadesd_power_vcpu_dec: cubesat_frame.metadata.vcpu_dec
    :field hadesd_power_icpu_dec: cubesat_frame.metadata.icpu_dec
    :field hadesd_power_ipl_dec: cubesat_frame.metadata.ipl_dec 
    :field hadesd_power_ibat_dec: cubesat_frame.metadata.ibat_dec
    :field hadesd_power_pwrdul1_dec: cubesat_frame.metadata.pwrdul1_dec
    :field hadesd_power_pwrdul4_dec: cubesat_frame.metadata.pwrdul4_dec
    # Type2 Frame (Temp):
    :field hadesd_temp_tpa_tmp: cubesat_frame.metadata.tpa_tmp
    :field hadesd_temp_tpb_tmp: cubesat_frame.metadata.tpb_tmp
    :field hadesd_temp_tpc_tmp: cubesat_frame.metadata.tpc_tmp
    :field hadesd_temp_tpd_tmp: cubesat_frame.metadata.tpd_tmp
    :field hadesd_temp_tpe_tmp: cubesat_frame.metadata.tpe_tmp
    :field hadesd_temp_teps_tmp: cubesat_frame.metadata.teps_tmp
    :field hadesd_temp_ttx_tmp: cubesat_frame.metadata.ttx_tmp
    :field hadesd_temp_ttx2_tmp: cubesat_frame.metadata.ttx2_tmp
    :field hadesd_temp_trx_tmp: cubesat_frame.metadata.trx_tmp
    :field hadesd_temp_tcpu_tmp: cubesat_frame.metadata.tcpu_tmp
    :field hadesd_temp_tpa_dec: cubesat_frame.metadata.tpa_dec
    :field hadesd_temp_tpb_dec: cubesat_frame.metadata.tpb_dec
    :field hadesd_temp_tpc_dec: cubesat_frame.metadata.tpc_dec
    :field hadesd_temp_tpd_dec: cubesat_frame.metadata.tpd_dec
    :field hadesd_temp_teps_dec: cubesat_frame.metadata.teps_dec
    :field hadesd_temp_ttx_dec: cubesat_frame.metadata.ttx_dec
    :field hadesd_temp_ttx2_dec: cubesat_frame.metadata.ttx2_dec
    :field hadesd_temp_trx_dec: cubesat_frame.metadata.trx_dec
    :field hadesd_temp_tcpu_dec: cubesat_frame.metadata.tcpu_dec
    # Type3 Frame (Status):
    :field hadesd_status_sclock_dec: cubesat_frame.metadata.sclock_dec
    :field hadesd_status_uptime_dec: cubesat_frame.metadata.uptime_dec
    :field hadesd_status_nrun_dec: cubesat_frame.metadata.nrun_dec
    :field hadesd_status_npayload_dec: cubesat_frame.metadata.npayload_dec
    :field hadesd_status_nwire_dec: cubesat_frame.metadata.nwire_dec
    :field hadesd_status_nbusdrops_lastreset_tmp: cubesat_frame.metadata.nbusdrops_lastreset_tmp
    :field hadesd_status_bate_mote_tmp: cubesat_frame.metadata.bate_mote_tmp
    :field hadesd_status_ntasksnotexecuted_dec: cubesat_frame.metadata.ntasksnotexecuted_dec
    :field hadesd_status_antennadeployed_dec: cubesat_frame.metadata.antennadeployed_dec
    :field hadesd_status_nexteepromerrors_dec: cubesat_frame.metadata.nexteepromerrors_dec
    :field hadesd_status_failed_task_id_dec: cubesat_frame.metadata.failed_task_id_dec
    :field hadesd_status_orbperiod_dec: cubesat_frame.metadata.orbperiod_dec
    :field hadesd_status_strfwd0_dec: cubesat_frame.metadata.strfwd0_dec
    :field hadesd_status_strfwd1_dec: cubesat_frame.metadata.strfwd1_dec
    :field hadesd_status_strfwd2_dec: cubesat_frame.metadata.strfwd2_dec
    :field hadesd_status_strfwd3_dec: cubesat_frame.metadata.strfwd3_dec
    :field hadesd_status_nbusdrops_dec: cubesat_frame.metadata.nbusdrops_dec
    :field hadesd_status_ntrans_dec: cubesat_frame.metadata.ntrans_dec
    :field hadesd_status_last_reset_cause_dec: cubesat_frame.metadata.last_reset_cause_dec
    :field hadesd_status_battery_dec: cubesat_frame.metadata.battery_dec
    :field hadesd_status_transponder_dec: cubesat_frame.metadata.transponder_dec
    # Type4 Frame (PowerStats):
    :field hadesd_powerstats_minvbusadc_vbatadc_hi_tmp: cubesat_frame.metadata.minvbusadc_vbatadc_hi_tmp
    :field hadesd_powerstats_minvbatadc_lo_vcpuadc_hi_tmp: cubesat_frame.metadata.minvbatadc_lo_vcpuadc_hi_tmp
    :field hadesd_powerstats_minvcpuadc_lo_free_tmp: cubesat_frame.metadata.minvcpuadc_lo_free_tmp
    :field hadesd_powerstats_minvbus2_tmp: cubesat_frame.metadata.minvbus2_tmp
    :field hadesd_powerstats_minvbus3_tmp: cubesat_frame.metadata.minvbus3_tmp
    :field hadesd_powerstats_minvbat2_tmp: cubesat_frame.metadata.minvbat2_tmp
    :field hadesd_powerstats_minibat_tmp: cubesat_frame.metadata.minibat_tmp
    :field hadesd_powerstats_minicpu_dec: cubesat_frame.metadata.minicpu_dec
    :field hadesd_powerstats_minipl_dec: cubesat_frame.metadata.minipl_dec
    :field hadesd_powerstats_minpowerdul_dec: cubesat_frame.metadata.minpowerdul_dec
    :field hadesd_powerstats_minpowerdul455_dec: cubesat_frame.metadata.minpowerdul455_dec
    :field hadesd_powerstats_minvdac_dec: cubesat_frame.metadata.minvdac_dec
    :field hadesd_powerstats_maxvbusadc_vbatadc_hi_tmp: cubesat_frame.metadata.maxvbusadc_vbatadc_hi_tmp
    :field hadesd_powerstats_maxvbatadc_lo_vcpuadc_hi_tmp: cubesat_frame.metadata.maxvbatadc_lo_vcpuadc_hi_tmp
    :field hadesd_powerstats_maxvcpuadc_lo_free_tmp: cubesat_frame.metadata.maxvcpuadc_lo_free_tmp
    :field hadesd_powerstats_maxvbus2_tmp: cubesat_frame.metadata.maxvbus2_tmp
    :field hadesd_powerstats_maxvbus3_tmp: cubesat_frame.metadata.maxvbus3_tmp
    :field hadesd_powerstats_maxvbat2_tmp: cubesat_frame.metadata.maxvbat2_tmp
    :field hadesd_powerstats_maxibat_dec: cubesat_frame.metadata.maxibat_dec
    :field hadesd_powerstats_maxicpu_dec: cubesat_frame.metadata.maxicpu_dec
    :field hadesd_powerstats_maxipl_tmp: cubesat_frame.metadata.maxipl_tmp
    :field hadesd_powerstats_maxpowerdul_dec: cubesat_frame.metadata.maxpowerdul_dec
    :field hadesd_powerstats_maxpowerdul455_dec: cubesat_frame.metadata.maxpowerdul455_dec
    :field hadesd_powerstats_maxvdac_dec: cubesat_frame.metadata.maxvdac_dec
    :field hadesd_powerstats_medvbusadc_vbatadc_hi_tmp: cubesat_frame.metadata.medvbusadc_vbatadc_hi_tmp
    :field hadesd_powerstats_medvbatadc_lo_vcpuadc_hi_tmp: cubesat_frame.metadata.medvbatadc_lo_vcpuadc_hi_tmp
    :field hadesd_powerstats_medvcpuadc_lo_free_tmp: cubesat_frame.metadata.medvcpuadc_lo_free_tmp
    :field hadesd_powerstats_ibat_rx_charging_dec: cubesat_frame.metadata.ibat_rx_charging_dec
    :field hadesd_powerstats_ibat_rx_discharging_dec: cubesat_frame.metadata.ibat_rx_discharging_dec
    :field hadesd_powerstats_ibat_tx_low_power_charging_dec: cubesat_frame.metadata.ibat_tx_low_power_charging_dec
    :field hadesd_powerstats_ibat_tx_low_power_discharging_dec: cubesat_frame.metadata.ibat_tx_low_power_discharging_dec
    :field hadesd_powerstats_ibat_tx_high_power_charging_dec: cubesat_frame.metadata.ibat_tx_high_power_charging_dec
    :field hadesd_powerstats_ibat_tx_high_power_discharging_dec: cubesat_frame.metadata.ibat_tx_high_power_discharging_dec
    :field hadesd_powerstats_medpowerdul_dec: cubesat_frame.metadata.medpowerdul_dec
    :field hadesd_powerstats_medpowerdul455_dec: cubesat_frame.metadata.medpowerdul455_dec
    :field hadesd_powerstats_medvdac_dec: cubesat_frame.metadata.medvdac_dec
    :field hadesd_powerstats_minvbus1_dec: cubesat_frame.metadata.minvbus1_dec
    :field hadesd_powerstats_minvbat1_dec: cubesat_frame.metadata.minvbat1_dec
    :field hadesd_powerstats_minvcpu_dec: cubesat_frame.metadata.minvcpu_dec
    :field hadesd_powerstats_minvbus2_dec: cubesat_frame.metadata.minvbus2_dec
    :field hadesd_powerstats_minvbus3_dec: cubesat_frame.metadata.minvbus3_dec
    :field hadesd_powerstats_minvbat2_dec: cubesat_frame.metadata.minvbat2_dec
    :field hadesd_powerstats_minibat_dec: cubesat_frame.metadata.minibat_dec
    :field hadesd_powerstats_maxvbus1_dec: cubesat_frame.metadata.maxvbus1_dec
    :field hadesd_powerstats_maxvbat1_dec: cubesat_frame.metadata.maxvbat1_dec
    :field hadesd_powerstats_maxvcpu_dec: cubesat_frame.metadata.maxvcpu_dec
    :field hadesd_powerstats_maxvbus2_dec: cubesat_frame.metadata.maxvbus2_dec
    :field hadesd_powerstats_maxvbus3_dec: cubesat_frame.metadata.maxvbus3_dec
    :field hadesd_powerstats_maxvbat2_dec: cubesat_frame.metadata.maxvbat2_dec
    :field hadesd_powerstats_maxipl_dec: cubesat_frame.metadata.maxipl_dec
    # Type 5 Frame (TempStats):
    :field hadesd_tempstats_mintpa_tmp: cubesat_frame.metadata.mintpa_tmp
    :field hadesd_tempstats_mintpb_tmp: cubesat_frame.metadata.mintpb_tmp
    :field hadesd_tempstats_mintpc_tmp: cubesat_frame.metadata.mintpc_tmp
    :field hadesd_tempstats_mintpd_tmp: cubesat_frame.metadata.mintpd_tmp
    :field hadesd_tempstats_mintpe_tmp: cubesat_frame.metadata.mintpe_tmp
    :field hadesd_tempstats_minteps_tmp: cubesat_frame.metadata.minteps_tmp
    :field hadesd_tempstats_minttx_tmp: cubesat_frame.metadata.minttx_tmp
    :field hadesd_tempstats_minttx2_tmp: cubesat_frame.metadata.minttx2_tmp
    :field hadesd_tempstats_mintrx_tmp: cubesat_frame.metadata.mintrx_tmp
    :field hadesd_tempstats_mintcpu_tmp: cubesat_frame.metadata.mintcpu_tmp
    :field hadesd_tempstats_maxtpa_tmp: cubesat_frame.metadata.maxtpa_tmp
    :field hadesd_tempstats_maxtpb_tmp: cubesat_frame.metadata.maxtpb_tmp
    :field hadesd_tempstats_maxtpc_tmp: cubesat_frame.metadata.maxtpc_tmp
    :field hadesd_tempstats_maxtpd_tmp: cubesat_frame.metadata.maxtpd_tmp
    :field hadesd_tempstats_maxtpe_tmp: cubesat_frame.metadata.maxtpe_tmp
    :field hadesd_tempstats_maxteps_tmp: cubesat_frame.metadata.maxteps_tmp
    :field hadesd_tempstats_maxttx_tmp: cubesat_frame.metadata.maxttx_tmp
    :field hadesd_tempstats_maxttx2_tmp: cubesat_frame.metadata.maxttx2_tmp
    :field hadesd_tempstats_maxtrx_tmp: cubesat_frame.metadata.maxtrx_tmp
    :field hadesd_tempstats_maxtcpu_tmp: cubesat_frame.metadata.maxtcpu_tmp
    :field hadesd_tempstats_medtpa_tmp: cubesat_frame.metadata.medtpa_tmp
    :field hadesd_tempstats_medtpb_tmp: cubesat_frame.metadata.medtpb_tmp
    :field hadesd_tempstats_medtpc_tmp: cubesat_frame.metadata.medtpc_tmp
    :field hadesd_tempstats_medtpd_tmp: cubesat_frame.metadata.medtpd_tmp
    :field hadesd_tempstats_medtpe_tmp: cubesat_frame.metadata.medtpe_tmp
    :field hadesd_tempstats_medteps_tmp: cubesat_frame.metadata.medteps_tmp
    :field hadesd_tempstats_medttx_tmp: cubesat_frame.metadata.medttx_tmp
    :field hadesd_tempstats_medttx2_tmp: cubesat_frame.metadata.medttx2_tmp
    :field hadesd_tempstats_medtrx_tmp: cubesat_frame.metadata.medtrx_tmp
    :field hadesd_tempstats_medtcpu_tmp: cubesat_frame.metadata.medtcpu_tmp
    :field hadesd_tempstats_mintpa_dec: cubesat_frame.metadata.mintpa_dec
    :field hadesd_tempstats_mintpb_dec: cubesat_frame.metadata.mintpb_dec
    :field hadesd_tempstats_mintpc_dec: cubesat_frame.metadata.mintpc_dec
    :field hadesd_tempstats_mintpd_dec: cubesat_frame.metadata.mintpd_dec
    :field hadesd_tempstats_minteps_dec: cubesat_frame.metadata.minteps_dec
    :field hadesd_tempstats_minttx_dec: cubesat_frame.metadata.minttx_dec
    :field hadesd_tempstats_minttx2_dec: cubesat_frame.metadata.minttx2_dec
    :field hadesd_tempstats_mintrx_dec: cubesat_frame.metadata.mintrx_dec
    :field hadesd_tempstats_mintcpu_dec: cubesat_frame.metadata.mintcpu_dec
    :field hadesd_tempstats_maxtpa_dec: cubesat_frame.metadata.maxtpa_dec
    :field hadesd_tempstats_maxtpb_dec: cubesat_frame.metadata.maxtpb_dec
    :field hadesd_tempstats_maxtpc_dec: cubesat_frame.metadata.maxtpc_dec
    :field hadesd_tempstats_maxtpd_dec: cubesat_frame.metadata.maxtpd_dec
    :field hadesd_tempstats_maxteps_dec: cubesat_frame.metadata.maxteps_dec
    :field hadesd_tempstats_maxttx_dec: cubesat_frame.metadata.maxttx_dec
    :field hadesd_tempstats_maxttx2_dec: cubesat_frame.metadata.maxttx2_dec
    :field hadesd_tempstats_maxtrx_dec: cubesat_frame.metadata.maxtrx_dec
    :field hadesd_tempstats_maxtcpu_dec: cubesat_frame.metadata.maxtcpu_dec
    :field hadesd_tempstats_medtpa_dec: cubesat_frame.metadata.medtpa_dec
    :field hadesd_tempstats_medtpb_dec: cubesat_frame.metadata.medtpb_dec
    :field hadesd_tempstats_medtpc_dec: cubesat_frame.metadata.medtpc_dec
    :field hadesd_tempstats_medtpd_dec: cubesat_frame.metadata.medtpd_dec
    :field hadesd_tempstats_medteps_dec: cubesat_frame.metadata.medteps_dec
    :field hadesd_tempstats_medttx_dec: cubesat_frame.metadata.medttx_dec
    :field hadesd_tempstats_medttx2_dec: cubesat_frame.metadata.medttx2_dec
    :field hadesd_tempstats_medtrx_dec: cubesat_frame.metadata.medtrx_dec
    :field hadesd_tempstats_medtcpu_dec: cubesat_frame.metadata.medtcpu_dec
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.cubesat_frame = Hadesd.CubesatFrame(self._io, self, self._root)

    class PowerFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.spa_tmp = self._io.read_u1()
            self.spb_tmp = self._io.read_u1()
            self.spc_tmp = self._io.read_u1()
            self.spd_tmp = self._io.read_u1()
            self.spe_tmp = self._io.read_u1()
            self.spf_tmp = self._io.read_u1()
            self.vbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.vbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.vcpuadc_lo_vbus2_tmp = self._io.read_u2le()
            self.vbus3_vbat2_hi_tmp = self._io.read_u2le()
            self.vbat2_lo_ibat_hi_tmp = self._io.read_u2le()
            self.ibat_lo_icpu_hi_tmp = self._io.read_u2le()
            self.icpu_lo_ipl_tmp = self._io.read_u2le()
            self.powerdul_tmp = self._io.read_u1()
            self.powerdul455_tmp = self._io.read_u1()
            self.vdac_tmp = self._io.read_u1()

        @property
        def pwrdul1_dec(self):
            if hasattr(self, '_m_pwrdul1_dec'):
                return self._m_pwrdul1_dec

            self._m_pwrdul1_dec = (self.powerdul_tmp * 16)
            return getattr(self, '_m_pwrdul1_dec', None)

        @property
        def vbus3_vbus2_dec(self):
            if hasattr(self, '_m_vbus3_vbus2_dec'):
                return self._m_vbus3_vbus2_dec

            self._m_vbus3_vbus2_dec = (self.vbus3_dec - self.vbus2_dec)
            return getattr(self, '_m_vbus3_vbus2_dec', None)

        @property
        def spc_dec(self):
            if hasattr(self, '_m_spc_dec'):
                return self._m_spc_dec

            self._m_spc_dec = (self.spc_tmp << 1)
            return getattr(self, '_m_spc_dec', None)

        @property
        def ibat_dec(self):
            if hasattr(self, '_m_ibat_dec'):
                return self._m_ibat_dec

            self._m_ibat_dec = (((((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)) - 4096) if (((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)) > 2047 else (((self.vbat2_lo_ibat_hi_tmp << 8) & 3840) | ((self.ibat_lo_icpu_hi_tmp >> 8) & 4095)))
            return getattr(self, '_m_ibat_dec', None)

        @property
        def vbat1_dec(self):
            if hasattr(self, '_m_vbat1_dec'):
                return self._m_vbat1_dec

            self._m_vbat1_dec = ((((self.vbatadc_lo_vcpuadc_hi_tmp << 8) & 3840) | ((self.vbatadc_lo_vcpuadc_hi_tmp >> 8) & 4095)) * 1400) // 1000
            return getattr(self, '_m_vbat1_dec', None)

        @property
        def spa_dec(self):
            if hasattr(self, '_m_spa_dec'):
                return self._m_spa_dec

            self._m_spa_dec = (self.spa_tmp << 1)
            return getattr(self, '_m_spa_dec', None)

        @property
        def vbus1_dec(self):
            if hasattr(self, '_m_vbus1_dec'):
                return self._m_vbus1_dec

            self._m_vbus1_dec = ((self.vbusadc_vbatadc_hi_tmp >> 4) * 1400) // 1000
            return getattr(self, '_m_vbus1_dec', None)

        @property
        def pwrdul4_dec(self):
            if hasattr(self, '_m_pwrdul4_dec'):
                return self._m_pwrdul4_dec

            self._m_pwrdul4_dec = (self.powerdul455_tmp * 16)
            return getattr(self, '_m_pwrdul4_dec', None)

        @property
        def vbus1_vbat1_dec(self):
            if hasattr(self, '_m_vbus1_vbat1_dec'):
                return self._m_vbus1_vbat1_dec

            self._m_vbus1_vbat1_dec = (self.vbus1_dec - self.vbat1_dec)
            return getattr(self, '_m_vbus1_vbat1_dec', None)

        @property
        def spb_dec(self):
            if hasattr(self, '_m_spb_dec'):
                return self._m_spb_dec

            self._m_spb_dec = (self.spb_tmp << 1)
            return getattr(self, '_m_spb_dec', None)

        @property
        def vcpu_dec(self):
            if hasattr(self, '_m_vcpu_dec'):
                return self._m_vcpu_dec

            self._m_vcpu_dec = (1210 * 4096) // (((self.vbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | (self.vcpuadc_lo_vbus2_tmp >> 12))
            return getattr(self, '_m_vcpu_dec', None)

        @property
        def ipl_dec(self):
            if hasattr(self, '_m_ipl_dec'):
                return self._m_ipl_dec

            self._m_ipl_dec = (self.icpu_lo_ipl_tmp & 4095)
            return getattr(self, '_m_ipl_dec', None)

        @property
        def vbat2_dec(self):
            if hasattr(self, '_m_vbat2_dec'):
                return self._m_vbat2_dec

            self._m_vbat2_dec = ((((self.vbus3_vbat2_hi_tmp << 8) & 3840) | (self.vbat2_lo_ibat_hi_tmp >> 8)) * 4)
            return getattr(self, '_m_vbat2_dec', None)

        @property
        def spd_dec(self):
            if hasattr(self, '_m_spd_dec'):
                return self._m_spd_dec

            self._m_spd_dec = (self.spd_tmp << 1)
            return getattr(self, '_m_spd_dec', None)

        @property
        def vbus2_dec(self):
            if hasattr(self, '_m_vbus2_dec'):
                return self._m_vbus2_dec

            self._m_vbus2_dec = ((self.vcpuadc_lo_vbus2_tmp & 4095) * 4)
            return getattr(self, '_m_vbus2_dec', None)

        @property
        def vbus3_dec(self):
            if hasattr(self, '_m_vbus3_dec'):
                return self._m_vbus3_dec

            self._m_vbus3_dec = ((self.vbus3_vbat2_hi_tmp >> 4) * 4)
            return getattr(self, '_m_vbus3_dec', None)

        @property
        def icpu_dec(self):
            if hasattr(self, '_m_icpu_dec'):
                return self._m_icpu_dec

            self._m_icpu_dec = (((self.ibat_lo_icpu_hi_tmp << 4) & 4080) | (self.icpu_lo_ipl_tmp >> 12))
            return getattr(self, '_m_icpu_dec', None)


    class StatusFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sclock_dec = self._io.read_u4le()
            self.uptime_dec = self._io.read_u2le()
            self.nrun_dec = self._io.read_u2le()
            self.npayload_dec = self._io.read_u1()
            self.nwire_dec = self._io.read_u1()
            self.nbusdrops_lastreset_tmp = self._io.read_u1()
            self.bate_mote_tmp = self._io.read_u1()
            self.ntasksnotexecuted_dec = self._io.read_u1()
            self.antennadeployed_dec = self._io.read_u1()
            self.nexteepromerrors_dec = self._io.read_u1()
            self.failed_task_id_dec = self._io.read_u1()
            self.orbperiod_dec = self._io.read_u1()
            self.strfwd0_dec = self._io.read_u1()
            self.strfwd1_dec = self._io.read_u2le()
            self.strfwd2_dec = self._io.read_u2le()
            self.strfwd3_dec = self._io.read_u1()

        @property
        def transponder_dec(self):
            if hasattr(self, '_m_transponder_dec'):
                return self._m_transponder_dec

            self._m_transponder_dec = (self.bate_mote_tmp & 15)
            return getattr(self, '_m_transponder_dec', None)

        @property
        def nbusdrops_dec(self):
            if hasattr(self, '_m_nbusdrops_dec'):
                return self._m_nbusdrops_dec

            self._m_nbusdrops_dec = (self.nbusdrops_lastreset_tmp >> 4)
            return getattr(self, '_m_nbusdrops_dec', None)

        @property
        def battery_dec(self):
            if hasattr(self, '_m_battery_dec'):
                return self._m_battery_dec

            self._m_battery_dec = (self.bate_mote_tmp >> 4)
            return getattr(self, '_m_battery_dec', None)

        @property
        def last_reset_cause_dec(self):
            if hasattr(self, '_m_last_reset_cause_dec'):
                return self._m_last_reset_cause_dec

            self._m_last_reset_cause_dec = (self.nbusdrops_lastreset_tmp & 15)
            return getattr(self, '_m_last_reset_cause_dec', None)

        @property
        def ntrans_dec(self):
            if hasattr(self, '_m_ntrans_dec'):
                return self._m_ntrans_dec

            self._m_ntrans_dec = (0 if self.nwire_dec <= 25 else (self.nwire_dec - 26))
            return getattr(self, '_m_ntrans_dec', None)


    class FirstHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type = self._io.read_bits_int_be(4)
            if not self.type >= 1:
                raise kaitaistruct.ValidationLessThanError(1, self.type, self._io, u"/types/first_header/seq/0")
            if not self.type <= 5:
                raise kaitaistruct.ValidationGreaterThanError(5, self.type, self._io, u"/types/first_header/seq/0")
            self.address = self._io.read_bits_int_be(4)
            if not self.address == 8:
                raise kaitaistruct.ValidationNotEqualError(8, self.address, self._io, u"/types/first_header/seq/1")


    class TempstatsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mintpa_tmp = self._io.read_u1()
            self.mintpb_tmp = self._io.read_u1()
            self.mintpc_tmp = self._io.read_u1()
            self.mintpd_tmp = self._io.read_u1()
            self.mintpe_tmp = self._io.read_u1()
            self.minteps_tmp = self._io.read_u1()
            self.minttx_tmp = self._io.read_u1()
            self.minttx2_tmp = self._io.read_u1()
            self.mintrx_tmp = self._io.read_u1()
            self.mintcpu_tmp = self._io.read_u1()
            self.maxtpa_tmp = self._io.read_u1()
            self.maxtpb_tmp = self._io.read_u1()
            self.maxtpc_tmp = self._io.read_u1()
            self.maxtpd_tmp = self._io.read_u1()
            self.maxtpe_tmp = self._io.read_u1()
            self.maxteps_tmp = self._io.read_u1()
            self.maxttx_tmp = self._io.read_u1()
            self.maxttx2_tmp = self._io.read_u1()
            self.maxtrx_tmp = self._io.read_u1()
            self.maxtcpu_tmp = self._io.read_u1()
            self.medtpa_tmp = self._io.read_u1()
            self.medtpb_tmp = self._io.read_u1()
            self.medtpc_tmp = self._io.read_u1()
            self.medtpd_tmp = self._io.read_u1()
            self.medtpe_tmp = self._io.read_u1()
            self.medteps_tmp = self._io.read_u1()
            self.medttx_tmp = self._io.read_u1()
            self.medttx2_tmp = self._io.read_u1()
            self.medtrx_tmp = self._io.read_u1()
            self.medtcpu_tmp = self._io.read_u1()

        @property
        def mintpc_dec(self):
            if hasattr(self, '_m_mintpc_dec'):
                return self._m_mintpc_dec

            self._m_mintpc_dec = ((self.mintpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpc_dec', None)

        @property
        def medtpa_dec(self):
            if hasattr(self, '_m_medtpa_dec'):
                return self._m_medtpa_dec

            self._m_medtpa_dec = ((self.medtpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtpa_dec', None)

        @property
        def maxtrx_dec(self):
            if hasattr(self, '_m_maxtrx_dec'):
                return self._m_maxtrx_dec

            self._m_maxtrx_dec = ((self.maxtrx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtrx_dec', None)

        @property
        def medtrx_dec(self):
            if hasattr(self, '_m_medtrx_dec'):
                return self._m_medtrx_dec

            self._m_medtrx_dec = ((self.medtrx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtrx_dec', None)

        @property
        def maxtpb_dec(self):
            if hasattr(self, '_m_maxtpb_dec'):
                return self._m_maxtpb_dec

            self._m_maxtpb_dec = ((self.maxtpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpb_dec', None)

        @property
        def medtcpu_dec(self):
            if hasattr(self, '_m_medtcpu_dec'):
                return self._m_medtcpu_dec

            self._m_medtcpu_dec = ((self.medtcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtcpu_dec', None)

        @property
        def mintcpu_dec(self):
            if hasattr(self, '_m_mintcpu_dec'):
                return self._m_mintcpu_dec

            self._m_mintcpu_dec = ((self.mintcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintcpu_dec', None)

        @property
        def maxttx2_dec(self):
            if hasattr(self, '_m_maxttx2_dec'):
                return self._m_maxttx2_dec

            self._m_maxttx2_dec = ((self.maxttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxttx2_dec', None)

        @property
        def minteps_dec(self):
            if hasattr(self, '_m_minteps_dec'):
                return self._m_minteps_dec

            self._m_minteps_dec = ((self.minteps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minteps_dec', None)

        @property
        def maxtpd_dec(self):
            if hasattr(self, '_m_maxtpd_dec'):
                return self._m_maxtpd_dec

            self._m_maxtpd_dec = ((self.maxtpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpd_dec', None)

        @property
        def minttx_dec(self):
            if hasattr(self, '_m_minttx_dec'):
                return self._m_minttx_dec

            self._m_minttx_dec = ((self.minttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minttx_dec', None)

        @property
        def medttx2_dec(self):
            if hasattr(self, '_m_medttx2_dec'):
                return self._m_medttx2_dec

            self._m_medttx2_dec = ((self.medttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medttx2_dec', None)

        @property
        def maxtcpu_dec(self):
            if hasattr(self, '_m_maxtcpu_dec'):
                return self._m_maxtcpu_dec

            self._m_maxtcpu_dec = ((self.maxtcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtcpu_dec', None)

        @property
        def minttx2_dec(self):
            if hasattr(self, '_m_minttx2_dec'):
                return self._m_minttx2_dec

            self._m_minttx2_dec = ((self.minttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_minttx2_dec', None)

        @property
        def medttx_dec(self):
            if hasattr(self, '_m_medttx_dec'):
                return self._m_medttx_dec

            self._m_medttx_dec = ((self.medttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medttx_dec', None)

        @property
        def maxtpa_dec(self):
            if hasattr(self, '_m_maxtpa_dec'):
                return self._m_maxtpa_dec

            self._m_maxtpa_dec = ((self.maxtpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpa_dec', None)

        @property
        def medtpb_dec(self):
            if hasattr(self, '_m_medtpb_dec'):
                return self._m_medtpb_dec

            self._m_medtpb_dec = ((self.medtpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtpb_dec', None)

        @property
        def mintrx_dec(self):
            if hasattr(self, '_m_mintrx_dec'):
                return self._m_mintrx_dec

            self._m_mintrx_dec = ((self.mintrx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintrx_dec', None)

        @property
        def mintpd_dec(self):
            if hasattr(self, '_m_mintpd_dec'):
                return self._m_mintpd_dec

            self._m_mintpd_dec = ((self.mintpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpd_dec', None)

        @property
        def medteps_dec(self):
            if hasattr(self, '_m_medteps_dec'):
                return self._m_medteps_dec

            self._m_medteps_dec = ((self.medteps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medteps_dec', None)

        @property
        def mintpa_dec(self):
            if hasattr(self, '_m_mintpa_dec'):
                return self._m_mintpa_dec

            self._m_mintpa_dec = ((self.mintpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpa_dec', None)

        @property
        def maxtpc_dec(self):
            if hasattr(self, '_m_maxtpc_dec'):
                return self._m_maxtpc_dec

            self._m_maxtpc_dec = ((self.maxtpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxtpc_dec', None)

        @property
        def maxteps_dec(self):
            if hasattr(self, '_m_maxteps_dec'):
                return self._m_maxteps_dec

            self._m_maxteps_dec = ((self.maxteps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxteps_dec', None)

        @property
        def mintpb_dec(self):
            if hasattr(self, '_m_mintpb_dec'):
                return self._m_mintpb_dec

            self._m_mintpb_dec = ((self.mintpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_mintpb_dec', None)

        @property
        def maxttx_dec(self):
            if hasattr(self, '_m_maxttx_dec'):
                return self._m_maxttx_dec

            self._m_maxttx_dec = ((self.maxttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_maxttx_dec', None)

        @property
        def medtpd_dec(self):
            if hasattr(self, '_m_medtpd_dec'):
                return self._m_medtpd_dec

            self._m_medtpd_dec = ((self.medtpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtpd_dec', None)

        @property
        def medtpc_dec(self):
            if hasattr(self, '_m_medtpc_dec'):
                return self._m_medtpc_dec

            self._m_medtpc_dec = ((self.medtpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_medtpc_dec', None)


    class PowerstatsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.minvbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.minvbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.minvcpuadc_lo_free_tmp = self._io.read_u1()
            self.minvbus2_tmp = self._io.read_u1()
            self.minvbus3_tmp = self._io.read_u1()
            self.minvbat2_tmp = self._io.read_u1()
            self.minibat_tmp = self._io.read_u1()
            self.minicpu_dec = self._io.read_u1()
            self.minipl_dec = self._io.read_u1()
            self.minpowerdul_dec = self._io.read_u1()
            self.minpowerdul455_dec = self._io.read_u1()
            self.minvdac_dec = self._io.read_u1()
            self.maxvbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.maxvbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.maxvcpuadc_lo_free_tmp = self._io.read_u1()
            self.maxvbus2_tmp = self._io.read_u1()
            self.maxvbus3_tmp = self._io.read_u1()
            self.maxvbat2_tmp = self._io.read_u1()
            self.maxibat_dec = self._io.read_u1()
            self.maxicpu_dec = self._io.read_u1()
            self.maxipl_tmp = self._io.read_u1()
            self.maxpowerdul_dec = self._io.read_u1()
            self.maxpowerdul455_dec = self._io.read_u1()
            self.maxvdac_dec = self._io.read_u1()
            self.medvbusadc_vbatadc_hi_tmp = self._io.read_u2le()
            self.medvbatadc_lo_vcpuadc_hi_tmp = self._io.read_u2le()
            self.medvcpuadc_lo_free_tmp = self._io.read_u1()
            self.ibat_rx_charging_dec = self._io.read_u1()
            self.ibat_rx_discharging_dec = self._io.read_u1()
            self.ibat_tx_low_power_charging_dec = self._io.read_u1()
            self.ibat_tx_low_power_discharging_dec = self._io.read_u1()
            self.ibat_tx_high_power_charging_dec = self._io.read_u1()
            self.ibat_tx_high_power_discharging_dec = self._io.read_u1()
            self.medpowerdul_dec = self._io.read_u1()
            self.medpowerdul455_dec = self._io.read_u1()
            self.medvdac_dec = self._io.read_u1()

        @property
        def maxvbat2_dec(self):
            if hasattr(self, '_m_maxvbat2_dec'):
                return self._m_maxvbat2_dec

            self._m_maxvbat2_dec = ((self.maxvbat2_tmp * 16) * 4)
            return getattr(self, '_m_maxvbat2_dec', None)

        @property
        def maxvcpu_dec(self):
            if hasattr(self, '_m_maxvcpu_dec'):
                return self._m_maxvcpu_dec

            self._m_maxvcpu_dec = ((1210 * 4096) // (((self.maxvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | 1) if self.maxvcpuadc_lo_free_tmp > 4 else (1210 * 4096) // ((self.maxvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080))
            return getattr(self, '_m_maxvcpu_dec', None)

        @property
        def maxvbus3_dec(self):
            if hasattr(self, '_m_maxvbus3_dec'):
                return self._m_maxvbus3_dec

            self._m_maxvbus3_dec = ((self.maxvbus2_tmp * 16) * 4)
            return getattr(self, '_m_maxvbus3_dec', None)

        @property
        def maxipl_dec(self):
            if hasattr(self, '_m_maxipl_dec'):
                return self._m_maxipl_dec

            self._m_maxipl_dec = (self.maxipl_tmp << 2)
            return getattr(self, '_m_maxipl_dec', None)

        @property
        def minvbus1_dec(self):
            if hasattr(self, '_m_minvbus1_dec'):
                return self._m_minvbus1_dec

            self._m_minvbus1_dec = (1400 * (self.minvbusadc_vbatadc_hi_tmp >> 4)) // 1000
            return getattr(self, '_m_minvbus1_dec', None)

        @property
        def maxvbus1_dec(self):
            if hasattr(self, '_m_maxvbus1_dec'):
                return self._m_maxvbus1_dec

            self._m_maxvbus1_dec = (1400 * (self.maxvbusadc_vbatadc_hi_tmp >> 4)) // 1000
            return getattr(self, '_m_maxvbus1_dec', None)

        @property
        def minibat_dec(self):
            if hasattr(self, '_m_minibat_dec'):
                return self._m_minibat_dec

            self._m_minibat_dec = (self.minibat_tmp * -1)
            return getattr(self, '_m_minibat_dec', None)

        @property
        def minvbat2_dec(self):
            if hasattr(self, '_m_minvbat2_dec'):
                return self._m_minvbat2_dec

            self._m_minvbat2_dec = ((self.minvbat2_tmp * 16) * 4)
            return getattr(self, '_m_minvbat2_dec', None)

        @property
        def minvbus2_dec(self):
            if hasattr(self, '_m_minvbus2_dec'):
                return self._m_minvbus2_dec

            self._m_minvbus2_dec = ((self.minvbus2_tmp * 16) * 4)
            return getattr(self, '_m_minvbus2_dec', None)

        @property
        def minvbat1_dec(self):
            if hasattr(self, '_m_minvbat1_dec'):
                return self._m_minvbat1_dec

            self._m_minvbat1_dec = (1400 * (((self.minvbusadc_vbatadc_hi_tmp << 8) & 3840) | ((self.minvbatadc_lo_vcpuadc_hi_tmp >> 8) & 255))) // 1000
            return getattr(self, '_m_minvbat1_dec', None)

        @property
        def maxvbat1_dec(self):
            if hasattr(self, '_m_maxvbat1_dec'):
                return self._m_maxvbat1_dec

            self._m_maxvbat1_dec = (1400 * (((self.maxvbusadc_vbatadc_hi_tmp << 8) & 3840) | ((self.maxvbatadc_lo_vcpuadc_hi_tmp >> 8) & 255))) // 1000
            return getattr(self, '_m_maxvbat1_dec', None)

        @property
        def minvbus3_dec(self):
            if hasattr(self, '_m_minvbus3_dec'):
                return self._m_minvbus3_dec

            self._m_minvbus3_dec = ((self.minvbus2_tmp * 16) * 4)
            return getattr(self, '_m_minvbus3_dec', None)

        @property
        def minvcpu_dec(self):
            if hasattr(self, '_m_minvcpu_dec'):
                return self._m_minvcpu_dec

            self._m_minvcpu_dec = ((1210 * 4096) // (((self.minvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080) | 1) if self.minvcpuadc_lo_free_tmp > 4 else (1210 * 4096) // ((self.minvbatadc_lo_vcpuadc_hi_tmp << 4) & 4080))
            return getattr(self, '_m_minvcpu_dec', None)

        @property
        def maxvbus2_dec(self):
            if hasattr(self, '_m_maxvbus2_dec'):
                return self._m_maxvbus2_dec

            self._m_maxvbus2_dec = ((self.maxvbus2_tmp * 16) * 4)
            return getattr(self, '_m_maxvbus2_dec', None)


    class TempFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
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
        def ttx_dec(self):
            if hasattr(self, '_m_ttx_dec'):
                return self._m_ttx_dec

            self._m_ttx_dec = ((self.ttx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_ttx_dec', None)

        @property
        def ttx2_dec(self):
            if hasattr(self, '_m_ttx2_dec'):
                return self._m_ttx2_dec

            self._m_ttx2_dec = ((self.ttx2_tmp / 2.0) - 40.0)
            return getattr(self, '_m_ttx2_dec', None)

        @property
        def teps_dec(self):
            if hasattr(self, '_m_teps_dec'):
                return self._m_teps_dec

            self._m_teps_dec = ((self.teps_tmp / 2.0) - 40.0)
            return getattr(self, '_m_teps_dec', None)

        @property
        def tpc_dec(self):
            if hasattr(self, '_m_tpc_dec'):
                return self._m_tpc_dec

            self._m_tpc_dec = ((self.tpc_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpc_dec', None)

        @property
        def tpd_dec(self):
            if hasattr(self, '_m_tpd_dec'):
                return self._m_tpd_dec

            self._m_tpd_dec = ((self.tpd_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpd_dec', None)

        @property
        def tpb_dec(self):
            if hasattr(self, '_m_tpb_dec'):
                return self._m_tpb_dec

            self._m_tpb_dec = ((self.tpb_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpb_dec', None)

        @property
        def tcpu_dec(self):
            if hasattr(self, '_m_tcpu_dec'):
                return self._m_tcpu_dec

            self._m_tcpu_dec = ((self.tcpu_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tcpu_dec', None)

        @property
        def trx_dec(self):
            if hasattr(self, '_m_trx_dec'):
                return self._m_trx_dec

            self._m_trx_dec = ((self.trx_tmp / 2.0) - 40.0)
            return getattr(self, '_m_trx_dec', None)

        @property
        def tpa_dec(self):
            if hasattr(self, '_m_tpa_dec'):
                return self._m_tpa_dec

            self._m_tpa_dec = ((self.tpa_tmp / 2.0) - 40.0)
            return getattr(self, '_m_tpa_dec', None)


    class CubesatFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.first_header = Hadesd.FirstHeader(self._io, self, self._root)
            _on = self.first_header.type
            if _on == 4:
                self.metadata = Hadesd.PowerstatsFrame(self._io, self, self._root)
            elif _on == 1:
                self.metadata = Hadesd.PowerFrame(self._io, self, self._root)
            elif _on == 3:
                self.metadata = Hadesd.StatusFrame(self._io, self, self._root)
            elif _on == 5:
                self.metadata = Hadesd.TempstatsFrame(self._io, self, self._root)
            elif _on == 2:
                self.metadata = Hadesd.TempFrame(self._io, self, self._root)



