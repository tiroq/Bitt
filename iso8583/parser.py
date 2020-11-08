
class ISO8583Parser(object):
    def __init__(self, config):
        self.__cfg = config
    
    def parse(self, msg):
        mti, position = self.__getMTI(msg)
    
    def __getMTI(self, msg):
        return msg[0:self.__cfg.mti.Length], self.__cfg.mti.Length

    def __getBitmap(self, msg, position):
        BitmapFieldID = 1  # TODO: move?