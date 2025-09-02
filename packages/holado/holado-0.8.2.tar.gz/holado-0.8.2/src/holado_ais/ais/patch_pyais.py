
#################################################
# HolAdo (Holistic Automation do)
#
# (C) Copyright 2021-2025 by Eric Klumpp
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# The Software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the Software.
#################################################


#################################################
#
# Patches are done to follow ITU recommendation:
# https://www.e-navigation.nl/sites/default/files/R-REC-M.1371-5-201402-I!!PDF-E_1.pdf
#
#################################################


import logging
from bitarray import bitarray
import attr
import typing
import pyais
from pyais.messages import Payload, bit_field, from_mmsi, NMEA_VALUE, CommunicationStateMixin, from_speed, to_speed,\
    from_lat_lon, to_lat_lon, from_10th, to_10th, from_lat_lon_600, to_lat_lon_600,\
    from_turn, to_turn, ANY_MESSAGE
from pyais.util import get_int, from_bytes_signed, from_bytes, bits2bytes, chunks, str_to_bin, bytes2bits
from pyais.exceptions import InvalidDataTypeException
from pyais.constants import NavigationStatus, EpfdType, ShipType, NavAid, StationType, TransmitMode, StationIntervals,\
    TurnRate, ManeuverIndicator
import functools

logger = logging.getLogger(__name__)



### Fix conversion of message types to/from bitarray

# All @ at end of string are considered padding.
# Note: in pyais implementation, decode is stopped at first @, which can be a regular field information, and following regular characters are skipped.
def HA_decode_bin_as_ascii6(bit_arr: bitarray) -> str:
    """
    Decode binary data as 6 bit ASCII.
    :param bit_arr: array of bits
    :return: ASCII String
    """
    string: str = ""
    c: bitarray
    for c in chunks(bit_arr, 6):  # type:ignore
        n: int = from_bytes(c.tobytes()) >> 2

        # Last entry may not have 6 bits
        if len(c) != 6:
            n >> (6 - len(c))

        if n < 0x20:
            n += 0x40

        string += chr(n)
    
    # Remove all @ at end since they correspond to padding
    string = string.rstrip('@')
    
    # Remove spaces as some encoders make padding with spaces instead of @
    return string.strip()

pyais.util.decode_bin_as_ascii6 = HA_decode_bin_as_ascii6


def HA_int_to_bin(val: typing.Union[int, bool], width: int, signed: bool = True) -> bitarray:
    """
    Convert an integer or boolean value to binary. 
    Compared to pyais implementation, the behaviour is changed if the value is too great to fit into
    `width` bits: 
      - in pyais, the maximum possible number that still fits is used,
      - in this implementation, a ValueError is raised.

    @param val:     Any integer or boolean value.
    @param width:   The bit width. If less than width bits are required, leading zeros are added.
    @param signed:  Set to True/False if the value is signed or not.
    @return:        The binary representation of value with exactly width bits. Type is bitarray.
    """
    # Compute the total number of bytes required to hold up to `width` bits.
    n_bytes, mod = divmod(width, 8)
    if mod > 0:
        n_bytes += 1

    # If the value is too big, return a bitarray of all 1's
    mask = (1 << width) - 1
    if val > mask:
        raise ValueError(f"Value {val} is too big for bit width {width} (max possible value: {mask})")

    bits = bitarray(endian='big')
    bits.frombytes(val.to_bytes(n_bytes, 'big', signed=signed))
    return bits[8 - mod if mod else 0:]

pyais.util.int_to_bin = HA_int_to_bin
pyais.messages.int_to_bin = HA_int_to_bin


