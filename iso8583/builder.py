from .base import ISO8583
from .message import Message
# from .config import DeviceConfig


class BaseBuilder(ISO8583):
    def __init__(self, config_name) -> None:
        super().__init__(config_name)
        self.__raw = b''
        self._buildField = None
        self._buildSField = None
    
    def build(self, msg: Message) -> bytes:
        self.log.Info(f"Start building message. MTI={msg.mti.decode('utf-8')}")
        self.__raw = msg.mti  # Clean mesage
        self.__raw += msg.bitmap
        self.log.Debug(f"MTI+Bitmap[{msg.lbitmap}]:\n{self.hexdump(self.__raw)}")
        for field, data in msg:
            self.__raw += self.buildField(data, self.cfg[field])
        self.log.Debug(f"Build Done. RAW Message:\n{self.hexdump(self.__raw)}")
        return self.__raw
    
    def __repr__(self) -> str:
        return self.__raw
        
    def buildField(self, msg, rule) -> bytes:
        self.log.Debug(f"Loaded build rule: {rule}")
        return {
            "Field": self._buildField
        ,   "SField": self._buildSField
        }[type(rule).__name__](msg, rule)


class CDbBuilder(BaseBuilder):
    def __init__(self, config_name) -> None:
        super().__init__(config_name)
        self._buildField = self.__buildField
        self._buildSField = self.__buildSField

    def __buildField(self, data, rule) -> bytes:
        length = { # TODO: correct length processing
            0: lambda x, r: ''
        ,   1: lambda d, r: str(r.MaxLen) if len(data) > r.MaxLen else str(len(data))
        ,   2: lambda d, r: f"{r.MaxLen:02}" if len(data) > r.MaxLen else f"{len(data):02}"
        ,   3: lambda d, r: f"{r.MaxLen:03}" if len(data) > r.MaxLen else f"{len(data):03}"
        }[rule.LenType](data, rule)
        _length = int(length) if length else rule.MaxLen
        data = bytes(length + data.ljust(_length)[:_length], 'utf-8')
        self.log.Debug(f"FieldID[{rule.FieldID}] Length[{_length}]:\n{self.hexdump(data)}")
        return data
    
    def __buildSField(self, msg, rule) -> bytes:
        data = b''
        for fieldID, smsg in msg:
            data += self._buildField(smsg, rule[fieldID])
        return data


class Builder(object):
    mapper = {
        'CDb': CDbBuilder
    }
    def __init__(self, device):
        return self.mapper[f"{device.encoding}{device.format}{device.order}"]
