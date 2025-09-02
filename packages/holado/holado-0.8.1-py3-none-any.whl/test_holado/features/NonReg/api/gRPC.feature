@testing_solution
@grpc
Feature: Test gRPC module

    @go_nogo
    Scenario: Simple request

        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given SERVER = start internal gRPC server
        Given CLIENT = new internal gRPC client on service 'account.UserController'

        Given end preconditions
        ### PRECONDITIONS - END

        Given SERVICE_NAMES = service names (gRPC client: CLIENT)
        Then SERVICE_NAMES is list
            | 'account.UserController' |

        When RESULT = request 'account.UserController.List' (gRPC client: CLIENT)

        When TABLE = convert json RESULT to table with names as columns recursively
        Then table TABLE is
            | email           | groups | id  | username    |
            | 'auto@test.com' | []     | N/A | 'test_user' |


    Scenario: Request with parameters
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given SERVER = start internal gRPC server
        Given CLIENT = new internal gRPC client on service 'account.UserController'

        Given end preconditions
        ### PRECONDITIONS - END

        # Extract a user
        When RESULT = request 'account.UserController.List' (gRPC client: CLIENT)
        Given USER_JSON = RESULT[0]

        When RESULT = request 'account.UserController.List' (gRPC client: CLIENT ; with Protobuf response)
        Given USER_PROTO = RESULT[0]

        # Retrieve user with json request & response
        When RESULT = request 'account.UserController.Retrieve' (gRPC client: CLIENT)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        Then RESULT == USER_JSON
        
        # Retrieve user with json request & proto response
        When RESULT = request 'account.UserController.Retrieve' (gRPC client: CLIENT ; with Protobuf response)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        Then RESULT == USER_PROTO
        
        # Retrieve user with proto request & json response
        When RESULT = request 'account.UserController.Retrieve' (gRPC client: CLIENT ; with Protobuf request)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        Then RESULT == USER_JSON
        
        # Retrieve user with proto request & proto response
        When RESULT = request 'account.UserController.Retrieve' (gRPC client: CLIENT ; with Protobuf request & response)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        Then RESULT == USER_PROTO
        
        

    Scenario: Request with request data build before request
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given SERVER = start internal gRPC server
        Given CLIENT = new internal gRPC client on service 'account.UserController'

        Given end preconditions
        ### PRECONDITIONS - END

        # Extract a user
        When RESULT = request 'account.UserController.List' (gRPC client: CLIENT)
        Given USER_JSON = RESULT[0]

        When RESULT = request 'account.UserController.List' (gRPC client: CLIENT ; with Protobuf response)
        Given USER_PROTO = RESULT[0]

        # Retrieve user with json request & response
        When DATA = data for request 'account.UserController.Retrieve' (gRPC client: CLIENT)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        When RESULT = request 'account.UserController.Retrieve' with data DATA (gRPC client: CLIENT)
        Then RESULT == USER_JSON
        
        # Retrieve user with json request & proto response
        When DATA = data for request 'account.UserController.Retrieve' (gRPC client: CLIENT)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        When RESULT = request 'account.UserController.Retrieve' with data DATA (gRPC client: CLIENT ; with Protobuf response)
        Then RESULT == USER_PROTO
        
        # Retrieve user with proto request & json response
        When DATA = data for request 'account.UserController.Retrieve' (gRPC client: CLIENT ; as Protobuf)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        When RESULT = request 'account.UserController.Retrieve' with data DATA (gRPC client: CLIENT)
        Then RESULT == USER_JSON
        
        # Retrieve user with proto request & proto response
        When DATA = data for request 'account.UserController.Retrieve' (gRPC client: CLIENT ; as Protobuf)
            | Name | Value         |
            | 'id' | USER_PROTO.id |
        When RESULT = request 'account.UserController.Retrieve' with data DATA (gRPC client: CLIENT ; with Protobuf response)
        Then RESULT == USER_PROTO

