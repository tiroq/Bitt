import os
import yaml

from collections import namedtuple

Field = namedtuple("Field", ["FieldID", "Type", "MaxLen", "LenType", "Description"])

class Config(object):
    def __init__(self, config):
        super().__init__()
        if not os.path.exists(config):
            print("Can't find configuration file.")
            return
        self.raw_config = yaml.load(open(config))
        self.__init_mti()
        self.__init_fields()
    
    def __init_mti(self):
        mti = self.raw_config.get("MTI", dict(Type="ASCII", Length=8))
        MTI = namedtuple("MTI", mti)
        self.mti = MTI(**mti)

    def __init_fields(self):
        self.fields = {}
        for field in self.raw_config['Fields']:
            if isinstance(field, tuple):
                self.fields[field[0]]=Field(*field)
            else:
                print("Unexpected field format:", field)