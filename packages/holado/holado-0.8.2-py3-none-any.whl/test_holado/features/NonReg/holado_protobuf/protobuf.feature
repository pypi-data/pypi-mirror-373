@testing_solution
@protobuf
@go_nogo
Feature: Test Protobuf module

    Scenario: Tutorial example

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO = new Protobuf object of type 'tutorial.AddressBook'
            | Name                         | Value                  |
            | 'people[0].id'               | 0                      |
            | 'people[0].name'             | 'name0'                |
            | 'people[0].email'            | 'email0@test.com'      |
            | 'people[0].last_updated'     | '2022-01-01T01:00:00Z' |
            | 'people[0].phones[0].number' | '0623456789'           |
            | 'people[0].phones[0].type'   | MOBILE                 |
            #| 'people[0].phones[0].type'   | 0                      |
            | 'people[0].phones[1].number' | '0123456789'           |
            #| 'people[0].phones[1].type'   | HOME                   |
            | 'people[0].phones[1].type'   | 1                      |
            | 'people[1].id'               | 1                      |
            | 'people[1].name'             | 'name1'                |
            | 'people[1].email'            | 'email1@test.com'      |
            | 'people[1].last_updated'     | '2022-02-02 02:00:00'  |
            | 'people[1].phones[0].number' | '0523456789'           |
            | 'people[1].phones[0].type'   | WORK                   |
            #| 'people[1].phones[0].type'   | 2                      |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'tutorial.AddressBook' Protobuf object


    Scenario: Map field assigned by key name

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithMap'
            | Name      | Value |
            | 'id'      | 0     |
            | 'map[k1]' | 'v1'  |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithMap' Protobuf object

        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table with names uncollapsed
        Then table NEW_PROTO_TABLE is
            | Name      | Value |
            | 'id'      | 0     |
            | 'map[k1]' | 'v1'  |

    Scenario: Map field assigned by dict

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithMap'
            | Name  | Value       |
            | 'id'  | 0           |
            | 'map' | {'k1':'v1'} |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithMap' Protobuf object
        
        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table
        Then table NEW_PROTO_TABLE is
            | Name  | Value       |
            | 'id'  | 0           |
            | 'map' | {'k1':'v1'} |
        
        
    Scenario: Optional field when set
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithOptional'
            | Name            | Value       |
            | 'id'            | 0           |
            | 'text'          | 'toto'      |
            | 'optional_text' | 'pipo'      |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO_TABLE = convert Protobuf object PROTO to name/value table
        Then table PROTO_TABLE is
            | Name            | Value       |
            | 'id'            | 0           |
            | 'text'          | 'toto'      |
            | 'optional_text' | 'pipo'      |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithOptional' Protobuf object
        
        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table
        Then NEW_PROTO_TABLE == PROTO_TABLE
        
        
    Scenario: Optional field when not set
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithOptional'
            | Name            | Value       |
            | 'id'            | 0           |
            | 'text'          | 'toto'      |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO_TABLE = convert Protobuf object PROTO to name/value table
        Then table PROTO_TABLE is
            | Name            | Value       |
            | 'id'            | 0           |
            | 'text'          | 'toto'      |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithOptional' Protobuf object
        
        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table
        Then NEW_PROTO_TABLE == PROTO_TABLE
        
        
    Scenario: Normal field when not set
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithOptional'
            | Name            | Value       |
            | 'id'            | 0           |
            | 'optional_text' | 'pipo'      |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO_TABLE = convert Protobuf object PROTO to name/value table
        Then table PROTO_TABLE is
            | Name            | Value       |
            | 'id'            | 0           |
            | 'text'          | ''          |
            | 'optional_text' | 'pipo'      |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithOptional' Protobuf object
        
        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table
        Then NEW_PROTO_TABLE == PROTO_TABLE
        
    @repeated_assigned_by_list
    Scenario: Repeated field assigned by list

        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        Given PROTO = new Protobuf object of type 'custom_types.MessageWithRepeated'
            | Name     | Value     |
            | 'id'     | 0         |
            | 'values' | [1, 2, 3] |
            
        Given PROTO_STR = serialize Protobuf object PROTO
        
        Given NEW_PROTO = unserialize string PROTO_STR as 'custom_types.MessageWithRepeated' Protobuf object
        
        Given NEW_PROTO_TABLE = convert Protobuf object NEW_PROTO to name/value table
        Then table NEW_PROTO_TABLE is
            | Name     | Value     |
            | 'id'     | 0         |
            | 'values' | [1, 2, 3] |

        
    @enum_field
    Scenario: Enum field
        ### PRECONDITIONS - BEGIN
        Given begin preconditions
        
        Given PROTO = new Protobuf object of type 'tutorial.AddressBook'
            | Name                         | Value                  |
            | 'people[0].id'               | 0                      |
            | 'people[0].name'             | 'name0'                |
            | 'people[0].email'            | 'email0@test.com'      |
            | 'people[0].last_updated'     | '2022-01-01T01:00:00Z' |
            | 'people[0].phones[0].number' | '0623456789'           |
            | 'people[0].phones[0].type'   | MOBILE                 |
            #| 'people[0].phones[0].type'   | 0                      |
            | 'people[0].phones[1].number' | '0123456789'           |
            #| 'people[0].phones[1].type'   | HOME                   |
            | 'people[0].phones[1].type'   | 1                      |
            | 'people[0].phones[2].number' | '0923456789'           |
            | 'people[0].phones[2].type'   | WORK                   |
            #| 'people[0].phones[2].type'   | 2                      |
        
        Given end preconditions
        ### PRECONDITIONS - END
        
        # Get enum value
        Given MOBILE_VALUE = value of Protobuf enum 'tutorial.Person.PhoneType.MOBILE'
        Then MOBILE_VALUE == 0
        Given HOME_VALUE = value of Protobuf enum 'tutorial.Person.PhoneType.HOME'
        Then HOME_VALUE == 1
        Given WORK_VALUE = value of Protobuf enum 'tutorial.Person.PhoneType.WORK'
        Then WORK_VALUE == 2
        
        # Verify enum value in a Protobuf message
        Then PROTO.people[0].phones[0].type == MOBILE_VALUE
        Then PROTO.people[0].phones[1].type == HOME_VALUE
        Then PROTO.people[0].phones[2].type == WORK_VALUE
        
        # Verify enum name by its value
        Given PHONE_TYPE_NAME = name of value MOBILE_VALUE of Protobuf enum type 'tutorial.Person.PhoneType'
        Then PHONE_TYPE_NAME == 'MOBILE'
        
        # Verify message by convertion as a table
        Given PROTO_TABLE = convert Protobuf object PROTO to name/value table with names and repeated uncollapsed
        Then table PROTO_TABLE is
            | Name                             | Value                  |
            | 'people[0].name'                 | 'name0'                |
            | 'people[0].id'                   | 0                      |
            | 'people[0].email'                | 'email0@test.com'      |
            | 'people[0].phones[0].number'     | '0623456789'           |
            | 'people[0].phones[0].type'       | MOBILE                 |
            | 'people[0].phones[1].number'     | '0123456789'           |
            | 'people[0].phones[1].type'       | HOME                   |
            | 'people[0].phones[2].number'     | '0923456789'           |
            | 'people[0].phones[2].type'       | WORK                   |
            | 'people[0].last_updated.seconds' | 1640998800             |
            | 'people[0].last_updated.nanos'   | 0                      |
        
        
    @import_enum
    Scenario: Import enum
        Given import Protobuf enum type 'tutorial.Person.PhoneType'
        Then PhoneType.MOBILE == 0
        Then PhoneType.HOME == 1
        Then PhoneType.WORK == 2
        Then tutorial.Person.PhoneType.MOBILE == 0
        Then tutorial.Person.PhoneType.HOME == 1
        Then tutorial.Person.PhoneType.WORK == 2
        
        Given import values of Protobuf enum type 'tutorial.Person.PhoneType'
        Then MOBILE == 0
        Then HOME == 1
        Then WORK == 2
        
        Given import values of Protobuf enum type 'tutorial.Person.PhoneType' with prefix 'PHONE_TYPE_'
        Then PHONE_TYPE_MOBILE == 0
        Then PHONE_TYPE_HOME == 1
        Then PHONE_TYPE_WORK == 2
        
        # Use imports in other sentences
        Given VALUE = -1
        Given if ${PHONE_TYPE_MOBILE} == 0:
            Given VALUE = 0
        Given end if
        Then VALUE == 0
        
        Given if ${PhoneType.HOME} == 1:
            Given VALUE = 1
        Given end if
        Then VALUE == 1
        
        Given if 2 == ${PhoneType.WORK}:
            Given VALUE = 2
        Given end if
        Then VALUE == 2
        
        
        