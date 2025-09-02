@testing_solution
@rabbitmq
@steps
Feature: Test RabbitMQ steps
  
    @doesnt_receive_message
    Scenario: Consumer doesn't receive messages
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |

        Given CONSUMER = new buffer consumer on queue 'test' (RMQ client: CLIENT)
        When start consuming (RMQ client: CLIENT)
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Then consumer CONSUMER doesn't receive any message (timeout: 0.3 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then DUR >= 0.3
        Then DUR < 0.4
        
        When close (RMQ client: CLIENT)
        When stop (RMQ server: SERVER)
    
    
    
    @wait_consumer_receives_messages
    Scenario: Wait consumer receives messages
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |
        Given PUBLISHER = new publisher on queue 'test' (RMQ client: CLIENT_PUB)
        Given start data events processing (RMQ client: CLIENT_PUB)
        
        Given CLIENT = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |

        Given CONSUMER = new buffer consumer on queue 'test' (RMQ client: CLIENT)
        When start consuming (RMQ client: CLIENT)
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Use case: 
        #   - message takes time to arrive
        #   - message arrives before timeout
        Given PUB_THREAD = new thread that calls steps
            """
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        When await consumer CONSUMER receives a message (timeout: 1 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then consumer CONSUMER received 1 messages
        
        Then DUR >= 0.3
        Then DUR < 0.4
        
        When join thread PUB_THREAD
        
        
        # Use case: 
        #   - message takes time to arrive
        #   - message arrives after timeout
        
        # Wait a little before resetting consumer, in case last publish is received after reset
        Given wait 0.2 seconds
        Given reset stored messages in consumer CONSUMER
        
        Given PUB_THREAD = new thread that calls steps
            """
            When wait 0.5 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        Given next step shall fail on exception matching 'No message was received \(timeout: 0.3 seconds\)'
        When await consumer CONSUMER receives a message (timeout: 0.3 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then DUR >= 0.3
        Then DUR < 0.4
        
        When join thread PUB_THREAD
        
        
        
        # Use case: 
        #   - 1 message arrives rapidely
        #   - messages arrive before timeout
        
        # Wait a little before resetting consumer, in case last publish is received after reset
        Given wait 0.2 seconds
        Given reset stored messages in consumer CONSUMER
        
        Given PUB_THREAD = new thread that calls steps
            """
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.5 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        When await consumer CONSUMER receives a message (timeout: 0.3 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then consumer CONSUMER received 1 messages
        
        Then DUR >= 0.001
        Then DUR < 0.1
        
        When join thread PUB_THREAD
        
        
        # Close
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT)
        When stop (RMQ server: SERVER)
    
    
    
    @wait_consumer_stops_to_receive_messages
    Scenario: Wait consumer stops to receive messages
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |
        Given PUBLISHER = new publisher on queue 'test' (RMQ client: CLIENT_PUB)
        Given start data events processing (RMQ client: CLIENT_PUB)
        
        Given CLIENT = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |

        Given CONSUMER = new buffer consumer on queue 'test' (RMQ client: CLIENT)
        When start consuming (RMQ client: CLIENT)
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Use case: 
        #   - first message takes time to arrive
        #   - first message arrives before first timeout
        Given PUB_THREAD = new thread that calls steps
            """
            When wait 0.5 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.01 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.1 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        When await consumer CONSUMER receives messages (first timeout: 1 s ; window: 0.12 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then consumer CONSUMER received 3 messages
        
        Then DUR >= 0.73
        Then DUR < 0.83
        
        When join thread PUB_THREAD
        
        
        # Use case: 
        #   - first message takes time to arrive
        #   - first message arrives after first timeout
        When await consumer CONSUMER receives no messages (window: 0.2 s ; polling: 0.001 s)
        Given reset stored messages in consumer CONSUMER
        Given PUB_THREAD = new thread that calls steps
            """
            When wait 0.5 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        Given next step shall fail on exception matching 'No message was received \(timeout: 0.3 seconds\)'
        When await consumer CONSUMER receives messages (first timeout: 0.3 s ; window: 0.12 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then DUR >= 0.3
        Then DUR < 0.4
        
        When join thread PUB_THREAD
        
        
        
        # Use case: 
        #   - first message arrives rapidely
        #   - first message arrives before first timeout
        When await consumer CONSUMER receives no messages (window: 0.2 s ; polling: 0.001 s)
        Given reset stored messages in consumer CONSUMER
        Given PUB_THREAD = new thread that calls steps
            """
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.01 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.1 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            
            When wait 0.3 seconds
            When publish 'test message' (RMQ publisher: PUBLISHER)
            """
        
        When start thread PUB_THREAD
        When await consumer CONSUMER receives messages (first timeout: 1 s ; window: 0.12 s ; polling: 0.001 s)
        Given DUR = last step duration
        
        Then consumer CONSUMER received 3 messages
        
        Then DUR >= 0.23
        Then DUR < 0.33
        
        When join thread PUB_THREAD
        
        
        # Close
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT)
        When stop (RMQ server: SERVER)





