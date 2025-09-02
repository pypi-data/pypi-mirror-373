# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Kafasat1(KaitaiStruct):
    """:field dest_callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field src_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field dest_ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field version: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.version
    :field type: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.type
    :field sec_hdr_flag: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.sec_hdr_flag
    :field pkt_apid: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.pkt_apid
    :field seq_flgs: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.seq_flgs
    :field seq_ctr: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.seq_ctr
    :field pkt_len: ax25_frame.payload.ax25_info.ccsds_space_packet.packet_primary_header.pkt_len
    :field pus_header: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.pus_header
    :field service_type: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.service_type
    :field service_subtype: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.secondary_header.service_subtype
    :field sys_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.mode.sys_mode
    :field battery_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.mode.battery_mode
    :field vbat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.vbat
    :field cbat: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.cbat
    :field cbchg: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.cbchg
    :field st_5v: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.st_5v
    :field temperature_bat1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.temperature_bat1
    :field temperature_bat2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.temperature_bat2
    :field heater: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.battery.heater
    :field gnd_wdt: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.gnd_wdt
    :field vin0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin0
    :field vin1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin1
    :field vin2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin2
    :field vin3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin3
    :field vin4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin4
    :field vin5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.vin5
    :field cin0: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin0
    :field cin1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin1
    :field cin2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin2
    :field cin3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin3
    :field cin4: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin4
    :field cin5: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.acu.cin5
    :field sw_cam_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_cam_vout
    :field sw_hrm1_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_hrm1_vout
    :field sw_ant_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_ant_vout
    :field sw_wheel_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_wheel_vout
    :field sw_trxvu_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_trxvu_vout
    :field sw_sband_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_sband_vout
    :field sw_hrm2_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_hrm2_vout
    :field sw_mtqr_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_mtqr_vout
    :field sw_adcs_vout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_adcs_vout
    :field sw_cam_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_cam_cout
    :field sw_hrm1_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_hrm1_cout
    :field sw_ant_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_ant_cout
    :field sw_wheel_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_wheel_cout
    :field sw_trxvu_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_trxvu_cout
    :field sw_sband_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_sband_cout
    :field sw_hrm2_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_hrm2_cout
    :field sw_mtqr_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_mtqr_cout
    :field sw_adcs_cout: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.pdu.sw_adcs_cout
    :field hrm1_deploy: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.deploy.hrm1_deploy
    :field hrm2_deploy: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.deploy.hrm2_deploy
    :field hrm1_deploy_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.deploy.hrm1_deploy_count
    :field hrm2_deploy_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.deploy.hrm2_deploy_count
    :field rx_uptime: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uptime.rx_uptime
    :field tx_uptime: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.uptime.tx_uptime
    :field attitude_estimation_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.attitude_estimation_mode
    :field control_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.control_mode
    :field adcs_run_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.adcs_run_mode
    :field asgp4_mode: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.asgp4_mode
    :field cubecontrol_signal_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cubecontrol_signal_enabled
    :field cubecontrol_motor_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cubecontrol_motor_enabled
    :field cube_sense_enabled: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cube_sense_enabled
    :field cube_enabled1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cube_enabled1
    :field cube_error1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cube_error1
    :field cube_error2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cube_error2
    :field cube_error3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.cube_error3
    :field estimated_roll_angle: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_roll_angle
    :field estimated_pitch_angle: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_pitch_angle
    :field estimated_yaw_angle: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_yaw_angle
    :field estimated_q1: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_q1
    :field estimated_q2: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_q2
    :field estimated_q3: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_q3
    :field estimated_x_angular_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_x_angular_rate
    :field estimated_y_angular_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_y_angular_rate
    :field estimated_z_angular_rate: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.estimated_z_angular_rate
    :field position_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.position_x
    :field position_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.position_y
    :field position_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.position_z
    :field velocity_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.velocity_x
    :field velocity_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.velocity_y
    :field velocity_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.velocity_z
    :field latitude: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.latitude
    :field longitude: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.longitude
    :field altitude: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.altitude
    :field ecef_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.ecef_x
    :field ecef_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.ecef_y
    :field ecef_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_state.ecef_z
    :field magnetic_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.magnetic_x
    :field magnetic_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.magnetic_y
    :field magnetic_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.magnetic_z
    :field css_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.css_x
    :field css_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.css_y
    :field css_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.css_z
    :field sun_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.sun_x
    :field sun_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.sun_y
    :field sun_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.sun_z
    :field nadir_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.nadir_x
    :field nadir_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.nadir_y
    :field nadir_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.nadir_z
    :field angular_rate_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.angular_rate_x
    :field angular_rate_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.angular_rate_y
    :field angular_rate_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.angular_rate_z
    :field wheel_x: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.wheel_x
    :field wheel_y: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.wheel_y
    :field wheel_z: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_measure.wheel_z
    :field adcs_seconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_seconds
    :field adcs_subseconds: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.adcs_subseconds
    :field boot_count: ax25_frame.payload.ax25_info.ccsds_space_packet.data_section.user_data_field.boot_count
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Kafasat1.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Kafasat1.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Kafasat1.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Kafasat1.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Kafasat1.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Kafasat1.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Kafasat1.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Kafasat1.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Kafasat1.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Kafasat1.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Kafasat1.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Kafasat1.SsidMask(self._io, self, self._root)
            self.ctl = self._io.read_u1()


    class AdcsMeasureT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.magnetic_x = self._io.read_s2le()
            self.magnetic_y = self._io.read_s2le()
            self.magnetic_z = self._io.read_s2le()
            self.css_x = self._io.read_s2le()
            self.css_y = self._io.read_s2le()
            self.css_z = self._io.read_s2le()
            self.sun_x = self._io.read_s2le()
            self.sun_y = self._io.read_s2le()
            self.sun_z = self._io.read_s2le()
            self.nadir_x = self._io.read_s2le()
            self.nadir_y = self._io.read_s2le()
            self.nadir_z = self._io.read_s2le()
            self.angular_rate_x = self._io.read_s2le()
            self.angular_rate_y = self._io.read_s2le()
            self.angular_rate_z = self._io.read_s2le()
            self.wheel_x = self._io.read_s2le()
            self.wheel_y = self._io.read_s2le()
            self.wheel_z = self._io.read_s2le()


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
            self.ax25_info = Kafasat1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")


    class AcuT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vin0 = self._io.read_u2le()
            self.vin1 = self._io.read_u2le()
            self.vin2 = self._io.read_u2le()
            self.vin3 = self._io.read_u2le()
            self.vin4 = self._io.read_u2le()
            self.vin5 = self._io.read_u2le()
            self.cin0 = self._io.read_s2le()
            self.cin1 = self._io.read_s2le()
            self.cin2 = self._io.read_s2le()
            self.cin3 = self._io.read_s2le()
            self.cin4 = self._io.read_s2le()
            self.cin5 = self._io.read_s2le()


    class DeployT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw_deploy_stat = []
            for i in range(8):
                self.raw_deploy_stat.append(self._io.read_bits_int_be(1) != 0)

            self._io.align_to_byte()
            self.hrm1_deploy_count = self._io.read_u2le()
            self.hrm2_deploy_count = self._io.read_u2le()

        @property
        def hrm1_deploy(self):
            if hasattr(self, '_m_hrm1_deploy'):
                return self._m_hrm1_deploy

            self._m_hrm1_deploy = (True if self.raw_deploy_stat[0] else False)
            return getattr(self, '_m_hrm1_deploy', None)

        @property
        def hrm2_deploy(self):
            if hasattr(self, '_m_hrm2_deploy'):
                return self._m_hrm2_deploy

            self._m_hrm2_deploy = (True if self.raw_deploy_stat[2] else False)
            return getattr(self, '_m_hrm2_deploy', None)


    class AdcsStateT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.attitude_estimation_mode = self._io.read_bits_int_be(4)
            self.control_mode = self._io.read_bits_int_be(4)
            self.adcs_run_mode = self._io.read_bits_int_be(2)
            self.asgp4_mode = self._io.read_bits_int_be(2)
            self.cubecontrol_signal_enabled = self._io.read_bits_int_be(1) != 0
            self.cubecontrol_motor_enabled = self._io.read_bits_int_be(1) != 0
            self.cube_sense_enabled = self._io.read_bits_int_be(2)
            self._io.align_to_byte()
            self.cube_enabled1 = self._io.read_u1()
            self.cube_error1 = self._io.read_u1()
            self.cube_error2 = self._io.read_u4le()
            self.cube_error3 = self._io.read_u4le()
            self.estimated_roll_angle = self._io.read_s2le()
            self.estimated_pitch_angle = self._io.read_s2le()
            self.estimated_yaw_angle = self._io.read_s2le()
            self.estimated_q1 = self._io.read_s2le()
            self.estimated_q2 = self._io.read_s2le()
            self.estimated_q3 = self._io.read_s2le()
            self.estimated_x_angular_rate = self._io.read_s2le()
            self.estimated_y_angular_rate = self._io.read_s2le()
            self.estimated_z_angular_rate = self._io.read_s2le()
            self.position_x = self._io.read_s2le()
            self.position_y = self._io.read_s2le()
            self.position_z = self._io.read_s2le()
            self.velocity_x = self._io.read_s2le()
            self.velocity_y = self._io.read_s2le()
            self.velocity_z = self._io.read_s2le()
            self.latitude = self._io.read_s2le()
            self.longitude = self._io.read_s2le()
            self.altitude = self._io.read_u2le()
            self.ecef_x = self._io.read_s2le()
            self.ecef_y = self._io.read_s2le()
            self.ecef_z = self._io.read_s2le()


    class IFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pid = self._io.read_u1()
            self._raw_ax25_info = self._io.read_bytes_full()
            _io__raw_ax25_info = KaitaiStream(BytesIO(self._raw_ax25_info))
            self.ax25_info = Kafasat1.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class DataSectionT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_secondary_header = self._io.read_bytes(3)
            _io__raw_secondary_header = KaitaiStream(BytesIO(self._raw_secondary_header))
            self.secondary_header = Kafasat1.SecondaryHeaderT(_io__raw_secondary_header, self, self._root)
            self.user_data_field = Kafasat1.KafasatDataFieldT(self._io, self, self._root)


    class KafasatDataFieldT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_mode = self._io.read_bytes(2)
            _io__raw_mode = KaitaiStream(BytesIO(self._raw_mode))
            self.mode = Kafasat1.ModeT(_io__raw_mode, self, self._root)
            self._raw_battery = self._io.read_bytes(13)
            _io__raw_battery = KaitaiStream(BytesIO(self._raw_battery))
            self.battery = Kafasat1.BatteryT(_io__raw_battery, self, self._root)
            self.gnd_wdt = self._io.read_u4le()
            self._raw_acu = self._io.read_bytes(24)
            _io__raw_acu = KaitaiStream(BytesIO(self._raw_acu))
            self.acu = Kafasat1.AcuT(_io__raw_acu, self, self._root)
            self._raw_pdu = self._io.read_bytes(36)
            _io__raw_pdu = KaitaiStream(BytesIO(self._raw_pdu))
            self.pdu = Kafasat1.PduT(_io__raw_pdu, self, self._root)
            self._raw_deploy = self._io.read_bytes(5)
            _io__raw_deploy = KaitaiStream(BytesIO(self._raw_deploy))
            self.deploy = Kafasat1.DeployT(_io__raw_deploy, self, self._root)
            self._raw_uptime = self._io.read_bytes(8)
            _io__raw_uptime = KaitaiStream(BytesIO(self._raw_uptime))
            self.uptime = Kafasat1.UptimeT(_io__raw_uptime, self, self._root)
            self._raw_adcs_state = self._io.read_bytes(54)
            _io__raw_adcs_state = KaitaiStream(BytesIO(self._raw_adcs_state))
            self.adcs_state = Kafasat1.AdcsStateT(_io__raw_adcs_state, self, self._root)
            self._raw_adcs_measure = self._io.read_bytes(36)
            _io__raw_adcs_measure = KaitaiStream(BytesIO(self._raw_adcs_measure))
            self.adcs_measure = Kafasat1.AdcsMeasureT(_io__raw_adcs_measure, self, self._root)
            self.adcs_seconds = self._io.read_u4le()
            self.adcs_subseconds = self._io.read_u2le()
            self.boot_count = self._io.read_u2le()


    class UptimeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rx_uptime = self._io.read_u4le()
            self.tx_uptime = self._io.read_u4le()


    class SecondaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pus_header = self._io.read_u1()
            self.service_type = self._io.read_u1()
            self.service_subtype = self._io.read_u1()


    class PduT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sw_cam_vout = self._io.read_u2le()
            self.sw_hrm1_vout = self._io.read_u2le()
            self.sw_ant_vout = self._io.read_u2le()
            self.sw_wheel_vout = self._io.read_u2le()
            self.sw_trxvu_vout = self._io.read_u2le()
            self.sw_sband_vout = self._io.read_u2le()
            self.sw_hrm2_vout = self._io.read_u2le()
            self.sw_mtqr_vout = self._io.read_u2le()
            self.sw_adcs_vout = self._io.read_u2le()
            self.sw_cam_cout = self._io.read_s2le()
            self.sw_hrm1_cout = self._io.read_s2le()
            self.sw_ant_cout = self._io.read_s2le()
            self.sw_wheel_cout = self._io.read_s2le()
            self.sw_trxvu_cout = self._io.read_s2le()
            self.sw_sband_cout = self._io.read_s2le()
            self.sw_hrm2_cout = self._io.read_s2le()
            self.sw_mtqr_cout = self._io.read_s2le()
            self.sw_adcs_cout = self._io.read_s2le()


    class PacketPrimaryHeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version = self._io.read_bits_int_be(3)
            self.type = self._io.read_bits_int_be(1) != 0
            self.sec_hdr_flag = self._io.read_bits_int_be(1) != 0
            self.pkt_apid = self._io.read_bits_int_be(11)
            self.seq_flgs = self._io.read_bits_int_be(2)
            self.seq_ctr = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.pkt_len = self._io.read_u2be()


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
            self.callsign_ror = Kafasat1.Callsign(_io__raw_callsign_ror, self, self._root)


    class CcsdsSpacePacketT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self._raw_packet_primary_header = self._io.read_bytes(6)
            _io__raw_packet_primary_header = KaitaiStream(BytesIO(self._raw_packet_primary_header))
            self.packet_primary_header = Kafasat1.PacketPrimaryHeaderT(_io__raw_packet_primary_header, self, self._root)
            self.data_section = Kafasat1.DataSectionT(self._io, self, self._root)


    class ModeT(KaitaiStruct):

        class ObcMode(Enum):
            normal = 2
            safe = 6

        class P60dockMode(Enum):
            critical = 1
            safe = 2
            normal = 3
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sys_mode = KaitaiStream.resolve_enum(Kafasat1.ModeT.ObcMode, self._io.read_u1())
            self.battery_mode = KaitaiStream.resolve_enum(Kafasat1.ModeT.P60dockMode, self._io.read_u1())


    class BatteryT(KaitaiStruct):

        class HeaterState(Enum):
            false = 0
            true = 1
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vbat = self._io.read_u2le()
            self.cbat = self._io.read_s2le()
            self.cbchg = self._io.read_s2le()
            self.st_5v = self._io.read_u2le()
            self.tbat1 = self._io.read_s2le()
            self.tbat2 = self._io.read_s2le()
            self.heater = KaitaiStream.resolve_enum(Kafasat1.BatteryT.HeaterState, self._io.read_u1())

        @property
        def temperature_bat1(self):
            if hasattr(self, '_m_temperature_bat1'):
                return self._m_temperature_bat1

            self._m_temperature_bat1 = (self.tbat1 * 0.1)
            return getattr(self, '_m_temperature_bat1', None)

        @property
        def temperature_bat2(self):
            if hasattr(self, '_m_temperature_bat2'):
                return self._m_temperature_bat2

            self._m_temperature_bat2 = (self.tbat2 * 0.1)
            return getattr(self, '_m_temperature_bat2', None)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ccsds_space_packet = Kafasat1.CcsdsSpacePacketT(self._io, self, self._root)



