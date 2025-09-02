@testing_solution
@ValueTableManager
Feature: Features related to ValueTableManager

    Scenario: Convert Name/Value Scenario table to json
    
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given VAR = 'Variable value'
        Given INPUT_TABLE = table with header
            | Name        | Value                 |
            | 'test1'     | 1                     |
            | 'test2'     | 2.0                   |
            | 'test3'     | 'test3'               |
            | 'test4'     | None                  |
            | 'test5[0]'  | 'test5'               |
            | 'test6'     | VAR                   |
        
        Given end preconditions
        ### PRECONDITIONS - END
      
        When JSON = convert name/value table INPUT_TABLE to json
        
        Given JSON_STR = convert object value JSON to string
        Given STR = '{'test1': 1, 'test2': 2.0, 'test3': 'test3', 'test4': None, 'test5': ['test5'], 'test6': 'Variable value'}' 
        Then JSON_STR == STR 
            
  
