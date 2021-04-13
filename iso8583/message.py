# from .config import DictConfigLoader
from .logger import Logger


class Message(object):
    # def __init__(self, mti, config_name):
    lead_mti_chars = {
        "1987": "0",
        "1993": "1",
        "2003": "2",
        "Error": "9",
        "error": "9",
        "Err": "9",
        "err": "9"
    }
    def __init__(self, mti=200, version="1987"):
        self.log = Logger()
        self.lead_mti_char = self.lead_mti_chars.get(version, "0")
        # set mti via setter
        self.mti = mti
        self._bitmap = []
        # self.config = DictConfigLoader(config_name)
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
        b = ''.join(['1' if i + 1 in bitmap else '0' for i in range(length)])
        return bytes(int(b[i:i + 8], 2) for i in range(0, len(b), 8))

    @property
    def mti(self):
        return bytes(self._mti, "utf-8")
    
    @mti.setter
    def mti(self, mti):
        if isinstance(mti, str):
            if len(mti) == 4:
                self._mti = mti
                return
            elif len(mti) == 3:
                self._mti = f"{self.lead_mti_char}{mti}"
                return
        elif isinstance(mti, int):
            self._mti = f"{self.lead_mti_char}{mti:03}"
            return
        raise Exception(f"Unexpected MTI = {mti}, type={type(mti)}")
    
    def __setitem__(self, field_id, value):
        self.log.Debug(f"Adding field {field_id} = [{value}]")
        if field_id == 1:
            return
        self.fields[field_id] = value
        if field_id not in self._bitmap:
            self._bitmap.append(field_id)
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
        for field_id in self.fields:
            msg += f"  [{field_id}] = {repr(self.fields[field_id])}\n"

        return msg
