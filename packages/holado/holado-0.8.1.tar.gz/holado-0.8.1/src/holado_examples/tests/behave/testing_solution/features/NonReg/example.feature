@example
Feature: Example of feature

    Scenario: Get and verify file content
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given DT_NOW = datetime now
        Given DT_NOW_STR = convert datetime DT_NOW to string with format '%Y-%m-%dT%H-%M-%S-%f'
        Given FILENAME = 'test_${DT_NOW_STR}.xml'
        
        Given TEXT = 'text'
        Given FILE_PATH = create file with name FILENAME
            """
            <node>${TEXT}</node>
            """
            
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given FILE_CONTENT = content of file FILE_PATH
        Given FILE_CONTENT_STR = convert object value FILE_CONTENT to string
        Then FILE_CONTENT_STR == '<node>text</node>'

        
        