import yaml
from pprint import pprint
from iso8583.loader import Config

msg = bytes.fromhex('303230307234000008C08000313634303030303130303030303030303031383430303030303030303030303031303030313130363134303131373333343734383230313130363134303131373235313230333131313433333437343830303939393230314D3939393230312020202020202020383130')

cfg = Config('dicts/sample.yaml')
print(cfg.config)
print(msg)
p = 0
print(msg[p:p + cfg.config['MTI']['Size']])
p += cfg.config['MTI']['Size']
# b = bytearray(msg[p:p + cfg.config['Bitmap']['Size']])
flags = msg[p:p + cfg.config['Bitmap']['Size']]
# Make Bitmap
_bits =  [flags[i//8] & 1 << i%8 != 0 for i in range(len(flags) * 8)]
#change order of bits
bits = []
for i in range(int(len(_bits)/8)):
    bits += _bits[i*8:i*8+8][::-1]
print(len(bits))
bitmap = []
for i, b in enumerate(bits):
    if b:
        print(i+1, b)
        bitmap.append(i + 1)
print(bitmap)
# print('7234000008C08000')
# print(bytes.fromhex('7234000008C08000'))
# print(bytearray(msg[p:p + cfg.config['Bitmap']['Size']]))