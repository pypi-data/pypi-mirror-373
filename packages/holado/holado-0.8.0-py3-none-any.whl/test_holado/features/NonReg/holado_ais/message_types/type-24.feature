@ais
@type_24
Feature: Message type 24 : Static Data Report Part A & part B

    @part_A
    Scenario: Create, convert, encode and decode message for Channel A
        # Create message
        When MESSAGE = new AIS message of type 'T24_STATIC_DATA_REPORT'
            | repeat | mmsi      | partno | shipname         |
            | 1      | 235006280 | 0      | 'THOUSAND SUNNY' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T24_STATIC_DATA_REPORT' as bitarray bytes
            | repeat | mmsi      | partno | shipname         |
            | 1      | 235006280 | 0      | 'THOUSAND SUNNY' |
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
            | mmsi      | msg_type | partno | repeat | shipname         |
            | 235006280 | 24       | 0      | 1      | 'THOUSAND SUNNY' |




    @part_B
    Scenario: Create, convert, encode and decode message for Channel B
        # Create message
        When MESSAGE = new AIS message of type 'T24_STATIC_DATA_REPORT'
            | repeat | mmsi      | partno | shipname   | vendorid | model | serial  | callsign | to_bow | to_stern | to_port | to_starboard |
            | 1      | 235006280 | 1      | 'MERRY GO' | '123'    | 14    | 1048574 | 'DEL 55' | True   | True     | True    | True         |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T24_STATIC_DATA_REPORT' as bitarray bytes
            | repeat | mmsi      | partno | shipname   | vendorid | model | serial  | callsign | to_bow | to_stern | to_port | to_starboard |
            | 1      | 235006280 | 1      | 'MERRY GO' | '123'    | 14    | 1048574 | 'DEL 55' | True   | True     | True    | True         |
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
            | callsign | mmsi      | model | msg_type | partno | repeat | serial  | ship_type | to_bow | to_port | to_starboard | to_stern | vendorid |
            | 'DEL 55' | 235006280 | 14    | 24       | 1      | 1      | 1048574 | 0         | 1      | 1       | 1            | 1        | '123'    |




