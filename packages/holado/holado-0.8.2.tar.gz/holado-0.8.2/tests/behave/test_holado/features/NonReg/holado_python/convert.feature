@testing_solution
@python
Feature: Test python convert steps

    @list_to_hexa
    Scenario: Convert list to hexa strings

        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given LIST_STR = ['v1', 'v2']
        Given LIST_HEX_EXPECTED = ['7631', '7632']

        Given end preconditions
        ### PRECONDITIONS - END
        
        Given LIST_HEX = convert list LIST_STR of strings to list of hexadecimal strings
        Then LIST_HEX == LIST_HEX_EXPECTED
        

