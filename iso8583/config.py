import os
import sys
import yaml
import random
import string

# from collections import NamedTuple
from typing import NamedTuple

from .logger import Logger
from pprint import pprint

# Field = namedtuple("Field", ["FieldID", "Type", "MaxLen", "LenType", "Description"])
class Field(NamedTuple):
    FieldID: int
    Type: str
    MaxLen: int
    LenType: str
    Description: str = ""


class MTI(NamedTuple):
    # MTI: str = "000"
    Type: str
    Length: int


class SField(object):
    def __init__(self, data) -> None:
        self._fields = {}
        self.ID = data["ID"]
        self.Fields = [self.convert(field) for field in data["Fields"]]
        for i in self.Fields:
            self._fields[i.FieldID] = i
    
    def convert(self, field: list) -> Field:
        field[3] = {
            "LLLVAR": 3,
            "LLVAR" : 2,
            "LVAR"  : 1,
            "FIXED" : 0
        }[field[3]]
        return Field(*field)
    
    def __getitem__(self, key):
        return self._fields.get(key)
    
    def __repr__(self):
        return str(self._fields)


class Fields(object):
    def __init__(self):
        self._fields = {}
    
    def __getitem__(self, key):
        return self._fields.get(key)


class Config(object):
    def __init__(self, config):
        self.log = Logger()
        if not os.path.exists(config):
            self.log.Error("Can't find configuration file.")
            return
        self.config_name = config
        self.raw_config = yaml.load(open(config))
        self.name = self.raw_config["Name"]
    
    def gen_id(self, size=6, chars=string.ascii_uppercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))


class DictConfig(Config):

    def __init__(self, config):
        super().__init__(config)
        self._fields = {}
        self.__init_mti()
        self.__init_fields()
    
    def __getitem__(self, key):
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        return self._fields[key]
    
    def __init_mti(self):
        mti = self.raw_config.get("MTI", dict(Type="ASCII", Length=8))
        self.mti = MTI(**mti)
    
    def __init_fields(self):
        fields = {}
        for field in self.raw_config["Fields"]:
            if isinstance(field, list):
                field[3] = {
                    "LLLVAR": 3,
                    "LLVAR" : 2,
                    "LVAR"  : 1,
                    "FIXED" : 0
                }[field[3]]
                self._fields[field[0]] = Field(*field)
            elif isinstance(field, dict):
                self._fields[field["ID"]] = SField(field)
            else:
                self.log.Info("Unexpected field format:", field)
        # self.log.debug(f"Loaded config: {self.fields}")


class DeviceConfig(Config):
    def __init__(self, config) -> None:
        super().__init__(config)
        self.socket = {"TCP_NO_DELAY": 0, "SO_REUSEADDR": 1}
        self.__init_config()
    
    def __init_config(self):
        self.name = self.raw_config.get("Name", self.gen_id())
        self.socket["TCP_NO_DELAY"] = self.raw_config.get("Socket", self.socket).get("TCP_NO_DELAY")
        self.socket["SO_REUSEADDR"] = self.raw_config.get("Socket", self.socket).get("SO_REUSEADDR")
        self.encoding = self.raw_config["Header"].get("Encoding", "C")
        self.format = self.raw_config["Header"].get("Format", "D")
        self.order = self.raw_config["Header"].get("ByteOrder", "b")
        self.host = self.raw_config.get("Host", "127.0.0.1")
        self.port = self.raw_config.get("Port", 12345)
        self.log.Debug(f"Config for Device[{self.name}]: Bytes order[{self.order}]; Host[{self.host}]; Port[{self.port}]; cfg={self.config_name}")


class ConfigLoader(object):
    def __init__(self, name, path, tclass=Config):
        root_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        configs_path = os.path.join(root_path, path)
        for root, dirs, files in os.walk(configs_path):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    config_name = os.path.join(root, file)
                    config = tclass(config_name)
                    if config.name == name:
                        self.__class__ = tclass
                        self.__dict__.update(config.__dict__)
                        return
        raise Exception(f"Can't detect configuration for '{name}'")


class DeviceConfigLoader(ConfigLoader):
    def __init__(self, name):
        super().__init__(name, "devices", tclass=DeviceConfig)


class DictConfigLoader(ConfigLoader):
    def __init__(self, name):
        super().__init__(name, "dicts", tclass=DictConfig)
