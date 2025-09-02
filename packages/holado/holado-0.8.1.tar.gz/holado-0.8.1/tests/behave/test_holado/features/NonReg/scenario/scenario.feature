@testing_solution
@scenario
Feature: Features related to scenario

    @preconditions
    Scenario: preconditions

        Given next step shall fail on exception matching ''ScenarioContext' object has no attribute 'is_in_preconditions''
        Then SCENARIO_CONTEXT.is_in_preconditions == False
        
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Then SCENARIO_CONTEXT.is_in_preconditions == True
        
        Given end preconditions
        ### PRECONDITIONS - END

        Then SCENARIO_CONTEXT.is_in_preconditions == False
        
        
    @postconditions
    Scenario: postconditions
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Verify no post processes are still persisted
        Given NB = number of persisted post processes to perform for scenario context
        Then NB == 0
        
        # Manage verification that postconditions are called
        Given VAR = 'before postcondition'
        Given at end of scenario, call steps
            """
            Given VAR = 'after postcondition'
            """
        
        # Manage verification that a same postcondition is called only once
        Given COUNTER = 0
        Given at end of scenario, call steps
            """
            Given COUNTER = ${${COUNTER} + 1}
            """
        Given at end of scenario, call steps
            """
            Given COUNTER = ${${COUNTER} + 1}
            """
        Given at end of scenario, call steps
            """
            Given COUNTER = ${${COUNTER} + 1}
            """
        
        # Manage verification that a failed postcondition become expired after 10 tries
        Given at end of scenario, call steps
            """
            Then 0 == 1
            """
        
        Given end preconditions
        ### PRECONDITIONS - END

        Then VAR == 'before postcondition'
        Then COUNTER == 0
        
        Given NB = number of persisted post processes to perform for scenario context
        Then NB == 3
        
        When execute post processes of scenario context
        
        Then VAR == 'after postcondition'
        Then COUNTER == 1

        Given NB = number of persisted post processes to perform for scenario context
        Then NB == 1
        
        # Verify post processes in failure are expiring after 10 tries
        Given for _ in range(8):
            When execute persisted post processes of scenario context
        Given end for
        Given NB = number of persisted post processes to perform for scenario context
        Then NB == 1

        When execute persisted post processes of scenario context
        Given NB = number of persisted post processes to perform for scenario context
        Then NB == 0

    @table_possible_values
    Scenario: Scenario table possible values
    
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given INPUT_TEXT = multiline text
            """
            {"test01": 1, "test02":2.0, "test03": "test3", "test04": null, "test05": "dummy", 
            "test06": "Variable value", "test07": "Variable value", "test08": "ExtractIn function", 
            "test09": "has txt inside", "test10": 3}
            """
        Given INPUT_TABLE = convert json INPUT_TEXT to name/value table with names uncollapsed
        Given VAR = 'Variable value'
        Given TXT = 'txt'
        Given VAL_2 = 2
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then table INPUT_TABLE is
            | Name     | Value                                   |
            | 'test01' | 1                                       |
            | 'test02' | 2.0                                     |
            | 'test03' | 'test3'                                 |
            | 'test04' | None                                    |
            | 'test05' | N/A                                     |
            | 'test06' | VAR                                     |
            | 'test07' | '${VAR}'                                |
            | 'test08' | '${ExtractIn(VAR2)}'                    |
            | 'test09' | '${MatchPattern(has ${TXT} inside)}'    |
            | 'test10' | ${VAL_2} + 1                            |

        Then VAR2 == 'ExtractIn function'
        
    Scenario: Use a table variable as a scenario table
    
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given INPUT_TABLE = convert json '{"test1": 1, "test2":2.0, "test3": "test3", "test4": null, "test5": "dummy", "test6": "Variable value", "test7": "Variable value", "test8": "ExtractIn function"}' to name/value table with names uncollapsed
        Given VAR = 'Variable value'
        
        Given end preconditions
        ### PRECONDITIONS - END
      
        Given TABLE = table with header
            | INPUT_TABLE |
            
        Then table TABLE is
            | Name    | Value                 |
            | 'test1' | 1                     |
            | 'test2' | 2.0                   |
            | 'test3' | 'test3'               |
            | 'test4' | None                  |
            | 'test5' | N/A                   |
            | 'test6' | VAR                   |
            | 'test7' | '${VAR}'              |
            | 'test8' | '${ExtractIn(VAR2)}'  |
            
        Then VAR2 == 'ExtractIn function'
        
        
    @ScenarioTools.evaluate_scenario_parameter
    Scenario: ScenarioTools.evaluate_scenario_parameter
        Given VAR1 = 10
        Given VAR2 = 11
        Given VAR2S = '11'
        Given VAR2_PLUS = '10 + 1'
        Given VAR3 = 9
        
        Then VAR2 == ${VAR1} + 1
        Then VAR2_PLUS == '${VAR1} + 1'
        Then VAR2 == ${${VAR1} + 1}
        Then VAR2S == '${${VAR1} + 1}'
        Then VAR3 == ${VAR1} - 1
        
        Given URL = 'http://auto.test'
        Given PORT = '1234'
        Given ENDPOINT = '${URL}:${PORT}'
        Then ENDPOINT == 'http://auto.test:1234'
        
        
        # Python expression evaluation
        Given VAR4 = ${"{:>08s}".format("A0")}
        Then VAR4 == '000000A0'
        Given VAR4 = ${"{{:>08s}}".format("A0")}
        Then VAR4 == '000000A0'
        Given VAR4 = ${'{{:>08s}}'.format('A0')}
        Then VAR4 == '000000A0'
        
        Given VAR5 = ${[{'a': {'b': 'c'}}]}
        Then VAR5 is list
        Then VAR5[0]['a']['b'] == 'c'
        
        
        