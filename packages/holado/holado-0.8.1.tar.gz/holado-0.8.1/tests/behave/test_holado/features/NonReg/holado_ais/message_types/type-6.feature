@ais
@type_6
Feature: Message type 6 : Addressed Binary Message

    Scenario: Create, convert, encode and decode message
        # Create message
        When MESSAGE = new AIS message of type 'T6_ADDRESSED_BINARY_MESSAGE'
            | repeat | mmsi      | seqno | dest_mmsi | retransmit | dac | fid | data        |
            | 1      | 235006280 | 3     | 23200002  | True       | 1   | 1   | b'15007B00' |
            
        # Verify bytes conversion
        When MESSAGE_TO_BYTES = convert AIS message MESSAGE to bytes
        When MESSAGE_BYTES = new AIS message of type 'T6_ADDRESSED_BINARY_MESSAGE' as bitarray bytes
            | repeat | mmsi      | seqno | dest_mmsi | retransmit | dac | fid | data        |
            | 1      | 235006280 | 3     | 23200002  | True       | 1   | 1   | b'15007B00' |
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
            | dac | data        | dest_mmsi | fid | mmsi      | msg_type | repeat | retransmit | seqno |
            | 1   | b'15007B00' | 23200002  | 1   | 235006280 | 6        | 1      | True       | 3     |




