# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Eshail2(KaitaiStruct):
    """:field ao40_beacon_type: ao40_frame.ao40_coding.ao40_beacon_type
    :field ao40_message_line1: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line1
    :field ao40_message_line2: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line2
    :field ao40_message_line3: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line3
    :field ao40_message_line4: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line4
    :field ao40_message_line5: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line5
    :field ao40_message_line6: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line6
    :field ao40_message_line7: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line7
    :field ao40_message_line8: ao40_frame.ao40_coding.ao40_beacon_data.ao40_message_line8
    :field uptime: ao40_frame.ao40_coding.ao40_beacon_data.uptime
    :field commands: ao40_frame.ao40_coding.ao40_beacon_data.commands
    :field leila_req: ao40_frame.ao40_coding.ao40_beacon_data.leila_req
    :field leila_act: ao40_frame.ao40_coding.ao40_beacon_data.leila_act
    :field temperature: ao40_frame.ao40_coding.ao40_beacon_data.temperature
    :field volt_1: ao40_frame.ao40_coding.ao40_beacon_data.volt_1
    :field volt_2: ao40_frame.ao40_coding.ao40_beacon_data.volt_2
    :field volt_3: ao40_frame.ao40_coding.ao40_beacon_data.volt_3
    :field volt_4: ao40_frame.ao40_coding.ao40_beacon_data.volt_4
    :field volt_5: ao40_frame.ao40_coding.ao40_beacon_data.volt_5
    :field volt_6: ao40_frame.ao40_coding.ao40_beacon_data.volt_6
    :field volt_7: ao40_frame.ao40_coding.ao40_beacon_data.volt_7
    :field volt_8: ao40_frame.ao40_coding.ao40_beacon_data.volt_8
    :field volt_9: ao40_frame.ao40_coding.ao40_beacon_data.volt_9
    
    .. seealso::
       Source - https://amsat-dl.org/wp-content/uploads/2019/01/tlmspec.pdf
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.ao40_frame = Eshail2.Ao40Frame(self._io, self, self._root)

    class Ao40FecMessageSpare(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40Frame(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self._root.frame_length
            if _on == 256:
                self.ao40_coding = Eshail2.Ao40FrameFec(self._io, self, self._root)
            elif _on == 514:
                self.ao40_coding = Eshail2.Ao40FrameUncoded(self._io, self, self._root)


    class Ao40CommandResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FrameUncoded(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.ao40_beacon_type
            if _on == 77:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 69:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 88:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 78:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 65:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 76:
                self.ao40_beacon_data = Eshail2.Ao40MessageL(self._io, self, self._root)
            elif _on == 68:
                self.ao40_beacon_data = Eshail2.Ao40MessageSpare(self._io, self, self._root)
            elif _on == 75:
                self.ao40_beacon_data = Eshail2.Ao40MessageK(self._io, self, self._root)
            else:
                self.ao40_beacon_data = Eshail2.Ao40CommandResponse(self._io, self, self._root)
            self.crc = self._io.read_u2be()

        @property
        def ao40_beacon_type(self):
            if hasattr(self, '_m_ao40_beacon_type'):
                return self._m_ao40_beacon_type

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_ao40_beacon_type = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_ao40_beacon_type', None)


    class Ao40FecMessageL(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FrameFec(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            _on = self.ao40_beacon_type
            if _on == 77:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 69:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 88:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 78:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 65:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 76:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageL(self._io, self, self._root)
            elif _on == 68:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageSpare(self._io, self, self._root)
            elif _on == 75:
                self.ao40_beacon_data = Eshail2.Ao40FecMessageK(self._io, self, self._root)
            else:
                self.ao40_beacon_data = Eshail2.Ao40FecCommandResponse(self._io, self, self._root)

        @property
        def ao40_beacon_type(self):
            if hasattr(self, '_m_ao40_beacon_type'):
                return self._m_ao40_beacon_type

            _pos = self._io.pos()
            self._io.seek(0)
            self._m_ao40_beacon_type = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_ao40_beacon_type', None)


    class Ao40MessageSpare(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageL(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40FecMessageK(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")

        @property
        def tfl_str(self):
            if hasattr(self, '_m_tfl_str'):
                return self._m_tfl_str

            _pos = self._io.pos()
            self._io.seek(201)
            self._m_tfl_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfl_str', None)

        @property
        def volts_str_9(self):
            if hasattr(self, '_m_volts_str_9'):
                return self._m_volts_str_9

            _pos = self._io.pos()
            self._io.seek(182)
            self._m_volts_str_9 = []
            for i in range(3):
                self._m_volts_str_9.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_9', None)

        @property
        def leila_act(self):
            if hasattr(self, '_m_leila_act'):
                return self._m_leila_act

            self._m_leila_act = self.leila_active_str > 48
            return getattr(self, '_m_leila_act', None)

        @property
        def volt_3(self):
            if hasattr(self, '_m_volt_3'):
                return self._m_volt_3

            self._m_volt_3 = (((self.volts_str_3[0] - 48) * 1.0) + ((self.volts_str_3[2] - 48) / 10.0))
            return getattr(self, '_m_volt_3', None)

        @property
        def uptime_dd_str(self):
            if hasattr(self, '_m_uptime_dd_str'):
                return self._m_uptime_dd_str

            _pos = self._io.pos()
            self._io.seek(71)
            self._m_uptime_dd_str = []
            for i in range(2):
                self._m_uptime_dd_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_dd_str', None)

        @property
        def volts_str_2(self):
            if hasattr(self, '_m_volts_str_2'):
                return self._m_volts_str_2

            _pos = self._io.pos()
            self._io.seek(154)
            self._m_volts_str_2 = []
            for i in range(3):
                self._m_volts_str_2.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_2', None)

        @property
        def commands(self):
            if hasattr(self, '_m_commands'):
                return self._m_commands

            self._m_commands = ((((((1 if self.commands_str[0] > 47 else 0) * (self.commands_str[0] - 48)) * 1000) + (((1 if self.commands_str[1] > 47 else 0) * (self.commands_str[1] - 48)) * 100)) + (((1 if self.commands_str[2] > 47 else 0) * (self.commands_str[2] - 48)) * 10)) + (self.commands_str[3] - 48))
            return getattr(self, '_m_commands', None)

        @property
        def volt_8(self):
            if hasattr(self, '_m_volt_8'):
                return self._m_volt_8

            self._m_volt_8 = (((self.volts_str_8[0] - 48) * 1.0) + ((self.volts_str_8[2] - 48) / 10.0))
            return getattr(self, '_m_volt_8', None)

        @property
        def volts_str_8(self):
            if hasattr(self, '_m_volts_str_8'):
                return self._m_volts_str_8

            _pos = self._io.pos()
            self._io.seek(178)
            self._m_volts_str_8 = []
            for i in range(3):
                self._m_volts_str_8.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_8', None)

        @property
        def volts_str_6(self):
            if hasattr(self, '_m_volts_str_6'):
                return self._m_volts_str_6

            _pos = self._io.pos()
            self._io.seek(170)
            self._m_volts_str_6 = []
            for i in range(3):
                self._m_volts_str_6.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_6', None)

        @property
        def tfh_str(self):
            if hasattr(self, '_m_tfh_str'):
                return self._m_tfh_str

            _pos = self._io.pos()
            self._io.seek(222)
            self._m_tfh_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfh_str', None)

        @property
        def volt_7(self):
            if hasattr(self, '_m_volt_7'):
                return self._m_volt_7

            self._m_volt_7 = (((self.volts_str_7[0] - 48) * 1.0) + ((self.volts_str_7[2] - 48) / 10.0))
            return getattr(self, '_m_volt_7', None)

        @property
        def commands_str(self):
            if hasattr(self, '_m_commands_str'):
                return self._m_commands_str

            _pos = self._io.pos()
            self._io.seek(90)
            self._m_commands_str = []
            for i in range(4):
                self._m_commands_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_commands_str', None)

        @property
        def volts_str_7(self):
            if hasattr(self, '_m_volts_str_7'):
                return self._m_volts_str_7

            _pos = self._io.pos()
            self._io.seek(174)
            self._m_volts_str_7 = []
            for i in range(3):
                self._m_volts_str_7.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_7', None)

        @property
        def hth_str(self):
            if hasattr(self, '_m_hth_str'):
                return self._m_hth_str

            _pos = self._io.pos()
            self._io.seek(245)
            self._m_hth_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hth_str', None)

        @property
        def temperature(self):
            if hasattr(self, '_m_temperature'):
                return self._m_temperature

            self._m_temperature = ((((1 if self.temp_str[0] > 47 else 0) * (self.temp_str[0] - 48)) * 10) + (self.temp_str[1] - 48))
            return getattr(self, '_m_temperature', None)

        @property
        def uptime_hh_str(self):
            if hasattr(self, '_m_uptime_hh_str'):
                return self._m_uptime_hh_str

            _pos = self._io.pos()
            self._io.seek(75)
            self._m_uptime_hh_str = []
            for i in range(2):
                self._m_uptime_hh_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_hh_str', None)

        @property
        def volt_9(self):
            if hasattr(self, '_m_volt_9'):
                return self._m_volt_9

            self._m_volt_9 = (((self.volts_str_9[0] - 48) * 1.0) + ((self.volts_str_9[2] - 48) / 10.0))
            return getattr(self, '_m_volt_9', None)

        @property
        def volts_str_4(self):
            if hasattr(self, '_m_volts_str_4'):
                return self._m_volts_str_4

            _pos = self._io.pos()
            self._io.seek(162)
            self._m_volts_str_4 = []
            for i in range(3):
                self._m_volts_str_4.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_4', None)

        @property
        def volt_2(self):
            if hasattr(self, '_m_volt_2'):
                return self._m_volt_2

            self._m_volt_2 = (((self.volts_str_2[0] - 48) * 1.0) + ((self.volts_str_2[2] - 48) / 10.0))
            return getattr(self, '_m_volt_2', None)

        @property
        def leila_request_str(self):
            if hasattr(self, '_m_leila_request_str'):
                return self._m_leila_request_str

            _pos = self._io.pos()
            self._io.seek(110)
            self._m_leila_request_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_leila_request_str', None)

        @property
        def leila_req(self):
            if hasattr(self, '_m_leila_req'):
                return self._m_leila_req

            self._m_leila_req = self.leila_request_str > 48
            return getattr(self, '_m_leila_req', None)

        @property
        def volt_4(self):
            if hasattr(self, '_m_volt_4'):
                return self._m_volt_4

            self._m_volt_4 = (((self.volts_str_4[0] - 48) * 1.0) + ((self.volts_str_4[2] - 48) / 10.0))
            return getattr(self, '_m_volt_4', None)

        @property
        def leila_active_str(self):
            if hasattr(self, '_m_leila_active_str'):
                return self._m_leila_active_str

            _pos = self._io.pos()
            self._io.seek(127)
            self._m_leila_active_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_leila_active_str', None)

        @property
        def volts_str_5(self):
            if hasattr(self, '_m_volts_str_5'):
                return self._m_volts_str_5

            _pos = self._io.pos()
            self._io.seek(166)
            self._m_volts_str_5 = []
            for i in range(3):
                self._m_volts_str_5.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_5', None)

        @property
        def volt_1(self):
            if hasattr(self, '_m_volt_1'):
                return self._m_volt_1

            self._m_volt_1 = (((self.volts_str_1[0] - 48) * 1.0) + ((self.volts_str_1[2] - 48) / 10.0))
            return getattr(self, '_m_volt_1', None)

        @property
        def uptime_mm_str(self):
            if hasattr(self, '_m_uptime_mm_str'):
                return self._m_uptime_mm_str

            _pos = self._io.pos()
            self._io.seek(79)
            self._m_uptime_mm_str = []
            for i in range(2):
                self._m_uptime_mm_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_mm_str', None)

        @property
        def tfe_str(self):
            if hasattr(self, '_m_tfe_str'):
                return self._m_tfe_str

            _pos = self._io.pos()
            self._io.seek(212)
            self._m_tfe_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfe_str', None)

        @property
        def temp_str(self):
            if hasattr(self, '_m_temp_str'):
                return self._m_temp_str

            _pos = self._io.pos()
            self._io.seek(134)
            self._m_temp_str = []
            for i in range(2):
                self._m_temp_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_temp_str', None)

        @property
        def volts_str_3(self):
            if hasattr(self, '_m_volts_str_3'):
                return self._m_volts_str_3

            _pos = self._io.pos()
            self._io.seek(158)
            self._m_volts_str_3 = []
            for i in range(3):
                self._m_volts_str_3.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_3', None)

        @property
        def volt_6(self):
            if hasattr(self, '_m_volt_6'):
                return self._m_volt_6

            self._m_volt_6 = (((self.volts_str_6[0] - 48) * 1.0) + ((self.volts_str_6[2] - 48) / 10.0))
            return getattr(self, '_m_volt_6', None)

        @property
        def volt_5(self):
            if hasattr(self, '_m_volt_5'):
                return self._m_volt_5

            self._m_volt_5 = (((self.volts_str_5[0] - 48) * 1.0) + ((self.volts_str_5[2] - 48) / 10.0))
            return getattr(self, '_m_volt_5', None)

        @property
        def uptime(self):
            if hasattr(self, '_m_uptime'):
                return self._m_uptime

            self._m_uptime = (((((((((1 if self.uptime_dd_str[0] > 47 else 0) * (self.uptime_dd_str[0] - 48)) * 10) + (self.uptime_dd_str[1] - 48)) * 24) * 60) * 60) + ((((((1 if self.uptime_hh_str[0] > 47 else 0) * (self.uptime_hh_str[0] - 48)) * 10) + (self.uptime_hh_str[1] - 48)) * 60) * 60)) + (((((1 if self.uptime_mm_str[0] > 47 else 0) * (self.uptime_mm_str[0] - 48)) * 10) + (self.uptime_mm_str[1] - 48)) * 60))
            return getattr(self, '_m_uptime', None)

        @property
        def volts_str_1(self):
            if hasattr(self, '_m_volts_str_1'):
                return self._m_volts_str_1

            _pos = self._io.pos()
            self._io.seek(150)
            self._m_volts_str_1 = []
            for i in range(3):
                self._m_volts_str_1.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_1', None)

        @property
        def hff_str(self):
            if hasattr(self, '_m_hff_str'):
                return self._m_hff_str

            _pos = self._io.pos()
            self._io.seek(234)
            self._m_hff_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hff_str', None)

        @property
        def hr_str(self):
            if hasattr(self, '_m_hr_str'):
                return self._m_hr_str

            _pos = self._io.pos()
            self._io.seek(255)
            self._m_hr_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hr_str', None)


    class Ao40FecCommandResponse(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")


    class Ao40MessageK(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ao40_message_line1 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line2 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line3 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line4 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line5 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line6 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line7 = (self._io.read_bytes(64)).decode(u"ASCII")
            self.ao40_message_line8 = (self._io.read_bytes(64)).decode(u"ASCII")

        @property
        def tfl_str(self):
            if hasattr(self, '_m_tfl_str'):
                return self._m_tfl_str

            _pos = self._io.pos()
            self._io.seek(201)
            self._m_tfl_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfl_str', None)

        @property
        def volts_str_9(self):
            if hasattr(self, '_m_volts_str_9'):
                return self._m_volts_str_9

            _pos = self._io.pos()
            self._io.seek(182)
            self._m_volts_str_9 = []
            for i in range(3):
                self._m_volts_str_9.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_9', None)

        @property
        def leila_act(self):
            if hasattr(self, '_m_leila_act'):
                return self._m_leila_act

            self._m_leila_act = self.leila_active_str > 48
            return getattr(self, '_m_leila_act', None)

        @property
        def volt_3(self):
            if hasattr(self, '_m_volt_3'):
                return self._m_volt_3

            self._m_volt_3 = (((self.volts_str_3[0] - 48) * 1.0) + ((self.volts_str_3[2] - 48) / 10.0))
            return getattr(self, '_m_volt_3', None)

        @property
        def uptime_dd_str(self):
            if hasattr(self, '_m_uptime_dd_str'):
                return self._m_uptime_dd_str

            _pos = self._io.pos()
            self._io.seek(71)
            self._m_uptime_dd_str = []
            for i in range(2):
                self._m_uptime_dd_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_dd_str', None)

        @property
        def volts_str_2(self):
            if hasattr(self, '_m_volts_str_2'):
                return self._m_volts_str_2

            _pos = self._io.pos()
            self._io.seek(154)
            self._m_volts_str_2 = []
            for i in range(3):
                self._m_volts_str_2.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_2', None)

        @property
        def commands(self):
            if hasattr(self, '_m_commands'):
                return self._m_commands

            self._m_commands = ((((((1 if self.commands_str[0] > 47 else 0) * (self.commands_str[0] - 48)) * 1000) + (((1 if self.commands_str[1] > 47 else 0) * (self.commands_str[1] - 48)) * 100)) + (((1 if self.commands_str[2] > 47 else 0) * (self.commands_str[2] - 48)) * 10)) + (self.commands_str[3] - 48))
            return getattr(self, '_m_commands', None)

        @property
        def volt_8(self):
            if hasattr(self, '_m_volt_8'):
                return self._m_volt_8

            self._m_volt_8 = (((self.volts_str_8[0] - 48) * 1.0) + ((self.volts_str_8[2] - 48) / 10.0))
            return getattr(self, '_m_volt_8', None)

        @property
        def volts_str_8(self):
            if hasattr(self, '_m_volts_str_8'):
                return self._m_volts_str_8

            _pos = self._io.pos()
            self._io.seek(178)
            self._m_volts_str_8 = []
            for i in range(3):
                self._m_volts_str_8.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_8', None)

        @property
        def volts_str_6(self):
            if hasattr(self, '_m_volts_str_6'):
                return self._m_volts_str_6

            _pos = self._io.pos()
            self._io.seek(170)
            self._m_volts_str_6 = []
            for i in range(3):
                self._m_volts_str_6.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_6', None)

        @property
        def tfh_str(self):
            if hasattr(self, '_m_tfh_str'):
                return self._m_tfh_str

            _pos = self._io.pos()
            self._io.seek(222)
            self._m_tfh_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfh_str', None)

        @property
        def volt_7(self):
            if hasattr(self, '_m_volt_7'):
                return self._m_volt_7

            self._m_volt_7 = (((self.volts_str_7[0] - 48) * 1.0) + ((self.volts_str_7[2] - 48) / 10.0))
            return getattr(self, '_m_volt_7', None)

        @property
        def commands_str(self):
            if hasattr(self, '_m_commands_str'):
                return self._m_commands_str

            _pos = self._io.pos()
            self._io.seek(90)
            self._m_commands_str = []
            for i in range(4):
                self._m_commands_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_commands_str', None)

        @property
        def volts_str_7(self):
            if hasattr(self, '_m_volts_str_7'):
                return self._m_volts_str_7

            _pos = self._io.pos()
            self._io.seek(174)
            self._m_volts_str_7 = []
            for i in range(3):
                self._m_volts_str_7.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_7', None)

        @property
        def hth_str(self):
            if hasattr(self, '_m_hth_str'):
                return self._m_hth_str

            _pos = self._io.pos()
            self._io.seek(245)
            self._m_hth_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hth_str', None)

        @property
        def temperature(self):
            if hasattr(self, '_m_temperature'):
                return self._m_temperature

            self._m_temperature = ((((1 if self.temp_str[0] > 47 else 0) * (self.temp_str[0] - 48)) * 10) + (self.temp_str[1] - 48))
            return getattr(self, '_m_temperature', None)

        @property
        def uptime_hh_str(self):
            if hasattr(self, '_m_uptime_hh_str'):
                return self._m_uptime_hh_str

            _pos = self._io.pos()
            self._io.seek(75)
            self._m_uptime_hh_str = []
            for i in range(2):
                self._m_uptime_hh_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_hh_str', None)

        @property
        def volt_9(self):
            if hasattr(self, '_m_volt_9'):
                return self._m_volt_9

            self._m_volt_9 = (((self.volts_str_9[0] - 48) * 1.0) + ((self.volts_str_9[2] - 48) / 10.0))
            return getattr(self, '_m_volt_9', None)

        @property
        def volts_str_4(self):
            if hasattr(self, '_m_volts_str_4'):
                return self._m_volts_str_4

            _pos = self._io.pos()
            self._io.seek(162)
            self._m_volts_str_4 = []
            for i in range(3):
                self._m_volts_str_4.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_4', None)

        @property
        def volt_2(self):
            if hasattr(self, '_m_volt_2'):
                return self._m_volt_2

            self._m_volt_2 = (((self.volts_str_2[0] - 48) * 1.0) + ((self.volts_str_2[2] - 48) / 10.0))
            return getattr(self, '_m_volt_2', None)

        @property
        def leila_request_str(self):
            if hasattr(self, '_m_leila_request_str'):
                return self._m_leila_request_str

            _pos = self._io.pos()
            self._io.seek(110)
            self._m_leila_request_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_leila_request_str', None)

        @property
        def leila_req(self):
            if hasattr(self, '_m_leila_req'):
                return self._m_leila_req

            self._m_leila_req = self.leila_request_str > 48
            return getattr(self, '_m_leila_req', None)

        @property
        def volt_4(self):
            if hasattr(self, '_m_volt_4'):
                return self._m_volt_4

            self._m_volt_4 = (((self.volts_str_4[0] - 48) * 1.0) + ((self.volts_str_4[2] - 48) / 10.0))
            return getattr(self, '_m_volt_4', None)

        @property
        def leila_active_str(self):
            if hasattr(self, '_m_leila_active_str'):
                return self._m_leila_active_str

            _pos = self._io.pos()
            self._io.seek(127)
            self._m_leila_active_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_leila_active_str', None)

        @property
        def volts_str_5(self):
            if hasattr(self, '_m_volts_str_5'):
                return self._m_volts_str_5

            _pos = self._io.pos()
            self._io.seek(166)
            self._m_volts_str_5 = []
            for i in range(3):
                self._m_volts_str_5.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_5', None)

        @property
        def volt_1(self):
            if hasattr(self, '_m_volt_1'):
                return self._m_volt_1

            self._m_volt_1 = (((self.volts_str_1[0] - 48) * 1.0) + ((self.volts_str_1[2] - 48) / 10.0))
            return getattr(self, '_m_volt_1', None)

        @property
        def uptime_mm_str(self):
            if hasattr(self, '_m_uptime_mm_str'):
                return self._m_uptime_mm_str

            _pos = self._io.pos()
            self._io.seek(79)
            self._m_uptime_mm_str = []
            for i in range(2):
                self._m_uptime_mm_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_uptime_mm_str', None)

        @property
        def tfe_str(self):
            if hasattr(self, '_m_tfe_str'):
                return self._m_tfe_str

            _pos = self._io.pos()
            self._io.seek(212)
            self._m_tfe_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_tfe_str', None)

        @property
        def temp_str(self):
            if hasattr(self, '_m_temp_str'):
                return self._m_temp_str

            _pos = self._io.pos()
            self._io.seek(134)
            self._m_temp_str = []
            for i in range(2):
                self._m_temp_str.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_temp_str', None)

        @property
        def volts_str_3(self):
            if hasattr(self, '_m_volts_str_3'):
                return self._m_volts_str_3

            _pos = self._io.pos()
            self._io.seek(158)
            self._m_volts_str_3 = []
            for i in range(3):
                self._m_volts_str_3.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_3', None)

        @property
        def volt_6(self):
            if hasattr(self, '_m_volt_6'):
                return self._m_volt_6

            self._m_volt_6 = (((self.volts_str_6[0] - 48) * 1.0) + ((self.volts_str_6[2] - 48) / 10.0))
            return getattr(self, '_m_volt_6', None)

        @property
        def volt_5(self):
            if hasattr(self, '_m_volt_5'):
                return self._m_volt_5

            self._m_volt_5 = (((self.volts_str_5[0] - 48) * 1.0) + ((self.volts_str_5[2] - 48) / 10.0))
            return getattr(self, '_m_volt_5', None)

        @property
        def uptime(self):
            if hasattr(self, '_m_uptime'):
                return self._m_uptime

            self._m_uptime = (((((((((1 if self.uptime_dd_str[0] > 47 else 0) * (self.uptime_dd_str[0] - 48)) * 10) + (self.uptime_dd_str[1] - 48)) * 24) * 60) * 60) + ((((((1 if self.uptime_hh_str[0] > 47 else 0) * (self.uptime_hh_str[0] - 48)) * 10) + (self.uptime_hh_str[1] - 48)) * 60) * 60)) + (((((1 if self.uptime_mm_str[0] > 47 else 0) * (self.uptime_mm_str[0] - 48)) * 10) + (self.uptime_mm_str[1] - 48)) * 60))
            return getattr(self, '_m_uptime', None)

        @property
        def volts_str_1(self):
            if hasattr(self, '_m_volts_str_1'):
                return self._m_volts_str_1

            _pos = self._io.pos()
            self._io.seek(150)
            self._m_volts_str_1 = []
            for i in range(3):
                self._m_volts_str_1.append(self._io.read_u1())

            self._io.seek(_pos)
            return getattr(self, '_m_volts_str_1', None)

        @property
        def hff_str(self):
            if hasattr(self, '_m_hff_str'):
                return self._m_hff_str

            _pos = self._io.pos()
            self._io.seek(234)
            self._m_hff_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hff_str', None)

        @property
        def hr_str(self):
            if hasattr(self, '_m_hr_str'):
                return self._m_hr_str

            _pos = self._io.pos()
            self._io.seek(255)
            self._m_hr_str = self._io.read_u1()
            self._io.seek(_pos)
            return getattr(self, '_m_hr_str', None)


    @property
    def frame_length(self):
        if hasattr(self, '_m_frame_length'):
            return self._m_frame_length

        self._m_frame_length = self._io.size()
        return getattr(self, '_m_frame_length', None)


