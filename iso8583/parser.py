import logging

from .loader import Config
from .logger import Logger

class ISO8583Parser(object):
    BitmapFieldID = 1

    def __init__(self, config):
        self.__cfg = Config(config)
        self.log = Logger()
    
    def ordp(self, c):
        output = []
        for i in c:
            if (i < 32) or (i >= 127):
                output.append('.')
            else:
                output.append(chr(i))
        return ''.join(output)

    def hexdump(self, p):
        output = []
        l = len(p)
        i = 0
        while i < l:
            output.append('{:04d}   '.format(i))
            for j in range(16):
                if (i + j) < l:
                    byte = p[i + j]
                    output.append('{:02X} '.format(byte))
                else:
                    output.append('   ')
                if (j % 16) == 7:
                    output.append(' ')
            output.append('  ')
            output.append(self.ordp(p[i:i + 16]))
            output.append('\n')
            i += 16
        return ''.join(output).rstrip('\n')
    
    def parse(self, msg):
        self.log.Debug(f"Start parsing message:\n{self.hexdump(msg)}")
        mti = self._getMTI(msg)
        fields = self._getFields(msg)
        return mti, fields
    
    def _getMTI(self, msg):
        raw_mti = msg[0:self.__cfg.mti.Length] 
        mti = raw_mti.decode("utf-8")
        self.log.Debug(f"MTI:\n{self.hexdump(raw_mti)}")
        return mti

    def _getBitmap(self, msg, position=None):
        if position is None:
            position = self.__cfg.mti.Length
        end_position = position + self.__cfg.fields[self.BitmapFieldID].MaxLen
        flags = msg[position:end_position]
        # Make Bitmap
        # bits = [(flags[i//8] >> (7-i)%8) & 1 for i in range(len(flags) * 8)] # TODO: check performance with next line
        bits = [flags[i//8] & 1 << (7 - i)%8 != 0 for i in range(len(flags) * 8)]

        bitmap = [ i + 1 for i, b in enumerate(bits) if b ]
        if self.BitmapFieldID in bitmap:
            ext_bitmap, end_position = self._getBitmap(msg, position=end_position)
            ext_bitmap = [ x + 64 for x in ext_bitmap ]
            bitmap += ext_bitmap
            bitmap.pop(0)  # Delete BitMapID parsing task
        return bitmap, end_position
    
    def _getFields(self, msg, position=None):
        _msg = msg[::]
        # if position is None:
        #     position = self.__cfg.mti.Length + self.__cfg.fields[self.BitmapFieldID].MaxLen
        bitmap, position = self._getBitmap(_msg)
        self.log.Debug(f"RAW Bitmap:\n{self.hexdump(_msg[:position])}")
        self.log.Debug(f"Bitmap: {bitmap}")
        _msg = _msg[position:]
        fields = []
        for fieldID in bitmap:
            rule = self.__cfg.fields[fieldID]
            self.log.Debug(f"Loaded rule: {rule}")
            _msg, data = {
                "Field": self.__getFieldValue
            ,   "SField": self.__getSFieldValue
            }[type(rule).__name__](_msg, rule)
            self.log.Info(f"{fieldID:>3} = {data}")
            fields.append((fieldID, data))
        return fields

    def __getFieldValue(self, msg, rule):
        if rule.LenType == 0:
            data = msg[:rule.MaxLen]
            self.log.Debug(f"RAW {rule.FieldID:>3}:\n{self.hexdump(data)}")
            msg = msg[rule.MaxLen:]
        else:
            length = int(msg[:rule.LenType])
            data = msg[rule.LenType:rule.LenType + length]
            self.log.Debug(f"RAW {rule.FieldID:>3}:\n{self.hexdump(msg[:rule.LenType + length])}")
            msg = msg[rule.LenType + length:]
        data = repr(data.decode("utf-8"))
        return msg, data

    def __getSFieldValue(self, msg, rule):
        data = []
        for field_rule in rule.Fields:
            _data = msg[:field_rule.MaxLen]
            self.log.Debug(f"RAW {field_rule.FieldID:>3}:\n{self.hexdump(_data)}")
            data.append((field_rule.FieldID, repr(_data.decode("utf-8"))))
            msg = msg[field_rule.MaxLen:]
        return msg, data