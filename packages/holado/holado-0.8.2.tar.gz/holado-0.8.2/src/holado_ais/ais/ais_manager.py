
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
from holado_core.common.resource.persisted_data_manager import PersistedDataManager
import os
from holado_python.standard_library.csv import CsvManager
from holado_core.common.exceptions.technical_exception import TechnicalException

logger = logging.getLogger(__name__)


class AISManager(object):
    
    def __init__(self):
        self.__persisted_data_manager = PersistedDataManager(data_name="AIS data",
                                                             table_name=self.__get_persisted_data_table_name(),
                                                             table_sql_create=self.__get_persisted_data_table_sql_create(),
                                                             db_name="ais")
        self.__possible_mids = []
        
    def initialize(self, resource_manager):
        self.__persisted_data_manager.initialize(resource_manager)
        
        self.__possible_mids = self.__load_mids()
    
    def __load_mids(self):
        """Return possible MID (Maritime Identification Digits) values.
        Resource file MaritimeIdentificationDigits.csv is an export from https://www.itu.int/en/ITU-R/terrestrial/fmd/Pages/mid.aspx
        """
        here = os.path.abspath(os.path.dirname(__file__))
        path = os.path.normpath(os.path.join(here, "MaritimeIdentificationDigits.csv"))
        
        table = CsvManager.table_with_content_of_CSV_file(path, delimiter=',')
        return table.get_column(name='Digit').cells_content
    
    def new_unique_mmsi_number(self):
        # Ensure persistent DB exists
        self.__persisted_data_manager.ensure_persistent_db_exists()
        
        last_mmsi = self.__get_persisted_data_value("unique_mmsi")
        res = self.next_valid_mmsi(last_mmsi)
        if res is None:
            # This case appears when last unique MMSI was last valid MMSI. Get first possible MMSI.
            res = self.next_valid_mmsi(None)
            
        self.__update_or_add_persisted_data("unique_mmsi", res)
        
        return res
    
    def format_mmsi_number_as_string(self, mmsi):
        if not isinstance(mmsi, int):
            raise TechnicalException(f"MMSI is not an integer (obtained type: {type(mmsi)})")
        return f"{mmsi:09d}"

    def first_valid_mmsi(self):
        return int(self.__possible_mids[0]) * 10000
    
    def next_valid_mmsi(self, previous_mmsi=None):
        """Return next valid MMSI.
        
        Notes:
            If previous_mmsi is None, return first valid MMSI number.
            If previous_mmsi is last valid MMSI, return None.
        """
        if previous_mmsi is None:
            # Return smallest possible MMSI
            return self.first_valid_mmsi()
        else:
            for mmsi in range(previous_mmsi+1, int(1e9)):
                if self.is_valid_mmsi(mmsi):
                    return mmsi
            return None
    
    def is_valid_mmsi(self, mmsi):
        """Return if MMSI is valid
        The MMSI uniquely identifies a ship (or a group of ships), or a coast radio station.
        MMSI stands for Maritime Mobile Service Identity.
        Possible values:
        * 97<nnnnnnn>: valid
        * [00|98|99]<MID><nnnn> : valid if MID is valid
        * [0|8]<MID><nnnnn> : valid if MID is valid
        * <MID><nnnnnn> : valid if MID is valid
        * <any other value (incl. > 999999999) : invalid
        @param mmsi: MMSI to validate (type: int, str)
        """
        if mmsi is None:
            return False
        
        if isinstance(mmsi, int):
            mmsi = self.format_mmsi_number_as_string(mmsi)
        if mmsi[0:2] in ['97', '99']:
            return True
        else:
            if mmsi[0:2] in ['00', '98', '99']:
                mid = mmsi[2:5]
            elif mmsi[0:1] in ['0', '8']:
                mid = mmsi[1:4]
            else:
                mid = mmsi[0:3]
            return self.is_valid_mid(mid)
    
    def is_valid_mid(self, mid):
        return mid in self.__possible_mids

    def __next_mid(self, previous_mid):
        """Return next MID in possible MID values"""
        if previous_mid is None:
            return self.__possible_mids[0]
        elif previous_mid in self.__possible_mids:
            index = self.__possible_mids.index(previous_mid)
            if index + 1 < len(self.__possible_mids):
                return self.__possible_mids[index+1]
            else:
                return None
        else:
            raise TechnicalException(f"MID {previous_mid} is not valid")

    # Manage persistent data

    def __get_persisted_data_table_name(self):
        return "ais_data"

    def __get_persisted_data_table_sql_create(self):
        return """CREATE TABLE ais_data (
                key text NOT NULL,
                value text
            )"""

    def __update_or_add_persisted_data(self, key, value):
        self.__persisted_data_manager.update_or_add_persisted_data(persisted_filter_data={'key':key}, data={'value':value})

    def __get_persisted_data_value(self, key):
        persisted_data = self.__persisted_data_manager.get_persisted_data(filter_data={'key':key})
        if persisted_data is not None:
            return int(persisted_data['value'])
        else:
            return None
        


