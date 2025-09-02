@testing_solution
@behave_steps
Feature: Steps in behave_steps.py

    @expected_exception
    Scenario: expected exception

        Given VAR = 'test'
        Then VAR == 'test'
        
        Given next step shall fail on exception ValueError(invalid literal for int() with base 10: 'test1')
        Then VAR = ${int('test1')}

        Then VAR == 'test'
        
    @expected_following_exception
    Scenario: expected following exception

        Given VAR = 'test'
        Then VAR == 'test'
        
        Given next step shall fail on following exception
            """
            holado_core.common.exceptions.verify_exception.VerifyException(Match failure: 'test' is different than 'test1')
            """
        Then VAR == 'test1'

        Then VAR == 'test'

    @expected_matching_exception
    Scenario: expected matching exception

        Given VAR = 'test'
        Then VAR == 'test'
        
        Given next step shall fail on exception matching 'Match failure: 'test' is different than 'test1''
        Then VAR == 'test1'
        
        Given next step shall fail on exception matching '.*'test' is different than 'test1'.*'
        Then VAR == 'test1'

        Then VAR == 'test'
    
    @decorator=For
    Scenario: decorator "For"
        Given VAR = 0

        #For X in Y:
        Given for X in [1, 2, 3]:
            Given VAR = X
        #For end
        Given end for
        
        Then VAR == 3
        
        Given VAR = 0
        Given NB = 3
        Given for X in range(${${NB} + 5}):
            Given VAR = X
        Given end for
        Then VAR == 7
        
    @decorator=For
    @nested_for
    @simple
    Scenario: nested "For"
        Given N = 0
        Given for X in range(3):
            Given for Y in range(1, 6):
                Given N = ${${N} + 1}
            Given end for
        Given end for
        Then N == 15
        
        
    
    @decorator=While
    Scenario: decorator "While"
        # Condition as a variable
        Given N = 0
        Given COND = True
        Given while COND:
            Given N = ${${N} + 1}
            Given COND = ${${N} < 10}
        Given end while
        Then N == 10
    
        # Condition as expression
        Given N = 0
        Given while ${N} < 10:
            Given N = ${${N} + 1}
        Given end while
        Then N == 10
    
    @function
    Scenario: define function
        Given define function 'N++':
            Given N = ${${N} + 1}
        Given end function
        
        Given N = 0
        When call function 'N++'
        When call function 'N++'
        When call function 'N++'
        Then N == 3
        
        
    @decorator=For
    @nested_for
    @table_with_new_rows
    Scenario: nested "For" with table transformation
        Given TABLE = table with header
            | Name | Value |
            | 'A'  | 'VA'  |
        Given for X in range(3):
            Given for Y in range(1, 6):
                Given TABLE = table TABLE with new rows
                    | Name         | Value   |
                    | 'A${X}.${Y}' | ${Y} |
            Given end for
        Given end for
        Then table TABLE contains
            | Name   | Value |
            | 'A0.1' | 1  |
            | 'A2.5' | 5  |
        
        
    @decorator=If
    Scenario: decorators "If / Else If / Else"
        Given VAR = 0

        # Test If condition
        Given N = 5
        
        Given if ${N} < 10:
            Given VAR = 1
        Given else if ${N} < 20:
            Given VAR = 2
        Given else:
            Given VAR = 3
        Given end if
        
        Then VAR == 1
        
        # Test Else If condition
        Given N = 10
        
        Given if ${N} < 10:
            Given VAR = 1
        Given else if ${N} < 20:
            Given VAR = 2
        Given else:
            Given VAR = 3
        Given end if
        
        Then VAR == 2
        
        # Test Else
        Given N = 20
        
        Given if ${N} < 10:
            Given VAR = 1
        Given else if ${N} < 20:
            Given VAR = 2
        Given else:
            Given VAR = 3
        Given end if
        
        Then VAR == 3
        
        
    @decorator=If
    @nested_if
    @simple
    Scenario: nested "If / Else If / Else"
        Given VAR = 0

        # Test If condition
        Given N = 5
        
        Given if ${N} < 10:
            Given if ${N} < 5:
                Given VAR = 1
            Given else:
                Given VAR = 2
            Given end if
        Given else:
            Given VAR = 3
        Given end if
        
        Then VAR == 2
        
        
    @decorator=If
    @if_in_for
    @simple
    Scenario: If in For
        Given N = 5
        Given M = 2
        
        Given for INDEX in range(0,5):
            Given N = ${${N} + 1}
            Given if ${N} < 10:
                Given N = ${${N} + 3}
            Given else:
                Given M = ${${N} + ${M} + 10}
            Given end if
        Given end for
        
        Then N == 13
        Then M == 88
        
    @decorator=If
    @if_in_for
    @missing_end_if
    #TODO EKL: fix that a missing "end if" has no impact
    @draft
    Scenario: If in For
        Given N = 5
        Given M = 2
        
        Given for INDEX in range(0,5):
            Given N = ${${N} + 1}
            Given if ${N} < 10:
                Given N = ${${N} + 3}
            Given else:
                Given M = ${${N} + ${M} + 10}
        Given end for
        
        Then N == 13
        Then M == 88
        
    @decorator=If
    @for_in_if
    @simple
    Scenario: If in For
        Given N = 5
        Given M = 2
        
        Given if ${N} < 10:
            Given for INDEX in range(0,3):
                Given N = ${${N} + 3}
            Given end for
        Given else:
            Given for INDEX in range(0,3):
                Given M = ${${M} + 2}
            Given end for
        Given end if
        
        Then N == 14
        Then M == 2
        
        Given if ${N} < 10:
            Given for INDEX in range(0,3):
                Given N = ${${N} + 3}
            Given end for
        Given else:
            Given for INDEX in range(0,3):
                Given M = ${${M} + 2}
            Given end for
        Given end if
        
        Then N == 14
        Then M == 8
    
    
    @last_step_duration
    Scenario: Last step duration
        When wait 0.3 seconds
        Given DUR = last step duration
        Then DUR >= 0.3
        Then DUR < 0.31
        
        
    