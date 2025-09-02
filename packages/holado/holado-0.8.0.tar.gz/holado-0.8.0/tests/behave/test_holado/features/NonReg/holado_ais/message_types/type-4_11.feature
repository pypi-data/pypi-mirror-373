@ais
@type_4
@type_11
Feature: Message types 4 and 11 : Base Station Report

    Scenario Outline: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type '<message_type>'
            | repeat | mmsi      | year | month | day | hour | minute | second | accuracy | lon  | lat  | epfd | raim  | radio |
            | 1      | 235006280 | 2024 | 01    | 01  | 08   | 30     | 56     | True     | 70.9 | 44.2 | 1    | False | 1     |

        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type '<message_type>' as bitarray bytes
            | repeat | mmsi      | year | month | day | hour | minute | second | accuracy | lon  | lat  | epfd | raim  | radio |
            | 1      | 235006280 | 2024 | 01    | 01  | 08   | 30     | 56     | True     | 70.9 | 44.2 | 1    | False | 1     |
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
            | accuracy | day | epfd | hour | lat  | lon  | minute | mmsi      | month | msg_type | radio | raim  | repeat | second | year |
            | True     | 1   | N/A  | 8    | 44.2 | 70.9 | 30     | 235006280 | 1     | <type>   | 1     | False | 1      | 56     | 2024 |

        Examples: With types 4 and 11
            | message_type            | type | channel |
            | T4_BASE_STATION_REPORT  | 4    | 'A'     |
            | T11_BASE_STATION_REPORT | 11   | 'A'     |