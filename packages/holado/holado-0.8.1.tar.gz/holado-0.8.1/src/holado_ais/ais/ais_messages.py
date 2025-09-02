
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

import logging
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_value.common.tables.value_table_manager import ValueTableManager
from holado_value.common.tables.converters.value_table_converter import ValueTableConverter
from typing import Union
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tools.string_tools import StrTools
from holado_binary.ipc.binary import Binary
from holado_core.common.tools.tools import Tools
from holado_python.standard_library.typing import Typing
import copy
from holado_core.common.exceptions.functional_exception import FunctionalException
from holado_ais.ais.enums import AISMessageType

logger = logging.getLogger(__name__)

try:
    import pyais
    from bitarray import bitarray
    from pyais.encode import ais_to_nmea_0183
    from pyais.messages import TagBlock
    with_pyais = True
    
    # Patch pyais with some fixes
    import holado_ais.ais.patch_pyais  # @UnusedImport
except Exception as exc:
    if Tools.do_log(logger, logging.DEBUG):
        logger.debug(f"AIS is not available. Initialization failed on error: {exc}")
    with_pyais = False
# else:
#     if Tools.do_log(logger, logging.DEBUG):
#         logger.debug(f"AIS is available !")


class AISMessages(object):
    
    @classmethod
    def is_available(cls):
        return with_pyais
    
    ###########################################################################
    # Methods depending to pyais
    ###########################################################################
    if with_pyais:
        
        def __init__(self):
            self.__tag_block_group_id = 0
        
        def default_message_data(self, msg_type:Union[int,str]):
            """Return default data values for required data by pyais but not functionnaly required.
            It is useful when generating custom messages, for example for tests.
            """
            return {}
        
        def new_message_as_bitarray_bytes(self, msg_type:Union[int,str], data:Union[dict,TableWithHeader]):
            msg = self.new_message(msg_type, data)
            res = self.convert_message_to_bytes(msg)
            return res
        
        def new_message(self, msg_type:Union[int,str], data:Union[dict,TableWithHeader]):
            if isinstance(data, TableWithHeader):
                data = self.__convert_table_to_dict(data)
            if not isinstance(data, dict):
                raise TechnicalException(f"Unexpected data type '{Typing.get_object_class_fullname(data)}'")
            
            # Add data key 'msg_type' if missing
            if 'msg_type' not in data:
                data['msg_type'] = self.__get_message_type_int(msg_type)
            
            message_type = self.__get_message_type(msg_type)
            res = message_type.create(**data)
            return res
    
        def decode(self, *args, encoded_msg=None, parts_separator=b'\n'):
            if encoded_msg is not None:
                if isinstance(encoded_msg, str):
                    encoded_bytes = encoded_msg.encode("utf-8")
                elif isinstance(encoded_msg, bytes):
                    encoded_bytes = encoded_msg
                else:
                    raise TechnicalException(f"Parameter 'encoded_msg' must be of type str or bytes")
                args = encoded_bytes.split(parts_separator)
            return pyais.decode(*args, error_if_checksum_invalid=True)
        
        def decode_message(self, msg_type:Union[int,str], bit_array:Union[str,bitarray]):
            if isinstance(bit_array, str):
                if StrTools.is_hex(bit_array) and not StrTools.is_bitarray(bit_array):
                    bit_array = Binary.convert_hex_str_to_bin_str(bit_array)
                bit_array = bitarray(bit_array)
            if not isinstance(bit_array, bitarray):
                raise TechnicalException(f"Bad parameter 'bit_array' (accepted types: bitarray, str)")
                
            message_type = self.__get_message_type(msg_type)
            return message_type.from_bitarray(bit_array)
        
        def encode_raw_payload(self, payload:Union[str,bytes], tag_block: TagBlock = None, with_tag_block=True, talker_id: str = "AIVDM", **kwargs):
            from pyais.util import encode_ascii_6
            
            if isinstance(payload, bytes):
                payload_bytes = payload
            elif isinstance(payload, str):
                payload_bytes = bytes.fromhex(payload)
            else:
                raise TechnicalException(f"Unmanaged payload type '{Typing.get_object_class_fullname(payload)}'")
            
            payload_bitarray = bitarray()
            payload_bitarray.frombytes(payload_bytes)
            payload_ascii6, fill_bits = encode_ascii_6(payload_bitarray)
            
            seq_id = kwargs.pop('seq_id') if 'seq_id' in kwargs else self.__tag_block_group_id % 10
            radio_channel = kwargs['radio_channel'] if 'radio_channel' in kwargs else 'A'
            group_id = kwargs.pop('group_id') if 'group_id' in kwargs else None
            
            # sentences = HA_ais_to_nmea_0183(payload_ascii6, talker_id, radio_channel, fill_bits, seq_id)
            sentences = ais_to_nmea_0183(payload_ascii6, talker_id, radio_channel, fill_bits, seq_id)
            return self.__encode_add_tag_block(sentences, tag_block, with_tag_block=with_tag_block, group_id=group_id)
            
        def encode(self, data, tag_block: TagBlock = None, with_tag_block=True, talker_id: str = "AIVDM", **kwargs):
            if isinstance(data, pyais.messages.Payload):
                return self.encode_msg(data, tag_block=tag_block, with_tag_block=with_tag_block, talker_id=talker_id, **kwargs)
            elif isinstance(data, dict):
                return self.encode_data(data, tag_block=tag_block, with_tag_block=with_tag_block, talker_id=talker_id, **kwargs)
            elif isinstance(data, TableWithHeader):
                return self.encode_table(data, tag_block=tag_block, with_tag_block=with_tag_block, talker_id=talker_id, **kwargs)
            else:
                raise TechnicalException(f"Unexpected data type '{Typing.get_object_class_fullname(data)}'")
        
        def encode_msg(self, msg, tag_block: TagBlock = None, with_tag_block=True, talker_id: str = "AIVDM", **kwargs):
            if not isinstance(msg, pyais.messages.Payload):
                raise TechnicalException(f"Parameter 'msg' is not an AIS message (obtained type: {Typing.get_object_class_fullname(msg)})")
            
            seq_id = kwargs.pop('seq_id') if 'seq_id' in kwargs else self.__tag_block_group_id % 10
            group_id = kwargs.pop('group_id') if 'group_id' in kwargs else None
            
            logger.print(f"+++++++ encode_msg: {msg=} ; {talker_id=} ; {kwargs=}")
            sentences = pyais.encode_msg(msg, seq_id=seq_id, talker_id=talker_id, **kwargs)
            return self.__encode_add_tag_block(sentences, tag_block, with_tag_block=with_tag_block, group_id=group_id)
        
        def encode_data(self, data, tag_block: TagBlock = None, with_tag_block=True, talker_id: str = "AIVDM", **kwargs):
            if not isinstance(data, dict):
                raise TechnicalException(f"Parameter 'data' is not a dict (obtained type: {Typing.get_object_class_fullname(data)})")
            
            seq_id = kwargs.pop('seq_id') if 'seq_id' in kwargs else self.__tag_block_group_id % 10
            group_id = kwargs.pop('group_id') if 'group_id' in kwargs else None
            
            sentences = pyais.encode_dict(data, seq_id=seq_id, talker_id=talker_id, **kwargs)
            return self.__encode_add_tag_block(sentences, tag_block, with_tag_block=with_tag_block, group_id=group_id)
        
        def encode_table(self, table, tag_block: TagBlock = None, with_tag_block=True, talker_id: str = "AIVDM", **kwargs):
            data = self.__convert_table_to_dict(table)
            return self.encode_data(data, tag_block=tag_block, with_tag_block=with_tag_block, talker_id=talker_id, **kwargs)
        
        def __encode_add_tag_block(self, encoded_sentences, tag_block: TagBlock = None, with_tag_block=True, group_id=None):
            from pyais.messages import TagBlockGroup
            
            if not with_tag_block:
                return encoded_sentences
            
            res = []
            nb_sentences = len(encoded_sentences)
            if nb_sentences > 1 and group_id is None:
                group_id = self.__tag_block_group_id
                # Increment group_id for next message needing a group_id
                self.__new_tag_block_group_id()
            elif nb_sentences == 1:
                # No group tag block is needed
                group_id = None
            
            for index, sentence in enumerate(encoded_sentences):
                sentence_tag_block = copy.deepcopy(tag_block) if index == 0 else None
                if group_id is not None:
                    if sentence_tag_block is None:
                        sentence_tag_block = TagBlock(None)
                    sentence_tag_block._group = TagBlockGroup(msg_id=index+1, total=nb_sentences, group_id=group_id)
                
                if sentence_tag_block is not None:
                    res.append('\\' + sentence_tag_block.to_raw().decode() + '\\' + sentence)
                else:
                    res.append(sentence)
            
            return res
        
        def convert_message_to_binary_str(self, msg):
            return msg.to_bitarray().to01()
        
        def convert_message_to_bytes(self, msg):
            return msg.to_bitarray().tobytes()
        
        def __get_message_type(self, msg_type:Union[int,str]):
            import importlib
            
            if isinstance(msg_type, str):
                msg_type = AISMessageType[msg_type].value
            
            module = importlib.import_module('pyais.messages')
            res = getattr(module, f"MessageType{msg_type}")
            return res
        
        def __get_message_type_int(self, msg_type:Union[int,str]):
            if isinstance(msg_type, int):
                return msg_type
            
            if isinstance(msg_type, str):
                msg_type = AISMessageType[msg_type]
            if not isinstance(msg_type, AISMessageType):
                raise TechnicalException(f"Unmanaged message type of class '{Typing.get_object_class_fullname(msg_type)}'")
            return msg_type.value
            
        def __convert_table_to_dict(self, table):
            if not ValueTableManager.is_table_with_header(table):
                raise TechnicalException(f"Parameter 'table' is not a table with header (obtained type: {Typing.get_object_class_fullname(table)})")
            
            if ValueTableManager.verify_table_is_name_value_table(table, raise_exception=False):
                res = ValueTableConverter.convert_name_value_table_2_dict(table)
            else:
                res = ValueTableConverter.convert_table_with_header_to_dict(table)
            return res
        
    
    
    ###########################################################################
    # Methods independent of pyais
    ###########################################################################
    
    def __new_tag_block_group_id(self):
        self.__tag_block_group_id += 1
        if self.__tag_block_group_id > 9999:
            self.__tag_block_group_id = 0
        return self.__tag_block_group_id
    
    def split_raw_to_sentences(self, ais_raw):
        if isinstance(ais_raw, str):
            split_char = '\n'
        elif isinstance(ais_raw, bytes):
            split_char = b'\n'
        else:
            raise FunctionalException(f"Raw must by of type str or bytes (obtained type: {Typing.get_object_class_fullname(ais_raw)})")
        
        res = ais_raw.split(split_char)
        
        return res
    
    def split_sentence_to_tab_block_and_message(self, ais_sentence):
        if isinstance(ais_sentence, str):
            split_char = '\\'
        elif isinstance(ais_sentence, bytes):
            split_char = b'\\'
        else:
            raise FunctionalException(f"Sentence must by of type str or bytes (obtained type: {Typing.get_object_class_fullname(ais_sentence)})")
        
        res = ais_sentence.split(split_char)
        if len(res) > 1:
            # Remove part before first '\'
            del res[0]
        else:
            # Tag block is not present, insert it as None
            res.insert(0, None)
            
        return res
    
    def convert_tag_block_to_dict(self, tag_block):
        if isinstance(tag_block, str):
            checksum_delimiter = '*'
            param_delimiter = ','
            name_delimiter = ':'
        elif isinstance(tag_block, bytes):
            checksum_delimiter = b'*'
            param_delimiter = b','
            name_delimiter = b':'
        else:
            raise FunctionalException(f"Tag Block must by of type str or bytes (obtained type: {Typing.get_object_class_fullname(tag_block)})")
        
        # Remove checksum
        try:
            chk_index = tag_block.index(checksum_delimiter)
        except:
            chk_index = None
        tb_str = tag_block[:chk_index] if chk_index else tag_block
        
        # Split parameters
        tb_list = tb_str.split(param_delimiter)
        
        # Extract parameter names and values
        param_list = [e.split(name_delimiter) for e in tb_list]
        res = {p[0]:p[1] for p in param_list}
        
        return res
    
    def split_message_to_fields(self, ais_message):
        split_char = self.__get_fields_delimiter_for_message(ais_message)
        res = ais_message.split(split_char)
        return res
    
    def __get_fields_delimiter_for_message(self, ais_message):
        if isinstance(ais_message, str):
            return ','
        elif isinstance(ais_message, bytes):
            return b','
        else:
            raise FunctionalException(f"Message must by of type str or bytes (obtained type: {Typing.get_object_class_fullname(ais_message)})")
        
    def replace_message_id_in_message(self, ais_message, replacement_id):
        if type(ais_message) != type(replacement_id):
            raise FunctionalException(f"Replacement ID must of same type than message ({Typing.get_object_class_fullname(ais_message)})")
        
        fields = self.split_message_to_fields(ais_message)
        fields[3] = replacement_id
        
        split_char = self.__get_fields_delimiter_for_message(ais_message)
        return split_char.join(fields)
        
        
    