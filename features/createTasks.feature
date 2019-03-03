Feature: Create Task

  Scenario: Create Task with no data
    Given the user is on task list page
    When user clicks on New
    And clicks on submit
    Then a new task should be created 
    And Task title is "<No Title>"
    And Task Due Date is "today"
    And the user is on task list page


  Scenario: Create Task with Title only
    Given the user is on task list page
    When user clicks on New
    And user enters "TitleOnlyTest" on title field
    And clicks on submit
    Then a new task should be created 
    And Task title is "TitleOnlyTest"
    And Task Due Date is "today"
    And the user is on task list page

  Scenario: Create Task with Title and Frequency
    Given the user is on task list page
    When user clicks on New
    And user enters "TitleWithFreqTest" on title field
    And user enters "Daily" on the frequency field
    And clicks on submit
    Then a new task should be created 
    And Task title is "TitleWithFreqTest"
    And Task Due Date is "today"
    And Task Frequency is "Daily"
    And Task Next is "1" day after "today"
    And the user is on task list page


  Scenario: Create Task with Title and Frequency and Due Date
    Given the user is on task list page
    When user clicks on New
    And user enters "TitleWithFreqTest" on title field
    And user enters "Daily" on the frequency field
    And user enters due date as "05-Nov-2018"
    And clicks on submit
    Then a new task should be created 
    And Task title is "TitleWithFreqTest"
    And Task Due Date is "05-Nov-2018"
    And Task Frequency is "Daily"
    And Task Next is "1" day after "05-Nov-2018"
    And the user is on task list page
    
