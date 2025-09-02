@testing_solution
@VariableManager
Feature: Features related to VariableManager

    Scenario: basic variable use
        Given VAR1 = 'test'
        Given VAR2 = VAR1
        Then VAR1 == 'test'
        Then VAR2 == 'test'
        Then VAR1 == VAR2

    Scenario: string compare
        Then 'test' == 'test'
        Then 'test' != 'test1'
        Then 'test' <= 'test'
        Then 'test' <= 'tesu'
        Then 'test' < 'tesu'
        
        Given VAR = 'test'
        
        Then VAR == 'test'
        Then VAR != 'test1'
        Then VAR <= 'test'
        Then VAR <= 'tesu'
        Then VAR < 'tesu'
        
        Then 'test' == VAR
        Then 'test1' != VAR
        Then 'test' <= VAR
        Then 'tess' <= VAR
        Then 'tess' < VAR
        Then 'tesu' > VAR
      
    @list
    Scenario: List of ids
        Given LISTVAR = list
            | 1    |
            | 0    |
            | 5    |
            
        Then [1, 0, 5] == ${LISTVAR}
        Then '[1, 0, 5]' != ${LISTVAR}
        Then '[1, 0, 5]' == '${LISTVAR}'
        
        Then '[1, 0, 5]' == str(${LISTVAR})
        # In next expression, after having casted to str, ${} makes an evaluation of obtained string, thus result of ${str(LISTVAR)} is a list
        Then '[1, 0, 5]' != ${str(LISTVAR)}
        Then [1, 0, 5] == ${str(LISTVAR)}
    
    Scenario: Comprehension expression
        Given LISTVAR = list(range(0,5))
        Then LISTVAR == [0, 1, 2, 3, 4]
        
        Given RES = list of ${X} * 2 for X in LISTVAR
        Then RES == [0, 2, 4, 6, 8]
        
    Scenario: Sorted
        Given VAL = [2,4,0,3,1]
        Given RES = sorted VAL
        Then RES == [0, 1, 2, 3, 4]
        
        Given VAL = [(0,2),(1,4),(2,0),(3,3),(4,1)]
        Given RES = sorted VAL by x: x[1]
        Then RES == [(2,0),(4,1),(0,2),(3,3),(1,4)]
        
    Scenario: Call python builtin functions
        Given VAL_FLOAT = 2.568
        When VAL_INT = round(${VAL_FLOAT})
        Then VAL_INT == 3
        
        