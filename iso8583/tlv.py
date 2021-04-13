"""TLV lib"""


class TLV(object):
    """TLV Processor"""

    def __init__(self, tlv=None):
        if tlv is not None:
            self.raw = self._read_str(tlv)

    def _get_length(self, raw):
        length = int(raw[:2], 16)
        data = raw[2:]
        assert length == len(data), f"Length of TLV data is {length}, but actual length is {len(data)}"
        return length, data

    def is_two_byte(self, val):
        """A tag is at least two bytes long if the least significant
        5 bits of the first byte are set."""
        return val & 0b00011111 == 0b00011111

    def read(self, tlv_data):
        # print(tlv_data)
        length, tlv_data = self._get_length(tlv_data)
        print(self.read_byte(tlv_data))

    def _read_str(self, tlv):
        # print(tlv_data)
        length, tlv_data = self._get_length(tlv)
        print(self.read_byte(tlv_data))

    def read_byte(self, data):
        print(data[:2])
        print(int(data[:2], 16))
        print(bytearray.fromhex(data[:2]))
        # 5F = 01 0 11111 00000000
        b_array = [0 for _ in range(8)]
        for i in range(8):
            if int(data[:2], 16) & 1 << i > 0:
                b_array[7 - i] = 1
        return b_array