@attr.s(slots=True)
class HAPayload(Payload):
    """Payload class with fix in to/from bitarray conversion.
    """

    @classmethod
    def from_bitarray(cls, bit_arr: bitarray) -> "ANY_MESSAGE":
        cur: int = 0
        end: int = 0
        length: int = len(bit_arr)
        kwargs: typing.Dict[str, typing.Any] = {}
        
        # Manage field with a variable length
        index_variable_length_field: int = None
        cursor_variable_length_field_beg: int = None
        cursor_variable_length_field_end: int = None

        # Iterate over the bits until a variable length field or the last bit of the bitarray or all fields are fully decoded
        for field_index, field in enumerate(cls.fields()):
            # Stop if field has a variable length
            if field.metadata['variable_length']:
                index_variable_length_field = field_index
                cursor_variable_length_field_beg = cur
                break
            
            if end >= length:
                # All fields that did not fit into the bit array are None
                kwargs[field.name] = None
                continue

            width = field.metadata['width']
            end = min(length, cur + width)
            bits = bit_arr[cur: end]
            
            kwargs[field.name] = cls._bitarray_to_field_type(bits, field)
            cur = end
        
        if index_variable_length_field is not None:
            # Iterate over fields in reverse order until variable length field
            end = length
            cur = length
            
            last_fields = tuple(cls.fields())[index_variable_length_field+1:]
            for field in reversed(last_fields):
                if end <= cursor_variable_length_field_beg:
                    # All fields that did not fit into the bit array are None
                    kwargs[field.name] = None
                    continue
                
                width = field.metadata['width']
                cur = max(cursor_variable_length_field_beg, end - width)
                bits = bit_arr[cur: end]
                
                kwargs[field.name] = cls._bitarray_to_field_type(bits, field)
                end = cur
            
            # Add variable length field
            cursor_variable_length_field_end = end
            field = cls.fields()[index_variable_length_field]
            bits = bit_arr[cursor_variable_length_field_beg: cursor_variable_length_field_end]
            kwargs[field.name] = cls._bitarray_to_field_type(bits, field)

        return cls(**kwargs)  # type:ignore

    @classmethod
    def _bitarray_to_field_type(cls, bits, field) -> typing.Any:
        val: typing.Any
        d_type = field.metadata['d_type']
        converter = field.metadata['to_converter']
        
        # Get the correct data type and decoding function
        if d_type == int or d_type == bool or d_type == float:
            shift = (8 - (len(bits) % 8)) % 8
            if field.metadata['signed']:
                val = from_bytes_signed(bits) >> shift
            else:
                val = from_bytes(bits) >> shift

            if d_type == float:
                val = float(val)
            elif d_type == bool:
                val = bool(val)

        elif d_type == str:
            val = HA_decode_bin_as_ascii6(bits)
        elif d_type == bytes:
            val = bits2bytes(bits)
        else:
            raise InvalidDataTypeException(d_type)

        val = converter(val) if converter is not None else val
        
        return val

    def to_bitarray(self) -> bitarray:
        """
        Convert all attributes of a given Payload/Message to binary.
        """
        out = bitarray()
        for field in self.fields():
            width = field.metadata['width']
            d_type = field.metadata['d_type']
            converter = field.metadata['from_converter']
            signed = field.metadata['signed']
            variable_length = field.metadata['variable_length']

            val = getattr(self, field.name)
            if val is None:
                continue

            val = converter(val) if converter is not None else val
            
            try:
                if d_type in (bool, int):
                    bits = HA_int_to_bin(val, width, signed=signed)
                elif d_type == float:
                    val = int(val)
                    bits = HA_int_to_bin(val, width, signed=signed)
                elif d_type == str:
                    trailing_spaces = not variable_length
                    bits = str_to_bin(val, width, trailing_spaces=trailing_spaces)
                elif d_type == bytes:
                    bits = bytes2bits(val, default=bitarray('0' * width))
                else:
                    raise InvalidDataTypeException(d_type)
            except ValueError as exc:
                raise ValueError(f"Invalid value for field '{field.name}': {exc}") from None

            bits = bits[:width]
            out += bits

        return out


# Fix message types:
# - Use fixes of Payload implemented in HAPayload, in all message types
# - type 21: exclude full_name property from asdict result
# - type 26: fix create and from_bitarray methods

@attr.s(slots=True)
class HAMessageType1(HAPayload, CommunicationStateMixin):
    """
    AIS Vessel position report using SOTDMA (Self-Organizing Time Division Multiple Access)
    """
    msg_type = bit_field(6, int, default=1, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    status = bit_field(4, int, default=0, converter=NavigationStatus.from_value, signed=False)
    turn = bit_field(8, float, default=TurnRate.NO_TI_DEFAULT, signed=True, to_converter=to_turn, from_converter=from_turn)
    speed = bit_field(10, float, from_converter=from_speed, to_converter=to_speed, default=0, signed=False)
    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, default=0, signed=True)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, default=0, signed=True)
    course = bit_field(12, float, from_converter=from_10th, to_converter=to_10th, default=0, signed=False)
    heading = bit_field(9, int, default=0, signed=False)
    second = bit_field(6, int, default=0, signed=False)
    maneuver = bit_field(2, int, default=0, from_converter=ManeuverIndicator.from_value,
                         to_converter=ManeuverIndicator.from_value, signed=False)
    spare_1 = bit_field(3, bytes, default=b'', is_spare=True)
    raim = bit_field(1, bool, default=0)
    radio = bit_field(19, int, default=0, signed=False)

pyais.messages.MessageType1 = HAMessageType1
pyais.messages.MSG_CLASS[1] = pyais.messages.MessageType1


class HAMessageType2(HAMessageType1):
    """
    AIS Vessel position report using SOTDMA (Self-Organizing Time Division Multiple Access)
    """
    msg_type = bit_field(6, int, default=2)

pyais.messages.MessageType2 = HAMessageType2
pyais.messages.MSG_CLASS[2] = pyais.messages.MessageType2


class HAMessageType3(HAMessageType1):
    """
    AIS Vessel position report using ITDMA (Incremental Time Division Multiple Access)
    """
    msg_type = bit_field(6, int, default=3)

pyais.messages.MessageType3 = HAMessageType3
pyais.messages.MSG_CLASS[3] = pyais.messages.MessageType3


