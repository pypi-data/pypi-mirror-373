@testing_solution
@multiprocessing
Feature: Basic features related to multiprocessing

    Scenario: execute simple steps
        Given BEG = datetime now
        Given EXPECTED_MIN = BEG + 3 seconds
        Given EXPECTED_MAX = EXPECTED_MIN + 400 milliseconds
        
        Given PROC_ID_1 = call steps in a process
            """
            Given wait 2 seconds
            """
        Given PROC_ID_2 = call steps in a process
            """
            Given wait 3 seconds
            """
        Given PROC_ID_3 = call steps in a process
            """
            Given wait 1 seconds
            """
        When join process PROC_ID_1
        When join process PROC_ID_2
        When join process PROC_ID_3
        
        Given END = datetime now
        Then END >= EXPECTED_MIN
        Then END < EXPECTED_MAX

    Scenario: execute steps reading variables
        Given SLEEP_1_S = 1
        Given SLEEP_2_S = 2
        Given SLEEP_3_S = 3
        
        Given BEG = datetime now
        Given EXPECTED_MIN = BEG + 3 seconds
        Given EXPECTED_MAX = EXPECTED_MIN + 250 milliseconds
        
        Given PROC_ID_1 = call steps in a process
            """
            Given wait SLEEP_2_S seconds
            """
        Given PROC_ID_2 = call steps in a process
            """
            Given wait SLEEP_3_S seconds
            """
        Given PROC_ID_3 = call steps in a process
            """
            Given wait SLEEP_1_S seconds
            """
        When join process PROC_ID_1
        When join process PROC_ID_2
        When join process PROC_ID_3
        
        Given END = datetime now
        Then END >= EXPECTED_MIN
        Then END < EXPECTED_MAX
        
        
        
