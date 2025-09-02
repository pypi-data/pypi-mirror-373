
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



from holado_core.common.tables.converters.table_converter import TableConverter
from holado_ui_selenium.ui.gui.selenium.handlers.selenium_holder import SeleniumHolder
from holado_ui_selenium.ui.gui.selenium.inspectors.selenium_inspector import SeleniumInspector
import logging
from holado_ui_selenium.ui.gui.selenium.tables.selenium_table_with_header import SeleniumTableWithHeader
from holado_core.common.exceptions.technical_exception import TechnicalException
from holado_ui_selenium.ui.gui.selenium.tables.selenium_table import SeleniumTable
from holado_ui_selenium.ui.gui.selenium.tables.selenium_table_row import SeleniumTableRow
from holado_ui_selenium.ui.gui.selenium.tables.selenium_table_cell import SeleniumTableCell
from holado_core.common.tables.enums import MergeTypes
from holado_core.common.tools.converters.converter import Converter
from holado_core.common.tools.tools import Tools

logger = logging.getLogger(__name__)


class SeleniumTableConverter(TableConverter):
    
    
    @classmethod
    def convert_element_to_selenium_table_with_header(cls, inspector:SeleniumInspector, table_element:SeleniumHolder):
        """
        Convert a SeleniumHolder to a table with header.
        Note: invisible cells will also be added to table
        @param inspector HTML inspector
        @param table_element SeleniumHolder corresponding to the table to convert
        @return Element as a Table
        """
        find_parameters = table_element.find_info.find_parameters.with_visibility(None)   # Visibility is None to extract also hidden rows and cells
        
        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace("Converting SeleniumHolder to SeleniumTableWithHeader...")

        res = SeleniumTableWithHeader(inspector.driver, table_element.element)
        res.parent = inspector
        
        # Get header and rows
        finder = inspector.get_finder_table_row()
        rows = finder.find_all_in(table_element, find_parameters) 
        
        # Set header
        if len(rows) > 0:
            row = rows[0]
            row.description = "header"
            
            finder = inspector.get_finder_table_cell()
            
            row_cells = finder.find_all_in(row, find_parameters)
            header = cls.convert_element_to_selenium_table_row(inspector, row, row_cells)
            res.header = header
        else:
            raise TechnicalException("Unable to find table header")
        
        # Set body
        cls.__fill_body(inspector, res, rows, 1, table_element)

        if Tools.do_log(logger, logging.TRACE):  # @UndefinedVariable
            logger.trace(f"Converted SeleniumHolder to SeleniumTableWithHeader of size (nb rows:{res.nb_rows} ; nb cols:{res.nb_columns})")
        
        return res
    
    @classmethod
    def convert_element_to_selenium_table(cls, inspector:SeleniumInspector, table_element:SeleniumHolder):
        """
        Convert a SeleniumHolder to a table of SeleniumHolder.
        Note: invisible rows and cells will also be added to table
        @param inspector Inspector instance
        @param table_element Table web element
        @return Table of web elements
        """
        res = SeleniumTable(inspector.driver, table_element)
        res.parent = inspector

        sub_find_parameters = table_element.find_info.find_parameters.with_visibility(None)   # Visibility is None to extract also hidden rows
        
        # Get rows
        finder = inspector.get_finder_table_row()
        rows = finder.find_all_in(table_element, sub_find_parameters) 

        # Fill body
        cls.__fill_body(inspector, res, rows, 0, table_element)

        return res
    

    @classmethod
    def __fill_body(cls, inspector, table, rows, start_index, table_element):
        # Init
        previous_row = None
        top_merge_counters = []
        finder = inspector.get_finder_table_cell()

        # Iterate through rows and add cells to matrix
        for row_element in rows[start_index:]:
