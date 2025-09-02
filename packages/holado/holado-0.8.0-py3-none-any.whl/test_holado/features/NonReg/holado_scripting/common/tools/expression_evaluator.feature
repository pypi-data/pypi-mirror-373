@testing_solution
@expression_evaluator
Feature: Features related to expression_evaluator

    Scenario: Expressions in tables

        Given VAL_5 = 5
        Given VAL_9 = 9
        Given VAL_10 = 10
        Given VAL_11 = 11
        Given VAL_20 = 20
        
        #Given TABLE = table
            #| Name      | Value   |
            #| 'name'    | VAL     |
            #| 'name +'  | VAL + 1 |
            #| 'name -'  | VAL - 1 |
        Given TABLE = convert json '{"name": 10, "name +": 11, "name -": 9}' to name/value table with names uncollapsed

        Then table TABLE is
            | Name      | Value |
            | 'name'    | 10    |
            | 'name +'  | 11    |
            | 'name -'  | 9     |

        Then table TABLE is
            | Name      | Value       |
            | 'name'    | VAL_10      |
            | 'name +'  | ${VAL_10} + 1  |
            | 'name -'  | ${VAL_10} - 1  |

        Then table TABLE is
            | Name      | Value       |
            | 'name'    | ${VAL_9} + 1   |
            | 'name +'  | ${VAL_9} + 2   |
            | 'name -'  | ${VAL_11} - 2  |

        Then table TABLE is
            | Name      | Value         |
            | 'name'    | ${VAL_20} / 2    |
            | 'name +'  | ${VAL_5} * 2 + 1 |
            | 'name -'  | ${VAL_5} * 2 - 1 |
            
            
    @expression_assignment
    Scenario: Expressions in assignment

        Given VAL = ${int(32)}
        Then VAL == 32

        Given VAL = ${32}
        Then VAL == 32

        Given VAL = ${128} >> 2
        Then VAL == 32
        
        Given X = 128
        Given VAL = ${X} >> 2 if ${X} >= 64 else ${X} >> 1
        Then VAL == 32
        
        Given X = 32
        Given VAL = ${X} >> 2 if ${X} >= 64 else ${X} >> 1
        Then VAL == 16
        
        Given X = 32
        Given VAL = ${X} + 1
        Then VAL == 33
        
        Given LIST = [1, 2, 3]
        Given INDEX = 1
        Given VAL = ${LIST[${INDEX}]}
        Then VAL == 2
        
        Given LIST_STR = '[1, 2, 3]'
        Given LIST = ${list(${LIST_STR})}
        Given INDEX = 1
        Given VAL = ${LIST[${INDEX}]}
        Then VAL == 2
        
    @timedelta
    Scenario: timedelta
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given DT_1 = datetime now
        Given DT_2 = DT_1 + 3 seconds
        Given EXPECTED = ${datetime.timedelta(seconds=3)}
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given DELTA = ${DT_2} - ${DT_1}
        Then DELTA == EXPECTED

    Scenario: Expressions in for and if
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given VAL_5 = 5
        Given VAL_9 = 9
        Given VAL_10 = 10
        Given VAL_11 = 11
        Given VAL_20 = 20
        
        Given TABLE = convert json '{"name": 10, "name +": 11, "name -": 9}' to name/value table with names uncollapsed
        
        Given end preconditions
        ### PRECONDITIONS - END

        Given for N in range(0,2):
            Given VAL_5_1 = ${VAL_5} - 1
            Given VAL_5_N = ${VAL_5} - ${N}
            
            Then VAL_5_1 == 4
            Then table TABLE is
                | Name      | Value       |
                | 'name'    | VAL_10      |
                | 'name +'  | ${VAL_10} + 1  |
                | 'name -'  | ${VAL_10} - 1  |
                
            Given if ${N} == 0:
                Then VAL_5_N == 5
                
                Then table TABLE is
                    | Name      | Value       |
                    | 'name'    | VAL_10      |
                    | 'name +'  | ${VAL_10} + 1  |
                    | 'name -'  | ${VAL_10} - 1  |
            Given else:
                Then VAL_5_N == 4
                
                Then table TABLE is
                    | Name      | Value       |
                    | 'name'    | VAL_10      |
                    | 'name +'  | ${VAL_10} + ${N} |
                    | 'name -'  | ${VAL_10} - ${N} |
            Given end if
        Given end for
        
    
    @expression_if
    Scenario: Expressions in if
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given VAL_5 = 5
        Given VAL_9 = 9
        Given VAL_10 = 10
        Given VAL_11 = 11
        Given VAL_20 = 20
        
        Given TABLE = convert json '{"name": 10, "name +": 11, "name -": 9}' to name/value table with names uncollapsed
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given INDEX = 2
        Given N_2 = 5
        Given if ${N_${INDEX}} == 3:
            Given RESULT = 13
        Given else if ${N_${INDEX}} == 5:
            Given RESULT = 15
        Given else:
            Given RESULT = 10
        Given end if
        
        Then RESULT == 15
        
    @string_evaluation
    Scenario: String evaluation
        Given INDEX = 3
        Given TEXT = 'toto.tata[${INDEX}]'
        Then TEXT == 'toto.tata[3]'
        
        Given TABLE = table with header
            | Name                  | Value |
            | 'toto.tata[${INDEX}]' | 5     |
        Then table TABLE is
            | Name           | Value |
            | 'toto.tata[3]' | 5     |
            
        Given TOTO = 'toto'
        Given TEXT = 'TOTO.tata[${INDEX}]'
        Then TEXT == 'TOTO.tata[3]'
        
