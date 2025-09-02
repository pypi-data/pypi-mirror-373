@ais
@type_8
Feature: Message type 8 : Binary Broadcast Message

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T8_BINARY_BROADCAST_MESSAGE'
            | repeat | mmsi      | dac | fid | data |
            | 1      | 235006280 | 5   | 3   | b'1' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T8_BINARY_BROADCAST_MESSAGE' as bitarray bytes
            | repeat | mmsi      | dac | fid | data |
            | 1      | 235006280 | 5   | 3   | b'1' |
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
            | dac | data | fid | mmsi      | msg_type | repeat |
            | 5   | b'1' | 3   | 235006280 | 8        | 1      |




