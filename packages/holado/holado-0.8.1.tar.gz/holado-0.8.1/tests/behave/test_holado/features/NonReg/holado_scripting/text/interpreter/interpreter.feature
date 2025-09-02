@testing_solution
@TextInterpreter
Feature: Features related to TextInterpreter

    @variable
    Scenario: interpret with variable reference
        Given VAL_1 = 'value 1'
        Given PARAM_NAME = 'VAL_1'
        
        When RES = PARAM_NAME
        Then RES == 'VAL_1'
        
        When RES = '${PARAM_NAME}'
        Then RES == 'VAL_1'
        
        When RES = ${PARAM_NAME}
        Then RES == 'value 1'
        
        When RES = '${${PARAM_NAME}}'
        Then RES == 'value 1'

    @HexToBytes
    Scenario: function HexToBytes

        Given HEX = '01569F'
        Given VALUE_1 = ${HexToBytes(HEX)}
        Then VALUE_1 == b'\x01\x56\x9F'

        Given VALUE_2 = ${HexToBytes('FFFF')}
        Then VALUE_2 == b'\xFF\xFF'

    @HexToInt
    Scenario: function HexToInt
        
        Given HEX = '040A'
        Given VALUE = ${HexToInt(HEX)}
        Then VALUE == 1034
        
        Given VALUE = ${HexToInt(040A)}
        Then VALUE == 1034
        
        Given VALUE = ${HexToInt('040A')}
        Then VALUE == 1034
        
    @MatchPattern
    Scenario: function MatchPattern
        
        Given TEXT = 'Hello TOTO !'
        Then TEXT == '${MatchPattern(.*TOTO.*)}'
        
        Then TEXT == '${MatchPattern([^ ]+ (?P<NAME>\w+).*)}'
        Then NAME == 'TOTO'
        
        
        Given TEXT = 'Hello !\nHow are you TOTO ?'
        
        Given next step shall fail on exception matching '.*holado_core.common.exceptions.verify_exception.VerifyException\(Match failure, value doesn't match pattern.*'
        Then TEXT == '${MatchPattern(.*(?P<NAME>\w+) \?)}'
        
        Then TEXT == '${MatchPattern(.*?(?P<NAME>\w+) \?, re.DOTALL)}'
        Then NAME == 'TOTO'
        
        
        Given TEXT = 'First plan was launched at 2024-06-20'
        Then TEXT == '${MatchPattern(^First plan was launched at \d{4}-\d{2}-\d{2}$)}'
        
        
        Given TABLE = table with header
            | Name   | Value                                    |
            | 'text' | 'First plan was launched at 2024-06-20'  |
        Then table TABLE is
            | Name   | Value                                                              |
            | 'text' | '${MatchPattern(^First plan was launched at \d{4}-\d{2}-\d{2})}'  |
        
        
    @ToHex
    Scenario: function ToHex
        
        Given VALUE = 1034
        Given HEX = '${ToHex(VALUE)}'
        Then HEX == '040A'
        Given HEX = '${ToHex(VALUE, False)}'
        Then HEX == '040a'
        
        Given VALUE = 'TEST'
        Given HEX = '${ToHex(VALUE)}'
        Then HEX == '54455354'

        Given VALUE = b'\xF1\x4A'
        Given HEX = '${ToHex(VALUE)}'
        Then HEX == 'F14A'
        
    @EscapeAllBytes
    Scenario: function EscapeAllBytes
        
        Given HEX = 'd27ced'
        Given VALUE = ${HexToBytes(HEX)}
        Given ESCAPED_VALUE = '${EscapeAllBytes(VALUE)}'
        
        Then ESCAPED_VALUE == 'b'\\xd2\\x7c\\xed''
        
        # Same in a thread
        Given THREAD_ID = call steps in a thread
            """
            Given ESCAPED_VALUE_2 = '${EscapeAllBytes(VALUE)}'
            """
        When join thread THREAD_ID
        Then ESCAPED_VALUE_2 == ESCAPED_VALUE
        
        # Same with explicit byte expression in text
        Given THREAD_ID = call steps in a thread
            """
            Given ESCAPED_VALUE_3 = '${EscapeAllBytes(b'\\xd2\\x7c\\xed')}'
            """
        When join thread THREAD_ID
        Then ESCAPED_VALUE_3 == ESCAPED_VALUE
        
        
        
        
