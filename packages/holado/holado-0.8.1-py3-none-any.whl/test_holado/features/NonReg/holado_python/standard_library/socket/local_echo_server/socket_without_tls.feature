@testing_solution
@python
@socket
Feature: Test python socket steps

    @blocking_socket
    Scenario: Server and client with blocking connections

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
        
        # Start echo server
        When start (socket server: SERVER)
        
        # Write data and verify result is identical
        When write b'\x01\x02' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x01\x02'
        
        When write b'\x11\x21' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x11\x21'
        
        # Stop server & client
        #When stop (socket server: SERVER)



    @message_socket
    @blocking_socket
    Scenario: Echo server and message client with blocking connection

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
        
        # Verify received messages
        When await socket CLIENT receives messages (window: 0.1 s)
        When MESSAGES = received messages (socket: CLIENT)
        Then MESSAGES is list
            | b'\x01\x02' |
            | b'\x11\x21' |
        
        When MESSAGES_2 = received messages (socket: CLIENT)
        Then MESSAGES_2 == MESSAGES
        
        # Verify pop messages functionality
        When MSG_1 = read message (socket: CLIENT)
        Then MSG_1 == b'\x01\x02'
        When MESSAGES_3 = received messages (socket: CLIENT)
        Then MESSAGES_3 is list
            | b'\x11\x21' |

        When MSG_2 = read message (socket: CLIENT)
        Then MSG_2 == b'\x11\x21'
        When MESSAGES_4 = received messages (socket: CLIENT)
        Then MESSAGES_4 is empty list
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



    @message_socket
    @non_blocking_socket
    Scenario: Echo server and message client with non blocking connection

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
        
        # Verify received messages
        When await socket CLIENT receives messages (window: 0.1 s)
        When MESSAGES = received messages (socket: CLIENT)
        Then MESSAGES is list
            | b'\x01\x02' |
            | b'\x11\x21' |
        
        When MESSAGES_2 = received messages (socket: CLIENT)
        Then MESSAGES_2 == MESSAGES
        
        # Verify pop messages functionality
        When MSG_1 = read message (socket: CLIENT)
        Then MSG_1 == b'\x01\x02'
        When MESSAGES_3 = received messages (socket: CLIENT)
        Then MESSAGES_3 is list
            | b'\x11\x21' |

        When MSG_2 = read message (socket: CLIENT)
        Then MSG_2 == b'\x11\x21'
        When MESSAGES_4 = received messages (socket: CLIENT)
        Then MESSAGES_4 is empty list
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



