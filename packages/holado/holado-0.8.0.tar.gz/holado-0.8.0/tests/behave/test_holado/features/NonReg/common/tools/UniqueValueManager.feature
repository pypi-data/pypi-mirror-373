@testing_solution
@UniqueValueManager
Feature: Features related to UniqueValueManager

    Scenario: unique integer

        Given VAR1 = new unique integer
        Given VAR2 = new unique integer

        Then VAR1 != VAR2
        Then VAR1 < VAR2

    Scenario: unique HEX integer

        Given VAR1 = new unique HEX integer
        Given VAR2 = new unique HEX integer

        Then VAR1 != VAR2

    Scenario: unique HEX integer with padding

        Given VAR1 = new unique HEX integer (length: 8)
        Given VAR2 = new unique HEX integer (length: 8)

        Then VAR1 != VAR2
        Then VAR1 < VAR2

    Scenario: unique string

        Given VAR1 = new unique string
        Given VAR2 = new unique string

        Then VAR1 != VAR2
        Then VAR1 < VAR2

    Scenario: unique string with padding

        Given VAR1 = new unique string (padding length: 20)
        Given VAR2 = new unique string (padding length: 20)

        Then VAR1 != VAR2
        Then VAR1 < VAR2
        