@attr.s(slots=True)
class HAMessageType4(HAPayload, CommunicationStateMixin):
    """
    AIS Vessel position report using SOTDMA (Self-Organizing Time Division Multiple Access)
    """
    msg_type = bit_field(6, int, default=4, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    year = bit_field(14, int, default=1970, signed=False)
    month = bit_field(4, int, default=1, signed=False)
    day = bit_field(5, int, default=1, signed=False)
    hour = bit_field(5, int, default=0, signed=False)
    minute = bit_field(6, int, default=0, signed=False)
    second = bit_field(6, int, default=0, signed=False)
    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    epfd = bit_field(4, int, default=0, from_converter=EpfdType.from_value, to_converter=EpfdType.from_value,
                     signed=False)
    spare_1 = bit_field(10, bytes, default=b'', is_spare=True)
    raim = bit_field(1, bool, default=0)
    radio = bit_field(19, int, default=0, signed=False)

pyais.messages.MessageType4 = HAMessageType4
pyais.messages.MSG_CLASS[4] = pyais.messages.MessageType4


@attr.s(slots=True)
class HAMessageType5(HAPayload):
    """
    Static and Voyage Related Data
    """
    msg_type = bit_field(6, int, default=5, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    ais_version = bit_field(2, int, default=0, signed=False)
    imo = bit_field(30, int, default=0, signed=False)
    callsign = bit_field(42, str, default='')
    shipname = bit_field(120, str, default='')
    ship_type = bit_field(8, int, default=0, from_converter=ShipType.from_value, to_converter=ShipType.from_value)
    to_bow = bit_field(9, int, default=0, signed=False)
    to_stern = bit_field(9, int, default=0, signed=False)
    to_port = bit_field(6, int, default=0, signed=False)
    to_starboard = bit_field(6, int, default=0, signed=False)
    epfd = bit_field(4, int, default=0, from_converter=EpfdType.from_value, to_converter=EpfdType.from_value)
    month = bit_field(4, int, default=0, signed=False)
    day = bit_field(5, int, default=0, signed=False)
    hour = bit_field(5, int, default=0, signed=False)
    minute = bit_field(6, int, default=0, signed=False)
    draught = bit_field(8, float, from_converter=from_10th, to_converter=to_10th, default=0, signed=False)
    destination = bit_field(120, str, default='')
    dte = bit_field(1, bool, default=0, signed=False)
    spare_1 = bit_field(1, bytes, default=b'', is_spare=True)

pyais.messages.MessageType5 = HAMessageType5
pyais.messages.MSG_CLASS[5] = pyais.messages.MessageType5


@attr.s(slots=True)
class HAMessageType6(HAPayload):
    """
    Binary Addresses Message
    """
    msg_type = bit_field(6, int, default=6)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    seqno = bit_field(2, int, default=0, signed=False)
    dest_mmsi = bit_field(30, int, from_converter=from_mmsi)
    retransmit = bit_field(1, bool, default=False, signed=False)
    spare_1 = bit_field(1, bytes, default=b'', is_spare=True)
    dac = bit_field(10, int, default=0, signed=False)
    fid = bit_field(6, int, default=0, signed=False)
    data = bit_field(920, bytes, default=b'', variable_length=True)

pyais.messages.MessageType6 = HAMessageType6
pyais.messages.MSG_CLASS[6] = pyais.messages.MessageType6


@attr.s(slots=True)
class HAMessageType7(HAPayload):
    """
    Binary Acknowledge
    """
    msg_type = bit_field(6, int, default=7, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    mmsi1 = bit_field(30, int, default=0, from_converter=from_mmsi)
    mmsiseq1 = bit_field(2, int, default=0, signed=False)
    mmsi2 = bit_field(30, int, default=0, from_converter=from_mmsi)
    mmsiseq2 = bit_field(2, int, default=0, signed=False)
    mmsi3 = bit_field(30, int, default=0, from_converter=from_mmsi)
    mmsiseq3 = bit_field(2, int, default=0, signed=False)
    mmsi4 = bit_field(30, int, default=0, from_converter=from_mmsi)
    mmsiseq4 = bit_field(2, int, default=0, signed=False)

pyais.messages.MessageType7 = HAMessageType7
pyais.messages.MSG_CLASS[7] = pyais.messages.MessageType7


@attr.s(slots=True)
class HAMessageType8(HAPayload):
    """
    Binary Acknowledge
    """
    msg_type = bit_field(6, int, default=8, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    dac = bit_field(10, int, default=0, signed=False)
    fid = bit_field(6, int, default=0, signed=False)
    data = bit_field(952, bytes, default=b'', variable_length=True)

pyais.messages.MessageType8 = HAMessageType8
pyais.messages.MSG_CLASS[8] = pyais.messages.MessageType8


@attr.s(slots=True)
class HAMessageType9(HAPayload, CommunicationStateMixin):
    """
    Standard SAR Aircraft Position Report
    """
    msg_type = bit_field(6, int, default=9, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    alt = bit_field(12, int, default=0, signed=False)
    # speed over ground is in knots, not deciknots
    speed = bit_field(10, float, default=0, signed=False)
    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    course = bit_field(12, float, from_converter=from_10th, to_converter=to_10th, default=0, signed=False)
    second = bit_field(6, int, default=0, signed=False)

    reserved_1 = bit_field(8, int, default=0)
    dte = bit_field(1, bool, default=0)
    spare_1 = bit_field(3, bytes, default=b'', is_spare=True)
    assigned = bit_field(1, bool, default=0)
    raim = bit_field(1, bool, default=0)
    radio = bit_field(20, int, default=0, signed=False)

pyais.messages.MessageType9 = HAMessageType9
pyais.messages.MSG_CLASS[9] = pyais.messages.MessageType9


@attr.s(slots=True)
class HAMessageType10(HAPayload):
    """
    UTC/Date Inquiry
    """
    msg_type = bit_field(6, int, default=10, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    dest_mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_2 = bit_field(2, bytes, default=b'', is_spare=True)

pyais.messages.MessageType10 = HAMessageType10
pyais.messages.MSG_CLASS[10] = pyais.messages.MessageType10


class HAMessageType11(HAMessageType4):
    """
    UTC/Date Response
    """
    msg_type = bit_field(6, int, default=11, signed=False)

pyais.messages.MessageType11 = HAMessageType11
pyais.messages.MSG_CLASS[11] = pyais.messages.MessageType11


@attr.s(slots=True)
class HAMessageType12(HAPayload):
    """
    Addressed Safety-Related Message
    """
    msg_type = bit_field(6, int, default=12, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    seqno = bit_field(2, int, default=0, signed=False)
    dest_mmsi = bit_field(30, int, from_converter=from_mmsi)
    retransmit = bit_field(1, bool, default=False, signed=False)
    spare_1 = bit_field(1, bytes, default=b'', is_spare=True)
    text = bit_field(936, str, default='', variable_length=True)

pyais.messages.MessageType12 = HAMessageType12
pyais.messages.MSG_CLASS[12] = pyais.messages.MessageType12


class HAMessageType13(HAMessageType7):
    """
    Identical to type 7
    """
    msg_type = bit_field(6, int, default=13, signed=False)

pyais.messages.MessageType13 = HAMessageType13
pyais.messages.MSG_CLASS[13] = pyais.messages.MessageType13


@attr.s(slots=True)
class HAMessageType14(HAPayload):
    """
    Safety-Related Broadcast Message
    """
    msg_type = bit_field(6, int, default=14, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    text = bit_field(968, str, default='', variable_length=True)

pyais.messages.MessageType14 = HAMessageType14
pyais.messages.MSG_CLASS[14] = pyais.messages.MessageType14


@attr.s(slots=True)
class HAMessageType15(HAPayload):
    """
    Interrogation
    """
    msg_type = bit_field(6, int, default=15, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    mmsi1 = bit_field(30, int, default=0, from_converter=from_mmsi)
    type1_1 = bit_field(6, int, default=0, signed=False)
    offset1_1 = bit_field(12, int, default=0, signed=False)
    spare_2 = bit_field(2, bytes, default=b'', is_spare=True)
    type1_2 = bit_field(6, int, default=0, signed=False)
    offset1_2 = bit_field(12, int, default=0, signed=False)
    spare_3 = bit_field(2, bytes, default=b'', is_spare=True)
    mmsi2 = bit_field(30, int, default=0, from_converter=from_mmsi)
    type2_1 = bit_field(6, int, default=0, signed=False)
    offset2_1 = bit_field(12, int, default=0, signed=False)
    spare_4 = bit_field(2, bytes, default=b'', is_spare=True)

pyais.messages.MessageType15 = HAMessageType15
pyais.messages.MSG_CLASS[15] = pyais.messages.MessageType15


@attr.s(slots=True)
class HAMessageType16DestinationA(HAPayload):
    """
    Assignment Mode Command
    """
    msg_type = bit_field(6, int, default=16, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    mmsi1 = bit_field(30, int, default=0, from_converter=from_mmsi)
    offset1 = bit_field(12, int, default=0, signed=False)
    increment1 = bit_field(10, int, default=0, signed=False)
    spare_2 = bit_field(4, bytes, default=b'', is_spare=True)

pyais.messages.MessageType16DestinationA = HAMessageType16DestinationA


@attr.s(slots=True)
class HAMessageType16DestinationAB(HAPayload):
    """
    Assignment Mode Command
    """
    msg_type = bit_field(6, int, default=16, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    mmsi1 = bit_field(30, int, default=0, from_converter=from_mmsi)
    offset1 = bit_field(12, int, default=0, signed=False)
    increment1 = bit_field(10, int, default=0, signed=False)

    mmsi2 = bit_field(30, int, default=0, from_converter=from_mmsi)
    offset2 = bit_field(12, int, default=0, signed=False)
    increment2 = bit_field(10, int, default=0, signed=False)

pyais.messages.MessageType16DestinationAB = HAMessageType16DestinationAB


@attr.s(slots=True)
class HAMessageType16(HAPayload):
    @classmethod
    def create(cls, **kwargs: typing.Union[str, float, int, bool, bytes]) -> "ANY_MESSAGE":
        if 'mmsi2' in kwargs:
            return HAMessageType16DestinationAB.create(**kwargs)
        else:
            return HAMessageType16DestinationA.create(**kwargs)

    @classmethod
    def from_bitarray(cls, bit_arr: bitarray) -> "ANY_MESSAGE":
        if len(bit_arr) > 96:
            return HAMessageType16DestinationAB.from_bitarray(bit_arr)
        else:
            return HAMessageType16DestinationA.from_bitarray(bit_arr)

pyais.messages.MessageType16 = HAMessageType16
pyais.messages.MSG_CLASS[16] = pyais.messages.MessageType16


@attr.s(slots=True)
class HAMessageType17(HAPayload):
    """
    DGNSS Broadcast Binary Message
    """
    msg_type = bit_field(6, int, default=17, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)
    # Note that latitude and longitude are in units of a tenth of a minute
    lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    spare_2 = bit_field(5, bytes, default=b'', is_spare=True)
    data = bit_field(736, bytes, default=b'', variable_length=True)

pyais.messages.MessageType17 = HAMessageType17
pyais.messages.MSG_CLASS[17] = pyais.messages.MessageType17


@attr.s(slots=True)
class HAMessageType18(HAPayload, CommunicationStateMixin):
    """
    Standard Class B CS Position Report
    Src: https://gpsd.gitlab.io/gpsd/AIVDM.html#_type_18_standard_class_b_cs_position_report
    """
    msg_type = bit_field(6, int, default=18, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    reserved_1 = bit_field(8, int, default=0, signed=False)
    speed = bit_field(10, float, from_converter=from_speed, to_converter=to_speed, default=0, signed=False)
    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    course = bit_field(12, float, from_converter=from_10th, to_converter=to_10th, default=0, signed=False)
    heading = bit_field(9, int, default=0, signed=False)
    second = bit_field(6, int, default=0, signed=False)
    reserved_2 = bit_field(2, int, default=0, signed=False)
    cs = bit_field(1, bool, default=0, signed=False)
    display = bit_field(1, bool, default=0)
    dsc = bit_field(1, bool, default=0)
    band = bit_field(1, bool, default=0)
    msg22 = bit_field(1, bool, default=0)
    assigned = bit_field(1, bool, default=0)
    raim = bit_field(1, bool, default=0)
    radio = bit_field(20, int, default=0)

pyais.messages.MessageType18 = HAMessageType18
pyais.messages.MSG_CLASS[18] = pyais.messages.MessageType18


@attr.s(slots=True)
class HAMessageType19(HAPayload):
    """
    Extended Class B CS Position Report
    """
    msg_type = bit_field(6, int, default=19, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    reserved_1 = bit_field(8, int, default=0)

    speed = bit_field(10, float, from_converter=from_speed, to_converter=to_speed, default=0, signed=False)
    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    course = bit_field(12, float, from_converter=from_10th, to_converter=to_10th, default=0, signed=False)
    heading = bit_field(9, int, default=0, signed=False)
    second = bit_field(6, int, default=0, signed=False)
    reserved_2 = bit_field(4, int, default=0, signed=False)
    shipname = bit_field(120, str, default='')
    ship_type = bit_field(8, int, default=0, from_converter=ShipType.from_value, to_converter=ShipType.from_value,
                          signed=False)
    to_bow = bit_field(9, int, default=0, signed=False)
    to_stern = bit_field(9, int, default=0, signed=False)
    to_port = bit_field(6, int, default=0, signed=False)
    to_starboard = bit_field(6, int, default=0, signed=False)
    epfd = bit_field(4, int, default=0, from_converter=EpfdType.from_value, to_converter=EpfdType.from_value)
    raim = bit_field(1, bool, default=0)
    dte = bit_field(1, bool, default=0)
    assigned = bit_field(1, bool, default=0, signed=False)
    spare_1 = bit_field(4, bytes, default=b'', is_spare=True)

pyais.messages.MessageType19 = HAMessageType19
pyais.messages.MSG_CLASS[19] = pyais.messages.MessageType19


@attr.s(slots=True)
class HAMessageType20ReservationBlock1(HAPayload):
    """
    Data Link Management Message
    """
    msg_type = bit_field(6, int, default=20, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    offset1 = bit_field(12, int, default=0, signed=False)
    number1 = bit_field(4, int, default=0, signed=False)
    timeout1 = bit_field(3, int, default=0, signed=False)
    increment1 = bit_field(11, int, default=0, signed=False)
    spare_2 = bit_field(2, bytes, default=b'', is_spare=True)

pyais.messages.MessageType20ReservationBlock1 = HAMessageType20ReservationBlock1


@attr.s(slots=True)
class HAMessageType20ReservationBlock12(HAPayload):
    """
    Data Link Management Message
    """
    msg_type = bit_field(6, int, default=20, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    offset1 = bit_field(12, int, default=0, signed=False)
    number1 = bit_field(4, int, default=0, signed=False)
    timeout1 = bit_field(3, int, default=0, signed=False)
    increment1 = bit_field(11, int, default=0, signed=False)

    offset2 = bit_field(12, int, default=0, signed=False)
    number2 = bit_field(4, int, default=0, signed=False)
    timeout2 = bit_field(3, int, default=0, signed=False)
    increment2 = bit_field(11, int, default=0, signed=False)
    spare_2 = bit_field(4, bytes, default=b'', is_spare=True)

pyais.messages.MessageType20ReservationBlock12 = HAMessageType20ReservationBlock12


@attr.s(slots=True)
class HAMessageType20ReservationBlock123(HAPayload):
    """
    Data Link Management Message
    """
    msg_type = bit_field(6, int, default=20, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    offset1 = bit_field(12, int, default=0, signed=False)
    number1 = bit_field(4, int, default=0, signed=False)
    timeout1 = bit_field(3, int, default=0, signed=False)
    increment1 = bit_field(11, int, default=0, signed=False)

    offset2 = bit_field(12, int, default=0, signed=False)
    number2 = bit_field(4, int, default=0, signed=False)
    timeout2 = bit_field(3, int, default=0, signed=False)
    increment2 = bit_field(11, int, default=0, signed=False)

    offset3 = bit_field(12, int, default=0, signed=False)
    number3 = bit_field(4, int, default=0, signed=False)
    timeout3 = bit_field(3, int, default=0, signed=False)
    increment3 = bit_field(11, int, default=0, signed=False)
    spare_2 = bit_field(6, bytes, default=b'', is_spare=True)

pyais.messages.MessageType20ReservationBlock123 = HAMessageType20ReservationBlock123


@attr.s(slots=True)
class HAMessageType20ReservationBlock1234(HAPayload):
    """
    Data Link Management Message
    """
    msg_type = bit_field(6, int, default=20, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    offset1 = bit_field(12, int, default=0, signed=False)
    number1 = bit_field(4, int, default=0, signed=False)
    timeout1 = bit_field(3, int, default=0, signed=False)
    increment1 = bit_field(11, int, default=0, signed=False)

    offset2 = bit_field(12, int, default=0, signed=False)
    number2 = bit_field(4, int, default=0, signed=False)
    timeout2 = bit_field(3, int, default=0, signed=False)
    increment2 = bit_field(11, int, default=0, signed=False)

    offset3 = bit_field(12, int, default=0, signed=False)
    number3 = bit_field(4, int, default=0, signed=False)
    timeout3 = bit_field(3, int, default=0, signed=False)
    increment3 = bit_field(11, int, default=0, signed=False)

    offset4 = bit_field(12, int, default=0, signed=False)
    number4 = bit_field(4, int, default=0, signed=False)
    timeout4 = bit_field(3, int, default=0, signed=False)
    increment4 = bit_field(11, int, default=0, signed=False)

pyais.messages.MessageType20ReservationBlock1234 = HAMessageType20ReservationBlock1234


@attr.s(slots=True)
class HAMessageType20(HAPayload):
    @classmethod
    def create(cls, **kwargs: typing.Union[str, float, int, bool, bytes]) -> "ANY_MESSAGE":
        if 'offset4' in kwargs and int(kwargs['offset4']) > 0:
            return HAMessageType20ReservationBlock1234.create(**kwargs)
        elif 'offset3' in kwargs and int(kwargs['offset3']) > 0:
            return HAMessageType20ReservationBlock123.create(**kwargs)
        elif 'offset2' in kwargs and int(kwargs['offset2']) > 0:
            return HAMessageType20ReservationBlock12.create(**kwargs)
        else:
            return HAMessageType20ReservationBlock1.create(**kwargs)

    @classmethod
    def from_bitarray(cls, bit_arr: bitarray) -> "ANY_MESSAGE":
        if len(bit_arr) > 136:
            return HAMessageType20ReservationBlock1234.from_bitarray(bit_arr)
        elif len(bit_arr) > 104:
            return HAMessageType20ReservationBlock123.from_bitarray(bit_arr)
        elif len(bit_arr) > 72:
            return HAMessageType20ReservationBlock12.from_bitarray(bit_arr)
        else:
            return HAMessageType20ReservationBlock1.from_bitarray(bit_arr)

pyais.messages.MessageType20 = HAMessageType20
pyais.messages.MSG_CLASS[20] = pyais.messages.MessageType20


@attr.s(slots=True)
class HAMessageType21(HAPayload):
    """
    Aid-to-Navigation Report
    """
    msg_type = bit_field(6, int, default=21, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    aid_type = bit_field(5, int, default=0, from_converter=NavAid.from_value, to_converter=NavAid.from_value,
                         signed=False)
    name = bit_field(120, str, default='')

    accuracy = bit_field(1, bool, default=0, signed=False)
    lon = bit_field(28, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    lat = bit_field(27, float, from_converter=from_lat_lon, to_converter=to_lat_lon, signed=True, default=0)
    to_bow = bit_field(9, int, default=0, signed=False)
    to_stern = bit_field(9, int, default=0, signed=False)
    to_port = bit_field(6, int, default=0, signed=False)
    to_starboard = bit_field(6, int, default=0, signed=False)

    epfd = bit_field(4, int, default=0, from_converter=EpfdType.from_value, to_converter=EpfdType.from_value)
    second = bit_field(6, int, default=0, signed=False)
    off_position = bit_field(1, bool, default=0)
    reserved_1 = bit_field(8, int, default=0, signed=False)
    raim = bit_field(1, bool, default=0)
    virtual_aid = bit_field(1, bool, default=0)
    assigned = bit_field(1, bool, default=0)
    spare_1 = bit_field(1, bytes, default=b'', is_spare=True)
    name_ext = bit_field(88, str, default='')

    @functools.cached_property
    def full_name(self) -> str:
        """The name field is up to 20 characters of 6-bit ASCII. If this field
        is full (has no trailing @ characters) the decoder should interpret
        the Name Extension field later in the message (no more than 14 6-bit
        characters) and concatenate it to this one to obtain the full name."""
        if self.name:
            if self.name_ext:
                return f"{self.name}{self.name_ext}"
            return str(self.name)
        return ""
    
    # TODO: replace following override by a generic implementation in Payload.asdict that exports only fields
    def asdict(self, enum_as_int: bool = False) -> typing.Dict[str, typing.Optional[NMEA_VALUE]]:
        res = super().asdict(enum_as_int)
        
        # Remove key 'full_name' if present
        if 'full_name' in res:
            del res['full_name']
        
        return res

pyais.messages.MessageType21 = HAMessageType21
pyais.messages.MSG_CLASS[21] = pyais.messages.MessageType21


@attr.s(slots=True)
class HAMessageType22Addressed(HAPayload):
    """
    Channel Management
    """
    msg_type = bit_field(6, int, default=22, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    channel_a = bit_field(12, int, default=0, signed=False)
    channel_b = bit_field(12, int, default=0, signed=False)
    txrx = bit_field(4, int, default=0, signed=False)
    power = bit_field(1, bool, default=0)  # 69 bits

    # If it is addressed (addressed field is 1),
    # the same span of data is interpreted as two 30-bit MMSIs
    # beginning at bit offsets 69 and 104 respectively.
    dest1 = bit_field(30, int, default=0, from_converter=from_mmsi)
    empty_1 = bit_field(5, int, default=0)
    dest2 = bit_field(30, int, default=0, from_converter=from_mmsi)
    empty_2 = bit_field(5, int, default=0)

    addressed = bit_field(1, bool, default=0)
    band_a = bit_field(1, bool, default=0)
    band_b = bit_field(1, bool, default=0)
    zonesize = bit_field(3, int, default=0)
    spare_2 = bit_field(23, bytes, default=b'', is_spare=True)

pyais.messages.MessageType22Addressed = HAMessageType22Addressed


@attr.s(slots=True)
class HAMessageType22Broadcast(HAPayload):
    """
    Channel Management
    """
    msg_type = bit_field(6, int, default=22, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    channel_a = bit_field(12, int, default=0, signed=False)
    channel_b = bit_field(12, int, default=0, signed=False)
    txrx = bit_field(4, int, default=0, signed=False)
    power = bit_field(1, bool, default=0)

    # If the message is broadcast (addressed field is 0),
    # the ne_lon, ne_lat, sw_lon, and sw_lat fields are the
    # corners of a rectangular jurisdiction area over which control parameter
    # ne_lon, ne_lat, sw_lon, and sw_lat fields are in 0.1 minutes
    ne_lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    ne_lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    sw_lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    sw_lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)

    addressed = bit_field(1, bool, default=0)
    band_a = bit_field(1, bool, default=0)
    band_b = bit_field(1, bool, default=0)
    zonesize = bit_field(3, int, default=0, signed=False)
    spare_2 = bit_field(23, bytes, default=b'', is_spare=True)

pyais.messages.MessageType22Broadcast = HAMessageType22Broadcast


@attr.s(slots=True)
class HAMessageType23(HAPayload):
    """
    Group Assignment Command
    """
    msg_type = bit_field(6, int, default=23, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)
    spare_1 = bit_field(2, bytes, default=b'', is_spare=True)

    ne_lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    ne_lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    sw_lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    sw_lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)

    station_type = bit_field(4, int, default=0, from_converter=StationType.from_value,
                             to_converter=StationType.from_value)
    ship_type = bit_field(8, int, default=0, from_converter=ShipType.from_value, to_converter=ShipType.from_value)
    spare_2 = bit_field(22, bytes, default=b'', is_spare=True)

    txrx = bit_field(2, int, default=0, from_converter=TransmitMode.from_value, to_converter=TransmitMode.from_value,
                     signed=False)
    interval = bit_field(4, int, default=0, from_converter=StationIntervals.from_value,
                         to_converter=StationIntervals.from_value)
    quiet = bit_field(4, int, default=0, signed=False)
    spare_3 = bit_field(6, bytes, default=b'', is_spare=True)

pyais.messages.MessageType23 = HAMessageType23
pyais.messages.MSG_CLASS[23] = pyais.messages.MessageType23


@attr.s(slots=True)
class HAMessageType24PartA(HAPayload):
    msg_type = bit_field(6, int, default=24, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    # partno = bit_field(2, int, default=0, signed=False)
    reserved = bit_field(1, int, default=0, signed=False, is_spare=True)
    partno = bit_field(1, int, default=0, signed=False)
    shipname = bit_field(120, str, default='')
    spare_1 = bit_field(8, bytes, default=b'', is_spare=True)

pyais.messages.MessageType24PartA = HAMessageType24PartA


@attr.s(slots=True)
class HAMessageType24PartB(HAPayload):
    msg_type = bit_field(6, int, default=24, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    # partno = bit_field(2, int, default=0, signed=False)
    reserved = bit_field(1, int, default=0, signed=False, is_spare=True)
    partno = bit_field(1, int, default=0, signed=False)
    ship_type = bit_field(8, int, default=0, signed=False)
    vendorid = bit_field(18, str, default='', signed=False)
    model = bit_field(4, int, default=0, signed=False)
    serial = bit_field(20, int, default=0, signed=False)
    callsign = bit_field(42, str, default='')

    to_bow = bit_field(9, int, default=0, signed=False)
    to_stern = bit_field(9, int, default=0, signed=False)
    to_port = bit_field(6, int, default=0, signed=False)
    to_starboard = bit_field(6, int, default=0, signed=False)

    spare_1 = bit_field(6, bytes, default=b'', is_spare=True)

pyais.messages.MessageType24PartB = HAMessageType24PartB


@attr.s(slots=True)
class HAMessageType25AddressedStructured(HAPayload):
    msg_type = bit_field(6, int, default=25, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    dest_mmsi = bit_field(30, int, default=0, from_converter=from_mmsi, signed=False)
    spare = bit_field(2, int, default=0, signed=False, is_spare=True)
    app_id = bit_field(16, int, default=0, signed=False)
    data = bit_field(80, bytes, default=b'', variable_length=True)
    
pyais.messages.MessageType25AddressedStructured = HAMessageType25AddressedStructured


@attr.s(slots=True)
class HAMessageType25AddressedUnstructured(HAPayload):
    msg_type = bit_field(6, int, default=25, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    dest_mmsi = bit_field(30, int, default=0, from_converter=from_mmsi)
    spare = bit_field(2, int, default=0, signed=False, is_spare=True)
    data = bit_field(96, bytes, default=b'', variable_length=True)

pyais.messages.MessageType25AddressedUnstructured = HAMessageType25AddressedUnstructured


@attr.s(slots=True)
class HAMessageType26AddressedStructured(HAPayload, CommunicationStateMixin):
    msg_type = bit_field(6, int, default=26, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    dest_mmsi = bit_field(30, int, default=0, from_converter=from_mmsi)
    spare1 = bit_field(2, int, default=0, signed=False, is_spare=True)
    app_id = bit_field(16, int, default=0, signed=False)
    data = bit_field(952, bytes, default=b'', variable_length=True)
    spare2 = bit_field(4, int, default=0, signed=False, is_spare=True)
    radio = bit_field(20, int, default=0, signed=False)

pyais.messages.MessageType26AddressedStructured = HAMessageType26AddressedStructured


@attr.s(slots=True)
class HAMessageType26BroadcastStructured(HAPayload, CommunicationStateMixin):
    msg_type = bit_field(6, int, default=26, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    app_id = bit_field(16, int, default=0, signed=False)
    data = bit_field(984, bytes, default=b'', variable_length=True)
    spare2 = bit_field(4, int, default=0, signed=False, is_spare=True)
    radio = bit_field(20, int, default=0, signed=False)

pyais.messages.MessageType26BroadcastStructured = HAMessageType26BroadcastStructured


@attr.s(slots=True)
class HAMessageType26AddressedUnstructured(HAPayload, CommunicationStateMixin):
    msg_type = bit_field(6, int, default=26, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    dest_mmsi = bit_field(30, int, default=0, from_converter=from_mmsi)
    spare1 = bit_field(2, int, default=0, signed=False, is_spare=True)
    data = bit_field(968, bytes, default=b'', variable_length=True)
    spare2 = bit_field(4, int, default=0, signed=False, is_spare=True)
    radio = bit_field(20, int, default=0, signed=False)

pyais.messages.MessageType26AddressedUnstructured = HAMessageType26AddressedUnstructured


@attr.s(slots=True)
class HAMessageType26BroadcastUnstructured(HAPayload, CommunicationStateMixin):
    msg_type = bit_field(6, int, default=26, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    addressed = bit_field(1, bool, default=0, signed=False)
    structured = bit_field(1, bool, default=0, signed=False)

    data = bit_field(1000, bytes, default=b'', variable_length=True)
    spare2 = bit_field(4, int, default=0, signed=False, is_spare=True)
    radio = bit_field(20, int, default=0, signed=False)

pyais.messages.MessageType26BroadcastUnstructured = HAMessageType26BroadcastUnstructured


class HAMessageType26(HAPayload):
    """
    Multiple Slot Binary Message

    NOTE: This message type is quite uncommon and
    I was not able find any real world occurrence of the type.
    Also documentation seems to vary. Use with caution.
    """

    @classmethod
    def create(cls, **kwargs: typing.Union[str, float, int, bool, bytes]) -> "ANY_MESSAGE":
        addressed = kwargs.get('addressed', False)
        structured = kwargs.get('structured', False)

        if addressed:
            if structured:
                return HAMessageType26AddressedStructured.create(**kwargs)
            else:
                return HAMessageType26AddressedUnstructured.create(**kwargs)
        else:
            if structured:
                return HAMessageType26BroadcastStructured.create(**kwargs)
            else:
                return HAMessageType26BroadcastUnstructured.create(**kwargs)

    @classmethod
    def from_bitarray(cls, bit_arr: bitarray) -> "ANY_MESSAGE":
        addressed: int = get_int(bit_arr, 38, 39)
        structured: int = get_int(bit_arr, 39, 40)

        if addressed:
            if structured:
                return HAMessageType26AddressedStructured.from_bitarray(bit_arr)
            else:
                return HAMessageType26AddressedUnstructured.from_bitarray(bit_arr)
        else:
            if structured:
                return HAMessageType26BroadcastStructured.from_bitarray(bit_arr)
            else:
                return HAMessageType26BroadcastUnstructured.from_bitarray(bit_arr)

pyais.messages.MessageType26 = HAMessageType26
pyais.messages.MSG_CLASS[26] = pyais.messages.MessageType26


@attr.s(slots=True)
class HAMessageType27(HAPayload):
    """
    Long Range AIS Broadcast message
    """
    msg_type = bit_field(6, int, default=27, signed=False)
    repeat = bit_field(2, int, default=0, signed=False)
    mmsi = bit_field(30, int, from_converter=from_mmsi)

    accuracy = bit_field(1, bool, default=0, signed=False)
    raim = bit_field(1, bool, default=0, signed=False)
    status = bit_field(4, int, default=0, from_converter=NavigationStatus, to_converter=NavigationStatus, signed=False)
    lon = bit_field(18, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    lat = bit_field(17, float, from_converter=from_lat_lon_600, to_converter=to_lat_lon_600, default=0, signed=True)
    speed = bit_field(6, float, default=0, signed=False)
    course = bit_field(9, float, default=0, signed=False)
    gnss = bit_field(1, bool, default=0, signed=False)
    spare_1 = bit_field(1, bytes, default=b'', is_spare=True)

pyais.messages.MessageType27 = HAMessageType27
pyais.messages.MSG_CLASS[27] = pyais.messages.MessageType27




