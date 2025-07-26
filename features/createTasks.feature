Feature: Create Task

  Scenario: Create Task with no data
    Given the user is on task list page
    When user clicks on New
    And clicks on submit
    Then a new task should be created 
    And Task title is "<No Title>"
    And Task Due Date is "today"
    And Task banner should be "Uncategorized - Anytime"
    And the user is on task list page


  Scenario: Create Task with Title only
    Given the user is on task list page
    When user clicks on New
    And user enters "TitleOnlyTest" on title field
    And clicks on submit
    Then a new task should be created 
    And Task title is "TitleOnlyTest"
    And Task Due Date is "today"
    And Task banner should be "Uncategorized - Anytime"
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


  Scenario: Create Task with Title, Frequency, Category and Due Date
    Given the user is on task list page
    When user clicks on New
    And user enters "TitleWithFreqTest" on title field
    And user enters "Daily" on the frequency field
    And user enters due date as "05-Nov-2018"
    And user selects category as "bills"
    And clicks on submit
    Then a new task should be created 
    And Task title is "TitleWithFreqTest"
    And Task Due Date is "05-Nov-2018"
    And Task Frequency is "Daily"
    And Task banner should be "Bills - Anytime"
    And Task Next is "0" day after "today"
    And the user is on task list page
  
  Scenario: Create Tasks with Title and Time Slots
    Given the user is on task list page
    When user clicks on New
    And user enters "Slot1Task" on title field
    And user selects slot "1"
    And clicks on submit
    And user clicks on New
    And user enters "Slot2Task" on title field
    And user selects slot "2"
    And clicks on submit
    Then the user is on task list page
    And "2" new tasks should be created
    And "Slot1Task" should appear before "Slot2Task" in today

  Scenario: Create Tasks with Title and Reminder
    Given the user is on task list page
    When user clicks on New
    And user enters "RemindTask" on title field
    And user enters due date "5" days in future
    And user enters "5" in remind before field
    And clicks on submit
    Then the user is on task list page
    And "1" new tasks should be created
    And "RemindTask" should appear in the alerts section

  Scenario: Create Tasks with Title ,Frequency and Track Habit
    Given the user is on task list page
    When user clicks on New
    And user enters "HabitTask" on title field
    And user enters "Daily" on the frequency field
    And user selects Track Habit
    And clicks on submit
    Then the user is on task list page
    And "1" new tasks should be created
    And "HabitTask" should have Done and Skip button with 0 count

  Scenario: Create Tasks with Title ,Duration and Description
    Given the user is on task list page
    When user clicks on New
    And user enters "DurationTaskWithDesc" on title field
    And user enters duration as "10" mins
    And user enters the description as "Description of Task"
    And clicks on submit
    Then the user is on task list page
    And "1" new tasks should be created
    And Duration should be displayed as "10" mins
