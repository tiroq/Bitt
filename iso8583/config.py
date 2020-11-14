import os
import yaml

from collections import namedtuple
from .logger import Logger
from pprint import pprint

Field = namedtuple("Field", ["FieldID", "Type", "MaxLen", "LenType", "Description"])

class SField(object):
    def __init__(self, data):
        self.ID = data["ID"]
        self.Fields = [self.convert(field) for field in data["Fields"]]
    
    def convert(self, field):
        field[3] = {
            'LLLVAR': 3,
            'LLVAR' : 2,
            'LVAR'  : 1,
            'FIXED' : 0
        }[field[3]]
        return Field(*field)

class Fields(object):
    _fields = {}
    def __init__(self):
        pass
    
    def __getitem__(self, key):
        return self._fields.get(key)

class Config(object):
    _msgs = {}
    def __init__(self, config, logger=None):
        self.log = Logger()
        if not os.path.exists(config):
            self.log.Error("Can't find configuration file.")
            return
        self.raw_config = yaml.load(open(config))
        self.__init_mti()
        self.__init_msgs()
        # self.__init_fields()
    
    def __getitem__(self, key):
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        return self._msgs[key]
    
    def __init_mti(self):
        mti = self.raw_config.get("MTI", dict(Type="ASCII", Length=8))
        MTI = namedtuple("MTI", mti)
        self.mti = MTI(**mti)
    
    def __init_msgs(self):
        for msg in self.raw_config.get("Messages", []):
            self.__init_fields(msg)

    def __init_fields(self, msg):
        mti = msg.get('MTI')
        fields = {}
        for field in msg['Fields']:
            if isinstance(field, list):
                field[3] = {
                    'LLLVAR': 3,
                    'LLVAR' : 2,
                    'LVAR'  : 1,
                    'FIXED' : 0
                }[field[3]]
                fields[field[0]]=Field(*field)
            elif isinstance(field, dict):
                fields[field["ID"]] = SField(field)
            else:
                self.log.Info("Unexpected field format:", field)
        self._msgs[mti] = fields
        # self.log.debug(f"Loaded config: {self.fields}")
        