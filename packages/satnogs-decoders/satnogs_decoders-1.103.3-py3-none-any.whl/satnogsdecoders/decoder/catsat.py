# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Catsat(KaitaiStruct):
    """:field type: packet.header.type
    
    :field bcn0_timestamp: packet.payload.hk_1_95.timestamp
    :field callsign: packet.payload.callsign
    :field motd: packet.payload.motd
    
    :field bcn1_timestamp: packet.payload.hk_1_4_1.timestamp
    :field obc_temp_mcu: packet.payload.obc_temp_mcu
    :field obc_boot_cnt: packet.payload.obc_boot_cnt
    :field obc_clock: packet.payload.obc_clock
    :field batt_vbatt: packet.payload.bpx_vbatt
    :field batt_temp_0: packet.payload.bpx_temp
    :field batt_boot_cnt: packet.payload.bpx_boot_cnt
    :field ax100_temp_brd: packet.payload.ax100_temp_brd
    :field ax100_boot_cnt: packet.payload.ax100_boot_cnt
    :field ax100_last_contact: packet.payload.ax100_last_contact
    :field p60_boot_cnt: packet.payload.p60_boot_cnt
    :field p60_batt_mode: packet.payload.p60_batt_mode
    :field p60_batt_v: packet.payload.p60_batt_v
    :field p60_batt_c: packet.payload.p60_batt_c
    :field pdu_x2_cout_obc: packet.payload.pdu_x2_cout.0
    :field pdu_x2_cout_hdcam: packet.payload.pdu_x2_cout.1
    :field pdu_x2_cout_ant_sel: packet.payload.pdu_x2_cout.2
    :field pdu_x2_cout_met_pwr: packet.payload.pdu_x2_cout.3
    :field pdu_x2_cout_wspr_dep: packet.payload.pdu_x2_cout.5
    :field pdu_x2_cout_asdr: packet.payload.pdu_x2_cout.6
    :field pdu_x2_cout_ax100: packet.payload.pdu_x2_cout.7
    :field pdu_x2_cout_inf_5v: packet.payload.pdu_x2_cout.8
    
    :field bcn2_timestamp: packet.payload.hk_10_4_2.timestamp
    :field pdu_x3_cout_hf_up: packet.payload.pdu_x3_cout.0
    :field pdu_x3_cout_xband: packet.payload.pdu_x3_cout.1
    :field pdu_x3_cout_adcs: packet.payload.pdu_x3_cout.2
    :field pdu_x3_cout_rwheels: packet.payload.pdu_x3_cout.3
    :field pdu_x3_cout_gyro: packet.payload.pdu_x3_cout.4
    :field pdu_x3_cout_met_sel: packet.payload.pdu_x3_cout.5
    :field pdu_x3_cout_inf_12v: packet.payload.pdu_x3_cout.6
    :field pdu_x3_cout_inf_3v: packet.payload.pdu_x3_cout.7
    :field acu_power_0: packet.payload.acu_power.0
    :field acu_power_1: packet.payload.acu_power.1
    :field acu_power_2: packet.payload.acu_power.2
    :field acu_power_3: packet.payload.acu_power.3
    :field acu_power_4: packet.payload.acu_power.4
    :field acu_power_5: packet.payload.acu_power.5
    :field adcs_boot_cnt: packet.payload.adcs_boot_cnt
    :field adcs_clock: packet.payload.adcs_clock
    :field extgyro_x: packet.payload.extgyro.0
    :field extgyro_y: packet.payload.extgyro.1
    :field extgyro_z: packet.payload.extgyro.2
    :field gps_pos_x: packet.payload.gps_pos.0
    :field gps_pos_y: packet.payload.gps_pos.1
    :field gps_pos_z: packet.payload.gps_pos.2
    :field gps_vel_x: packet.payload.gps_vel.0
    :field gps_vel_y: packet.payload.gps_vel.1
    :field gps_vel_z: packet.payload.gps_vel.2
    :field acs_mode: packet.payload.acs_mode
    :field status_extmag: packet.payload.status_extmag
    :field status_fss_xneg: packet.payload.status_fss.0
    :field status_fss_yneg: packet.payload.status_fss.1
    :field status_fss_zneg: packet.payload.status_fss.2
    :field status_fss_xpos: packet.payload.status_fss.3
    :field status_fss_ypos: packet.payload.status_fss.4
    :field status_extgyro: packet.payload.status_extgyro
    :field status_gps: packet.payload.status_gps
    
    :field bcn3_timestamp: packet.payload.hk_1_4_3.timestamp
    :field obc_fs_mnted: packet.payload.obc_fs_mnted
    :field obc_temp_ram: packet.payload.obc_temp_ram
    :field obc_resetcause: packet.payload.obc_resetcause
    :field obc_bootcause: packet.payload.obc_bootcause
    :field obc_uptime: packet.payload.obc_uptime
    :field batt_charge: packet.payload.batt_charge
    :field batt_dcharge: packet.payload.batt_dcharge
    :field batt_heater: packet.payload.batt_heater
    :field batt_temp_1: packet.payload.batt_temp2
    :field batt_temp_2: packet.payload.batt_temp3
    :field batt_temp_3: packet.payload.batt_temp4
    :field batt_bootcause: packet.payload.batt_bootcause
    :field sat_temps_met_cam: packet.payload.sat_temps.0
    :field sat_temps_hd_cam: packet.payload.sat_temps.1
    :field sat_temps_asdr: packet.payload.sat_temps.2
    :field sat_temps_xband: packet.payload.sat_temps.3
    :field sat_temps_rad_y: packet.payload.sat_temps.4
    :field sat_temps_rad_z: packet.payload.sat_temps.5
    :field ax100_reboot_in: packet.payload.ax100_reboot_in
    :field ax100_tx_inhibit: packet.payload.ax100_tx_inhibit
    :field ax100_rx_freq: packet.payload.ax100_rx_freq
    :field ax100_rx_baud: packet.payload.ax100_rx_baud
    :field ax100_temp_pa: packet.payload.ax100_temp_pa
    :field ax100_last_rssi: packet.payload.ax100_last_rssi
    :field ax100_active_conf: packet.payload.ax100_active_conf
    :field ax100_bootcause: packet.payload.ax100_bootcause
    :field ax100_bgnd_rssi: packet.payload.ax100_bgnd_rssi
    :field ax100_tx_duty: packet.payload.ax100_tx_duty
    :field ax100_tx_freq: packet.payload.ax100_tx_freq
    :field ax100_tx_baud: packet.payload.ax100_tx_baud
    
    :field bcn4_timestamp: packet.payload.hk_8_4_4.timestamp
    :field p60_cout_acu_x1_vcc: packet.payload.p60_cout.0
    :field p60_cout_pdu_x2_vcc: packet.payload.p60_cout.1
    :field p60_cout_pdu_x3_vcc: packet.payload.p60_cout.2
    :field p60_cout_acu_x1_vbatt: packet.payload.p60_cout.4
    :field p60_cout_pdu_x2_vbatt: packet.payload.p60_cout.5
    :field p60_cout_pdu_x3_vbatt: packet.payload.p60_cout.6
    :field p60_cout_stk_vbatt: packet.payload.p60_cout.8
    :field p60_cout_stk_3v: packet.payload.p60_cout.9
    :field p60_cout_stk_5v: packet.payload.p60_cout.10
    :field p60_cout_gssb_3v: packet.payload.p60_cout.11
    :field p60_cout_gssb_5v: packet.payload.p60_cout.12
    :field p60_out_en_acu_x1_vcc: packet.payload.p60_out_en.0
    :field p60_out_en_pdu_x2_vcc: packet.payload.p60_out_en.1
    :field p60_out_en_pdu_x3_vcc: packet.payload.p60_out_en.2
    :field p60_out_en_acu_x1_vbatt: packet.payload.p60_out_en.4
    :field p60_out_en_pdu_x2_vbatt: packet.payload.p60_out_en.5
    :field p60_out_en_pdu_x3_vbatt: packet.payload.p60_out_en.6
    :field p60_out_en_stk_vbatt:packet.payload.p60_out_en.8
    :field p60_out_en_stk_3v: packet.payload.p60_out_en.9
    :field p60_out_en_stk_5v: packet.payload.p60_out_en.10
    :field p60_out_en_gssb_3v: packet.payload.p60_out_en.11
    :field p60_out_en_gssb_5v: packet.payload.p60_out_en.12
    :field p60_temp_0: packet.payload.p60_temp.0
    :field p60_temp_1: packet.payload.p60_temp.1
    :field p60_bootcause: packet.payload.p60_bootcause
    :field p60_uptime: packet.payload.p60_uptime
    :field p60_resetcause: packet.payload.p60_resetcause
    :field p60_latchup_acu_x1_vcc: packet.payload.p60_latchup.0
    :field p60_latchup_pdu_x2_vcc: packet.payload.p60_latchup.1
    :field p60_latchup_pdu_x3_vcc: packet.payload.p60_latchup.2
    :field p60_latchup_acu_x1_vbatt:  packet.payload.p60_latchup.4
    :field p60_latchup_pdu_x2_vbatt:  packet.payload.p60_latchup.5
    :field p60_latchup_pdu_x3_vbatt:  packet.payload.p60_latchup.6
    :field p60_latchup_stk_vbatt: packet.payload.p60_latchup.8
    :field p60_latchup_stk_3v: packet.payload.p60_latchup.9
    :field p60_latchup_stk_5v: packet.payload.p60_latchup.10
    :field p60_latchup_gssb_3v: packet.payload.p60_latchup.11
    :field p60_latchup_gssb_5v: packet.payload.p60_latchup.12
    :field p60_vcc_c: packet.payload.p60_vcc_c
    :field p60_batt_v: packet.payload.p60_batt_v
    :field p60_dearm_status: packet.payload.p60_dearm_status
    :field p60_wdt_cnt_gnd: packet.payload.p60_wdt_cnt_gnd
    :field p60_wdt_cnt_can: packet.payload.p60_wdt_cnt_can
    :field p60_wdt_cnt_left: packet.payload.p60_wdt_cnt_left
    :field p60_batt_chrg: packet.payload.p60_batt_chrg
    :field p60_batt_dchrg: packet.payload.p60_batt_dchrg
    :field ant6_depl: packet.payload.ant6_depl
    :field ar6_depl: packet.payload.ar6_depl
    :field pdu_x2_vout_obc: packet.payload.pdu_x2_vout.0
    :field pdu_x2_vout_hdcam: packet.payload.pdu_x2_vout.1
    :field pdu_x2_vout_ant_sel: packet.payload.pdu_x2_vout.2
    :field pdu_x2_vout_met_pwr: packet.payload.pdu_x2_vout.3
    :field pdu_x2_vout_wspr_dep: packet.payload.pdu_x2_vout.5
    :field pdu_x2_vout_asdr: packet.payload.pdu_x2_vout.6
    :field pdu_x2_vout_ax100: packet.payload.pdu_x2_vout.7
    :field pdu_x2_vout_inf_5v: packet.payload.pdu_x2_vout.8
    :field pdu_x2_temp: packet.payload.pdu_x2_temp
    :field pdu_x2_out_en_obc: packet.payload.pdu_x2_out_en.0
    :field pdu_x2_out_en_hdcam: packet.payload.pdu_x2_out_en.1
    :field pdu_x2_out_en_ant_sel: packet.payload.pdu_x2_out_en.2
    :field pdu_x2_out_en_met_pwr: packet.payload.pdu_x2_out_en.3
    :field pdu_x2_out_en_wspr_dep: packet.payload.pdu_x2_out_en.5
    :field pdu_x2_out_en_asdr: packet.payload.pdu_x2_out_en.6
    :field pdu_x2_out_en_ax100: packet.payload.pdu_x2_out_en.7
    :field pdu_x2_out_en_inf_5v: packet.payload.pdu_x2_out_en.8
    :field pdu_x2_bootcause: packet.payload.pdu_x2_bootcause
    :field pdu_x2_boot_cnt: packet.payload.pdu_x2_boot_cnt
    :field pdu_x2_uptime: packet.payload.pdu_x2_uptime
    :field pdu_x2_resetcause: packet.payload.pdu_x2_resetcause
    :field pdu_x2_latchup_obc: packet.payload.pdu_x2_latchup.0
    :field pdu_x2_latchup_hdcam: packet.payload.pdu_x2_latchup.1
    :field pdu_x2_latchup_ant_sel: packet.payload.pdu_x2_latchup.2
    :field pdu_x2_latchup_met_pwr: packet.payload.pdu_x2_latchup.3
    :field pdu_x2_latchup_wspr_dep: packet.payload.pdu_x2_latchup.5
    :field pdu_x2_latchup_asdr: packet.payload.pdu_x2_latchup.6
    :field pdu_x2_latchup_ax100: packet.payload.pdu_x2_latchup.7
    :field pdu_x2_latchup_inf_5v: packet.payload.pdu_x2_latchup.8
    
    :field bcn5_timestamp: packet.payload.hk_10_4_5.timestamp
    :field pdu_x3_vout_hf_up: packet.payload.pdu_x3_vout.0
    :field pdu_x3_vout_xband: packet.payload.pdu_x3_vout.1
    :field pdu_x3_vout_adcs: packet.payload.pdu_x3_vout.2
    :field pdu_x3_vout_rwheels: packet.payload.pdu_x3_vout.3
    :field pdu_x3_vout_gyro: packet.payload.pdu_x3_vout.4
    :field pdu_x3_vout_met_sel: packet.payload.pdu_x3_vout.5
    :field pdu_x3_vout_inf_12v: packet.payload.pdu_x3_vout.6
    :field pdu_x3_vout_inf_3v: packet.payload.pdu_x3_vout.7
    :field pdu_x3_temp: packet.payload.pdu_x3_temp
    :field pdu_x3_out_en_hf_up: packet.payload.pdu_x3_out_en.0
    :field pdu_x3_out_en_xband: packet.payload.pdu_x3_out_en.1
    :field pdu_x3_out_en_adcs: packet.payload.pdu_x3_out_en.2
    :field pdu_x3_out_en_rwheels: packet.payload.pdu_x3_out_en.3
    :field pdu_x3_out_en_gyro: packet.payload.pdu_x3_out_en.4
    :field pdu_x3_out_en_met_sel: packet.payload.pdu_x3_out_en.5
    :field pdu_x3_out_en_inf_12v: packet.payload.pdu_x3_out_en.6
    :field pdu_x3_out_en_inf_3v: packet.payload.pdu_x3_out_en.7
    :field pdu_x3_bootcause: packet.payload.pdu_x3_bootcause
    :field pdu_x3_boot_cnt: packet.payload.pdu_x3_boot_cnt
    :field pdu_x3_uptime: packet.payload.pdu_x3_uptime
    :field pdu_x3_resetcause: packet.payload.pdu_x3_resetcause
    :field pdu_x3_latchup_hf_up: packet.payload.pdu_x3_latchup.0
    :field pdu_x3_latchup_xband: packet.payload.pdu_x3_latchup.1
    :field pdu_x3_latchup_adcs: packet.payload.pdu_x3_latchup.2
    :field pdu_x3_latchup_rwheels: packet.payload.pdu_x3_latchup.3
    :field pdu_x3_latchup_gyro: packet.payload.pdu_x3_latchup.4
    :field pdu_x3_latchup_met_sel: packet.payload.pdu_x3_latchup.5
    :field pdu_x3_latchup_inf_12v: packet.payload.pdu_x3_latchup.6
    :field pdu_x3_latchup_inf_3v: packet.payload.pdu_x3_latchup.7
    :field acu_cin_0: packet.payload.acu_cin.0
    :field acu_cin_1: packet.payload.acu_cin.1
    :field acu_cin_2: packet.payload.acu_cin.2
    :field acu_cin_3: packet.payload.acu_cin.3
    :field acu_cin_4: packet.payload.acu_cin.4
    :field acu_cin_5: packet.payload.acu_cin.5
    :field acu_vin_0: packet.payload.acu_vin.0
    :field acu_vin_1: packet.payload.acu_vin.1
    :field acu_vin_2: packet.payload.acu_vin.2
    :field acu_vin_3: packet.payload.acu_vin.3
    :field acu_vin_4: packet.payload.acu_vin.4
    :field acu_vin_5: packet.payload.acu_vin.5
    :field acu_vbatt: packet.payload.acu_vbatt
    :field acu_temp_0: packet.payload.acu_temp.0
    :field acu_temp_1: packet.payload.acu_temp.1
    :field acu_temp_2: packet.payload.acu_temp.2
    :field acu_mppt_mode: packet.payload.acu_mppt_mode
    :field acu_vboost_0: packet.payload.acu_vboost.0
    :field acu_vboost_1: packet.payload.acu_vboost.1
    :field acu_vboost_2: packet.payload.acu_vboost.2
    :field acu_vboost_3: packet.payload.acu_vboost.3
    :field acu_vboost_4: packet.payload.acu_vboost.4
    :field acu_vboost_5: packet.payload.acu_vboost.5
    :field acu_bootcause: packet.payload.acu_bootcause
    :field acu_boot_cnt: packet.payload.acu_boot_cnt
    :field acu_uptime: packet.payload.acu_uptime
    :field acu_resetcause: packet.payload.acu_resetcause
    
    :field bcn6_timestamp: packet.payload.hk_1_96_6.timestamp
    :field ant_1_brn: packet.payload.ant_1_brn
    :field ant_2_brn: packet.payload.ant_2_brn
    :field ant_3_brn: packet.payload.ant_3_brn
    :field ant_4_brn: packet.payload.ant_4_brn
    :field ant_1_rel: packet.payload.ant_1_rel
    :field ant_2_rel: packet.payload.ant_2_rel
    :field ant_3_rel: packet.payload.ant_3_rel
    :field ant_4_rel: packet.payload.ant_4_rel
    :field dsp_1_brn: packet.payload.dsp_1_brn
    :field dsp_2_brn: packet.payload.dsp_2_brn
    :field dsp_1_rel: packet.payload.dsp_1_rel
    :field dsp_2_rel: packet.payload.dsp_2_rel
    
    :field bcn7_timestamp: packet.payload.hk_4_150_7.timestamp
    :field extmag_x: packet.payload.extmag.0
    :field extmag_y: packet.payload.extmag.1
    :field extmag_z: packet.payload.extmag.2
    :field torquer_duty_x: packet.payload.torquer_duty.0
    :field torquer_duty_y: packet.payload.torquer_duty.1
    :field torquer_duty_z: packet.payload.torquer_duty.2
    :field bdot_rate_filter1: packet.payload.bdot_rate.0
    :field bdot_rate_filter2: packet.payload.bdot_rate.1
    :field bdot_dmag_x: packet.payload.bdot_dmag.0
    :field bdot_dmag_y: packet.payload.bdot_dmag.1
    :field bdot_dmag_z: packet.payload.bdot_dmag.2
    :field bdot_torquer_x: packet.payload.bdot_torquer.0
    :field bdot_torquer_y: packet.payload.bdot_torquer.1
    :field bdot_torquer_z: packet.payload.bdot_torquer.2
    :field bdot_detumble: packet.payload.bdot_detumble
    :field ctrl_refq_0: packet.payload.ctrl_refq.0
    :field ctrl_refq_1: packet.payload.ctrl_refq.1
    :field ctrl_refq_2: packet.payload.ctrl_refq.2
    :field ctrl_refq_3: packet.payload.ctrl_refq.3
    :field ctrl_errq_0: packet.payload.ctrl_errq.0
    :field ctrl_errq_1: packet.payload.ctrl_errq.1
    :field ctrl_errq_2: packet.payload.ctrl_errq.2
    :field ctrl_errq_3: packet.payload.ctrl_errq.3
    :field ctrl_m_x: packet.payload.ctrl_m.0
    :field ctrl_m_y: packet.payload.ctrl_m.1
    :field ctrl_m_z: packet.payload.ctrl_m.2
    :field ctrl_mwspeed_0: packet.payload.ctrl_mwspeed.0
    :field ctrl_mwspeed_1: packet.payload.ctrl_mwspeed.1
    :field ctrl_mwspeed_2: packet.payload.ctrl_mwspeed.2
    :field ctrl_mwspeed_3: packet.payload.ctrl_mwspeed.3
    :field ctrl_euleroff_x: packet.payload.ctrl_euleroff.0
    :field ctrl_euleroff_y: packet.payload.ctrl_euleroff.1
    :field ctrl_euleroff_z: packet.payload.ctrl_euleroff.2
    :field ctrl_btorque_x: packet.payload.ctrl_btorque.0
    :field ctrl_btorque_y: packet.payload.ctrl_btorque.1
    :field ctrl_btorque_z: packet.payload.ctrl_btorque.2
    
    :field bcn11_timestamp: packet.payload.hk_4_150_11.timestamp
    :field extmag_x: packet.payload.extmag.0
    :field extmag_y: packet.payload.extmag.1
    :field extmag_z: packet.payload.extmag.2
    :field extmag_temp: packet.payload.extmag_temp
    :field extmag_valid: packet.payload.extmag_valid
    :field suns_xneg: packet.payload.suns.0
    :field suns_yneg: packet.payload.suns.1
    :field suns_xpos: packet.payload.suns.3
    :field suns_ypos: packet.payload.suns.4
    :field suns_zpos: packet.payload.suns.5
    :field suns_temp_xneg: packet.payload.suns_temp.0
    :field suns_temp_yneg: packet.payload.suns_temp.1
    :field suns_temp_xpos: packet.payload.suns_temp.3
    :field suns_temp_ypos: packet.payload.suns_temp.4
    :field suns_temp_zpos: packet.payload.suns_temp.5
    :field suns_valid: packet.payload.suns_valid
    :field extgyro_x: packet.payload.extgyro.0
    :field extgyro_y: packet.payload.extgyro.1
    :field extgyro_z: packet.payload.extgyro.2
    :field extgyro_temp: packet.payload.extgyro_temp
    :field extgyro_valid: packet.payload.extgyro_valid
    :field fss_xneg_x: packet.payload.fss.0
    :field fss_xneg_y: packet.payload.fss.1
    :field fss_xneg_z: packet.payload.fss.2
    :field fss_yneg_x: packet.payload.fss.3
    :field fss_yneg_y: packet.payload.fss.4
    :field fss_yneg_z: packet.payload.fss.5
    :field fss_zneg_x: packet.payload.fss.6
    :field fss_zneg_y: packet.payload.fss.7
    :field fss_zneg_z: packet.payload.fss.8
    :field fss_xpos_x: packet.payload.fss.9
    :field fss_xpos_y: packet.payload.fss.10
    :field fss_xpos_z: packet.payload.fss.11
    :field fss_ypos_x: packet.payload.fss.12
    :field fss_ypos_y: packet.payload.fss.13
    :field fss_ypos_z: packet.payload.fss.14
    :field fss_temp: packet.payload.fss_temp
    :field fss_valid_xneg: packet.payload.fss_valid.0
    :field fss_valid_yneg: packet.payload.fss_valid.1
    :field fss_valid_zneg: packet.payload.fss_valid.2
    :field fss_valid_xpos: packet.payload.fss_valid.3
    :field fss_valid_ypos: packet.payload.fss_valid.4
    :field gps_pos_x: packet.payload.gps_pos.0
    :field gps_pos_y: packet.payload.gps_pos.1
    :field gps_pos_z: packet.payload.gps_pos.2
    :field gps_vel_x: packet.payload.gps_vel.0
    :field gps_vel_y: packet.payload.gps_vel.1
    :field gps_vel_z: packet.payload.gps_vel.2
    :field gps_epoch: packet.payload.gps_epoch
    :field gps_valid: packet.payload.gps_valid
    :field gps_sat: packet.payload.gps_sat
    :field gps_satsol: packet.payload.gps_satsol
    :field pps_unix: packet.payload.pps_unix
    
    :field bcn12_timestamp: packet.payload.hk_4_150_12.timestamp
    :field wheel_torque_0: packet.payload.wheel_torque.0
    :field wheel_torque_1: packet.payload.wheel_torque.1
    :field wheel_torque_2: packet.payload.wheel_torque.2
    :field wheel_torque_3: packet.payload.wheel_torque.3
    :field wheel_momentum_0: packet.payload.wheel_momentum.0
    :field wheel_momentum_1: packet.payload.wheel_momentum.1
    :field wheel_momentum_2: packet.payload.wheel_momentum.2
    :field wheel_momentum_3: packet.payload.wheel_momentum.3
    :field wheel_speed_0: packet.payload.wheel_speed.0
    :field wheel_speed_1: packet.payload.wheel_speed.1
    :field wheel_speed_2: packet.payload.wheel_speed.2
    :field wheel_speed_3: packet.payload.wheel_speed.3
    :field wheel_enable_0: packet.payload.wheel_enable.0
    :field wheel_enable_1: packet.payload.wheel_enable.1
    :field wheel_enable_2: packet.payload.wheel_enable.2
    :field wheel_enable_3: packet.payload.wheel_enable.3
    :field wheel_current_0: packet.payload.wheel_current.0
    :field wheel_current_1: packet.payload.wheel_current.1
    :field wheel_current_2: packet.payload.wheel_current.2
    :field wheel_current_3: packet.payload.wheel_current.3
    :field torquer_duty_x: packet.payload.torquer_duty.0
    :field torquer_duty_y: packet.payload.torquer_duty.1
    :field torquer_duty_z: packet.payload.torquer_duty.2
    :field torquer_calib_x: packet.payload.torquer_calib.0
    :field torquer_calib_y: packet.payload.torquer_calib.1
    :field torquer_calib_z: packet.payload.torquer_calib.2
    :field acs_mode: packet.payload.acs_mode
    :field acs_dmode: packet.payload.acs_dmode
    :field ads_mode: packet.payload.ads_mode
    :field ads_dmode: packet.payload.ads_dmode
    :field ephem_mode: packet.payload.ephem_mode
    :field ephem_dmode: packet.payload.ephem_dmode
    :field spin_mode: packet.payload.spin_mode
    :field status_mag: packet.payload.status_mag
    :field status_extmag: packet.payload.status_extmag
    :field status_css: packet.payload.status_css
    :field status_fss_xneg: packet.payload.status_fss.0
    :field status_fss_yneg: packet.payload.status_fss.1
    :field status_fss_zneg: packet.payload.status_fss.2
    :field status_fss_xpos: packet.payload.status_fss.3
    :field status_fss_ypos: packet.payload.status_fss.4
    :field status_gyro: packet.payload.status_gyro
    :field status_extgyro: packet.payload.status_extgyro
    :field status_gps: packet.payload.status_gps
    :field status_bdot: packet.payload.status_bdot
    :field status_ukf: packet.payload.status_ukf
    :field status_etime: packet.payload.status_etime
    :field status_ephem: packet.payload.status_ephem
    :field status_run: packet.payload.status_run
    :field looptime: packet.payload.looptime
    :field max_looptime: packet.payload.max_looptime
    :field bdot_rate_filter1: packet.payload.bdot_rate.0
    :field bdot_rate_filter2: packet.payload.bdot_rate.1
    :field bdot_dmag_x: packet.payload.bdot_dmag.0
    :field bdot_dmag_y: packet.payload.bdot_dmag.1
    :field bdot_dmag_z: packet.payload.bdot_dmag.2
    :field bdot_torquer_x: packet.payload.bdot_torquer.0
    :field bdot_torquer_y: packet.payload.bdot_torquer.1
    :field bdot_torquer_z: packet.payload.bdot_torquer.2
    :field bdot_detumble: packet.payload.bdot_detumble
    
    :field bcn13_timestamp: packet.payload.hk_4_152_13.timestamp
    :field ukf_x_0: packet.payload.ukf_x.0
    :field ukf_x_1: packet.payload.ukf_x.1
    :field ukf_x_2: packet.payload.ukf_x.2
    :field ukf_x_3: packet.payload.ukf_x.3
    :field ukf_x_4: packet.payload.ukf_x.4
    :field ukf_x_5: packet.payload.ukf_x.5
    :field ukf_x_6: packet.payload.ukf_x.6
    :field ukf_x_7: packet.payload.ukf_x.7
    :field ukf_x_8: packet.payload.ukf_x.8
    :field ukf_x_9: packet.payload.ukf_x.9
    :field ukf_x_10: packet.payload.ukf_x.10
    :field ukf_x_11: packet.payload.ukf_x.11
    :field ukf_x_12: packet.payload.ukf_x.12
    :field ukf_q_0: packet.payload.ukf_q.0
    :field ukf_q_1: packet.payload.ukf_q.1
    :field ukf_q_2: packet.payload.ukf_q.2
    :field ukf_q_3: packet.payload.ukf_q.3
    :field ukf_w_0: packet.payload.ukf_w.0
    :field ukf_w_1: packet.payload.ukf_w.1
    :field ukf_w_2: packet.payload.ukf_w.2
    :field ukf_xpred_0: packet.payload.ukf_xpred.0
    :field ukf_xpred_1: packet.payload.ukf_xpred.1
    :field ukf_xpred_2: packet.payload.ukf_xpred.2
    :field ukf_xpred_3: packet.payload.ukf_xpred.3
    :field ukf_xpred_4: packet.payload.ukf_xpred.4
    :field ukf_xpred_5: packet.payload.ukf_xpred.5
    :field ukf_xpred_6: packet.payload.ukf_xpred.6
    :field ukf_xpred_7: packet.payload.ukf_xpred.7
    :field ukf_xpred_8: packet.payload.ukf_xpred.8
    :field ukf_xpred_9: packet.payload.ukf_xpred.9
    :field ukf_xpred_10: packet.payload.ukf_xpred.10
    :field ukf_xpred_11: packet.payload.ukf_xpred.11
    :field ukf_xpred_12: packet.payload.ukf_xpred.12
    :field ukf_zpred_0: packet.payload.ukf_zpred.0
    :field ukf_zpred_1: packet.payload.ukf_zpred.1
    :field ukf_zpred_2: packet.payload.ukf_zpred.2
    :field ukf_zpred_3: packet.payload.ukf_zpred.3
    :field ukf_zpred_4: packet.payload.ukf_zpred.4
    :field ukf_zpred_5: packet.payload.ukf_zpred.5
    :field ukf_zpred_6: packet.payload.ukf_zpred.6
    :field ukf_zpred_7: packet.payload.ukf_zpred.7
    :field ukf_zpred_8: packet.payload.ukf_zpred.8
    :field ukf_zpred_9: packet.payload.ukf_zpred.9
    :field ukf_zpred_10: packet.payload.ukf_zpred.10
    :field ukf_zpred_11: packet.payload.ukf_zpred.11
    
    :field bcn14_timestamp: packet.payload.hk_4_152_14.timestamp
    :field ukf_z_0: packet.payload.ukf_z.0
    :field ukf_z_1: packet.payload.ukf_z.1
    :field ukf_z_2: packet.payload.ukf_z.2
    :field ukf_z_3: packet.payload.ukf_z.3
    :field ukf_z_4: packet.payload.ukf_z.4
    :field ukf_z_5: packet.payload.ukf_z.5
    :field ukf_z_6: packet.payload.ukf_z.6
    :field ukf_z_7: packet.payload.ukf_z.7
    :field ukf_z_8: packet.payload.ukf_z.8
    :field ukf_z_9: packet.payload.ukf_z.9
    :field ukf_z_10: packet.payload.ukf_z.10
    :field ukf_z_11: packet.payload.ukf_z.11
    :field ukf_enable_0: packet.payload.ukf_enable.0
    :field ukf_enable_1: packet.payload.ukf_enable.1
    :field ukf_enable_2: packet.payload.ukf_enable.2
    :field ukf_enable_3: packet.payload.ukf_enable.3
    :field ukf_enable_4: packet.payload.ukf_enable.4
    :field ukf_enable_5: packet.payload.ukf_enable.5
    :field ukf_enable_6: packet.payload.ukf_enable.6
    :field ukf_enable_7: packet.payload.ukf_enable.7
    :field ukf_enable_8: packet.payload.ukf_enable.8
    :field ukf_enable_9: packet.payload.ukf_enable.9
    :field ukf_enable_10: packet.payload.ukf_enable.10
    :field ukf_enable_11: packet.payload.ukf_enable.11
    :field ukf_sunmax_0: packet.payload.ukf_sunmax.0
    :field ukf_sunmax_1: packet.payload.ukf_sunmax.1
    :field ukf_sunmax_2: packet.payload.ukf_sunmax.2
    :field ukf_sunmax_3: packet.payload.ukf_sunmax.3
    :field ukf_sunmax_4: packet.payload.ukf_sunmax.4
    :field ukf_sunmax_5: packet.payload.ukf_sunmax.5
    :field ukf_in_ecl: packet.payload.ukf_in_eclipse
    :field ukf_choice: packet.payload.ukf_choice
    :field ukf_ctrl_t_0: packet.payload.ukf_ctrl_t.0
    :field ukf_ctrl_t_1: packet.payload.ukf_ctrl_t.1
    :field ukf_ctrl_t_2: packet.payload.ukf_ctrl_t.2
    :field ukf_ctrl_m_0: packet.payload.ukf_ctrl_m.0
    :field ukf_ctrl_m_1: packet.payload.ukf_ctrl_m.1
    :field ukf_ctrl_m_2: packet.payload.ukf_ctrl_m.2
    :field ukf_rate_x: packet.payload.ukf_rate.0
    :field ukf_rate_y: packet.payload.ukf_rate.1
    :field ukf_rate_z: packet.payload.ukf_rate.2
    
    :field bcn15_timestamp: packet.payload.hk_4_153_15.timestamp
    :field ephem_jdat: packet.payload.ephem_jdat
    :field ephem_reci_0: packet.payload.ephem_reci.0
    :field ephem_reci_1: packet.payload.ephem_reci.1
    :field ephem_reci_2: packet.payload.ephem_reci.2
    :field ephem_veci_0: packet.payload.ephem_veci.0
    :field ephem_veci_1: packet.payload.ephem_veci.1
    :field ephem_veci_2: packet.payload.ephem_veci.2
    :field ephem_sun_eci_x: packet.payload.ephem_sun_eci.0
    :field ephem_sun_eci_y: packet.payload.ephem_sun_eci.1
    :field ephem_sun_eci_z: packet.payload.ephem_sun_eci.2
    :field ephem_quat_ie_0: packet.payload.ephem_quat_ie.0
    :field ephem_quat_ie_1: packet.payload.ephem_quat_ie.1
    :field ephem_quat_ie_2: packet.payload.ephem_quat_ie.2
    :field ephem_quat_ie_3: packet.payload.ephem_quat_ie.3
    :field ephem_quat_io_0: packet.payload.ephem_quat_io.0
    :field ephem_quat_io_1: packet.payload.ephem_quat_io.1
    :field ephem_quat_io_2: packet.payload.ephem_quat_io.2
    :field ephem_quat_io_3: packet.payload.ephem_quat_io.3
    :field ephem_quat_il_0: packet.payload.ephem_quat_il.0
    :field ephem_quat_il_1: packet.payload.ephem_quat_il.1
    :field ephem_quat_il_2: packet.payload.ephem_quat_il.2
    :field ephem_quat_il_3: packet.payload.ephem_quat_il.3
    :field ephem_rate_io_x: packet.payload.ephem_rate_io.0
    :field ephem_rate_io_y: packet.payload.ephem_rate_io.1
    :field ephem_rate_io_z: packet.payload.ephem_rate_io.2
    :field ephem_rate_il_x: packet.payload.ephem_rate_il.0
    :field ephem_rate_il_y: packet.payload.ephem_rate_il.1
    :field ephem_rate_il_z: packet.payload.ephem_rate_il.2
    :field ephem_t_eclipse: packet.payload.ephem_t_eclipse
    :field ephem_time: packet.payload.ephem_time
    
    :field bcn16_timestamp: packet.payload.hk_4_1_16.timestamp
    :field ads_time: packet.payload.ads_time
    :field acs_time: packet.payload.acs_time
    :field sens_time: packet.payload.sens_time
    :field adcs_swload_cnt1: packet.payload.adcs_swload_cnt1
    :field adcs_fs_mounted: packet.payload.adcs_fs_mounted
    :field adcs_temp_mcu: packet.payload.adcs_temp_mcu
    :field adcs_temp_ram: packet.payload.adcs_temp_ram
    :field adcs_resetcause: packet.payload.adcs_resetcause
    :field adcs_bootcause: packet.payload.adcs_bootcause
    :field adcs_boot_cnt: packet.payload.adcs_boot_cnt
    :field adcs_clock: packet.payload.adcs_clock
    :field adcs_uptime: packet.payload.adcs_uptime
    
    :field bcn17_timestamp: packet.payload.hk_4_154_17.timestamp
    :field ctrl_refq_0: packet.payload.ctrl_refq.0
    :field ctrl_refq_1: packet.payload.ctrl_refq.1
    :field ctrl_refq_2: packet.payload.ctrl_refq.2
    :field ctrl_refq_3: packet.payload.ctrl_refq.3
    :field ctrl_errq_0: packet.payload.ctrl_errq.0
    :field ctrl_errq_1: packet.payload.ctrl_errq.1
    :field ctrl_errq_2: packet.payload.ctrl_errq.2
    :field ctrl_errq_3: packet.payload.ctrl_errq.3
    :field ctrl_errrate_x: packet.payload.ctrl_errrate.0
    :field ctrl_errrate_y: packet.payload.ctrl_errrate.1
    :field ctrl_errrate_z: packet.payload.ctrl_errrate.2
    :field ctrl_m_x: packet.payload.ctrl_m.0
    :field ctrl_m_y: packet.payload.ctrl_m.1
    :field ctrl_m_z: packet.payload.ctrl_m.2
    :field ctrl_mwtorque_0: packet.payload.ctrl_mwtorque.0
    :field ctrl_mwtorque_1: packet.payload.ctrl_mwtorque.1
    :field ctrl_mwtorque_2: packet.payload.ctrl_mwtorque.2
    :field ctrl_mwtorque_3: packet.payload.ctrl_mwtorque.3
    :field ctrl_mwspeed_0: packet.payload.ctrl_mwspeed.0
    :field ctrl_mwspeed_1: packet.payload.ctrl_mwspeed.1
    :field ctrl_mwspeed_2: packet.payload.ctrl_mwspeed.2
    :field ctrl_mwspeed_3: packet.payload.ctrl_mwspeed.3
    :field ctrl_mwmoment_0: packet.payload.ctrl_mwmoment.0
    :field ctrl_mwmoment_1: packet.payload.ctrl_mwmoment.1
    :field ctrl_mwmoment_2: packet.payload.ctrl_mwmoment.2
    :field ctrl_mwmoment_3: packet.payload.ctrl_mwmoment.3
    :field ctrl_refrate_x: packet.payload.ctrl_refrate.0
    :field ctrl_refrate_y: packet.payload.ctrl_refrate.1
    :field ctrl_refrate_z: packet.payload.ctrl_refrate.2
    :field ctrl_euleroff_x: packet.payload.ctrl_euleroff.0
    :field ctrl_euleroff_y: packet.payload.ctrl_euleroff.1
    :field ctrl_euleroff_z: packet.payload.ctrl_euleroff.2
    :field ctrl_btorque_x: packet.payload.ctrl_btorque.0
    :field ctrl_btorque_y: packet.payload.ctrl_btorque.1
    :field ctrl_btorque_z: packet.payload.ctrl_btorque.2
    :field ctrl_bmoment_x: packet.payload.ctrl_bmoment.0
    :field ctrl_bmoment_y: packet.payload.ctrl_bmoment.1
    :field ctrl_bmoment_z: packet.payload.ctrl_bmoment.2
    
    :field bcn21_timestamp: packet.payload.hk_14_0_21.timestamp
    :field core: packet.payload.core_loaded
    :field sector_history_0: packet.payload.sector_history.0
    :field sector_history_1: packet.payload.sector_history.1
    :field sector_history_2: packet.payload.sector_history.2
    :field sector_history_3: packet.payload.sector_history.3
    :field sector_history_4: packet.payload.sector_history.4
    :field sector_history_5: packet.payload.sector_history.5
    :field sector_history_6: packet.payload.sector_history.6
    :field sector_history_7: packet.payload.sector_history.7
    :field sector_history_8: packet.payload.sector_history.8
    :field sector_history_9: packet.payload.sector_history.9
    :field sector_history_10: packet.payload.sector_history.10
    :field sector_history_11: packet.payload.sector_history.11
    :field sector_history_12: packet.payload.sector_history.12
    :field sector_history_13: packet.payload.sector_history.13
    :field sector_history_14: packet.payload.sector_history.14
    :field sector_history_15: packet.payload.sector_history.15
    :field mbytes_history_0: packet.payload.mbytes_history.0
    :field mbytes_history_1: packet.payload.mbytes_history.1
    :field mbytes_history_2: packet.payload.mbytes_history.2
    :field mbytes_history_3: packet.payload.mbytes_history.3
    :field mbytes_history_4: packet.payload.mbytes_history.4
    :field mbytes_history_5: packet.payload.mbytes_history.5
    :field mbytes_history_6: packet.payload.mbytes_history.6
    :field mbytes_history_7: packet.payload.mbytes_history.7
    :field mbytes_history_8: packet.payload.mbytes_history.8
    :field mbytes_history_9: packet.payload.mbytes_history.9
    :field mbytes_history_10: packet.payload.mbytes_history.10
    :field mbytes_history_11: packet.payload.mbytes_history.11
    :field mbytes_history_12: packet.payload.mbytes_history.12
    :field mbytes_history_13: packet.payload.mbytes_history.13
    :field mbytes_history_14: packet.payload.mbytes_history.14
    :field mbytes_history_15: packet.payload.mbytes_history.15
    :field hdcam_exposure: packet.payload.exposure
    :field hdcam_gain: packet.payload.gain
    :field chan_ref_lock: packet.payload.chan_ref_lock
    :field chan_temp: packet.payload.chan_temp
    :field chan_inited: packet.payload.chan_inited
    :field chan_written: packet.payload.chan_written
    :field chan_rec_status: packet.payload.chan_rec_status
    :field chan_req_mbytes: packet.payload.chan_req_mbytes
    :field chan_time: packet.payload.chan_time
    
    :field bcn21_timestamp: packet.payload.hk_14_29_22.timestamp
    :field chan_pps_present: packet.payload.chan_pps_present
    :field chan_pps_count: packet.payload.chan_pps_count
    :field rec_inited: packet.payload.rec_inited
    :field rec_written: packet.payload.rec_written
    :field rec_rec_status: packet.payload.rec_rec_status
    :field rec_req_mbytes: packet.payload.rec_req_mbytes
    :field rec_time: packet.payload.rec_time
    :field rec_temp: packet.payload.rec_temp
    :field trans_inited: packet.payload.trans_inited
    :field trans_mbytes_sent: packet.payload.trans_mbytes_sent
    :field trans_system_time: packet.payload.trans_system_time
    :field mis1_temp: packet.payload.mis1_temp
    :field mis1_fsk_incr: packet.payload.mis1_fsk_incr
    :field mis1_system_time: packet.payload.mis1_system_time
    
    :field bcn93_timestamp: packet.payload.hk_1_93_93.timestamp
    :field inf_blob: packet.payload.inf_blob
    """

    class CoreType(Enum):
        channelizer = 0
        mission1_fsk = 1
        recorder = 2
        transmitter = 3
        asdr_bsp = 4
        failed = 127
        none = 255

    class MpptType(Enum):
        tracking = 1
        fixed = 2
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.packet = Catsat.BeaconFrame(self._io, self, self._root)

    class Asdr2BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_14_29_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.chan_pps_present = self._io.read_u1()
            self.chan_pps_count = self._io.read_s4be()
            self.hk_14_37_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.rec_inited = self._io.read_u1()
            self.hk_14_38_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.rec_written = self._io.read_f4be()
            self.rec_rec_status = self._io.read_u1()
            self.rec_req_mbytes = self._io.read_s4be()
            self.rec_time = self._io.read_f4be()
            self.hk_14_43_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.rec_temp = self._io.read_f4be()
            self.hk_14_52_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.trans_inited = self._io.read_u1()
            self.trans_mbytes_sent = self._io.read_f4be()
            self.hk_14_53_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.trans_system_time = self._io.read_s8be()
            self.hk_14_33_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.mis1_temp = self._io.read_f4be()
            self.hk_14_34_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.mis1_fsk_incr = self._io.read_s4be()
            self.hk_14_35_22 = Catsat.ElementHeader(self._io, self, self._root)
            self.mis1_system_time = self._io.read_s8be()


    class CspHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_flags = []
            for i in range(4):
                self.csp_flags.append(self._io.read_u1())


        @property
        def source(self):
            if hasattr(self, '_m_source'):
                return self._m_source

            self._m_source = ((self.csp_flags[3] >> 1) & 31)
            return getattr(self, '_m_source', None)

        @property
        def rdp(self):
            if hasattr(self, '_m_rdp'):
                return self._m_rdp

            self._m_rdp = ((self.csp_flags[0] >> 1) & 1)
            return getattr(self, '_m_rdp', None)

        @property
        def src_port(self):
            if hasattr(self, '_m_src_port'):
                return self._m_src_port

            self._m_src_port = (self.csp_flags[1] & 63)
            return getattr(self, '_m_src_port', None)

        @property
        def destination(self):
            if hasattr(self, '_m_destination'):
                return self._m_destination

            self._m_destination = (((self.csp_flags[2] >> 2) | (self.csp_flags[3] << 4)) & 31)
            return getattr(self, '_m_destination', None)

        @property
        def dst_port(self):
            if hasattr(self, '_m_dst_port'):
                return self._m_dst_port

            self._m_dst_port = (((self.csp_flags[1] >> 6) | (self.csp_flags[2] << 2)) & 63)
            return getattr(self, '_m_dst_port', None)

        @property
        def priority(self):
            if hasattr(self, '_m_priority'):
                return self._m_priority

            self._m_priority = (self.csp_flags[3] >> 6)
            return getattr(self, '_m_priority', None)

        @property
        def reserved(self):
            if hasattr(self, '_m_reserved'):
                return self._m_reserved

            self._m_reserved = (self.csp_flags[0] >> 4)
            return getattr(self, '_m_reserved', None)

        @property
        def xtea(self):
            if hasattr(self, '_m_xtea'):
                return self._m_xtea

            self._m_xtea = ((self.csp_flags[0] >> 2) & 1)
            return getattr(self, '_m_xtea', None)

        @property
        def hmac(self):
            if hasattr(self, '_m_hmac'):
                return self._m_hmac

            self._m_hmac = ((self.csp_flags[0] >> 3) & 1)
            return getattr(self, '_m_hmac', None)

        @property
        def crc(self):
            if hasattr(self, '_m_crc'):
                return self._m_crc

            self._m_crc = (self.csp_flags[0] & 1)
            return getattr(self, '_m_crc', None)


    class Adcs0BcnFast(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_150_7 = Catsat.ElementHeader(self._io, self, self._root)
            self.extmag = []
            for i in range(3):
                self.extmag.append(self._io.read_f4be())

            self.torquer_duty = []
            for i in range(3):
                self.torquer_duty.append(self._io.read_f4be())

            self.hk_4_151_7 = Catsat.ElementHeader(self._io, self, self._root)
            self.bdot_rate = []
            for i in range(2):
                self.bdot_rate.append(self._io.read_f4be())

            self.bdot_dmag = []
            for i in range(3):
                self.bdot_dmag.append(self._io.read_f4be())

            self.bdot_torquer = []
            for i in range(3):
                self.bdot_torquer.append(self._io.read_f4be())

            self.bdot_detumble = self._io.read_u1()
            self.hk_4_154_7 = Catsat.ElementHeader(self._io, self, self._root)
            self.ctrl_refq = []
            for i in range(4):
                self.ctrl_refq.append(self._io.read_f4be())

            self.ctrl_errq = []
            for i in range(4):
                self.ctrl_errq.append(self._io.read_f4be())

            self.ctrl_m = []
            for i in range(3):
                self.ctrl_m.append(self._io.read_f4be())

            self.ctrl_mwspeed = []
            for i in range(4):
                self.ctrl_mwspeed.append(self._io.read_f4be())

            self.ctrl_euleroff = []
            for i in range(3):
                self.ctrl_euleroff.append(self._io.read_f4be())

            self.ctrl_btorque = []
            for i in range(3):
                self.ctrl_btorque.append(self._io.read_f4be())



    class ObcBcnMed(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_1_4_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.obc_fs_mnted = self._io.read_u1()
            self.obc_temp_ram = self._io.read_s2be()
            self.obc_resetcause = self._io.read_u4be()
            self.obc_bootcause = self._io.read_u4be()
            self.obc_uptime = self._io.read_u4be()
            self.hk_1_91_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.batt_charge = self._io.read_u2be()
            self.batt_dcharge = self._io.read_u2be()
            self.batt_heater = self._io.read_u2be()
            self.batt_temp2 = self._io.read_s2be()
            self.batt_temp3 = self._io.read_s2be()
            self.batt_temp4 = self._io.read_s2be()
            self.batt_bootcause = self._io.read_u1()
            self.hk_1_94_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.sat_temps = []
            for i in range(6):
                self.sat_temps.append(self._io.read_f4be())

            self.hk_5_0_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.ax100_reboot_in = self._io.read_u2be()
            self.ax100_tx_inhibit = self._io.read_u4be()
            self.hk_5_1_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.ax100_rx_freq = self._io.read_u4be()
            self.ax100_rx_baud = self._io.read_u4be()
            self.hk_5_4_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.ax100_temp_pa = self._io.read_s2be()
            self.ax100_last_rssi = self._io.read_s2be()
            self.ax100_last_rferr = self._io.read_s2be()
            self.ax100_active_conf = self._io.read_u1()
            self.ax100_bootcause = self._io.read_u2be()
            self.ax100_bgnd_rssi = self._io.read_s2be()
            self.ax100_tx_duty = self._io.read_u1()
            self.hk_5_5_3 = Catsat.ElementHeader(self._io, self, self._root)
            self.ax100_tx_freq = self._io.read_u4be()
            self.ax100_tx_baud = self._io.read_u4be()


    class Adcs2BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_150_12 = Catsat.ElementHeader(self._io, self, self._root)
            self.wheel_torque = []
            for i in range(4):
                self.wheel_torque.append(self._io.read_f4be())

            self.wheel_momentum = []
            for i in range(4):
                self.wheel_momentum.append(self._io.read_f4be())

            self.wheel_speed = []
            for i in range(4):
                self.wheel_speed.append(self._io.read_f4be())

            self.wheel_enable = []
            for i in range(4):
                self.wheel_enable.append(self._io.read_u1())

            self.wheel_current = []
            for i in range(4):
                self.wheel_current.append(self._io.read_u2be())

            self.wheel_temp = []
            for i in range(4):
                self.wheel_temp.append(self._io.read_s2be())

            self.torquer_duty = []
            for i in range(3):
                self.torquer_duty.append(self._io.read_f4be())

            self.torquer_calib = []
            for i in range(3):
                self.torquer_calib.append(self._io.read_f4be())

            self.hk_4_151_12 = Catsat.ElementHeader(self._io, self, self._root)
            self.acs_mode = self._io.read_s1()
            self.acs_dmode = self._io.read_s1()
            self.ads_mode = self._io.read_s1()
            self.ads_dmode = self._io.read_s1()
            self.ephem_mode = self._io.read_s1()
            self.ephem_dmode = self._io.read_s1()
            self.spin_mode = self._io.read_s1()
            self.status_mag = self._io.read_s1()
            self.status_extmag = self._io.read_s1()
            self.status_css = self._io.read_s1()
            self.status_fss = []
            for i in range(5):
                self.status_fss.append(self._io.read_s1())

            self.status_gyro = self._io.read_s1()
            self.status_extgyro = self._io.read_s1()
            self.status_gps = self._io.read_s1()
            self.status_bdot = self._io.read_s1()
            self.status_ukf = self._io.read_s1()
            self.status_etime = self._io.read_s1()
            self.status_ephem = self._io.read_s1()
            self.status_run = self._io.read_s1()
            self.looptime = self._io.read_s2be()
            self.max_looptime = self._io.read_s2be()
            self.bdot_rate = []
            for i in range(2):
                self.bdot_rate.append(self._io.read_f4be())

            self.bdot_dmag = []
            for i in range(3):
                self.bdot_dmag.append(self._io.read_f4be())

            self.bdot_torquer = []
            for i in range(3):
                self.bdot_torquer.append(self._io.read_f4be())

            self.bdot_detumble = self._io.read_u1()


    class Pdu2BcnMed(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_10_4_5 = Catsat.ElementHeader(self._io, self, self._root)
            self.pdu_x3_vout = []
            for i in range(9):
                self.pdu_x3_vout.append(self._io.read_s2be())

            self.pdu_x3_temp = self._io.read_s2be()
            self.pdu_x3_out_en = []
            for i in range(9):
                self.pdu_x3_out_en.append(self._io.read_u1())

            self.pdu_x3_bootcause = self._io.read_u4be()
            self.pdu_x3_boot_cnt = self._io.read_u4be()
            self.pdu_x3_uptime = self._io.read_u4be()
            self.pdu_x3_resetcause = self._io.read_u2be()
            self.pdu_x3_latchup = []
            for i in range(9):
                self.pdu_x3_latchup.append(self._io.read_u2be())

            self.hk_11_4_5 = Catsat.ElementHeader(self._io, self, self._root)
            self.acu_cin = []
            for i in range(6):
                self.acu_cin.append(self._io.read_s2be())

            self.acu_vin = []
            for i in range(6):
                self.acu_vin.append(self._io.read_u2be())

            self.acu_vbatt = self._io.read_u2be()
            self.acu_temp = []
            for i in range(3):
                self.acu_temp.append(self._io.read_s2be())

            self.acu_mppt_mode = KaitaiStream.resolve_enum(Catsat.MpptType, self._io.read_u1())
            self.acu_vboost = []
            for i in range(6):
                self.acu_vboost.append(self._io.read_u2be())

            self.acu_bootcause = self._io.read_u4be()
            self.acu_boot_cnt = self._io.read_u4be()
            self.acu_uptime = self._io.read_u4be()
            self.acu_resetcause = self._io.read_u2be()


    class BeaconFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Catsat.Header(self._io, self, self._root)
            _on = self.header.type
            if _on == 93:
                self.payload = Catsat.BcnInf(self._io, self, self._root)
            elif _on == 14:
                self.payload = Catsat.Adcs4BcnLow(self._io, self, self._root)
            elif _on == 17:
                self.payload = Catsat.Adcs7BcnMed(self._io, self, self._root)
            elif _on == 0:
                self.payload = Catsat.MotdBcn(self._io, self, self._root)
            elif _on == 4:
                self.payload = Catsat.Pdu1BcnMed(self._io, self, self._root)
            elif _on == 6:
                self.payload = Catsat.DepBcnLow(self._io, self, self._root)
            elif _on == 7:
                self.payload = Catsat.Adcs0BcnFast(self._io, self, self._root)
            elif _on == 1:
                self.payload = Catsat.Crit1BcnHigh(self._io, self, self._root)
            elif _on == 13:
                self.payload = Catsat.Adcs3BcnLow(self._io, self, self._root)
            elif _on == 11:
                self.payload = Catsat.Adcs1BcnLow(self._io, self, self._root)
            elif _on == 12:
                self.payload = Catsat.Adcs2BcnLow(self._io, self, self._root)
            elif _on == 3:
                self.payload = Catsat.ObcBcnMed(self._io, self, self._root)
            elif _on == 5:
                self.payload = Catsat.Pdu2BcnMed(self._io, self, self._root)
            elif _on == 15:
                self.payload = Catsat.Adcs5BcnLow(self._io, self, self._root)
            elif _on == 21:
                self.payload = Catsat.Asdr1BcnLow(self._io, self, self._root)
            elif _on == 16:
                self.payload = Catsat.Adcs6BcnLow(self._io, self, self._root)
            elif _on == 2:
                self.payload = Catsat.Crit2BcnHigh(self._io, self, self._root)
            elif _on == 22:
                self.payload = Catsat.Asdr2BcnLow(self._io, self, self._root)


    class BcnInf(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_1_93_93 = Catsat.ElementHeader(self._io, self, self._root)
            self.inf_blob = []
            for i in range(42):
                self.inf_blob.append(self._io.read_u1())



    class Adcs4BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_152_14 = Catsat.ElementHeader(self._io, self, self._root)
            self.ukf_z = []
            for i in range(12):
                self.ukf_z.append(self._io.read_f4be())

            self.ukf_enable = []
            for i in range(12):
                self.ukf_enable.append(self._io.read_u1())

            self.ukf_sunmax = []
            for i in range(6):
                self.ukf_sunmax.append(self._io.read_f4be())

            self.ukf_in_eclipse = self._io.read_u1()
            self.ukf_choice = self._io.read_u1()
            self.ukf_ctrl_t = []
            for i in range(3):
                self.ukf_ctrl_t.append(self._io.read_f4be())

            self.ukf_ctrl_m = []
            for i in range(3):
                self.ukf_ctrl_m.append(self._io.read_f4be())

            self.ukf_rate = []
            for i in range(3):
                self.ukf_rate.append(self._io.read_f4be())



    class Adcs6BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_1_16 = Catsat.ElementHeader(self._io, self, self._root)
            self.adcs_swload_cnt1 = self._io.read_u2be()
            self.hk_4_4_16 = Catsat.ElementHeader(self._io, self, self._root)
            self.adcs_fs_mounted = self._io.read_u1()
            self.adcs_temp_mcu = self._io.read_s2be()
            self.adcs_temp_ram = self._io.read_s2be()
            self.adcs_resetcause = self._io.read_u4be()
            self.adcs_bootcause = self._io.read_u4be()
            self.adcs_boot_cnt = self._io.read_u2be()
            self.adcs_clock = self._io.read_u4be()
            self.adcs_uptime = self._io.read_u4be()


    class Adcs7BcnMed(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_154_17 = Catsat.ElementHeader(self._io, self, self._root)
            self.ctrl_refq = []
            for i in range(4):
                self.ctrl_refq.append(self._io.read_f4be())

            self.ctrl_errq = []
            for i in range(4):
                self.ctrl_errq.append(self._io.read_f4be())

            self.ctrl_errrate = []
            for i in range(3):
                self.ctrl_errrate.append(self._io.read_f4be())

            self.ctrl_m = []
            for i in range(3):
                self.ctrl_m.append(self._io.read_f4be())

            self.ctrl_mwtorque = []
            for i in range(4):
                self.ctrl_mwtorque.append(self._io.read_f4be())

            self.ctrl_mwspeed = []
            for i in range(4):
                self.ctrl_mwspeed.append(self._io.read_f4be())

            self.ctrl_mwmoment = []
            for i in range(4):
                self.ctrl_mwmoment.append(self._io.read_f4be())

            self.ctrl_refrate = []
            for i in range(3):
                self.ctrl_refrate.append(self._io.read_f4be())

            self.ctrl_euleroff = []
            for i in range(3):
                self.ctrl_euleroff.append(self._io.read_f4be())

            self.ctrl_btorque = []
            for i in range(3):
                self.ctrl_btorque.append(self._io.read_f4be())

            self.ctrl_bmoment = []
            for i in range(3):
                self.ctrl_bmoment.append(self._io.read_f4be())



    class Adcs5BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_153_15 = Catsat.ElementHeader(self._io, self, self._root)
            self.ephem_jdat = self._io.read_f8be()
            self.ephem_reci = []
            for i in range(3):
                self.ephem_reci.append(self._io.read_f4be())

            self.ephem_veci = []
            for i in range(3):
                self.ephem_veci.append(self._io.read_f4be())

            self.ephem_sun_eci = []
            for i in range(3):
                self.ephem_sun_eci.append(self._io.read_f4be())

            self.ephem_quat_ie = []
            for i in range(4):
                self.ephem_quat_ie.append(self._io.read_f4be())

            self.ephem_quat_io = []
            for i in range(4):
                self.ephem_quat_io.append(self._io.read_f4be())

            self.ephem_quat_il = []
            for i in range(4):
                self.ephem_quat_il.append(self._io.read_f4be())

            self.ephem_rate_io = []
            for i in range(3):
                self.ephem_rate_io.append(self._io.read_f4be())

            self.ephem_rate_il = []
            for i in range(3):
                self.ephem_rate_il.append(self._io.read_f4be())

            self.ephem_t_eclipse = self._io.read_s4be()
            self.hk_4_156_15 = Catsat.ElementHeader(self._io, self, self._root)
            self.ephem_time = self._io.read_u4be()
            self.ads_time = self._io.read_u4be()
            self.acs_time = self._io.read_u4be()
            self.sens_time = self._io.read_u4be()


    class MotdBcn(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_1_95 = Catsat.ElementHeader(self._io, self, self._root)
            self.callsign = (KaitaiStream.bytes_terminate(self._io.read_bytes(8), 0, False)).decode(u"ASCII")
            self.motd = (KaitaiStream.bytes_terminate(self._io.read_bytes(80), 0, False)).decode(u"ASCII")


    class Adcs1BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_150_11 = Catsat.ElementHeader(self._io, self, self._root)
            self.extmag = []
            for i in range(3):
                self.extmag.append(self._io.read_f4be())

            self.extmag_temp = self._io.read_f4be()
            self.extmag_valid = self._io.read_u1()
            self.suns = []
            for i in range(6):
                self.suns.append(self._io.read_f4be())

            self.suns_valid = self._io.read_u1()
            self.suns_temp = []
            for i in range(6):
                self.suns_temp.append(self._io.read_s2be())

            self.extgyro = []
            for i in range(3):
                self.extgyro.append(self._io.read_f4be())

            self.extgyro_temp = self._io.read_f4be()
            self.extgyro_valid = self._io.read_u1()
            self.fss = []
            for i in range(16):
                self.fss.append(self._io.read_f4be())

            self.fss_temp = self._io.read_f4be()
            self.fss_valid = []
            for i in range(5):
                self.fss_valid.append(self._io.read_u1())

            self.gps_pos = []
            for i in range(3):
                self.gps_pos.append(self._io.read_f4be())

            self.gps_vel = []
            for i in range(3):
                self.gps_vel.append(self._io.read_f4be())

            self.gps_epoch = self._io.read_u4be()
            self.gps_valid = self._io.read_u1()
            self.gps_sat = self._io.read_u1()
            self.gps_satsol = self._io.read_u1()
            self.pps_unix = self._io.read_u4be()


    class DepBcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_1_96_6 = Catsat.ElementHeader(self._io, self, self._root)
            self.ant_1_brn = self._io.read_s2be()
            self.ant_2_brn = self._io.read_s2be()
            self.ant_3_brn = self._io.read_s2be()
            self.ant_4_brn = self._io.read_s2be()
            self.ant_1_rel = self._io.read_s1()
            self.ant_2_rel = self._io.read_s1()
            self.ant_3_rel = self._io.read_s1()
            self.ant_4_rel = self._io.read_s1()
            self.dsp_1_brn = self._io.read_s2be()
            self.dsp_2_brn = self._io.read_s2be()
            self.dsp_1_rel = self._io.read_s1()
            self.dsp_2_rel = self._io.read_s1()


    class ElementHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.checksum = self._io.read_u2be()
            self.timestamp = self._io.read_u4be()
            self.source = self._io.read_u2be()


    class Adcs3BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_4_152_13 = Catsat.ElementHeader(self._io, self, self._root)
            self.ukf_x = []
            for i in range(13):
                self.ukf_x.append(self._io.read_f4be())

            self.ukf_q = []
            for i in range(4):
                self.ukf_q.append(self._io.read_f4be())

            self.ukf_w = []
            for i in range(3):
                self.ukf_w.append(self._io.read_f4be())

            self.ukf_xpred = []
            for i in range(13):
                self.ukf_xpred.append(self._io.read_f4be())

            self.ukf_zpred = []
            for i in range(12):
                self.ukf_zpred.append(self._io.read_f4be())



    class Header(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.csp_header = Catsat.CspHeader(self._io, self, self._root)
            self.protocol_version = self._io.read_u1()
            self.type = self._io.read_u1()
            self.version = self._io.read_u1()
            self.satid = self._io.read_u2be()


    class Pdu1BcnMed(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_8_4_4 = Catsat.ElementHeader(self._io, self, self._root)
            self.p60_cout = []
            for i in range(13):
                self.p60_cout.append(self._io.read_s2be())

            self.p60_out_en = []
            for i in range(13):
                self.p60_out_en.append(self._io.read_u1())

            self.p60_temp = []
            for i in range(2):
                self.p60_temp.append(self._io.read_s2be())

            self.p60_bootcause = self._io.read_u4be()
            self.p60_uptime = self._io.read_u4be()
            self.p60_resetcause = self._io.read_u2be()
            self.p60_latchup = []
            for i in range(13):
                self.p60_latchup.append(self._io.read_u2be())

            self.p60_vcc_c = self._io.read_s2be()
            self.p60_batt_v = self._io.read_u2be()
            self.p60_dearm_status = self._io.read_u1()
            self.p60_wdt_cnt_gnd = self._io.read_u4be()
            self.p60_wdt_cnt_can = self._io.read_u4be()
            self.p60_wdt_cnt_left = self._io.read_u4be()
            self.p60_batt_chrg = self._io.read_s2be()
            self.p60_batt_dchrg = self._io.read_s2be()
            self.ant6_depl = self._io.read_s1()
            self.ar6_depl = self._io.read_s1()
            self.hk_9_4_4 = Catsat.ElementHeader(self._io, self, self._root)
            self.pdu_x2_vout = []
            for i in range(9):
                self.pdu_x2_vout.append(self._io.read_s2be())

            self.pdu_x2_temp = self._io.read_s2be()
            self.pdu_x2_out_en = []
            for i in range(9):
                self.pdu_x2_out_en.append(self._io.read_u1())

            self.pdu_x2_bootcause = self._io.read_u4be()
            self.pdu_x2_boot_cnt = self._io.read_u4be()
            self.pdu_x2_uptime = self._io.read_u4be()
            self.pdu_x2_resetcause = self._io.read_u2be()
            self.pdu_x2_latchup = []
            for i in range(9):
                self.pdu_x2_latchup.append(self._io.read_u2be())



    class Crit2BcnHigh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_10_4_2 = Catsat.ElementHeader(self._io, self, self._root)
            self.pdu_x3_cout = []
            for i in range(9):
                self.pdu_x3_cout.append(self._io.read_s2be())

            self.hk_11_4_2 = Catsat.ElementHeader(self._io, self, self._root)
            self.acu_power = []
            for i in range(6):
                self.acu_power.append(self._io.read_u2be())

            self.hk_4_4_2 = Catsat.ElementHeader(self._io, self, self._root)
            self.adcs_boot_cnt = self._io.read_u2be()
            self.adcs_clock = self._io.read_u4be()
            self.hk_4_150_2 = Catsat.ElementHeader(self._io, self, self._root)
            self.extgyro = []
            for i in range(3):
                self.extgyro.append(self._io.read_f4be())

            self.gps_pos = []
            for i in range(3):
                self.gps_pos.append(self._io.read_f4be())

            self.gps_vel = []
            for i in range(3):
                self.gps_vel.append(self._io.read_f4be())

            self.hk_4_151_2 = Catsat.ElementHeader(self._io, self, self._root)
            self.acs_mode = self._io.read_s1()
            self.status_extmag = self._io.read_s1()
            self.status_fss = []
            for i in range(5):
                self.status_fss.append(self._io.read_s1())

            self.status_extgyro = self._io.read_s1()
            self.status_gps = self._io.read_s1()


    class Crit1BcnHigh(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_1_4_1 = Catsat.ElementHeader(self._io, self, self._root)
            self.obc_temp_mcu = self._io.read_s2be()
            self.obc_boot_cnt = self._io.read_u2be()
            self.obc_clock = self._io.read_u4be()
            self.hk_1_91 = Catsat.ElementHeader(self._io, self, self._root)
            self.bpx_vbatt = self._io.read_u2be()
            self.bpx_temp = self._io.read_s2be()
            self.bpx_boot_cnt = self._io.read_u4be()
            self.hk_5_4_1 = Catsat.ElementHeader(self._io, self, self._root)
            self.ax100_temp_brd = self._io.read_s2be()
            self.ax100_boot_cnt = self._io.read_u2be()
            self.ax100_last_contact = self._io.read_u4be()
            self.hk_8_4_1 = Catsat.ElementHeader(self._io, self, self._root)
            self.p60_boot_cnt = self._io.read_u4be()
            self.p60_batt_mode = self._io.read_u1()
            self.p60_batt_v = self._io.read_u2be()
            self.p60_batt_c = self._io.read_s2be()
            self.hk_9_4 = Catsat.ElementHeader(self._io, self, self._root)
            self.pdu_x2_cout = []
            for i in range(9):
                self.pdu_x2_cout.append(self._io.read_s2be())



    class Asdr1BcnLow(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_14_0_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.core_loaded = KaitaiStream.resolve_enum(Catsat.CoreType, self._io.read_u1())
            self.hk_14_1_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.sector_history = []
            for i in range(16):
                self.sector_history.append(self._io.read_u2be())

            self.mbytes_history = []
            for i in range(16):
                self.mbytes_history.append(self._io.read_u2be())

            self.exposure = self._io.read_u4be()
            self.gain = self._io.read_f4be()
            self.hk_14_12_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.chan_ref_lock = self._io.read_u1()
            self.hk_14_13_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.chan_temp = self._io.read_f4be()
            self.hk_14_16_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.chan_inited = self._io.read_u1()
            self.hk_14_18_21 = Catsat.ElementHeader(self._io, self, self._root)
            self.chan_written = self._io.read_f4be()
            self.chan_rec_status = self._io.read_u1()
            self.chan_req_mbytes = self._io.read_s4be()
            self.chan_time = self._io.read_f4be()


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length

        self._m_frame_length = self._io.size()
        return getattr(self, '_m_frame_length', None)


