# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Eirsat1(KaitaiStruct):
    """:field version_no: frame_contents.header.version_no
    :field sc_id: frame_contents.header.sc_id
    :field vc_id: frame_contents.header.vc_id
    :field ocf: frame_contents.header.ocf
    :field mc_count: frame_contents.header.mc_count
    :field vc_count: frame_contents.header.vc_count
    :field sec_hdr_flag: frame_contents.header.sec_hdr_flag
    :field sync_flag: frame_contents.header.sync_flag
    :field pkt_order_flag: frame_contents.header.pkt_order_flag
    :field seg_len_id: frame_contents.header.seg_len_id
    :field first_hdr_pointer: frame_contents.header.first_hdr_pointer
    :field packets___version_no: frame_contents.packets.___.header.version_no
    :field packets___type_indicator: frame_contents.packets.___.header.type_indicator
    :field packets___sec_hdr_flag: frame_contents.packets.___.header.sec_hdr_flag
    :field packets___apid: frame_contents.packets.___.header.apid
    :field packets___grouping_flags: frame_contents.packets.___.header.grouping_flags
    :field packets___src_seq: frame_contents.packets.___.header.src_seq
    :field packets___packet_data_len: frame_contents.packets.___.header.packet_data_len
    :field packets___pus_version: frame_contents.packets.___.data_field.sec_hdr.pus_version
    :field packets___ack: frame_contents.packets.___.data_field.sec_hdr.ack
    :field packets___service: frame_contents.packets.___.data_field.service
    :field packets___subservice: frame_contents.packets.___.data_field.subservice
    :field packets___hk_structure_id: frame_contents.packets.___.data_field.data.hk_structure_id
    :field packets___version_satellitestring_0: frame_contents.packets.___.data_field.data.hk_data.version_satellitestring_0
    :field packets___version_messagestring_0: frame_contents.packets.___.data_field.data.hk_data.version_messagestring_0
    :field packets___core_obt_time_0: frame_contents.packets.___.data_field.data.hk_data.core_obt_time_0
    :field packets___core_obt_uptime_0: frame_contents.packets.___.data_field.data.hk_data.core_obt_uptime_0
    :field packets___mission_separationsequence_state_0: frame_contents.packets.___.data_field.data.hk_data.mission_separationsequence_state_0
    :field packets___mission_separationsequence_antswitchesstatuses_0_3_uhf_minusy: frame_contents.packets.___.data_field.data.hk_data.mission_separationsequence_antswitchesstatuses_0_3_uhf_minusy
    :field packets___mission_separationsequence_antswitchesstatuses_0_2_vhf_minusx: frame_contents.packets.___.data_field.data.hk_data.mission_separationsequence_antswitchesstatuses_0_2_vhf_minusx
    :field packets___mission_separationsequence_antswitchesstatuses_0_1_uhf_plusy: frame_contents.packets.___.data_field.data.hk_data.mission_separationsequence_antswitchesstatuses_0_1_uhf_plusy
    :field packets___mission_separationsequence_antswitchesstatuses_0_0_vhf_plusx: frame_contents.packets.___.data_field.data.hk_data.mission_separationsequence_antswitchesstatuses_0_0_vhf_plusx
    :field packets___platform_obc_obc_currbootimage_0: frame_contents.packets.___.data_field.data.hk_data.platform_obc_obc_currbootimage_0
    :field packets___comms_hmac_sequencenumber_0: frame_contents.packets.___.data_field.data.hk_data.comms_hmac_sequencenumber_0
    :field packets___platform_bat_batterycurrent_2: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batterycurrent_2
    :field packets___platform_bat_batteryvoltage_2: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batteryvoltage_2
    :field packets___platform_bat_batterytemperature_0: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batterytemperature_0
    :field packets___platform_bat_batterytemperature_1: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batterytemperature_1
    :field packets___platform_bat_batterytemperature_2: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batterytemperature_2
    :field packets___platform_bat_batterycurrentdir_0: frame_contents.packets.___.data_field.data.hk_data.platform_bat_batterycurrentdir_0
    :field packets___platform_bat_packedheaterstatus_0: frame_contents.packets.___.data_field.data.hk_data.platform_bat_packedheaterstatus_0
    :field packets___platform_bat_packedheaterstatus_1: frame_contents.packets.___.data_field.data.hk_data.platform_bat_packedheaterstatus_1
    :field packets___platform_bat_packedheaterstatus_2: frame_contents.packets.___.data_field.data.hk_data.platform_bat_packedheaterstatus_2
    :field packets___platform_eps_actualswitchstatesbitmap_0_9: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_9
    :field packets___platform_eps_actualswitchstatesbitmap_0_8: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_8
    :field packets___platform_eps_actualswitchstatesbitmap_0_7: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_7
    :field packets___platform_eps_actualswitchstatesbitmap_0_6: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_6
    :field packets___platform_eps_actualswitchstatesbitmap_0_5: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_5
    :field packets___platform_eps_actualswitchstatesbitmap_0_4: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_4
    :field packets___platform_eps_actualswitchstatesbitmap_0_3: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_3
    :field packets___platform_eps_actualswitchstatesbitmap_0_2: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_2
    :field packets___platform_eps_actualswitchstatesbitmap_0_1: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_1
    :field packets___platform_eps_actualswitchstatesbitmap_0_0: frame_contents.packets.___.data_field.data.hk_data.platform_eps_actualswitchstatesbitmap_0_0
    :field packets___platform_eps_switchovercurrentbitmap_0_9: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_9
    :field packets___platform_eps_switchovercurrentbitmap_0_8: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_8
    :field packets___platform_eps_switchovercurrentbitmap_0_7: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_7
    :field packets___platform_eps_switchovercurrentbitmap_0_6: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_6
    :field packets___platform_eps_switchovercurrentbitmap_0_5: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_5
    :field packets___platform_eps_switchovercurrentbitmap_0_4: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_4
    :field packets___platform_eps_switchovercurrentbitmap_0_3: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_3
    :field packets___platform_eps_switchovercurrentbitmap_0_2: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_2
    :field packets___platform_eps_switchovercurrentbitmap_0_1: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_1
    :field packets___platform_eps_switchovercurrentbitmap_0_0: frame_contents.packets.___.data_field.data.hk_data.platform_eps_switchovercurrentbitmap_0_0
    :field packets___platform_eps_board_temperature_0: frame_contents.packets.___.data_field.data.hk_data.platform_eps_board_temperature_0
    :field packets___platform_eps_bus_voltages_0_battery: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_voltages_0_battery
    :field packets___platform_eps_bus_voltages_1_3v3: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_voltages_1_3v3
    :field packets___platform_eps_bus_voltages_2_5v: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_voltages_2_5v
    :field packets___platform_eps_bus_voltages_3_12v: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_voltages_3_12v
    :field packets___platform_eps_bus_currents_0_battery: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_currents_0_battery
    :field packets___platform_eps_bus_currents_1_3v3: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_currents_1_3v3
    :field packets___platform_eps_bus_currents_2_5v: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_currents_2_5v
    :field packets___platform_eps_bus_currents_3_12v: frame_contents.packets.___.data_field.data.hk_data.platform_eps_bus_currents_3_12v
    :field packets___platform_adcs_array_temperature_1_plusx: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_array_temperature_1_plusx
    :field packets___platform_adcs_array_temperature_4_minusx: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_array_temperature_4_minusx
    :field packets___platform_adcs_array_temperature_3_plusy: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_array_temperature_3_plusy
    :field packets___platform_adcs_array_temperature_2_minusy: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_array_temperature_2_minusy
    :field packets___platform_eps_solar_array_currents_1_plusx: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_currents_1_plusx
    :field packets___platform_eps_solar_array_currents_4_minusx: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_currents_4_minusx
    :field packets___platform_eps_solar_array_currents_3_plusy: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_currents_3_plusy
    :field packets___platform_eps_solar_array_currents_2_minusy: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_currents_2_minusy
    :field packets___platform_eps_solar_array_voltages_0: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_voltages_0
    :field packets___platform_eps_solar_array_voltages_1: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_voltages_1
    :field packets___platform_eps_solar_array_voltages_2: frame_contents.packets.___.data_field.data.hk_data.platform_eps_solar_array_voltages_2
    :field packets___platform_adcs_packedadcsmode_0: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_packedadcsmode_0
    :field packets___platform_adcs_executioncount_0: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_executioncount_0
    :field packets___platform_adcs_rawgyrorate_0: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_rawgyrorate_0
    :field packets___platform_adcs_rawgyrorate_1: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_rawgyrorate_1
    :field packets___platform_adcs_rawgyrorate_2: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_rawgyrorate_2
    :field packets___platform_adcs_fss1alphaangle_0: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_fss1alphaangle_0
    :field packets___platform_adcs_fss1betaangle_0: frame_contents.packets.___.data_field.data.hk_data.platform_adcs_fss1betaangle_0
    :field packets___platform_cmc_mode_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_mode_0
    :field packets___platform_cmc_beaconenable_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_beaconenable_0
    :field packets___platform_cmc_txtransparent_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_txtransparent_0
    :field packets___platform_cmc_txconvenabled_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_txconvenabled_0
    :field packets___platform_cmc_txpower_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_txpower_0
    :field packets___platform_cmc_rxlock_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_rxlock_0
    :field packets___platform_cmc_rxrssi_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_rxrssi_0
    :field packets___platform_cmc_rxfrequencyoffset_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_rxfrequencyoffset_0
    :field packets___platform_cmc_rxpacketcount_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_rxpacketcount_0
    :field packets___platform_cmc_temperaturepa_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_temperaturepa_0
    :field packets___platform_cmc_current5v_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_current5v_0
    :field packets___platform_cmc_voltage5v_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_voltage5v_0
    :field packets___platform_cmc_rxcrcerrorcount_0: frame_contents.packets.___.data_field.data.hk_data.platform_cmc_rxcrcerrorcount_0
    :field packets___core_eventdispatcher_eventcount_0: frame_contents.packets.___.data_field.data.hk_data.core_eventdispatcher_eventcount_0
    :field packets___core_eventdispatcher_lastevent_0_severity: frame_contents.packets.___.data_field.data.hk_data.core_eventdispatcher_lastevent_0_severity
    :field packets___core_eventdispatcher_lastevent_0_event_id: frame_contents.packets.___.data_field.data.hk_data.core_eventdispatcher_lastevent_0_event_id
    :field packets___core_eventdispatcher_lastevent_0_event_source_id: frame_contents.packets.___.data_field.data.hk_data.core_eventdispatcher_lastevent_0_event_source_id
    :field packets___core_eventdispatcher_lastevent_0_info: frame_contents.packets.___.data_field.data.hk_data.core_eventdispatcher_lastevent_0_info
    :field packets___padding: frame_contents.packets.___.data_field.data.hk_data.padding
    :field packets___mission_modemanager_mode_0: frame_contents.packets.___.data_field.data.hk_data.mission_modemanager_mode_0
    :field packets___platform_obc_telemetryadcb_channeloutput_7_obctemperature: frame_contents.packets.___.data_field.data.hk_data.platform_obc_telemetryadcb_channeloutput_7_obctemperature
    :field packets___platform_obc_gps_lastvalidstatevec_0_locktime: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_locktime
    :field packets___platform_obc_gps_lastvalidstatevec_0_lockfinetime: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_lockfinetime
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefpositionx: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefpositionx
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefpositiony: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefpositiony
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefpositionz: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefpositionz
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefvelocityx: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefvelocityx
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefvelocityy: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefvelocityy
    :field packets___platform_obc_gps_lastvalidstatevec_0_ecefvelocityz: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_ecefvelocityz
    :field packets___platform_obc_gps_lastvalidstatevec_0_hours: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_hours
    :field packets___platform_obc_gps_lastvalidstatevec_0_minutes: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_minutes
    :field packets___platform_obc_gps_lastvalidstatevec_0_seconds: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_seconds
    :field packets___platform_obc_gps_lastvalidstatevec_0_milliseconds: frame_contents.packets.___.data_field.data.hk_data.platform_obc_gps_lastvalidstatevec_0_milliseconds
    :field packets___payload_emod_dp_resetcounter_0: frame_contents.packets.___.data_field.data.hk_data.payload_emod_dp_resetcounter_0
    :field packets___payload_emod_dp_emodmode_0: frame_contents.packets.___.data_field.data.hk_data.payload_emod_dp_emodmode_0
    :field packets___payload_emod_dp_lastpageaddr_0: frame_contents.packets.___.data_field.data.hk_data.payload_emod_dp_lastpageaddr_0
    :field packets___payload_emod_autopollpages_0: frame_contents.packets.___.data_field.data.hk_data.payload_emod_autopollpages_0
    :field packets___payload_emod_nextpageaddrtopoll_0: frame_contents.packets.___.data_field.data.hk_data.payload_emod_nextpageaddrtopoll_0
    :field packets___payload_gmod_dp_resetcounter_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_resetcounter_0
    :field packets___payload_gmod_dp_gmodmode_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_gmodmode_0
    :field packets___payload_gmod_dp_lastpagesumaddr_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_lastpagesumaddr_0
    :field packets___payload_gmod_dp_streamsumchstatus_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_streamsumchstatus_0
    :field packets___payload_gmod_lastpagesumaddrrx_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_lastpagesumaddrrx_0
    :field packets___payload_gmod_dp_lastpage16addr_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_lastpage16addr_0
    :field packets___payload_gmod_dp_stream16chstatus_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_stream16chstatus_0
    :field packets___payload_gmod_lastpage16addrrx_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_lastpage16addrrx_0
    :field packets___payload_gmod_dp_biasvoltage_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_biasvoltage_0
    :field packets___payload_gmod_dp_biasoffsetvalue_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_biasoffsetvalue_0
    :field packets___payload_gmod_dp_boostconverterenable_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_boostconverterenable_0
    :field packets___payload_gmod_dp_biasoffsetvoltage_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_biasoffsetvoltage_0
    :field packets___payload_gmod_dp_biasoffsetenable_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_dp_biasoffsetenable_0
    :field packets___payload_gmod_grbtriggeringenabled_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_grbtriggeringenabled_0
    :field packets___payload_gmod_grbtriggercount_0: frame_contents.packets.___.data_field.data.hk_data.payload_gmod_grbtriggercount_0
    :field packets___payload_wbc_wbcenabled_0: frame_contents.packets.___.data_field.data.hk_data.payload_wbc_wbcenabled_0
    :field packets___payload_wbc_controllerexecutioncount_0: frame_contents.packets.___.data_field.data.hk_data.payload_wbc_controllerexecutioncount_0
    :field packets___datapool_paramvalid_170: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_170
    :field packets___datapool_paramvalid_43: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_43
    :field packets___datapool_paramvalid_44: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_44
    :field packets___datapool_paramvalid_46: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_46
    :field packets___datapool_paramvalid_42: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_42
    :field packets___datapool_paramvalid_56: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_56
    :field packets___datapool_paramvalid_73: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_73
    :field packets___datapool_paramvalid_74: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_74
    :field packets___datapool_paramvalid_77: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_77
    :field packets___datapool_paramvalid_85: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_85
    :field packets___datapool_paramvalid_86: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_86
    :field packets___datapool_paramvalid_129: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_129
    :field packets___datapool_paramvalid_80: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_80
    :field packets___datapool_paramvalid_84: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_84
    :field packets___datapool_paramvalid_130: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_130
    :field packets___datapool_paramvalid_131: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_131
    :field packets___datapool_paramvalid_89: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_89
    :field packets___datapool_paramvalid_95: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_95
    :field packets___datapool_paramvalid_96: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_96
    :field packets___datapool_paramvalid_2: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_2
    :field packets___datapool_paramvalid_3: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_3
    :field packets___datapool_paramvalid_7: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_7
    :field packets___datapool_paramvalid_8: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_8
    :field packets___datapool_paramvalid_11: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_11
    :field packets___datapool_paramvalid_20: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_20
    :field packets___datapool_paramvalid_22: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_22
    :field packets___datapool_paramvalid_19: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_19
    :field packets___datapool_paramvalid_26: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_26
    :field packets___datapool_paramvalid_32: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_32
    :field packets___datapool_paramvalid_36: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_36
    :field packets___datapool_paramvalid_34: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_34
    :field packets___datapool_paramvalid_28: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_28
    :field packets___datapool_paramvalid_142: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_142
    :field packets___datapool_paramvalid_141: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_141
    :field packets___datapool_paramvalid_143: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_143
    :field packets___datapool_paramvalid_139: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_139
    :field packets___datapool_paramvalid_140: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_140
    :field packets___datapool_paramvalid_149: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_149
    :field packets___datapool_paramvalid_148: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_148
    :field packets___datapool_paramvalid_150: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_150
    :field packets___datapool_paramvalid_151: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_151
    :field packets___datapool_paramvalid_144: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_144
    :field packets___datapool_paramvalid_152: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_152
    :field packets___datapool_paramvalid_153: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_153
    :field packets___datapool_paramvalid_145: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_145
    :field packets___datapool_paramvalid_154: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_154
    :field packets___datapool_paramvalid_155: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_155
    :field packets___datapool_paramvalid_156: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_156
    :field packets___datapool_paramvalid_157: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_157
    :field packets___datapool_paramvalid_158: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_158
    :field packets___datapool_paramvalid_146: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_146
    :field packets___datapool_paramvalid_147: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_147
    :field packets___datapool_paramvalid_168: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_168
    :field packets___datapool_paramvalid_169: frame_contents.packets.___.data_field.data.hk_data.datapool_paramvalid_169
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_frame_contents = self._io.read_bytes(892)
        _io__raw_frame_contents = KaitaiStream(BytesIO(self._raw_frame_contents))
        self.frame_contents = Eirsat1.CcsdsFrame(_io__raw_frame_contents, self, self._root)

    class CcsdsHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_no = self._io.read_bits_int_be(2)
            self.sc_id = self._io.read_bits_int_be(10)
            self.vc_id = self._io.read_bits_int_be(3)
            self.ocf = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.mc_count = self._io.read_u1()
            self.vc_count = self._io.read_u1()
            self.sec_hdr_flag = self._io.read_bits_int_be(1) != 0
            self.sync_flag = self._io.read_bits_int_be(1) != 0
            self.pkt_order_flag = self._io.read_bits_int_be(1) != 0
            self.seg_len_id = self._io.read_bits_int_be(2)
            self.first_hdr_pointer = self._io.read_bits_int_be(11)


    class HkStruct02(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_satellitestring_0 = (self._io.read_bytes(8)).decode(u"ascii")
            self.version_messagestring_0 = (self._io.read_bytes(32)).decode(u"ascii")
            self.core_obt_time_0 = self._io.read_bits_int_be(32)
            self.core_obt_uptime_0 = self._io.read_bits_int_be(32)
            self.mission_modemanager_mode_0 = self._io.read_bits_int_be(4)
            self.mission_separationsequence_state_0 = self._io.read_bits_int_be(8)
            self.mission_separationsequence_antswitchesstatuses_0_3_uhf_minusy = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_2_vhf_minusx = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_1_uhf_plusy = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_0_vhf_plusx = self._io.read_bits_int_be(1) != 0
            self.platform_obc_obc_currbootimage_0 = self._io.read_bits_int_be(8)
            self.comms_hmac_sequencenumber_0 = self._io.read_bits_int_be(24)
            self.platform_obc_telemetryadcb_channeloutput_7_obctemperature = self._io.read_bits_int_be(12)
            self.platform_obc_gps_lastvalidstatevec_0_locktime = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_lockfinetime = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefpositionx = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefpositiony = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefpositionz = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefvelocityx = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefvelocityy = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_ecefvelocityz = self._io.read_bits_int_be(32)
            self.platform_obc_gps_lastvalidstatevec_0_hours = self._io.read_bits_int_be(8)
            self.platform_obc_gps_lastvalidstatevec_0_minutes = self._io.read_bits_int_be(8)
            self.platform_obc_gps_lastvalidstatevec_0_seconds = self._io.read_bits_int_be(8)
            self.platform_obc_gps_lastvalidstatevec_0_milliseconds = self._io.read_bits_int_be(16)
            self.platform_bat_batterycurrent_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batteryvoltage_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_0 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_1 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batterycurrentdir_0 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_0 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_1 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_9 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_8 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_7 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_6 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_5 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_4 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_3 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_1 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_0 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_9 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_8 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_7 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_6 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_5 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_4 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_3 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_1 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_0 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_board_temperature_0 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_0_battery = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_1_3v3 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_2_5v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_3_12v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_0_battery = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_1_3v3 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_2_5v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_3_12v = self._io.read_bits_int_be(10)
            self.platform_adcs_array_temperature_1_plusx = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_4_minusx = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_3_plusy = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_2_minusy = self._io.read_bits_int_be(16)
            self.platform_eps_solar_array_currents_1_plusx = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_4_minusx = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_3_plusy = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_2_minusy = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_0 = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_1 = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_2 = self._io.read_bits_int_be(10)
            self.platform_adcs_packedadcsmode_0 = self._io.read_bits_int_be(8)
            self.platform_adcs_executioncount_0 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_0 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_1 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_2 = self._io.read_bits_int_be(16)
            self.platform_adcs_fss1alphaangle_0 = self._io.read_bits_int_be(32)
            self.platform_adcs_fss1betaangle_0 = self._io.read_bits_int_be(32)
            self.platform_cmc_mode_0 = self._io.read_bits_int_be(2)
            self.platform_cmc_beaconenable_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txtransparent_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txconvenabled_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txpower_0 = self._io.read_bits_int_be(2)
            self.platform_cmc_rxlock_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_rxrssi_0 = self._io.read_bits_int_be(12)
            self.platform_cmc_rxfrequencyoffset_0 = self._io.read_bits_int_be(10)
            self.platform_cmc_rxpacketcount_0 = self._io.read_bits_int_be(16)
            self.platform_cmc_temperaturepa_0 = self._io.read_bits_int_be(8)
            self.platform_cmc_current5v_0 = self._io.read_bits_int_be(16)
            self.platform_cmc_voltage5v_0 = self._io.read_bits_int_be(13)
            self.platform_cmc_rxcrcerrorcount_0 = self._io.read_bits_int_be(16)
            self.payload_emod_dp_resetcounter_0 = self._io.read_bits_int_be(8)
            self.payload_emod_dp_emodmode_0 = self._io.read_bits_int_be(2)
            self.payload_emod_dp_lastpageaddr_0 = self._io.read_bits_int_be(24)
            self.payload_emod_autopollpages_0 = self._io.read_bits_int_be(1) != 0
            self.payload_emod_nextpageaddrtopoll_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_resetcounter_0 = self._io.read_bits_int_be(8)
            self.payload_gmod_dp_gmodmode_0 = self._io.read_bits_int_be(4)
            self.payload_gmod_dp_lastpagesumaddr_0 = self._io.read_bits_int_be(24)
            self.payload_gmod_dp_streamsumchstatus_0 = self._io.read_bits_int_be(2)
            self.payload_gmod_lastpagesumaddrrx_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_lastpage16addr_0 = self._io.read_bits_int_be(24)
            self.payload_gmod_dp_stream16chstatus_0 = self._io.read_bits_int_be(2)
            self.payload_gmod_lastpage16addrrx_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_biasvoltage_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_biasoffsetvalue_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_boostconverterenable_0 = self._io.read_bits_int_be(2)
            self.payload_gmod_dp_biasoffsetvoltage_0 = self._io.read_bits_int_be(16)
            self.payload_gmod_dp_biasoffsetenable_0 = self._io.read_bits_int_be(2)
            self.payload_gmod_grbtriggeringenabled_0 = self._io.read_bits_int_be(1) != 0
            self.payload_gmod_grbtriggercount_0 = self._io.read_bits_int_be(16)
            self.payload_wbc_wbcenabled_0 = self._io.read_bits_int_be(1) != 0
            self.payload_wbc_controllerexecutioncount_0 = self._io.read_bits_int_be(8)
            self.core_eventdispatcher_eventcount_0 = self._io.read_bits_int_be(32)
            self.core_eventdispatcher_lastevent_0_severity = self._io.read_bits_int_be(2)
            self.core_eventdispatcher_lastevent_0_event_id = self._io.read_bits_int_be(14)
            self.core_eventdispatcher_lastevent_0_event_source_id = self._io.read_bits_int_be(16)
            self.core_eventdispatcher_lastevent_0_info = self._io.read_bits_int_be(32)
            self.datapool_paramvalid_170 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_43 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_44 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_46 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_42 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_56 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_73 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_74 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_77 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_85 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_86 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_129 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_80 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_84 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_130 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_131 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_89 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_95 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_96 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_2 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_3 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_7 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_8 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_11 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_20 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_22 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_19 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_26 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_32 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_36 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_34 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_28 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_142 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_141 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_143 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_139 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_140 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_149 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_148 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_150 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_151 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_144 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_152 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_153 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_145 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_154 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_155 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_156 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_157 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_158 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_146 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_147 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_168 = self._io.read_bits_int_be(1) != 0
            self.datapool_paramvalid_169 = self._io.read_bits_int_be(1) != 0


    class PusHdr(KaitaiStruct):

        class Tmtc(Enum):
            tm = 0
            tc = 1
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_no = self._io.read_bits_int_be(3)
            self.type_indicator = KaitaiStream.resolve_enum(Eirsat1.PusHdr.Tmtc, self._io.read_bits_int_be(1))
            self.sec_hdr_flag = self._io.read_bits_int_be(1) != 0
            self.apid = self._io.read_bits_int_be(11)
            self.grouping_flags = self._io.read_bits_int_be(2)
            self.src_seq = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_data_len = self._io.read_u2be()


    class PusDataField(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._parent.header.type_indicator
            if _on == Eirsat1.PusHdr.Tmtc.tm:
                self.sec_hdr = Eirsat1.TmSecHdr(self._io, self, self._root)
            elif _on == Eirsat1.PusHdr.Tmtc.tc:
                self.sec_hdr = Eirsat1.TcSecHdr(self._io, self, self._root)
            self.service = self._io.read_u1()
            self.subservice = self._io.read_u1()
            _on = ((self.service << 8) + self.subservice)
            if _on == 793:
                self.data = Eirsat1.Housekeeping(self._io, self, self._root)


    class TmSecHdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pus_version = self._io.read_bits_int_be(4)


    class TcSecHdr(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pus_version = self._io.read_bits_int_be(4)
            self.ack = self._io.read_bits_int_be(4)


    class PusPkt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Eirsat1.PusHdr(self._io, self, self._root)
            self._raw_data_field = self._io.read_bytes((self.header.packet_data_len - 1))
            _io__raw_data_field = KaitaiStream(BytesIO(self._raw_data_field))
            self.data_field = Eirsat1.PusDataField(_io__raw_data_field, self, self._root)
            self.packet_error_control = self._io.read_bytes(2)


    class HkStruct00(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_satellitestring_0 = (self._io.read_bytes(8)).decode(u"ascii")
            self.version_messagestring_0 = (self._io.read_bytes(32)).decode(u"ascii")
            self.core_obt_time_0 = self._io.read_bits_int_be(32)
            self.core_obt_uptime_0 = self._io.read_bits_int_be(32)
            self.mission_separationsequence_state_0 = self._io.read_bits_int_be(8)
            self.mission_separationsequence_antswitchesstatuses_0_3_uhf_minusy = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_2_vhf_minusx = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_1_uhf_plusy = self._io.read_bits_int_be(1) != 0
            self.mission_separationsequence_antswitchesstatuses_0_0_vhf_plusx = self._io.read_bits_int_be(1) != 0
            self.platform_obc_obc_currbootimage_0 = self._io.read_bits_int_be(8)
            self.comms_hmac_sequencenumber_0 = self._io.read_bits_int_be(24)
            self.platform_bat_batterycurrent_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batteryvoltage_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_0 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_1 = self._io.read_bits_int_be(10)
            self.platform_bat_batterytemperature_2 = self._io.read_bits_int_be(10)
            self.platform_bat_batterycurrentdir_0 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_0 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_1 = self._io.read_bits_int_be(1) != 0
            self.platform_bat_packedheaterstatus_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_9 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_8 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_7 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_6 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_5 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_4 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_3 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_1 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_actualswitchstatesbitmap_0_0 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_9 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_8 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_7 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_6 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_5 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_4 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_3 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_2 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_1 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_switchovercurrentbitmap_0_0 = self._io.read_bits_int_be(1) != 0
            self.platform_eps_board_temperature_0 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_0_battery = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_1_3v3 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_2_5v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_voltages_3_12v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_0_battery = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_1_3v3 = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_2_5v = self._io.read_bits_int_be(10)
            self.platform_eps_bus_currents_3_12v = self._io.read_bits_int_be(10)
            self.platform_adcs_array_temperature_1_plusx = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_4_minusx = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_3_plusy = self._io.read_bits_int_be(16)
            self.platform_adcs_array_temperature_2_minusy = self._io.read_bits_int_be(16)
            self.platform_eps_solar_array_currents_1_plusx = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_4_minusx = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_3_plusy = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_currents_2_minusy = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_0 = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_1 = self._io.read_bits_int_be(10)
            self.platform_eps_solar_array_voltages_2 = self._io.read_bits_int_be(10)
            self.platform_adcs_packedadcsmode_0 = self._io.read_bits_int_be(8)
            self.platform_adcs_executioncount_0 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_0 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_1 = self._io.read_bits_int_be(16)
            self.platform_adcs_rawgyrorate_2 = self._io.read_bits_int_be(16)
            self.platform_adcs_fss1alphaangle_0 = self._io.read_bits_int_be(32)
            self.platform_adcs_fss1betaangle_0 = self._io.read_bits_int_be(32)
            self.platform_cmc_mode_0 = self._io.read_bits_int_be(2)
            self.platform_cmc_beaconenable_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txtransparent_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txconvenabled_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_txpower_0 = self._io.read_bits_int_be(2)
            self.platform_cmc_rxlock_0 = self._io.read_bits_int_be(1) != 0
            self.platform_cmc_rxrssi_0 = self._io.read_bits_int_be(12)
            self.platform_cmc_rxfrequencyoffset_0 = self._io.read_bits_int_be(10)
            self.platform_cmc_rxpacketcount_0 = self._io.read_bits_int_be(16)
            self.platform_cmc_temperaturepa_0 = self._io.read_bits_int_be(8)
            self.platform_cmc_current5v_0 = self._io.read_bits_int_be(16)
            self.platform_cmc_voltage5v_0 = self._io.read_bits_int_be(13)
            self.platform_cmc_rxcrcerrorcount_0 = self._io.read_bits_int_be(16)
            self.core_eventdispatcher_eventcount_0 = self._io.read_bits_int_be(32)
            self.core_eventdispatcher_lastevent_0_severity = self._io.read_bits_int_be(2)
            self.core_eventdispatcher_lastevent_0_event_id = self._io.read_bits_int_be(14)
            self.core_eventdispatcher_lastevent_0_event_source_id = self._io.read_bits_int_be(16)
            self.core_eventdispatcher_lastevent_0_info = self._io.read_bits_int_be(32)
            self.padding = self._io.read_bits_int_be(7)


    class Housekeeping(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_structure_id = self._io.read_u1()
            _on = self.hk_structure_id
            if _on == 0:
                self._raw_hk_data = self._io.read_bytes_full()
                _io__raw_hk_data = KaitaiStream(BytesIO(self._raw_hk_data))
                self.hk_data = Eirsat1.HkStruct00(_io__raw_hk_data, self, self._root)
            elif _on == 2:
                self._raw_hk_data = self._io.read_bytes_full()
                _io__raw_hk_data = KaitaiStream(BytesIO(self._raw_hk_data))
                self.hk_data = Eirsat1.HkStruct02(_io__raw_hk_data, self, self._root)
            else:
                self.hk_data = self._io.read_bytes_full()


    class CcsdsFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.header = Eirsat1.CcsdsHeader(self._io, self, self._root)
            self.packets = []
            i = 0
            while not self._io.is_eof():
                self.packets.append(Eirsat1.PusPkt(self._io, self, self._root))
                i += 1




