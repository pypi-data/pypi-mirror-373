@testing_solution
@bit_series
@go_nogo
Feature: Test bit_series module

    @to_hexadecimal_string
    Scenario: Create and convert bit-series to hexa
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 2          | int  | 2     |
            | 'F4'    | 2          | int  | 1     |
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        Then RAW_TM == '99'

        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value   |
            | 'F1'    | 3          | int  | 4       |
            | 'F2'    | 1          | int  | 1       |
            | 'F3'    | 2          | int  | 2       |
            | 'F4'    | 2          | int  | 1       |
            | 'F5'    | 16         | str  | 'ffff'  |
            | 'F6'    | 16         | str  | 'AE1B'  |
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        Then RAW_TM == '99FFFFAE1B'

    
    @to_hexadecimal_string
    @padding
    Scenario: Create and convert to hexa bit-series of bit length out of bytes array length
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 1          | int  | 1     |
            
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        Then RAW_TM == '13'

        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string (left padded)
        Then RAW_TM == '13'

        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string (right padded)
        Then RAW_TM == '98'


        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 3          | int  | 1     |
            
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        Then RAW_TM == '49'
            
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string (left padded)
        Then RAW_TM == '49'
            
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string (right padded)
        Then RAW_TM == '92'

    
    @from_hexadecimal_string
    Scenario: Create a bit-series from hexa
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type |
            | 'F1'    | 3          | int  |
            | 'F2'    | 1          | int  |
            | 'F3'    | 2          | int  |
            | 'F4'    | 2          | int  |
        When fill bit series BIT_SERIES from hexadecimal string '92'
        Then bit series BIT_SERIES is
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 2          | int  | 0     |
            | 'F4'    | 2          | int  | 2     |


    @from_hexadecimal_string
    @padding
    Scenario: Create from hexa bit-series of bit length out of bytes array length
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type |
            | 'F1'    | 3          | int  |
            | 'F2'    | 1          | int  |
            | 'F3'    | 1          | int  |
            
        When fill bit series BIT_SERIES from hexadecimal string '13'
        Then bit series BIT_SERIES is
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 1          | int  | 1     |
            
        When fill bit series BIT_SERIES from hexadecimal string '13' (left padded)
        Then bit series BIT_SERIES is
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 1          | int  | 1     |
            
        When fill bit series BIT_SERIES from hexadecimal string '98' (right padded)
        Then bit series BIT_SERIES is
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 1          | int  | 1     |


    @is_bit_series
    Scenario: Verify hexa string is bit series
        Then hexadecimal string '92' is bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 2          | int  | 0     |
            | 'F4'    | 2          | int  | 2     |


    @set_field
    Scenario: Set bit-series field by variable expression
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 2          | int  | 2     |
            | 'F4'    | 2          | int  | 1     |
            | 'F5'    | 16         | int  | 0     |
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        Then BIT_SERIES['F5'] == 0
        Then RAW_TM[-4:] == '0000'

        Given BIT_SERIES['F5'] = 1
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        
        Then BIT_SERIES['F5'] == 1
        Then RAW_TM[-4:] == '0001'
        Then BIT_SERIES['F5'] != 0
        Then RAW_TM[-4:] != '0000'
        
    
        