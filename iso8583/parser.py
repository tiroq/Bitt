from .base import ISO8583
from .message import Message
from pprint import pprint

class Parser(ISO8583):
    def __init__(self, config):
        self._cfg_name = config
        super().__init__(config)
    
    def parse(self, msg):
        self.log.Debug(f"Start parsing message:\n{self.hexdump(msg)}")
        mti = self._getMTI(msg)
        pmsg = Message(mti, self._cfg_name)
        for fID, data in self._getFields(msg[self.cfg.mti.Length:]):
            pmsg[fID] = data
        return pmsg
    
    def _getMTI(self, msg):
        raw_mti = msg[0:self.cfg.mti.Length] 
        mti = raw_mti.decode("utf-8")
        self.log.Debug(f"MTI:\n{self.hexdump(raw_mti)}")
        return mti

    def _getBitmap(self, msg, position=0):
        end_position = position + self.cfg[self.BitmapFieldID].MaxLen
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
    
    def _getFields(self, msg):
        _msg = msg[::]
        # pprint(self.cfg._msgs)
        bitmap, position = self._getBitmap(_msg)
        self.log.Debug(f"RAW Bitmap:\n{self.hexdump(_msg[:position])}")
        self.log.Debug(f"Bitmap: {bitmap}")
        _msg = _msg[position:]
        fields = []
        for fieldID in bitmap:
            rule = self.cfg[fieldID]
            _msg, data = self.__parseField(_msg, rule)
            self.log.Info(f"{fieldID:>3} = {data}")
            fields.append((fieldID, data))
        return fields
    
    def __parseField(self, msg, rule):
        self.log.Debug(f"Loaded rule: {rule}")
        return {
                "Field": self.__getFieldValue
            ,   "SField": self.__getSFieldValue
            }[type(rule).__name__](msg, rule)
    
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
        data = data.decode("utf-8")
        # data = repr(data)
        return msg, data

    def __getSFieldValue(self, msg, rule):
        data = []
        for field_rule in rule.Fields:
            msg, _data = self.__parseField(msg, field_rule)
            data.append((field_rule.FieldID, _data))
        return msg, data