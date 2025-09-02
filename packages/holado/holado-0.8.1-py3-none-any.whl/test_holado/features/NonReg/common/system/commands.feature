@testing_solution
@commands
Feature: Features realted to commands

    Scenario: Simple command
    
        Given VAR = new command 'pwd'
        Then command VAR has status Ready
        
        Given run command VAR
        Then wait until command VAR has status Success (accepted time: 5 s ; timeout: 10 s)

    Scenario: Simple command with arguments
    
        Given VAR = new command 'pwd' with
            | Name        | Value             |
            | 'blocking'  | False             |
        Then command VAR has status Ready
        
        Given run command VAR
        Then wait until command VAR has status Success (accepted time: 5 s ; timeout: 10 s)

    Scenario: Simple python command
    
        Given VAR = new command 'python3 -c "print('Hello')"' with
            | Name        | Value             |
            | 'blocking'  | True              |
            | 'auto_stop' | True              |
            | 'name'      | 'My command name' |
        Then command VAR has status Ready
        
        Given run command VAR
        Then wait until command VAR has status Success (accepted time: 5 s ; timeout: 10 s)

    Scenario: Failed command
    
        Given VAR = new command 'xxxxxx'
        Then command VAR has status Ready
        
        Given run command VAR
        Then wait until command VAR has status Error (accepted time: 5 s ; timeout: 10 s)
        
        