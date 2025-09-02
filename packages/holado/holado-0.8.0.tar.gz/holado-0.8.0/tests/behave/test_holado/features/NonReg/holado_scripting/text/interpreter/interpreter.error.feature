@testing_solution
@TextInterpreter
@error
Feature: Features related to TextInterpreter

    @HexToBytes
    Scenario: function HexToBytes

        Given HEX = '\x2d569F'
        Given next step shall fail on exception matching 'Source \[-569F\] \(type: str\) is not an hexadecimal string'
        Given VALUE_1 = ${HexToBytes(HEX)}

        Given TABLE = table with header
            | Name   | Value              |
            | 'test' | ${HexToBytes(HEX)} |
        Given next step shall fail on exception matching 'Source \[-569F\] \(type: str\) is not an hexadecimal string'
        Then table TABLE is
            | Name   | Value  |
            | 'test' | 'PIPO' |


