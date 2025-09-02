@testing_solution
@behave_parameter
Feature: Test behave parameter

    Scenario: Parameter with -D argument

        Given PARAM = defined user data 'A_PARAMETER_NAME'
        Then PARAM == None

        Given PARAM = defined user data 'A_PARAMETER_NAME' (default: 100)
        Then PARAM == 100

        Given PARAM = defined user data 'param' (default: 100)
        
        