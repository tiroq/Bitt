from .base import ISO8583

class ISO8583Builder(ISO8583):
    raw = b''

    def __init__(self, config):
        super().__init__(config)
    
    def build(self, msg):
        self.raw = msg.mti
        self.raw += msg.bitmap
        for field, data in msg:
            self.raw += self._buildField(data, self.cfg.fields[field])
        return self.raw

    def _buildField(self, data, rule):
        length = { # TODO: correct
            0: lambda x, r: ''
        ,   1: lambda d, r: str(r.MaxLen) if len(data) > r.MaxLen else str(len(data))
        ,   2: lambda d, r: f"{r.MaxLen:02}" if len(data) > r.MaxLen else f"{len(data):02}"
        ,   3: lambda d, r: f"{r.MaxLen:03}" if len(data) > r.MaxLen else f"{len(data):03}"
        }[rule.LenType](data, rule)
        _length = int(length) if length else rule.MaxLen
        data = data.ljust(_length)
        return bytes(length + data, 'utf-8')