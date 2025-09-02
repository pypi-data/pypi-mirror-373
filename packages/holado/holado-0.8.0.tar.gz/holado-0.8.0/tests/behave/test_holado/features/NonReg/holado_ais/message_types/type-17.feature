@ais
@type_17
Feature: Message type 17 : GNSS Broadcast Binary Message

    Scenario: Create, convert, encode and decode message
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given LON = 90.5
        Given LAT = 44.5

        Given end preconditions
        ### PRECONDITIONS - END

        # Create message
        When MESSAGE = new AIS message of type 'T17_GNSS_BROADCAST_BINARY_MESSAGE'
            | repeat | mmsi      | lon | lat | data |
            | 1      | 235006280 | LON | LAT | b'1' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T17_GNSS_BROADCAST_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | lon | lat | data |
            | 1      | 235006280 | LON | LAT | b'1' |
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
            | data | lat | lon | mmsi      | msg_type | repeat |
            | b'1' | LAT | LON | 235006280 | 17       | 1      |




