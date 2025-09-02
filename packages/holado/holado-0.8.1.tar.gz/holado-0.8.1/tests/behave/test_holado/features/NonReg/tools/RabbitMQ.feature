@testing_solution
@rabbitmq
Feature: Test RabbitMQ module

    @go_nogo
    @simple
    Scenario: Simple queue and one message

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_1 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_1)
            | Name          | Value       |
            | 'host'        | 'localhost' |
            | 'port'        | 5673        |
        Given PUBLISHER = new publisher on queue 'test' (RMQ client: CLIENT_1)
        Given start data events processing (RMQ client: CLIENT_1)
        
        Given CLIENT_2 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_2)
            | Name          | Value       |
            | 'port'        | 5673        |
        Given CONSUMER = new buffer consumer on queue 'test' (RMQ client: CLIENT_2)
        When start consuming (RMQ client: CLIENT_2)
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        
        When publish 'test message' (RMQ publisher: PUBLISHER)
        
        When await consumer CONSUMER receives messages (first timeout: 0.1 s)
        Then consumer CONSUMER received 1 string messages:
            | 'test message' |
            
        When close (RMQ client: CLIENT_1)
        When close (RMQ client: CLIENT_2)



    Scenario: Simple queue and multiple messages

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_1 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_1)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given CLIENT_2 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_2)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PUBLISHER = new publisher on queue 'test' (RMQ client: CLIENT_1)
        
        Given CONSUMER = new buffer consumer on queue 'test' (RMQ client: CLIENT_2)
        When start consuming (RMQ client: CLIENT_2)
        
        When publish 'test message 1' (RMQ publisher: PUBLISHER)
        When publish 'test message 2' (RMQ publisher: PUBLISHER)
        When publish 'test message 3' (RMQ publisher: PUBLISHER)
        When publish 'test message 4' (RMQ publisher: PUBLISHER)
        When publish 'test message 5' (RMQ publisher: PUBLISHER)
        
        When await consumer CONSUMER receives messages (first timeout: 1 s)
        Then consumer CONSUMER received 5 string messages:
            | 'test message 1' |
            | 'test message 2' |
            | 'test message 3' |
            | 'test message 4' |
            | 'test message 5' |

        When close (RMQ client: CLIENT_1)
        When close (RMQ client: CLIENT_2)



    Scenario: Queue + Exchange

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_1 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_1)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given CLIENT_2 = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_2)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PUBLISHER = new publisher (RMQ client: CLIENT_1)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
        
        Given CONSUMER = new buffer consumer (RMQ client: CLIENT_2)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
        When start consuming (RMQ client: CLIENT_2)
        
        When publish 'test message 1' (RMQ publisher: PUBLISHER)
        When publish 'test message 2' (RMQ publisher: PUBLISHER)
        When publish 'test message 3' (RMQ publisher: PUBLISHER)
        When publish 'test message 4' (RMQ publisher: PUBLISHER)
        When publish 'test message 5' (RMQ publisher: PUBLISHER)
        
        When await consumer CONSUMER receives messages (first timeout: 1 s)
        Then consumer CONSUMER received 5 string messages:
            | 'test message 1' |
            | 'test message 2' |
            | 'test message 3' |
            | 'test message 4' |
            | 'test message 5' |

        When close (RMQ client: CLIENT_1)
        When close (RMQ client: CLIENT_2)


    @automatic_connection_type
    Scenario: Queue + Exchange + Routing key (automatic connection type)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new RabbitMQ client with rapid close
        When connect (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given CLIENT_CON = new RabbitMQ client with rapid close
        When connect (RMQ client: CLIENT_CON)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PUBLISHER_1 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk'       |
        Given PUBLISHER_2 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_tmp'   |
        
        Given CONSUMER = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk'       |
        When start consuming (RMQ client: CLIENT_CON)

        When publish 'test message tmp 1' (RMQ publisher: PUBLISHER_2)
        
        When publish 'test message 1' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 2' (RMQ publisher: PUBLISHER_2)

        When publish 'test message 2' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 3' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 4' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 5' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 3' (RMQ publisher: PUBLISHER_2)
        
        When await consumer CONSUMER receives messages (first timeout: 1 s)
        Then consumer CONSUMER received 5 string messages:
            | 'test message 1' |
            | 'test message 2' |
            | 'test message 3' |
            | 'test message 4' |
            | 'test message 5' |
            
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT_CON)
        


    @blocking_connection
    Scenario: Queue + Exchange + Routing key (blocking connection)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given CLIENT_CON = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_CON)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PUBLISHER_1 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk'       |
        Given PUBLISHER_2 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_tmp'   |
        
        Given CONSUMER = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk'       |
        When start consuming (RMQ client: CLIENT_CON)

        When publish 'test message tmp 1' (RMQ publisher: PUBLISHER_2)
        
        When publish 'test message 1' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 2' (RMQ publisher: PUBLISHER_2)

        When publish 'test message 2' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 3' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 4' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 5' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 3' (RMQ publisher: PUBLISHER_2)
        
        When await consumer CONSUMER receives messages (first timeout: 1 s)
        Then consumer CONSUMER received 5 string messages:
            | 'test message 1' |
            | 'test message 2' |
            | 'test message 3' |
            | 'test message 4' |
            | 'test message 5' |
            
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT_CON)


    # Note: this scenario is failing at connect steps on error pika.exceptions.IncompatibleProtocolError 
    @select_connection
    @ScenarioStatus=Draft
    Scenario: Queue + Exchange + Routing key (select connection)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new asynchronous RabbitMQ client
        #When connect (RMQ client: CLIENT_PUB_1)
        When connect with a select connection (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given CLIENT_CON = new asynchronous RabbitMQ client
        When connect with a select connection (RMQ client: CLIENT_CON)
            | Name          | Value       |
            | 'port'        | 5673        |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PUBLISHER_1 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk'       |
        Given PUBLISHER_2 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_tmp'   |
        
        Given CONSUMER = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test'          |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk'       |
        When start consuming (RMQ client: CLIENT_CON)

        When publish 'test message tmp 1' (RMQ publisher: PUBLISHER_2)
        
        When publish 'test message 1' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 2' (RMQ publisher: PUBLISHER_2)

        When publish 'test message 2' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 3' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 4' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 5' (RMQ publisher: PUBLISHER_1)

        When publish 'test message tmp 3' (RMQ publisher: PUBLISHER_2)
        
        When await consumer CONSUMER receives messages (first timeout: 1 s)
        Then consumer CONSUMER received 5 string messages:
            | 'test message 1' |
            | 'test message 2' |
            | 'test message 3' |
            | 'test message 4' |
            | 'test message 5' |
            
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT_CON)
        
        

    @blocking_connection
    @multiple_publishers
    @multiple_consumers
    Scenario: Multiple publishers and consumers (blocking connection)

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given SERVER = new RabbitMQ server
        When run as docker the RabbitMQ server SERVER on ports (5673, 15673)

        Given CLIENT_PUB = new RabbitMQ client
        When connect with a blocking connection (RMQ client: CLIENT_PUB)
            | Name          | Value       |
            | 'port'        | 5673        |
        Given PUBLISHER_1 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test_pub1'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_1'     |
        Given PUBLISHER_2 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test_pub2'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_2'     |
        Given PUBLISHER_3 = new publisher (RMQ client: CLIENT_PUB)
            | Name                      | Value           |
            | 'queue.name'              | 'test_pub3'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'routing_key'             | 'test_rk_3'     |
        
        Given CLIENT_CON = new RabbitMQ client with rapid close
        When connect with a blocking connection (RMQ client: CLIENT_CON)
            | Name          | Value       |
            | 'port'        | 5673        |
        Given CONSUMER_1 = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test_con1'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk_1'     |
        Given CONSUMER_2 = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test_con2'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk_2'     |
        Given CONSUMER_3 = new buffer consumer (RMQ client: CLIENT_CON)
            | Name                      | Value           |
            | 'queue.name'              | 'test_con3'     |
            | 'exchange.name'           | 'test_exchange' |
            | 'exchange.exchange_type'  | 'topic'         |
            | 'bind.routing_key'        | 'test_rk_3'     |
        When start consuming (RMQ client: CLIENT_CON)
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        

        When publish 'test message 1.1' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 2.1' (RMQ publisher: PUBLISHER_2)
        When publish 'test message 1.2' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 3.1' (RMQ publisher: PUBLISHER_3)
        When publish 'test message 3.2' (RMQ publisher: PUBLISHER_3)
        When publish 'test message 2.2' (RMQ publisher: PUBLISHER_2)
        When publish 'test message 1.3' (RMQ publisher: PUBLISHER_1)
        When publish 'test message 3.3' (RMQ publisher: PUBLISHER_3)
        When publish 'test message 2.3' (RMQ publisher: PUBLISHER_2)

        When await consumer CONSUMER_1 receives messages (first timeout: 1 s)
        When await consumer CONSUMER_2 receives messages (first timeout: 0.1 s)
        When await consumer CONSUMER_3 receives messages (first timeout: 0.1 s)
        
        Then consumer CONSUMER_1 received 3 string messages:
            | 'test message 1.1' |
            | 'test message 1.2' |
            | 'test message 1.3' |
        Then consumer CONSUMER_2 received 3 string messages:
            | 'test message 2.1' |
            | 'test message 2.2' |
            | 'test message 2.3' |
        Then consumer CONSUMER_3 received 3 string messages:
            | 'test message 3.1' |
            | 'test message 3.2' |
            | 'test message 3.3' |
            
        When close (RMQ client: CLIENT_PUB)
        When close (RMQ client: CLIENT_CON)
        
        
        