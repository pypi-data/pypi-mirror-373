@testing_solution
@python
Feature: Test python iterable steps

    @is_in
    Scenario: Get if an element is in an iterable

        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given LIST_STR = ['v1', 'v2']
        Given STR_IN = 'v1'
        Given STR_NOT_IN = 'x'

        Given end preconditions
        ### PRECONDITIONS - END
        
        Given IS_IN = is 'v1' in ['v1', 'v2']
        Then IS_IN == True
        
        Given IS_IN = is 'xx' in ['v1', 'v2']
        Then IS_IN == False
        
        
        Given IS_IN = is STR_IN in LIST_STR
        Then IS_IN == True
        
        Given IS_IN = is STR_NOT_IN in LIST_STR
        Then IS_IN == False
        
        
    @then_is_in
    Scenario: Verify that element is in an iterable

        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given LIST_STR = ['v1', 'v2']
        Given STR_IN = 'v1'
        Given STR_NOT_IN = 'x'

        Given end preconditions
        ### PRECONDITIONS - END
        
        Then 'v1' is in ['v1', 'v2']
        Then 'xx' is not in ['v1', 'v2']
        
        Then STR_IN is in LIST_STR
        Then STR_NOT_IN is not in LIST_STR
        
        Given next step shall fail on exception matching 'VerifyException\(Value is in iterable:.*value: v1.*iterable: \['v1', 'v2'\]\)'
        Then STR_IN is not in LIST_STR
        
        Given next step shall fail on exception matching 'VerifyException\(Value is not in iterable:.*value: x.*iterable: \['v1', 'v2'\]\)'
        Then STR_NOT_IN is in LIST_STR
        





