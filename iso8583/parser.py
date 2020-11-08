from .loader import Config

class ISO8583Parser(object):
    def __init__(self, config):
        self.__cfg = Config(config)
    
    def parse(self, msg):
        mti, position = self._getMTI(msg)
        bitmap, position = self._getBitmap(msg, position)
        return mti, bitmap
    
    def _getMTI(self, msg):
        return msg[0:self.__cfg.mti.Length].decode("utf-8") , self.__cfg.mti.Length

    def _getBitmap(self, msg, position):
        BitmapFieldID = 1  # TODO: move?
        end_position = position + self.__cfg.fields[BitmapFieldID].MaxLen
        flags = msg[position:end_position]
        # Make Bitmap
        _bits = [flags[i//8] & 1 << i%8 != 0 for i in range(len(flags) * 8)]
        # change order of bits foreach byte
        bits = []
        for i in range(int(len(_bits)/8)):
            bits += _bits[i*8:i*8+8][::-1] 

        bitmap = [ i + 1 for i, b in enumerate(bits) if b ]
        return bitmap, end_position