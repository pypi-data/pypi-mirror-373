@ais
@type_1
@type_2
@type_3
Feature: Message types 1, 2 and 3 : position report

    Scenario Outline: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type '<message_type>'
            | repeat | mmsi      | status | turn | speed | accuracy | lon  | lat  | course | heading | second | maneuver | raim | radio |
            | 1      | 235006280 | 1      | 2    | 50.4  | True     | 11.2 | 13.1 | 0.0    | 1       | 1      | 1        | True | 1     |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type '<message_type>' as bitarray bytes
            | repeat | mmsi      | status | turn | speed | accuracy | lon  | lat  | course | heading | second | maneuver | raim | radio |
            | 1      | 235006280 | 1      | 2    | 50.4  | True     | 11.2 | 13.1 | 0.0    | 1       | 1      | 1        | True | 1     |
		Then MESSAGE_TO_BYTES == MESSAGE_BYTES
		
		# Encode in NMEA
		When NMEA_SENTENCES = encode AIS raw payload MESSAGE_BYTES to NMEA
            | talker_id | radio_channel | seq_id | group_id |
            | 'AIVDM'   | <channel>     | 0      | 0        |
        Then ${len(NMEA_SENTENCES)} == 1
		
        # Verify some NMEA fields
        Given STRING_NMEA_MSG = split NMEA AIS message NMEA_SENTENCES[0] to fields
        Then STRING_NMEA_MSG[-3] == <channel>

        # Decode NMEA message
        Given DECODED_NMEA_MESSAGE = decode NMEA AIS message NMEA_SENTENCES as dictionnary
        When DECODED_NMEA_MESSAGE_TABLE = convert dictionary DECODED_NMEA_MESSAGE to table with keys as columns
        Then table DECODED_NMEA_MESSAGE_TABLE is
            | accuracy | course | heading | lat  | lon  | maneuver | mmsi      | msg_type | radio | raim | repeat | second | speed | status | turn |
            | True     | 0.0    | 1       | 13.1 | 11.2 | N/A      | 235006280 | <type>   | 1     | True | 1      | 1      | 50.4  | N/A    | 2    |

        Examples: With types 1, 2 and 3
            | message_type    | type | channel |
            | T1_POSITION_REPORT | 1    | 'A'     |
            | T2_POSITION_REPORT | 2    | 'A'     |
            | T3_POSITION_REPORT | 3    | 'A'     |

