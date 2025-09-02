@ais
@type_21
Feature: Message type 21 : Aids To Navigation Report

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T21_AIDS_TO_NAVIGATION_REPORT'
            | repeat | mmsi       | name      | accuracy | lon  | lat  | to_bow | to_stern | to_port | to_starboard | epfd | second | off_position | reserved_1 | raim | virtual_aid | assigned | name_ext |
            | 1      | 0235006280 | 'TYPE 21' | True     | 11.2 | 13.1 | 1      | 1        | 1       | 1            | 1    | 1      | True         | 7          | True | True        | True     | 'AIS 21' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T21_AIDS_TO_NAVIGATION_REPORT' as bitarray bytes
            | repeat | mmsi       | name      | accuracy | lon  | lat  | to_bow | to_stern | to_port | to_starboard | epfd | second | off_position | reserved_1 | raim | virtual_aid | assigned | name_ext |
            | 1      | 0235006280 | 'TYPE 21' | True     | 11.2 | 13.1 | 1      | 1        | 1       | 1            | 1    | 1      | True         | 7          | True | True        | True     | 'AIS 21' |
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
            | accuracy | aid_type | assigned | epfd | lat  | lon  | mmsi      | msg_type | name      | name_ext | off_position | raim | repeat | reserved_1 | second | to_bow | to_port | to_starboard | to_stern | virtual_aid |
            | True     | N/A      | True     | N/A  | 13.1 | 11.2 | 235006280 | 21       | 'TYPE 21' | 'AIS 21' | True         | True | 1      | 7          | 1      | 1      | 1       | 1            | 1        | True        |




