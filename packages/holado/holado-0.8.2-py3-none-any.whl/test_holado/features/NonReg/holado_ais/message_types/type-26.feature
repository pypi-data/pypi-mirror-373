@ais
@type_26
Feature: Message type 26

    @addressed
    @structured
    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data | radio |
            | 1      | 235006280 | 1         | 1          | 23200001  | 0      | b''  | 1     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data | radio |
            | 1      | 235006280 | 1         | 1          | 23200001  | 0      | b''  | 1     |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'A'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 3
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'A'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | addressed | app_id | data | dest_mmsi | mmsi      | msg_type | radio | repeat | structured |
            | True      | 0      | N/A  | 23200001  | 235006280 | 26       | 1     | 1      | True       |




    @broadcast
    @structured
    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data | radio |
            | 1      | 235006280 | 0         | 1          | 23200001  | 1      | b'A' | 1     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data | radio |
            | 1      | 235006280 | 0         | 1          | 23200001  | 1      | b'A' | 1     |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'A'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 1
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'A'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | addressed | app_id | data | mmsi      | msg_type | radio | repeat | structured |
            | False     | 1      | N/A  | 235006280 | 26       | 1     | 1      | True       |




    @addressed
    @unstructured
    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | data            | radio |
            | 1      | 235006280 | 1         | 0          | 23200001  | b'\x01\x02\x03' | 4     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | data            | radio |
            | 1      | 235006280 | 1         | 0          | 23200001  | b'\x01\x02\x03' | 4     |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'A'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 1
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'A'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | addressed | data            | dest_mmsi | mmsi      | msg_type | radio | repeat | structured |
            | True      | b'\x01\x02\x03' | 23200001  | 235006280 | 26       | 4     | 1      | False      |




    @broadcast
    @unstructured
    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | data            | radio |
            | 1      | 235006280 | 0         | 0          | b'\x01\x02\x03' | 3     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T26_MULTIPLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | data            | radio |
            | 1      | 235006280 | 0         | 0          | b'\x01\x02\x03' | 3     |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'A'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 1
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'A'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | addressed | data            | mmsi      | msg_type | radio | repeat | structured |
            | False     | b'\x01\x02\x03' | 235006280 | 26       | 3     | 1      | False      |




