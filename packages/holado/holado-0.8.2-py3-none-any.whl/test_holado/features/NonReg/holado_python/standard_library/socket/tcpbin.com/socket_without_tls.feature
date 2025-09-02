@testing_solution
@python
@socket
@tcpbin.com
@without_tls
Feature: Test python socket steps with tcpbin.com echo server

    @blocking_socket
    Scenario: Client with blocking connections

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given CLIENT = new TCP socket client
            | Name       | Value        |
            | 'host'     | 'tcpbin.com' |
            | 'port'     | 4242         |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Write data and verify result is identical
        When write b'test 1\n' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'test 1\n'
        
        When write b'test 2\n' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'test 2\n'
        


    @non_blocking_socket
    Scenario: Client with non blocking connections

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given CLIENT = new TCP socket client
            | Name       | Value        |
            | 'host'     | 'tcpbin.com' |
            | 'port'     | 4242         |
            | 'blocking' | False        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start message client
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write b'test 1\n' (socket: CLIENT)
        When await socket CLIENT receives a data
        When DATA = read (socket: CLIENT)
        Then DATA == b'test 1\n'
        
        When write b'test 2\n' (socket: CLIENT)
        When await socket CLIENT receives a data (timeout: 10 s)
        When DATA = read (socket: CLIENT)
        Then DATA == b'test 2\n'
        
        # Stop client
        When stop (socket client: CLIENT)
        


    @message_socket
    @blocking_socket
    Scenario: Message client with blocking connection

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name        | Value        |
            | 'host'      | 'tcpbin.com' |
            | 'port'      | 4242         |
            | 'separator' | b'\n'        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start message client
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write message b'\x01\x02' (socket: CLIENT)
        When write message b'\x11\x21' (socket: CLIENT)
        
        # Verify received messages
        When await socket CLIENT receives messages (first timeout: 10 s ; window: 0.1 s)
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
        When stop (socket client: CLIENT)



    @message_socket
    @non_blocking_socket
    Scenario: Message client with non blocking connection

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name        | Value        |
            | 'host'      | 'tcpbin.com' |
            | 'port'      | 4242         |
            | 'separator' | b'\n'        |
            | 'blocking'  | False        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start message client
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write message b'\x01\x02' (socket: CLIENT)
        When write message b'\x11\x21' (socket: CLIENT)
        
        # Verify received messages
        When await socket CLIENT receives messages (first timeout: 10 s ; window: 0.1 s)
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
        
        # Stop client
        When stop (socket client: CLIENT)



