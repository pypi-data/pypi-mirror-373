@testing_solution
@docker_controller
Feature: Test Docker Controller client

    Scenario: List containers

        Given CLIENT = new Docker Controller client
            | Name  | Value                   |
            | 'url' | 'http://localhost:8000' |

        Given RESULT = list containers (Docker Controller client: CLIENT)
        
        