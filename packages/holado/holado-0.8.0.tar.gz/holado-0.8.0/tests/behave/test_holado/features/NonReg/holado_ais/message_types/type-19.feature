@ais
@type_19
Feature: Message type 19 : Extended Class B Position Report

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T19_EXTENDED_CLASS_B_POSITION_REPORT'
            | repeat | mmsi      | reserved_1 | speed | accuracy | lon  | lat  | course | heading | second | reserved_2 | shipname | ship_type | to_bow | to_stern | to_port | to_starboard | epfd | raim | dte  | assigned |
            | 1      | 235006280 | 1          | 62.7  | True     | 44.3 | 22.7 | 267.7  | 1       | 2      | 3          | 'WOOHP'  | 1         | 1      | 1        | 2       | 4            | 2    | True | True | True     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T19_EXTENDED_CLASS_B_POSITION_REPORT' as bitarray bytes
            | repeat | mmsi      | reserved_1 | speed | accuracy | lon  | lat  | course | heading | second | reserved_2 | shipname | ship_type | to_bow | to_stern | to_port | to_starboard | epfd | raim | dte  | assigned |
            | 1      | 235006280 | 1          | 62.7  | True     | 44.3 | 22.7 | 267.7  | 1       | 2      | 3          | 'WOOHP'  | 1         | 1      | 1        | 2       | 4            | 2    | True | True | True     |
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
            | accuracy | assigned | course | dte  | epfd | heading | lat  | lon  | mmsi      | msg_type | raim | repeat | reserved_1 | reserved_2 | second | ship_type | shipname | speed | to_bow | to_port | to_starboard | to_stern |
            | True     | True     | 267.7  | True | N/A  | 1       | 22.7 | 44.3 | 235006280 | 19       | True | 1      | 1          | 3          | 2      | N/A       | 'WOOHP'  | 62.7  | 1      | 2       | 4            | 1        |





