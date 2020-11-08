import os
import yaml

from collections import namedtuple

Field = namedtuple("Field", ["FieldID", "Type", "MaxLen", "LenType", "Description"])

class Config(object):
    def __init__(self, config):
        super().__init__()
        if not os.path.exists(config):
            print("Can't find configuration file.")
        self.config = yaml.load(open(config))
        fields = {}
        for field in self.config['Fields']:
            if isinstance(field, tuple):
                fields[field[0]]=Field(*field)
            else:
                print("Unexpected field format:", field)
        self.config['Fields'] = fields