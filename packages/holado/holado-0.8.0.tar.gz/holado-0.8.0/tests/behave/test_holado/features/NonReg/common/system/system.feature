@testing_solution
@system
Feature: Features related to generic system actions

    Scenario: Create file with content in context.text
    
        Given DT_NOW = datetime now
        Given DT_NOW_STR = convert datetime DT_NOW to string with format '%Y-%m-%dT%H-%M-%S-%f'
        Given FILENAME = 'SC_KINEIS_OPS-ACK_${DT_NOW_STR}.xml'
        
        Given TEXT = 'text'
        
        Given FILE_PATH = create file with name FILENAME
            """
            <node>${TEXT}</node>
            """
            
        Given FILE_CONTENT = content of file FILE_PATH
        Given FILE_CONTENT_STR = convert object value FILE_CONTENT to string
        Then FILE_CONTENT_STR == '<node>text</node>'
