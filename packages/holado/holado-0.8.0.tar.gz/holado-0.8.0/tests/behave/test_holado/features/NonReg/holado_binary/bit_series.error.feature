@testing_solution
@bit_series
@error
@go_nogo
Feature: Test bit_series module

    Scenario: Create from hexa bit-series of bit length out of bytes array length
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type |
            | 'F1'    | 3          | int  |
            | 'F2'    | 1          | int  |
            | 'F3'    | 1          | int  |
        
        Given next step shall fail on exception matching 'Hexadecimal string has unexpected padded characters, only zero padding is managed \(expected bits number: 5 ; left padding ; obtained padding bits: 100\)'
        When fill bit series BIT_SERIES from hexadecimal string '92'
        
        Given next step shall fail on exception matching 'Hexadecimal string has unexpected padded characters, only zero padding is managed \(expected bits number: 5 ; left padding ; obtained padding bits: 100\)'
        When fill bit series BIT_SERIES from hexadecimal string '92' (left padded)
        
        Given next step shall fail on exception matching 'Hexadecimal string has unexpected padded characters, only zero padding is managed \(expected bits number: 5 ; right padding ; obtained padding bits: 010\)'
        When fill bit series BIT_SERIES from hexadecimal string '92' (right padded)
        
    Scenario: Create and convert bit-series to hexa with a field value exceeding bit length
        Given BIT_SERIES = bit series
            | Name    | Bit length | Type | Value |
            | 'F1'    | 3          | int  | 4     |
            | 'F2'    | 1          | int  | 1     |
            | 'F3'    | 2          | int  | 2     |
            | 'F4'    | 2          | int  | 4     |
        Given next step shall fail on exception matching 'For field 'F4', the value \[4\] has binary length 3 \(expected length: 2\)'
        Given RAW_TM = convert bit series BIT_SERIES to hexadecimal string
        
        