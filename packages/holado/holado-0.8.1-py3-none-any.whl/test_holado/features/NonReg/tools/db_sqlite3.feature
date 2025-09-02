@testing_solution
@db
@sqlite3
Feature: Test DB module with Sqlite3

    Scenario: Simple example

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given CLIENT = new SQLite3 client
            | Name       | Value      |
            | 'database' | ':memory:' |
        
        When execute [create table people (name_last, age)] (DB client: CLIENT)
        
        # Execute command with parameters in the qmark style:
        Given WHO = 'Yeltsin'
        Given AGE = 72
        When RESULT = result of [insert into people (name_last, age) values (?, ?)] with parameters ('${WHO}', ${AGE}) (DB client: CLIENT)
        Then RESULT == 1

        # Execute command without parameters:
        When RESULT = result of [select * from people] (DB client: CLIENT)
        Then table RESULT is
            | name_last | age |
            | WHO       | AGE |

        # Execute command with parameters in the named style:
        When RESULT = result of [select * from people where name_last=:who and age=:age] with parameters (DB client: CLIENT)
            | Name  | Value    |
            | 'who' | '${WHO}' |
            | 'age' | ${AGE} |
        Then table RESULT is
            | name_last | age |
            | WHO       | AGE |
            