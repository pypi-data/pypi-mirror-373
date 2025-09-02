@testing_solution
@sftp
Feature: Test sFTP module

    @go_nogo
    Scenario: Simple test

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = start internal sFTP server
        Given wait 1 seconds

        Given CLIENT = new internal sFTP client
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        When RESULT = result of [pwd] (sFTP client: CLIENT)
        Then RESULT == '/'
        
        When RESULT = result of [listdir()] (sFTP client: CLIENT)
        Then RESULT is empty list
        
            