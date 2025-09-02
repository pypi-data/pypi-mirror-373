@testing_solution
@yaml
Feature: Test YAML module

    @load_file
    Scenario: Load a YAML file
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |

    @base_load_file
    Scenario: Load a YAML file with only base YAML features
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH (client type: 'base')
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | '2001'                       |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | '2001'                       |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | '1996'                       |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |

    @safe_load_file
    Scenario: Load a YAML file with safe YAML features
        Given FILE_PATH = create file with name 'load.yaml'
            """
            company: spacelift
            domain:
             - devops
             - devsecops
            tutorial:
              - yaml: &reference
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json: *reference
              - xml:
                  <<: *reference
                  born: 1996
            author: omkarbirade
            """
            
        When CONTENT = load YAML file FILE_PATH (client type: 'safe')
        
        Given TABLE = convert json CONTENT to name/value table with names and list uncollapsed
        Then table TABLE is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[1].json.type' | 'awesome'                    |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'YAML Ain't Markup Language' |
            | 'tutorial[2].xml.type'  | 'awesome'                    |


    @load_multiple_document
    Scenario: Load a multiple document YAML file
        Given FILE_PATH = create file with name 'load_multiple.yaml'
            """
            ---
            company: spacelift
            domain:
             - devops
             - devsecops
            ---
            tutorial:
              - yaml:
                  name: "YAML Ain't Markup Language"
                  type: awesome
                  born: 2001
              - json:
                  name: JavaScript Object Notation
                  type: great
                  born: 2001
              - xml:
                  name: Extensible Markup Language
                  type: good
                  born: 1996
            author: omkarbirade
            ...
            """
            
        When CONTENT = load multiple documents YAML file FILE_PATH
        
        Given TABLE_1 = convert json CONTENT[0] to name/value table with names and list uncollapsed
        Given TABLE_2 = convert json CONTENT[1] to name/value table with names and list uncollapsed
        Then table TABLE_1 is
            | Name                    | Value                        |
            | 'company'               | 'spacelift'                  |
            | 'domain[0]'             | 'devops'                     |
            | 'domain[1]'             | 'devsecops'                  |
        Then table TABLE_2 is
            | Name                    | Value                        |
            | 'author'                | 'omkarbirade'                |
            | 'tutorial[0].yaml.born' | 2001                         |
            | 'tutorial[0].yaml.name' | 'YAML Ain't Markup Language' |
            | 'tutorial[0].yaml.type' | 'awesome'                    |
            | 'tutorial[1].json.born' | 2001                         |
            | 'tutorial[1].json.name' | 'JavaScript Object Notation' |
            | 'tutorial[1].json.type' | 'great'                      |
            | 'tutorial[2].xml.born'  | 1996                         |
            | 'tutorial[2].xml.name'  | 'Extensible Markup Language' |
            | 'tutorial[2].xml.type'  | 'good'                       |


    @save_file
    Scenario: Save data in a YAML file
        Given DATA = ${{'company': 'spacelift', 'domain': ['devops', 'devsecops'], 'tutorial': [{'yaml': {'name': "YAML Ain't Markup Language", 'type': 'awesome', 'born': 2001}}, {'json': {'name': 'JavaScript Object Notation', 'type': 'great', 'born': 2001}}, {'xml': {'name': 'Extensible Markup Language', 'type': 'good', 'born': 1996}}], 'author': 'omkarbirade'}}
        
        Given FILE_PATH = path to file with name 'save.yaml'
        When save DATA in YAML file FILE_PATH
        
        Given CONTENT_BYTES = content of file FILE_PATH
        Given CONTENT_STR = convert object value CONTENT_BYTES to string
        Given CONTENT_STR = ${CONTENT_STR.strip()}
        
        Given EXPECTED = multiline text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            tutorial:
            - yaml:
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
            - json:
                name: JavaScript Object Notation
                type: great
                born: 2001
            - xml:
                name: Extensible Markup Language
                type: good
                born: 1996
            author: omkarbirade
            """
        Then CONTENT_STR == EXPECTED

    @update_file
    Scenario: Update a YAML file
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Initialize file
        Given CONTENT_FILE_INIT = multiline text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: omkarbirade
            """
        Given FILE_PATH = create file with name 'load.yaml' and content CONTENT_FILE_INIT
        Given BACKUP_PATH = '${FILE_PATH}.ha_bak'
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Define data to update in file
        When DATA_1 = json object
            """
            {
                "domain": [
                    "architect"
                ],
                "size": 100,
                "author": "holado"
            }
            """
        When DATA_2 = json object
            """
            {
                "size": 50
            }
            """
        
        # Update file with DATA_1 and backup
        When update YAML file FILE_PATH with data DATA_1 (with backup ; backup extension: '.ha_bak')
        
        # Verify content of file and backup
        Given CONTENT_FILE = content of text file FILE_PATH
        Then CONTENT_FILE is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 100
            """
        
        Given CONTENT_BACKUP = content of text file BACKUP_PATH
        Then CONTENT_BACKUP == CONTENT_FILE_INIT
        
        # Update file with DATA_2 and backup
        When update YAML file FILE_PATH with data DATA_2 (with backup ; backup extension: '.ha_bak')
        
        # Verify content of file and backup
        Given CONTENT_FILE = content of text file FILE_PATH
        Then CONTENT_FILE is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 50
            """
        
        Given CONTENT_BACKUP = content of text file BACKUP_PATH
        Then CONTENT_BACKUP == CONTENT_FILE_INIT
        
        # Restore file
        When restore YAML file FILE_PATH (backup extension: '.ha_bak')
        
        # Verify content of file, and backup doesn't exist anymore
        Given CONTENT_FILE = content of text file FILE_PATH
        Then CONTENT_FILE == CONTENT_FILE_INIT
        Then file BACKUP_PATH doesn't exist

    @update_string
    Scenario: Update a YAML string
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Initialize string
        Given STR_INIT = multiline text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: omkarbirade
            """
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Define data to update in file
        When DATA_1 = json object
            """
            {
                "domain": [
                    "architect"
                ],
                "size": 100,
                "author": "holado"
            }
            """
        When DATA_2 = json object
            """
            {
                "size": 50
            }
            """
        
        # Update string with DATA_1
        When STR_1 = update YAML string STR_INIT with data DATA_1
        
        # Verify string
        Then STR_1 is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 100
            """
        
        # Update string with DATA_2
        When STR_2 = update YAML string STR_1 with data DATA_2
        
        # Verify string
        Then STR_2 is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 50
            """

    @update_yaml_object
    Scenario: Update a YAML object
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        # Initialize string
        Given STR_INIT = multiline text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: omkarbirade
            """
        Given OBJ = load YAML string STR_INIT
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Define data to update in file
        When DATA_1 = YAML object
            """
            domain:
            - architect
            size: 100
            author: holado
            """
        When DATA_2 = json object
            """
            {
                "size": 50
            }
            """
        
        # Update object with DATA_1
        When update YAML object OBJ with data DATA_1
        
        # Verify object
        When STR_1 = convert YAML object OBJ to string
        Then STR_1 is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 100
            """
        
        # Update object with DATA_2
        When update YAML object OBJ with data DATA_2
        
        # Verify string
        When STR_2 = convert YAML object OBJ to string
        Then STR_2 is text
            """
            company: spacelift
            domain:
            - devops
            - devsecops
            - architect
            tutorial:
              yaml: &reference
                name: YAML Ain't Markup Language
                type: awesome
                born: 2001
              json: *reference
              xml:
                <<: *reference
                born: 1996
            author: holado
            size: 50
            """
        



