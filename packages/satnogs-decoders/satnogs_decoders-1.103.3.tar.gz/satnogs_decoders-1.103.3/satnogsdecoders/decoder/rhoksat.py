# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Rhoksat(KaitaiStruct):
    """:field panel_temp: sp_telemetry.panel0.panel_temp
    :field panel_status: sp_telemetry.panel0.panel_status
    :field panel_voltage: sp_telemetry.panel0.panel_voltage
    :field panel_photodiode: sp_telemetry.panel0.panel_photodiode
    :field panel1_panel_temp: sp_telemetry.panel1.panel_temp
    :field panel1_panel_status: sp_telemetry.panel1.panel_status
    :field panel1_panel_voltage: sp_telemetry.panel1.panel_voltage
    :field panel1_panel_photodiode: sp_telemetry.panel1.panel_photodiode
    :field panel2_panel_temp: sp_telemetry.panel2.panel_temp
    :field panel2_panel_status: sp_telemetry.panel2.panel_status
    :field panel2_panel_voltage: sp_telemetry.panel2.panel_voltage
    :field panel2_panel_photodiode: sp_telemetry.panel2.panel_photodiode
    :field panel3_panel_temp: sp_telemetry.panel3.panel_temp
    :field panel3_panel_status: sp_telemetry.panel3.panel_status
    :field panel3_panel_voltage: sp_telemetry.panel3.panel_voltage
    :field panel3_panel_photodiode: sp_telemetry.panel3.panel_photodiode
    :field panel4_panel_temp: sp_telemetry.panel4.panel_temp
    :field panel4_panel_status: sp_telemetry.panel4.panel_status
    :field panel4_panel_voltage: sp_telemetry.panel4.panel_voltage
    :field panel4_panel_photodiode: sp_telemetry.panel4.panel_photodiode
    :field volt_brdsup: eps_telemetry.volt_brdsup
    :field volt: eps_telemetry.dist_input.volt
    :field current: eps_telemetry.dist_input.current
    :field power: eps_telemetry.dist_input.power
    :field batt_input_volt: eps_telemetry.batt_input.volt
    :field batt_input_current: eps_telemetry.batt_input.current
    :field batt_input_power: eps_telemetry.batt_input.power
    :field stat_obc_on: eps_telemetry.stat_obc_on
    :field stat_obc_ocf: eps_telemetry.stat_obc_ocf
    :field bat_stat: eps_telemetry.bat_stat
    :field temp: eps_telemetry.temp
    :field temp2: eps_telemetry.temp2
    :field temp3: eps_telemetry.temp3
    :field stid: eps_telemetry.status.reply_header.stid
    :field ivid: eps_telemetry.status.reply_header.ivid
    :field rc: eps_telemetry.status.reply_header.rc
    :field bid: eps_telemetry.status.reply_header.bid
    :field cmderrstat: eps_telemetry.status.reply_header.cmderrstat
    :field mode: eps_telemetry.status.mode
    :field conf: eps_telemetry.status.conf
    :field reset_cause: eps_telemetry.status.reset_cause
    :field uptime: eps_telemetry.status.uptime
    :field error: eps_telemetry.status.error
    :field rc_cnt_pwron: eps_telemetry.status.rc_cnt_pwron
    :field rc_cnt_wdg: eps_telemetry.status.rc_cnt_wdg
    :field rc_cnt_cmd: eps_telemetry.status.rc_cnt_cmd
    :field rc_cnt_pweron_mcu: eps_telemetry.status.rc_cnt_pweron_mcu
    :field rc_cnt_emlopo: eps_telemetry.status.rc_cnt_emlopo
    :field prevcmd_elapsed: eps_telemetry.status.prevcmd_elapsed
    :field ants_temperature: anta_telemetry.ants_temperature
    :field ants_deployment: anta_telemetry.ants_deployment
    :field ants_uptime: anta_telemetry.ants_uptime
    :field antb_telemetry_ants_temperature: antb_telemetry.ants_temperature
    :field antb_telemetry_ants_deployment: antb_telemetry.ants_deployment
    :field antb_telemetry_ants_uptime: antb_telemetry.ants_uptime
    :field imtq_system_state_mode: imtq_system_state.mode
    :field err: imtq_system_state.err
    :field imtq_system_state_conf: imtq_system_state.conf
    :field imtq_system_state_uptime: imtq_system_state.uptime
    :field x: imtq_magnetometer.cal_magf.x
    :field y: imtq_magnetometer.cal_magf.y
    :field z: imtq_magnetometer.cal_magf.z
    :field coilact: imtq_magnetometer.coilact
    :field last_detumble_time: last_detumble_time
    :field acc_x: acc.x
    :field acc_y: acc.y
    :field acc_z: acc.z
    :field gyro_x: gyro.x
    :field gyro_y: gyro.y
    :field gyro_z: gyro.z
    :field trxvu_mode: trxvu_mode
    :field onboard_time: onboard_time
    :field obc_up_time: obc_up_time
    :field num_reboots: num_reboots
    :field rtcok: rtcok
    :field storage_available_ram: storage_available_ram
    :field storage_available_sd: storage_available_sd
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.resetcounter = self._io.read_u4le()
        self.latest_time = self._io.read_u4le()
        self.sp_telemetry = Rhoksat.SpTelemetry(self._io, self, self._root)
        self.eps_telemetry = Rhoksat.EpsTelemetry(self._io, self, self._root)
        self.anta_telemetry = Rhoksat.IsisAntsTelemetry(self._io, self, self._root)
        self.antb_telemetry = Rhoksat.IsisAntsTelemetry(self._io, self, self._root)
        self.imtq_system_state = Rhoksat.ImtqSystemstateT(self._io, self, self._root)
        self.imtq_magnetometer = Rhoksat.ImtqCalMagfT(self._io, self, self._root)
        self.last_detumble_time = self._io.read_u4le()
        self.acc = Rhoksat.Axis(self._io, self, self._root)
        self.gyro = Rhoksat.Axis(self._io, self, self._root)
        self.trxvu_mode = self._io.read_u1()
        self.onboard_time = self._io.read_u4le()
        self.obc_up_time = self._io.read_u4le()
        self.num_reboots = self._io.read_u1()
        self.rtcok = self._io.read_u1()
        self.storage_available_ram = self._io.read_u4le()
        self.storage_available_sd = self._io.read_u4le()

    class IsisAntsTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ants_temperature = self._io.read_u2le()
            self.ants_deployment = self._io.read_u2le()
            self.ants_uptime = self._io.read_u4le()


    class Panel(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.panel_temp = self._io.read_f4le()
            self.panel_status = self._io.read_u1()
            self.panel_voltage = self._io.read_u2le()
            self.panel_photodiode = self._io.read_u2le()


    class IsisEpsGetsystemstatusFromT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reply_header = Rhoksat.IsisEpsReplyheaderT(self._io, self, self._root)
            self.mode = self._io.read_u1()
            self.conf = self._io.read_u1()
            self.reset_cause = self._io.read_u1()
            self.uptime = self._io.read_u4le()
            self.error = self._io.read_u2le()
            self.rc_cnt_pwron = self._io.read_u2le()
            self.rc_cnt_wdg = self._io.read_u2le()
            self.rc_cnt_cmd = self._io.read_u2le()
            self.rc_cnt_pweron_mcu = self._io.read_u2le()
            self.rc_cnt_emlopo = self._io.read_u2le()
            self.prevcmd_elapsed = self._io.read_u2le()


    class ImtqSystemstateT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.mode = self._io.read_u1()
            self.err = self._io.read_u1()
            self.conf = self._io.read_u1()
            self.uptime = self._io.read_u4le()


    class IsisEpsReplyheaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.stid = self._io.read_u1()
            self.ivid = self._io.read_u1()
            self.rc = self._io.read_u1()
            self.bid = self._io.read_u1()
            self.cmderrstat = self._io.read_u1()


    class Vec3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()
            self.z = self._io.read_s4le()


    class ImtqCalMagfT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.cal_magf = Rhoksat.Vec3(self._io, self, self._root)
            self.coilact = self._io.read_u1()


    class IsisEpsVipdengT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.volt = self._io.read_u2le()
            self.current = self._io.read_u2le()
            self.power = self._io.read_u2le()


    class SpTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.panel0 = Rhoksat.Panel(self._io, self, self._root)
            self.panel1 = Rhoksat.Panel(self._io, self, self._root)
            self.panel2 = Rhoksat.Panel(self._io, self, self._root)
            self.panel3 = Rhoksat.Panel(self._io, self, self._root)
            self.panel4 = Rhoksat.Panel(self._io, self, self._root)


    class EpsTelemetry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.volt_brdsup = self._io.read_s2le()
            self.dist_input = Rhoksat.IsisEpsVipdengT(self._io, self, self._root)
            self.batt_input = Rhoksat.IsisEpsVipdengT(self._io, self, self._root)
            self.stat_obc_on = self._io.read_bits_int_be(16)
            self._io.align_to_byte()
            self.stat_obc_ocf = self._io.read_u2le()
            self.bat_stat = self._io.read_u2le()
            self.temp = self._io.read_s2le()
            self.temp2 = self._io.read_s2le()
            self.temp3 = self._io.read_s2le()
            self.status = Rhoksat.IsisEpsGetsystemstatusFromT(self._io, self, self._root)


    class Axis(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()



