@ais
@type_5
Feature: Message type 5 : Ship Static Data

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T5_SHIP_STATIC_DATA'
            | repeat | mmsi      | ais_version | imo | callsign  | shipname  | ship_type | to_bow | to_stern | to_port | to_starboard | epfd | year | month | day | hour | minute | draught | destination | dte  |
            | 1      | 235006280 | 1           | 1   | 'DEL 001' | 'TITANIC' | True      | True   | True     | True    | True         | 11   | 2024 | 01    | 01  | 08   | 30     | 0.0     | 'SAT KIN'   | True |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T5_SHIP_STATIC_DATA' as bitarray bytes
            | repeat | mmsi      | ais_version | imo | callsign  | shipname  | ship_type | to_bow | to_stern | to_port | to_starboard | epfd | year | month | day | hour | minute | draught | destination | dte  |
            | 1      | 235006280 | 1           | 1   | 'DEL 001' | 'TITANIC' | True      | True   | True     | True    | True         | 11   | 2024 | 01    | 01  | 08   | 30     | 0.0     | 'SAT KIN'   | True |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | 'A'           | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 2
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == 'A'

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | ais_version | callsign  | day | destination | draught | dte  | epfd | hour | imo | minute | mmsi      | month | msg_type | repeat | ship_type | shipname  | to_bow | to_port | to_starboard | to_stern |
            | 1           | 'DEL 001' | 1   | 'SAT KIN'   | 0.0     | True | N/A  | 8    | 1   | 30     | 235006280 | 1     | 5        | 1      | N/A       | 'TITANIC' | 1      | 1       | 1            | 1        |
