# from iso8583.loader import Config
from iso8583.config import DeviceConfig
from iso8583.builder import CDbBuilder
from iso8583.message import Message
from iso8583.service import Client
from iso8583.parser import Parser

from datetime import datetime
import random
f11 = f"{random.randrange(999999):06}"
imsg = [(2, "4000010000000001"),
        (3, "840000"),
        (4, "000000001000"),
        (7, datetime.now().strftime("%m%d%H%M%S")),
        (11, f11),
        (12, datetime.now().strftime("%y%m%d%H%M%S")),
        (14, "2512"),
        (37, f"{random.randrange(999999999999):012}"),
        (41, "00999201"),
        (42, "M999201"),
        (49, "810")]

msgs = [
    bytes.fromhex('303230307234000008C0800031363430303030313030303030303030303138343030303030303030303030303130303031' +
                  '31303631343031313733333437343832303131303631343031313732353132303331313134333334373438303039393932' +
                  '30314D3939393230312020202020202020383130'),
    bytes.fromhex('30323030F234000008C0800000000000040000003136343030303031303030303030303030313834303030303030303030' +
                  '30303031303030313130363134303131373333343734383230313130363134303131373235313230333131313433333437' +
                  '343830303939393230314D3939393230312020202020202020383130313634303030303130303030303030303031'),
    bytes.fromhex('30323030F234000008C3840000000040040000003136343030303031303030303030303030313834303030303030303030' +
                  '30303031303030313130363134303131373333343734383230313130363134303131373235313230333131313433333437' +
                  '343830303939393230314D3939393230312020202020202020303138303037303033303031303039303033353435303037' +
                  '31313033383430383130303230303030323634334330303030303030303030303030313030303133363638313130393137' +
                  '32363533313634303030303130303030303030303031'),
    bytes.fromhex('30323130723400000EC0800031363430303030313030303030303030303138343030303030303030303030303130303031' +
                  '31313331303431323639313130373832303131313331303431323632353132303331383130393131303738313030313032' +
                  '303030303939393230314D3939393230312020202020202020383130'),
    bytes.fromhex('30343030723440000CC2000031363430303030313030303030303030303138343030303030303030303030303130303031' +
                  '31313331303431333039313130373832303131313331303431323632353132333634353033313831303931313037383130' +
                  '3031303230303939393230314D39393932303120202020202020203030383138373030323531'),
    bytes.fromhex('30343130723440000AC0800031363430303030313030303030303030303138343030303030303030303030303130303031' +
                  '31313331303431333039313130373832303131313331303431323632353132363031303033313831303931313037383030' +
                  '30303939393230314D3939393230312020202020202020383130')
    # ,   bytes.fromhex('')
    # ,   bytes.fromhex('')
    # ,   bytes.fromhex('')
]

# print(cfg.fields)
for msg in msgs:
    continue
    parser = Parser('example_1')
    builder = CDbBuilder('example_1')
    parsed = parser.parse(msg)
    new_msg = builder.build(parsed)
    print(parsed)
    print("From  : ", msg)
    print("To    : ", new_msg)
    print("Equal : ", msg == new_msg)
    print("=" * 40)

# Client().set_dictionary()

c = Client('test_device_1', 'example_1')
m = Message(200)
for i, v in imsg:
    m[i] = v

# b = CDbBuilder('example_1')
# msg = b.build(m)
# raw = bytes("{0:04}".format(len(msg)), 'utf-8') + msg
c.send(raw)
print(9, raw)
# parser = Parser('example_1')
# _msg = None
# while True:
#     if c.tcp_socket():
#         _msg = c.recv()
#         print(0, _msg)
#     if _msg:
#         print(1, _msg[4:])
#         parsed = parser.parse(_msg[4:])
#         print(parsed)
#         break
#
#     else:
#         continue

# TODO: GUI https://github.com/adelbs/ISO8583 ???
# TODO: Research:
# - https://github.com/moov-io/iso8583
# - https://github.com/tilln/jmeter-iso8583
# - https://github.com/knovichikhin/pyiso8583/blob/master/iso8583/encoder.py
# - https://github.com/mchinchilla/StressTestISO8583Server
# - https://github.com/mahyaresteki/Horizon/blob/master/Source/controllers/services/IsoService.py
# - https://github.com/arthurhenrique/iso-8583/tree/master/Pyso8583
# - https://github.com/arthurhenrique/iso-8583/blob/master/Pyso8583/parser_tlv.py
# - https://github.com/danil/iso8583
# - https://github.com/timgabets/pythales
# - https://github.com/timgabets/pyatm
# - https://github.com/timgabets/pybank
# tlv:
# - https://github.com/russss/python-emv/blob/main/emv/protocol/structures.py
# - https://stackoverflow.com/questions/49205117/looking-to-parse-emv-data-into-tlv
# socket server:
# - https://gist.github.com/lkraider/abd24f224751a6edc5c5
# - https://gist.github.com/gruzovator/edef1011b6886615c01a