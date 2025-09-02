@ais
@type_7
@type_13
Feature: Message types 7 and 13 : Binary Acknowledge

    Scenario Outline: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type '<message_type>'
            | repeat | mmsi      | mmsi1    | mmsiseq1 | mmsi2    | mmsiseq2 | mmsi3    | mmsiseq3 | mmsi4    | mmsiseq4 |
            | 2      | 235006280 | 23200001 | 3        | 23200002 | 3        | 23200003 | 2        | 23200004 | 1        |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type '<message_type>' as bitarray bytes
            | repeat | mmsi      | mmsi1    | mmsiseq1 | mmsi2    | mmsiseq2 | mmsi3    | mmsiseq3 | mmsi4    | mmsiseq4 |
            | 2      | 235006280 | 23200001 | 3        | 23200002 | 3        | 23200003 | 2        | 23200004 | 1        |
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
            | mmsi      | mmsi1    | mmsi2    | mmsi3    | mmsi4    | mmsiseq1 | mmsiseq2 | mmsiseq3 | mmsiseq4 | msg_type | repeat |
            | 235006280 | 23200001 | 23200002 | 23200003 | 23200004 | 3        | 3        | 2        | 1        | <type>   | 2      |

        Examples: With types 7 and 13
            | message_type           | type | channel |
            | T7_BINARY_ACKNOWLEGDE  | 7     | 'A'     |
            | T13_BINARY_ACKNOWLEGDE | 13    | 'A'     |

            
            
            