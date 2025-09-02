@ais
@type_16
Feature: Message type 16 : Assigned Mode Command

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T16_ASSIGNED_MODE_COMMAND'
            | repeat | mmsi      | mmsi1 | offset1 | increment1 | mmsi2    | offset2 | increment2 |
            | 1      | 235006280 | 232   | 501     | 1001       | 23200002 | 102     | 1002       |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T16_ASSIGNED_MODE_COMMAND' as bitarray bytes
            | repeat | mmsi      | mmsi1 | offset1 | increment1 | mmsi2    | offset2 | increment2 |
            | 1      | 235006280 | 232   | 501     | 1001       | 23200002 | 102     | 1002       |
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
            | increment1 | increment2 | mmsi      | mmsi1 | mmsi2    | msg_type | offset1 | offset2 | repeat |
            | 1001       | 1002       | 235006280 | 232   | 23200002 | 16       | 501     | 102     | 1      |