#            if (inspector.internal_api.is_displayed(row_element)):
            row_cells = finder.find_all_in(row_element, row_element.find_info.find_parameters)

            row = cls.convert_element_to_selenium_table_row(inspector, row_element, row_cells, previous_row, top_merge_counters)

            table.add_row(row)
            previous_row = row
    
    @classmethod
    def convert_element_to_selenium_table_row(cls, inspector:SeleniumInspector, row_element:SeleniumHolder, row_elements):
        """
        @param inspector Inspector instance
        @param row_element Row web element
        @param row_elements List of web elements
        @return Web element table row
        """
        res = SeleniumTableRow(inspector.driver, row_element)
        ind_cell = 0
        ind_cell_in_row = 0
        colspan_counter = 0
        
        while ind_cell_in_row < len(row_elements) or colspan_counter > 0:
            if colspan_counter > 0:
                # Add new cell merged with left cell
                new_cell = SeleniumTableCell(inspector.driver, MergeTypes.LeftMerged, res[ind_cell - 1])
                # Update counter
                colspan_counter -= 1
            else:
                cell = row_elements[ind_cell_in_row]
                
                # Manage merge cells
                cell_element = cell.element
                tag = cell_element.tag_name
                if tag.lower() == "td":
                    colspan = cell_element.get_attribute("colspan")
                    if colspan is not None:
                        span_int = Converter.to_integer(colspan)
                        if span_int > 1:
                            colspan_counter = span_int - 1
                
                new_cell = SeleniumTableCell(inspector.driver, cell)
                ind_cell_in_row += 1
            
            # Add new cell
            res.add(new_cell)
            ind_cell += 1
        
        return res
    
    @classmethod
    def convert_element_to_selenium_table_row(cls, inspector:SeleniumInspector, row_element:SeleniumHolder, row_elements, previous_row:SeleniumTableRow, top_merge_counters):
        """
        @param inspector Inspector instance
        @param row_element Row web element
        @param row_elements List of web elements
        @param previous_row Previous row converted
        @param top_merge_counters Counters of number time each row cell must be merged with top cell (In/Out)
        @return Web element table row
        """
        res = SeleniumTableRow(inspector.driver, row_element)
        colspan_counter = 0
        stop = False
        
        # Add cells according top_merge_counters
        ind_cell_in_row = 0
        ind_cell = 0
        while not stop:
            # Manage merge from previous rows
            if ind_cell >= len(top_merge_counters):
                top_merge_counters.extend([0] * (ind_cell - len(top_merge_counters) + 1))
            cell_counter = top_merge_counters[ind_cell]
            
            if cell_counter > 0:
                # Add new cell merged with top cell
                new_cell = SeleniumTableCell(inspector.driver, MergeTypes.TopMerged, previous_row[ind_cell])
                res.add(new_cell)
                # Update counter for next row
                cell_counter -= 1
                top_merge_counters.insert(ind_cell, cell_counter)
                ind_cell += 1
            elif colspan_counter > 0:
                # Add new cell merged with left cell
                new_cell = SeleniumTableCell(inspector.driver, MergeTypes.LeftMerged, res[ind_cell - 1])
                res.add(new_cell)
                # Update counter
                colspan_counter -= 1
                ind_cell += 1
            elif ind_cell_in_row < len(row_elements):
                cell = row_elements[ind_cell_in_row]
                cell_element = cell.element

                # Manage merge cells
                tag = cell_element.tag_name
                if (tag.lower() == "td"):
                    rowspan = cell_element.get_attribute("rowspan")
                    colspan = cell_element.get_attribute("colspan")
                    if rowspan is not None:
                        span_int = Converter.to_integer(rowspan)
                        if span_int > 1:
                            top_merge_counters.insert(ind_cell, span_int - 1)
                    
                    if colspan is not None:
                        span_int = Converter.to_integer(colspan)
                        if span_int > 1:
                            colspan_counter = span_int - 1
                
                # Add new cell
                res.add(SeleniumTableCell(inspector.driver, cell))
                ind_cell += 1
                ind_cell_in_row  += 1
            else:
                stop = True
        
        return res
    
    # @classmethod
    # def convert_selenium_table_to_value_table(cls, SeleniumTableWithHeader table, SeleniumInspector seleniumInspector, TableConvertParameters parameters):
    #     """
    #     Convert SeleniumHolder Tables to Scenario Tables
    #     @param table table to convert
    #     @param seleniumInspector Inspector instance
    #     @param parameters Convert parameters
    #     @return Scenario table with header
    #     """
    #     InfoTableWithHeader res = InfoTableWithHeader(None)
    #     InfoTableRow resRow
    #     SeleniumTableRow row
    #
    #     TableConvertContext context = TableConvertContext.getDefault()
    #             .withColumnIndexesByName(table.columnIndexesByHeaderStringContent())
    #
    #     # Set header
    #     TableConvertParameters headerParameters = (parameters is None ? None : parameters.withoutPatternConvertByColumn())
    #     StringTableRow header = TableConverter.convertTableRowToStringTableRow(table.getHeader(), headerParameters)
    #     header.updateAfterCreate()
    #     res.header = header
    #
    #     # Set rows
    #     for (int i = 0  i < table.nbRows()  i += 1):
    #         row = table.getRow(i)
    #         resRow = convertSeleniumTableRowToScenarioTableRow(row, seleniumInspector, context, parameters)
    #         res.addRow(resRow)
    #         resRow.updateAfterCreate(res, i)
    #
    #
    #     return res
    #
    #
    #
    # @classmethod
    # def convertSeleniumTableRowToScenarioTableRow(cls, SeleniumTableRow row, SeleniumInspector seleniumInspector, TableConvertContext context, TableConvertParameters parameters):
    #     """
    #     Convert a table row to Scenario row
    #     @param row Row to convert
    #     @param seleniumInspector Inspector instance
    #     @param context Convert context
    #     @param parameters Convert parameters
    #     @return Scenario row
    #     """
    #     InfoTableRow res = InfoTableRow(None)
    #     SeleniumHolder obtainedElement 
    #
    #     for (SeleniumTableCell cell : row):
    #         # Manage merge type
    #         if (cell.getMergeType() is not None):
    #             res.add(InfoTableCell(cell.getMergeType(), None))
    #             continue
    #
    #
    #         # Get cell content
    #         obtainedElement = (SeleniumHolder) cell.getContent()
    #         if (obtainedElement is None)
    #             raise FunctionalException("Element content is not defined.")
    #
    #         # Else string content
    #         res.add(InfoTableCell(cell.getStringContent()))
    #
    #
    #     return res
