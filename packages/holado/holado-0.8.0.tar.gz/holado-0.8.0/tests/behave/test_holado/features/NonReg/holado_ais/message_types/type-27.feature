@ais
@type_27
Feature: Message type 27

    Scenario: Create, convert, encode and decode message for Channel A
        # Create message
        When MESSAGE = new AIS message of type 'T27_LONG_RANG_AIS_BROADCAST_MESSAGE'
            | repeat | mmsi      | accuracy | raim  | status | lon  | lat  | speed | course | gnss |
            | 1      | 235006280 | True     | False | 1      | 65.2 | 20.3 | 11.0  | 6.0    | True |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T27_LONG_RANG_AIS_BROADCAST_MESSAGE' as bitarray bytes
            | repeat | mmsi      | accuracy | raim  | status | lon  | lat  | speed | course | gnss |
            | 1      | 235006280 | True     | False | 1      | 65.2 | 20.3 | 11.0  | 6.0    | True |
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
            | accuracy | course | gnss | lat  | lon  | mmsi      | msg_type | raim  | repeat | speed | status |
            | True     | 6.0    | True | 20.3 | 65.2 | 235006280 | 27       | False | 1      | 11.0  | N/A    |



