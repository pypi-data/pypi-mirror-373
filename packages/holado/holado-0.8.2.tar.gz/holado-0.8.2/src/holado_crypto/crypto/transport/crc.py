
import logging
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class Crc(object):
    
    @staticmethod
    def crc(msg_bytes, offset, nb_bits, crc_size, polynomial, init_val, xor_val, reverse=False):
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Computing CRC for:\n  {msg_bytes=}\n  {offset=}\n  {nb_bits=}\n  {crc_size=}\n  {polynomial=}\n  {init_val=}\n  {xor_val=}")
        res = init_val
        
        # For each data bit in the data, process bits from left to right (or from right to left if reverse=True)
        if reverse:
            bits_range = range(offset+nb_bits-1, offset-1, -1)
        else:
            bits_range = range(offset, offset+nb_bits)
        for i in bits_range:
            bit = (msg_bytes[i // 8] >> (7 - (i % 8))) & 0x1
            out = (res >> (crc_size - 1)) & 0x1
            res = (res << 1) & (0xFFFFFFFF >> (32 - crc_size))
            # Apply polynomial if the bit about to be shifted out of the crc is different than the processed bit
            if bit ^ out == 1:
                res ^= polynomial
            if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
                logger.trace(f"Computing CRC: {i=}, {bit=} => {res}")
        
        res ^= xor_val
        
        # Be careful, for a crc-32, we can't make <<32, this should result to <<0
        res &= 0xFFFFFFFF >> (32 - crc_size)
        
        if Tools.do_log(logger, logging.DEBUG):
            logger.debug(f"CRC for:\n  {msg_bytes=}\n  {offset=}\n  {nb_bits=}\n  {crc_size=}\n  {polynomial=}\n  {init_val=}\n  {xor_val=}\n => {res}")
        return res
        
        