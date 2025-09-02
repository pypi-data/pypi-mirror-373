# -*- coding: utf-8 -*-

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
import csv
from holado_core.common.tables.table_with_header import TableWithHeader
from holado_core.common.tables.table_row import TableRow
from holado.common.context.session_context import SessionContext
from holado_core.common.tables.table import Table
from holado_core.common.tables.table_manager import TableManager
from holado_data.data.generator.base import BaseGenerator

logger = logging.getLogger(__name__)




class CsvManager():
    # Default settings for CSV files: dialect Excel but with ';' delimiter
    default_dialect = "excel"
    default_delimiter = ";"
    default_quotechar = None
    default_quoting = None

    @classmethod
    def __get_path_manager(cls):
        return SessionContext.instance().path_manager
    
    @classmethod
    def _get_csv_kwargs(cls, dialect, delimiter, quotechar, quoting):
        csv_kwargs = {}
        
        if dialect is not None:
            csv_kwargs['dialect'] = dialect
        elif cls.default_dialect is not None:
            csv_kwargs['dialect'] = cls.default_dialect
            
        if delimiter is not None:
            csv_kwargs['delimiter'] = delimiter
        elif cls.default_delimiter is not None:
            csv_kwargs['delimiter'] = cls.default_delimiter
            
        if quotechar is not None:
            csv_kwargs['quotechar'] = quotechar
        elif cls.default_quotechar is not None:
            csv_kwargs['quotechar'] = cls.default_quotechar
            
        if quoting is not None:
            csv_kwargs['quoting'] = quoting
        elif cls.default_quoting is not None:
            csv_kwargs['quoting'] = cls.default_quoting
            
        return csv_kwargs
        
    @classmethod
    def table_with_content_of_CSV_file(cls, path, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None, with_header=True):
        csv_kwargs = cls._get_csv_kwargs(dialect, delimiter, quotechar, quoting)
        
        with open(path, 'r', encoding=encoding) as fin:
            if with_header:
                dr = csv.DictReader(fin, **csv_kwargs)
                
                res = TableWithHeader()
                res.header = TableRow(cells_content=dr.fieldnames)
                
                for row in dr:
                    nrow=dict(row)
                    res.add_row(contents_by_colname=nrow)
            else:
                reader = csv.reader(fin, **csv_kwargs)
                
                res = Table()
                for row in reader:
                    res.add_row(cells_content=row)
        
        return res
        
    @classmethod
    def dict_list_with_content_of_CSV_file(cls, path, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None):
        dg = cls.dict_generator_with_content_of_CSV_file(path, encoding, dialect, delimiter, quotechar, quoting)
        return [d for d in dg]
    
    @classmethod
    def dict_generator_with_content_of_CSV_file(cls, path, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None):
        csv_kwargs = cls._get_csv_kwargs(dialect, delimiter, quotechar, quoting)
        
        class DictCSVGenerator(BaseGenerator):
            def __init__(self, path, encoding, csv_kwargs):
                super().__init__(name="dict CSV generator")
                
                self.__path = path
                self.__encoding = encoding
                self.__csv_kwargs = csv_kwargs
                
                self.__fin = None
                self.__dict_reader = None
            
            def __open_file_if_needed(self):
                if self.__fin is None:
                    self.__fin = open(self.__path, 'r', encoding=self.__encoding)
                    self.__dict_reader = csv.DictReader(self.__fin, **self.__csv_kwargs)
            
            def __close_file(self):
                self.__dict_reader = None
                self.__fin.close()
                self.__fin = None
                
            def __next__(self):
                self.__open_file_if_needed()
                try:
                    return dict(next(self.__dict_reader))
                except StopIteration as exc:
                    self.__close_file()
                    raise exc
        
        return DictCSVGenerator(path, encoding, csv_kwargs)
    
    @classmethod
    def tuple_list_with_content_of_CSV_file(cls, path, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None):
        tg = cls.tuple_generator_with_content_of_CSV_file(path, encoding, dialect, delimiter, quotechar, quoting)
        return [t for t in tg]
    
    @classmethod
    def tuple_generator_with_content_of_CSV_file(cls, path, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None):
        csv_kwargs = cls._get_csv_kwargs(dialect, delimiter, quotechar, quoting)
        
        class TupleCSVGenerator(BaseGenerator):
            def __init__(self, path, encoding, csv_kwargs):
                super().__init__(name="tuple CSV generator")
                
                self.__path = path
                self.__encoding = encoding
                self.__csv_kwargs = csv_kwargs
                
                self.__fin = None
                self.__reader = None
            
            def __open_file_if_needed(self):
                if self.__fin is None:
                    self.__fin = open(self.__path, 'r', encoding=self.__encoding)
                    self.__reader = csv.reader(self.__fin, **self.__csv_kwargs)
            
            def __close_file(self):
                self.__reader = None
                self.__fin.close()
                self.__fin = None
                
            def __next__(self):
                self.__open_file_if_needed()
                try:
                    return tuple(next(self.__reader))
                except StopIteration as exc:
                    self.__close_file()
                    raise exc
        
        return TupleCSVGenerator(path, encoding, csv_kwargs)
    
    @classmethod
    def create_csv_file(cls, path, table, encoding=None, dialect=None, delimiter=None, quotechar=None, quoting=None):
        csv_kwargs = cls._get_csv_kwargs(dialect, delimiter, quotechar, quoting)
        
        cls.__get_path_manager().makedirs(path)
        
        with open(path, 'w', encoding=encoding) as fout:
            if TableManager.is_table_with_header(table):
                fieldnames = table.header.cells_content
                dw = csv.DictWriter(fout, fieldnames=fieldnames, **csv_kwargs)
                
                dw.writeheader()
                for row in table.rows:
                    rowdict = {fieldnames[i]:row[i].string_content for i in range(len(fieldnames))}
                    dw.writerow(rowdict)
            else:
                writer = csv.writer(fout, **csv_kwargs)
                for row in table.rows:
                    cells_content = [c.string_content for c in row]
                    writer.writerow(cells_content)
    
    @classmethod
    def merge_csv(cls, input_paths, output_path=None, sort_column=None, with_header=True):
        input_tables = [cls.table_with_content_of_CSV_file(ip, with_header=with_header) for ip in input_paths]
        
        # Merge tables
        output_table = input_tables[0]
        for i in range(1, len(input_tables)):
            output_table.extend(input_tables[i])
        
        # Sort rows
        if sort_column is not None:
            output_table.sort(names=[sort_column])
        
        if output_path is not None:
            cls.create_csv_file(output_path, output_table)
        else:
            return output_table
    
