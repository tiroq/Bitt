from .base import ISO8583

class ISO8583Builder(ISO8583):
    raw = b''

    def __init__(self, config):
        super().__init__(config)
    
    def build(self, msg):
        self.log.Info(f"Start building message. MTI={msg.mti.decode('utf-8')}")
        self.raw = msg.mti
        self.raw += msg.bitmap
        self.log.Debug(f"MTI+Bitmap:\n{self.hexdump(self.raw)}")
        cfg = self.cfg[msg.mti]
        for field, data in msg:
            self.raw += self._buildField(data, cfg[field])
        self.log.Debug(f"Build Done. RAW Message:\n{self.hexdump(self.raw)}")
        return self.raw

    def _buildField(self, data, rule):
        length = { # TODO: correct length processing
            0: lambda x, r: ''
        ,   1: lambda d, r: str(r.MaxLen) if len(data) > r.MaxLen else str(len(data))
        ,   2: lambda d, r: f"{r.MaxLen:02}" if len(data) > r.MaxLen else f"{len(data):02}"
        ,   3: lambda d, r: f"{r.MaxLen:03}" if len(data) > r.MaxLen else f"{len(data):03}"
        }[rule.LenType](data, rule)
        _length = int(length) if length else rule.MaxLen
        data = bytes(length + data.ljust(_length)[:_length], 'utf-8')
        self.log.Debug(f"Field[{rule.FieldID}] Length[{_length}]:\n{self.hexdump(data)}")
        return data