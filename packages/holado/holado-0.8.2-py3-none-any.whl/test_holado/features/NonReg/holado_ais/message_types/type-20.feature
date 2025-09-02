@ais
@type_20
Feature: Message type 20 : Data Link Management

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T20_DATA_LINK_MANAGEMENT'
            | repeat | mmsi      | offset1 | number1 | timeout1 | increment1 | offset2 | number2 | timeout2 | increment2 | offset3 | number3 | timeout3 | increment3 | offset4 | number4 | timeout4 | increment4 |
            | 1      | 235006280 | 1000    | 5       | 1        | 2047       | 2000    | 10      | 5        | 2000       | 3000    | 15      | 7        | 1000       | 4000    | 15      | 7        | 500        |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T20_DATA_LINK_MANAGEMENT' as bitarray bytes
            | repeat | mmsi      | offset1 | number1 | timeout1 | increment1 | offset2 | number2 | timeout2 | increment2 | offset3 | number3 | timeout3 | increment3 | offset4 | number4 | timeout4 | increment4 |
            | 1      | 235006280 | 1000    | 5       | 1        | 2047       | 2000    | 10      | 5        | 2000       | 3000    | 15      | 7        | 1000       | 4000    | 15      | 7        | 500        |
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
            | increment1 | increment2 | increment3 | increment4 | mmsi      | msg_type | number1 | number2 | number3 | number4 | offset1 | offset2 | offset3 | offset4 | repeat | timeout1 | timeout2 | timeout3 | timeout4 |
            | 2047       | 2000       | 1000       | 500        | 235006280 | 20       | 5       | 10      | 15      | 15      | 1000    | 2000    | 3000    | 4000    | 1      | 1        | 5        | 7        | 7        |





