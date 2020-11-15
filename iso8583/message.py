from .config import Config
from .logger import Logger

class Message(object):
    def __init__(self, mti, config):
        self.log = Logger()
        self.mti = mti
        self._bitmap = []
        self.config = Config(config)
        self.fields = {}

    @property
    def lbitmap(self):
        return self._bitmap[::]

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
        if isinstance(mti, str):
            self._mti = mti
        elif isinstance(mti, int):
            self._mti = f"{mti:04}"
        else:
            raise f"Unexpected MTI = {mti}, type={type(mti)}"
    
    def __setitem__(self, id, value):
        self.log.Debug(f"Adding field {id} = [{value}]")
        if id == 1: return
        self.fields[id] = value
        if id not in self._bitmap:
            self._bitmap.append(id)
            self._bitmap.sort()

    def __getitem__(self, key):
        return self.fields.get(key)
    
    def __iter__(self):
        for field_id in self._bitmap:
            yield field_id, self.fields[field_id]

    def __repr__(self):
        return "Message()"

    def __str__(self):
        msg = f"Message MTI[{self._mti}]:\n"
        msg += f" {self.lbitmap}\n"
        for id in self.fields:
            msg += f"  [{id}] = {repr(self.fields[id])}\n"

        return msg