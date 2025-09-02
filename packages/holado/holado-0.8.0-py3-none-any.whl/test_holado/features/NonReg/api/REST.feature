@testing_solution
@rest
Feature: Test REST module

    #@need_update
    Scenario: Simple get

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = start internal REST server

        Given CLIENT = new internal REST client
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        When RESULT = get '/users' (REST client: CLIENT)
        Then RESULT['results'] is list
        
        Given TABLE = convert json RESULT['results'] to table with names as columns
        Then table TABLE contains
            | email | groups | url | username |
            | N/A   | N/A    | N/A | 'admin'  |
        
        