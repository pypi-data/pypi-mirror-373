@ais
@type_23
Feature: Message type 23 : Group Assignment Command

    Scenario: Create, convert, encode and decode message for Channel A
        ### PRECONDITIONS - BEGIN
        Given begin preconditions

        Given NE_LON = 11.5
        Given NE_LAT = 9.3

        Given SW_LON = 22.7
        Given SW_LAT = 18.0

        Given end preconditions
        ### PRECONDITIONS - END

        # Create message
        When MESSAGE = new AIS message of type 'T23_GROUP_ASSIGNMENT_COMMAND'
            | repeat | mmsi      | ne_lon | ne_lat | sw_lon | sw_lat | station_type | ship_type | txrx | interval | quiet |
            | 1      | 235006280 | NE_LON | NE_LAT | SW_LON | SW_LAT | 2            | 1         | 1    | 1        | 15    |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T23_GROUP_ASSIGNMENT_COMMAND' as bitarray bytes
            | repeat | mmsi      | ne_lon | ne_lat | sw_lon | sw_lat | station_type | ship_type | txrx | interval | quiet |
            | 1      | 235006280 | NE_LON | NE_LAT | SW_LON | SW_LAT | 2            | 1         | 1    | 1        | 15    |
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
            | interval | mmsi      | msg_type | ne_lat | ne_lon | quiet | repeat | ship_type | station_type | sw_lat | sw_lon | txrx |
            | N/A      | 235006280 | 23       | NE_LAT | NE_LON | 15    | 1      | N/A       | N/A          | SW_LAT | SW_LON | N/A  |




