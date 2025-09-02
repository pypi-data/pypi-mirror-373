@ais
@type_15
Feature: Message type 15 : Interrogation

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T15_INTERROGATION'
            | repeat | mmsi      | mmsi1    | type1_1 | offset1_1 | type1_2 | offset1_2 | mmsi2    | type2_1 | offset2_1 |
            | 1      | 235006280 | 23200001 | 1       | 1000      | 27      | 2000      | 23200002 | 30      | 3000      |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T15_INTERROGATION' as bitarray bytes
            | repeat | mmsi      | mmsi1    | type1_1 | offset1_1 | type1_2 | offset1_2 | mmsi2    | type2_1 | offset2_1 |
            | 1      | 235006280 | 23200001 | 1       | 1000      | 27      | 2000      | 23200002 | 30      | 3000      |
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
            | mmsi      | mmsi1    | mmsi2    | msg_type | offset1_1 | offset1_2 | offset2_1 | repeat | type1_1 | type1_2 | type2_1 |
            | 235006280 | 23200001 | 23200002 | 15       | 1000      | 2000      | 3000      | 1      | 1       | 27      | 30      |



