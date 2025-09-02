@ais
@type_9
Feature: Message type 9 : Standard SAR Aircraft Position Report

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T9_STANDARD_SAR_AIRCRAFT_POSITION_REPORT'
            | repeat | mmsi      | alt | speed | accuracy | lon  | lat  | course | second | reserved_1 | dte  | assigned | raim | radio |
            | 1      | 235006280 | 1   | 44.2  | False    | 60.3 | 45.0 | 1.7    | 1      | 1          | True | True     | True | 1     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T9_STANDARD_SAR_AIRCRAFT_POSITION_REPORT' as bitarray bytes
            | repeat | mmsi      | alt | speed | accuracy | lon  | lat  | course | second | reserved_1 | dte  | assigned | raim | radio |
            | 1      | 235006280 | 1   | 44.2  | False    | 60.3 | 45.0 | 1.7    | 1      | 1          | True | True     | True | 1     |
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
            | accuracy | alt | assigned | course | dte  | lat  | lon  | mmsi      | msg_type | radio | raim | repeat | reserved_1 | second | speed |
            | False    | 1   | True     | 1.7    | True | 45.0 | 60.3 | 235006280 | 9        | 1     | True | 1      | 1          | 1      | 44.0  |




