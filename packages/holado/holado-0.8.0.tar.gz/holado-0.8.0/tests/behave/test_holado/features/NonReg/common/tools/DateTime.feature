@testing_solution
@DateTime
Feature: Features related to DateTime

    @datetime_now-to_string
    Scenario: DateTime to String without format
        Given DT_REF = datetime now
        Given DT_REF_STR = convert datetime DT_REF to string
       
    @datetime_now_in_utc_tai
    Scenario: DateTime to String without format
        Given DT_UTC = datetime now in UTC
        Given DT_TAI = datetime now in TAI
        
        Given DT_UTC_SEC = ${DT_UTC.timestamp()}
        Given DT_TAI_SEC = ${DT_TAI.timestamp()}
        Then ${${DT_UTC_SEC}+36} < DT_TAI_SEC
        Then DT_TAI_SEC < ${${DT_UTC_SEC}+38}
        
    @datetime-to_string
    Scenario: DateTime to String without format
        Given DT = datetime '2022/12/09T12:34:56.012345678'
        Given DT_STR = convert datetime DT to string
        Then DT_STR == '2022-12-09T12:34:56.012345'
        
        Given DT = datetime '2022/12/09T12:34:56.012345678Z'
        Given DT_STR = convert datetime DT to string
        Then DT_STR == '2022-12-09T12:34:56.012345+00:00'
        
    @datetime-to_string_with_format
    Scenario: DateTime to String without format
        Given DT = datetime '2022/12/09T12:34:56.012345678Z'
        
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%SZ'
        Then DT_STR == '2022-12-09T12:34:56Z'
        
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T12:34:56.012345Z'
        
    @datetime-delta
    Scenario: Add delta to DateTime
        Given DT_init = datetime '2022/12/09T12:34:56.012345678Z'
        
        # Plus duration
        Given DT = DT_init + 800 microseconds
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T12:34:56.013145Z'
        
        Given DT = DT_init + 9 milliseconds
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T12:34:56.021345Z'
        
        Given DT = DT_init + 10 seconds
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T12:35:06.012345Z'
        
        Given DT = DT_init + 30 minutes
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T13:04:56.012345Z'
        
        Given DT = DT_init + 12 hours
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-10T00:34:56.012345Z'
        
        Given DT = DT_init + 25 days
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2023-01-03T12:34:56.012345Z'
        
        Given DT = DT_init + 2 weeks
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-23T12:34:56.012345Z'
        
        Given DT = DT_init + 2 months
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2023-02-09T12:34:56.012345Z'
        
        Given DT = DT_init + 10 years
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2032-12-09T12:34:56.012345Z'
        
        
        # Minus duration
        Given DT = DT_init - 70 seconds
        Given DT_STR = convert datetime DT to string with format '%Y-%m-%dT%H:%M:%S.%fZ'
        Then DT_STR == '2022-12-09T12:33:46.012345Z'
        
        
        