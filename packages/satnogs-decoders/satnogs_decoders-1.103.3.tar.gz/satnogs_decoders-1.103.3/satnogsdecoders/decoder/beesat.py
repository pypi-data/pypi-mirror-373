# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Beesat(KaitaiStruct):
    """:field sync: master_frame.sync
    :field contrl0: master_frame.contrl0
    :field contrl1: master_frame.contrl1
    :field calsgn: master_frame.calsgn
    :field crcsgn: master_frame.crcsgn
    :field asm: master_frame.packet_type.transfer_frame0.asm
    :field tfvn: master_frame.packet_type.transfer_frame0.tfvn
    :field scid: master_frame.packet_type.transfer_frame0.scid
    :field vcid: master_frame.packet_type.transfer_frame0.vcid
    :field ocff: master_frame.packet_type.transfer_frame0.ocff
    :field mcfc: master_frame.packet_type.transfer_frame0.mcfc
    :field vcfc: master_frame.packet_type.transfer_frame0.vcfc
    :field tf_shf: master_frame.packet_type.transfer_frame0.tf_shf
    :field sync_flag: master_frame.packet_type.transfer_frame0.sync_flag
    :field pof: master_frame.packet_type.transfer_frame0.pof
    :field slid: master_frame.packet_type.transfer_frame0.slid
    :field fhp: master_frame.packet_type.transfer_frame0.fhp
    :field pvn: master_frame.packet_type.transfer_frame0.source_packet.pvn
    :field pt: master_frame.packet_type.transfer_frame0.source_packet.pt
    :field shf: master_frame.packet_type.transfer_frame0.source_packet.shf
    :field apid: master_frame.packet_type.transfer_frame0.source_packet.apid
    :field sequence_flag: master_frame.packet_type.transfer_frame0.source_packet.sequence_flag
    :field psc: master_frame.packet_type.transfer_frame0.source_packet.psc
    :field pdl: master_frame.packet_type.transfer_frame0.source_packet.pdl
    :field value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused00.value
    :field unused01_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused01.value
    :field unused02_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused02.value
    :field unused03_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused03.value
    :field unused04_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused04.value
    :field unused05_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused05.value
    :field unused06_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused06.value
    :field unused07_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused07.value
    :field unused08_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused08.value
    :field unused09_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused09.value
    :field unused10_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused10.value
    :field unused11_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused11.value
    :field unused12_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused12.value
    :field unused13_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused13.value
    :field unused14_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused14.value
    :field unused15_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused15.value
    :field unused16_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.unused16.value
    :field analog_value_01_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_01.value
    :field psant0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psant0
    :field psant1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psant1
    :field pscom0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pscom0
    :field pscom1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pscom1
    :field analog_value_02_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_02.value
    :field psuhf0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psuhf0
    :field psuhf1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psuhf1
    :field pstnc0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pstnc0
    :field pstnc1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pstnc1
    :field analog_value_03_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_03.value
    :field psgyro: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psgyro
    :field psmcsx: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psmcsx
    :field psmcsy: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psmcsy
    :field psmcsz: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psmcsz
    :field analog_value_04_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_04.value
    :field pswhee: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pswhee
    :field psobc0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psobc0
    :field psobc1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psobc1
    :field pspdh0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pspdh0
    :field analog_value_05_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_05.value
    :field pscam0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pscam0
    :field pssuns: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pssuns
    :field psmfs0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psmfs0
    :field psmfs1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psmfs1
    :field analog_value_06_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_06.value
    :field pstemp: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pstemp
    :field pscan0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pscan0
    :field pscan1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pscan1
    :field psccw0: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psccw0
    :field analog_value_07_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_07.value
    :field psccw1: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.psccw1
    :field ps5vcn: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ps5vcn
    :field reserved00: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved00
    :field pcbobc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcbobc
    :field analog_value_08_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_08.value
    :field pcbext: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcbext
    :field pcch00: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch00
    :field pcch01: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch01
    :field pcch02: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch02
    :field analog_value_09_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_09.value
    :field pcch03: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch03
    :field pcch04: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch04
    :field pcch05: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch05
    :field pcch06: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch06
    :field analog_value_10: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_10
    :field pcch07: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch07
    :field pcch08: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch08
    :field pcch09: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch09
    :field pcch10: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch10
    :field analog_value_11: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_11
    :field pcch11: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch11
    :field pcch12: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch12
    :field pcch13: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch13
    :field pcch14: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch14
    :field analog_value_12_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_12.value
    :field pcch15: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch15
    :field pcch16: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch16
    :field pcch17: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch17
    :field pcch18: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch18
    :field analog_value_13_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_13.value
    :field pcch19: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch19
    :field pcch20: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch20
    :field pcch21: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch21
    :field pcch22: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch22
    :field analog_value_14_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_14.value
    :field pcch23: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch23
    :field pcch24: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch24
    :field pcch25: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch25
    :field pcch26: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch26
    :field analog_value_15_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_15.value
    :field tcrxid: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.tcrxid
    :field obcaid: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.obcaid
    :field tmtxrt: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.tmtxrt
    :field pcch27: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch27
    :field analog_value_16_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_16.value
    :field pcch28: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch28
    :field pcch29: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch29
    :field pcch30: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch30
    :field pcch31: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch31
    :field ccticc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccticc
    :field cctctt: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.cctctt
    :field ccetcs: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccetcs
    :field cceimc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.cceimc
    :field ccettc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccettc
    :field ccettg: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccettg
    :field ccetcc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccetcc
    :field tcrxqu_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.tcrxqu.value
    :field tcfrcp: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.tcfrcp
    :field tmhkur: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.tmhkur
    :field cstutc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.cstutc
    :field cstsys: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.cstsys
    :field obcbad: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.obcbad
    :field ceswmc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ceswmc
    :field reserved01: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved01
    :field beacon: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.beacon
    :field obcabc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.obcabc
    :field modobc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.modobc
    :field ccecan: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.ccecan
    :field obccan: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.obccan
    :field pcsyst: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcsyst
    :field pcbcnt: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcbcnt
    :field pctxec: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pctxec
    :field pcrxec: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcrxec
    :field pcoffc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcoffc
    :field pcackc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcackc
    :field pcch32: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch32
    :field pcch33: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch33
    :field pcch34: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch34
    :field pcch35: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch35
    :field pcch36: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch36
    :field pcch37: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch37
    :field pcch38: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch38
    :field pcch39: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch39
    :field pcch40: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch40
    :field pcch41: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.pcch41
    :field reserved02: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved02
    :field analog_value_17_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_17.value
    :field reserved03: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved03
    :field analog_value_18_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_18.value
    :field reserved04: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved04
    :field analog_value_19_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_19.value
    :field reserved05: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved05
    :field acswhx: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acswhx
    :field acswhy: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acswhy
    :field acswhz: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acswhz
    :field acsq00_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsq00.value
    :field acsq01_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsq01.value
    :field acsq02_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsq02.value
    :field acsq03_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsq03.value
    :field acssux_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acssux.value
    :field acssuy_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acssuy.value
    :field acssuz_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acssuz.value
    :field acsm0x_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm0x.value
    :field acsm0y_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm0y.value
    :field acsm0z_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm0z.value
    :field acsm1x_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm1x.value
    :field acsm1y_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm1y.value
    :field acsm1z_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsm1z.value
    :field acsmod: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsmod
    :field acsgsc: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsgsc
    :field acsshd: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsshd
    :field reserved06: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved06
    :field acserr: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acserr
    :field acsgyx_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsgyx.value
    :field acsgyy_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsgyy.value
    :field acsgyz_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.acsgyz.value
    :field analog_value_20_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_20.value
    :field reserved07: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved07
    :field analog_value_21_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_21.value
    :field reserved08: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved08
    :field analog_value_22_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_22.value
    :field reserved09: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved09
    :field analog_value_23_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_23.value
    :field reserved10: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved10
    :field analog_value_24_value: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.analog_value_24.value
    :field reserved11: master_frame.packet_type.transfer_frame0.source_packet.telemetry_values.reserved11
    :field fecf: master_frame.packet_type.transfer_frame0.fecf
    :field two_byte_combined: master_frame.packet_type.transfer_frame0.two_byte_combined
    :field transfer_frame1_asm: master_frame.packet_type.transfer_frame1.asm
    :field transfer_frame1_tfvn: master_frame.packet_type.transfer_frame1.tfvn
    :field transfer_frame1_scid: master_frame.packet_type.transfer_frame1.scid
    :field transfer_frame1_vcid: master_frame.packet_type.transfer_frame1.vcid
    :field transfer_frame1_ocff: master_frame.packet_type.transfer_frame1.ocff
    :field transfer_frame1_mcfc: master_frame.packet_type.transfer_frame1.mcfc
    :field transfer_frame1_vcfc: master_frame.packet_type.transfer_frame1.vcfc
    :field transfer_frame1_tf_shf: master_frame.packet_type.transfer_frame1.tf_shf
    :field transfer_frame1_sync_flag: master_frame.packet_type.transfer_frame1.sync_flag
    :field transfer_frame1_pof: master_frame.packet_type.transfer_frame1.pof
    :field transfer_frame1_slid: master_frame.packet_type.transfer_frame1.slid
    :field transfer_frame1_fhp: master_frame.packet_type.transfer_frame1.fhp
    :field transfer_frame1_pvn: master_frame.packet_type.transfer_frame1.source_packet.pvn
    :field transfer_frame1_pt: master_frame.packet_type.transfer_frame1.source_packet.pt
    :field transfer_frame1_shf: master_frame.packet_type.transfer_frame1.source_packet.shf
    :field transfer_frame1_apid: master_frame.packet_type.transfer_frame1.source_packet.apid
    :field transfer_frame1_sequence_flag: master_frame.packet_type.transfer_frame1.source_packet.sequence_flag
    :field transfer_frame1_psc: master_frame.packet_type.transfer_frame1.source_packet.psc
    :field transfer_frame1_pdl: master_frame.packet_type.transfer_frame1.source_packet.pdl
    :field transfer_frame1_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused00.value
    :field transfer_frame1_unused01_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused01.value
    :field transfer_frame1_unused02_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused02.value
    :field transfer_frame1_unused03_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused03.value
    :field transfer_frame1_unused04_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused04.value
    :field transfer_frame1_unused05_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused05.value
    :field transfer_frame1_unused06_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused06.value
    :field transfer_frame1_unused07_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused07.value
    :field transfer_frame1_unused08_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused08.value
    :field transfer_frame1_unused09_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused09.value
    :field transfer_frame1_unused10_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused10.value
    :field transfer_frame1_unused11_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused11.value
    :field transfer_frame1_unused12_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused12.value
    :field transfer_frame1_unused13_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused13.value
    :field transfer_frame1_unused14_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused14.value
    :field transfer_frame1_unused15_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused15.value
    :field transfer_frame1_unused16_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.unused16.value
    :field transfer_frame1_analog_value_01_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_01.value
    :field transfer_frame1_psant0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psant0
    :field transfer_frame1_psant1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psant1
    :field transfer_frame1_pscom0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pscom0
    :field transfer_frame1_pscom1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pscom1
    :field transfer_frame1_analog_value_02_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_02.value
    :field transfer_frame1_psuhf0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psuhf0
    :field transfer_frame1_psuhf1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psuhf1
    :field transfer_frame1_pstnc0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pstnc0
    :field transfer_frame1_pstnc1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pstnc1
    :field transfer_frame1_analog_value_03_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_03.value
    :field transfer_frame1_psgyro: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psgyro
    :field transfer_frame1_psmcsx: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psmcsx
    :field transfer_frame1_psmcsy: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psmcsy
    :field transfer_frame1_psmcsz: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psmcsz
    :field transfer_frame1_analog_value_04_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_04.value
    :field transfer_frame1_pswhee: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pswhee
    :field transfer_frame1_psobc0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psobc0
    :field transfer_frame1_psobc1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psobc1
    :field transfer_frame1_pspdh0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pspdh0
    :field transfer_frame1_analog_value_05_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_05.value
    :field transfer_frame1_pscam0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pscam0
    :field transfer_frame1_pssuns: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pssuns
    :field transfer_frame1_psmfs0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psmfs0
    :field transfer_frame1_psmfs1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psmfs1
    :field transfer_frame1_analog_value_06_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_06.value
    :field transfer_frame1_pstemp: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pstemp
    :field transfer_frame1_pscan0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pscan0
    :field transfer_frame1_pscan1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pscan1
    :field transfer_frame1_psccw0: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psccw0
    :field transfer_frame1_analog_value_07_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_07.value
    :field transfer_frame1_psccw1: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.psccw1
    :field transfer_frame1_ps5vcn: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ps5vcn
    :field transfer_frame1_reserved00: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved00
    :field transfer_frame1_pcbobc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcbobc
    :field transfer_frame1_analog_value_08_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_08.value
    :field transfer_frame1_pcbext: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcbext
    :field transfer_frame1_pcch00: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch00
    :field transfer_frame1_pcch01: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch01
    :field transfer_frame1_pcch02: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch02
    :field transfer_frame1_analog_value_09_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_09.value
    :field transfer_frame1_pcch03: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch03
    :field transfer_frame1_pcch04: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch04
    :field transfer_frame1_pcch05: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch05
    :field transfer_frame1_pcch06: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch06
    :field transfer_frame1_analog_value_10: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_10
    :field transfer_frame1_pcch07: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch07
    :field transfer_frame1_pcch08: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch08
    :field transfer_frame1_pcch09: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch09
    :field transfer_frame1_pcch10: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch10
    :field transfer_frame1_analog_value_11: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_11
    :field transfer_frame1_pcch11: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch11
    :field transfer_frame1_pcch12: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch12
    :field transfer_frame1_pcch13: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch13
    :field transfer_frame1_pcch14: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch14
    :field transfer_frame1_analog_value_12_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_12.value
    :field transfer_frame1_pcch15: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch15
    :field transfer_frame1_pcch16: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch16
    :field transfer_frame1_pcch17: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch17
    :field transfer_frame1_pcch18: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch18
    :field transfer_frame1_analog_value_13_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_13.value
    :field transfer_frame1_pcch19: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch19
    :field transfer_frame1_pcch20: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch20
    :field transfer_frame1_pcch21: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch21
    :field transfer_frame1_pcch22: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch22
    :field transfer_frame1_analog_value_14_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_14.value
    :field transfer_frame1_pcch23: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch23
    :field transfer_frame1_pcch24: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch24
    :field transfer_frame1_pcch25: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch25
    :field transfer_frame1_pcch26: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch26
    :field transfer_frame1_analog_value_15_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_15.value
    :field transfer_frame1_tcrxid: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.tcrxid
    :field transfer_frame1_obcaid: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.obcaid
    :field transfer_frame1_tmtxrt: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.tmtxrt
    :field transfer_frame1_pcch27: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch27
    :field transfer_frame1_analog_value_16_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_16.value
    :field transfer_frame1_pcch28: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch28
    :field transfer_frame1_pcch29: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch29
    :field transfer_frame1_pcch30: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch30
    :field transfer_frame1_pcch31: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch31
    :field transfer_frame1_ccticc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccticc
    :field transfer_frame1_cctctt: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.cctctt
    :field transfer_frame1_ccetcs: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccetcs
    :field transfer_frame1_cceimc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.cceimc
    :field transfer_frame1_ccettc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccettc
    :field transfer_frame1_ccettg: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccettg
    :field transfer_frame1_ccetcc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccetcc
    :field transfer_frame1_tcrxqu_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.tcrxqu.value
    :field transfer_frame1_tcfrcp: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.tcfrcp
    :field transfer_frame1_tmhkur: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.tmhkur
    :field transfer_frame1_cstutc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.cstutc
    :field transfer_frame1_cstsys: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.cstsys
    :field transfer_frame1_obcbad: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.obcbad
    :field transfer_frame1_ceswmc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ceswmc
    :field transfer_frame1_reserved01: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved01
    :field transfer_frame1_beacon: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.beacon
    :field transfer_frame1_obcabc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.obcabc
    :field transfer_frame1_modobc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.modobc
    :field transfer_frame1_ccecan: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.ccecan
    :field transfer_frame1_obccan: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.obccan
    :field transfer_frame1_pcsyst: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcsyst
    :field transfer_frame1_pcbcnt: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcbcnt
    :field transfer_frame1_pctxec: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pctxec
    :field transfer_frame1_pcrxec: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcrxec
    :field transfer_frame1_pcoffc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcoffc
    :field transfer_frame1_pcackc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcackc
    :field transfer_frame1_pcch32: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch32
    :field transfer_frame1_pcch33: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch33
    :field transfer_frame1_pcch34: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch34
    :field transfer_frame1_pcch35: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch35
    :field transfer_frame1_pcch36: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch36
    :field transfer_frame1_pcch37: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch37
    :field transfer_frame1_pcch38: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch38
    :field transfer_frame1_pcch39: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch39
    :field transfer_frame1_pcch40: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch40
    :field transfer_frame1_pcch41: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.pcch41
    :field transfer_frame1_reserved02: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved02
    :field transfer_frame1_analog_value_17_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_17.value
    :field transfer_frame1_reserved03: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved03
    :field transfer_frame1_analog_value_18_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_18.value
    :field transfer_frame1_reserved04: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved04
    :field transfer_frame1_analog_value_19_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_19.value
    :field transfer_frame1_reserved05: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved05
    :field transfer_frame1_acswhx: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acswhx
    :field transfer_frame1_acswhy: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acswhy
    :field transfer_frame1_acswhz: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acswhz
    :field transfer_frame1_acsq00_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsq00.value
    :field transfer_frame1_acsq01_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsq01.value
    :field transfer_frame1_acsq02_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsq02.value
    :field transfer_frame1_acsq03_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsq03.value
    :field transfer_frame1_acssux_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acssux.value
    :field transfer_frame1_acssuy_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acssuy.value
    :field transfer_frame1_acssuz_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acssuz.value
    :field transfer_frame1_acsm0x_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm0x.value
    :field transfer_frame1_acsm0y_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm0y.value
    :field transfer_frame1_acsm0z_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm0z.value
    :field transfer_frame1_acsm1x_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm1x.value
    :field transfer_frame1_acsm1y_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm1y.value
    :field transfer_frame1_acsm1z_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsm1z.value
    :field transfer_frame1_acsmod: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsmod
    :field transfer_frame1_acsgsc: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsgsc
    :field transfer_frame1_acsshd: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsshd
    :field transfer_frame1_reserved06: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved06
    :field transfer_frame1_acserr: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acserr
    :field transfer_frame1_acsgyx_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsgyx.value
    :field transfer_frame1_acsgyy_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsgyy.value
    :field transfer_frame1_acsgyz_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.acsgyz.value
    :field transfer_frame1_analog_value_20_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_20.value
    :field transfer_frame1_reserved07: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved07
    :field transfer_frame1_analog_value_21_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_21.value
    :field transfer_frame1_reserved08: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved08
    :field transfer_frame1_analog_value_22_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_22.value
    :field transfer_frame1_reserved09: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved09
    :field transfer_frame1_analog_value_23_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_23.value
    :field transfer_frame1_reserved10: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved10
    :field transfer_frame1_analog_value_24_value: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.analog_value_24.value
    :field transfer_frame1_reserved11: master_frame.packet_type.transfer_frame1.source_packet.telemetry_values.reserved11
    :field transfer_frame1_fecf: master_frame.packet_type.transfer_frame1.fecf
    :field transfer_frame1_two_byte_combined: master_frame.packet_type.transfer_frame1.two_byte_combined
    :field transfer_frame2_asm: master_frame.packet_type.transfer_frame2.asm
    :field transfer_frame2_tfvn: master_frame.packet_type.transfer_frame2.tfvn
    :field transfer_frame2_scid: master_frame.packet_type.transfer_frame2.scid
    :field transfer_frame2_vcid: master_frame.packet_type.transfer_frame2.vcid
    :field transfer_frame2_ocff: master_frame.packet_type.transfer_frame2.ocff
    :field transfer_frame2_mcfc: master_frame.packet_type.transfer_frame2.mcfc
    :field transfer_frame2_vcfc: master_frame.packet_type.transfer_frame2.vcfc
    :field transfer_frame2_tf_shf: master_frame.packet_type.transfer_frame2.tf_shf
    :field transfer_frame2_sync_flag: master_frame.packet_type.transfer_frame2.sync_flag
    :field transfer_frame2_pof: master_frame.packet_type.transfer_frame2.pof
    :field transfer_frame2_slid: master_frame.packet_type.transfer_frame2.slid
    :field transfer_frame2_fhp: master_frame.packet_type.transfer_frame2.fhp
    :field transfer_frame2_pvn: master_frame.packet_type.transfer_frame2.source_packet.pvn
    :field transfer_frame2_pt: master_frame.packet_type.transfer_frame2.source_packet.pt
    :field transfer_frame2_shf: master_frame.packet_type.transfer_frame2.source_packet.shf
    :field transfer_frame2_apid: master_frame.packet_type.transfer_frame2.source_packet.apid
    :field transfer_frame2_sequence_flag: master_frame.packet_type.transfer_frame2.source_packet.sequence_flag
    :field transfer_frame2_psc: master_frame.packet_type.transfer_frame2.source_packet.psc
    :field transfer_frame2_pdl: master_frame.packet_type.transfer_frame2.source_packet.pdl
    :field transfer_frame2_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused00.value
    :field transfer_frame2_unused01_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused01.value
    :field transfer_frame2_unused02_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused02.value
    :field transfer_frame2_unused03_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused03.value
    :field transfer_frame2_unused04_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused04.value
    :field transfer_frame2_unused05_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused05.value
    :field transfer_frame2_unused06_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused06.value
    :field transfer_frame2_unused07_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused07.value
    :field transfer_frame2_unused08_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused08.value
    :field transfer_frame2_unused09_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused09.value
    :field transfer_frame2_unused10_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused10.value
    :field transfer_frame2_unused11_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused11.value
    :field transfer_frame2_unused12_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused12.value
    :field transfer_frame2_unused13_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused13.value
    :field transfer_frame2_unused14_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused14.value
    :field transfer_frame2_unused15_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused15.value
    :field transfer_frame2_unused16_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.unused16.value
    :field transfer_frame2_analog_value_01_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_01.value
    :field transfer_frame2_psant0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psant0
    :field transfer_frame2_psant1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psant1
    :field transfer_frame2_pscom0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pscom0
    :field transfer_frame2_pscom1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pscom1
    :field transfer_frame2_analog_value_02_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_02.value
    :field transfer_frame2_psuhf0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psuhf0
    :field transfer_frame2_psuhf1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psuhf1
    :field transfer_frame2_pstnc0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pstnc0
    :field transfer_frame2_pstnc1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pstnc1
    :field transfer_frame2_analog_value_03_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_03.value
    :field transfer_frame2_psgyro: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psgyro
    :field transfer_frame2_psmcsx: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psmcsx
    :field transfer_frame2_psmcsy: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psmcsy
    :field transfer_frame2_psmcsz: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psmcsz
    :field transfer_frame2_analog_value_04_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_04.value
    :field transfer_frame2_pswhee: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pswhee
    :field transfer_frame2_psobc0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psobc0
    :field transfer_frame2_psobc1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psobc1
    :field transfer_frame2_pspdh0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pspdh0
    :field transfer_frame2_analog_value_05_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_05.value
    :field transfer_frame2_pscam0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pscam0
    :field transfer_frame2_pssuns: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pssuns
    :field transfer_frame2_psmfs0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psmfs0
    :field transfer_frame2_psmfs1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psmfs1
    :field transfer_frame2_analog_value_06_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_06.value
    :field transfer_frame2_pstemp: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pstemp
    :field transfer_frame2_pscan0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pscan0
    :field transfer_frame2_pscan1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pscan1
    :field transfer_frame2_psccw0: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psccw0
    :field transfer_frame2_analog_value_07_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_07.value
    :field transfer_frame2_psccw1: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.psccw1
    :field transfer_frame2_ps5vcn: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ps5vcn
    :field transfer_frame2_reserved00: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved00
    :field transfer_frame2_pcbobc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcbobc
    :field transfer_frame2_analog_value_08_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_08.value
    :field transfer_frame2_pcbext: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcbext
    :field transfer_frame2_pcch00: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch00
    :field transfer_frame2_pcch01: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch01
    :field transfer_frame2_pcch02: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch02
    :field transfer_frame2_analog_value_09_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_09.value
    :field transfer_frame2_pcch03: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch03
    :field transfer_frame2_pcch04: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch04
    :field transfer_frame2_pcch05: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch05
    :field transfer_frame2_pcch06: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch06
    :field transfer_frame2_analog_value_10: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_10
    :field transfer_frame2_pcch07: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch07
    :field transfer_frame2_pcch08: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch08
    :field transfer_frame2_pcch09: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch09
    :field transfer_frame2_pcch10: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch10
    :field transfer_frame2_analog_value_11: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_11
    :field transfer_frame2_pcch11: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch11
    :field transfer_frame2_pcch12: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch12
    :field transfer_frame2_pcch13: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch13
    :field transfer_frame2_pcch14: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch14
    :field transfer_frame2_analog_value_12_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_12.value
    :field transfer_frame2_pcch15: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch15
    :field transfer_frame2_pcch16: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch16
    :field transfer_frame2_pcch17: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch17
    :field transfer_frame2_pcch18: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch18
    :field transfer_frame2_analog_value_13_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_13.value
    :field transfer_frame2_pcch19: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch19
    :field transfer_frame2_pcch20: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch20
    :field transfer_frame2_pcch21: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch21
    :field transfer_frame2_pcch22: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch22
    :field transfer_frame2_analog_value_14_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_14.value
    :field transfer_frame2_pcch23: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch23
    :field transfer_frame2_pcch24: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch24
    :field transfer_frame2_pcch25: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch25
    :field transfer_frame2_pcch26: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch26
    :field transfer_frame2_analog_value_15_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_15.value
    :field transfer_frame2_tcrxid: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.tcrxid
    :field transfer_frame2_obcaid: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.obcaid
    :field transfer_frame2_tmtxrt: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.tmtxrt
    :field transfer_frame2_pcch27: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch27
    :field transfer_frame2_analog_value_16_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_16.value
    :field transfer_frame2_pcch28: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch28
    :field transfer_frame2_pcch29: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch29
    :field transfer_frame2_pcch30: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch30
    :field transfer_frame2_pcch31: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch31
    :field transfer_frame2_ccticc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccticc
    :field transfer_frame2_cctctt: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.cctctt
    :field transfer_frame2_ccetcs: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccetcs
    :field transfer_frame2_cceimc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.cceimc
    :field transfer_frame2_ccettc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccettc
    :field transfer_frame2_ccettg: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccettg
    :field transfer_frame2_ccetcc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccetcc
    :field transfer_frame2_tcrxqu_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.tcrxqu.value
    :field transfer_frame2_tcfrcp: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.tcfrcp
    :field transfer_frame2_tmhkur: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.tmhkur
    :field transfer_frame2_cstutc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.cstutc
    :field transfer_frame2_cstsys: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.cstsys
    :field transfer_frame2_obcbad: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.obcbad
    :field transfer_frame2_ceswmc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ceswmc
    :field transfer_frame2_reserved01: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved01
    :field transfer_frame2_beacon: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.beacon
    :field transfer_frame2_obcabc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.obcabc
    :field transfer_frame2_modobc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.modobc
    :field transfer_frame2_ccecan: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.ccecan
    :field transfer_frame2_obccan: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.obccan
    :field transfer_frame2_pcsyst: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcsyst
    :field transfer_frame2_pcbcnt: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcbcnt
    :field transfer_frame2_pctxec: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pctxec
    :field transfer_frame2_pcrxec: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcrxec
    :field transfer_frame2_pcoffc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcoffc
    :field transfer_frame2_pcackc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcackc
    :field transfer_frame2_pcch32: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch32
    :field transfer_frame2_pcch33: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch33
    :field transfer_frame2_pcch34: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch34
    :field transfer_frame2_pcch35: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch35
    :field transfer_frame2_pcch36: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch36
    :field transfer_frame2_pcch37: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch37
    :field transfer_frame2_pcch38: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch38
    :field transfer_frame2_pcch39: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch39
    :field transfer_frame2_pcch40: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch40
    :field transfer_frame2_pcch41: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.pcch41
    :field transfer_frame2_reserved02: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved02
    :field transfer_frame2_analog_value_17_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_17.value
    :field transfer_frame2_reserved03: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved03
    :field transfer_frame2_analog_value_18_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_18.value
    :field transfer_frame2_reserved04: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved04
    :field transfer_frame2_analog_value_19_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_19.value
    :field transfer_frame2_reserved05: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved05
    :field transfer_frame2_acswhx: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acswhx
    :field transfer_frame2_acswhy: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acswhy
    :field transfer_frame2_acswhz: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acswhz
    :field transfer_frame2_acsq00_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsq00.value
    :field transfer_frame2_acsq01_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsq01.value
    :field transfer_frame2_acsq02_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsq02.value
    :field transfer_frame2_acsq03_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsq03.value
    :field transfer_frame2_acssux_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acssux.value
    :field transfer_frame2_acssuy_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acssuy.value
    :field transfer_frame2_acssuz_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acssuz.value
    :field transfer_frame2_acsm0x_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm0x.value
    :field transfer_frame2_acsm0y_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm0y.value
    :field transfer_frame2_acsm0z_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm0z.value
    :field transfer_frame2_acsm1x_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm1x.value
    :field transfer_frame2_acsm1y_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm1y.value
    :field transfer_frame2_acsm1z_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsm1z.value
    :field transfer_frame2_acsmod: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsmod
    :field transfer_frame2_acsgsc: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsgsc
    :field transfer_frame2_acsshd: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsshd
    :field transfer_frame2_reserved06: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved06
    :field transfer_frame2_acserr: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acserr
    :field transfer_frame2_acsgyx_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsgyx.value
    :field transfer_frame2_acsgyy_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsgyy.value
    :field transfer_frame2_acsgyz_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.acsgyz.value
    :field transfer_frame2_analog_value_20_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_20.value
    :field transfer_frame2_reserved07: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved07
    :field transfer_frame2_analog_value_21_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_21.value
    :field transfer_frame2_reserved08: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved08
    :field transfer_frame2_analog_value_22_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_22.value
    :field transfer_frame2_reserved09: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved09
    :field transfer_frame2_analog_value_23_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_23.value
    :field transfer_frame2_reserved10: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved10
    :field transfer_frame2_analog_value_24_value: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.analog_value_24.value
    :field transfer_frame2_reserved11: master_frame.packet_type.transfer_frame2.source_packet.telemetry_values.reserved11
    :field transfer_frame2_fecf: master_frame.packet_type.transfer_frame2.fecf
    :field transfer_frame2_two_byte_combined: master_frame.packet_type.transfer_frame2.two_byte_combined
    :field transfer_frame3_asm: master_frame.packet_type.transfer_frame3.asm
    :field transfer_frame3_tfvn: master_frame.packet_type.transfer_frame3.tfvn
    :field transfer_frame3_scid: master_frame.packet_type.transfer_frame3.scid
    :field transfer_frame3_vcid: master_frame.packet_type.transfer_frame3.vcid
    :field transfer_frame3_ocff: master_frame.packet_type.transfer_frame3.ocff
    :field transfer_frame3_mcfc: master_frame.packet_type.transfer_frame3.mcfc
    :field transfer_frame3_vcfc: master_frame.packet_type.transfer_frame3.vcfc
    :field transfer_frame3_tf_shf: master_frame.packet_type.transfer_frame3.tf_shf
    :field transfer_frame3_sync_flag: master_frame.packet_type.transfer_frame3.sync_flag
    :field transfer_frame3_pof: master_frame.packet_type.transfer_frame3.pof
    :field transfer_frame3_slid: master_frame.packet_type.transfer_frame3.slid
    :field transfer_frame3_fhp: master_frame.packet_type.transfer_frame3.fhp
    :field transfer_frame3_pvn: master_frame.packet_type.transfer_frame3.source_packet.pvn
    :field transfer_frame3_pt: master_frame.packet_type.transfer_frame3.source_packet.pt
    :field transfer_frame3_shf: master_frame.packet_type.transfer_frame3.source_packet.shf
    :field transfer_frame3_apid: master_frame.packet_type.transfer_frame3.source_packet.apid
    :field transfer_frame3_sequence_flag: master_frame.packet_type.transfer_frame3.source_packet.sequence_flag
    :field transfer_frame3_psc: master_frame.packet_type.transfer_frame3.source_packet.psc
    :field transfer_frame3_pdl: master_frame.packet_type.transfer_frame3.source_packet.pdl
    :field transfer_frame3_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused00.value
    :field transfer_frame3_unused01_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused01.value
    :field transfer_frame3_unused02_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused02.value
    :field transfer_frame3_unused03_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused03.value
    :field transfer_frame3_unused04_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused04.value
    :field transfer_frame3_unused05_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused05.value
    :field transfer_frame3_unused06_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused06.value
    :field transfer_frame3_unused07_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused07.value
    :field transfer_frame3_unused08_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused08.value
    :field transfer_frame3_unused09_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused09.value
    :field transfer_frame3_unused10_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused10.value
    :field transfer_frame3_unused11_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused11.value
    :field transfer_frame3_unused12_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused12.value
    :field transfer_frame3_unused13_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused13.value
    :field transfer_frame3_unused14_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused14.value
    :field transfer_frame3_unused15_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused15.value
    :field transfer_frame3_unused16_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.unused16.value
    :field transfer_frame3_analog_value_01_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_01.value
    :field transfer_frame3_psant0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psant0
    :field transfer_frame3_psant1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psant1
    :field transfer_frame3_pscom0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pscom0
    :field transfer_frame3_pscom1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pscom1
    :field transfer_frame3_analog_value_02_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_02.value
    :field transfer_frame3_psuhf0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psuhf0
    :field transfer_frame3_psuhf1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psuhf1
    :field transfer_frame3_pstnc0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pstnc0
    :field transfer_frame3_pstnc1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pstnc1
    :field transfer_frame3_analog_value_03_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_03.value
    :field transfer_frame3_psgyro: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psgyro
    :field transfer_frame3_psmcsx: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psmcsx
    :field transfer_frame3_psmcsy: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psmcsy
    :field transfer_frame3_psmcsz: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psmcsz
    :field transfer_frame3_analog_value_04_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_04.value
    :field transfer_frame3_pswhee: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pswhee
    :field transfer_frame3_psobc0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psobc0
    :field transfer_frame3_psobc1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psobc1
    :field transfer_frame3_pspdh0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pspdh0
    :field transfer_frame3_analog_value_05_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_05.value
    :field transfer_frame3_pscam0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pscam0
    :field transfer_frame3_pssuns: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pssuns
    :field transfer_frame3_psmfs0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psmfs0
    :field transfer_frame3_psmfs1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psmfs1
    :field transfer_frame3_analog_value_06_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_06.value
    :field transfer_frame3_pstemp: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pstemp
    :field transfer_frame3_pscan0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pscan0
    :field transfer_frame3_pscan1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pscan1
    :field transfer_frame3_psccw0: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psccw0
    :field transfer_frame3_analog_value_07_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_07.value
    :field transfer_frame3_psccw1: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.psccw1
    :field transfer_frame3_ps5vcn: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ps5vcn
    :field transfer_frame3_reserved00: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved00
    :field transfer_frame3_pcbobc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcbobc
    :field transfer_frame3_analog_value_08_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_08.value
    :field transfer_frame3_pcbext: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcbext
    :field transfer_frame3_pcch00: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch00
    :field transfer_frame3_pcch01: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch01
    :field transfer_frame3_pcch02: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch02
    :field transfer_frame3_analog_value_09_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_09.value
    :field transfer_frame3_pcch03: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch03
    :field transfer_frame3_pcch04: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch04
    :field transfer_frame3_pcch05: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch05
    :field transfer_frame3_pcch06: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch06
    :field transfer_frame3_analog_value_10: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_10
    :field transfer_frame3_pcch07: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch07
    :field transfer_frame3_pcch08: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch08
    :field transfer_frame3_pcch09: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch09
    :field transfer_frame3_pcch10: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch10
    :field transfer_frame3_analog_value_11: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_11
    :field transfer_frame3_pcch11: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch11
    :field transfer_frame3_pcch12: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch12
    :field transfer_frame3_pcch13: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch13
    :field transfer_frame3_pcch14: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch14
    :field transfer_frame3_analog_value_12_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_12.value
    :field transfer_frame3_pcch15: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch15
    :field transfer_frame3_pcch16: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch16
    :field transfer_frame3_pcch17: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch17
    :field transfer_frame3_pcch18: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch18
    :field transfer_frame3_analog_value_13_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_13.value
    :field transfer_frame3_pcch19: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch19
    :field transfer_frame3_pcch20: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch20
    :field transfer_frame3_pcch21: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch21
    :field transfer_frame3_pcch22: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch22
    :field transfer_frame3_analog_value_14_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_14.value
    :field transfer_frame3_pcch23: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch23
    :field transfer_frame3_pcch24: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch24
    :field transfer_frame3_pcch25: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch25
    :field transfer_frame3_pcch26: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch26
    :field transfer_frame3_analog_value_15_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_15.value
    :field transfer_frame3_tcrxid: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.tcrxid
    :field transfer_frame3_obcaid: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.obcaid
    :field transfer_frame3_tmtxrt: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.tmtxrt
    :field transfer_frame3_pcch27: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch27
    :field transfer_frame3_analog_value_16_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_16.value
    :field transfer_frame3_pcch28: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch28
    :field transfer_frame3_pcch29: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch29
    :field transfer_frame3_pcch30: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch30
    :field transfer_frame3_pcch31: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch31
    :field transfer_frame3_ccticc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccticc
    :field transfer_frame3_cctctt: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.cctctt
    :field transfer_frame3_ccetcs: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccetcs
    :field transfer_frame3_cceimc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.cceimc
    :field transfer_frame3_ccettc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccettc
    :field transfer_frame3_ccettg: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccettg
    :field transfer_frame3_ccetcc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccetcc
    :field transfer_frame3_tcrxqu_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.tcrxqu.value
    :field transfer_frame3_tcfrcp: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.tcfrcp
    :field transfer_frame3_tmhkur: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.tmhkur
    :field transfer_frame3_cstutc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.cstutc
    :field transfer_frame3_cstsys: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.cstsys
    :field transfer_frame3_obcbad: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.obcbad
    :field transfer_frame3_ceswmc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ceswmc
    :field transfer_frame3_reserved01: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved01
    :field transfer_frame3_beacon: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.beacon
    :field transfer_frame3_obcabc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.obcabc
    :field transfer_frame3_modobc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.modobc
    :field transfer_frame3_ccecan: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.ccecan
    :field transfer_frame3_obccan: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.obccan
    :field transfer_frame3_pcsyst: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcsyst
    :field transfer_frame3_pcbcnt: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcbcnt
    :field transfer_frame3_pctxec: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pctxec
    :field transfer_frame3_pcrxec: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcrxec
    :field transfer_frame3_pcoffc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcoffc
    :field transfer_frame3_pcackc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcackc
    :field transfer_frame3_pcch32: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch32
    :field transfer_frame3_pcch33: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch33
    :field transfer_frame3_pcch34: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch34
    :field transfer_frame3_pcch35: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch35
    :field transfer_frame3_pcch36: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch36
    :field transfer_frame3_pcch37: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch37
    :field transfer_frame3_pcch38: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch38
    :field transfer_frame3_pcch39: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch39
    :field transfer_frame3_pcch40: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch40
    :field transfer_frame3_pcch41: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.pcch41
    :field transfer_frame3_reserved02: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved02
    :field transfer_frame3_analog_value_17_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_17.value
    :field transfer_frame3_reserved03: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved03
    :field transfer_frame3_analog_value_18_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_18.value
    :field transfer_frame3_reserved04: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved04
    :field transfer_frame3_analog_value_19_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_19.value
    :field transfer_frame3_reserved05: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved05
    :field transfer_frame3_acswhx: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acswhx
    :field transfer_frame3_acswhy: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acswhy
    :field transfer_frame3_acswhz: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acswhz
    :field transfer_frame3_acsq00_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsq00.value
    :field transfer_frame3_acsq01_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsq01.value
    :field transfer_frame3_acsq02_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsq02.value
    :field transfer_frame3_acsq03_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsq03.value
    :field transfer_frame3_acssux_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acssux.value
    :field transfer_frame3_acssuy_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acssuy.value
    :field transfer_frame3_acssuz_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acssuz.value
    :field transfer_frame3_acsm0x_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm0x.value
    :field transfer_frame3_acsm0y_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm0y.value
    :field transfer_frame3_acsm0z_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm0z.value
    :field transfer_frame3_acsm1x_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm1x.value
    :field transfer_frame3_acsm1y_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm1y.value
    :field transfer_frame3_acsm1z_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsm1z.value
    :field transfer_frame3_acsmod: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsmod
    :field transfer_frame3_acsgsc: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsgsc
    :field transfer_frame3_acsshd: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsshd
    :field transfer_frame3_reserved06: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved06
    :field transfer_frame3_acserr: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acserr
    :field transfer_frame3_acsgyx_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsgyx.value
    :field transfer_frame3_acsgyy_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsgyy.value
    :field transfer_frame3_acsgyz_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.acsgyz.value
    :field transfer_frame3_analog_value_20_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_20.value
    :field transfer_frame3_reserved07: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved07
    :field transfer_frame3_analog_value_21_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_21.value
    :field transfer_frame3_reserved08: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved08
    :field transfer_frame3_analog_value_22_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_22.value
    :field transfer_frame3_reserved09: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved09
    :field transfer_frame3_analog_value_23_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_23.value
    :field transfer_frame3_reserved10: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved10
    :field transfer_frame3_analog_value_24_value: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.analog_value_24.value
    :field transfer_frame3_reserved11: master_frame.packet_type.transfer_frame3.source_packet.telemetry_values.reserved11
    :field transfer_frame3_fecf: master_frame.packet_type.transfer_frame3.fecf
    :field transfer_frame3_two_byte_combined: master_frame.packet_type.transfer_frame3.two_byte_combined
    :field count: master_frame.packet_type.digipeater_info_block.count
    :field byte_count: master_frame.packet_type.digipeater_info_block.byte_count
    :field local_time: master_frame.packet_type.digipeater_info_block.local_time
    :field calsgn_snd: master_frame.packet_type.digipeater_info_block.calsgn_snd
    :field long_qth_field: master_frame.packet_type.digipeater_info_block.long_qth_field
    :field lat_qth_field: master_frame.packet_type.digipeater_info_block.lat_qth_field
    :field long_qth_square: master_frame.packet_type.digipeater_info_block.long_qth_square
    :field lat_qth_square: master_frame.packet_type.digipeater_info_block.lat_qth_square
    :field long_qth_subsquare: master_frame.packet_type.digipeater_info_block.long_qth_subsquare
    :field lat_qth_subsquare: master_frame.packet_type.digipeater_info_block.lat_qth_subsquare
    :field message: master_frame.packet_type.digipeater_message.message
    
    .. seealso::
       'https://www.tu.berlin/en/raumfahrttechnik/institute/amateur-radio'
       'https://www.static.tu.berlin/fileadmin/www/10002275/Amateur_Radio/BEESAT-1_Digipeater-Format.ods'
       'https://www.static.tu.berlin/fileadmin/www/10002275/Amateur_Radio/BEESAT-1_telemetry_format.pdf'
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.master_frame = Beesat.MasterFrame(self._io, self, self._root)

    class SourcePacket(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.pvn = self._io.read_bits_int_be(3)
            if not self.pvn == 0:
                raise kaitaistruct.ValidationNotEqualError(0, self.pvn, self._io, u"/types/source_packet/seq/0")
            self.pt = self._io.read_bits_int_be(1) != 0
            if not self.pt == False:
                raise kaitaistruct.ValidationNotEqualError(False, self.pt, self._io, u"/types/source_packet/seq/1")
            self.shf = self._io.read_bits_int_be(1) != 0
            if not self.shf == False:
                raise kaitaistruct.ValidationNotEqualError(False, self.shf, self._io, u"/types/source_packet/seq/2")
            self.apid = self._io.read_bits_int_le(11)
            self.sequence_flag = self._io.read_bits_int_be(2)
            self.psc = self._io.read_bits_int_be(14)
            self.pdl = self._io.read_bits_int_be(16)
            self._io.align_to_byte()
            _on = self._parent.two_byte_combined
            if _on == 65535:
                self.telemetry_values = Beesat.TelemetryValuesUnused(self._io, self, self._root)
            else:
                self.telemetry_values = Beesat.TelemetryValues(self._io, self, self._root)


    class Voltage1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.0033725265168795620437956204379562 * self.raw)
            return getattr(self, '_m_value', None)


    class Ampere0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.6103515625 * self.raw)
            return getattr(self, '_m_value', None)


    class Unused2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0 * self.raw)
            return getattr(self, '_m_value', None)


    class Acs4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((-0.0573 * self.raw) + 2.5210)
            return getattr(self, '_m_value', None)


    class Celsius0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((0.244140625 * self.raw) - 50)
            return getattr(self, '_m_value', None)


    class DigipeaterFrame(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.static.tu.berlin/fileadmin/www/10002275/Amateur_Radio/BEESAT-1_Digipeater-Format.ods
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.digipeater_info_block = Beesat.DigipeaterInfoBlock(self._io, self, self._root)
            self.digipeater_message = Beesat.DigipeaterMessage(self._io, self, self._root)


    class TelemetryTransferFrames(KaitaiStruct):
        """
        .. seealso::
           Source - https://www.static.tu.berlin/fileadmin/www/10002275/Amateur_Radio/BEESAT-1_telemetry_format.pdf
        """
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.transfer_frame0 = Beesat.TransferFrame(self._io, self, self._root)
            self.transfer_frame1 = Beesat.TransferFrame(self._io, self, self._root)
            self.transfer_frame2 = Beesat.TransferFrame(self._io, self, self._root)
            self.transfer_frame3 = Beesat.TransferFrame(self._io, self, self._root)


    class Unused8(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u8be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0 * self.raw)
            return getattr(self, '_m_value', None)


    class Unused4(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u4be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0 * self.raw)
            return getattr(self, '_m_value', None)


    class Celsius3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((0.48577 * self.raw) - 270.595)
            return getattr(self, '_m_value', None)


    class TelemetryValuesUnused(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unused00 = Beesat.Unused8(self._io, self, self._root)
            self.unused01 = Beesat.Unused8(self._io, self, self._root)
            self.unused02 = Beesat.Unused8(self._io, self, self._root)
            self.unused03 = Beesat.Unused8(self._io, self, self._root)
            self.unused04 = Beesat.Unused8(self._io, self, self._root)
            self.unused05 = Beesat.Unused8(self._io, self, self._root)
            self.unused06 = Beesat.Unused8(self._io, self, self._root)
            self.unused07 = Beesat.Unused8(self._io, self, self._root)
            self.unused08 = Beesat.Unused8(self._io, self, self._root)
            self.unused09 = Beesat.Unused8(self._io, self, self._root)
            self.unused10 = Beesat.Unused8(self._io, self, self._root)
            self.unused11 = Beesat.Unused8(self._io, self, self._root)
            self.unused12 = Beesat.Unused8(self._io, self, self._root)
            self.unused13 = Beesat.Unused8(self._io, self, self._root)
            self.unused14 = Beesat.Unused8(self._io, self, self._root)
            self.unused15 = Beesat.Unused4(self._io, self, self._root)
            self.unused16 = Beesat.Unused2(self._io, self, self._root)


    class Db0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_u1()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((0.0548780487 * self.raw) + 1.573172)
            return getattr(self, '_m_value', None)


    class Acs1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (10 * self.raw)
            return getattr(self, '_m_value', None)


    class TelemetryValues(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.analog_value_01 = Beesat.Voltage0(self._io, self, self._root)
            self.psant0 = self._io.read_bits_int_be(1) != 0
            self.psant1 = self._io.read_bits_int_be(1) != 0
            self.pscom0 = self._io.read_bits_int_be(1) != 0
            self.pscom1 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_02 = Beesat.Voltage1(self._io, self, self._root)
            self.psuhf0 = self._io.read_bits_int_be(1) != 0
            self.psuhf1 = self._io.read_bits_int_be(1) != 0
            self.pstnc0 = self._io.read_bits_int_be(1) != 0
            self.pstnc1 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_03 = Beesat.Voltage1(self._io, self, self._root)
            self.psgyro = self._io.read_bits_int_be(1) != 0
            self.psmcsx = self._io.read_bits_int_be(1) != 0
            self.psmcsy = self._io.read_bits_int_be(1) != 0
            self.psmcsz = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_04 = Beesat.Voltage0(self._io, self, self._root)
            self.pswhee = self._io.read_bits_int_be(1) != 0
            self.psobc0 = self._io.read_bits_int_be(1) != 0
            self.psobc1 = self._io.read_bits_int_be(1) != 0
            self.pspdh0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_05 = Beesat.Voltage2(self._io, self, self._root)
            self.pscam0 = self._io.read_bits_int_be(1) != 0
            self.pssuns = self._io.read_bits_int_be(1) != 0
            self.psmfs0 = self._io.read_bits_int_be(1) != 0
            self.psmfs1 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_06 = Beesat.Ampere0(self._io, self, self._root)
            self.pstemp = self._io.read_bits_int_be(1) != 0
            self.pscan0 = self._io.read_bits_int_be(1) != 0
            self.pscan1 = self._io.read_bits_int_be(1) != 0
            self.psccw0 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_07 = Beesat.Ampere0(self._io, self, self._root)
            self.psccw1 = self._io.read_bits_int_be(1) != 0
            self.ps5vcn = self._io.read_bits_int_be(1) != 0
            self.reserved00 = self._io.read_bits_int_be(1) != 0
            self.pcbobc = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_08 = Beesat.Celsius0(self._io, self, self._root)
            self.pcbext = self._io.read_bits_int_be(1) != 0
            self.pcch00 = self._io.read_bits_int_be(1) != 0
            self.pcch01 = self._io.read_bits_int_be(1) != 0
            self.pcch02 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_09 = Beesat.Celsius0(self._io, self, self._root)
            self.pcch03 = self._io.read_bits_int_be(1) != 0
            self.pcch04 = self._io.read_bits_int_be(1) != 0
            self.pcch05 = self._io.read_bits_int_be(1) != 0
            self.pcch06 = self._io.read_bits_int_be(1) != 0
            self.analog_value_10 = self._io.read_bits_int_be(12)
            self.pcch07 = self._io.read_bits_int_be(1) != 0
            self.pcch08 = self._io.read_bits_int_be(1) != 0
            self.pcch09 = self._io.read_bits_int_be(1) != 0
            self.pcch10 = self._io.read_bits_int_be(1) != 0
            self.analog_value_11 = self._io.read_bits_int_be(12)
            self.pcch11 = self._io.read_bits_int_be(1) != 0
            self.pcch12 = self._io.read_bits_int_be(1) != 0
            self.pcch13 = self._io.read_bits_int_be(1) != 0
            self.pcch14 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_12 = Beesat.Ampere1(self._io, self, self._root)
            self.pcch15 = self._io.read_bits_int_be(1) != 0
            self.pcch16 = self._io.read_bits_int_be(1) != 0
            self.pcch17 = self._io.read_bits_int_be(1) != 0
            self.pcch18 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_13 = Beesat.Celsius1(self._io, self, self._root)
            self.pcch19 = self._io.read_bits_int_be(1) != 0
            self.pcch20 = self._io.read_bits_int_be(1) != 0
            self.pcch21 = self._io.read_bits_int_be(1) != 0
            self.pcch22 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_14 = Beesat.Celsius1(self._io, self, self._root)
            self.pcch23 = self._io.read_bits_int_be(1) != 0
            self.pcch24 = self._io.read_bits_int_be(1) != 0
            self.pcch25 = self._io.read_bits_int_be(1) != 0
            self.pcch26 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_15 = Beesat.Celsius1(self._io, self, self._root)
            self.tcrxid = self._io.read_bits_int_be(1) != 0
            self.obcaid = self._io.read_bits_int_be(1) != 0
            self.tmtxrt = self._io.read_bits_int_be(1) != 0
            self.pcch27 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.analog_value_16 = Beesat.Ampere1(self._io, self, self._root)
            self.pcch28 = self._io.read_bits_int_be(1) != 0
            self.pcch29 = self._io.read_bits_int_be(1) != 0
            self.pcch30 = self._io.read_bits_int_be(1) != 0
            self.pcch31 = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.ccticc = self._io.read_u1()
            self.cctctt = self._io.read_u1()
            self.ccetcs = self._io.read_u1()
            self.cceimc = self._io.read_u1()
            self.ccettc = self._io.read_u1()
            self.ccettg = self._io.read_u1()
            self.ccetcc = self._io.read_u1()
            self.tcrxqu = Beesat.Db0(self._io, self, self._root)
            self.tcfrcp = self._io.read_u2be()
            self.tmhkur = self._io.read_u2be()
            self.cstutc = self._io.read_u4be()
            self.cstsys = self._io.read_u4be()
            self.obcbad = self._io.read_u1()
            self.ceswmc = self._io.read_u1()
            self.reserved01 = self._io.read_u1()
            self.beacon = self._io.read_u1()
            self.obcabc = self._io.read_u1()
            self.modobc = self._io.read_u1()
            self.ccecan = self._io.read_u1()
            self.obccan = self._io.read_u1()
            self.pcsyst = self._io.read_u2be()
            self.pcbcnt = self._io.read_u1()
            self.pctxec = self._io.read_u1()
            self.pcrxec = self._io.read_u1()
            self.pcoffc = self._io.read_u1()
            self.pcackc = self._io.read_u1()
            self.pcch32 = self._io.read_bits_int_be(1) != 0
            self.pcch33 = self._io.read_bits_int_be(1) != 0
            self.pcch34 = self._io.read_bits_int_be(1) != 0
            self.pcch35 = self._io.read_bits_int_be(1) != 0
            self.pcch36 = self._io.read_bits_int_be(1) != 0
            self.pcch37 = self._io.read_bits_int_be(1) != 0
            self.pcch38 = self._io.read_bits_int_be(1) != 0
            self.pcch39 = self._io.read_bits_int_be(1) != 0
            self.pcch40 = self._io.read_bits_int_be(1) != 0
            self.pcch41 = self._io.read_bits_int_be(1) != 0
            self.reserved02 = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.analog_value_17 = Beesat.Ampere1(self._io, self, self._root)
            self.reserved03 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_18 = Beesat.Celsius2(self._io, self, self._root)
            self.reserved04 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_19 = Beesat.Celsius1(self._io, self, self._root)
            self.reserved05 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.acswhx = self._io.read_s2be()
            self.acswhy = self._io.read_s2be()
            self.acswhz = self._io.read_s2be()
            self.acsq00 = Beesat.Acs0(self._io, self, self._root)
            self.acsq01 = Beesat.Acs0(self._io, self, self._root)
            self.acsq02 = Beesat.Acs0(self._io, self, self._root)
            self.acsq03 = Beesat.Acs0(self._io, self, self._root)
            self.acssux = Beesat.Acs0(self._io, self, self._root)
            self.acssuy = Beesat.Acs0(self._io, self, self._root)
            self.acssuz = Beesat.Acs0(self._io, self, self._root)
            self.acsm0x = Beesat.Acs1(self._io, self, self._root)
            self.acsm0y = Beesat.Acs1(self._io, self, self._root)
            self.acsm0z = Beesat.Acs1(self._io, self, self._root)
            self.acsm1x = Beesat.Acs1(self._io, self, self._root)
            self.acsm1y = Beesat.Acs1(self._io, self, self._root)
            self.acsm1z = Beesat.Acs1(self._io, self, self._root)
            self.acsmod = self._io.read_bits_int_be(4)
            self.acsgsc = self._io.read_bits_int_be(1) != 0
            self.acsshd = self._io.read_bits_int_be(1) != 0
            self.reserved06 = self._io.read_bits_int_be(2)
            self._io.align_to_byte()
            self.acserr = self._io.read_u1()
            self.acsgyx = Beesat.Acs2(self._io, self, self._root)
            self.acsgyy = Beesat.Acs3(self._io, self, self._root)
            self.acsgyz = Beesat.Acs4(self._io, self, self._root)
            self.analog_value_20 = Beesat.Celsius2(self._io, self, self._root)
            self.reserved07 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_21 = Beesat.Ampere2(self._io, self, self._root)
            self.reserved08 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_22 = Beesat.Ampere2(self._io, self, self._root)
            self.reserved09 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_23 = Beesat.Ampere2(self._io, self, self._root)
            self.reserved10 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.analog_value_24 = Beesat.Celsius3(self._io, self, self._root)
            self.reserved11 = self._io.read_bits_int_be(4)


    class Ampere2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.152587891 * self.raw)
            return getattr(self, '_m_value', None)


    class Acs0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.0001 * self.raw)
            return getattr(self, '_m_value', None)


    class Acs2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((0.0573 * self.raw) + 19.7097)
            return getattr(self, '_m_value', None)


    class DigipeaterInfoBlock(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.count = self._io.read_u2be()
            self.byte_count = self._io.read_u2be()
            self.local_time = self._io.read_u4be()
            self.calsgn_snd = (KaitaiStream.bytes_terminate(self._io.read_bytes(6), 0, False)).decode(u"ascii")
            self.long_qth_field = self._io.read_bits_int_be(6)
            self.lat_qth_field = self._io.read_bits_int_be(6)
            self.long_qth_square = self._io.read_bits_int_be(4)
            self.lat_qth_square = self._io.read_bits_int_be(4)
            self.long_qth_subsquare = self._io.read_bits_int_be(6)
            self.lat_qth_subsquare = self._io.read_bits_int_be(6)


    class Voltage2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.001220703125 * self.raw)
            return getattr(self, '_m_value', None)


    class MasterFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sync = self._io.read_u2be()
            self.contrl0 = self._io.read_u1()
            self.contrl1 = self._io.read_u1()
            self.calsgn = (KaitaiStream.bytes_terminate(self._io.read_bytes(6), 0, False)).decode(u"ascii")
            if not self.calsgn == u"DP0BEE":
                raise kaitaistruct.ValidationNotEqualError(u"DP0BEE", self.calsgn, self._io, u"/types/master_frame/seq/3")
            self.crcsgn = self._io.read_u2be()
            _on = self.contrl0
            if _on == 20:
                self.packet_type = Beesat.TelemetryTransferFrames(self._io, self, self._root)
            elif _on == 150:
                self.packet_type = Beesat.DigipeaterFrame(self._io, self, self._root)


    class DigipeaterMessage(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = self._io.read_bits_int_be(1296)


    class Ampere1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.30517578125 * self.raw)
            return getattr(self, '_m_value', None)


    class TransferFrame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.asm = self._io.read_bits_int_be(32)
            if not self.asm == 449838109:
                raise kaitaistruct.ValidationNotEqualError(449838109, self.asm, self._io, u"/types/transfer_frame/seq/0")
            self.tfvn = self._io.read_bits_int_be(2)
            self.scid = self._io.read_bits_int_be(10)
            self.vcid = self._io.read_bits_int_be(3)
            self.ocff = self._io.read_bits_int_be(1) != 0
            self._io.align_to_byte()
            self.mcfc = self._io.read_u1()
            self.vcfc = self._io.read_u1()
            self.tf_shf = self._io.read_bits_int_be(1) != 0
            if not self.tf_shf == False:
                raise kaitaistruct.ValidationNotEqualError(False, self.tf_shf, self._io, u"/types/transfer_frame/seq/7")
            self.sync_flag = self._io.read_bits_int_be(1) != 0
            if not self.sync_flag == False:
                raise kaitaistruct.ValidationNotEqualError(False, self.sync_flag, self._io, u"/types/transfer_frame/seq/8")
            self.pof = self._io.read_bits_int_be(1) != 0
            if not self.pof == False:
                raise kaitaistruct.ValidationNotEqualError(False, self.pof, self._io, u"/types/transfer_frame/seq/9")
            self.slid = self._io.read_bits_int_be(2)
            if not self.slid == 3:
                raise kaitaistruct.ValidationNotEqualError(3, self.slid, self._io, u"/types/transfer_frame/seq/10")
            self.fhp = self._io.read_bits_int_be(11)
            if not self.fhp == 0:
                raise kaitaistruct.ValidationNotEqualError(0, self.fhp, self._io, u"/types/transfer_frame/seq/11")
            self._io.align_to_byte()
            self.source_packet = Beesat.SourcePacket(self._io, self, self._root)
            self.fecf = self._io.read_u2be()

        @property
        def two_byte_combined(self):
            """combine tfvn, scid, vcid and ocff to two bytes in order to check whether offline transfer frame contains any valid data, does not contain any if these bytes are FFFF."""
            if hasattr(self, '_m_two_byte_combined'):
                return self._m_two_byte_combined

            self._m_two_byte_combined = ((((self.tfvn << 14) | (self.scid << 4)) | (self.vcid << 1)) | int(self.ocff))
            return getattr(self, '_m_two_byte_combined', None)


    class Celsius2(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.125 * self.raw)
            return getattr(self, '_m_value', None)


    class Acs3(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_s2be()

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((-0.0573 * self.raw) + 21.9443)
            return getattr(self, '_m_value', None)


    class Celsius1(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = ((0.06103515625 * self.raw) - 50)
            return getattr(self, '_m_value', None)


    class Voltage0(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.raw = self._io.read_bits_int_be(12)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (0.001619779146 * self.raw)
            return getattr(self, '_m_value', None)



