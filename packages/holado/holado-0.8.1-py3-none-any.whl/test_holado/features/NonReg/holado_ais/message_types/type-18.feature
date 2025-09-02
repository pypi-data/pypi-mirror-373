@ais
@type_18
Feature: Message type 18 : Standard Class B Position Report

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T18_STANDARD_CLASS_B_POSITION_REPORT'
            | repeat | mmsi      | reserved_1 | speed | accuracy | lon  | lat  | course | heading | second | reserved_2 | cs   | display | dsc  | band | msg22 | raim | radio | assigned |
            | 1      | 235006280 | 1          | 20.2  | True     | 44.3 | 22.7 | 67     | 1       | 2      | 1          | True | True    | True | True | True  | True | 11    | True     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T18_STANDARD_CLASS_B_POSITION_REPORT' as bitarray bytes
            | repeat | mmsi      | reserved_1 | speed | accuracy | lon  | lat  | course | heading | second | reserved_2 | cs   | display | dsc  | band | msg22 | raim | radio | assigned |
            | 1      | 235006280 | 1          | 20.2  | True     | 44.3 | 22.7 | 67     | 1       | 2      | 1          | True | True    | True | True | True  | True | 11    | True     |
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
            | accuracy | assigned | band | course | cs   | display | dsc  | heading | lat  | lon  | mmsi      | msg22 | msg_type | radio | raim | repeat | reserved_1 | reserved_2 | second | speed |
            | True     | True     | True | 67.0   | True | True    | True | 1       | 22.7 | 44.3 | 235006280 | True  | 18       | 11    | True | 1      | 1          | 1          | 2      | 20.2  |




