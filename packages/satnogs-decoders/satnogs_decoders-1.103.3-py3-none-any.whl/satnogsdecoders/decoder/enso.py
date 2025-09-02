# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
import satnogsdecoders.process


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Enso(KaitaiStruct):
    """:field callsign: ax25_frame.ax25_header.dest_callsign_raw.callsign_ror.callsign
    :field ssid_mask: ax25_frame.ax25_header.dest_ssid_raw.ssid_mask
    :field ssid: ax25_frame.ax25_header.dest_ssid_raw.ssid
    :field src_callsign_raw_callsign: ax25_frame.ax25_header.src_callsign_raw.callsign_ror.callsign
    :field src_ssid_raw_ssid_mask: ax25_frame.ax25_header.src_ssid_raw.ssid_mask
    :field src_ssid_raw_ssid: ax25_frame.ax25_header.src_ssid_raw.ssid
    :field repeater_rpt_instance_rpt_callsign_raw_callsign: ax25_frame.ax25_header.repeater.rpt_instance.rpt_callsign_raw.callsign_ror.callsign
    :field repeater_rpt_instance_rpt_ssid_raw_ssid_mask: ax25_frame.ax25_header.repeater.rpt_instance.rpt_ssid_raw.ssid_mask
    :field repeater_rpt_instance_rpt_ssid_raw_ssid: ax25_frame.ax25_header.repeater.rpt_instance.rpt_ssid_raw.ssid
    :field ctl: ax25_frame.ax25_header.ctl
    :field pid: ax25_frame.payload.pid
    :field length: ax25_frame.payload.ax25_info.length
    :field frame_type: ax25_frame.payload.ax25_info.frame_type
    :field var_ts: ax25_frame.payload.ax25_info.var_ts
    :field obdh_timestamp: ax25_frame.payload.ax25_info.obdh_timestamp
    :field sat_mode: ax25_frame.payload.ax25_info.sat_mode
    :field obdh_mode: ax25_frame.payload.ax25_info.obdh_mode
    :field obdh_nb_bytes_to_transmit: ax25_frame.payload.ax25_info.obdh_nb_bytes_to_transmit
    :field obdh_nb_of_obdh_resets: ax25_frame.payload.ax25_info.obdh_nb_of_obdh_resets
    :field obdh_nb_of_errors: ax25_frame.payload.ax25_info.obdh_nb_of_errors
    :field eps_eps_mode: ax25_frame.payload.ax25_info.eps_eps_mode
    :field eps_bat_temp: ax25_frame.payload.ax25_info.eps_bat_temp
    :field eps_temp_z_minus: ax25_frame.payload.ax25_info.eps_temp_z_minus
    :field eps_obdh_cur: ax25_frame.payload.ax25_info.eps_obdh_cur
    :field eps_eps_cur: ax25_frame.payload.ax25_info.eps_eps_cur
    :field eps_ttc_micro_cur: ax25_frame.payload.ax25_info.eps_ttc_micro_cur
    :field eps_temp_x_plus: ax25_frame.payload.ax25_info.eps_temp_x_plus
    :field eps_temp_x_minus: ax25_frame.payload.ax25_info.eps_temp_x_minus
    :field eps_temp_y_plus: ax25_frame.payload.ax25_info.eps_temp_y_plus
    :field eps_temp_y_minus: ax25_frame.payload.ax25_info.eps_temp_y_minus
    :field eps_temp_z_plus: ax25_frame.payload.ax25_info.eps_temp_z_plus
    :field eps_temp_5v_reg: ax25_frame.payload.ax25_info.eps_temp_5v_reg
    :field eps_temp_6v_reg: ax25_frame.payload.ax25_info.eps_temp_6v_reg
    :field ttc_mode: ax25_frame.payload.ax25_info.ttc_mode
    :field ttc_resets: ax25_frame.payload.ax25_info.ttc_resets
    :field ttc_last_reset_cause: ax25_frame.payload.ax25_info.ttc_last_reset_cause
    :field ttc_total_valid_rcv_packets: ax25_frame.payload.ax25_info.ttc_total_valid_rcv_packets
    :field ttc_tx_packets: ax25_frame.payload.ax25_info.ttc_tx_packets
    :field ttc_power_fw_val: ax25_frame.payload.ax25_info.ttc_power_fw_val
    :field ttc_power_rev_val: ax25_frame.payload.ax25_info.ttc_power_rev_val
    :field ttc_last_err_code: ax25_frame.payload.ax25_info.ttc_last_err_code
    :field ttc_pwr_config: ax25_frame.payload.ax25_info.ttc_pwr_config
    :field ttc_pwr_amp_temp: ax25_frame.payload.ax25_info.ttc_pwr_amp_temp
    :field ttc_beacon_period: ax25_frame.payload.ax25_info.ttc_beacon_period
    :field tweet: ax25_frame.payload.ax25_info.tweet
    :field eps_bat_volt_val: ax25_frame.payload.ax25_info.eps_bat_volt_val
    :field eps_bat_volt_min_val: ax25_frame.payload.ax25_info.eps_bat_volt_min_val
    :field eps_bat_volt_max_val: ax25_frame.payload.ax25_info.eps_bat_volt_max_val
    :field eps_bat_volt_avg_val: ax25_frame.payload.ax25_info.eps_bat_volt_avg_val
    :field eps_avg_charge_cur_val: ax25_frame.payload.ax25_info.eps_avg_charge_cur_val
    :field eps_max_charge_cur_val: ax25_frame.payload.ax25_info.eps_max_charge_cur_val
    :field eps_ttc_tx_cur_val: ax25_frame.payload.ax25_info.eps_ttc_tx_cur_val
    :field eps_ttc_tx_cur_max_val: ax25_frame.payload.ax25_info.eps_ttc_tx_cur_max_val
    :field eps_pl_cur_val: ax25_frame.payload.ax25_info.eps_pl_cur_val
    :field eps_obdh_volt_val: ax25_frame.payload.ax25_info.eps_obdh_volt_val
    :field eps_ttc_volt_val: ax25_frame.payload.ax25_info.eps_ttc_volt_val
    :field eps_pl_volt_val: ax25_frame.payload.ax25_info.eps_pl_volt_val
    :field eps_mos1_volt_val: ax25_frame.payload.ax25_info.eps_mos1_volt_val
    :field eps_mos2_volt_val: ax25_frame.payload.ax25_info.eps_mos2_volt_val
    :field eps_mos3_volt_val: ax25_frame.payload.ax25_info.eps_mos3_volt_val
    :field eps_ref_volt_val: ax25_frame.payload.ax25_info.eps_ref_volt_val
    :field eps_ttc_mcu_volt_val: ax25_frame.payload.ax25_info.eps_ttc_mcu_volt_val
    :field ttc_rssi_last_packet_val: ax25_frame.payload.ax25_info.ttc_rssi_last_packet_val
    :field ttc_freq_dev_last_packet_val: ax25_frame.payload.ax25_info.ttc_freq_dev_last_packet_val
    :field temperature_val: ax25_frame.payload.ax25_info.temperature_val
    :field eps_charge_cur_val: ax25_frame.payload.ax25_info.eps_charge_cur_val
    :field payload: ax25_frame.payload.ax25_info.payload.payload_raw
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ax25_frame = Enso.Ax25Frame(self._io, self, self._root)

    class Ax25Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ax25_header = Enso.Ax25Header(self._io, self, self._root)
            _on = (self.ax25_header.ctl & 19)
            if _on == 0:
                self.payload = Enso.IFrame(self._io, self, self._root)
            elif _on == 3:
                self.payload = Enso.UiFrame(self._io, self, self._root)
            elif _on == 19:
                self.payload = Enso.UiFrame(self._io, self, self._root)
            elif _on == 16:
                self.payload = Enso.IFrame(self._io, self, self._root)
            elif _on == 18:
                self.payload = Enso.IFrame(self._io, self, self._root)
            elif _on == 2:
                self.payload = Enso.IFrame(self._io, self, self._root)


    class Ax25Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dest_callsign_raw = Enso.CallsignRaw(self._io, self, self._root)
            self.dest_ssid_raw = Enso.SsidMask(self._io, self, self._root)
            self.src_callsign_raw = Enso.CallsignRaw(self._io, self, self._root)
            self.src_ssid_raw = Enso.SsidMask(self._io, self, self._root)
            if (self.src_ssid_raw.ssid_mask & 1) == 0:
                self.repeater = Enso.Repeater(self._io, self, self._root)

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
            self.ax25_info = Enso.Ax25InfoData(_io__raw_ax25_info, self, self._root)


    class Callsign(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.callsign = (self._io.read_bytes(6)).decode(u"ASCII")
            if not  ((self.callsign == u"F4KJX ") or (self.callsign == u"FX6FRC")) :
                raise kaitaistruct.ValidationNotAnyOfError(self.callsign, self._io, u"/types/callsign/seq/0")


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
            self.ax25_info = Enso.Ax25InfoData(_io__raw_ax25_info, self, self._root)


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


    class PayloadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.payload_raw = (self._io.read_bytes(48)).decode(u"ASCII")


    class Repeaters(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.rpt_callsign_raw = Enso.CallsignRaw(self._io, self, self._root)
            self.rpt_ssid_raw = Enso.SsidMask(self._io, self, self._root)


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
                _ = Enso.Repeaters(self._io, self, self._root)
                self.rpt_instance.append(_)
                if (_.rpt_ssid_raw.ssid_mask & 1) == 1:
                    break
                i += 1


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
            self.callsign_ror = Enso.Callsign(_io__raw_callsign_ror, self, self._root)


    class Ax25InfoData(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = self._io.read_u1()
            self.frame_type = self._io.read_u1()
            if not self.frame_type == 16:
                raise kaitaistruct.ValidationNotEqualError(16, self.frame_type, self._io, u"/types/ax25_info_data/seq/1")
            self.var_ts = self._io.read_u4le()
            self.obdh_timestamp = self._io.read_u4le()
            self.temperature = self._io.read_u2le()
            self.sat_mode = self._io.read_u1()
            self.obdh_mode = self._io.read_u1()
            self.obdh_nb_bytes_to_transmit = self._io.read_u4le()
            self.obdh_nb_of_obdh_resets = self._io.read_u2le()
            self.obdh_nb_of_errors = self._io.read_u2le()
            self.eps_eps_mode = self._io.read_u1()
            self.eps_bat_volt = self._io.read_u1()
            self.eps_bat_temp = self._io.read_s1()
            self.eps_bat_volt_min = self._io.read_u1()
            self.eps_bat_volt_max = self._io.read_u1()
            self.eps_bat_volt_avg = self._io.read_u1()
            self.eps_avg_charge_cur = self._io.read_u1()
            self.eps_max_charge_cur = self._io.read_u1()
            self.eps_temp_z_minus = self._io.read_s1()
            self.eps_obdh_cur = self._io.read_u1()
            self.eps_eps_cur = self._io.read_u1()
            self.eps_ttc_micro_cur = self._io.read_u1()
            self.eps_ttc_tx_cur = self._io.read_u1()
            self.eps_ttc_tx_cur_max = self._io.read_u1()
            self.eps_pl_cur = self._io.read_u1()
            self.eps_charge_cur = self._io.read_u1()
            self.eps_temp_x_plus = self._io.read_s1()
            self.eps_temp_x_minus = self._io.read_s1()
            self.eps_temp_y_plus = self._io.read_s1()
            self.eps_temp_y_minus = self._io.read_s1()
            self.eps_temp_z_plus = self._io.read_s1()
            self.eps_obdh_volt = self._io.read_u1()
            self.eps_ttc_volt = self._io.read_u1()
            self.eps_pl_volt = self._io.read_u1()
            self.eps_mos1_volt = self._io.read_u1()
            self.eps_mos2_volt = self._io.read_u1()
            self.eps_mos3_volt = self._io.read_u1()
            self.eps_ref_volt = self._io.read_u2le()
            self.eps_temp_5v_reg = self._io.read_s1()
            self.eps_temp_6v_reg = self._io.read_s1()
            self.eps_ttc_mcu_volt = self._io.read_u1()
            self.ttc_mode = self._io.read_u1()
            self.ttc_resets = self._io.read_u2le()
            self.ttc_last_reset_cause = self._io.read_u1()
            self.ttc_total_valid_rcv_packets = self._io.read_u2le()
            self.ttc_tx_packets = self._io.read_u2le()
            self.ttc_power_fw = self._io.read_u1()
            self.ttc_power_rev = self._io.read_u1()
            self.ttc_last_err_code = self._io.read_u1()
            self.ttc_pwr_config = self._io.read_u1()
            self.ttc_pwr_amp_temp = self._io.read_s1()
            self.ttc_rssi_last_packet = self._io.read_u1()
            self.ttc_freq_dev_last_packet = self._io.read_s1()
            self.ttc_beacon_period = self._io.read_u1()
            self._raw__raw_payload = self._io.read_bytes(48)
            _process = satnogsdecoders.process.Hexl()
            self._raw_payload = _process.decode(self._raw__raw_payload)
            _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
            self.payload = Enso.PayloadT(_io__raw_payload, self, self._root)
            self.tweet = (self._io.read_bytes_full()).decode(u"utf-8")

        @property
        def eps_ttc_mcu_volt_val(self):
            if hasattr(self, '_m_eps_ttc_mcu_volt_val'):
                return self._m_eps_ttc_mcu_volt_val

            self._m_eps_ttc_mcu_volt_val = ((self.eps_ttc_mcu_volt * 10) + 4000)
            return getattr(self, '_m_eps_ttc_mcu_volt_val', None)

        @property
        def eps_ttc_tx_cur_max_val(self):
            if hasattr(self, '_m_eps_ttc_tx_cur_max_val'):
                return self._m_eps_ttc_tx_cur_max_val

            self._m_eps_ttc_tx_cur_max_val = (self.eps_ttc_tx_cur_max * 5)
            return getattr(self, '_m_eps_ttc_tx_cur_max_val', None)

        @property
        def ttc_rssi_last_packet_val(self):
            if hasattr(self, '_m_ttc_rssi_last_packet_val'):
                return self._m_ttc_rssi_last_packet_val

            self._m_ttc_rssi_last_packet_val = (self.ttc_rssi_last_packet * -1)
            return getattr(self, '_m_ttc_rssi_last_packet_val', None)

        @property
        def eps_charge_cur_val(self):
            if hasattr(self, '_m_eps_charge_cur_val'):
                return self._m_eps_charge_cur_val

            self._m_eps_charge_cur_val = (self.eps_charge_cur * 12)
            return getattr(self, '_m_eps_charge_cur_val', None)

        @property
        def eps_max_charge_cur_val(self):
            if hasattr(self, '_m_eps_max_charge_cur_val'):
                return self._m_eps_max_charge_cur_val

            self._m_eps_max_charge_cur_val = (self.eps_max_charge_cur * 12)
            return getattr(self, '_m_eps_max_charge_cur_val', None)

        @property
        def eps_ttc_tx_cur_val(self):
            if hasattr(self, '_m_eps_ttc_tx_cur_val'):
                return self._m_eps_ttc_tx_cur_val

            self._m_eps_ttc_tx_cur_val = (self.eps_ttc_tx_cur * 5)
            return getattr(self, '_m_eps_ttc_tx_cur_val', None)

        @property
        def temperature_val(self):
            if hasattr(self, '_m_temperature_val'):
                return self._m_temperature_val

            self._m_temperature_val = ((self.temperature * 0.0625) if self.temperature <= 4095 else ((self.temperature - 8192) * 0.0625))
            return getattr(self, '_m_temperature_val', None)

        @property
        def eps_ttc_volt_val(self):
            if hasattr(self, '_m_eps_ttc_volt_val'):
                return self._m_eps_ttc_volt_val

            self._m_eps_ttc_volt_val = ((self.eps_ttc_volt * 10) + 4000)
            return getattr(self, '_m_eps_ttc_volt_val', None)

        @property
        def eps_ref_volt_val(self):
            if hasattr(self, '_m_eps_ref_volt_val'):
                return self._m_eps_ref_volt_val

            self._m_eps_ref_volt_val = (self.eps_ref_volt * 0.805)
            return getattr(self, '_m_eps_ref_volt_val', None)

        @property
        def eps_bat_volt_max_val(self):
            if hasattr(self, '_m_eps_bat_volt_max_val'):
                return self._m_eps_bat_volt_max_val

            self._m_eps_bat_volt_max_val = (self.eps_bat_volt_max * 20)
            return getattr(self, '_m_eps_bat_volt_max_val', None)

        @property
        def ttc_power_rev_val(self):
            if hasattr(self, '_m_ttc_power_rev_val'):
                return self._m_ttc_power_rev_val

            self._m_ttc_power_rev_val = (self.ttc_power_rev * 10)
            return getattr(self, '_m_ttc_power_rev_val', None)

        @property
        def eps_mos2_volt_val(self):
            if hasattr(self, '_m_eps_mos2_volt_val'):
                return self._m_eps_mos2_volt_val

            self._m_eps_mos2_volt_val = ((self.eps_mos2_volt + 2200) * 0.805)
            return getattr(self, '_m_eps_mos2_volt_val', None)

        @property
        def eps_bat_volt_min_val(self):
            if hasattr(self, '_m_eps_bat_volt_min_val'):
                return self._m_eps_bat_volt_min_val

            self._m_eps_bat_volt_min_val = (self.eps_bat_volt_min * 20)
            return getattr(self, '_m_eps_bat_volt_min_val', None)

        @property
        def eps_bat_volt_avg_val(self):
            if hasattr(self, '_m_eps_bat_volt_avg_val'):
                return self._m_eps_bat_volt_avg_val

            self._m_eps_bat_volt_avg_val = (self.eps_bat_volt_avg * 20)
            return getattr(self, '_m_eps_bat_volt_avg_val', None)

        @property
        def eps_pl_cur_val(self):
            if hasattr(self, '_m_eps_pl_cur_val'):
                return self._m_eps_pl_cur_val

            self._m_eps_pl_cur_val = (self.eps_pl_cur * 5)
            return getattr(self, '_m_eps_pl_cur_val', None)

        @property
        def eps_obdh_volt_val(self):
            if hasattr(self, '_m_eps_obdh_volt_val'):
                return self._m_eps_obdh_volt_val

            self._m_eps_obdh_volt_val = ((self.eps_obdh_volt * 10) + 4000)
            return getattr(self, '_m_eps_obdh_volt_val', None)

        @property
        def eps_bat_volt_val(self):
            if hasattr(self, '_m_eps_bat_volt_val'):
                return self._m_eps_bat_volt_val

            self._m_eps_bat_volt_val = (self.eps_bat_volt * 20)
            return getattr(self, '_m_eps_bat_volt_val', None)

        @property
        def eps_mos1_volt_val(self):
            if hasattr(self, '_m_eps_mos1_volt_val'):
                return self._m_eps_mos1_volt_val

            self._m_eps_mos1_volt_val = ((self.eps_mos1_volt + 2200) * 0.805)
            return getattr(self, '_m_eps_mos1_volt_val', None)

        @property
        def eps_mos3_volt_val(self):
            if hasattr(self, '_m_eps_mos3_volt_val'):
                return self._m_eps_mos3_volt_val

            self._m_eps_mos3_volt_val = ((self.eps_mos3_volt + 2200) * 0.805)
            return getattr(self, '_m_eps_mos3_volt_val', None)

        @property
        def ttc_freq_dev_last_packet_val(self):
            if hasattr(self, '_m_ttc_freq_dev_last_packet_val'):
                return self._m_ttc_freq_dev_last_packet_val

            self._m_ttc_freq_dev_last_packet_val = (self.ttc_freq_dev_last_packet * 17)
            return getattr(self, '_m_ttc_freq_dev_last_packet_val', None)

        @property
        def ttc_power_fw_val(self):
            if hasattr(self, '_m_ttc_power_fw_val'):
                return self._m_ttc_power_fw_val

            self._m_ttc_power_fw_val = (self.ttc_power_fw * 10)
            return getattr(self, '_m_ttc_power_fw_val', None)

        @property
        def eps_avg_charge_cur_val(self):
            if hasattr(self, '_m_eps_avg_charge_cur_val'):
                return self._m_eps_avg_charge_cur_val

            self._m_eps_avg_charge_cur_val = (self.eps_avg_charge_cur * 12)
            return getattr(self, '_m_eps_avg_charge_cur_val', None)

        @property
        def eps_pl_volt_val(self):
            if hasattr(self, '_m_eps_pl_volt_val'):
                return self._m_eps_pl_volt_val

            self._m_eps_pl_volt_val = ((self.eps_pl_volt * 10) + 4000)
            return getattr(self, '_m_eps_pl_volt_val', None)



