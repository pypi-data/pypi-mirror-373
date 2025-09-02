@testing_solution
@python
@socket
@ssl
@without_cert_file
Feature: Test python socket steps with ssl, server with self-signed keys, and client doesn't verify certificate

    @blocking_socket
    Scenario: Server and client with blocking connections

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Get certificate
        #Given CACERTS_PATH = default CA certs file path
        #Given CACERTS_PATH = CA certs file path (from certifi package)
        #Given CERTS_PATH = default certs directory path
        
        # Generate key files
        Given CERTFILE_PATH = path to file with name 'localhost.crt'
        Given KEYFILE_PATH = path to file with name 'localhost.key'
        Given generate new self-signed key files for localhost
            | Name                | Value         |
            | 'public_key_path'   | CERTFILE_PATH |
            | 'private_key_path'  | KEYFILE_PATH  |
            | 'algorithm'         | 'rsa:2048'    |
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name                                   | Value         |
            | 'host'                                 | 'localhost'   |
            | 'port'                                 | PORT          |
            | 'ssl.activate'                         | True          |
            #| 'ssl.create_default_context.cafile'    | CACERTS_PATH  |
            #| 'ssl.create_default_context.capath'    | CERTS_PATH    |
            | 'ssl.context.ciphers'                  | 'ALL'         |
            #| 'ssl.context.ciphers'                  | '@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:AESGCM:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM:!PSK'         |
            #| 'ssl.context.ciphers'                  | 'AES256-GCM-SHA384'         |
            #| 'ssl.context.ciphers'                  | 'DEFAULT'         |
            #| 'ssl.context.ciphers'                  | 'OPENSSL_CIPHERS'         |
            #| 'ssl.context.ciphers'                  | '@SECLEVEL=1:ALL'         |
            | 'ssl.context.load_cert_chain.certfile' | CERTFILE_PATH |
            | 'ssl.context.load_cert_chain.keyfile'  | KEYFILE_PATH  |
            #| 'ssl.context.minimum_version'                  | ssl.TLSVersion.TLSv1_2     |
        
        # Create a TCP client with a blocking connection
        Given CLIENT = new TCP socket client
            | Name                                       | Value         |
            | 'host'                                     | 'localhost'   |
            | 'port'                                     | PORT          |
            | 'ssl.activate'                             | True          |
            #| 'ssl.create_default_context.cafile'        | CERTFILE_PATH |
            | 'ssl.context.ciphers'                      | 'ALL'         |
            #| 'ssl.context.ciphers'                      | '@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:AESGCM:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM:!PSK' |
            #| 'ssl.context.ciphers'                      | 'AES256-GCM-SHA384' |
            #| 'ssl.context.ciphers'                      | 'DEFAULT'     |
            #| 'ssl.context.ciphers'                      | 'OPENSSL_CIPHERS' |
            #| 'ssl.context.ciphers'                      | '@SECLEVEL=1:ALL' |
            #| 'ssl.context.minimum_version'              | ssl.TLSVersion.TLSv1_2 |
            | 'ssl.context.check_hostname'               | False         |
            | 'ssl.context.verify_mode'                  | ssl.CERT_NONE |
            #| 'ssl.context.load_verify_locations.cafile' | CERTFILE_PATH |
            
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server
        When start (socket server: SERVER)
        When ensure SSL handshake is done (socket: CLIENT)
        
        # Write data and verify result is identical
        When write b'\x01\x02' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x01\x02'
        
        When write b'\x11\x21' (socket: CLIENT)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x11\x21'
        
        # Stop server
        #When stop (socket server: SERVER)


    @non_blocking_socket
    Scenario: Server and client with non blocking connection

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Generate key files
        Given CERTFILE_PATH = path to file with name 'localhost.crt'
        Given KEYFILE_PATH = path to file with name 'localhost.key'
        Given generate new self-signed key files for localhost
            | Name                | Value         |
            | 'public_key_path'   | CERTFILE_PATH |
            | 'private_key_path'  | KEYFILE_PATH  |
            | 'algorithm'         | 'rsa:2048'    |
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name                                   | Value         |
            | 'host'                                 | 'localhost'   |
            | 'port'                                 | PORT          |
            | 'ssl.activate'                         | True          |
            | 'ssl.context.ciphers'                  | 'ALL'         |
            | 'ssl.context.load_cert_chain.certfile' | CERTFILE_PATH |
            | 'ssl.context.load_cert_chain.keyfile'  | KEYFILE_PATH  |
        
        # Create a TCP client with a blocking connection
        Given CLIENT = new TCP socket client
            | Name                                       | Value         |
            | 'host'                                     | 'localhost'   |
            | 'port'                                     | PORT          |
            | 'blocking'                                 | False         |
            | 'ssl.activate'                             | True          |
            | 'ssl.context.check_hostname'               | False         |
            | 'ssl.context.verify_mode'                  | ssl.CERT_NONE |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server & client
        When start (socket server: SERVER)
        When start (socket client: CLIENT)
        
        # Write data and verify result is identical
        When write b'\x01\x02' (socket: CLIENT)
        When await socket CLIENT receives data (window: 0.1 s)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x01\x02'
        
        When write b'\x11\x21' (socket: CLIENT)
        When await socket CLIENT receives data (window: 0.1 s)
        When DATA = read (socket: CLIENT)
        Then DATA == b'\x11\x21'
        
        # Stop server & client
        #When stop (socket server: SERVER)
        When stop (socket client: CLIENT)



    @message_socket
    @blocking_socket
    Scenario: Echo server and message client (with underlying blocking connection)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Generate key files
        Given CERTFILE_PATH = path to file with name 'localhost.crt'
        Given KEYFILE_PATH = path to file with name 'localhost.key'
        Given generate new self-signed key files for localhost
            | Name                | Value         |
            | 'public_key_path'   | CERTFILE_PATH |
            | 'private_key_path'  | KEYFILE_PATH  |
            | 'algorithm'         | 'rsa:2048'    |
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name                                   | Value         |
            | 'host'                                 | 'localhost'   |
            | 'port'                                 | PORT          |
            | 'ssl.activate'                         | True          |
            | 'ssl.context.ciphers'                  | 'OPENSSL_CIPHERS' |
            | 'ssl.context.load_cert_chain.certfile' | CERTFILE_PATH |
            | 'ssl.context.load_cert_chain.keyfile'  | KEYFILE_PATH  |
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name                                       | Value         |
            | 'host'                                     | 'localhost'   |
            | 'port'                                     | PORT          |
            | 'separator'                                | b'\n'         |
            | 'ssl.activate'                             | True          |
            | 'ssl.context.check_hostname'               | False         |
            | 'ssl.context.verify_mode'                  | ssl.CERT_NONE |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server & message client
        When start (socket server: SERVER)
        #When ensure SSL handshake is done (socket: CLIENT)
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
    Scenario: Echo server and message client (with underlying non-blocking connection)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Generate key files
        Given CERTFILE_PATH = path to file with name 'localhost.crt'
        Given KEYFILE_PATH = path to file with name 'localhost.key'
        Given generate new self-signed key files for localhost
            | Name                | Value         |
            | 'public_key_path'   | CERTFILE_PATH |
            | 'private_key_path'  | KEYFILE_PATH  |
            | 'algorithm'         | 'rsa:2048'    |
        
        # Use echo server with a blocking connection
        Given PORT = first available anonymous port
        Given SERVER = new echo TCP socket server
            | Name                                   | Value         |
            | 'host'                                 | 'localhost'   |
            | 'port'                                 | PORT          |
            | 'ssl.activate'                         | True          |
            | 'ssl.context.ciphers'                  | 'SHA256'      |
            | 'ssl.context.load_cert_chain.certfile' | CERTFILE_PATH |
            | 'ssl.context.load_cert_chain.keyfile'  | KEYFILE_PATH  |
        
        # Create a message client
        Given CLIENT = new message TCP socket client
            | Name                                       | Value         |
            | 'host'                                     | 'localhost'   |
            | 'port'                                     | PORT          |
            | 'separator'                                | b'\n'         |
            | 'blocking'                                 | False         |
            | 'ssl.activate'                             | True          |
            | 'ssl.context.check_hostname'               | False         |
            | 'ssl.context.verify_mode'                  | ssl.CERT_NONE |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Start echo server & message client
        When start (socket server: SERVER)
        #When ensure SSL handshake is done (socket: CLIENT)
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



