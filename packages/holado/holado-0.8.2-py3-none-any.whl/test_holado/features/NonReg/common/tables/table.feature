@testing_solution
@table
Feature: Features related to tables

    Scenario: Extract data from table
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given INPUT_TABLE = convert json '{"test1" : 1, "test2":2.0, "test3": "test3", "test4" : null}' to name/value table with names uncollapsed
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then table INPUT_TABLE is
            | Name    | Value   |
            | 'test1' | 1       |
            | 'test2' | 2.0     |
            | 'test3' | 'test3' |
            | 'test4' | None    |
            
        Given EXTRACTED = extract column 'Name' from table INPUT_TABLE
        Then table EXTRACTED is
            | Name    |
            | 'test1' |
            | 'test2' |
            | 'test3' |
            | 'test4' |
            
        Given EXTRACTED = extract column 'Value' cells from table INPUT_TABLE
        Then table EXTRACTED is
            | 1       |
            | 2.0     |
            | 'test3' |
            | None    |
            
        Given EXTRACTED = extract column 'Value' cells from table INPUT_TABLE as row
        Then table EXTRACTED is
            | 1       | 2.0     | 'test3' | None    |

    Scenario: Empty table
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
      
        Given INPUT_TABLE = convert json '{}' to name/value table with names uncollapsed
        Then table INPUT_TABLE is
            | Name | Value |
  
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then table INPUT_TABLE is empty
       
    Scenario: Table count
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
      
        Given INPUT_TABLE = convert json '{"test1" : 1, "test2":2.0, "test3": "test3", "test4" : null}' to name/value table with names uncollapsed
        
        Then table INPUT_TABLE is
            | Name    | Value   |
            | 'test1' | 1       |
            | 'test2' | 2.0     |
            | 'test3' | 'test3' |
            | 'test4' | None    |
  
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given TABLE_COUNT = number of rows in table INPUT_TABLE
        Then TABLE_COUNT == 4
    

    Scenario: Table count empty
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given INPUT_TABLE = convert json '{}' to name/value table with names uncollapsed
  
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given TABLE_COUNT = number of rows in table INPUT_TABLE
        Then TABLE_COUNT == 0

    @table_is
    Scenario: Table verification and variables
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given TABLE_1 = convert json '{"test1" : 1, "test2":2.0, "test3": "TEST3 value", "test4" : null}' to name/value table with names uncollapsed
        Given TABLE_2 = convert json '{"TEST1" : 1, "TEST2":2.0, "TEST3": "TEST3 value", "TEST4" : null}' to table with names as columns
        
        Given TEST3 = 'test3'
        Given TEST3_VALUE = 'TEST3 value'
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then table TABLE_1 is
            | Name    | Value   |
            | 'test1' | 1       |
            | 'test2' | 2.0     |
            | ${TEST3} | ${TEST3_VALUE} |
            | 'test4' | None    |

        Then table TABLE_2 is
            | TEST1 | TEST2 | TEST3          | TEST4 |
            | 1     | 2.0   | ${TEST3_VALUE} | None  |


    @table_without_rows
    Scenario: Table without rows
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given INPUT_TABLE = convert json '{"a":"a", "b.c.b":"bcb", "b.d.a":"bda", "c.a":"ca", "c.b.a":"cba", "d.a":"da", "dab":"dab", "ea.id":"eaid", "f.a[0].g":"fa0g"}' to name/value table with names uncollapsed
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given TABLE = table INPUT_TABLE without rows verifying
            | Name                              |
            | '${MatchPattern(c\..*)}'          |
            | 'dab'                             |
            | 'd.a'                             |
            | '${MatchPattern(f\.a\[\d+\]\.g)}' |
        Then table TABLE is
            | Name    | Value  |
            | 'a'     | 'a'    |
            | 'b.c.b' | 'bcb'  |
            | 'b.d.a' | 'bda'  |
            | 'ea.id' | 'eaid' |

    @table_with_new_columns
    Scenario: Table with new columns
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given INPUT_TABLE = table with header
            | Name | Value | seconds | nanos     |
            | 'A'  | 'VA'  | 15      | 123456789 |
            | 'B'  | 'VB'  | 3600    | 123456    |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given X = 2
        Given TABLE = table INPUT_TABLE with new columns
            | Column Name | Value Expression                                                |
            | 'Col 1'     | 'Name: "${Column(Name)}"'                                       |
            | 'Col 2'     | 'Name: '${Column(Name)}' ; Value: '${Column(Value)}' ; X: ${X}' |
            | 'Time 1'    | ${Column(seconds)} + ${Column(nanos)} / 1e9                     |
            | 'Time 2'    | float(f"{${Column(seconds)}}.{${Column(nanos)}:09d}")           |

        Then table TABLE is
            | Name | Value | seconds | nanos     | Col 1       | Col 2                            | Time 1         | Time 2         |
            | 'A'  | 'VA'  | 15      | 123456789 | 'Name: "A"' | 'Name: 'A' ; Value: 'VA' ; X: 2' | 15.123456789   | 15.123456789   |
            | 'B'  | 'VB'  | 3600    | 123456    | 'Name: "B"' | 'Name: 'B' ; Value: 'VB' ; X: 2' | 3600.000123456 | 3600.000123456 |

    @table_with_new_rows
    Scenario: Table with new rows
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given TABLE = table with header
            | Name | Value |
            | 'A'  | 'VA'  |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given X = 2
        Given Y = 5
        Given TABLE = table TABLE with new rows
            | Name         | Value |
            | 'A${X}.${Y}' | ${Y}  |

        Then table TABLE is
            | Name   | Value |
            | 'A'    | 'VA'  |
            | 'A2.5' | 5     |

    @table_without_duplicated_rows
    Scenario: Table without duplicated rows
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given TABLE = table with header
            | Col 1 | Col 2 | Col 3 |
            | 'A1'  | 'A2'  | 'A3'  |
            | 'A1'  | 'B2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'B3'  |
            | 'A1'  | 'A2'  | 'B3'  |
            | 'A1'  | 'C2'  | 'A3'  |
            | 'B1'  | 'B2'  | 'B3'  |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given TABLE = table TABLE without duplicated rows
            | Col 1 | Col 3 |

        Then table TABLE is
            | Col 1 | Col 2 | Col 3 |
            | 'A1'  | 'A2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'B3'  |
            | 'A1'  | 'A2'  | 'B3'  |

    @contains
    @doesnt_contain
    Scenario: Table contains or not a row
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given TABLE = table with header
            | Col 1 | Col 2 | Col 3 |
            | 'A1'  | 'A2'  | 'A3'  |
            | 'A1'  | 'B2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'A3'  |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then table TABLE contains
            | Col 1 | Col 2 | Col 3 |
            | 'A1'  | 'A2'  | 'A3'  |
            | 'B1'  | 'A2'  | 'A3'  |
        
        Given next step shall fail on exception matching 'Table obtained doesn't contain row expected of index 0'
        Then table TABLE contains
            | Col 1  | Col 2 | Col 3 |
            | 'PIPO' | 'A2'  | 'A3'  |
        
        Then table TABLE doesn't contain
            | Col 1  | Col 2 | Col 3 |
            | 'PIPO' | 'A2'  | 'A3'  |
        
        Given next step shall fail on exception matching 'Table obtained contains row expected of index 1'
        Then table TABLE doesn't contain
            | Col 1  | Col 2 | Col 3 |
            | 'PIPO' | 'A2'  | 'A3'  |
            | 'A1'   | 'A2'  | 'A3'  |

