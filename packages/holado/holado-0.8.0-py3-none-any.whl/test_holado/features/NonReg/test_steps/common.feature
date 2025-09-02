@testing_solution
@common
Feature: Steps in common_steps.py

    Scenario: wait time

        When wait 1 seconds
        
        When wait 0.55 seconds
        

    @wait_until
    Scenario: wait until

        When wait until '1' == '1'
        When wait until '1' == '1' (accepted time: 1 s)
        When wait until '1' == '1' (accepted time: 1 s ; timeout: 2 s)
        When wait until '1' == '1' (accepted time: 1 s ; polling: 0.1 s)
        When wait until '1' == '1' (accepted time: 1 s ; timeout: 2 s ; polling: 0.1 s)
        When wait until wait 0.5 seconds (timeout: 0.7 s)
        
        Given next step shall fail on exception matching 'holado_core.common.exceptions.timeout_exception.TimeoutException\(Timeout \(2 s\) when waiting '1' != '1'.*-> Timed out after 2.\d+ s'
        When wait until '1' != '1' (accepted time: 1 s ; timeout: 2 s)
        
        Given next step shall fail on exception matching 'holado_core.common.exceptions.functional_exception.FunctionalException\(Too long \(1.1\d+ s\) to wait wait 1.1 seconds \(accepted time: 1 s\)'
        When wait until wait 1.1 seconds (accepted time: 1 s ; timeout: 2 s)
        
        Given next step shall fail on exception matching 'A step doesn't exist in'
        When wait until missing step (accepted time: 1 s ; timeout: 2 s)

    @wait_until_after_steps
    Scenario: wait until after steps
        # Part with same verifications than previous scenario without " after steps"
        When wait until '1' == '1' after steps
            """
            Given TOTO = 'TITI'
            """
        When wait until '1' == '1' after steps (accepted time: 1 s)
            """
            Given TOTO = 'TITI'
            """
        When wait until '1' == '1' after steps (accepted time: 1 s ; timeout: 2 s)
            """
            Given TOTO = 'TITI'
            """
        When wait until '1' == '1' after steps (accepted time: 1 s ; polling: 0.1 s)
            """
            Given TOTO = 'TITI'
            """
        When wait until '1' == '1' after steps (accepted time: 1 s ; timeout: 2 s ; polling: 0.1 s)
            """
            Given TOTO = 'TITI'
            """
        When wait until wait 0.5 seconds (timeout: 0.75 s)
            """
            Given TOTO = 'TITI'
            """
        
        Given next step shall fail on exception matching 'holado_core.common.exceptions.timeout_exception.TimeoutException\(Timeout \(2 s\) when waiting '1' != '1'.*-> Timed out after 2.\d+ s'
        When wait until '1' != '1' after steps (accepted time: 1 s ; timeout: 2 s)
            """
            Given TOTO = 'TITI'
            """
        
        Given next step shall fail on exception matching 'holado_core.common.exceptions.functional_exception.FunctionalException\(Too long \(1.1\d+ s\) to wait wait 1.1 seconds \(accepted time: 1 s\)'
        When wait until wait 1.1 seconds after steps (accepted time: 1 s ; timeout: 2 s)
            """
            Given TOTO = 'TITI'
            """
        
        Given next step shall fail on exception matching 'A step doesn't exist in'
        When wait until missing step after steps (accepted time: 1 s ; timeout: 2 s)
            """
            Given TOTO = 'TITI'
            """
            
        # Part with specific verifications with "after steps"
        Given VALUE = 0
        When wait until VALUE == 10 after steps (polling: 0 s)
            """
            Given VALUE = ${${VALUE} + 1}
            """
            
        Given next step shall fail on exception matching 'Missing steps to execute before Then step'
        When wait until TOTO == '1' after steps
        
    @match_pattern
    Scenario: match pattern
    
        Then 'test (comment)' matches pattern 'est'
        Then 'test (comment)' matches pattern 'est \('
        Then 'test (comment)' matches pattern 'est \\('
        
        Then 'test (comment)\nauto' matches pattern '\nauto'
        Then 'test (comment)\nauto' matches pattern '\)\nauto'
        Then 'test (comment)\nauto' matches pattern '\\)\nauto'
        
        Given TXT = 'comment'
        Then 'test (comment)\nauto' matches pattern 'test \(${TXT}\)\nauto'
    
