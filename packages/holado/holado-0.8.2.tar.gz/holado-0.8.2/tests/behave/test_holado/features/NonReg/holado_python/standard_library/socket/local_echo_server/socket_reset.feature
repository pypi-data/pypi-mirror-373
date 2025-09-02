@testing_solution
@python
@socket
Feature: Test python socket reset steps

    @blocking_socket
    @reset_data
    Scenario: Reset received data (client with blocking connections)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name   | Value       |
            | 'host' | '127.0.0.1' |
            | 'port' | PORT        |
        
        Given CLIENT = new TCP socket client
            | Name       | Value       |
            | 'host'     | '127.0.0.1' |
            | 'port'     | PORT        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start server & client
        When start (socket server: SERVER)
        When start (socket client: CLIENT)
        
        # Write data and verify received data size
        When write b'\x01\x02' (socket: CLIENT)
        
        When await socket CLIENT receives data
        When SIZE = size of received data (socket: CLIENT)
        Then SIZE > 0
        
        # Reset data and verify
        Given reset stored received data in socket CLIENT
        When SIZE = size of received data (socket: CLIENT)
        Then SIZE == 0
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



    @non_blocking_socket
    @reset_data
    Scenario: Reset received data (client with non blocking connections)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name   | Value       |
            | 'host' | '127.0.0.1' |
            | 'port' | PORT        |
        
        Given CLIENT = new TCP socket client
            | Name       | Value       |
            | 'host'     | '127.0.0.1' |
            | 'port'     | PORT        |
            | 'blocking' | False       |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start server & client
        When start (socket server: SERVER)
        When start (socket client: CLIENT)
        
        # Write data and verify received data size
        When write b'\x01\x02' (socket: CLIENT)
        
        When await socket CLIENT receives data
        When SIZE = size of received data (socket: CLIENT)
        Then SIZE > 0
        
        # Reset data and verify
        Given reset stored received data in socket CLIENT
        When SIZE = size of received data (socket: CLIENT)
        Then SIZE == 0
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



    @message_socket
    @blocking_socket
    @reset_messages
    Scenario: Reset received messages (client with blocking connections)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name   | Value       |
            | 'host' | '127.0.0.1' |
            | 'port' | PORT        |
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name        | Value       |
            | 'host'      | '127.0.0.1' |
            | 'port'      | PORT        |
            | 'separator' | b'\n'       |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server & message client
        When start (socket server: SERVER)
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write message b'\x01\x02' (socket: CLIENT)
        When write message b'\x11\x21' (socket: CLIENT)
        
        # Verify number of received messages
        When await socket CLIENT receives messages (window: 0.1 s)
        When NB_MSG = number of received messages (socket: CLIENT)
        Then NB_MSG == 2
        
        # Reset data and verify
        Given reset stored received messages in socket CLIENT
        When NB_MSG = number of received messages (socket: CLIENT)
        Then NB_MSG == 0
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



    @message_socket
    @non_blocking_socket
    @reset_messages
    Scenario: Reset received messages (client with non blocking connections)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name   | Value       |
            | 'host' | '127.0.0.1' |
            | 'port' | PORT        |
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name        | Value       |
            | 'host'      | '127.0.0.1' |
            | 'port'      | PORT        |
            | 'separator' | b'\n'       |
            | 'blocking'  | False       |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server & message client
        When start (socket server: SERVER)
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write message b'\x01\x02' (socket: CLIENT)
        When write message b'\x11\x21' (socket: CLIENT)
        
        # Verify number of received messages
        When await socket CLIENT receives messages (window: 0.1 s)
        When NB_MSG = number of received messages (socket: CLIENT)
        Then NB_MSG == 2
        
        # Reset data and verify
        Given reset stored received messages in socket CLIENT
        When NB_MSG = number of received messages (socket: CLIENT)
        Then NB_MSG == 0
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



