import os
import yaml

from collections import namedtuple
from .logger import Logger
from pprint import pprint

Field = namedtuple("Field", ["FieldID", "Type", "MaxLen", "LenType", "Description"])

class SField(object):
    _fields = {}
    def __init__(self, data):
        self.ID = data["ID"]
        self.Fields = [self.convert(field) for field in data["Fields"]]
        for i in self.Fields:
            self._fields[i.FieldID] = i
    
    def convert(self, field):
        field[3] = {
            'LLLVAR': 3,
            'LLVAR' : 2,
            'LVAR'  : 1,
            'FIXED' : 0
        }[field[3]]
        return Field(*field)
    
    def __getitem__(self, key):
        return self._fields.get(key)


class Fields(object):
    _fields = {}
    def __init__(self):
        pass
    
    def __getitem__(self, key):
        return self._fields.get(key)

class Config(object):
    _fields = {}
    def __init__(self, config, logger=None):
        self.log = Logger()
        if not os.path.exists(config):
            self.log.Error("Can't find configuration file.")
            return
        self.raw_config = yaml.load(open(config))
        self.__init_mti()
        self.__init_fields()
    
    def __getitem__(self, key):
        if isinstance(key, bytes):
            key = key.decode('utf-8')
        return self._fields[key]
    
    def __init_mti(self):
        mti = self.raw_config.get("MTI", dict(Type="ASCII", Length=8))
        MTI = namedtuple("MTI", mti)
        self.mti = MTI(**mti)
    
    def __init_fields(self):
        fields = {}
        for field in self.raw_config['Fields']:
            if isinstance(field, list):
                field[3] = {
                    'LLLVAR': 3,
                    'LLVAR' : 2,
                    'LVAR'  : 1,
                    'FIXED' : 0
                }[field[3]]
                self._fields[field[0]] = Field(*field)
            elif isinstance(field, dict):
                self._fields[field["ID"]] = SField(field)
            else:
                self.log.Info("Unexpected field format:", field)
        # self.log.debug(f"Loaded config: {self.fields}")
        