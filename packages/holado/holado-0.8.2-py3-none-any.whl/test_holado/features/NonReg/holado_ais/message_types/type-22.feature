@ais
@type_22
Feature: Message type 22 : Channel Management Addressed & Broadcast

    @addressed
    Scenario: Create, convert, encode and decode message for Channel A
        # Create message
        When MESSAGE = new AIS message of type 'T22_CHANNEL_MANAGEMENT'
            | repeat | mmsi      | channel_a | channel_b | txrx | power | addressed | dest1     | empty_1 | dest2     | empty_2 | zonesize |
            | 1      | 235006280 | True      | False     | True | 1     | 1         | 235006281 | 1       | 235006282 | 2       | 1        |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T22_CHANNEL_MANAGEMENT' as bitarray bytes
            | repeat | mmsi      | channel_a | channel_b | txrx | power | addressed | dest1     | empty_1 | dest2     | empty_2 | zonesize |
            | 1      | 235006280 | True      | False     | True | 1     | 1         | 235006281 | 1       | 235006282 | 2       | 1        |
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
            | addressed | band_a | band_b | channel_a | channel_b | dest1     | dest2     | empty_1 | empty_2 | mmsi      | msg_type | power | repeat | txrx | zonesize |
            | True      | False  | False  | 1         | 0         | 235006281 | 235006282 | 1       | 2       | 235006280 | 22       | True  | 1      | 1    | 1        |




    @broadcast
    Scenario: Create, convert, encode and decode message for Channel B
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given NE_LON = 33.2
        Given NE_LAT = 6.2

        Given SW_LON = 15.7
        Given SW_LAT = 1.1

        Given end preconditions
        ### PRECONDITIONS - END

        # Create message
        When MESSAGE = new AIS message of type 'T22_CHANNEL_MANAGEMENT'
            | repeat | mmsi      | channel_a | channel_b | txrx  | power | addressed | dest1 | empty_1 | dest2 | empty_2 | zonesize | ne_lon | ne_lat | sw_lon | sw_lat |
            | 1      | 235006280 | False     | True      | False | 1     | 0         | 11    | 1       | 22    | 2       | 0        | NE_LON | NE_LAT | SW_LON | SW_LAT |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T22_CHANNEL_MANAGEMENT' as bitarray bytes
            | repeat | mmsi      | channel_a | channel_b | txrx  | power | addressed | dest1 | empty_1 | dest2 | empty_2 | zonesize | ne_lon | ne_lat | sw_lon | sw_lat |
            | 1      | 235006280 | False     | True      | False | 1     | 0         | 11    | 1       | 22    | 2       | 0        | NE_LON | NE_LAT | SW_LON | SW_LAT |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'B'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 1
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'B'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | addressed | band_a | band_b | channel_a | channel_b | mmsi      | msg_type | ne_lat | ne_lon | power | repeat | sw_lat | sw_lon | txrx | zonesize |
            | False     | False  | False  | 0         | 1         | 235006280 | 22       | NE_LAT  | NE_LON | True  | 1      | SW_LAT   | SW_LON  | 0    | 0        |




