@testing_solution
@DynamicTextManager
Feature: Features related to DynamicTextManager

    Scenario: dynamic string compare

        Given VAR = 'test'%

        Then VAR == 'test'%
        #Then VAR == '${MatchPattern(test[a-zA-Z0-9]{6})}'
        Then VAR != 'test'
        Then VAR < 'tesu'
        
        Then 'test'% == VAR
        #Then '${MatchPattern(test[a-zA-Z0-9]{6})}' == VAR
        Then 'test' != VAR
        Then 'test' < VAR
        
