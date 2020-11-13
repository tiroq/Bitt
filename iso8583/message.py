from .config import Config

class Message(object):
    _bitmap = []

    def __init__(self, mti, config):
        self.mti = mti
        self.config = Config(config)
        self.fields = {}

    @property
    def bitmap(self):
        bitmap = self._bitmap[::]
        length = 63
        if max(bitmap) > 63:
            bitmap = [1] + self._bitmap
            length = 127
        b = ''.join(['1' if i + 1 in bitmap else '0'for i in range(length)])
        return bytes(int(b[i : i + 8], 2) for i in range(0, len(b), 8))

    @property
    def mti(self):
        return bytes(self._mti, "utf-8")
    
    @mti.setter
    def mti(self, mti):
        self._mti = f"{mti:04}"
    
    def __setitem__(self, id, value):
        if id == 1: return
        self.fields[id] = value
        if id not in self._bitmap:
            self._bitmap.append(id)
            self._bitmap.sort()

    def __getitem__(self, key):
        return self.content.get(key)
    
    def __iter__(self):
        for field_id in self._bitmap:
            yield field_id, self.fields[field_id]