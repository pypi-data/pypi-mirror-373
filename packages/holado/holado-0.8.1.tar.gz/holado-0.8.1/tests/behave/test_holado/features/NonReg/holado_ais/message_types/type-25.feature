@ais
@type_25
Feature: Message type 25 : Single Slot Binary Message

    @addressed
    @structured
    Scenario: Create, convert, encode and decode message for Channel A
        # Create message
        When MESSAGE = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 1         | 1          | 23200001  | 1      | b'1' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 1         | 1          | 23200001  | 1      | b'1' |
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
            | addressed | app_id | data | dest_mmsi | mmsi      | msg_type | repeat | structured |
            | True      | 1      | b'1' | 23200001  | 235006280 | 25       | 1      | True       |




    @broadcast
    @structured
    Scenario: Create, convert, encode and decode message for Channel B
        # Create message
        When MESSAGE = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 0         | 1          | 23200001  | 1      | b'A' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 0         | 1          | 23200001  | 1      | b'A' |
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
            | addressed | app_id | data | mmsi      | msg_type | repeat | structured |
            | False     | 1      | b'A' | 235006280 | 25       | 1      | True       |




    @addressed
    @unstructured
    Scenario: Create, convert, encode and decode message for Channel A
        # Create message
        When MESSAGE = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 1         | 0          | 23200001  | 0      | b'B' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data |
            | 1      | 235006280 | 1         | 0          | 23200001  | 0      | b'B' |
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
            | addressed | data | dest_mmsi | mmsi      | msg_type | repeat | structured |
            | True      | b'B' | 23200001  | 235006280 | 25       | 1      | False      |




    @broadcast
    @unstructured
    Scenario: Create, convert, encode and decode message for Channel B
        # Create message
        When MESSAGE = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE'
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data  |
            | 1      | 235006280 | 0         | 0          | 23200001  | 0      | b'21' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T25_SINGLE_SLOT_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | addressed | structured | dest_mmsi | app_id | data  |
            | 1      | 235006280 | 0         | 0          | 23200001  | 0      | b'21' |
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
            | addressed | data  | mmsi      | msg_type | repeat | structured |
            | False     | b'21' | 235006280 | 25       | 1      | False      |



