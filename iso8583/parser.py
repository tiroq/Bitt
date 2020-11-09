from .loader import Config

class ISO8583Parser(object):
    BitmapFieldID = 1

    def __init__(self, config):
        self.__cfg = Config(config)
    
    def parse(self, msg):
        mti = self._getMTI(msg)
        fields = self._getFields(msg)
        return mti, fields
    
    def _getMTI(self, msg):
        return msg[0:self.__cfg.mti.Length].decode("utf-8")

    def _getBitmap(self, msg, position=None, ext=0):
        if position is None:
            position = self.__cfg.mti.Length
        end_position = position + self.__cfg.fields[self.BitmapFieldID].MaxLen
        flags = msg[position:end_position]
        # Make Bitmap
        # bits = [(flags[i//8] >> (7-i)%8) & 1 for i in range(len(flags) * 8)] # TODO: check performance with next line
        bits = [flags[i//8] & 1 << (7 - i)%8 != 0 for i in range(len(flags) * 8)]

        bitmap = [ i + ext + 1 for i, b in enumerate(bits) if b ]
        if 1 in bitmap:
            ext_bitmap, end_position = self._getBitmap(msg, position=end_position, ext=64)
            bitmap += ext_bitmap
            bitmap.pop(0)
        return bitmap, end_position
    
    def _getFields(self, msg, position=None):
        _msg = msg[::]
        # if position is None:
        #     position = self.__cfg.mti.Length + self.__cfg.fields[self.BitmapFieldID].MaxLen
        bitmap, position = self._getBitmap(_msg)
        _msg = _msg[position:]
        fields = []
        for fieldID in bitmap:
            rule = self.__cfg.fields[fieldID]
            if rule.LenType == 0:
                data = _msg[:rule.MaxLen]
                _msg = _msg[rule.MaxLen:]
            else:
                length = int(_msg[:rule.LenType])
                data = _msg[rule.LenType:rule.LenType + length]
                _msg = _msg[rule.LenType + length:]
            data = repr(data.decode("utf-8"))
            fields.append((fieldID, data))
        return fields
